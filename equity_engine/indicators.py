from typing import Dict, List
import numpy as np
import pandas as pd
import logging

try:
    import pandas_ta as ta
except Exception:
    ta = None
    
def compute_returns(close: pd.Series, windows: List[int]) -> Dict[str, float]:
    out = {}
    for w in windows:
        if len(close) > w:
            try:
                ret = float((close.iloc[-1] / close.iloc[-1-w] - 1) * 100.0)
                if np.isfinite(ret):  # Check for inf/nan
                    out[f"Return {w}d %"] = ret
            except Exception:
                pass
    return out

def compute_cagr(close: pd.Series, years: int) -> float:
    need = years*252
    if len(close) < need:
        return float("nan")
    start = close.iloc[-need]
    end = close.iloc[-1]
    if start <= 0:
        return float("nan")
    return float((end / start)**(1/years) - 1)

def add_technicals(df: pd.DataFrame, sma_windows=(20,50,200), rsi_window=14, macd=(12,26,9)) -> pd.DataFrame:
    import logging
    logger = logging.getLogger(__name__)
    
    if ta is None:
        logger.error("pandas_ta not available - technical indicators will be empty")
        # add empty columns if ta not available
        for w in sma_windows:
            df[f"SMA{w}"] = np.nan
        for col in ["RSI14","MACD Line","MACD Signal","MACD Hist","ATR14","BB Upper","BB Lower",
                    "OBV","ADL","ADX14","Aroon Up","Aroon Down","Stoch %K","Stoch %D"]:
            df[col] = np.nan
        return df
    
    # Verify we have enough data
    min_required = max(sma_windows)  # Longest SMA window
    if len(df) < min_required:
        logger.warning(f"Not enough data points ({len(df)}) for technical analysis. Need at least {min_required}")
        return df

    # SMA/RSI/MACD
    try:
        close = df["Close"]
        high, low, vol = df["High"], df["Low"], df["Volume"]
        
        # Check for NaN values
        if close.isna().any():
            logger.warning(f"Close price contains {close.isna().sum()} NaN values")
        
        for w in sma_windows:
            try:
                df[f"SMA{w}"] = ta.sma(close, length=w)
            except Exception as e:
                logger.error(f"Failed to calculate SMA{w}: {e}")
                df[f"SMA{w}"] = np.nan
                
        try:
            df["RSI14"] = ta.rsi(close, length=rsi_window)
        except Exception as e:
            logger.error(f"Failed to calculate RSI14: {e}")
            df["RSI14"] = np.nan
            
        fast, slow, signal = macd
        try:
            mac = ta.macd(close, fast=fast, slow=slow, signal=signal)
        except Exception as e:
            logger.error(f"Failed to calculate MACD: {e}")
            mac = None
    except Exception as e:
        logger.error(f"Failed to compute SMA/RSI/MACD block: {e}")
        # ensure consistent dataframe shape by setting expected columns to NaN, then exit early
        for w in sma_windows:
            df[f"SMA{w}"] = np.nan
        df["RSI14"] = np.nan
        df["MACD Line"] = np.nan
        df["MACD Signal"] = np.nan
        df["MACD Hist"] = np.nan
        return df
    if mac is not None:
        df["MACD Line"] = mac.get(f"MACD_{fast}_{slow}_{signal}")
        df["MACD Signal"] = mac.get(f"MACDs_{fast}_{slow}_{signal}")
        df["MACD Hist"] = mac.get(f"MACDh_{fast}_{slow}_{signal}")
    df["ATR14"] = ta.atr(high, low, close, length=14)
    bb = ta.bbands(close, length=20, std=2)
    if bb is not None:
        df["BB Upper"] = bb.get("BBU_20_2.0")
        df["BB Lower"] = bb.get("BBL_20_2.0")

    # Additional technicals requested
    # OBV, Chaikin Accumulation/Distribution (ADL), ADX, Aroon, Stochastic
    df["OBV"] = ta.obv(close, vol)
    ad = ta.ad(high, low, close, vol)  # Chaikin A/D line
    df["ADL"] = ad
    df["ADX14"] = ta.adx(high, low, close, length=14)["ADX_14"]
    aroon = ta.aroon(high, low, length=25)  # typical window
    df["Aroon Up"] = aroon["AROONU_25"]
    df["Aroon Down"] = aroon["AROOND_25"]
    stoch = ta.stoch(high, low, close, k=14, d=3, smooth_k=3)
    df["Stoch %K"] = stoch["STOCHk_14_3_3"]
    df["Stoch %D"] = stoch["STOCHd_14_3_3"]
    return df

def risk_stats(close: pd.Series, rf_annual_pct: float, lookback: int = 252) -> Dict[str, float]:
    ret = np.log(close/close.shift(1))
    tail = ret.dropna().iloc[-lookback:]
    vol_30 = float(ret.tail(30).std()*np.sqrt(252)*100)
    vol_90 = float(ret.tail(90).std()*np.sqrt(252)*100)
    # Max drawdown 1Y from price series
    px = close.tail(252)
    dd = (px/px.cummax() - 1).min()*100.0
    sharpe = float((tail.mean()*252 - rf_annual_pct/100) / (tail.std()*np.sqrt(252))) if tail.std()>0 else float("nan")
    return {"Volatility 30D %": vol_30, "Volatility 90D %": vol_90, "Max Drawdown 1Y %": float(dd), "Sharpe 1Y": sharpe}
