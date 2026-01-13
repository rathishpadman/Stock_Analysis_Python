"""Canonical technical indicator implementations for the project.

Functions return floats or NaN where appropriate.
"""
from typing import Dict
import pandas as pd


def compute_technicals(df: pd.DataFrame) -> Dict[str, float]:
    close = df['Close']
    high = df['High']
    low = df['Low']
    vol = df['Volume']

    out = {}
    out['SMA20'] = close.rolling(window=20).mean().iloc[-1]
    out['SMA50'] = close.rolling(window=50).mean().iloc[-1]
    out['SMA200'] = close.rolling(window=200).mean().iloc[-1]

    # RSI14 using Wilder smoothing
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/14, adjust=False).mean()
    ma_down = down.ewm(alpha=1/14, adjust=False).mean()
    rs = ma_up / ma_down
    out['RSI14'] = (100 - (100 / (1 + rs))).iloc[-1]

    # MACD 12/26/9
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    out['MACD Line'] = macd_line.iloc[-1]
    out['MACD Signal'] = macd_signal.iloc[-1]
    out['MACD Hist'] = out['MACD Line'] - out['MACD Signal']

    # ATR14 (Wilder)
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    out['ATR14'] = tr.ewm(alpha=1/14, adjust=False).mean().iloc[-1]

    # Bollinger
    # Bollinger: prefer 20-day window but fall back to shorter windows when history is limited
    try:
        window = 20
        if len(close.dropna()) >= 20:
            ma = close.rolling(window=window).mean()
            sd = close.rolling(window=window).std()
            out['BB Upper'] = (ma + 2 * sd).iloc[-1]
            out['BB Lower'] = (ma - 2 * sd).iloc[-1]
            out['_BB_confidence'] = 0.9
        else:
            # fallback: use smaller window if at least 10 days exist
            available = len(close.dropna())
            if available >= 10:
                win2 = max(10, available)
                ma = close.rolling(window=win2).mean()
                sd = close.rolling(window=win2).std()
                out['BB Upper'] = (ma + 2 * sd).iloc[-1]
                out['BB Lower'] = (ma - 2 * sd).iloc[-1]
                # lower confidence since window < 20
                out['_BB_confidence'] = 0.5
            else:
                out['BB Upper'] = float('nan')
                out['BB Lower'] = float('nan')
                out['_BB_confidence'] = 0.0
    except Exception:
        out['BB Upper'] = float('nan')
        out['BB Lower'] = float('nan')
        out['_BB_confidence'] = 0.0

    # OBV
    direction = close.diff().fillna(0).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    obv = (direction * vol).cumsum()
    out['OBV'] = obv.iloc[-1]

    # ADX14 approximation
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    atr = tr.ewm(alpha=1/14, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1/14, adjust=False).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(alpha=1/14, adjust=False).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    out['ADX14'] = dx.ewm(alpha=1/14, adjust=False).mean().iloc[-1]

    # Aroon (25)
    period = 25
    highest_idx = close[-period:].idxmax()
    lowest_idx = close[-period:].idxmin()
    days_since_high = (len(close) - 1) - close.index.get_loc(highest_idx)
    days_since_low = (len(close) - 1) - close.index.get_loc(lowest_idx)
    out['Aroon Up'] = ((period - days_since_high) / period) * 100
    out['Aroon Down'] = ((period - days_since_low) / period) * 100

    # Stochastic
    low14 = low.rolling(window=14).min()
    high14 = high.rolling(window=14).max()
    stoch_k = 100 * (close - low14) / (high14 - low14)
    stoch_d = stoch_k.rolling(window=3).mean()
    out['Stoch %K'] = stoch_k.iloc[-1]
    out['Stoch %D'] = stoch_d.iloc[-1]

    return out
