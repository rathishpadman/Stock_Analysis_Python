from typing import List, Optional
import urllib.parse
import numpy as np
import pandas as pd
import requests
import yfinance as yf
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
def get_nse_index_constituents(index_name: str) -> pd.DataFrame:
    """
    Fetch constituents for an NSE index by display name, e.g. "NIFTY 50".
    Normalizes response to always include at least 'symbol' and 'companyName'.
    Filters out non-ticker rows (e.g. the index name row "NIFTY 50").
    """
    base = "https://www.nseindia.com"
    api_path = f"/api/equity-stockIndices?index={urllib.parse.quote(index_name, safe='')}"
    url = f"{base}{api_path}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"{base}/",
        "Connection": "keep-alive",
    }

    s = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    s.mount("https://", adapter)
    s.mount("http://", adapter)

    # Prime session
    for path in ["/", "/market-data", "/market-data/live-equity-market"]:
        try:
            s.get(f"{base}{path}", headers=headers, timeout=10)
        except Exception as e:
            logging.debug("Session priming request to %s failed: %s", path, e)
        time.sleep(0.35)

    try:
        r = s.get(url, headers=headers, timeout=20)
    except Exception as e:
        raise RuntimeError(f"Failed to request NSE API for {index_name}: {e}")

    if r.status_code == 401:
        logging.debug("Received 401 from NSE API for %s, retrying with alternate headers", index_name)
        alt_headers = dict(headers)
        alt_headers["Referer"] = f"{base}/market-data/live-equity-market"
        alt_headers["X-Requested-With"] = "XMLHttpRequest"
        try:
            r = s.get(url, headers=alt_headers, timeout=20)
        except Exception as e:
            raise RuntimeError(f"Retry to NSE API failed for {index_name}: {e}")

    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        is_ci = os.getenv("CI", "false").lower() == "true"
        # If in CI (GitHub Actions) or general failure, try fallback
        fallback_path = os.path.join("data", "nifty200_staging.csv")
        if os.path.exists(fallback_path):
            logging.warning(
                f"NSE request failed for {index_name} ({e}). "
                f"Falling back to local file: {fallback_path}"
            )
            df_fallback = pd.read_csv(fallback_path)
            # Normalize columns to match API expectation
            # CSV has 'ticker' like 'VEDL.NS' -> symbol 'VEDL'
            # 'company_name' -> 'companyName'
            if "ticker" in df_fallback.columns:
                df_fallback["symbol"] = df_fallback["ticker"].astype(str).str.replace(r"\.NS$", "", regex=True)
            if "company_name" in df_fallback.columns:
                df_fallback["companyName"] = df_fallback["company_name"]
            
            # If we are looking for a specific index, we might want to filter, 
            # but the staging file is likely NIFTY 200 which covers most.
            # For now, return the whole set as a safe fallback.
            return df_fallback
            
        raise RuntimeError(
            f"NSE request failed for {index_name}: {r.status_code} {r.reason}. "
            "This may be due to NSE blocking automated requests. "
            "Try running once in a browser to capture cookies, or add more priming requests."
        ) from e

    js = r.json()
    if "data" not in js:
        raise RuntimeError(f"Unexpected NSE response for {index_name}: missing 'data' field")

    df = pd.DataFrame(js["data"])

    # Ensure a 'symbol' column exists
    symbol_candidates = ["symbol", "code", "identifier", "ticker", "sc_code", "symbolName"]
    if "symbol" not in df.columns:
        for cand in symbol_candidates:
            if cand in df.columns:
                df["symbol"] = df[cand].astype(str)
                break
    if "symbol" not in df.columns:
        raise RuntimeError("NSE response missing a recognizable symbol column")

    df["symbol"] = df["symbol"].astype(str).str.strip()

    # Ensure a 'companyName' column exists; try common alternatives, otherwise fall back to symbol
    name_candidates = ["companyName", "company", "securityName", "name", "symbolName", "issuer"]
    if "companyName" not in df.columns:
        for cand in name_candidates:
            if cand in df.columns:
                df["companyName"] = df[cand].astype(str).str.strip()
                break
    if "companyName" not in df.columns:
        df["companyName"] = df["symbol"]

    # Filter out rows that are clearly not tickers (e.g. the index row "NIFTY 50", any entries with spaces,
    # or symbols containing characters unlikely in tickers). Keep typical ticker pattern: letters/numbers/dot/hyphen.
    idx_upper = index_name.upper().strip()
    sym_upper = df["symbol"].astype(str).str.upper().str.strip()
    valid_pattern = re.compile(r'^[A-Z0-9\.\-\&]+$')

    mask_valid = sym_upper.str.match(valid_pattern) & (sym_upper.str.len() > 1) & (sym_upper != idx_upper)
    filtered = df[mask_valid].copy()

    if filtered.empty:
        logging.warning("After filtering non-ticker rows, no constituents remain for %s. Returning original set.", index_name)
        # fallback: return deduped original df (so pipeline can proceed) but keep index row removed if exact match
        fallback = df[df["symbol"].str.upper().str.strip() != idx_upper].drop_duplicates(subset=["symbol"]).reset_index(drop=True)
        return fallback

    # Log symbols before and after filtering
    logging.info(f"Original symbols: {sorted(df['symbol'].tolist())}")
    logging.info(f"Filtered symbols: {sorted(filtered['symbol'].tolist())}")
    
    filtered = filtered.drop_duplicates(subset=["symbol"]).reset_index(drop=True)
    return filtered

def to_yahoo(symbol: str, suffix: Optional[str] = None) -> str:
    if suffix is None:
        suffix = ".NS"
    s = str(symbol).strip()
    if "." in s:
        return s
    if not suffix.startswith("."):
        suffix = f".{suffix}"
    return f"{s}{suffix}"

def fetch_company_metadata(symbols: List[str], yahoo_suffix: str = ".NS", pause: float = 0.35, attempts: int = 2) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    rows = []
    for sym in symbols:
        yahoo = to_yahoo(sym, yahoo_suffix)
        info = {}
        last_exc = None
        for a in range(attempts):
            try:
                t = yf.Ticker(yahoo)
                info = getattr(t, "info", {}) or {}
                if not info and hasattr(t, "fast_info"):
                    info = getattr(t, "fast_info") or {}
                
                # Get financial data
                try:
                    financials = t.financials
                    balance_sheet = t.balance_sheet
                    cash_flow = t.cashflow
                    if not financials.empty:
                        info['totalRevenue'] = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else None
                        info['ebitda'] = financials.loc['EBITDA'].iloc[0] if 'EBITDA' in financials.index else None
                        info['netIncome'] = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials.index else None
                    if not balance_sheet.empty:
                        info['totalDebt'] = balance_sheet.loc['Total Debt'].iloc[0] if 'Total Debt' in balance_sheet.index else None
                        info['totalEquity'] = balance_sheet.loc['Total Stockholder Equity'].iloc[0] if 'Total Stockholder Equity' in balance_sheet.index else None
                    if not cash_flow.empty:
                        info['operatingCashflow'] = cash_flow.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cash_flow.index else None
                        info['capitalExpenditures'] = cash_flow.loc['Capital Expenditure'].iloc[0] if 'Capital Expenditure' in cash_flow.index else None
                except:
                    pass
                
                break
            except Exception as e:
                last_exc = e
                logger.debug("yfinance.info error for %s (%s) attempt %d: %s", sym, yahoo, a + 1, e)
                time.sleep(0.2)
        
        # Calculate additional ratios
        try:
            if info.get('totalDebt') is not None and info.get('totalEquity') is not None and info['totalEquity'] != 0:
                info['debtToEquity'] = info['totalDebt'] / info['totalEquity']
            
            if info.get('netIncome') is not None and info.get('totalRevenue') is not None and info['totalRevenue'] != 0:
                info['netProfitMargin'] = info['netIncome'] / info['totalRevenue']
        except:
            pass
            
        row = {
            "symbol": sym,
            "yahoo": yahoo,
            "sector": info.get("sector") or info.get("Sector"),
            "industry": info.get("industry") or info.get("Industry"),
            "marketCap": info.get("marketCap") or info.get("market_cap"),
            "sharesOutstanding": info.get("sharesOutstanding"),
            "currency": info.get("currency", "INR"),
            "exchange": info.get("exchange"),
            "longBusinessSummary": info.get("longBusinessSummary") or info.get("longName") or info.get("shortName"),
            "fullTimeEmployees": info.get("fullTimeEmployees"),
            
            # Price metrics
            "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            
            # Financial metrics
            "totalRevenue": info.get("totalRevenue"),
            "ebitda": info.get("ebitda"),
            "netIncome": info.get("netIncome"),
            "operatingCashflow": info.get("operatingCashflow"),
            "capitalExpenditures": info.get("capitalExpenditures"),
            
            # Ratios and metrics
            "trailingPE": info.get("trailingPE"),
            "priceToBook": info.get("priceToBook"),
            "enterpriseToEbitda": info.get("enterpriseToEbitda"),
            "returnOnEquity": info.get("returnOnEquity"),
            "returnOnAssets": info.get("returnOnAssets"),
            "debtToEquity": info.get("debtToEquity"),
            "currentRatio": info.get("currentRatio"),
            "quickRatio": info.get("quickRatio"),
            
            # Growth and margins
            "revenueGrowth": info.get("revenueGrowth"),
            "earningsGrowth": info.get("earningsGrowth"),
            "profitMargins": info.get("profitMargins"),
            "operatingMargins": info.get("operatingMargins"),
            "grossMargins": info.get("grossMargins"),
            
            # Trading info
            "averageVolume": info.get("averageVolume"),
            "averageVolume10days": info.get("averageVolume10days"),
            
            # Additional metrics
            "beta": info.get("beta"),
            "trailingEps": info.get("trailingEps"),
            "forwardEps": info.get("forwardEps"),
            "dividendYield": info.get("dividendYield"),
            "isin": info.get("isin"),
            
            # Float data
            "floatShares": info.get("floatShares"),
            "sharesOutstanding": info.get("sharesOutstanding"),
            "impliedSharesOutstanding": info.get("impliedSharesOutstanding")
        }
        rows.append(row)
        time.sleep(pause)
    return pd.DataFrame(rows)

def safe_divide(a, b, default=""):
    """Safely divide two values, returning default if division not possible."""
    try:
        if a is None or b is None or b == 0:
            return default
        return float(a) / float(b)
    except (TypeError, ValueError):
        return default

def safe_multiply(a, b, default=""):
    """Safely multiply two values, returning default if multiplication not possible."""
    try:
        if a is None or b is None:
            return default
        return float(a) * float(b)
    except (TypeError, ValueError):
        return default

def calculate_additional_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate additional financial metrics and ratios from available data."""
    work = df.copy()

    def _num(series, fallback=None):
        base = work.get(series) if isinstance(series, str) else series
        if base is None:
            return pd.Series(fallback, index=work.index) if fallback is not None else pd.Series(np.nan, index=work.index)
        return pd.to_numeric(base, errors="coerce")

    # Basic aliases used repeatedly
    price = _num("currentPrice")
    price = price.fillna(_num("regularMarketPrice"))
    shares_out = _num("sharesOutstanding")
    float_shares = _num("floatShares")
    market_cap = _num("marketCap")
    net_income = _num("netIncome")
    total_revenue = _num("totalRevenue")
    ebitda = _num("ebitda")
    total_debt = _num("totalDebt")
    ocf = _num("operatingCashflow")
    capex = _num("capitalExpenditures")

    # Valuation ratios
    trailing_pe = _num("trailingPE")
    trailing_eps = _num("trailingEps")
    manual_pe = price / trailing_eps.replace(0, np.nan)
    income_pe = market_cap / net_income.replace(0, np.nan)
    work["P/E (TTM)"] = trailing_pe.where(trailing_pe > 0).combine_first(manual_pe).combine_first(income_pe)
    work["P/B"] = _num("priceToBook")
    revenue_per_share = total_revenue / shares_out.replace(0, np.nan)
    work["P/S Ratio"] = price / revenue_per_share
    work["EV/EBITDA (TTM)"] = _num("enterpriseToEbitda")
    work["PEG Ratio"] = _num("trailingPegRatio")

    # Profitability, growth, returns
    work["EPS Growth YoY %"] = _num("earningsGrowth") * 100
    work["Revenue Growth YoY %"] = _num("revenueGrowth") * 100
    work["Gross Profit Margin %"] = _num("grossMargins") * 100
    work["Operating Profit Margin %"] = _num("operatingMargins") * 100
    work["Net Profit Margin %"] = _num("profitMargins") * 100
    work["ROE TTM %"] = _num("returnOnEquity") * 100
    work["ROA %"] = _num("returnOnAssets") * 100

    # Liquidity & leverage
    work["Current Ratio"] = _num("currentRatio")
    work["Quick Ratio"] = _num("quickRatio")
    work["Debt/Equity"] = _num("debtToEquity")
    work["Interest Coverage"] = ebitda / total_debt.replace(0, np.nan)

    # Cash flow & capital metrics
    work["OCF TTM (INR Cr)"] = ocf / 1e7
    work["CapEx TTM (INR Cr)"] = capex / 1e7
    fcf = ocf - capex
    work["FCF TTM (INR Cr)"] = fcf / 1e7
    work["FCF Yield %"] = (fcf / market_cap.replace(0, np.nan)) * 100

    # Market size conversions
    work["Market Cap (INR Cr)"] = market_cap / 1e7
    work["Enterprise Value (INR Cr)"] = _num("enterpriseValue") / 1e7
    work["Revenue TTM (INR Cr)"] = total_revenue / 1e7
    work["EBITDA TTM (INR Cr)"] = ebitda / 1e7
    work["Net Income TTM (INR Cr)"] = net_income / 1e7

    # Trading metrics
    avg_vol = _num("averageVolume")
    avg_vol_10 = _num("averageVolume10days")
    work["Avg Daily Turnover 3M (INR Cr)"] = (avg_vol * price) / 1e7
    work["Avg Volume 1W"] = avg_vol_10
    vol_ratio = (avg_vol_10 / avg_vol.replace(0, np.nan)) * 100
    work["Volume vs 3M Avg %"] = vol_ratio

    # Free float, per-share, misc
    work["Free Float %"] = (float_shares / shares_out.replace(0, np.nan)) * 100
    work["Shares Outstanding"] = shares_out
    work["EPS TTM"] = trailing_eps
    work["Dividend Yield %"] = _num("dividendYield") * 100
    work["Currency"] = work.get("currency", "INR").fillna("INR")
    work["Exchange"] = work.get("exchange", "NSI").fillna("NSI")
    work["ISIN"] = work.get("isin", "").fillna("")
    work["Beta 1Y"] = _num("beta")

    # Technical anchors from fast_info
    work["52W High"] = _num("fiftyTwoWeekHigh")
    work["52W Low"] = _num("fiftyTwoWeekLow")
    work["SMA50"] = _num("fiftyDayAverage")
    work["SMA200"] = _num("twoHundredDayAverage")

    # Clean infinite / NaN values → empty string for template expectations
    work = work.replace([np.inf, -np.inf], np.nan)

    for col in [
        "P/E (TTM)", "P/B", "P/S Ratio", "EV/EBITDA (TTM)", "PEG Ratio",
        "EPS Growth YoY %", "Revenue Growth YoY %", "Gross Profit Margin %",
        "Operating Profit Margin %", "Net Profit Margin %", "ROE TTM %", "ROA %",
        "Current Ratio", "Quick Ratio", "Debt/Equity", "Interest Coverage",
        "OCF TTM (INR Cr)", "CapEx TTM (INR Cr)", "FCF TTM (INR Cr)", "FCF Yield %",
        "Market Cap (INR Cr)", "Enterprise Value (INR Cr)", "Revenue TTM (INR Cr)",
        "EBITDA TTM (INR Cr)", "Net Income TTM (INR Cr)", "Avg Daily Turnover 3M (INR Cr)",
        "Avg Volume 1W", "Volume vs 3M Avg %", "Free Float %", "Shares Outstanding",
        "EPS TTM", "Dividend Yield %", "Beta 1Y", "52W High", "52W Low", "SMA50", "SMA200"
    ]:
        if col in work.columns:
            work[col] = work[col].round(4)

    return work

def merge_constituents_with_metadata(df_const: pd.DataFrame, yahoo_suffix: str = ".NS") -> pd.DataFrame:
    if "symbol" not in df_const.columns:
        raise RuntimeError("constituents dataframe does not contain 'symbol' column")
    symbols = df_const["symbol"].astype(str).str.strip().tolist()
    meta = fetch_company_metadata(symbols, yahoo_suffix=yahoo_suffix)
    merged = df_const.merge(meta, on="symbol", how="left")
    
    # Calculate additional metrics for each stock
    with_metrics = calculate_additional_metrics(merged)
    return with_metrics
    

def fetch_history_yf(ticker: str, years: int = 5) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    # Use explicit start/end dates to avoid invalid 'period' strings for fractional years
    try:
        # Use tomorrow's date as end because yfinance end date is exclusive
        end = pd.Timestamp.today() + pd.Timedelta(days=1)
        days = max(5, int(round(float(years) * 365)))
        start = end - pd.Timedelta(days=days)
        # yfinance accepts start/end as date-like
        ticker_obj = yf.Ticker(ticker)
        # small retry loop to mitigate transient network/API failures
        last_exc = None
        for attempt in range(3):
            try:
                hist = ticker_obj.history(start=start.date(), end=end.date(), interval="1d", auto_adjust=True)
                break
            except Exception as e:
                last_exc = e
                logger.debug(f"{ticker}: Attempt {attempt + 1}/3 failed: {type(e).__name__}: {e}")
                time.sleep(0.5 * (attempt + 1))
        else:
            # Last attempt failed
            logger.warning(f"{ticker}: All 3 attempts failed - {type(last_exc).__name__}: {last_exc}")
            raise last_exc

        # Ensure title-cased columns Close/High/Low/Volume for downstream code
        if hist is None or hist.empty:
            logger.warning(f"{ticker}: yfinance returned empty/None (no data available)")
            return pd.DataFrame()
        logger.debug(f"{ticker}: Got {len(hist)} rows from yfinance")
        return hist.rename(columns=str.title)
    except Exception as e:
        # As a fallback, try the simple period-based call with integer years
        logger.debug(f"{ticker}: Primary fetch failed ({type(e).__name__}), trying fallback...")
        try:
            yrs = int(float(years))
            hist = yf.Ticker(ticker).history(period=f"{yrs}y", interval="1d", auto_adjust=True)
            if hist is None or hist.empty:
                logger.warning(f"{ticker}: Fallback also returned empty data")
                return pd.DataFrame()
            return hist.rename(columns=str.title)
        except Exception as fallback_e:
            logger.warning(f"{ticker}: Both primary and fallback failed - {type(fallback_e).__name__}: {fallback_e}")
            return pd.DataFrame()