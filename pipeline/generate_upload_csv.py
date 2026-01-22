
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from equity_engine.data_sources import get_nse_index_constituents
from equity_engine.config import load_settings
from equity_engine.pipeline import enrich_stock, prepare_output_df
from equity_engine.scoring import compute_subscores, overall_score
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def generate_csv():
    settings = load_settings()
    index_name = "NIFTY 200"
    print(f"Fetching constituents for {index_name}...")
    
    try:
        uni = get_nse_index_constituents(index_name)
    except Exception as e:
        print(f"Failed to fetch index: {e}")
        return

    print(f"Found {len(uni)} symbols.")
    
    rows = []
    # Process all stocks
    symbols = uni['symbol'].tolist()
    
    # Enrich in parallel
    print("Enriching data (fetching history & calculating metrics)...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(enrich_stock, sym, settings): sym for sym in symbols}
        
        for future in tqdm(as_completed(futures), total=len(futures)):
            sym = futures[future]
            try:
                data = future.result()
                if data:
                    # Merge minimal metadata
                    meta_row = uni[uni['symbol'] == sym].iloc[0]
                    data['Company Name'] = meta_row.get('companyName', '')
                    data['Sector'] = meta_row.get('sector', '')
                    data['Industry'] = meta_row.get('industry', '')
                    rows.append(data)
            except Exception as e:
                print(f"Error {sym}: {e}")

    if not rows:
        print("No data processed.")
        return

    df = pd.DataFrame(rows)
    print(f"Processed {len(df)} records.")

    # Apply Scoring (Normalized)
    # We need to map columns to what scoring expects if enrich_stock didn't provide everything
    # prepare_output_df helps normalize names
    
    # 1. Create temporary match for scoring
    # enrich_stock returns dict with keys like "P/E (TTM)", "SMA20" etc.
    # so we can run compute_subscores directly on df
    
    print("Computing Scores...")
    # metrics might be missing, ensure they exist as NaNs
    req_cols = [
        "ROE TTM %", "ROA %", "Net Profit Margin %", "Gross Profit Margin %",
        "Operating Profit Margin %", "EPS Growth YoY %", "Revenue Growth YoY %",
        "Dividend Yield %", "FCF Yield %", "Interest Coverage",
        "P/E (TTM)", "P/B", "P/S Ratio", "Debt/Equity", "PEG Ratio",
        "Altman Z-Score", "Piotroski F-Score"
    ]
    for c in req_cols:
        if c not in df.columns:
            df[c] = np.nan

    subs = compute_subscores(df)
    overall = overall_score(subs, settings.weights).clip(0, 100)
    
    df["Score Fundamental (0-100)"] = subs["Score Fundamental (0-100)"]
    df["Score Technical (0-100)"] = subs["Score Technical (0-100)"]
    df["Score Risk (0-100)"] = subs["Score Risk (0-100)"]
    df["Score Sentiment (0-100)"] = subs["Score Sentiment (0-100)"]
    df["Overall Score (0-100)"] = overall
    
    # Prepare final DB-ready CSV
    # matching Supabase columns
    
    # Map to DB schema
    db_map = {
        "Ticker": "ticker",
        "Company Name": "company_name",
        "Sector": "sector",
        "Industry": "industry",
        "Price (Last)": "price_last",
        "Return 1D %": "return_1d",
        "Return 1W %": "return_1w",
        "Return 1M %": "return_1m",
        "Return 3M %": "return_3m",
        "Return 6M %": "return_6m",
        "Return 1Y %": "return_1y",
        "Volume": "volume", # enrich_stock doesn't typically return 'Volume' explicitly in the dict? check
        "Market Cap (INR Cr)": "market_cap_cr",
        "P/E (TTM)": "pe_ttm",
        "P/B": "pb",
        "Dividend Yield %": "dividend_yield_pct",
        "ROA %": "roa_pct",
        "ROE TTM %": "roe_ttm",
        "Debt/Equity": "debt_equity",
        "Interest Coverage": "interest_coverage",
        "EPS TTM": "eps_ttm",
        "Revenue TTM (INR Cr)": "revenue_ttm",
        "EBITDA TTM (INR Cr)": "ebitda_ttm",
        "Net Income TTM (INR Cr)": "net_income_ttm",
        "PEG Ratio": "peg_ratio",
        "Alpha 1Y %": "alpha_1y",
        "Beta 1Y": "beta_1y",
        "Beta 3Y": "beta_3y",
        "Sharpe 1Y": "sharpe_1y",
        "Sortino 1Y": "sortino_1y",
        "Volatility 30D %": "volatility_30d",
        "Volatility 90D %": "volatility_90d",
        "Max Drawdown 1Y %": "max_drawdown_1y",
        "RSI14": "rsi14",
        "SMA20": "sma20",
        "SMA50": "sma50",
        "SMA200": "sma200",
        "MACD Line": "macd_line",
        "MACD Signal": "macd_signal",
        "MACD Hist": "macd_hist",
        "ATR14": "atr14",
        "BB Upper": "bb_upper",
        "BB Lower": "bb_lower",
        "Overall Score (0-100)": "overall_score",
        "Score Fundamental (0-100)": "score_fundamental",
        "Score Technical (0-100)": "score_technical",
        "Score Risk (0-100)": "score_risk",
        "Score Sentiment (0-100)": "score_sentiment",
        "Score Macro (0-100)": "score_macro",
        "Altman Z-Score": "altman_z",
        "Piotroski F-Score": "piotroski_f",
        "Quality Score": "quality_score",
        "Momentum Score": "momentum_score",
        "Recommendations": "recommendation",
        "Moat Notes": "moat_notes",
        "Risk Notes": "risk_notes",
        "Catalysts": "catalysts"
    }
    
    final_rows = []
    
    timestamp = datetime.now().isoformat()
    
    for _, row in df.iterrows():
        new_row = {"date": datetime.now().strftime("%Y-%m-%d")}
        for src, dest in db_map.items():
            val = row.get(src)
            # handle NaNs -> None for CSV/JSON consistency or keep empty
            if pd.isna(val) or val == "":
                new_row[dest] = ""
            else:
                new_row[dest] = val
        final_rows.append(new_row)
        
    out_df = pd.DataFrame(final_rows)
    
    # Save
    out_path = "data/nifty200_staging.csv"
    os.makedirs("data", exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"Saved {len(out_df)} rows to {out_path}")
    print("Columns with potential blanks (check these!):")
    print(out_df.isnull().sum()[out_df.isnull().sum() > 0])

if __name__ == "__main__":
    generate_csv()
