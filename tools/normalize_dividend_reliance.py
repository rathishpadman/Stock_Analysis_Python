"""Normalize dividend fields for RELIANCE and write a normalized CSV.

Outputs: OCT25/reliance_analysis_normalized.csv and a backup of original.
"""
from pathlib import Path
import csv
import sys
import shutil

import yfinance as yf


ROOT = Path(__file__).parents[1]
CSV_IN = ROOT / 'OCT25' / 'reliance_analysis.csv'
CSV_OUT = ROOT / 'OCT25' / 'reliance_analysis_normalized.csv'
BACKUP = ROOT / 'OCT25' / 'reliance_analysis.csv.bak'


def read_kv(path: Path):
    import pandas as pd
    df = pd.read_csv(path, header=None, dtype=str)
    if df.shape[1] >= 2:
        keys = df.iloc[:, 0].astype(str).str.strip()
        vals = df.iloc[:, 1].astype(str).str.strip()
        return dict(zip(keys, vals))
    return {}


def write_kv(path: Path, kv: dict):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for k, v in kv.items():
            writer.writerow([k, v])


def main():
    if not CSV_IN.exists():
        print('Input CSV not found:', CSV_IN)
        sys.exit(1)

    kv = read_kv(CSV_IN)
    ticker = kv.get('Ticker')
    if not ticker:
        print('Ticker missing in CSV')
        sys.exit(1)

    yahoo_t = ticker + '.NS' if '.' not in ticker else ticker
    t = yf.Ticker(yahoo_t)
    info = t.info

    # vendor DPS and dividendYield
    div_rate = info.get('dividendRate')  # in currency per share
    div_yield_dec = info.get('dividendYield')  # decimal e.g., 0.0037 or 0.37 depending on provider
    price = info.get('regularMarketPrice')

    # CSV raw value
    csv_div_raw = kv.get('Dividend Yield %')

    # Decision logic
    detected_dps = None
    detected_yield_dec = None
    flag = ''
    source = ''

    # If provider div_rate present and sane, prefer it
    if div_rate is not None and price and price > 0:
        detected_dps = float(div_rate)
        # Some providers give dividendYield as decimal (e.g., 0.0037) or percent-like 0.37
        if div_yield_dec is not None:
            # If div_yield_dec > 1 treat as percent (e.g., 37 meaning 37%) else decimal
            if div_yield_dec > 1:
                detected_yield_dec = float(div_yield_dec) / 100.0
            else:
                detected_yield_dec = float(div_yield_dec)
        else:
            detected_yield_dec = detected_dps / price
        source = 'yahoo_div_rate'

    # Inspect CSV raw: if numeric and >10, likely mis-scaled or DPS
    try:
        csv_div_num = float(csv_div_raw) if csv_div_raw is not None and csv_div_raw != '' else None
    except Exception:
        csv_div_num = None

    if csv_div_num is not None:
        if csv_div_num > 10:
            # could be DPS or percent without decimal; compare with detected DPS
            if detected_dps and abs(csv_div_num - detected_dps) < max(1, detected_dps * 0.1):
                detected_dps = csv_div_num
                detected_yield_dec = detected_dps / price if price else None
                flag = 'csv_used_as_dps'
                source = 'csv'
            else:
                # assume it's DPS if in typical DPS range
                if 0 < csv_div_num < 500:
                    detected_dps = csv_div_num
                    detected_yield_dec = detected_dps / price if price else None
                    flag = 'csv_assumed_dps'
                    source = 'csv'
                else:
                    flag = 'csv_unusual_high'
        elif 1 < csv_div_num <= 10:
            # ambiguous: could be DPS or percent (1..10%). prefer DPS if close to div_rate
            if detected_dps and abs(csv_div_num - detected_dps) < max(1, detected_dps * 0.1):
                detected_dps = csv_div_num
                detected_yield_dec = detected_dps / price if price else None
                flag = 'csv_matched_dps'
                source = 'csv'
            else:
                # treat as percent
                detected_yield_dec = csv_div_num / 100.0
                detected_dps = detected_yield_dec * price if price else None
                flag = 'csv_assumed_percent'
                source = 'csv'
        elif 0 <= csv_div_num <= 1:
            # likely a decimal e.g., 0.0037 or 0.37
            if csv_div_num <= 0.02:
                # treat as decimal (e.g., 0.0037)
                detected_yield_dec = csv_div_num
                detected_dps = detected_yield_dec * price if price else None
                flag = 'csv_decimal'
                source = 'csv'
            else:
                # treat as percent (e.g., 0.37 meaning 0.37%)
                detected_yield_dec = csv_div_num / 100.0
                detected_dps = detected_yield_dec * price if price else None
                flag = 'csv_small_percent'
                source = 'csv'

    # Final normalized values
    dividend_per_share = detected_dps
    dividend_yield_decimal = detected_yield_dec
    dividend_yield_percent = (detected_yield_dec * 100.0) if detected_yield_dec is not None else None

    # Append normalized keys to kv
    kv_out = dict(kv)  # copy
    kv_out['DividendPerShare_Detected'] = str(dividend_per_share) if dividend_per_share is not None else ''
    kv_out['DividendYield_decimal_Normalized'] = str(dividend_yield_decimal) if dividend_yield_decimal is not None else ''
    kv_out['DividendYield_percent_Normalized'] = str(dividend_yield_percent) if dividend_yield_percent is not None else ''
    kv_out['DividendFlag'] = flag
    kv_out['DividendSource'] = source
    kv_out['Dividend_PriceUsed'] = str(price) if price is not None else ''

    # backup original
    if not BACKUP.exists():
        shutil.copy2(CSV_IN, BACKUP)

    write_kv(CSV_OUT, kv_out)
    print('Wrote normalized CSV to', CSV_OUT)


if __name__ == '__main__':
    main()
