"""
Weekly analysis module for stock data.

Computes weekly metrics, patterns, and aggregated analysis
for swing trading insights.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from .aggregators import resample_to_weekly, add_weekly_technicals
from .data_sources import fetch_history_yf, to_yahoo


def compute_weekly_metrics(
    symbol: str,
    weeks: int = 52,
    yahoo_suffix: str = ".NS"
) -> pd.DataFrame:
    """
    Compute weekly metrics for a stock.
    
    Args:
        symbol: Stock symbol (without suffix)
        weeks: Number of weeks of history to return (default 52)
        yahoo_suffix: Yahoo Finance suffix (default .NS for NSE)
        
    Returns:
        DataFrame with weekly OHLCV and technical metrics
    """
    ticker = to_yahoo(symbol, yahoo_suffix)
    
    # Fetch enough daily history to cover requested weeks
    years_needed = max(2, (weeks // 52) + 1)
    df_daily = fetch_history_yf(ticker, years=years_needed)
    
    if df_daily.empty:
        return pd.DataFrame()
    
    # Resample to weekly
    df_weekly = resample_to_weekly(df_daily)
    
    if df_weekly.empty:
        return pd.DataFrame()
    
    # Add technical indicators
    df_weekly = add_weekly_technicals(df_weekly)
    
    # Keep only requested number of weeks
    df_weekly = df_weekly.tail(weeks)
    
    # Add metadata columns
    df_weekly['Ticker'] = symbol
    df_weekly['Week Ending'] = df_weekly.index.strftime('%Y-%m-%d')
    
    # Rename columns for clarity
    df_weekly = df_weekly.rename(columns={
        'Open': 'Weekly Open',
        'High': 'Weekly High',
        'Low': 'Weekly Low',
        'Close': 'Weekly Close',
        'Volume': 'Weekly Volume'
    })
    
    # Reorder columns
    col_order = [
        'Ticker', 'Week Ending',
        'Weekly Open', 'Weekly High', 'Weekly Low', 'Weekly Close',
        'Weekly Return %', 'Weekly Volume', 'Weekly Volume Ratio',
        'Weekly RSI(14)', 'Weekly SMA(10)', 'Weekly SMA(20)',
        '4-Week Return %', '13-Week Return %',
        '52W High Distance %', '52W Low Distance %',
        'Weekly Trend'
    ]
    
    existing_cols = [c for c in col_order if c in df_weekly.columns]
    df_weekly = df_weekly[existing_cols]
    
    return df_weekly


def compute_weekly_summary(symbol: str, yahoo_suffix: str = ".NS") -> Dict:
    """
    Compute a summary row of weekly analysis for a stock.
    
    Returns the latest week's data plus key weekly metrics.
    
    Args:
        symbol: Stock symbol
        yahoo_suffix: Yahoo suffix
        
    Returns:
        Dict with weekly summary metrics
    """
    df_weekly = compute_weekly_metrics(symbol, weeks=52, yahoo_suffix=yahoo_suffix)
    
    if df_weekly.empty:
        return {'Ticker': symbol, 'Weekly Data': 'No Data'}
    
    latest = df_weekly.iloc[-1].to_dict()
    
    # Add some rolling stats
    if len(df_weekly) >= 4:
        latest['Avg Weekly Return (4W)'] = df_weekly['Weekly Return %'].tail(4).mean()
    if len(df_weekly) >= 13:
        latest['Avg Weekly Return (13W)'] = df_weekly['Weekly Return %'].tail(13).mean()
        latest['Weekly Win Rate (13W)'] = (df_weekly['Weekly Return %'].tail(13) > 0).mean() * 100
    
    return latest


def build_weekly_analysis_sheet(
    symbols: List[str],
    company_names: Dict[str, str],
    weeks: int = 52,
    yahoo_suffix: str = ".NS"
) -> pd.DataFrame:
    """
    Build the Weekly_Analysis sheet for all symbols.
    
    Args:
        symbols: List of stock symbols
        company_names: Dict mapping symbol to company name
        weeks: Number of weeks per stock
        yahoo_suffix: Yahoo suffix
        
    Returns:
        DataFrame ready to write to Excel sheet
    """
    all_weekly = []
    
    for symbol in symbols:
        try:
            df = compute_weekly_metrics(symbol, weeks=weeks, yahoo_suffix=yahoo_suffix)
            if not df.empty:
                df['Company Name'] = company_names.get(symbol, '')
                all_weekly.append(df)
        except Exception as e:
            print(f"Warning: Failed to compute weekly metrics for {symbol}: {e}")
            continue
    
    if not all_weekly:
        return pd.DataFrame()
    
    result = pd.concat(all_weekly, ignore_index=True)
    
    # Ensure Company Name is second column
    cols = list(result.columns)
    if 'Company Name' in cols:
        cols.remove('Company Name')
        cols.insert(1, 'Company Name')
        result = result[cols]
    
    return result
