"""
Scan the latest pipeline workbook in OCT25 and verify key computed metrics
against yfinance/history-derived values for every ticker. Produces a CSV
diagnostic report in backups/diagnostics_<ts>/diagnostic_report.csv.

Usage:
    python -m tools.verify_all_tickers_yf --oct25 .\OCT25
"""
import os
import glob
import argparse
import datetime as dt
import pandas as pd
from equity_engine import normalizers


def find_latest_output(oct25_dir: str):
    pattern = os.path.join(oct25_dir, 'Stock_Analysis_*.xlsx')
    files = glob.glob(pattern)
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def safe_get(df_row, col):
    if col in df_row.index:
        v = df_row.get(col)
        try:
            if pd.isna(v):
                return None
        except Exception:
            pass
        return v
    return None


def run(oct25_dir: str):
    latest = find_latest_output(oct25_dir)
    if not latest:
        print('No pipeline output XLSX found in', oct25_dir)
        return

    xls = pd.read_excel(latest, sheet_name=None)
    # prefer sheet named NIFTY50, else first sheet
    sheet_name = 'NIFTY50' if 'NIFTY50' in xls else list(xls.keys())[0]
    df = xls[sheet_name].copy()

    rows = []
    for idx, row in df.iterrows():
        ticker = safe_get(row, 'Ticker') or safe_get(row, 'symbol') or safe_get(row, 'SYMBOL')
        if not ticker or str(ticker).strip() == '':
            continue

        t = str(ticker).strip()
        rec = {'row_index': idx, 'Ticker': t}

        # history lengths
        try:
            hist1 = normalizers.fetch_history_yf if hasattr(normalizers, 'fetch_history_yf') else None
        except Exception:
            hist1 = None

        # compute canonical metrics
        try:
            beta1, b1info = normalizers.compute_beta(t, index_symbol='^NSEI', years=1)
        except Exception:
            beta1, b1info = (float('nan'), {})
        try:
            beta3, b3info = normalizers.compute_beta(t, index_symbol='^NSEI', years=3)
        except Exception:
            beta3, b3info = (float('nan'), {})
        try:
            cagr3, c3info = normalizers.compute_cagr_for_ticker(t, years=3)
        except Exception:
            cagr3, c3info = (float('nan'), {})
        try:
            cagr5, c5info = normalizers.compute_cagr_for_ticker(t, years=5)
        except Exception:
            cagr5, c5info = (float('nan'), {})
        try:
            alpha1, ainfo = normalizers.compute_alpha(t, index_symbol='^NSEI', years=1)
        except Exception:
            alpha1, ainfo = (float('nan'), {})
        try:
            adl, adlinfo = normalizers.compute_adl(t, years=2)
        except Exception:
            adl, adlinfo = (float('nan'), {})

        # find sheet values
        sheet_beta1 = safe_get(row, 'Beta 1Y')
        sheet_beta3 = safe_get(row, 'Beta 3Y')
        sheet_cagr3 = safe_get(row, 'CAGR 3Y %')
        sheet_cagr5 = safe_get(row, 'CAGR 5Y %')
        sheet_alpha1 = safe_get(row, 'Alpha 1Y %')
        sheet_adl = safe_get(row, 'A/D Line')
        sheet_div_yield = safe_get(row, 'Dividend Yield %')
        sheet_div_rate = safe_get(row, 'Dividend Rate')
        sheet_ebitda = safe_get(row, 'EBITDA TTM (INR Cr)') or safe_get(row, 'EBITDA')

        rec.update({
            'sheet_Beta1': sheet_beta1,
            'computed_Beta1': (beta1 if beta1 == beta1 else None),
            'beta1_method': b1info.get('method') if isinstance(b1info, dict) else None,
            'sheet_Beta3': sheet_beta3,
            'computed_Beta3': (beta3 if beta3 == beta3 else None),
            'beta3_method': b3info.get('method') if isinstance(b3info, dict) else None,
            'sheet_CAGR3': sheet_cagr3,
            'computed_CAGR3_pct': (float(cagr3 * 100.0) if cagr3 == cagr3 else None),
            'sheet_CAGR5': sheet_cagr5,
            'computed_CAGR5_pct': (float(cagr5 * 100.0) if cagr5 == cagr5 else None),
            'sheet_Alpha1': sheet_alpha1,
            'computed_Alpha1_pct': (float(alpha1 * 100.0) if alpha1 == alpha1 else None),
            'sheet_ADL': sheet_adl,
            'computed_ADL': (float(adl) if adl == adl else None),
            'sheet_Dividend_Yield': sheet_div_yield,
            'sheet_Dividend_Rate': sheet_div_rate,
            'sheet_EBITDA_present': (not pd.isna(sheet_ebitda))
        })

        # quick discrepancy flags
        def diff_flag(a, b, rel_tol=0.2, abs_tol=0.5):
            try:
                if a is None or b is None:
                    return False
                a = float(a)
                b = float(b)
                if abs(a - b) <= abs_tol:
                    return False
                # relative
                if abs(b) > 1e-6 and abs((a - b) / b) <= rel_tol:
                    return False
                return True
            except Exception:
                return False

        rec['beta1_discrep'] = diff_flag(rec['sheet_Beta1'], rec['computed_Beta1'], rel_tol=0.25, abs_tol=0.5)
        rec['beta3_discrep'] = diff_flag(rec['sheet_Beta3'], rec['computed_Beta3'], rel_tol=0.25, abs_tol=0.5)
        rec['cagr3_discrep'] = diff_flag(rec['sheet_CAGR3'], rec['computed_CAGR3_pct'], rel_tol=0.3, abs_tol=2.0)
        rec['cagr5_discrep'] = diff_flag(rec['sheet_CAGR5'], rec['computed_CAGR5_pct'], rel_tol=0.3, abs_tol=2.0)

        rows.append(rec)

    out_dir = os.path.join('backups', f'diagnostics_{dt.datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(out_dir, exist_ok=True)
    out_csv = os.path.join(out_dir, 'diagnostic_report.csv')
    pd.DataFrame(rows).to_csv(out_csv, index=False)

    # print a short summary
    dfout = pd.DataFrame(rows)
    total = len(dfout)
    print('Diagnostic run for', latest)
    print('Total tickers scanned:', total)
    for col in ['beta1_discrep', 'beta3_discrep', 'cagr3_discrep', 'cagr5_discrep']:
        print(col, ':', int(dfout[col].sum()), 'rows flagged')
    print('Report written to', out_csv)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--oct25', default='./OCT25', help='Path to OCT25 folder')
    args = parser.parse_args()
    run(args.oct25)
