"""
Aggregators for weekly and monthly OHLCV data resampling.

Provides functions to resample daily stock data to weekly (Mon-Fri) and 
monthly (calendar month) timeframes, with technical indicator calculations.
"""
from typing import Dict, Tuple
import numpy as np
import pandas as pd


def resample_to_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample daily OHLCV data to weekly (Monday-Friday).
    
    Args:
        df: DataFrame with DatetimeIndex and columns: Open, High, Low, Close, Volume
        
    Returns:
        DataFrame with weekly OHLCV data, indexed by week-ending Friday date
    """
    if df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    
    # Ensure datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = pd.to_datetime(df.index)
    
    # Resample to weekly (W-FRI means week ending Friday)
    weekly = df.resample('W-FRI').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna(subset=['Close'])
    
    return weekly


def resample_to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample daily OHLCV data to monthly (calendar month).
    
    Args:
        df: DataFrame with DatetimeIndex and columns: Open, High, Low, Close, Volume
        
    Returns:
        DataFrame with monthly OHLCV data, indexed by month-end date
    """
    if df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    
    # Ensure datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = pd.to_datetime(df.index)
    
    # Resample to month-end
    monthly = df.resample('ME').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna(subset=['Close'])
    
    return monthly


def add_weekly_technicals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to weekly OHLCV data.
    
    Adds:
    - Weekly Return %
    - Weekly SMA(10), SMA(20)
    - Weekly RSI(14)
    - 4-Week Return %, 13-Week Return %
    - 52W High/Low distances
    - Weekly Trend signal
    
    Args:
        df: Weekly OHLCV DataFrame
        
    Returns:
        DataFrame with added technical columns
    """
    if df.empty:
        return df
    
    df = df.copy()
    close = df['Close']
    
    # Weekly return
    df['Weekly Return %'] = close.pct_change() * 100
    
    # SMAs
    df['Weekly SMA(10)'] = close.rolling(window=10, min_periods=1).mean()
    df['Weekly SMA(20)'] = close.rolling(window=20, min_periods=1).mean()
    
    # RSI(14) on weekly data
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss
    df['Weekly RSI(14)'] = 100 - (100 / (1 + rs))
    
    # Multi-week returns
    df['4-Week Return %'] = close.pct_change(periods=4) * 100
    df['13-Week Return %'] = close.pct_change(periods=13) * 100
    
    # 52-week high/low distances
    rolling_52w_high = close.rolling(window=52, min_periods=1).max()
    rolling_52w_low = close.rolling(window=52, min_periods=1).min()
    df['52W High Distance %'] = ((rolling_52w_high - close) / rolling_52w_high) * 100
    df['52W Low Distance %'] = ((close - rolling_52w_low) / rolling_52w_low) * 100
    
    # Volume analysis
    df['Weekly Volume Ratio'] = df['Volume'] / df['Volume'].rolling(window=4, min_periods=1).mean()
    
    # Weekly trend signal
    df['Weekly Trend'] = df.apply(_weekly_trend_signal, axis=1)
    
    return df


def add_monthly_technicals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to monthly OHLCV data.
    
    Adds:
    - Monthly Return %
    - Monthly SMA(3), SMA(6), SMA(12)
    - 3M, 6M, 12M returns
    - Positive months count, best/worst months
    - Monthly Trend signal
    
    Args:
        df: Monthly OHLCV DataFrame
        
    Returns:
        DataFrame with added technical columns
    """
    if df.empty:
        return df
    
    df = df.copy()
    close = df['Close']
    
    # Monthly return
    df['Monthly Return %'] = close.pct_change() * 100
    
    # SMAs
    df['Monthly SMA(3)'] = close.rolling(window=3, min_periods=1).mean()
    df['Monthly SMA(6)'] = close.rolling(window=6, min_periods=1).mean()
    df['Monthly SMA(12)'] = close.rolling(window=12, min_periods=1).mean()
    
    # Multi-month returns
    df['3-Month Return %'] = close.pct_change(periods=3) * 100
    df['6-Month Return %'] = close.pct_change(periods=6) * 100
    df['12-Month Return %'] = close.pct_change(periods=12) * 100
    
    # Calculate YTD return (from Jan 1st of each year)
    df['YTD Return %'] = df.groupby(df.index.year).apply(
        lambda x: (x['Close'] / x['Close'].iloc[0] - 1) * 100
    ).reset_index(level=0, drop=True)
    
    # Rolling 12-month statistics
    rolling_returns = df['Monthly Return %'].rolling(window=12, min_periods=1)
    df['Positive Months (12M)'] = rolling_returns.apply(lambda x: (x > 0).sum())
    df['Avg Monthly Return (12M)'] = rolling_returns.mean()
    df['Best Month Return (12M)'] = rolling_returns.max()
    df['Worst Month Return (12M)'] = rolling_returns.min()
    
    # Monthly trend signal
    df['Monthly Trend'] = df.apply(_monthly_trend_signal, axis=1)
    
    return df


def _weekly_trend_signal(row: pd.Series) -> str:
    """Determine weekly trend based on SMA crossover."""
    try:
        close = row.get('Close', np.nan)
        sma10 = row.get('Weekly SMA(10)', np.nan)
        sma20 = row.get('Weekly SMA(20)', np.nan)
        
        if pd.isna(close) or pd.isna(sma10) or pd.isna(sma20):
            return 'N/A'
        
        if close > sma10 > sma20:
            return 'UP'
        elif close < sma10 < sma20:
            return 'DOWN'
        else:
            return 'SIDEWAYS'
    except Exception:
        return 'N/A'


def _monthly_trend_signal(row: pd.Series) -> str:
    """Determine monthly trend based on SMA crossover."""
    try:
        close = row.get('Close', np.nan)
        sma3 = row.get('Monthly SMA(3)', np.nan)
        sma6 = row.get('Monthly SMA(6)', np.nan)
        
        if pd.isna(close) or pd.isna(sma3) or pd.isna(sma6):
            return 'N/A'
        
        if close > sma3 > sma6:
            return 'UP'
        elif close < sma3 < sma6:
            return 'DOWN'
        else:
            return 'SIDEWAYS'
    except Exception:
        return 'N/A'


def compute_seasonality(df: pd.DataFrame, years: int = 5) -> Dict[str, float]:
    """
    Compute historical monthly seasonality averages.
    
    Args:
        df: Daily OHLCV DataFrame with at least 'years' of history
        years: Number of years to analyze (default 5)
        
    Returns:
        Dict with keys: Jan Avg %, Feb Avg %, ..., Dec Avg %, Best Month, Worst Month
    """
    if df.empty or 'Close' not in df.columns:
        return {}
    
    # Ensure datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = pd.to_datetime(df.index)
    
    # Filter to last N years
    cutoff = df.index.max() - pd.DateOffset(years=years)
    df_period = df[df.index >= cutoff]
    
    # Resample to monthly and compute returns
    monthly = resample_to_monthly(df_period)
    monthly['Return %'] = monthly['Close'].pct_change() * 100
    monthly['Month'] = monthly.index.month
    
    # Calculate average return by month
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    result = {}
    for i, name in enumerate(month_names, 1):
        month_returns = monthly[monthly['Month'] == i]['Return %']
        avg = month_returns.mean() if len(month_returns) > 0 else np.nan
        result[f'{name} Avg %'] = round(avg, 2) if pd.notna(avg) else np.nan
    
    # Find best and worst months
    valid_months = {k: v for k, v in result.items() if pd.notna(v)}
    if valid_months:
        best_key = max(valid_months, key=valid_months.get)
        worst_key = min(valid_months, key=valid_months.get)
        result['Best Month'] = best_key.replace(' Avg %', '')
        result['Worst Month'] = worst_key.replace(' Avg %', '')
    else:
        result['Best Month'] = 'N/A'
        result['Worst Month'] = 'N/A'
    
    return result
