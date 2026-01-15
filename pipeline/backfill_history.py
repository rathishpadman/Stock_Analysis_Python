
import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv
import time

load_dotenv()

def get_supabase_client():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        print("Error: credentials not found")
        return None
    return create_client(url, key)

def calculate_technicals(df):
    """Calculate indicators using standard pandas to avoid dependencies"""
    if len(df) < 200:
        return df
    
    close = df['Close']
    
    # SMAs
    df['sma20'] = close.rolling(window=20).mean()
    df['sma50'] = close.rolling(window=50).mean()
    df['sma200'] = close.rolling(window=200).mean()
    
    # RSI (Simple Rolling for robustness)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi14'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - macd_signal
    
    df['macd_line'] = macd_line
    df['macd_signal'] = macd_signal
    df['macd_hist'] = macd_hist
        
    return df

def backfill_ticker(ticker, client):
    print(f"Processing {ticker}...")
    try:
        # 1. Fetch data
        stock = yf.Ticker(ticker + ".NS")
        hist = stock.history(period="1y")
        
        if hist.empty:
            print(f"No data for {ticker}")
            return
            
        hist = calculate_technicals(hist)
        hist.reset_index(inplace=True)
        
        payload = []
        for _, row in hist.iterrows():
            # Skip if date is today (handled by daily pipeline) or no price
            if row['Date'].date() == datetime.now().date():
                continue
                
            item = {
                "ticker": ticker,
                "date": row['Date'].strftime('%Y-%m-%d'),
                "price_last": row['Close'],
                "high_52w": row['High'], # Approximation for this row
                "low_52w": row['Low'],   # Approximation
                "avg_volume_1w": row['Volume'], # Just storing daily vol here
                
                # Technicals
                "sma20": None if pd.isna(row['sma20']) else row['sma20'],
                "sma50": None if pd.isna(row['sma50']) else row['sma50'],
                "sma200": None if pd.isna(row['sma200']) else row['sma200'],
                "rsi14": None if pd.isna(row['rsi14']) else row['rsi14'],
                "macd_line": None if pd.isna(row.get('macd_line')) else row.get('macd_line'),
                "macd_signal": None if pd.isna(row.get('macd_signal')) else row.get('macd_signal'),
                "macd_hist": None if pd.isna(row.get('macd_hist')) else row.get('macd_hist')
            }
            # Clean NaNs
            clean_item = {k: v for k, v in item.items() if v is not None}
            payload.append(clean_item)
            
        # Batch insert
        batch_size = 100
        for i in range(0, len(payload), batch_size):
            batch = payload[i:i+batch_size]
            client.table("daily_stocks").upsert(batch, on_conflict="ticker,date").execute()
            
        print(f"Uploaded {len(payload)} days for {ticker}")
        
    except Exception as e:
        print(f"Error {ticker}: {e}")

if __name__ == "__main__":
    client = get_supabase_client()
    if client:
        # List of tickers to backfill (manual for now, or fetch all from DB)
        tickers = ["NATIONALUM", "TATASTEEL", "INFY", "RELIANCE"] # Start with key ones
        for t in tickers:
            backfill_ticker(t, client)
            time.sleep(1)
