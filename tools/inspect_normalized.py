import glob
import os
import pandas as pd


def find_latest_normalized():
    base = os.path.join('backups', 'normalized_*')
    dirs = glob.glob(base)
    if not dirs:
        print('No backups/normalized_* directories found')
        return None, None
    dirs.sort(key=os.path.getmtime, reverse=True)
    d = dirs[0]
    files = glob.glob(os.path.join(d, '*_normalized_*.xlsx'))
    if not files:
        print('No normalized xlsx files in', d)
        return None, None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0], d


def inspect(file_path):
    print('Inspecting:', file_path)
    xls = pd.read_excel(file_path, sheet_name=None)
    sheet = 'NIFTY50'
    if sheet not in xls:
        print(f"Sheet {sheet} not found. Available sheets:", list(xls.keys()))
        return
    df = xls[sheet]
    print('\nColumns in NIFTY50 sheet:')
    print(df.columns.tolist())

    # Fields of interest
    keys = [
        'Ticker', 'Company Name', 'Price (Last)', 'Dividend Yield %', 'Dividend Rate',
        'CAGR 3Y %', 'CAGR 5Y %', 'Beta 1Y', 'Beta 3Y',
        'SMA20', 'SMA50', 'SMA200', 'RSI14', 'MACD Line', 'MACD Signal', 'MACD Hist',
        'ATR14', 'BB Upper', 'BB Lower', 'OBV', 'A/D Line', 'ADX14', 'Aroon Up', 'Aroon Down',
        'Stoch %K', 'Stoch %D', 'Alpha 1Y %'
    ]

    print('\nLooking up RELIANCE row:')
    mask = df['Ticker'].astype(str).str.upper().str.replace(r"\.NS$", "", regex=True).eq('RELIANCE')
    if not mask.any():
        # try symbol column
        if 'symbol' in df.columns:
            mask = df['symbol'].astype(str).str.upper().str.replace(r"\.NS$", "", regex=True).eq('RELIANCE')
    if not mask.any():
        print('RELIANCE row not found in sheet')
        return
    row = df.loc[mask].iloc[0]
    for k in keys:
        val = row.get(k, '<missing>')
        print(f"{k}: {val}")


if __name__ == '__main__':
    fp, d = find_latest_normalized()
    if fp:
        inspect(fp)
    else:
        print('No normalized workbook found to inspect')
