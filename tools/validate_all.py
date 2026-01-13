"""Validate all key-value CSV files under OCT25 against Yahoo Finance.

Produces tools/validation_report.csv with one row per validated file/stock.
"""
from pathlib import Path
import csv
import sys
import time
from typing import Dict, Optional

import pandas as pd
import yfinance as yf


ROOT = Path(__file__).parents[1]
OCT25 = ROOT / 'OCT25'
OUT = Path(__file__).parent / 'validation_report.csv'


def load_csv_kv(path: Path) -> Dict[str, str]:
    df = pd.read_csv(path, header=0, dtype=str)
    if df.shape[1] == 2:
        return dict(zip(df.iloc[:, 0].str.strip(), df.iloc[:, 1].str.strip()))
    return df.set_index(df.columns[0])[df.columns[1]].to_dict()


def safe_float(x: Optional[str]) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


def validate_one(path: Path) -> Dict[str, object]:
    # Try to detect the CSV layout. If the file is a table with a 'Ticker' column,
    # validate every row. Otherwise, fall back to key/value single-stock file.
    df = pd.read_csv(path, header=0, dtype=str)
    results = []

    if 'Ticker' in df.columns or 'Symbol' in df.columns:
        # table-style with many rows
        ticker_col = 'Ticker' if 'Ticker' in df.columns else 'Symbol'
        for idx, row in df.iterrows():
            kv = {col: (row[col] if col in row and pd.notna(row[col]) else '') for col in df.columns}
            kv['Ticker'] = str(kv.get(ticker_col, '')).strip()
            if not kv['Ticker']:
                results.append({'file': str(path), 'row': idx, 'error': 'empty ticker'})
                continue

            # Normalize yahoo ticker
            ticker = kv['Ticker']
            if '.' not in ticker and len(ticker) <= 6:
                yahoo_t = ticker + '.NS'
            else:
                yahoo_t = ticker

            try:
                info = yf.Ticker(yahoo_t).info
            except Exception as e:
                results.append({'file': str(path), 'row': idx, 'ticker': yahoo_t, 'error': f'yfinance error: {e}'})
                continue

            # CSV values for this row
            price_csv = safe_float(kv.get('Price (Last)'))
            marketcap_csv_cr = safe_float(kv.get('Market Cap (INR Cr)'))
            shares_csv = safe_float(kv.get('Shares Outstanding'))
            pe_csv = safe_float(kv.get('P/E (TTM)'))
            eps_csv = safe_float(kv.get('EPS TTM'))
            div_csv_raw = kv.get('Dividend Yield %')

            # Yahoo values
            price_y = info.get('regularMarketPrice')
            marketcap_y = info.get('marketCap')
            marketcap_y_cr = marketcap_y / 1e7 if marketcap_y else None
            shares_y = info.get('sharesOutstanding')
            pe_y = info.get('trailingPE') or info.get('forwardPE')
            eps_y = info.get('trailingEps')
            div_rate = info.get('dividendRate')
            div_yield = info.get('dividendYield')
            beta_y = info.get('beta')

            flags = []
            try:
                div_csv_val = float(div_csv_raw) if div_csv_raw not in (None, '') else None
            except Exception:
                div_csv_val = None

            if div_csv_val is not None:
                if div_csv_val > 10:
                    flags.append('large_dividend_field')
                elif 1 < div_csv_val <= 10:
                    flags.append('ambiguous_dividend_1_10')

            if marketcap_csv_cr and price_y and shares_csv:
                implied = (price_y * shares_csv) / 1e7
                if abs(implied - marketcap_csv_cr) / max(implied, marketcap_csv_cr) > 0.01:
                    flags.append('marketcap_mismatch')

            if price_y and eps_csv and pe_csv:
                implied_pe = price_y / eps_csv
                if abs(implied_pe - pe_csv) / max(implied_pe, pe_csv) > 0.01:
                    flags.append('pe_mismatch')

            results.append({
                'file': str(path),
                'row': idx,
                'ticker': yahoo_t,
                'price_csv': price_csv,
                'price_yahoo': price_y,
                'marketcap_csv_cr': marketcap_csv_cr,
                'marketcap_yahoo_cr': marketcap_y_cr,
                'shares_csv': shares_csv,
                'shares_yahoo': shares_y,
                'pe_csv': pe_csv,
                'pe_yahoo': pe_y,
                'eps_csv': eps_csv,
                'eps_yahoo': eps_y,
                'dividend_csv_raw': div_csv_raw,
                'dividendRate_yahoo': div_rate,
                'dividendYield_yahoo': div_yield,
                'beta_yahoo': beta_y,
                'flags': ';'.join(flags) if flags else ''
            })
        return results
    else:
        # fallback single key/value file
        kv = load_csv_kv(path)
        ticker = kv.get('Ticker') or kv.get('Symbol')
        if not ticker:
            return [{ 'file': str(path), 'error': 'no ticker found' }]

        if '.' not in ticker and len(ticker) <= 6:
            yahoo_t = ticker + '.NS'
        else:
            yahoo_t = ticker

        try:
            info = yf.Ticker(yahoo_t).info
        except Exception as e:
            return [{ 'file': str(path), 'ticker': yahoo_t, 'error': f'yfinance error: {e}' }]

        price_csv = safe_float(kv.get('Price (Last)'))
        marketcap_csv_cr = safe_float(kv.get('Market Cap (INR Cr)'))
        shares_csv = safe_float(kv.get('Shares Outstanding'))
        pe_csv = safe_float(kv.get('P/E (TTM)'))
        eps_csv = safe_float(kv.get('EPS TTM'))
        div_csv_raw = kv.get('Dividend Yield %')

        price_y = info.get('regularMarketPrice')
        marketcap_y = info.get('marketCap')
        marketcap_y_cr = marketcap_y / 1e7 if marketcap_y else None
        shares_y = info.get('sharesOutstanding')
        pe_y = info.get('trailingPE') or info.get('forwardPE')
        eps_y = info.get('trailingEps')
        div_rate = info.get('dividendRate')
        div_yield = info.get('dividendYield')
        beta_y = info.get('beta')

        flags = []
        try:
            div_csv_val = float(div_csv_raw) if div_csv_raw not in (None, '') else None
        except Exception:
            div_csv_val = None

        if div_csv_val is not None:
            if div_csv_val > 10:
                flags.append('large_dividend_field')
            elif 1 < div_csv_val <= 10:
                flags.append('ambiguous_dividend_1_10')

        if marketcap_csv_cr and price_y and shares_csv:
            implied = (price_y * shares_csv) / 1e7
            if abs(implied - marketcap_csv_cr) / max(implied, marketcap_csv_cr) > 0.01:
                flags.append('marketcap_mismatch')

        if price_y and eps_csv and pe_csv:
            implied_pe = price_y / eps_csv
            if abs(implied_pe - pe_csv) / max(implied_pe, pe_csv) > 0.01:
                flags.append('pe_mismatch')

        return [{
            'file': str(path),
            'row': 0,
            'ticker': yahoo_t,
            'price_csv': price_csv,
            'price_yahoo': price_y,
            'marketcap_csv_cr': marketcap_csv_cr,
            'marketcap_yahoo_cr': marketcap_y_cr,
            'shares_csv': shares_csv,
            'shares_yahoo': shares_y,
            'pe_csv': pe_csv,
            'pe_yahoo': pe_y,
            'eps_csv': eps_csv,
            'eps_yahoo': eps_y,
            'dividend_csv_raw': div_csv_raw,
            'dividendRate_yahoo': div_rate,
            'dividendYield_yahoo': div_yield,
            'beta_yahoo': beta_y,
            'flags': ';'.join(flags) if flags else ''
        }]


def main():
    rows = []
    found = list(OCT25.glob('*.csv'))
    if not found:
        print('No CSV files found in', OCT25)
        sys.exit(1)

    for p in found:
        print('Validating', p.name)
        try:
            r = validate_one(p)
            rows.append(r)
        except Exception as e:
            rows.append({'file': str(p), 'error': str(e)})
        time.sleep(0.5)  # avoid rapid-fire requests

    # Write report
    keys = set()
    for r in rows:
        keys.update(r.keys())
    keys = list(keys)
    with OUT.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print('\nWrote report to', OUT)


if __name__ == '__main__':
    main()
