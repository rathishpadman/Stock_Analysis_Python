
import yfinance as yf
import pandas as pd

def check_data():
    ticker = yf.Ticker("NATIONALUM.NS")
    
    print("--- Info Keys ---")
    keys = ["enterpriseToEbitda", "pegRatio", "beta", "forwardPE", "trailingPE"]
    for k in keys:
        print(f"{k}: {ticker.info.get(k)}")
        
    print("\n--- Balance Sheet ---")
    try:
        bs = ticker.balance_sheet
        if not bs.empty:
            print(bs.index.tolist()[:10]) # Print first 10 rows
            print("Total Assets:", bs.loc["Total Assets"].iloc[0] if "Total Assets" in bs.index else "N/A")
    except Exception as e:
        print(f"BS Error: {e}")

check_data()
