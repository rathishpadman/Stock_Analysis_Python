"""Fill derived fields for Reliance: Beta 1Y/3Y, CAGR 3Y/5Y, Alpha 1Y, A/D Line, and write filled CSV."""
from pathlib import Path
import math
import sys

import numpy as np
import pandas as pd
import yfinance as yf


ROOT = Path(__file__).parents[1]
OCT25 = ROOT / 'OCT25'
MERGED = OCT25 / 'reliance_analysis_merged.csv'
FILLED = OCT25 / 'reliance_analysis_merged_filled.csv'


def read_kv(path: Path):
    kv = {}
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            parts = line.split(',', 1)
            if len(parts) == 2:
                k = parts[0].strip()
                v = parts[1].strip()
                kv[k] = v
    return kv


def write_kv(path: Path, kv: dict):
    with path.open('w', encoding='utf-8', newline='') as f:
        for k, v in kv.items():
            f.write(f'{k},{v}\n')


def compute_beta(ticker, index_ticker, period_years):
    end = pd.Timestamp.today()
    start = end - pd.DateOffset(years=period_years)
    p = yf.download(ticker, start=start, end=end, progress=False)
    i = yf.download(index_ticker, start=start, end=end, progress=False)
    prices = p['Adj Close'] if 'Adj Close' in p.columns else p['Close']
    idx = i['Adj Close'] if 'Adj Close' in i.columns else i['Close']
    if prices.empty or idx.empty:
        return None
    # align
    df = pd.concat([prices, idx], axis=1).dropna()
    df.columns = ['stock', 'index']
    # daily returns
    rets = df.pct_change().dropna()
    cov = rets['stock'].cov(rets['index'])
    var = rets['index'].var()
    beta = cov / var if var != 0 else None
    return beta


def compute_cagr(ticker, years):
    end = pd.Timestamp.today()
    start = end - pd.DateOffset(years=years)
    p = yf.download(ticker, start=start, end=end, progress=False)
    prices = p['Adj Close'] if 'Adj Close' in p.columns else p['Close']
    # ensure prices is a Series
    if isinstance(prices, pd.DataFrame):
        prices = prices.iloc[:, 0]
    if prices is None or len(prices) == 0:
        return None
    start_price = prices.iloc[0]
    end_price = prices.iloc[-1]
    if start_price <= 0:
        return None
    cagr = (end_price / start_price) ** (1.0 / years) - 1
    return cagr


def compute_alpha(ticker, index_ticker, years):
    # compute alpha as annualized intercept from regression of excess returns (simplified)
    end = pd.Timestamp.today()
    start = end - pd.DateOffset(years=years)
    p = yf.download(ticker, start=start, end=end, progress=False)
    i = yf.download(index_ticker, start=start, end=end, progress=False)
    prices = p['Adj Close'] if 'Adj Close' in p.columns else p['Close']
    idx = i['Adj Close'] if 'Adj Close' in i.columns else i['Close']
    if prices.empty or idx.empty:
        return None
    df = pd.concat([prices, idx], axis=1).dropna()
    df.columns = ['stock', 'index']
    rets = df.pct_change().dropna()
    X = rets['index'].values.reshape(-1, 1)
    y = rets['stock'].values
    # add constant
    X1 = np.hstack([np.ones((X.shape[0], 1)), X])
    beta_hat = np.linalg.lstsq(X1, y, rcond=None)[0]
    alpha_daily = beta_hat[0]
    # annualize alpha (approx)
    alpha_ann = (1 + alpha_daily) ** 252 - 1
    return alpha_ann


def compute_ad_line(ticker):
    # Accumulation/Distribution Line = cumulative Money Flow Volume
    hist = yf.download(ticker, period='2y', interval='1d', progress=False)
    if hist.empty:
        return None
    high = hist['High']
    low = hist['Low']
    close = hist['Close']
    vol = hist['Volume']
    mfm = ((close - low) - (high - close)) / (high - low)
    mfm = mfm.fillna(0)
    mfv = mfm * vol
    ad = mfv.cumsum()
    return ad.iloc[-1]


def main():
    if not MERGED.exists():
        print('Merged CSV not found:', MERGED)
        sys.exit(1)

    kv = read_kv(MERGED)
    ticker = kv.get('Ticker')
    if not ticker:
        print('Ticker missing in merged CSV')
        sys.exit(1)
    yahoo_t = ticker + '.NS' if '.' not in ticker else ticker
    index_t = '^NSEI'  # Yahoo symbol for NIFTY 50

    print('Computing Beta 1Y...')
    beta1 = compute_beta(yahoo_t, index_t, 1)
    print('Computing Beta 3Y...')
    beta3 = compute_beta(yahoo_t, index_t, 3)
    print('Computing CAGR 3Y...')
    cagr3 = compute_cagr(yahoo_t, 3)
    print('Computing CAGR 5Y...')
    cagr5 = compute_cagr(yahoo_t, 5)
    print('Computing Alpha 1Y...')
    alpha1 = compute_alpha(yahoo_t, index_t, 1)
    print('Computing A/D Line...')
    ad_line = compute_ad_line(yahoo_t)

    if beta1 is not None:
        kv['Beta 1Y'] = str(round(beta1, 6))
    if beta3 is not None:
        kv['Beta 3Y'] = str(round(beta3, 6))
    if cagr3 is not None:
        kv['CAGR 3Y %'] = str(round(cagr3 * 100, 6))
    if cagr5 is not None:
        kv['CAGR 5Y %'] = str(round(cagr5 * 100, 6))
    if alpha1 is not None:
        kv['Alpha 1Y %'] = str(round(alpha1 * 100, 6))
    if ad_line is not None:
        kv['A/D Line'] = str(int(ad_line))

    write_kv(FILLED, kv)
    print('Wrote filled merged CSV to', FILLED)


if __name__ == '__main__':
    main()
