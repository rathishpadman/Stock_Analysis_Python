"""
List columns present in the latest pipeline Excel output (OCT25) for the NIFTY50 sheet.
"""
import os
import glob
import pandas as pd


def find_latest(oct25_dir):
    pattern = os.path.join(oct25_dir, 'Stock_Analysis_*.xlsx')
    files = glob.glob(pattern)
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def main():
    oct25 = os.path.join('.', 'OCT25')
    latest = find_latest(oct25)
    if not latest:
        print('No pipeline output found in', oct25)
        return
    print('Latest file:', latest)
    try:
        df = pd.read_excel(latest, sheet_name='NIFTY50')
    except Exception as e:
        print('Could not open NIFTY50 sheet:', e)
        return
    cols = list(df.columns)
    print('\nColumns in NIFTY50 sheet (count={}):'.format(len(cols)))
    for c in cols:
        print(c)

if __name__ == '__main__':
    main()
