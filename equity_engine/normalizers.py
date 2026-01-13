"""
Generic normalizers for key/value two-column CSVs.

This module provides a conservative dividend normalization heuristic and helpers
to compute per-key suggested corrections. It's intentionally small and safe — it
only returns suggestions and does not write to the original files.
"""
from typing import Dict, Any, Tuple, List
import re
import numpy as np
import pandas as pd
from .data_sources import to_yahoo, fetch_history_yf
import math
try:
    import yfinance as yf
except Exception:
    yf = None
from . import technical as technical_module


def _parse_number(s: Any) -> float:
    if s is None:
        return float('nan')
    if isinstance(s, (int, float)):
        return float(s)
    try:
        st = str(s).strip()
        if st.endswith('%'):
            st = st[:-1]
        # remove commas
        st = st.replace(',', '')
        # empty
        if st == '':
            return float('nan')
        return float(st)
    except Exception:
        return float('nan')


def normalize_dividend(kv: Dict[str, str], ticker: str = None, live_price: float = None) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
    """
    Heuristic normalization for dividend-related keys in a key/value dict.

    Returns (suggested_kv, explanations) where suggested_kv contains recommended
    values (only keys present in suggestions) and explanations is a list of change
    records with reason and confidence.
    """
    suggestions: Dict[str, str] = {}
    explanations: List[Dict[str, Any]] = []

    # Candidate keys that vendors use
    yield_keys = [
        'dividendYield', 'Dividend Yield %', 'Dividend Yield', 'dividend_yield',
        'DividendYield', 'dividendYield_meta'
    ]
    rate_keys = ['dividendRate', 'Dividend Rate', 'DPS', 'dividend_rate']

    # Find first present yield and rate
    raw_yield = None
    for k in yield_keys:
        if k in kv and str(kv[k]).strip() not in ('', 'nan', 'NaN'):
            raw_yield = kv[k]
            yield_key_found = k
            break

    raw_rate = None
    for k in rate_keys:
        if k in kv and str(kv[k]).strip() not in ('', 'nan', 'NaN'):
            raw_rate = kv[k]
            rate_key_found = k
            break

    # 1) If ticker provided try to compute yield from dividend history (trailing 12 months)
    if ticker and yf is not None:
        try:
            ytick = to_yahoo(str(ticker), '.NS')
            yf_t = yf.Ticker(ytick)
            divs = yf_t.dividends
            if not divs.empty:
                # sum dividends in last 12 months
                last_date = divs.index.max()
                cutoff = last_date - pd.DateOffset(months=12)
                recent = divs[divs.index > cutoff]
                total_div = recent.sum()
                if total_div > 0:
                    # determine price
                    price = None
                    if live_price and live_price == live_price and live_price > 0:
                        price = float(live_price)
                    else:
                        hist = fetch_history_yf(ytick, years=0.1)
                        if not hist.empty and 'Close' in hist.columns:
                            price = float(hist['Close'].iloc[-1])
                    if price and price > 0:
                        yield_pct = (total_div / price) * 100.0
                        # recommend both rate (DPS) and yield
                        suggestions['Dividend Rate'] = f"{float(total_div):.6f}"
                        suggestions['Dividend Yield %'] = f"{float(yield_pct):.6f}"
                        explanations.append({
                            'key': 'dividends_history',
                            'original': None,
                            'suggested': {
                                'Dividend Rate': suggestions['Dividend Rate'],
                                'Dividend Yield %': suggestions['Dividend Yield %']
                            },
                            'reason': 'Computed from trailing-12-month dividends',
                            'confidence': 0.98,
                        })
                        return suggestions, explanations
        except Exception:
            pass

    # 2) Prefer vendor-declared yield if present (fallback if history unavailable)
    if raw_yield is not None:
        val = _parse_number(raw_yield)
        if val == val and 0 <= val <= 100:
            # Accept vendor value but normalize formatting
            suggestions['Dividend Yield %'] = f"{float(val):.6f}"
            explanations.append({
                'key': yield_key_found,
                'original': raw_yield,
                'suggested': suggestions['Dividend Yield %'],
                'reason': 'Vendor-declared dividend yield used as fallback',
                'confidence': 0.6,
            })
            return suggestions, explanations

    # Normalize yield if present (fallback heuristics)
    if raw_yield is not None:
        val = _parse_number(raw_yield)
        reason = ''
        confidence = 0.5
        suggested_pct = None

        if val != val:  # nan
            pass
        else:
            # Heuristics for scaling/units
            if val < 0:
                # negative yields are unusual; keep as-is but low confidence
                suggested_pct = val
                reason = 'Negative yield preserved'
                confidence = 0.3
            elif val == 0:
                suggested_pct = 0.0
                reason = 'Zero yield'
                confidence = 0.9
            elif val <= 1.0:
                # probably decimal form (0.0206) => percent
                suggested_pct = val * 100.0
                reason = 'Yield in decimal form converted to percent'
                confidence = 0.9
            elif 1.0 < val <= 20.0:
                # likely already percent (e.g., 2.06)
                suggested_pct = val
                reason = 'Yield appears to be percent already'
                confidence = 0.9
            elif 20.0 < val <= 10000.0:
                # likely scaled (e.g., 206 -> 2.06) -> divide by 100
                suggested_pct = val / 100.0
                reason = 'Large numeric likely scaled by 100 (e.g., 206 -> 2.06%)'
                confidence = 0.8
            else:
                suggested_pct = val
                reason = 'Unusual numeric yield preserved'
                confidence = 0.4

            if suggested_pct is not None:
                # Format to a consistent string with 2 decimals
                suggestions['Dividend Yield %'] = f"{suggested_pct:.2f}"
                explanations.append({
                    'key': yield_key_found,
                    'original': raw_yield,
                    'suggested': suggestions['Dividend Yield %'],
                    'reason': reason,
                    'confidence': confidence,
                })

    # Normalize rate if present and derive yield if missing
    if raw_rate is not None:
        rv = _parse_number(raw_rate)
        if rv == rv:
            # If Shares Outstanding or Price information is not available here we cannot reliably
            # compute yield from rate. So we just normalize DPS/rate formatting.
            suggestions['Dividend Rate'] = f"{rv:.2f}"
            explanations.append({
                'key': rate_key_found,
                'original': raw_rate,
                'suggested': suggestions['Dividend Rate'],
                'reason': 'Normalized dividend rate formatting',
                'confidence': 0.9,
            })

    # If yield missing but rate present and Price available in kv, attempt compute
    if ('Dividend Yield %' not in suggestions) and raw_rate is not None:
        # attempt if price exists
        price_keys = ['Price (Last)', 'lastPrice', 'close', 'Price']
        price_val = None
        for pk in price_keys:
            if pk in kv and str(kv[pk]).strip() not in ('', 'nan', 'NaN'):
                price_val = _parse_number(kv[pk])
                break
        if price_val and price_val == price_val and price_val > 0:
            dv = _parse_number(raw_rate)
            if dv == dv:
                yield_pct = dv / price_val * 100.0
                suggestions['Dividend Yield %'] = f"{yield_pct:.2f}"
                explanations.append({
                    'key': 'computed_from_rate_and_price',
                    'original': raw_rate,
                    'suggested': suggestions['Dividend Yield %'],
                    'reason': 'Computed yield from Dividend Rate and Price',
                    'confidence': 0.6,
                })

    return suggestions, explanations


def compute_technicals_for_ticker(ticker: str, years: int = 2) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Fetch history and compute canonical technicals using equity_engine.technical.
    Returns (latest_values_dict, info)
    """
    info = {'method': 'technical_module', 'confidence': 0.0}
    try:
        if not ticker or str(ticker).strip() == '':
            return {}, info
        ytick = to_yahoo(str(ticker), '.NS')
        hist = fetch_history_yf(ytick, years=years)
        if hist.empty or 'Close' not in hist.columns:
            return {}, info
        tech = technical_module.compute_technicals(hist)
        if tech is None or tech.empty:
            return {}, info
        last = tech.iloc[-1]
        # pick desired keys
        keys = [
            'SMA20', 'SMA50', 'SMA200', 'RSI14', 'MACD Line', 'MACD Signal', 'MACD Hist',
            'ATR14', 'BB Upper', 'BB Lower', 'OBV', 'ADL', 'ADX14', 'Aroon Up', 'Aroon Down',
            'Stoch %K', 'Stoch %D'
        ]
        vals = {}
        for k in keys:
            if k in last.index:
                v = last.get(k)
                if v == v:
                    vals[k] = float(v)

        # Bollinger Bands fallback: compute from Close if BBs are missing
        try:
            if ("BB Upper" not in vals or "BB Lower" not in vals) and "Close" in hist.columns:
                close = hist['Close'].astype(float).dropna()
                if len(close) >= 20:
                    ma = close.rolling(window=20).mean()
                    sd = close.rolling(window=20).std()
                    bb_upper = (ma + 2 * sd).iloc[-1]
                    bb_lower = (ma - 2 * sd).iloc[-1]
                    if np.isfinite(bb_upper) and np.isfinite(bb_lower):
                        vals['BB Upper'] = float(bb_upper)
                        vals['BB Lower'] = float(bb_lower)
        except Exception:
            pass

        info['confidence'] = 0.9
        return vals, info
    except Exception:
        return {}, info


def diff_keyvalues(original: Dict[str, str], suggested: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Given original and suggested key/value dicts, produce a list of diffs.
    Each diff is a dict: {key, original, suggested, reason, confidence}
    """
    diffs = []
    for k, v in suggested.items():
        orig_val = original.get(k, '')
        if str(orig_val).strip() != str(v).strip():
            diffs.append({
                'key': k,
                'original': orig_val,
                'suggested': v,
            })
    return diffs


def compute_beta(ticker: str, index_symbol: str = '^NSEI', years: int = 2, window_days: int = 252) -> Tuple[float, Dict[str, Any]]:
    """
    Compute 1-year beta for a given ticker vs an index using historical closes.

    Returns (beta, info) where info contains method and confidence.

    Note: ticker should be the raw symbol (e.g., 'RELIANCE' or 'RELIANCE.NS');
    we convert to Yahoo ticker using `to_yahoo` and fetch history via fetch_history_yf.
    """
    info = {'method': 'covariance', 'index': index_symbol, 'confidence': 0.0}
    try:
        if not ticker or str(ticker).strip() == '':
            return float('nan'), info
        # convert to yahoo ticker (assume .NS suffix)
        ytick = to_yahoo(str(ticker), '.NS')
        hist = fetch_history_yf(ytick, years=years)
        idx_hist = fetch_history_yf(index_symbol, years=years)
        if hist.empty or idx_hist.empty or 'Close' not in hist.columns or 'Close' not in idx_hist.columns:
            return float('nan'), info
        # align on dates and compute daily returns
        s_daily = hist['Close'].pct_change().dropna()
        m_daily = idx_hist['Close'].pct_change().dropna()
        # align by date
        joined = s_daily.to_frame('s').join(m_daily.to_frame('m'), how='inner').dropna()

        # If joined daily returns are insufficient, fall back to monthly returns (more overlap)
        min_daily_points = max(60, int(window_days * 0.5))
        used_method = 'daily'
        if joined.empty or len(joined) < min_daily_points:
            try:
                s_month = hist['Close'].resample('M').last().pct_change().dropna()
                m_month = idx_hist['Close'].resample('M').last().pct_change().dropna()
                joinedm = s_month.to_frame('s').join(m_month.to_frame('m'), how='inner').dropna()
                if not joinedm.empty and len(joinedm) >= 12:
                    joined = joinedm
                    used_method = 'monthly'
                else:
                    # if still insufficient, return nan
                    return float('nan'), info
            except Exception:
                return float('nan'), info

        # focus on last window_days (or months when monthly used) if available
        if used_method == 'daily' and len(joined) > window_days:
            joined = joined.tail(window_days)
        # compute covariance and beta
        cov = joined['s'].cov(joined['m'])
        var = joined['m'].var()
        if var == 0 or np.isnan(var):
            return float('nan'), info

        beta = cov / var
        info['confidence'] = 0.9 if used_method == 'daily' else 0.8
        info['n_points'] = len(joined)
        info['method'] = f'covariance_{used_method}_{len(joined)}'
        return float(beta), info
    except Exception:
        return float('nan'), info


def compute_cagr_for_ticker(ticker: str, years: int = 3) -> Tuple[float, Dict[str, Any]]:
    """
    Compute CAGR over `years` for the ticker using Close prices.
    Returns (cagr_fraction, info)
    """
    info = {'method': 'price_ratio', 'years': years, 'confidence': 0.0}
    try:
        if not ticker or str(ticker).strip() == '':
            return float('nan'), info
        ytick = to_yahoo(str(ticker), '.NS')
        hist = fetch_history_yf(ytick, years=years+0.1)
        if hist.empty or 'Close' not in hist.columns:
            return float('nan'), info
        # use first and last Close
        first = hist['Close'].iloc[0]
        last = hist['Close'].iloc[-1]
        if first <= 0 or math.isnan(first) or math.isnan(last):
            return float('nan'), info
        cagr = (last / first) ** (1.0 / years) - 1.0
        info['confidence'] = 0.85
        info['n_points'] = len(hist)
        return float(cagr), info
    except Exception:
        return float('nan'), info


def compute_alpha(ticker: str, index_symbol: str = '^NSEI', years: int = 1, rf_annual: float = 0.05) -> Tuple[float, Dict[str, Any]]:
    """
    Compute annualized Alpha over `years` for ticker vs index: alpha = (r_stock - rf) - beta*(r_index - rf)
    Returns alpha as fraction and info dict.
    """
    info = {'method': 'alpha_covariance', 'confidence': 0.0}
    try:
        if not ticker or str(ticker).strip() == '':
            return float('nan'), info
        # compute annualized returns
        ytick = to_yahoo(str(ticker), '.NS')
        hist = fetch_history_yf(ytick, years=years+0.1)
        idx_hist = fetch_history_yf(index_symbol, years=years+0.1)
        if hist.empty or idx_hist.empty or 'Close' not in hist.columns or 'Close' not in idx_hist.columns:
            return float('nan'), info
        # compute total returns
        s_first = hist['Close'].iloc[0]
        s_last = hist['Close'].iloc[-1]
        m_first = idx_hist['Close'].iloc[0]
        m_last = idx_hist['Close'].iloc[-1]
        if s_first <= 0 or m_first <= 0:
            return float('nan'), info
        r_stock = (s_last / s_first) ** (1.0 / years) - 1.0
        r_index = (m_last / m_first) ** (1.0 / years) - 1.0
        beta, beta_info = compute_beta(ticker, index_symbol=index_symbol, years=years+1, window_days=252)
        if beta != beta or math.isnan(beta):
            return float('nan'), info
        alpha = (r_stock - rf_annual) - beta * (r_index - rf_annual)
        info['confidence'] = 0.8
        info['r_stock'] = r_stock
        info['r_index'] = r_index
        info['beta_used'] = beta
        return float(alpha), info
    except Exception:
        return float('nan'), info


def compute_adl(ticker: str, years: int = 2) -> Tuple[float, Dict[str, Any]]:
    """
    Compute the Accumulation/Distribution Line (A/D Line) for the ticker using history.
    Returns (last_adl_value, info)
    """
    info = {'method': 'adl', 'confidence': 0.0}
    try:
        if not ticker or str(ticker).strip() == '':
            return float('nan'), info
        ytick = to_yahoo(str(ticker), '.NS')
        hist = fetch_history_yf(ytick, years=years+0.1)
        if hist.empty or not all(c in hist.columns for c in ['High', 'Low', 'Close', 'Volume']):
            return float('nan'), info
        h = hist[['High', 'Low', 'Close', 'Volume']].copy().dropna()
        if h.empty:
            return float('nan'), info
        # Money Flow Multiplier and Volume
        mfm = ((h['Close'] - h['Low']) - (h['High'] - h['Close'])) / (h['High'] - h['Low']).replace({0: np.nan})
        mfv = mfm * h['Volume']
        adl = mfv.cumsum()
        last_adl = adl.iloc[-1]
        info['confidence'] = 0.75
        info['n_points'] = len(adl)
        return float(last_adl), info
    except Exception:
        return float('nan'), info
