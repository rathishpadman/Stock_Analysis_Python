"""Verify RELIANCE values directly from yfinance (info + history-derived).

This script loads the latest pipeline output, extracts the RELIANCE row, then
fetches yfinance 'info', dividends, and historical data to produce authoritative
values and comparisons.
"""
import sys
import pathlib
import pandas as pd
import math

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from equity_engine.data_sources import to_yahoo, fetch_history_yf
from equity_engine import normalizers

try:
    import yfinance as yf
except Exception:
    yf = None


def find_latest_output(oct_dir=ROOT / 'OCT25'):
    p = pathlib.Path(oct_dir)
    if not p.exists():
        return None
    files = sorted([f for f in p.glob('Stock_Analysis_*.xlsx')], key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0] if files else None


def load_nifty50(workbook_path):
    xl = pd.ExcelFile(workbook_path)
    if 'NIFTY50' not in xl.sheet_names:
        return xl.parse(xl.sheet_names[0])
    return xl.parse('NIFTY50')


def run():
    workbook = find_latest_output()
    if workbook is None:
        print('No pipeline output found in OCT25')
        return 2
    print('Inspecting:', workbook)
    df = load_nifty50(workbook)
    rel = df[df['Ticker'].astype(str).str.upper() == 'RELIANCE']
    if rel.empty:
        print('RELIANCE row not found in NIFTY50 sheet')
        return 2
    row = rel.iloc[0].to_dict()

    # Prepare yahoo ticker
    ytick = to_yahoo('RELIANCE', '.NS')
    if yf is None:
        print('yfinance not available')
        return 2

    t = yf.Ticker(ytick)
    info = {}
    try:
        info = t.info or {}
    except Exception:
        # some yfinance versions can raise; fall back to empty
        info = {}

    # vendor info fields
    vendor_div_yield = None
    vendor_div_rate = None
    try:
        if 'dividendYield' in info and info.get('dividendYield') is not None:
            vendor_div_yield = float(info.get('dividendYield')) * 100.0
        if 'dividendRate' in info and info.get('dividendRate') is not None:
            vendor_div_rate = float(info.get('dividendRate'))
    except Exception:
        pass

    # dividends history (trailing 12 months)
    divs = None
    try:
        divs = t.dividends
    except Exception:
        divs = None

    hist_price = fetch_history_yf(ytick, years=5)

    # compute trailing-12m dividend sum and yield from last close
    history_div_yield = None
    history_div_rate = None
    try:
        if divs is not None and not divs.empty:
            last_date = divs.index.max()
            cutoff = last_date - pd.DateOffset(months=12)
            recent = divs[divs.index > cutoff]
            total_div = recent.sum()
            if total_div > 0:
                history_div_rate = float(total_div)
                if not hist_price.empty and 'Close' in hist_price.columns:
                    last_price = float(hist_price['Close'].iloc[-1])
                    if last_price > 0:
                        history_div_yield = (total_div / last_price) * 100.0
    except Exception:
        pass

    # compute metrics using our normalizers (which use yfinance/history)
    tech_vals, tech_info = normalizers.compute_technicals_for_ticker('RELIANCE', years=2)
    c3, c3info = normalizers.compute_cagr_for_ticker('RELIANCE', years=3)
    c5, c5info = normalizers.compute_cagr_for_ticker('RELIANCE', years=5)
    b1, b1info = normalizers.compute_beta('RELIANCE', years=1)
    b3, b3info = normalizers.compute_beta('RELIANCE', years=3)
    adl, adlinfo = normalizers.compute_adl('RELIANCE', years=2)
    alpha1, alphainfo = normalizers.compute_alpha('RELIANCE', years=1)

    # print comparison
    print('\nField | Sheet Value | yfinance.info | yfinance.history-computed')
    print('-----|-------------|---------------|-------------------------')

    def disp(k):
        v = row.get(k, None)
        return v

    print(f"Dividend Yield % | {disp('Dividend Yield %')} | {vendor_div_yield} | {history_div_yield}")
    print(f"Dividend Rate | {disp('Dividend Rate')} | {vendor_div_rate} | {history_div_rate}")
    print(f"CAGR 3Y % | {disp('CAGR 3Y %')} | - | {c3 * 100.0 if c3==c3 else None}")
    print(f"CAGR 5Y % | {disp('CAGR 5Y %')} | - | {c5 * 100.0 if c5==c5 else None}")
    print(f"Beta 1Y | {disp('Beta 1Y')} | {info.get('beta', None)} | {b1}")
    print(f"Beta 3Y | {disp('Beta 3Y')} | - | {b3}")
    print(f"A/D Line | {disp('A/D Line')} | - | {adl}")
    print(f"Alpha 1Y % | {disp('Alpha 1Y %')} | - | {alpha1 * 100.0 if alpha1==alpha1 else None}")

    # Show some technicals
    for tk in ['SMA20', 'SMA50', 'SMA200', 'RSI14', 'MACD Line']:
        print(f"{tk} | {disp(tk)} | - | {tech_vals.get(tk)}")

    return 0


if __name__ == '__main__':
    raise SystemExit(run())
