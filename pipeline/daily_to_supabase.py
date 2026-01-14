import os
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
from equity_engine.pipeline import build_universe, enrich_stock
from equity_engine.config import load_settings
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    
    # Debug logging for URL format (masked for security)
    import logging
    logger = logging.getLogger(__name__)
    masked_url = f"{url[:12]}...{url[-5:]}" if len(url) > 20 else "Invalid Length"
    logger.info(f"Initializing Supabase client with URL: {masked_url}")
    
    return create_client(url, key)

def prepare_daily_payload(df: pd.DataFrame, snapshot_date: date) -> list:
    """Map enrichment dataframe to Supabase table schema"""
    payload = []
    
    # Replace NaN/inf with None for JSON compatibility
    df = df.replace([np.inf, -np.inf], np.nan)
    
    def get_val(row, keys):
        if isinstance(keys, str):
            keys = [keys]
        for k in keys:
            if k in row.index:
                v = row.get(k)
                if pd.notna(v):
                    return v
        return None

    for _, row in df.iterrows():
        # Get ticker from either 'symbol' or 'Ticker' column
        raw_symbol = row.get("symbol")
        raw_ticker = row.get("Ticker")
        
        ticker = ""
        if pd.notna(raw_symbol) and str(raw_symbol).strip():
            ticker = str(raw_symbol).strip()
        elif pd.notna(raw_ticker) and str(raw_ticker).strip():
            ticker = str(raw_ticker).strip()
            
        if not ticker or ticker.lower() == "nan":
            continue
            
        item = {
            "ticker": ticker,
            "company_name": str(get_val(row, ["Company Name", "companyName"]) or ""),
            "date": snapshot_date.isoformat(),
            
            # Price
            "price_last": get_val(row, ["Price (Last)", "Price"]),
            "high_52w": row.get("52W High"),
            "low_52w": row.get("52W Low"),
            
            # Returns
            "return_1d": get_val(row, ["Return 1d %", "Return 1D %", "1D Return %"]),
            "return_1w": get_val(row, ["Return 5d %", "Return 1W %", "1W Return %"]),
            "return_1m": get_val(row, ["Return 21d %", "Return 1M %", "1M Return %"]),
            "return_3m": get_val(row, ["Return 63d %", "Return 3M %", "3M Return %"]),
            "return_6m": get_val(row, ["Return 126d %", "Return 6M %", "6M Return %"]),
            "return_1y": get_val(row, ["Return 252d %", "Return 1Y %", "1Y Return %"]),
            
            # Fundamentals
            "pe_ttm": row.get("P/E (TTM)"),
            "pb": row.get("P/B"),
            "roe_ttm": row.get("ROE TTM %"),
            "debt_equity": row.get("Debt/Equity"),
            "market_cap_cr": get_val(row, ["Market Cap (Cr)", "Market Cap (INR Cr)"]),
            
            # Technicals
            "rsi14": get_val(row, ["RSI14", "RSI"]),
            "sma20": get_val(row, ["SMA20", "SMA 20"]),
            "sma50": get_val(row, ["SMA50", "SMA 50"]),
            "sma200": get_val(row, ["SMA200", "SMA 200"]),
            "macd_line": row.get("MACD Line"),
            "macd_signal": row.get("MACD Signal"),
            
            # Scores
            "score_fundamental": row.get("Score Fundamental (0-100)"),
            "score_technical": row.get("Score Technical (0-100)"),
            "score_risk": row.get("Score Risk (0-100)"),
            "overall_score": get_val(row, ["Overall Score (0-100)", "Overall Score"]),
            
            # Metadata
            "sector": row.get("Sector"),
            "industry": row.get("Industry")
        }
        
        # Convert all numpy values to python native for JSON
        for k, v in item.items():
            if pd.isna(v):
                item[k] = None
            elif isinstance(v, (np.float64, np.float32)):
                item[k] = float(v)
            elif isinstance(v, (np.int64, np.int32)):
                item[k] = int(v)
                
        payload.append(item)
    return payload

def upload_to_supabase(payload: list):
    supabase = get_supabase_client()
    try:
        # Upsert by (ticker, date) unique constraint
        supabase.table("daily_stocks").upsert(payload, on_conflict="ticker,date").execute()
        print(f"Successfully uploaded {len(payload)} rows to Supabase")
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        raise

def run_daily_pipeline(limit: int = None, dry_run: bool = False):
    settings = load_settings()
    uni = build_universe(settings.indexes)
    
    if limit:
        print(f"Limiting to first {limit} stocks for testing...")
        uni = uni.head(limit)
        
    rows = []
    batch_size = 20
    uni_list = list(uni.iterrows())
    
    print(f"Enriching {len(uni_list)} stocks...")
    for i in range(0, len(uni_list), batch_size):
        batch = uni_list[i:i + batch_size]
        with ThreadPoolExecutor(max_workers=min(settings.max_workers, len(batch))) as executor:
            futures = {executor.submit(enrich_stock, row["symbol"], settings): row for _, row in batch}
            for future in as_completed(futures):
                original_row = futures[future]
                try:
                    res = future.result()
                    if res:
                        res["Company Name"] = original_row.get("companyName", "")
                        rows.append(res)
                except Exception as e:
                    print(f"Error processing {original_row.get('symbol')}: {e}")

    if rows:
        df = pd.DataFrame(rows)
        
        # Compute sub-scores and overall scores before payload preparation
        try:
            from equity_engine.scoring import compute_subscores, overall_score
            print("Computing scores...")
            subs = compute_subscores(df)
            df = pd.concat([df, subs], axis=1)
            # Use 'overall_score' helper and assign to a canonical column name
            df["Overall Score (0-100)"] = overall_score(subs, settings.weights).clip(0, 100)
        except Exception as e:
            print(f"Warning: Could not compute scores: {e}")
            
        payload = prepare_daily_payload(df, date.today())
        
        if dry_run:
            print("\n--- DRY RUN: Payload Summary ---")
            print(f"Total records gathered: {len(payload)}")
            if payload:
                sample = payload[0]
                print(f"Sample Ticker: {sample['ticker']}")
                print(f"Sample Price: {sample['price_last']}")
                print(f"Sample Overall Score: {sample['overall_score']}")
            print("--- Dry run complete, skipping upload ---")
        else:
            upload_to_supabase(payload)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run daily enrichment and upload to Supabase")
    parser.add_argument("--limit", type=int, help="Limit the number of stocks to process")
    parser.add_argument("--dry-run", action="store_true", help="Run without uploading to Supabase")
    args = parser.parse_args()
    
    run_daily_pipeline(limit=args.limit, dry_run=args.dry_run)
