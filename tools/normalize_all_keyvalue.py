"""Normalize dividend and compute technicals for all key/value CSV files in OCT25.

For each two-column csv containing a 'Ticker' key, produces:
 - OCT25/<name>_normalized.csv
 - OCT25/<name>_normalized_tech.csv

And writes a summary CSV tools/normalize_all_summary.csv
"""
from pathlib import Path
import csv
import sys
import traceback

ROOT = Path(__file__).parents[1]
OCT25 = ROOT / 'OCT25'
OUT_SUM = Path(__file__).parent / 'normalize_all_summary.csv'

from normalize_dividend_reliance import read_kv, write_kv
from normalize_dividend_reliance import CSV_IN as dummy_in
from normalize_dividend_reliance import CSV_OUT as dummy_out
from apply_technicals_reliance import read_kv as read_kv2, write_kv as write_kv2
from apply_technicals_reliance import CSV_OUT as tech_out

import yfinance as yf
from equity_engine.technical import compute_technicals


def process_file(path: Path):
    kv = read_kv(path)
    if 'Ticker' not in kv:
        return {'file': str(path), 'status': 'no_ticker'}
    name = path.stem
    try:
        # Use normalize_dividend_reliance logic but adapted: call read_kv and then similar logic
        # For simplicity import and call normalize_dividend_reliance.main via exec doesn't work here; replicate minimal steps
        ticker = kv.get('Ticker')
        yahoo_t = ticker + '.NS' if '.' not in ticker else ticker
        t = yf.Ticker(yahoo_t)
        info = t.info
        price = info.get('regularMarketPrice')
        div_rate = info.get('dividendRate')
        div_yield = info.get('dividendYield')

        # simple detection
        detected_dps = None
        detected_yield_dec = None
        if div_rate is not None and price:
            detected_dps = float(div_rate)
            if div_yield is not None:
                if div_yield > 1:
                    detected_yield_dec = div_yield / 100.0
                else:
                    detected_yield_dec = float(div_yield)
            else:
                detected_yield_dec = detected_dps / price

        # Update kv and write normalized
        kv_out = dict(kv)
        kv_out['DividendPerShare_Detected'] = str(detected_dps) if detected_dps is not None else ''
        kv_out['DividendYield_decimal_Normalized'] = str(detected_yield_dec) if detected_yield_dec is not None else ''
        kv_out['DividendYield_percent_Normalized'] = str(detected_yield_dec * 100.0) if detected_yield_dec is not None else ''

        out_norm = path.with_name(name + '_normalized.csv')
        write_kv(out_norm, kv_out)

        # compute technicals
        hist = t.history(period='2y', interval='1d')
        if not hist.empty:
            tech = compute_technicals(hist)
            kv_tech = dict(kv_out)
            for k, v in tech.items():
                kv_tech[k] = str(v)
            out_tech = path.with_name(name + '_normalized_tech.csv')
            write_kv(out_tech, kv_tech)

        return {'file': str(path), 'status': 'ok'}
    except Exception as e:
        return {'file': str(path), 'status': 'error', 'error': str(e), 'trace': traceback.format_exc()}


def main():
    rows = []
    for p in OCT25.glob('*.csv'):
        res = process_file(p)
        rows.append(res)

    # write summary
    keys = set()
    for r in rows:
        keys.update(r.keys())
    keys = list(keys)
    with OUT_SUM.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print('Summary written to', OUT_SUM)


if __name__ == '__main__':
    main()
