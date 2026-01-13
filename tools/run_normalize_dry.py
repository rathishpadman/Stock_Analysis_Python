"""
Dry-run normalizer runner.

Scans OCT25 for two-column key/value CSVs, runs normalization heuristics, and writes
per-file diffs into backups/diffs_<timestamp>/ plus a combined CSV. Does not modify
any original files.
"""
import os
import csv
import argparse
import datetime as dt
from equity_engine import normalizers
import glob
import pandas as pd


def read_kv_csv(path: str) -> dict:
    kv = {}
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        for row in reader:
            if not row:
                continue
            if len(row) >= 2:
                key = row[0].strip()
                val = row[1].strip()
                kv[key] = val
            elif len(row) == 1:
                kv[row[0].strip()] = ''
    return kv


def write_diffs_csv(out_path: str, diffs: list):
    df = pd.DataFrame(diffs)
    df.to_csv(out_path, index=False, encoding='utf-8')


def main(oct25_dir: str, out_base: str):
    os.makedirs(out_base, exist_ok=True)
    files = glob.glob(os.path.join(oct25_dir, '*.csv'))
    combined = []
    for f in files:
        kv = read_kv_csv(f)
        suggestions, explanations = normalizers.normalize_dividend(kv)
        diffs = []
        for ex in explanations:
            diffs.append({
                'file': os.path.basename(f),
                'key': ex.get('key', ''),
                'original': ex.get('original', ''),
                'suggested': ex.get('suggested', ''),
                'reason': ex.get('reason', ''),
                'confidence': ex.get('confidence', 0),
            })
        # write per-file diffs
        if diffs:
            out_file = os.path.join(out_base, os.path.basename(f).replace('.csv', '_diffs.csv'))
            write_diffs_csv(out_file, diffs)
            combined.extend(diffs)

    # write combined report
    if combined:
        combined_path = os.path.join(out_base, 'combined_diffs.csv')
        write_diffs_csv(combined_path, combined)
        print(f"Wrote diffs to: {out_base}")
    else:
        print("No suggested changes detected by normalizer.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dry-run normalization for OCT25 CSVs')
    parser.add_argument('--oct25', default='./OCT25', help='Path to OCT25 folder')
    parser.add_argument('--out', default=None, help='Optional output base dir for diffs')
    args = parser.parse_args()
    ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    out_base = args.out or os.path.join('backups', f'diffs_{ts}')
    main(args.oct25, out_base)
