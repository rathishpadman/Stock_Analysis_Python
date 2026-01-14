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
    
    for _, row in df.iterrows():
        ticker = str(row.get("symbol", row.get("Ticker", ""))).strip()
        if not ticker:
            continue
            
        item = {
            "ticker": ticker,
            "company_name": str(row.get("Company Name", row.get("companyName", ""))),
            "date": snapshot_date.isoformat(),
            
            # Price
            "price_last": row.get("Price"),
            "high_52w": row.get("52W High"),
            "low_52w": row.get("52W Low"),
            
            # Returns
            "return_1d": row.get("1D Return %"),
            "return_1w": row.get("1W Return %"),
            "return_1m": row.get("1M Return %"),
            "return_3m": row.get("3M Return %"),
            "return_6m": row.get("6M Return %"),
            "return_1y": row.get("1Y Return %"),
            
            # Fundamentals
            "pe_ttm": row.get("P/E (TTM)"),
            "pb": row.get("P/B"),
            "roe_ttm": row.get("ROE TTM %"),
            "debt_equity": row.get("Debt/Equity"),
            "market_cap_cr": row.get("Market Cap (Cr)"),
            
            # Technicals
            "rsi14": row.get("RSI"),
            "sma20": row.get("SMA 20"),
            "sma50": row.get("SMA 50"),
            "sma200": row.get("SMA 200"),
            "macd_line": row.get("MACD Line"),
            "macd_signal": row.get("MACD Signal"),
            
            # Scores
            "score_fundamental": row.get("Score Fundamental (0-100)"),
            "score_technical": row.get("Score Technical (0-100)"),
            "score_risk": row.get("Score Risk (0-100)"),
            "overall_score": row.get("Overall Score"),
            
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

def run_daily_pipeline():
    settings = load_settings()
    uni = build_universe(settings.indexes)
    
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
        payload = prepare_daily_payload(df, date.today())
        upload_to_supabase(payload)

if __name__ == "__main__":
    run_daily_pipeline()
