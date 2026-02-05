from typing import Dict, List
import datetime as dt
import numpy as np
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys
from equity_engine import data_sources
from .config import Settings, load_settings
from .data_sources import get_nse_index_constituents, to_yahoo, fetch_history_yf
from .indicators import add_technicals, compute_returns, compute_cagr, risk_stats
from .scoring import compute_subscores, overall_score
from .logger import logger
from .weekly_analysis import build_weekly_analysis_sheet
from .monthly_analysis import build_monthly_analysis_sheet, build_seasonality_sheet
import logging
import re


def build_universe(indexes: List[str]) -> pd.DataFrame:
    all_rows: List[pd.DataFrame] = []
    for idx in indexes:
        logging.info("Loading constituents for %s", idx)
        df = data_sources.get_nse_index_constituents(idx)

        try:
            merged = data_sources.merge_constituents_with_metadata(df, yahoo_suffix=".NS")
            logging.info("Merged metadata for %s (%d rows)", idx, len(merged))

            sample_path = f"debug_merge_sample_{idx.replace(' ', '_')}.csv"
            merged.head(200).to_csv(sample_path, index=False, encoding="utf-8")
            logging.info("Wrote sample CSV: %s", sample_path)
        except Exception as exc:
            logging.warning("Failed to merge metadata for %s: %s. Proceeding with raw constituents.", idx, exc)
            merged = df

        all_rows.append(merged)

    if not all_rows:
        raise RuntimeError("No constituents found for requested indexes.")
    return pd.concat(all_rows, ignore_index=True)


def _extract_isin(meta_value: str) -> str:
    if isinstance(meta_value, dict):
        val = meta_value.get("isin") or meta_value.get("ISIN")
        return str(val) if val else ""
    if not isinstance(meta_value, str):
        return ""
    m = re.search(r"'isin'\s*:\s*'([^']+)'", meta_value)
    if m:
        return m.group(1)
    m2 = re.search(r'"isin"\s*:\s*"([^"]+)"', meta_value)
    if m2:
        return m2.group(1)
    return ""



def _pick_series(df: pd.DataFrame, names: List[str], default=np.nan) -> pd.Series:
    result = None
    for name in names:
        if name in df.columns:
            series = df[name]
            if hasattr(series, "replace"):
                series = series.replace({"": np.nan})
            result = series if result is None else result.combine_first(series)
    if result is None:
        return pd.Series(default, index=df.index)
    return result.fillna(default)


def prepare_output_df(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)

    # Derive template-friendly ticker symbol
    out["Ticker"] = df.get("symbol", df.get("Ticker", "")).astype(str).str.strip().str.replace(r"\.NS$", "", regex=True)
    out["Company Name"] = df.get("Company Name", df.get("companyName", df.get("longName", ""))).fillna("").astype(str)

    # Pull metadata columns with sensible fallbacks
    isin_series = _pick_series(df, ["ISIN", "isin"], default="")
    if isin_series.eq("").all():
        isin_series = df.get("meta", "").apply(_extract_isin)
    out["ISIN"] = isin_series
    out["Exchange"] = _pick_series(df, ["Exchange", "exchange", "Exchange_meta", "exchange_meta"], default="NSI")
    out["Sector"] = _pick_series(df, ["Sector", "sector", "Sector_meta", "sector_meta"], default="")
    out["Industry"] = _pick_series(df, ["Industry", "industry", "Industry_meta", "industry_meta"], default="")
    out["Currency"] = _pick_series(df, ["Currency", "currency", "Currency_meta", "currency_meta"], default="INR")

    # Numbers already harmonised in calculate_additional_metrics
    for col in [
        "Market Cap (INR Cr)", "Enterprise Value (INR Cr)", "Revenue TTM (INR Cr)",
        "EBITDA TTM (INR Cr)", "Net Income TTM (INR Cr)", "OCF TTM (INR Cr)",
        "CapEx TTM (INR Cr)", "FCF TTM (INR Cr)", "Free Float %", "Shares Outstanding",
        "Avg Daily Turnover 3M (INR Cr)", "Avg Volume 1W", "Volume vs 3M Avg %",
        "P/E (TTM)", "P/B", "P/S Ratio", "EV/EBITDA (TTM)", "Dividend Yield %",
        "EPS TTM", "ROE TTM %", "ROA %", "Debt/Equity", "Interest Coverage",
        "EPS Growth YoY %", "Revenue Growth YoY %", "Gross Profit Margin %",
        "Operating Profit Margin %", "Net Profit Margin %", "FCF Yield %", "PEG Ratio",
        "Beta 1Y"
    ]:
        out[col] = _pick_series(df, [col, f"{col}_meta"], default=np.nan)

    # Technical indicators
    for indicator in [
        "SMA20", "SMA50", "SMA200", "RSI14", "MACD Line", "MACD Signal",
        "MACD Hist", "ATR14", "BB Upper", "BB Lower", "OBV", "ADL",
        "ADX14", "Aroon Up", "Aroon Down", "Stoch %K", "Stoch %D"
    ]:
        out[indicator] = _pick_series(df, [indicator, f"{indicator}_meta"], default=np.nan)

    # Price levels
    for col in ["Price (Last)", "52W High", "52W Low"]:
        alt = []
        if col == "Price (Last)":
            alt = ["lastPrice", "close", "currentPrice"]
        elif col == "52W High":
            alt = ["fiftyTwoWeekHigh"]
        elif col == "52W Low":
            alt = ["fiftyTwoWeekLow"]
        out[col] = _pick_series(df, [col, f"{col}_meta", *alt], default=np.nan)

    # Returns
    return_candidates = {
        "Return 1D %": ["Return 1D %", "Return 1d %"],
        "Return 1W %": ["Return 1W %", "Return 5d %"],
        "Return 1M %": ["Return 1M %", "Return 21d %"],
        "Return 3M %": ["Return 3M %", "Return 63d %"],
        "Return 6M %": ["Return 6M %", "Return 126d %"],
        "Return 1Y %": ["Return 1Y %", "Return 252d %"],
    }
    for col, names in return_candidates.items():
        alts: List[str] = []
        for name in names:
            alts.append(name)
            alts.append(f"{name}_meta")
        out[col] = _pick_series(df, alts, default=np.nan)

    # CAGR and scores
    out["CAGR 3Y %"] = _pick_series(df, ["CAGR 3Y %", "CAGR 3Y %_meta"], default=np.nan)
    out["CAGR 5Y %"] = _pick_series(df, ["CAGR 5Y %", "CAGR 5Y %_meta"], default=np.nan)
    for col in [
        "Score Fundamental (0-100)", "Score Technical (0-100)", "Score Sentiment (0-100)",
        "Score Macro (0-100)", "Score Risk (0-100)", "Overall Score (0-100)", "Macro Composite (0-100)"
    ]:
        out[col] = _pick_series(df, [col, f"{col}_meta"], default=np.nan)

    # Qualitative placeholders (still blank until filled by other modules)
    for col in [
        "Consensus Rating (1-5)", "Target Price", "Upside %", "# Analysts",
        "Recommendation", "Moat Notes", "Risk Notes", "Catalysts", "ESG Score",
        "Sector Leader Ticker", "Leader Gap on Metric", "Sector Tailwinds/Headwinds",
        "Sector P/E (Median)", "Economic Moat Score", "Altman Z-Score", "Piotroski F-Score",
        "Alpha 1Y %", "Sortino 1Y", "Sector Relative Strength 6M %", "Quality Score",
        "Momentum Score", "News Sentiment Score", "Social Media Sentiment"
    ]:
        if col not in out.columns:
            out[col] = _pick_series(df, [col, f"{col}_meta"], default=np.nan)

    out["As Of Datetime"] = _pick_series(df, ["As Of Datetime"], default="")
    out["Sources"] = _pick_series(df, ["Sources"], default="")
    out["Data Quality Score"] = _pick_series(df, ["Data Quality Score"], default=np.nan)

    # Debug info retained
    out["_debug_yahoo"] = df.get("yahoo", "")
    out["_debug_meta"] = df.get("meta", "")

    return out.fillna("")

def enrich_stock(symbol: str, settings: Settings) -> Dict[str, float]:
    logger = logging.getLogger(__name__)
    ticker = to_yahoo(symbol, settings.yahoo_suffix)
    h = fetch_history_yf(ticker, years=settings.history_years)
    if h.empty:
        logger.warning(f"{symbol} ({ticker}): No historical data returned from yfinance")
        return {}
    if "Close" not in h.columns:
        logger.warning(f"{symbol} ({ticker}): Data returned but missing 'Close' column. Columns: {list(h.columns)}")
        return {}

    h = add_technicals(h, sma_windows=settings.sma_windows, rsi_window=settings.rsi_window, macd=settings.macd)
    # If some technicals like Bollinger Bands are missing from pandas_ta outputs,
    # compute a safe fallback using our internal canonical implementation.
    try:
        import equity_engine.technical as technical_module
        # compute canonical technicals (this uses rolling/window fallbacks)
        canonical = technical_module.compute_technicals(h)
        # copy missing keys from canonical into h's last row view for downstream extraction
        # We'll not modify the entire frame; just ensure the last row has these labels for later extraction
        last_idx = h.index[-1]
        for k, v in canonical.items():
            colname = k
            # only set if missing in the frame or NaN
            if colname not in h.columns or pd.isna(h.at[last_idx, colname]):
                try:
                    # create column if needed
                    if colname not in h.columns:
                        h[colname] = pd.NA
                    h.at[last_idx, colname] = v
                except Exception:
                    pass
    except Exception:
        # fallback: continue without canonical injection
        pass
    rets = compute_returns(h["Close"], settings.return_windows)
    cagr3 = compute_cagr(h["Close"], 3)
    cagr5 = compute_cagr(h["Close"], 5)
    risk = risk_stats(h["Close"], rf_annual_pct=settings.rf_annual_pct, lookback=252)

    last = h.iloc[-1]
    row = {
        "Ticker": ticker, "Exchange": "NSE", "Price (Last)": float(last["Close"]),
        "52W High": float(h["Close"].tail(252).max()), "52W Low": float(h["Close"].tail(252).min()),
        "RSI14": float(last.get("RSI14", np.nan)) if pd.notna(last.get("RSI14", np.nan)) else np.nan,
        "SMA20": float(last.get("SMA20", np.nan)) if pd.notna(last.get("SMA20", np.nan)) else np.nan,
        "SMA50": float(last.get("SMA50", np.nan)) if pd.notna(last.get("SMA50", np.nan)) else np.nan,
        "SMA200": float(last.get("SMA200", np.nan)) if pd.notna(last.get("SMA200", np.nan)) else np.nan,
        "MACD Line": float(last.get("MACD Line", np.nan)) if pd.notna(last.get("MACD Line", np.nan)) else np.nan,
        "MACD Signal": float(last.get("MACD Signal", np.nan)) if pd.notna(last.get("MACD Signal", np.nan)) else np.nan,
        "MACD Hist": float(last.get("MACD Hist", np.nan)) if pd.notna(last.get("MACD Hist", np.nan)) else np.nan,
        "ATR14": float(last.get("ATR14", np.nan)) if pd.notna(last.get("ATR14", np.nan)) else np.nan,
        "BB Upper": float(last.get("BB Upper", np.nan)) if pd.notna(last.get("BB Upper", np.nan)) else np.nan,
        "BB Lower": float(last.get("BB Lower", np.nan)) if pd.notna(last.get("BB Lower", np.nan)) else np.nan,
        "OBV": float(last.get("OBV", np.nan)) if pd.notna(last.get("OBV", np.nan)) else np.nan,
        "ADL": float(last.get("ADL", np.nan)) if pd.notna(last.get("ADL", np.nan)) else np.nan,
        "ADX14": float(last.get("ADX14", np.nan)) if pd.notna(last.get("ADX14", np.nan)) else np.nan,
        "Aroon Up": float(last.get("Aroon Up", np.nan)) if pd.notna(last.get("Aroon Up", np.nan)) else np.nan,
        "Aroon Down": float(last.get("Aroon Down", np.nan)) if pd.notna(last.get("Aroon Down", np.nan)) else np.nan,
        "Stoch %K": float(last.get("Stoch %K", np.nan)) if pd.notna(last.get("Stoch %K", np.nan)) else np.nan,
        "Stoch %D": float(last.get("Stoch %D", np.nan)) if pd.notna(last.get("Stoch %D", np.nan)) else np.nan,
        "As Of Datetime": dt.datetime.now().isoformat(timespec="seconds"), "Sources": "NSE index API, Yahoo Finance",
        "Data Quality Score": 1.0,
    }
    row.update(rets)
    row["CAGR 3Y %"] = float(cagr3*100) if cagr3==cagr3 else np.nan
    row["CAGR 5Y %"] = float(cagr5*100) if cagr5==cagr5 else np.nan
    row.update(risk)
    # Compute canonical metrics that may not be present in vendor metadata
    try:
        from .normalizers import compute_beta, compute_cagr_for_ticker, compute_alpha, compute_adl
        # Beta 1Y and 3Y
        try:
            beta1_val, beta1_info = compute_beta(symbol, index_symbol='^NSEI', years=1)
            if beta1_val == beta1_val:
                row['Beta 1Y'] = float(beta1_val)
        except Exception:
            pass
        try:
            beta3_val, beta3_info = compute_beta(symbol, index_symbol='^NSEI', years=3)
            if beta3_val == beta3_val:
                row['Beta 3Y'] = float(beta3_val)
        except Exception:
            pass

        # Alpha and A/D Line
        try:
            alpha1_val, ainfo = compute_alpha(symbol, index_symbol='^NSEI', years=1)
            if alpha1_val == alpha1_val:
                row['Alpha 1Y %'] = float(alpha1_val*100.0)
        except Exception:
            pass
        try:
            adl_val, adlinfo = compute_adl(symbol, years=2)
            if adl_val == adl_val:
                row['A/D Line'] = float(adl_val)
        except Exception:
            pass
    except Exception:
        # Keep enrichment robust: don't fail the whole stock on metric computation
        pass
    return row

def macro_composite_from_sheet(macro_df: pd.DataFrame) -> float:
    if "Parameter" in macro_df.columns and "Value" in macro_df.columns:
        mask = macro_df["Parameter"].str.lower().eq("macro composite (0-100)")
        if mask.any():
            try: return float(macro_df.loc[mask, "Value"].iloc[0])
            except Exception: pass
        try:
            pmi_rows = macro_df["Parameter"].str.contains("pmi", case=False, na=False)
            vix_rows = macro_df["Parameter"].str.contains("vix", case=False, na=False)
            pmi = float(macro_df.loc[pmi_rows, "Value"].iloc[-1]) if pmi_rows.any() else None
            vix = float(macro_df.loc[vix_rows, "Value"].iloc[-1]) if vix_rows.any() else None
            score = 50.0
            if pmi is not None: score += (pmi - 50.0) * 2.0
            if vix is not None: score += (20.0 - min(max(vix,10.0),30.0)) * 0.5
            return float(max(0.0, min(100.0, score)))
        except Exception: pass
    return 50.0


def run_pipeline(template_path: str, out_path: str) -> None:
    settings = load_settings()
    logger.info("Starting Equity Engine pipeline...")
    logger.info(f"Loading universe for indexes: {settings.indexes}")
    uni = build_universe(settings.indexes)

    rows = []
    batch_size = 20
    delay_between_batches = 2  # seconds
    logger.info(f"Processing {len(uni)} stocks in batches of {batch_size} with {delay_between_batches}s delays...")
    
    uni_list = list(uni.iterrows())
    for i in range(0, len(uni_list), batch_size):
        batch = uni_list[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(uni_list) + batch_size - 1)//batch_size} ({len(batch)} stocks)...")
        
        with ThreadPoolExecutor(max_workers=min(settings.max_workers, len(batch))) as executor:
            futures = {executor.submit(enrich_stock, row["symbol"], settings): row for _, row in batch}
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"Batch {i//batch_size + 1}"):
                original_row = futures[future]
                try:
                    res = future.result()
                    if res:
                        res["Company Name"] = original_row.get("companyName", "")
                        res["Index"] = original_row.get("index_name", "")
                        rows.append(res)
                except Exception as e:
                    logger.error(f"Error processing {original_row['symbol']}: {e}")
        
        # Add delay between batches (except for the last batch)
        if i + batch_size < len(uni_list):
            logger.info(f"Waiting {delay_between_batches}s before next batch...")
            import time
            time.sleep(delay_between_batches)
    
    if not rows:
        logger.error("No stock data could be processed. Exiting.")
        return
        
    stocks = pd.DataFrame(rows)
    logger.info(f"Successfully processed data for {len(stocks)} stocks.")

    try:
        readme = pd.read_excel(template_path, sheet_name="README")
        params = pd.read_excel(template_path, sheet_name="Parameters")
    except Exception:
        readme, params = pd.DataFrame(), pd.DataFrame()

    macro_score = 50.0
    try:
        macro_sheet = pd.read_excel(template_path, sheet_name="Macro_Sentiment")
        macro_score = macro_composite_from_sheet(macro_sheet)
    except Exception:
        macro_sheet = None
    stocks["Macro Composite (0-100)"] = macro_score
    logger.info(f"Applying Macro Composite score: {macro_score:.2f}")

    try:
        pd.read_excel(template_path, sheet_name="NIFTY50", nrows=0)
    except Exception:
        logger.warning("Could not find 'NIFTY50' sheet in template. Output columns may not match.")

    # Merge enriched technicals (stocks) with the universe metadata (uni)
    final_out_path = out_path
    if out_path == "Stocks_Analysis_Populated.xlsx":
        now = dt.datetime.now()
        folder_name = now.strftime("%b%y").upper()
        file_name = f"Stock_Analysis_{now.strftime('%d%m%y_%H%M')}.xlsx"
        os.makedirs(folder_name, exist_ok=True)
        final_out_path = os.path.join(folder_name, file_name)

    # Merge enriched technicals (stocks) with the universe metadata (uni)
    stocks["symbol"] = stocks["Ticker"].astype(str).str.replace(r"\.NS$", "", regex=True)
    meta_subset = uni.drop_duplicates(subset=["symbol"]).copy()
    merged_final = stocks.merge(meta_subset, on="symbol", how="left", suffixes=("", "_meta"))

    logger.info("Computing sub-scores and overall scores...")
    subs = compute_subscores(merged_final)
    merged_final = pd.concat([merged_final, subs], axis=1)
    merged_final["Overall Score (0-100)"] = overall_score(subs, settings.weights).clip(0, 100)

    logger.info("merged_final rows = %d", len(merged_final))
    logger.debug("merged_final sample:\n%s", merged_final.head(10).to_dict(orient="records"))

    # Create the prepared output (keeps column names that match template-friendly names)
    output_df = prepare_output_df(merged_final)
    debug_dir = os.path.dirname(final_out_path) or "."
    try:
        merged_final.to_csv(os.path.join(debug_dir, "_debug_merged_final.csv"), index=False)
        output_df.to_csv(os.path.join(debug_dir, "_debug_output_df.csv"), index=False)
    except Exception as debug_exc:
        logger.debug("Failed to write debug CSVs: %s", debug_exc)
    logger.info("output_df rows = %d", len(output_df))
    logger.debug("output_df sample:\n%s", output_df.head(10).to_dict(orient="records"))

    logger.info("Preparing template-preserved output...")

    # Read template sheets to preserve formatting/sheets
    with pd.ExcelFile(template_path) as xls:
        all_sheets = {name: xls.parse(name, dtype=str) for name in xls.sheet_names}

    sheet_name = "NIFTY50"   # ensure this matches your template
    template_df = all_sheets.get(sheet_name)
    if template_df is None:
        logger.warning("Template sheet '%s' not found; writing prepared output as new sheet.", sheet_name)
        all_sheets[sheet_name] = output_df
    else:
        # Normalize matching keys (no .NS, uppercase)
            # Create normalized columns efficiently using a copy
        template_df = template_df.copy()
        output_df = output_df.copy()
        merged_final = merged_final.copy()
        
        template_df["Ticker_norm"] = template_df.get("Ticker", "").astype(str).str.strip().str.replace(r"\.NS$", "", regex=True).str.upper()
        output_df["Ticker_norm"] = output_df.get("Ticker", "").astype(str).str.strip().str.replace(r"\.NS$", "", regex=True).str.upper()
        merged_final["Ticker_norm"] = merged_final.get("symbol", merged_final.get("Ticker", "")).astype(str).str.strip().str.replace(r"\.NS$", "", regex=True).str.upper()

        # lookups keyed by Ticker_norm
        out_lookup = output_df.set_index("Ticker_norm").to_dict(orient="index")
        merged_lookup = merged_final.set_index("Ticker_norm").to_dict(orient="index")

        # Full mapping table: template header -> list of candidate source columns (first available used)
        # Add or reorder candidates to prefer the column you have in merged_final/output_df
        column_candidates = {
            "Ticker": ["Ticker", "symbol", "yahoo"],
            "Company Name": ["Company Name", "companyName", "longBusinessSummary", "longName", "longName_meta"],
            "ISIN": ["ISIN", "isin", "meta", "meta_isin"],

            "Exchange": ["Exchange", "exchange"],
            "Sector": ["Sector", "sector"],
            "Industry": ["Industry", "industry"],
            "Market Cap (INR Cr)": ["Market Cap (INR Cr)", "marketCap_in_cr", "marketCap", "marketCap_meta"],
            "Free Float %": ["Free Float %", "freeFloatPct", "freeFloatPercent"],
            "Shares Outstanding": ["Shares Outstanding", "sharesOutstanding", "shares_outstanding"],

            "Avg Daily Turnover 3M (INR Cr)": ["Avg Daily Turnover 3M (INR Cr)", "avgDailyTurnover3M", "totalTradedValue", "totalTradedValue_meta"],
            "Price (Last)": ["Price (Last)", "lastPrice", "Price", "close"],
            "Currency": ["Currency", "currency"],
            "52W High": ["52W High", "yearHigh"],
            "52W Low": ["52W Low", "yearLow"],

            "Return 1D %": ["Return 1D %", "return_1d", "ret_1d"],
            "Return 1W %": ["Return 1W %", "return_1w", "ret_1w"],
            "Return 1M %": ["Return 1M %", "return_1m", "ret_1m"],
            "Return 3M %": ["Return 3M %", "return_3m", "ret_3m"],
            "Return 6M %": ["Return 6M %", "return_6m", "ret_6m"],
            "Return 1Y %": ["Return 1Y %", "return_1y", "ret_1y"],

            "CAGR 3Y %": ["CAGR 3Y %", "cagr_3y"],
            "CAGR 5Y %": ["CAGR 5Y %", "cagr_5y"],
            "Beta 1Y": ["Beta 1Y", "beta_1y", "beta"],
            "Beta 3Y": ["Beta 3Y", "beta_3y"],

            "P/E (TTM)": ["P/E (TTM)", "pe", "pe_ttm", "trailingPE"],
            "P/B": ["P/B", "pb", "priceToBook"],
            "EV/EBITDA (TTM)": ["EV/EBITDA (TTM)", "evToEbitda", "ev_ebitda"],

            "Dividend Yield %": ["Dividend Yield %", "dividendYield", "dividend_yield"],
            "Revenue TTM (INR Cr)": ["Revenue TTM (INR Cr)", "revenueTTM", "revenue_ttm", "totalRevenue"],
            "EBITDA TTM (INR Cr)": ["EBITDA TTM (INR Cr)", "ebitdaTTM", "ebitda_ttm"],
            "Net Income TTM (INR Cr)": ["Net Income TTM (INR Cr)", "netIncomeTTM", "netIncome_ttm"],

            "EPS TTM": ["EPS TTM", "eps", "trailingEps"],
            "ROE TTM %": ["ROE TTM %", "returnOnEquity"],
            "ROCE TTM %": ["ROCE TTM %", "roce"],
            "Debt/Equity": ["Debt/Equity", "debtToEquity", "debt_equity"],
            "Interest Coverage": ["Interest Coverage", "interestCoverage"],

            "OCF TTM (INR Cr)": ["OCF TTM (INR Cr)", "operatingCashflow", "ocf_ttm"],
            "CapEx TTM (INR Cr)": ["CapEx TTM (INR Cr)", "capitalExpenditures", "capex_ttm"],
            "FCF TTM (INR Cr)": ["FCF TTM (INR Cr)", "freeCashflow", "fcf_ttm"],

            # Technicals / indicators (common candidate names)
            "SMA20": ["SMA20", "sma20"],
            "SMA50": ["SMA50", "sma50"],
            "SMA200": ["SMA200", "sma200"],
            "RSI14": ["RSI14", "rsi14"],
            "MACD Line": ["MACD Line", "macd_line"],
            "MACD Signal": ["MACD Signal", "macd_signal"],
            "MACD Hist": ["MACD Hist", "macd_hist"],
            "ATR14": ["ATR14", "atr14"],
            "BB Upper": ["BB Upper", "bb_upper"],
            "BB Lower": ["BB Lower", "bb_lower"],
            "Volatility 30D %": ["Volatility 30D %", "volatility_30d"],
            "Volatility 90D %": ["Volatility 90D %", "volatility_90d"],
            "Max Drawdown 1Y %": ["Max Drawdown 1Y %", "max_drawdown_1y"],

            "Sharpe 1Y": ["Sharpe 1Y", "sharpe_1y"],
            "Downside Capture 1Y %": ["Downside Capture 1Y %", "downside_capture_1y"],

            "Consensus Rating (1-5)": ["Consensus Rating (1-5)", "consensusRating"],
            "Target Price": ["Target Price", "targetPrice"],
            "Upside %": ["Upside %", "upsidePct", "upside_percent"],
            "# Analysts": ["# Analysts", "numAnalysts"],
            "Recommendation": ["Recommendation", "recommendation"],
            "Moat Notes": ["Moat Notes", "moatNotes"],
            "Risk Notes": ["Risk Notes", "riskNotes"],
            "Catalysts": ["Catalysts", "catalysts"],

            "ESG Score": ["ESG Score", "esgScore"],
            "Sector Leader Ticker": ["Sector Leader Ticker", "sector_leader_ticker"],
            "Leader Gap on Metric": ["Leader Gap on Metric", "leader_gap"],
            "Sector Tailwinds/Headwinds": ["Sector Tailwinds/Headwinds", "sector_notes"],
            "As Of Datetime": ["As Of Datetime", "as_of_datetime", "date"],
            "Sources": ["Sources", "sources"],
            "Data Quality Score": ["Data Quality Score", "dataQualityScore"],

            # Fundamental growth / margins
            "EPS Growth YoY %": ["EPS Growth YoY %", "epsGrowthYoY", "eps_growth_yoy"],
            "Revenue Growth YoY %": ["Revenue Growth YoY %", "revenueGrowthYoY", "revenue_growth_yoy"],
            "Net Profit Margin %": ["Net Profit Margin %", "netProfitMargin", "net_profit_margin"],
            "FCF Yield %": ["FCF Yield %", "fcfYield"],
            "PEG Ratio": ["PEG Ratio", "pegRatio"],

            # Ratios / margins
            "Sector P/E (Median)": ["Sector P/E (Median)", "sector_pe_median"],
            "P/S Ratio": ["P/S Ratio", "ps"],
            "Gross Profit Margin %": ["Gross Profit Margin %", "grossProfitMargin"],
            "Operating Profit Margin %": ["Operating Profit Margin %", "operatingProfitMargin"],
            "ROA %": ["ROA %", "roa"],
            "Current Ratio": ["Current Ratio", "currentRatio"],
            "Quick Ratio": ["Quick Ratio", "quickRatio"],
            "Asset Turnover": ["Asset Turnover", "assetTurnover"],
            "Inventory Turnover": ["Inventory Turnover", "inventoryTurnover"],
            "Receivables Turnover": ["Receivables Turnover", "receivablesTurnover"],

            "Economic Moat Score": ["Economic Moat Score", "economicMoatScore"],
            "Avg Volume 1W": ["Avg Volume 1W", "avgVolume1W", "avg_volume_1w"],
            "Volume vs 3M Avg %": ["Volume vs 3M Avg %", "volume_vs_3m_avg_pct"],
            "OBV": ["OBV", "obv"],
            "A/D Line": ["A/D Line", "ad_line"],
            "ADX14": ["ADX14", "adx14"],
            "Aroon Up": ["Aroon Up", "aroon_up"],
            "Aroon Down": ["Aroon Down", "aroon_down"],
            "Stoch %K": ["Stoch %K", "stoch_k"],
            "Stoch %D": ["Stoch %D", "stoch_d"],

            "Altman Z-Score": ["Altman Z-Score", "altman_z"],
            "Piotroski F-Score": ["Piotroski F-Score", "piotroski_f"],
            "Alpha 1Y %": ["Alpha 1Y %", "alpha_1y"],
            "Sortino 1Y": ["Sortino 1Y", "sortino_1y"],
            "Sector Relative Strength 6M %": ["Sector Relative Strength 6M %","sector_rel_strength_6m"],
            "Quality Score": ["Quality Score", "quality_score"],
            "Momentum Score": ["Momentum Score", "momentum_score"],
            "News Sentiment Score": ["News Sentiment Score", "news_sentiment_score"],
            "Social Media Sentiment": ["Social Media Sentiment", "social_sentiment"],
            "Score Fundamental (0-100)": ["Score Fundamental (0-100)", "score_fundamental"],
            "Score Technical (0-100)": ["Score Technical (0-100)", "score_technical"],
            "Score Sentiment (0-100)": ["Score Sentiment (0-100)", "score_sentiment"],
            "Score Macro (0-100)": ["Score Macro (0-100)", "Score Macro", "Macro Composite (0-100)"],
            "Score Risk (0-100)": ["Score Risk (0-100)", "score_risk"],
            "Macro Composite (0-100)": ["Macro Composite (0-100)", "Macro Composite (0-100)"],
            "Overall Score (0-100)": ["Overall Score (0-100)", "Overall Score (0-100)"],
        }

        # Convert marketCap to INR Cr if numeric and add helper field
        def to_inr_cr_val(x):
            try:
                return float(x) / 1e7
            except Exception:
                return ""
        output_df["marketCap_in_cr"] = output_df.get("Market Cap (INR Cr)", output_df.get("marketCap", "")).apply(lambda x: to_inr_cr_val(x) if x not in (None, "") else "")
        # ensure 'Ticker' column exists in output_df for mapping
        if "Ticker" not in output_df.columns and "symbol" in output_df.columns:
            output_df["Ticker"] = output_df["symbol"].astype(str) + ".NS"

        # Build a merged lookup that prefers output_df then merged_final
        def get_value_for_key(info_out, info_merged, candidates):
            for c in candidates:
                # First check output_df since it has the template-formatted data
                if info_out and c in info_out and info_out[c] not in (None, "", "nan", "NaN", float("nan")):
                    val = info_out[c]
                    # Special case for Exchange field
                    if c == "Exchange" and val == "NSE":
                        return "NSI"
                    return val
                # Then check merged_final as fallback
                if info_merged and c in info_merged and info_merged[c] not in (None, "", "nan", "NaN", float("nan")):
                    val = info_merged[c]
                    # Special case for Exchange field
                    if c == "Exchange" and val == "NSE":
                        return "NSI"
                    return val
            return ""

        # Update template rows in-place using mapping candidates
        matched = 0
        total_template_rows = len(template_df)
        template_keys = set(template_df["Ticker_norm"].fillna("").astype(str).str.upper())

        for i, row in template_df.iterrows():
            key = str(row.get("Ticker_norm", "")).strip().upper()
            if not key:
                continue
            info_out = out_lookup.get(key)
            info_merged = merged_lookup.get(key)
            if not info_out and not info_merged:
                continue
            matched += 1
            for tmpl_col, candidates in column_candidates.items():
                if tmpl_col not in template_df.columns:
                    continue
                val = get_value_for_key(info_out, info_merged, candidates)
                template_df.at[i, tmpl_col] = "" if pd.isna(val) else val

        logger.info("Template rows: %d, matched rows updated: %d", total_template_rows, matched)

        # Append missing stocks (those present in output_df but not in template)
        missing_mask = ~output_df["Ticker_norm"].isin(template_keys)
        missing_rows = output_df.loc[missing_mask].copy()

        if not missing_rows.empty:
            logger.info("Appending %d missing rows to template sheet", len(missing_rows))
            # Create a new DataFrame with only required columns from output_df
            missing_rows_data = []
            for _, row in output_df.loc[missing_mask].iterrows():
                new_row = {}
                ticker = row.get("Ticker_norm", "").strip().upper()
                info_out = out_lookup.get(ticker, {})
                info_merged = merged_lookup.get(ticker, {})
                
                for tmpl_col, candidates in column_candidates.items():
                    if tmpl_col in template_df.columns:
                        val = get_value_for_key(info_out, info_merged, candidates)
                        new_row[tmpl_col] = "" if pd.isna(val) else val
                missing_rows_data.append(new_row)
            
            # Create DataFrame with properly ordered columns
            template_cols = [c for c in template_df.columns if c != "Ticker_norm"]
            missing_rows = pd.DataFrame(missing_rows_data, columns=template_cols)
            # drop helper in template before concatenation
            template_df = template_df.drop(columns=["Ticker_norm"], errors="ignore")
            template_df = pd.concat([template_df, missing_rows], ignore_index=True, sort=False)
        else:
            # Fill any remaining empty cells with data from merged_final
            for col in template_df.columns:
                if col == "Ticker_norm":
                    continue
                for candidates in [item for key, item in column_candidates.items() if key == col]:
                    for idx, row in template_df.iterrows():
                        if pd.isna(row[col]) or row[col] == "":
                            ticker = str(row.get("Ticker_norm", "")).strip().upper()
                            if ticker in merged_lookup:
                                val = get_value_for_key(None, merged_lookup[ticker], candidates)
                                template_df.at[idx, col] = "" if pd.isna(val) else val

            template_df = template_df.drop(columns=["Ticker_norm"], errors="ignore")

        # Calculate Sector P/E Median and add to template_df
        if "Sector" in template_df.columns and "P/E (TTM)" in template_df.columns:
            # Convert P/E column to numeric, filtering out non-numeric values
            pe_numeric = pd.to_numeric(template_df["P/E (TTM)"], errors="coerce")
            
            # Group by sector and calculate median P/E for numeric values only
            sector_pe_median = template_df.assign(pe_numeric=pe_numeric).groupby("Sector")["pe_numeric"].median()
            
            # Add sector median P/E to template_df
            if "Sector P/E (Median)" in template_df.columns:
                template_df["Sector P/E (Median)"] = template_df["Sector"].map(sector_pe_median)
                logger.info("Calculated Sector P/E (Median) for all stocks")
            else:
                logger.debug("Column 'Sector P/E (Median)' not found in template")
        
        # replace sheet in workbook
        all_sheets[sheet_name] = template_df

    # --- Weekly & Monthly Analysis ---
    logger.info("Building Weekly and Monthly Analysis sheets...")
    
    # Get list of symbols and company names for weekly/monthly analysis
    symbols = merged_final['symbol'].dropna().unique().tolist()
    company_names = dict(zip(
        merged_final['symbol'].fillna(''),
        merged_final.get('Company Name', merged_final.get('companyName', '')).fillna('')
    ))
    
    # Build Weekly Analysis sheet (52 weeks history)
    try:
        logger.info("Computing weekly analysis for %d stocks...", len(symbols))
        weekly_df = build_weekly_analysis_sheet(
            symbols=symbols,
            company_names=company_names,
            weeks=52,
            yahoo_suffix=settings.yahoo_suffix
        )
        if not weekly_df.empty:
            all_sheets["Weekly_Analysis"] = weekly_df
            logger.info("Weekly_Analysis sheet created with %d rows", len(weekly_df))
        else:
            logger.warning("Weekly_Analysis sheet is empty")
    except Exception as e:
        logger.error("Failed to build Weekly_Analysis sheet: %s", e)
    
    # Build Monthly Analysis sheet (24 months history)
    try:
        logger.info("Computing monthly analysis for %d stocks...", len(symbols))
        monthly_df = build_monthly_analysis_sheet(
            symbols=symbols,
            company_names=company_names,
            months=24,
            yahoo_suffix=settings.yahoo_suffix
        )
        if not monthly_df.empty:
            all_sheets["Monthly_Analysis"] = monthly_df
            logger.info("Monthly_Analysis sheet created with %d rows", len(monthly_df))
        else:
            logger.warning("Monthly_Analysis sheet is empty")
    except Exception as e:
        logger.error("Failed to build Monthly_Analysis sheet: %s", e)
    
    # Build Seasonality sheet (5 years historical averages)
    try:
        logger.info("Computing seasonality for %d stocks...", len(symbols))
        seasonality_df = build_seasonality_sheet(
            symbols=symbols,
            company_names=company_names,
            years=5,
            yahoo_suffix=settings.yahoo_suffix
        )
        if not seasonality_df.empty:
            all_sheets["Seasonality"] = seasonality_df
            logger.info("Seasonality sheet created with %d rows", len(seasonality_df))
        else:
            logger.warning("Seasonality sheet is empty")
    except Exception as e:
        logger.error("Failed to build Seasonality sheet: %s", e)

    # Ensure output folder exists and write workbook (preserve other sheets)
    out_folder = os.path.dirname(final_out_path) or "."
    os.makedirs(out_folder, exist_ok=True)
    with pd.ExcelWriter(final_out_path, engine="openpyxl") as writer:
        for name, df_sheet in all_sheets.items():
            df_sheet.to_excel(writer, sheet_name=name, index=False)

    # Preserve conditional formatting from template to output file by re-running the formatter
    try:
        import subprocess
        
        # Get the path to apply_conditional_formatting.py script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        formatter_script = os.path.join(os.path.dirname(script_dir), "apply_conditional_formatting.py")
        rules_csv = os.path.join(os.path.dirname(script_dir), "conditional_format_rules.csv")
        
        if os.path.exists(formatter_script) and os.path.exists(rules_csv):
            # Run the formatting script on the output file
            result = subprocess.run(
                [sys.executable, formatter_script, final_out_path, rules_csv],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Applied conditional formatting to output file via formatter script")
            else:
                logger.warning("Formatter script returned non-zero exit code: %s", result.stderr)
        else:
            logger.debug("Conditional formatting script not found at: %s", formatter_script)
    except Exception as e:
        logger.warning("Could not apply conditional formatting: %s", str(e))

    logger.info("Wrote merged results to %s (template preserved).", final_out_path)
    logger.info("Pipeline finished successfully.")
# --- end modified block ---


def run_pipeline_fresh(template_path: str, out_dir: str = None) -> str:
    """
    Helper to run the pipeline and produce a fresh output workbook outside OCT25.

    Args:
        template_path: path to the Excel template.
        out_dir: optional directory to place the output; if None a dated folder is created in cwd.

    Returns:
        The path to the written Excel file.
    """
    # Build a unique output filename not under OCT25
    now = dt.datetime.now()
    folder_name = now.strftime("%b%y").upper()
    file_name = f"Stock_Analysis_{now.strftime('%d%m%y_%H%M%S')}.xlsx"

    # If user provided an out_dir, use it; otherwise use the date-named folder
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        final_out = os.path.join(out_dir, file_name)
    else:
        os.makedirs(folder_name, exist_ok=True)
        final_out = os.path.join(folder_name, file_name)

    # Call existing pipeline to do the heavy lifting
    run_pipeline(template_path, final_out)
    return final_out