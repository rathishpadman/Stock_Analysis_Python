"""
Monthly analysis module for stock data.

Computes monthly metrics, seasonality patterns, and aggregated analysis
for portfolio management and long-term trading insights.
"""
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from .aggregators import resample_to_monthly, add_monthly_technicals, compute_seasonality
from .data_sources import fetch_history_yf, to_yahoo


def compute_monthly_metrics(
    symbol: str,
    months: int = 24,
    yahoo_suffix: str = ".NS"
) -> pd.DataFrame:
    """
    Compute monthly metrics for a stock.
    
    Args:
        symbol: Stock symbol (without suffix)
        months: Number of months of history to return (default 24)
        yahoo_suffix: Yahoo Finance suffix (default .NS for NSE)
        
    Returns:
        DataFrame with monthly OHLCV and technical metrics
    """
    ticker = to_yahoo(symbol, yahoo_suffix)
    
    # Fetch enough daily history to cover requested months plus extra for calculations
    years_needed = max(3, (months // 12) + 2)
    df_daily = fetch_history_yf(ticker, years=years_needed)
    
    if df_daily.empty:
        return pd.DataFrame()
    
    # Resample to monthly
    df_monthly = resample_to_monthly(df_daily)
    
    if df_monthly.empty:
        return pd.DataFrame()
    
    # Add technical indicators
    df_monthly = add_monthly_technicals(df_monthly)
    
    # Keep only requested number of months
    df_monthly = df_monthly.tail(months)
    
    # Add metadata columns
    df_monthly['Ticker'] = symbol
    df_monthly['Month'] = df_monthly.index.strftime('%Y-%m')
    
    # Rename columns for clarity
    df_monthly = df_monthly.rename(columns={
        'Open': 'Monthly Open',
        'High': 'Monthly High',
        'Low': 'Monthly Low',
        'Close': 'Monthly Close',
        'Volume': 'Monthly Volume'
    })
    
    # Reorder columns
    col_order = [
        'Ticker', 'Month',
        'Monthly Open', 'Monthly High', 'Monthly Low', 'Monthly Close',
        'Monthly Return %', 'Monthly Volume',
        'YTD Return %',
        'Monthly SMA(3)', 'Monthly SMA(6)', 'Monthly SMA(12)',
        '3-Month Return %', '6-Month Return %', '12-Month Return %',
        'Positive Months (12M)', 'Avg Monthly Return (12M)',
        'Best Month Return (12M)', 'Worst Month Return (12M)',
        'Monthly Trend'
    ]
    
    existing_cols = [c for c in col_order if c in df_monthly.columns]
    df_monthly = df_monthly[existing_cols]
    
    return df_monthly


def compute_stock_seasonality(
    symbol: str,
    years: int = 5,
    yahoo_suffix: str = ".NS"
) -> Dict[str, float]:
    """
    Compute historical monthly seasonality for a stock.
    
    Args:
        symbol: Stock symbol
        years: Number of years to analyze
        yahoo_suffix: Yahoo suffix
        
    Returns:
        Dict with monthly averages and best/worst month
    """
    ticker = to_yahoo(symbol, yahoo_suffix)
    df_daily = fetch_history_yf(ticker, years=years + 1)  # Extra year for calculations
    
    if df_daily.empty:
        return {'Ticker': symbol}
    
    seasonality = compute_seasonality(df_daily, years=years)
    seasonality['Ticker'] = symbol
    
    return seasonality


def compute_monthly_summary(symbol: str, yahoo_suffix: str = ".NS") -> Dict:
    """
    Compute a summary row of monthly analysis for a stock.
    
    Returns the latest month's data plus key monthly metrics.
    
    Args:
        symbol: Stock symbol
        yahoo_suffix: Yahoo suffix
        
    Returns:
        Dict with monthly summary metrics
    """
    df_monthly = compute_monthly_metrics(symbol, months=24, yahoo_suffix=yahoo_suffix)
    
    if df_monthly.empty:
        return {'Ticker': symbol, 'Monthly Data': 'No Data'}
    
    latest = df_monthly.iloc[-1].to_dict()
    
    # Add some rolling stats
    if len(df_monthly) >= 3:
        latest['Avg Monthly Return (3M)'] = df_monthly['Monthly Return %'].tail(3).mean()
    if len(df_monthly) >= 12:
        latest['Monthly Win Rate (12M)'] = (df_monthly['Monthly Return %'].tail(12) > 0).mean() * 100
    
    # Add seasonality
    seasonality = compute_stock_seasonality(symbol, years=5, yahoo_suffix=yahoo_suffix)
    for k, v in seasonality.items():
        if k != 'Ticker':
            latest[f'Seasonality {k}'] = v
    
    return latest


def build_monthly_analysis_sheet(
    symbols: List[str],
    company_names: Dict[str, str],
    months: int = 24,
    yahoo_suffix: str = ".NS"
) -> pd.DataFrame:
    """
    Build the Monthly_Analysis sheet for all symbols.
    
    Args:
        symbols: List of stock symbols
        company_names: Dict mapping symbol to company name
        months: Number of months per stock
        yahoo_suffix: Yahoo suffix
        
    Returns:
        DataFrame ready to write to Excel sheet
    """
    all_monthly = []
    
    for symbol in symbols:
        try:
            df = compute_monthly_metrics(symbol, months=months, yahoo_suffix=yahoo_suffix)
            if not df.empty:
                df['Company Name'] = company_names.get(symbol, '')
                all_monthly.append(df)
        except Exception as e:
            print(f"Warning: Failed to compute monthly metrics for {symbol}: {e}")
            continue
    
    if not all_monthly:
        return pd.DataFrame()
    
    result = pd.concat(all_monthly, ignore_index=True)
    
    # Ensure Company Name is second column
    cols = list(result.columns)
    if 'Company Name' in cols:
        cols.remove('Company Name')
        cols.insert(1, 'Company Name')
        result = result[cols]
    
    return result


def build_seasonality_sheet(
    symbols: List[str],
    company_names: Dict[str, str],
    years: int = 5,
    yahoo_suffix: str = ".NS"
) -> pd.DataFrame:
    """
    Build a seasonality summary sheet for all symbols.
    
    Args:
        symbols: List of stock symbols
        company_names: Dict mapping symbol to company name
        years: Number of years for seasonality calculation
        yahoo_suffix: Yahoo suffix
        
    Returns:
        DataFrame with one row per stock showing monthly seasonality
    """
    rows = []
    
    for symbol in symbols:
        try:
            seasonality = compute_stock_seasonality(symbol, years=years, yahoo_suffix=yahoo_suffix)
            seasonality['Company Name'] = company_names.get(symbol, '')
            rows.append(seasonality)
        except Exception as e:
            print(f"Warning: Failed to compute seasonality for {symbol}: {e}")
            continue
    
    if not rows:
        return pd.DataFrame()
    
    result = pd.DataFrame(rows)
    
    # Reorder columns
    col_order = [
        'Ticker', 'Company Name',
        'Jan Avg %', 'Feb Avg %', 'Mar Avg %', 'Apr Avg %',
        'May Avg %', 'Jun Avg %', 'Jul Avg %', 'Aug Avg %',
        'Sep Avg %', 'Oct Avg %', 'Nov Avg %', 'Dec Avg %',
        'Best Month', 'Worst Month'
    ]
    
    existing_cols = [c for c in col_order if c in result.columns]
    result = result[existing_cols]
    
    return result
