"""Generate a concise verification report comparing original vs normalized vs truth for RELIANCE.

Truth set is inlined here — update if needed.
"""
import pathlib
import pandas as pd
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

def find_latest_in_dir(d: pathlib.Path, pattern='Stock_Analysis_*.xlsx'):
    files = sorted(list(d.glob(pattern)), key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0] if files else None

def load_sheet(path, sheet='NIFTY50'):
    xl = pd.ExcelFile(path)
    if sheet in xl.sheet_names:
        return xl.parse(sheet)
    return xl.parse(xl.sheet_names[0])

def get_reliance_row(df):
    r = df[df['Ticker'].astype(str).str.upper() == 'RELIANCE']
    return r.iloc[0].to_dict() if not r.empty else None


def run():
    oct_dir = ROOT / 'OCT25'
    backups_dir = ROOT / 'backups'
    orig = find_latest_in_dir(oct_dir)
    normalized_dir = sorted([p for p in backups_dir.glob('normalized_*')], key=lambda x: x.stat().st_mtime, reverse=True)
    if not normalized_dir:
        print('No normalized backups found')
        return 2
    norm_folder = normalized_dir[0]
    norm_file = find_latest_in_dir(norm_folder)
    if not orig or not norm_file:
        print('Missing original or normalized file')
        return 2

    print('Original:', orig)
    print('Normalized:', norm_file)

    df_orig = load_sheet(orig)
    df_norm = load_sheet(norm_file)

    row_o = get_reliance_row(df_orig)
    row_n = get_reliance_row(df_norm)
    if row_o is None or row_n is None:
        print('RELIANCE row missing in one of the files')
        return 2

    # Truth set (user provided) — update these if different
    truth = {
        'Dividend Yield %': 2.525253,
        'CAGR 3Y %': 9.100579,
        'CAGR 5Y %': 8.748092,
        'Beta 1Y': 1.170806,
        'Beta 3Y': 1.200755,
    }

    keys = ['Dividend Yield %', 'Dividend Rate', 'CAGR 3Y %', 'CAGR 5Y %', 'Beta 1Y', 'Beta 3Y', 'A/D Line', 'Alpha 1Y %']

    print('\nVerification report for RELIANCE')
    print('Key | Original | Normalized | Truth | Delta(norm-truth)')
    print('----|----------|------------|-------|-----------------')
    for k in keys:
        o = row_o.get(k, None)
        n = row_n.get(k, None)
        t = truth.get(k, '')
        try:
            delta = None
            if t != '':
                if isinstance(n, (int, float)) and isinstance(t, (int, float)):
                    delta = n - t
                else:
                    try:
                        delta = float(n) - float(t)
                    except Exception:
                        delta = None
        except Exception:
            delta = None
        print(f"{k} | {o} | {n} | {t} | {delta}")

    return 0


if __name__ == '__main__':
    raise SystemExit(run())
