import os
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
from equity_engine.config import load_settings
from equity_engine.monthly_analysis import build_monthly_analysis_sheet, build_seasonality_sheet

def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    return create_client(url, key)

def prepare_monthly_payload(df: pd.DataFrame) -> list:
    payload = []
    df = df.replace([np.inf, -np.inf], np.nan)
    for _, row in df.iterrows():
        item = {
            "ticker": str(row.get("Ticker", "")),
            "company_name": str(row.get("Company Name", "")),
            "month": str(row.get("Month", "")),
            "monthly_open": row.get("Monthly Open"),
            "monthly_high": row.get("Monthly High"),
            "monthly_low": row.get("Monthly Low"),
            "monthly_close": row.get("Monthly Close"),
            "monthly_return_pct": row.get("Monthly Return %"),
            "monthly_volume": row.get("Monthly Volume"),
            "ytd_return_pct": row.get("YTD Return %"),
            "monthly_sma3": row.get("Monthly SMA(3)"),
            "monthly_sma6": row.get("Monthly SMA(6)"),
            "monthly_sma12": row.get("Monthly SMA(12)"),
            "return_3m": row.get("3-Month Return %"),
            "return_6m": row.get("6-Month Return %"),
            "return_12m": row.get("12-Month Return %"),
            "positive_months_12m": row.get("Pos Months (12M)"),
            "avg_monthly_return_12m": row.get("Avg Monthly Ret (12M)"),
            "best_month_return_12m": row.get("Best Month Ret (12M)"),
            "worst_month_return_12m": row.get("Worst Month Ret (12M)"),
            "monthly_trend": str(row.get("Monthly Trend", ""))
        }
        for k, v in item.items():
            if pd.isna(v): item[k] = None
        payload.append(item)
    return payload

def prepare_seasonality_payload(df: pd.DataFrame) -> list:
    payload = []
    df = df.replace([np.inf, -np.inf], np.nan)
    for _, row in df.iterrows():
        item = {
            "ticker": str(row.get("Ticker", "")),
            "company_name": str(row.get("Company Name", "")),
            "jan_avg": row.get("Jan Avg %"),
            "feb_avg": row.get("Feb Avg %"),
            "mar_avg": row.get("Mar Avg %"),
            "apr_avg": row.get("Apr Avg %"),
            "may_avg": row.get("May Avg %"),
            "jun_avg": row.get("Jun Avg %"),
            "jul_avg": row.get("Jul Avg %"),
            "aug_avg": row.get("Aug Avg %"),
            "sep_avg": row.get("Sep Avg %"),
            "oct_avg": row.get("Oct Avg %"),
            "nov_avg": row.get("Nov Avg %"),
            "dec_avg": row.get("Dec Avg %"),
            "best_month": str(row.get("Best Month", "")),
            "worst_month": str(row.get("Worst Month", ""))
        }
        for k, v in item.items():
            if pd.isna(v): item[k] = None
        payload.append(item)
    return payload

def run_monthly_pipeline():
    settings = load_settings()
    from equity_engine.pipeline import build_universe
    uni = build_universe(settings.indexes)
    symbols = uni["symbol"].tolist()
    company_names = dict(zip(uni["symbol"], uni.get("companyName", uni.get("longName", ""))))
    
    supabase = get_supabase_client()

    # 1. Monthly Analysis
    print("Running Monthly Analysis...")
    monthly_df = build_monthly_analysis_sheet(symbols, company_names, settings.monthly_history_months, settings.yahoo_suffix)
    if not monthly_df.empty:
        payload = prepare_monthly_payload(monthly_df)
        supabase.table("monthly_analysis").upsert(payload).execute()
        print(f"Uploaded {len(payload)} monthly rows")

    # 2. Seasonality
    print("Running Seasonality Analysis...")
    seasonality_df = build_seasonality_sheet(symbols, company_names, settings.seasonality_years, settings.yahoo_suffix)
    if not seasonality_df.empty:
        payload = prepare_seasonality_payload(seasonality_df)
        supabase.table("seasonality").upsert(payload).execute()
        print(f"Uploaded {len(payload)} seasonality rows")

if __name__ == "__main__":
    run_monthly_pipeline()
