"""Simple validation script for RELIANCE data against Yahoo Finance.

Usage: run with the project's Python (venv) to compare the CSV row with yfinance values.
"""
import csv
import sys
from pathlib import Path

import pandas as pd
import yfinance as yf


def load_csv_kv(path: Path):
    df = pd.read_csv(path, header=0, dtype=str)
    if df.shape[1] == 2:
        return dict(zip(df.iloc[:, 0].str.strip(), df.iloc[:, 1].str.strip()))
    return df.set_index(df.columns[0])[df.columns[1]].to_dict()


def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


def main():
    csv_path = Path(__file__).parents[1] / "OCT25" / "reliance_analysis.csv"
    if not csv_path.exists():
        print('CSV not found at', csv_path)
        sys.exit(1)

    kv = load_csv_kv(csv_path)

    # CSV values
    price_csv = safe_float(kv.get('Price (Last)'))
    marketcap_csv_cr = safe_float(kv.get('Market Cap (INR Cr)'))
    shares_csv = safe_float(kv.get('Shares Outstanding'))
    pe_csv = safe_float(kv.get('P/E (TTM)'))
    eps_csv = safe_float(kv.get('EPS TTM'))
    div_csv_raw = kv.get('Dividend Yield %')

    # Fetch Yahoo
    t = yf.Ticker('RELIANCE.NS')
    info = t.info

    price_y = info.get('regularMarketPrice')
    marketcap_y = info.get('marketCap')
    marketcap_y_cr = marketcap_y / 1e7 if marketcap_y else None
    shares_y = info.get('sharesOutstanding')
    pe_y = info.get('trailingPE') or info.get('forwardPE')
    eps_y = info.get('trailingEps')
    div_rate = info.get('dividendRate')
    div_yield = info.get('dividendYield')
    beta_y = info.get('beta')

    print('\n--- RELIANCE validation report ---')
    print('CSV timestamp:', kv.get('As Of Datetime'))

    print('\nPrice: CSV=%s | Yahoo=%s' % (price_csv, price_y))
    if price_y and shares_csv:
        implied_mc_cr = (price_y * shares_csv) / 1e7
        print('Implied MarketCap from Yahoo price & CSV shares (Cr):', round(implied_mc_cr, 6))

    print('MarketCap (Cr): CSV=%s | Yahoo=%s' % (marketcap_csv_cr, marketcap_y_cr))
    if marketcap_csv_cr and marketcap_y_cr:
        print('MarketCap delta (Cr):', round(marketcap_csv_cr - marketcap_y_cr, 6))

    print('Shares Outstanding: CSV=%s | Yahoo=%s' % (shares_csv, shares_y))
    print('P/E: CSV=%s | Yahoo=%s' % (pe_csv, pe_y))
    print('EPS: CSV=%s | Yahoo=%s' % (eps_csv, eps_y))

    print('\nDividend-related:')
    print('CSV Dividend Yield raw:', div_csv_raw)
    print('Yahoo dividendRate (₹):', div_rate)
    print('Yahoo dividendYield (decimal):', div_yield)
    if div_rate and price_y:
        print('Computed yield from dividendRate:', div_rate / price_y, '(decimal)')

    print('\nBeta: CSV=missing? | Yahoo=%s' % beta_y)

    # Flags
    flags = []
    # dividend yield plausibility
    try:
        div_csv_val = float(div_csv_raw) if div_csv_raw is not None and div_csv_raw != '' else None
    except Exception:
        div_csv_val = None

    # If CSV shows large dividend values (e.g., > 10), flag
    if div_csv_val is not None:
        if div_csv_val > 10:
            flags.append('CSV Dividend field unusually large: %s — check whether this is DPS, decimal, or percent.' % div_csv_val)
        elif div_csv_val > 1 and div_csv_val < 10:
            # could be DPS or percent; ask to verify
            flags.append('CSV Dividend value in 1..10: ambiguous (could be DPS rather than yield percent).')

    # Market cap consistency
    if marketcap_csv_cr and price_y and shares_csv:
        implied = (price_y * shares_csv) / 1e7
        if abs(implied - marketcap_csv_cr) / max(implied, marketcap_csv_cr) > 0.01:  # >1% diff
            flags.append('Market cap differs by more than 1% from implied by price*shares.')

    # P/E check
    if price_y and eps_csv:
        implied_pe = price_y / eps_csv
        if pe_csv and abs(implied_pe - pe_csv) / max(implied_pe, pe_csv) > 0.01:
            flags.append('P/E in CSV differs from implied P/E using CSV EPS and Yahoo price.')

    print('\nFlags:')
    if flags:
        for f in flags:
            print('-', f)
    else:
        print('No flags — basic arithmetic checks passed (except any label/unit issues).')


if __name__ == '__main__':
    main()
