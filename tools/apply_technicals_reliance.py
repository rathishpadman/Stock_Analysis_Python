from pathlib import Path
import csv
import sys

# ensure project root is on sys.path so equity_engine can be imported
ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

import yfinance as yf
import pandas as pd

from equity_engine.technical import compute_technicals


CSV_IN = ROOT / 'OCT25' / 'reliance_analysis_normalized.csv'
CSV_OUT = ROOT / 'OCT25' / 'reliance_analysis_normalized_tech.csv'


def read_kv(path: Path):
    kv = {}
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split(',', 1)
            if len(parts) == 2:
                k = parts[0].strip()
                v = parts[1].strip().strip('"')
                kv[k] = v
    return kv


def write_kv(path: Path, kv: dict):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for k, v in kv.items():
            writer.writerow([k, v])


def main():
    if not CSV_IN.exists():
        print('Normalized CSV not found:', CSV_IN)
        sys.exit(1)

    kv = read_kv(CSV_IN)
    ticker = kv.get('Ticker')
    if not ticker:
        print('Ticker missing')
        sys.exit(1)

    yahoo_t = ticker + '.NS' if '.' not in ticker else ticker
    t = yf.Ticker(yahoo_t)
    hist = t.history(period='2y', interval='1d')
    if hist.empty:
        print('No history')
        sys.exit(1)

    tech = compute_technicals(hist)

    # Append technicals to kv and write out
    kv_out = dict(kv)
    for k, v in tech.items():
        kv_out[k] = str(v)

    write_kv(CSV_OUT, kv_out)
    print('Wrote tech-appended CSV to', CSV_OUT)


if __name__ == '__main__':
    main()
