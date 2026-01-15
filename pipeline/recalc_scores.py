
import os
import pandas as pd
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from equity_engine.scoring import compute_subscores, overall_score
from equity_engine.config import load_settings

load_dotenv()

def get_supabase_client():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    return create_client(url, key)

def recalc_scores():
    client = get_supabase_client()
    if not client: return
    
    print("Fetching today's snapshot...")
    # Fetch all columns for today to re-score
    res = client.table("daily_stocks").select("*").order("date", desc=True).limit(500).execute()
    
    if not res.data:
        print("No data found")
        return
        
    df = pd.DataFrame(res.data)
    print(f"Loaded {len(df)} records. Columns: {df.columns.tolist()[:5]}...")
    
    # 1. Compute Subscores (Normalization happens here)
    # Ensure numeric types
    numeric_cols = ["pe_ttm", "roe_ttm", "market_cap_cr", "volatility_30d", "sharpe_1y", "altman_z"]
    # Map db columns to template columns expected by scoring.py
    # This is tricky because scoring.py expects "P/E (TTM)" but DB has "pe_ttm"
    # We need to map DB -> Template
    
    db_to_tmpl = {
        "pe_ttm": "P/E (TTM)",
        "pb": "P/B",
        "roe_ttm": "ROE TTM %",
        "roa_pct": "ROA %",
        "dividend_yield_pct": "Dividend Yield %",
        "debt_equity": "Debt/Equity",
        "volatility_30d": "Volatility 30D %",
        "volatility_90d": "Volatility 90D %",
        "max_drawdown_1y": "Max Drawdown 1Y %",
        "sharpe_1y": "Sharpe 1Y",
        "price_last": "Price (Last)",
        "sma50": "SMA50",
        "sma200": "SMA200",
        "rsi14": "RSI14"
        # Add others as needed for scoring
    }
    
    # create a scoring-friendly dataframe
    score_df = pd.DataFrame(index=df.index)
    for db_col, tmpl_col in db_to_tmpl.items():
        if db_col in df.columns:
            score_df[tmpl_col] = pd.to_numeric(df[db_col], errors='coerce')
            
    print("Computing new normalized scores...")
    subs = compute_subscores(score_df)
    
    # Load defaults
    settings = load_settings()
    overall = overall_score(subs, settings.weights).clip(0, 100)
    
    # Update Supabase
    print("Updating Supabase...")
    for idx, row in df.iterrows():
        ticker = row['ticker']
        date_str = row['date']
        
        updates = {
            "score_fundamental": None if pd.isna(subs.loc[idx, "Score Fundamental (0-100)"]) else float(subs.loc[idx, "Score Fundamental (0-100)"]),
            "score_technical": None if pd.isna(subs.loc[idx, "Score Technical (0-100)"]) else float(subs.loc[idx, "Score Technical (0-100)"]),
            "score_risk": None if pd.isna(subs.loc[idx, "Score Risk (0-100)"]) else float(subs.loc[idx, "Score Risk (0-100)"]),
            "score_sentiment": None if pd.isna(subs.loc[idx, "Score Sentiment (0-100)"]) else float(subs.loc[idx, "Score Sentiment (0-100)"]),
            "overall_score": None if pd.isna(overall[idx]) else float(overall[idx])
        }
        
        try:
            client.table("daily_stocks").update(updates).eq("ticker", ticker).eq("date", date_str).execute()
        except Exception as e:
            print(f"Failed {ticker}: {e}")
            
    print("Recalculation complete.")

if __name__ == "__main__":
    recalc_scores()
