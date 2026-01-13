"""Targeted dry-run verifier for RELIANCE.

Loads the latest pipeline output workbook (same logic as normalize_output_apply),
extracts the row for RELIANCE from sheet 'NIFTY50' and runs the normalizers to
produce suggested corrections without writing any files.
"""
import sys
import pathlib
from datetime import datetime
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
import os
sys.path.insert(0, str(ROOT))

from equity_engine import normalizers


def find_latest_output(oct_dir=ROOT / 'OCT25'):
    # find latest Excel workbook in OCT25 matching Stock_Analysis_*.xlsx
    p = pathlib.Path(oct_dir)
    if not p.exists():
        return None
    files = sorted([f for f in p.glob('Stock_Analysis_*.xlsx')], key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0] if files else None


def load_nifty50(workbook_path):
    xl = pd.ExcelFile(workbook_path)
    if 'NIFTY50' not in xl.sheet_names:
        # fallback to first sheet
        return xl.parse(xl.sheet_names[0])
    return xl.parse('NIFTY50')


def run():
    workbook = find_latest_output()
    if workbook is None:
        print('No pipeline output found in OCT25')
        return 2
    print('Inspecting:', workbook)
    df = load_nifty50(workbook)
    # find RELIANCE row by Ticker
    rel = df[df['Ticker'].astype(str).str.upper() == 'RELIANCE']
    if rel.empty:
        print('RELIANCE row not found in NIFTY50 sheet')
        return 2
    row = rel.iloc[0].to_dict()

    print('\nRunning dividend normalizer...')
    sugg, expl = normalizers.normalize_dividend(row, ticker='RELIANCE', live_price=row.get('Price (Last)'))
    print('Suggestions:')
    for k, v in sugg.items():
        print(f'  {k}: {v}')
    print('\nExplanations:')
    for e in expl:
        print(' -', e)

    print('\nComputing technicals and metrics...')
    tech_vals, tech_info = normalizers.compute_technicals_for_ticker('RELIANCE', years=2)
    print('\nTechnicals (2y):')
    for k, v in tech_vals.items():
        print(f'  {k}: {v}')

    c3, c3info = normalizers.compute_cagr_for_ticker('RELIANCE', years=3)
    c5, c5info = normalizers.compute_cagr_for_ticker('RELIANCE', years=5)
    b1, b1info = normalizers.compute_beta('RELIANCE', years=1)
    b3, b3info = normalizers.compute_beta('RELIANCE', years=3)
    adl, adlinfo = normalizers.compute_adl('RELIANCE', years=2)
    alpha1, alphainfo = normalizers.compute_alpha('RELIANCE', years=1)

    print('\nComputed multi-year metrics:')
    print(f'  CAGR 3Y %: {c3 * 100.0 if c3==c3 else None}')
    print(f'  CAGR 5Y %: {c5 * 100.0 if c5==c5 else None}')
    print(f'  Beta 1Y: {b1}')
    print(f'  Beta 3Y: {b3}')
    print(f'  A/D Line: {adl}')
    print(f'  Alpha 1Y %: {alpha1 * 100.0 if alpha1==alpha1 else None}')

    return 0


if __name__ == '__main__':
    raise SystemExit(run())
