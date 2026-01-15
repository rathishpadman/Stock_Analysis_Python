
import os
import pandas as pd
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

def get_supabase_client():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    return create_client(url, key)

def calculate_risk_metrics(prices):
    """
    Calculate volatility, sharpe, drawdown from price series.
    prices: pandas Series of close prices (sorted by date ascending)
    """
    if len(prices) < 30:
        return {}
        
    # Log returns
    ret = np.log(prices / prices.shift(1)).dropna()
    
    # Volatility (Annualized)
    vol_30 = float(ret.tail(30).std() * np.sqrt(252) * 100)
    vol_90 = float(ret.tail(90).std() * np.sqrt(252) * 100)
    
    # Sharpe (Simplistic risk-free = 6%)
    rf_daily = 0.06 / 252
    excess_ret = ret - rf_daily
    if ret.std() == 0:
        sharpe = 0.0
    else:
        sharpe = float(np.sqrt(252) * excess_ret.mean() / ret.std())
        
    # Drawdown (Max in last 1 year)
    rolling_max = prices.cummax()
    drawdown = (prices - rolling_max) / rolling_max
    max_dd = float(drawdown.min() * 100)
    
    return {
        "volatility_30d": vol_30,
        "volatility_90d": vol_90,
        "sharpe_1y": sharpe,
        "max_drawdown_1y": max_dd
    }

def process_ticker(client, ticker):
    print(f"Processing {ticker}...")
    
    # 1. Fetch history order by date ASC
    res = client.table("daily_stocks").select("date, price_last").eq("ticker", ticker).order("date", desc=False).limit(300).execute()
    
    if not res.data or len(res.data) < 30:
        print(f"Not enough history for {ticker}")
        return

    df = pd.DataFrame(res.data)
    df['price'] = df['price_last'].astype(float)
    df = df.sort_values('date')
    
    # 2. Compute metrics
    metrics = calculate_risk_metrics(df['price'])
    # Add dummy beta for now (requires index data)
    metrics["beta_1y"] = 1.05 
    metrics["beta_3y"] = 1.10
    
    # 3. Update the LATEST record
    latest_date = df['date'].iloc[-1]
    
    print(f"Updating {ticker} ({latest_date}): {metrics}")
    
    try:
        client.table("daily_stocks").update(metrics).eq("ticker", ticker).eq("date", latest_date).execute()
        print("Success.")
    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    client = get_supabase_client()
    if client:
        # Run for the backfilled tickers
        tickers = ["NATIONALUM", "TATASTEEL", "INFY", "RELIANCE"]
        for t in tickers:
            process_ticker(client, t)
            time.sleep(0.5)
