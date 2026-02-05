import os
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, date
from supabase import create_client, Client
from equity_engine.pipeline import build_universe, enrich_stock
from equity_engine.config import load_settings
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

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
    """Map enrichment dataframe to Supabase table schema using 110 fields"""
    payload = []
    
    # Replace NaN/inf with None for JSON compatibility
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Mapping from Template Columns to Database Columns
    field_map = {
        "Ticker": "ticker",
        "Company Name": "company_name",
        "ISIN": "isin",
        "Exchange": "exchange",
        "Sector": "sector",
        "Industry": "industry",
        "Currency": "currency",
        "Market Cap (INR Cr)": "market_cap_cr",
        "Enterprise Value (INR Cr)": "enterprise_value_cr",
        "Revenue TTM (INR Cr)": "revenue_ttm_cr",
        "EBITDA TTM (INR Cr)": "ebitda_ttm_cr",
        "Net Income TTM (INR Cr)": "net_income_ttm_cr",
        "OCF TTM (INR Cr)": "ocf_ttm_cr",
        "CapEx TTM (INR Cr)": "capex_ttm_cr",
        "FCF TTM (INR Cr)": "fcf_ttm_cr",
        "Free Float %": "free_float_pct",
        "Shares Outstanding": "shares_outstanding",
        "Avg Daily Turnover 3M (INR Cr)": "avg_daily_turnover_3m_cr",
        "Avg Volume 1W": "avg_volume_1w",
        "Volume vs 3M Avg %": "volume_vs_3m_avg_pct",
        "P/E (TTM)": "pe_ttm",
        "P/B": "pb",
        "P/S Ratio": "ps_ratio",
        "EV/EBITDA (TTM)": "ev_ebitda_ttm",
        "Dividend Yield %": "dividend_yield_pct",
        "EPS TTM": "eps_ttm",
        "ROE TTM %": "roe_ttm",
        "ROA %": "roa_pct",
        "Debt/Equity": "debt_equity",
        "Interest Coverage": "interest_coverage",
        "EPS Growth YoY %": "eps_growth_yoy_pct",
        "Revenue Growth YoY %": "revenue_growth_yoy_pct",
        "Gross Profit Margin %": "gross_profit_margin_pct",
        "Operating Profit Margin %": "operating_profit_margin_pct",
        "Net Profit Margin %": "net_profit_margin_pct",
        "FCF Yield %": "fcf_yield_pct",
        "PEG Ratio": "peg_ratio",
        "SMA20": "sma20",
        "SMA50": "sma50",
        "SMA200": "sma200",
        "RSI14": "rsi14",
        "MACD Line": "macd_line",
        "MACD Signal": "macd_signal",
        "MACD Hist": "macd_hist",
        "ATR14": "atr14",
        "BB Upper": "bb_upper",
        "BB Lower": "bb_lower",
        "OBV": "obv",
        "ADL": "adl",
        "ADX14": "adx14",
        "Aroon Up": "aroon_up",
        "Aroon Down": "aroon_down",
        "Stoch %K": "stoch_k",
        "Stoch %D": "stoch_d",
        "Price (Last)": "price_last",
        "52W High": "high_52w",
        "52W Low": "low_52w",
        "Return 1D %": "return_1d",
        "Return 1W %": "return_1w",
        "Return 1M %": "return_1m",
        "Return 3M %": "return_3m",
        "Return 6M %": "return_6m",
        "Return 1Y %": "return_1y",
        "CAGR 3Y %": "cagr_3y_pct",
        "CAGR 5Y %": "cagr_5y_pct",
        "Score Fundamental (0-100)": "score_fundamental",
        "Score Technical (0-100)": "score_technical",
        "Score Sentiment (0-100)": "score_sentiment",
        "Score Macro (0-100)": "score_macro",
        "Score Risk (0-100)": "score_risk",
        "Overall Score (0-100)": "overall_score",
        "Macro Composite (0-100)": "macro_composite",
        "Consensus Rating (1-5)": "consensus_rating",
        "Target Price": "target_price",
        "Upside %": "upside_pct",
        "# Analysts": "num_analysts",
        "Recommendation": "recommendation",
        "Moat Notes": "moat_notes",
        "Risk Notes": "risk_notes",
        "Catalysts": "catalysts",
        "ESG Score": "esg_score",
        "Sector Leader Ticker": "sector_leader_ticker",
        "Leader Gap on Metric": "leader_gap",
        "Sector Tailwinds/Headwinds": "sector_notes",
        "Sector P/E (Median)": "sector_pe_median",
        "Economic Moat Score": "economic_moat_score",
        "Altman Z-Score": "altman_z",
        "Piotroski F-Score": "piotroski_f",
        "Alpha 1Y %": "alpha_1y_pct",
        "Sortino 1Y": "sortino_1y",
        "Sector Relative Strength 6M %": "sector_relative_strength_6m_pct",
        "Quality Score": "quality_score",
        "Momentum Score": "momentum_score",
        "News Sentiment Score": "news_sentiment_score",
        "Social Media Sentiment": "social_sentiment",
    }

    for _, row in df.iterrows():
        ticker = str(row.get("Ticker", "")).strip()
        if not ticker or ticker.lower() == "nan":
            continue
            
        item = {
            "date": snapshot_date.isoformat(),
        }
        
        # Add mapped fields
        for tmpl_col, db_col in field_map.items():
            val = row.get(tmpl_col)
            if pd.isna(val) or val == "":
                item[db_col] = None
            elif isinstance(val, (np.float64, np.float32)):
                item[db_col] = float(val)
            elif isinstance(val, (np.int64, np.int32)):
                item[db_col] = int(val)
            else:
                item[db_col] = val
                
        payload.append(item)
    return payload

def upload_to_supabase(payload: list):
    if not payload:
        return
    
    supabase = get_supabase_client()
    try:
        # Extract snapshot date from first item to clear old records for the same day
        # This ensures 'created_at' timestamp reflects the latest successful run
        snapshot_date = payload[0].get("date")
        if snapshot_date:
            logger.info(f"Clearing existing records for {snapshot_date}...")
            supabase.table("daily_stocks").delete().eq("date", snapshot_date).execute()
            
        # Insert fresh records
        supabase.table("daily_stocks").insert(payload).execute()
        logger.info(f"Successfully uploaded {len(payload)} rows to Supabase")
    except Exception as e:
        logger.error(f"Error uploading to Supabase: {e}")
        raise

def run_daily_pipeline(limit: int = None, dry_run: bool = False):
    settings = load_settings()
    uni = build_universe(settings.indexes)
    
    if limit:
        logger.info(f"Limiting to first {limit} stocks for testing...")
        uni = uni.head(limit)
        
    rows = []
    failed_stocks = []  # Track failed stocks for retry
    batch_size = 20
    uni_list = list(uni.iterrows())
    
    def process_stock(row, retry_count=0):
        """Process a single stock with retry tracking"""
        try:
            res = enrich_stock(row["symbol"], settings)
            if res:
                res["symbol"] = row.get("symbol")
                return res, None
            else:
                return None, f"Empty result for {row.get('symbol')}"
        except Exception as e:
            return None, f"Error processing {row.get('symbol')}: {e}"
    
    logger.info(f"Enriching {len(uni_list)} stocks (Pass 1)...")
    for i in range(0, len(uni_list), batch_size):
        batch = uni_list[i:i + batch_size]
        with ThreadPoolExecutor(max_workers=min(settings.max_workers, len(batch))) as executor:
            futures = {executor.submit(process_stock, row): row for _, row in batch}
            for future in as_completed(futures):
                original_row = futures[future]
                result, error = future.result()
                if result:
                    rows.append(result)
                elif error:
                    logger.warning(error)
                    failed_stocks.append(original_row)
    
    # Retry failed stocks with delay between each (reduces rate limiting)
    if failed_stocks:
        logger.info(f"Retrying {len(failed_stocks)} failed stocks (Pass 2)...")
        time.sleep(5)  # Wait before retry pass
        
        retry_success = 0
        for row in failed_stocks:
            try:
                time.sleep(1)  # Rate limit: 1 second between retries
                res = enrich_stock(row["symbol"], settings)
                if res:
                    res["symbol"] = row.get("symbol")
                    rows.append(res)
                    retry_success += 1
                    logger.info(f"Retry successful: {row.get('symbol')}")
                else:
                    logger.error(f"Retry failed (empty result): {row.get('symbol')}")
            except Exception as e:
                logger.error(f"Retry failed: {row.get('symbol')} - {e}")
        
        logger.info(f"Retry pass complete: {retry_success}/{len(failed_stocks)} recovered")
    
    final_failed = len(failed_stocks) - sum(1 for r in rows if r.get("symbol") in [f.get("symbol") for f in failed_stocks])
    logger.info(f"Total stocks processed: {len(rows)}/{len(uni_list)} (failed: {final_failed})")

    if rows:
        stocks = pd.DataFrame(rows)
        
        # 1. Merge with universe metadata to get Sector, Industry, ISIN etc.
        meta_subset = uni.drop_duplicates(subset=["symbol"]).copy()
        merged_final = stocks.merge(meta_subset, on="symbol", how="left", suffixes=("", "_meta"))

        # 2. Compute scores
        try:
            from equity_engine.scoring import compute_subscores, overall_score
            logger.info("Computing scores...")
            subs = compute_subscores(merged_final)
            merged_final = pd.concat([merged_final, subs], axis=1)
            merged_final["Overall Score (0-100)"] = overall_score(subs, settings.weights).clip(0, 100)
        except Exception as e:
            logger.warning(f"Could not compute scores: {e}")
            
        # 3. Use the engine's prepare_output_df to get the 110-field structure
        from equity_engine.pipeline import prepare_output_df
        logger.info("Preparing 110-field output structure...")
        output_df = prepare_output_df(merged_final)
        
        # 4. Map to Supabase payload
        payload = prepare_daily_payload(output_df, date.today())
        
        if dry_run:
            logger.info("\n--- DRY RUN: Payload Summary ---")
            logger.info(f"Total records gathered: {len(payload)}")
            if payload:
                sample = payload[0]
                logger.info(f"Sample Ticker: {sample['ticker']}")
                logger.info(f"Sample Price: {sample['price_last']}")
                logger.info(f"Sample Overall Score: {sample['overall_score']}")
                logger.info(f"Sample Sector: {sample['sector']}")
                logger.info(f"Sample CAGR 3Y: {sample.get('cagr_3y_pct')}")
            logger.info("--- Dry run complete, skipping upload ---")
        else:
            upload_to_supabase(payload)
    else:
        logger.error("No stocks processed successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run daily enrichment and upload to Supabase")
    parser.add_argument("--limit", type=int, help="Limit the number of stocks to process")
    parser.add_argument("--dry-run", action="store_true", help="Run without uploading to Supabase")
    args = parser.parse_args()
    
    run_daily_pipeline(limit=args.limit, dry_run=args.dry_run)
