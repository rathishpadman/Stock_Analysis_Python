"""Full-field validation for RELIANCE against Yahoo Finance and computed technicals.

This script reads `OCT25/reliance_analysis.csv`, fetches Yahoo info and price history,
computes several technical indicators, and compares as many CSV fields as possible.
Outputs a CSV `tools/validation_full_report.csv` with comparisons and flags.
"""
from pathlib import Path
import csv
import math
import sys
from typing import Dict, Any

import pandas as pd
import yfinance as yf


ROOT = Path(__file__).parents[1]
CSV_PATH = ROOT / 'OCT25' / 'reliance_analysis.csv'
OUT_PATH = Path(__file__).parent / 'validation_full_report.csv'


def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


def compute_technical_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    out = {}
    close = df['Close']
    high = df['High']
    low = df['Low']
    vol = df['Volume']

    # SMAs
    out['SMA20'] = close.rolling(window=20).mean().iloc[-1]
    out['SMA50'] = close.rolling(window=50).mean().iloc[-1]
    out['SMA200'] = close.rolling(window=200).mean().iloc[-1]

    # RSI14
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(com=13, adjust=False).mean()
    ma_down = down.ewm(com=13, adjust=False).mean()
    rs = ma_up / ma_down
    out['RSI14'] = (100 - (100 / (1 + rs))).iloc[-1]

    # MACD (12,26,9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    out['MACD Line'] = macd_line.iloc[-1]
    out['MACD Signal'] = macd_signal.iloc[-1]
    out['MACD Hist'] = out['MACD Line'] - out['MACD Signal']

    # ATR14
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    out['ATR14'] = tr.rolling(window=14).mean().iloc[-1]

    # Bollinger Bands (20, 2sd)
    ma20 = close.rolling(window=20).mean()
    sd20 = close.rolling(window=20).std()
    out['BB Upper'] = (ma20 + 2 * sd20).iloc[-1]
    out['BB Lower'] = (ma20 - 2 * sd20).iloc[-1]

    # OBV
    direction = close.diff().fillna(0).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    obv = (direction * vol).cumsum()
    out['OBV'] = obv.iloc[-1]

    # ADX14 (Wilder smoothing)
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    tr = tr
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

    # Stochastic %K %D (14,3)
    low14 = low.rolling(window=14).min()
    high14 = high.rolling(window=14).max()
    stoch_k = 100 * (close - low14) / (high14 - low14)
    stoch_d = stoch_k.rolling(window=3).mean()
    out['Stoch %K'] = stoch_k.iloc[-1]
    out['Stoch %D'] = stoch_d.iloc[-1]

    return out


def main():
    if not CSV_PATH.exists():
        print('CSV not found at', CSV_PATH)
        sys.exit(1)

    kv = {}
    # read key,value pairs
    # Read without assuming a header row; the file is key,value rows (two columns)
    df = pd.read_csv(CSV_PATH, header=None, dtype=str)
    if df.shape[1] == 2:
        kv = dict(zip(df.iloc[:, 0].astype(str).str.strip(), df.iloc[:, 1].astype(str).str.strip()))
    else:
        print('Unexpected CSV shape; aborting')
        sys.exit(1)

    ticker = kv.get('Ticker')
    if not ticker:
        print('Ticker not found in CSV')
        sys.exit(1)

    yahoo_t = ticker + '.NS' if '.' not in ticker else ticker
    t = yf.Ticker(yahoo_t)
    info = t.info

    # fetch history for technicals; need at least 300 days
    hist = t.history(period='2y', interval='1d')
    if hist.empty:
        print('No history data from Yahoo; cannot compute technicals')
        sys.exit(1)

    tech = compute_technical_indicators(hist)

    # Mapping between CSV keys and either info keys or tech keys or computed conversions
    comparisons = []

    def cmp_field(csv_key, get_value_fn, transform_csv=lambda x: safe_float(x)):
        csv_val_raw = kv.get(csv_key)
        csv_val = transform_csv(csv_val_raw)
        try:
            ref_val = get_value_fn()
        except Exception:
            ref_val = None
        # normalise slight floats
        def almost_equal(a, b, rel=0.01):
            if a is None or b is None:
                return False
            try:
                if a == 0 and b == 0:
                    return True
                return abs(a - b) / max(abs(a), abs(b)) <= rel
            except Exception:
                return False

        match = almost_equal(csv_val, ref_val)
        comparisons.append({'field': csv_key, 'csv_raw': csv_val_raw, 'csv_val': csv_val, 'ref_val': ref_val, 'match': match})

    # simple direct mappings
    cmp_field('Price (Last)', lambda: info.get('regularMarketPrice'))
    cmp_field('Market Cap (INR Cr)', lambda: info.get('marketCap') / 1e7 if info.get('marketCap') else None)
    cmp_field('Shares Outstanding', lambda: info.get('sharesOutstanding'))
    cmp_field('P/E (TTM)', lambda: info.get('trailingPE'))
    cmp_field('EPS TTM', lambda: info.get('trailingEps'))
    cmp_field('Dividend Yield %', lambda: (info.get('dividendYield') * 100) if info.get('dividendYield') else None, transform_csv=lambda x: safe_float(x))
    cmp_field('Revenue TTM (INR Cr)', lambda: info.get('totalRevenue') / 1e7 if info.get('totalRevenue') else None)
    cmp_field('Revenue Growth YoY %', lambda: (info.get('revenueGrowth') * 100) if info.get('revenueGrowth') else None)
    cmp_field('P/B', lambda: info.get('priceToBook'))
    cmp_field('EV/EBITDA (TTM)', lambda: info.get('enterpriseToEbitda'))
    cmp_field('ROE TTM %', lambda: (info.get('returnOnEquity') * 100) if info.get('returnOnEquity') else None)
    cmp_field('ROA %', lambda: (info.get('returnOnAssets') * 100) if info.get('returnOnAssets') else None)
    cmp_field('Current Ratio', lambda: info.get('currentRatio'))
    cmp_field('Quick Ratio', lambda: info.get('quickRatio'))

    # technicals from history
    cmp_field('SMA20', lambda: tech.get('SMA20'))
    cmp_field('SMA50', lambda: tech.get('SMA50'))
    cmp_field('SMA200', lambda: tech.get('SMA200'))
    cmp_field('RSI14', lambda: tech.get('RSI14'))
    cmp_field('MACD Line', lambda: tech.get('MACD Line'))
    cmp_field('MACD Signal', lambda: tech.get('MACD Signal'))
    cmp_field('MACD Hist', lambda: tech.get('MACD Hist'))
    cmp_field('ATR14', lambda: tech.get('ATR14'))
    cmp_field('BB Upper', lambda: tech.get('BB Upper'))
    cmp_field('BB Lower', lambda: tech.get('BB Lower'))
    cmp_field('OBV', lambda: tech.get('OBV'))
    cmp_field('ADX14', lambda: tech.get('ADX14'))
    cmp_field('Aroon Up', lambda: tech.get('Aroon Up'))
    cmp_field('Aroon Down', lambda: tech.get('Aroon Down'))
    cmp_field('Stoch %K', lambda: tech.get('Stoch %K'))
    cmp_field('Stoch %D', lambda: tech.get('Stoch %D'))

    # fallback: any remaining numeric fields try to compare by name heuristics
    additional = [k for k in kv.keys() if k not in [c['field'] for c in comparisons]]
    for k in additional:
        # attempt to map common names
        lk = k.lower()
        if 'volatility' in lk or 'avg volume' in lk or 'volume' in lk:
            # compare avg volume if available
            if 'averageVolume' in info:
                cmp_field(k, lambda: info.get('averageVolume'))
                continue
        # If cannot map, add an entry marking no reference
        comparisons.append({'field': k, 'csv_raw': kv.get(k), 'csv_val': safe_float(kv.get(k)), 'ref_val': None, 'match': False})

    # write report
    with OUT_PATH.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['field', 'csv_raw', 'csv_val', 'ref_val', 'match'])
        writer.writeheader()
        for r in comparisons:
            # ensure ref_val serializable
            rv = r['ref_val']
            if isinstance(rv, float):
                if (math.isnan(rv)):
                    rv = None
            writer.writerow({'field': r['field'], 'csv_raw': r['csv_raw'], 'csv_val': r['csv_val'], 'ref_val': rv, 'match': r['match']})

    print('Wrote full validation report to', OUT_PATH)


if __name__ == '__main__':
    main()
