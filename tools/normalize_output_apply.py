"""
Apply normalizers to the latest pipeline Excel output in OCT25 and write a new workbook
with normalized values and a provenance sheet. Does not overwrite the original file in OCT25;
instead creates a backup copy and writes normalized workbook into backups/normalized_<ts>/

Usage:
    python -m tools.normalize_output_apply --oct25 .\OCT25
"""
import os
import glob
import shutil
import argparse
import datetime as dt
import pandas as pd
from equity_engine import normalizers
import math


def find_latest_output(oct25_dir: str):
    pattern = os.path.join(oct25_dir, 'Stock_Analysis_*.xlsx')
    files = glob.glob(pattern)
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def apply_normalization_to_workbook(input_path: str, out_dir: str):
    ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs(out_dir, exist_ok=True)
    # backup original workbook
    backup_path = os.path.join(out_dir, os.path.basename(input_path) + f'.bak_{ts}')
    shutil.copy2(input_path, backup_path)

    # Read all sheets
    xls = pd.read_excel(input_path, sheet_name=None)

    sheet_name = 'NIFTY50'
    provenance = []

    if sheet_name not in xls:
        print(f"Sheet '{sheet_name}' not found in {input_path}; no normalization applied.")
    else:
        df = xls[sheet_name].copy()
        # Ensure common columns exist
        for idx, row in df.iterrows():
            # build kv dict from relevant columns
            kv = {}
            # pick columns that might be present
            for col in ['Dividend Yield %', 'dividendYield', 'Dividend Rate', 'dividendRate', 'DPS', 'Price (Last)', 'lastPrice', 'close', 'Price']:
                if col in df.columns:
                    kv[col] = row.get(col, '')

            # pass Ticker and live price so normalize_dividend can compute history-first
            ticker_val = row.get('Ticker', '') if 'Ticker' in df.columns else ''
            live_price = None
            for pcol in ['Price (Last)', 'lastPrice', 'close', 'Price']:
                if pcol in df.columns and str(row.get(pcol, '')).strip() not in ('', 'nan', 'NaN'):
                    try:
                        live_price = float(row.get(pcol))
                        break
                    except Exception:
                        live_price = None

            suggestions, explanations = normalizers.normalize_dividend(kv, ticker=ticker_val, live_price=live_price)
            if explanations:
                for ex in explanations:
                    suggested = ex.get('suggested')
                    key = ex.get('key')
                    # suggested may be a dict with multiple keys (e.g., Dividend Rate and Yield)
                    if isinstance(suggested, dict):
                        for sk, sv in suggested.items():
                            target_col = None
                            if sk in ('dividendYield', 'Dividend Yield %', 'Dividend Yield'):
                                target_col = 'Dividend Yield %'
                            elif sk in ('dividendRate', 'Dividend Rate', 'DPS'):
                                target_col = 'Dividend Rate'
                            else:
                                target_col = sk
                            if target_col and target_col in df.columns:
                                orig_val = df.at[idx, target_col]
                                # coerce numeric strings to float when possible
                                try:
                                    new_val = float(sv)
                                except Exception:
                                    new_val = sv
                                df.at[idx, target_col] = new_val
                                provenance.append({
                                    'row_index': idx,
                                    'Ticker': df.at[idx, 'Ticker'] if 'Ticker' in df.columns else '',
                                    'sheet_key': key,
                                    'target_column': target_col,
                                    'original': orig_val,
                                    'suggested': new_val,
                                    'reason': ex.get('reason', ''),
                                    'confidence': ex.get('confidence', ''),
                                })
                    else:
                        # single suggestion
                        target_col = None
                        if key in ('dividendYield', 'Dividend Yield %', 'Dividend Yield'):
                            target_col = 'Dividend Yield %'
                        elif key in ('dividendRate', 'Dividend Rate', 'DPS', 'dividend_rate'):
                            target_col = 'Dividend Rate'
                        elif key == 'computed_from_rate_and_price':
                            target_col = 'Dividend Yield %'
                        else:
                            # try to use suggested key as column name
                            target_col = ex.get('key')

                        if target_col and target_col in df.columns:
                            orig_val = df.at[idx, target_col]
                            try:
                                new_val = float(suggested)
                            except Exception:
                                new_val = suggested
                            df.at[idx, target_col] = new_val
                            provenance.append({
                                'row_index': idx,
                                'Ticker': df.at[idx, 'Ticker'] if 'Ticker' in df.columns else '',
                                'sheet_key': key,
                                'target_column': target_col,
                                'original': orig_val,
                                'suggested': new_val,
                                'reason': ex.get('reason', ''),
                                'confidence': ex.get('confidence', ''),
                            })

            # Regardless of dividend explanations, compute Beta/CAGR/Alpha/A-D for each ticker row
            try:
                if 'Ticker' in df.columns:
                    tval = row.get('Ticker', '')
                else:
                    tval = ''

                # compute Beta 1Y and Beta 3Y
                try:
                    beta1_val, beta1_info = normalizers.compute_beta(tval, index_symbol='^NSEI', years=1, window_days=252)
                    beta3_val, beta3_info = normalizers.compute_beta(tval, index_symbol='^NSEI', years=3, window_days=252)
                    if beta1_val == beta1_val and not math.isnan(beta1_val):
                        if 'Beta 1Y' not in df.columns:
                            df['Beta 1Y'] = ''
                        orig_beta = df.at[idx, 'Beta 1Y'] if 'Beta 1Y' in df.columns else ''
                        df.at[idx, 'Beta 1Y'] = float(beta1_val)
                        provenance.append({
                            'row_index': idx,
                            'Ticker': df.at[idx, 'Ticker'] if 'Ticker' in df.columns else '',
                            'sheet_key': 'Beta 1Y',
                            'target_column': 'Beta 1Y',
                            'original': orig_beta,
                            'suggested': float(beta1_val),
                            'reason': beta1_info.get('method', 'computed_beta'),
                            'confidence': beta1_info.get('confidence', 0),
                        })
                    if beta3_val == beta3_val and not math.isnan(beta3_val):
                        if 'Beta 3Y' not in df.columns:
                            df['Beta 3Y'] = ''
                        orig_beta3 = df.at[idx, 'Beta 3Y'] if 'Beta 3Y' in df.columns else ''
                        df.at[idx, 'Beta 3Y'] = float(beta3_val)
                        provenance.append({
                            'row_index': idx,
                            'Ticker': df.at[idx, 'Ticker'] if 'Ticker' in df.columns else '',
                            'sheet_key': 'Beta 3Y',
                            'target_column': 'Beta 3Y',
                            'original': orig_beta3,
                            'suggested': float(beta3_val),
                            'reason': beta3_info.get('method', 'computed_beta'),
                            'confidence': beta3_info.get('confidence', 0),
                        })
                except Exception:
                    pass

                # Compute CAGR 3Y and 5Y
                try:
                    cagr3, cinfo3 = normalizers.compute_cagr_for_ticker(tval, years=3)
                    cagr5, cinfo5 = normalizers.compute_cagr_for_ticker(tval, years=5)
                    if cagr3 == cagr3 and not pd.isna(cagr3):
                        if 'CAGR 3Y %' not in df.columns:
                            df['CAGR 3Y %'] = ''
                        orig = df.at[idx, 'CAGR 3Y %'] if 'CAGR 3Y %' in df.columns else ''
                        df.at[idx, 'CAGR 3Y %'] = float(cagr3 * 100.0)
                        provenance.append({
                            'row_index': idx, 'Ticker': tval, 'sheet_key': 'CAGR 3Y %', 'target_column': 'CAGR 3Y %',
                            'original': orig, 'suggested': float(cagr3 * 100.0), 'reason': cinfo3.get('method', ''), 'confidence': cinfo3.get('confidence', 0)
                        })
                    if cagr5 == cagr5 and not pd.isna(cagr5):
                        if 'CAGR 5Y %' not in df.columns:
                            df['CAGR 5Y %'] = ''
                        orig = df.at[idx, 'CAGR 5Y %'] if 'CAGR 5Y %' in df.columns else ''
                        df.at[idx, 'CAGR 5Y %'] = float(cagr5 * 100.0)
                        provenance.append({
                            'row_index': idx, 'Ticker': tval, 'sheet_key': 'CAGR 5Y %', 'target_column': 'CAGR 5Y %',
                            'original': orig, 'suggested': float(cagr5 * 100.0), 'reason': cinfo5.get('method', ''), 'confidence': cinfo5.get('confidence', 0)
                        })
                except Exception:
                    pass

                # Alpha 1Y
                try:
                    alpha1, ainfo = normalizers.compute_alpha(tval, index_symbol='^NSEI', years=1, rf_annual=0.05)
                    if alpha1 == alpha1 and not pd.isna(alpha1):
                        if 'Alpha 1Y %' not in df.columns:
                            df['Alpha 1Y %'] = ''
                        orig = df.at[idx, 'Alpha 1Y %'] if 'Alpha 1Y %' in df.columns else ''
                        df.at[idx, 'Alpha 1Y %'] = float(alpha1 * 100.0)
                        provenance.append({
                            'row_index': idx, 'Ticker': tval, 'sheet_key': 'Alpha 1Y %', 'target_column': 'Alpha 1Y %',
                            'original': orig, 'suggested': float(alpha1 * 100.0), 'reason': ainfo.get('method', ''), 'confidence': ainfo.get('confidence', 0)
                        })
                except Exception:
                    pass

                # A/D Line
                try:
                    adl, adlinfo = normalizers.compute_adl(tval, years=2)
                    if adl == adl and not pd.isna(adl):
                        if 'A/D Line' not in df.columns:
                            df['A/D Line'] = ''
                        orig = df.at[idx, 'A/D Line'] if 'A/D Line' in df.columns else ''
                        df.at[idx, 'A/D Line'] = float(adl)
                        provenance.append({
                            'row_index': idx, 'Ticker': tval, 'sheet_key': 'A/D Line', 'target_column': 'A/D Line',
                            'original': orig, 'suggested': float(adl), 'reason': adlinfo.get('method', ''), 'confidence': adlinfo.get('confidence', 0)
                        })
                except Exception:
                    pass
            except Exception:
                # Protect per-row loop from unexpected failures
                pass

        # replace sheet
        xls[sheet_name] = df

    # write normalized workbook
    out_path = os.path.join(out_dir, os.path.basename(input_path).replace('.xlsx', f'_normalized_{ts}.xlsx'))
    with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
        for name, sheet in xls.items():
            sheet.to_excel(writer, sheet_name=name, index=False)
        # write provenance if any
        if provenance:
            prov_df = pd.DataFrame(provenance)
            prov_df.to_excel(writer, sheet_name='Normalization_Provenance', index=False)

    return backup_path, out_path, provenance


def main(oct25_dir: str):
    latest = find_latest_output(oct25_dir)
    if not latest:
        print('No pipeline output XLSX found in', oct25_dir)
        return
    ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join('backups', f'normalized_{ts}')
    backup_path, out_path, provenance = apply_normalization_to_workbook(latest, out_dir)
    print('Original workbook backed up to:', backup_path)
    print('Normalized workbook written to:', out_path)
    if provenance:
        print('Normalization applied to', len(provenance), 'cells. See sheet Normalization_Provenance in the output workbook.')
    else:
        print('No normalizations suggested by the heuristic.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--oct25', default='./OCT25', help='Path to OCT25 folder')
    args = parser.parse_args()
    main(args.oct25)
