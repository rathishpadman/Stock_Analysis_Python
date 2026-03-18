"""
Fundamentals Adapter Layer

Provides a unified interface for fetching stock fundamental data from
multiple sources. Each adapter maps source-specific fields to a common schema.

Cascade order (configurable):
1. Supabase  — fastest, no rate limits, pre-computed scores
2. nsepython — direct NSE API, PE/price/industry, no Yahoo dependency
3. yfinance  — richest data (margins, debt, dividends), but rate-limited
4. Finnhub   — optional, requires API key, good global coverage

Usage:
    from nifty_agents.tools.fundamentals_adapter import get_fundamentals
    data = get_fundamentals("COALINDIA")
"""

import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


# =============================================================================
# Standard Schema — all adapters map to these keys
# =============================================================================

STANDARD_FIELDS = {
    # Identity
    "ticker", "company_name", "sector", "industry",
    # Valuation
    "market_cap", "enterprise_value", "pe_ratio", "forward_pe",
    "pb_ratio", "ps_ratio", "peg_ratio", "ev_ebitda",
    # Profitability
    "roe", "roa", "gross_margin", "operating_margin", "profit_margin",
    # Financial Health
    "debt_to_equity", "current_ratio", "quick_ratio",
    # Dividends
    "dividend_yield", "dividend_rate", "payout_ratio",
    # Price
    "current_price", "previous_close", "52w_high", "52w_low",
    "50d_avg", "200d_avg",
    # Volume
    "avg_volume", "avg_volume_10d",
    # Other
    "beta", "shares_outstanding", "float_shares", "face_value",
    # Shareholding
    "promoter_holding_pct", "public_holding_pct",
    # Market-level FII/DII flows (from nse_fiidii)
    "fii_net_value_cr", "dii_net_value_cr",
    # Support & Resistance (pivot points)
    "pivot_point", "support_1", "support_2", "support_3",
    "resistance_1", "resistance_2", "resistance_3",
    # Scores (bonus, from pre-computed pipelines)
    "fundamental_score", "technical_score", "quality_score", "overall_score",
    # Metadata
    "data_source", "timestamp",
}


# =============================================================================
# Abstract Adapter
# =============================================================================

class FundamentalsAdapter(ABC):
    """Base class for all fundamentals data adapters."""

    name: str = "base"

    @abstractmethod
    def fetch(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch fundamentals for the given NSE ticker.

        Returns:
            Dict with standard schema keys, or None if unavailable.
            Must include 'data_source' and 'timestamp' fields.
        """
        ...

    def _base_result(self, ticker: str) -> Dict[str, Any]:
        """Return a template dict with ticker and metadata pre-filled."""
        return {
            "ticker": ticker,
            "data_source": self.name,
            "timestamp": datetime.now().isoformat(),
        }


# =============================================================================
# 1. Supabase Adapter (primary — fast, no rate limits)
# =============================================================================

class SupabaseAdapter(FundamentalsAdapter):
    name = "supabase"

    def fetch(self, ticker: str) -> Optional[Dict[str, Any]]:
        try:
            from .supabase_fetcher import get_daily_stock_data

            daily = get_daily_stock_data(ticker, limit=1)
            if "error" in daily or not daily.get("data"):
                return None

            d = daily["data"]
            result = self._base_result(ticker)
            result.update({
                "company_name": d.get("company_name", ticker),
                "sector": d.get("sector", "Unknown"),
                "industry": d.get("industry", "Unknown"),

                # Valuation
                "market_cap": d.get("market_cap_cr") or d.get("market_cap"),
                "enterprise_value": d.get("enterprise_value_cr"),
                "pe_ratio": d.get("pe_ttm"),
                "forward_pe": d.get("forward_pe"),
                "pb_ratio": d.get("pb"),
                "ps_ratio": d.get("ps_ratio"),
                "peg_ratio": d.get("peg_ratio"),
                "ev_ebitda": d.get("ev_ebitda_ttm"),

                # Profitability
                "roe": d.get("roe_ttm"),
                "roa": d.get("roa_pct"),
                "gross_margin": d.get("gross_profit_margin_pct"),
                "operating_margin": d.get("operating_profit_margin_pct"),
                "profit_margin": d.get("net_profit_margin_pct"),

                # Financial Health
                "debt_to_equity": d.get("debt_equity"),
                "current_ratio": d.get("current_ratio"),
                "interest_coverage": d.get("interest_coverage"),

                # Dividends
                # Dividend yield: Supabase stores in basis points (478 = 4.78%)
                # Normalize to percentage if > 20 (no stock has 20%+ div yield)
                "dividend_yield": (
                    d.get("dividend_yield_pct") / 100
                    if d.get("dividend_yield_pct") and d.get("dividend_yield_pct") > 20
                    else d.get("dividend_yield_pct")
                ),

                # Growth
                "eps_growth_yoy": d.get("eps_growth_yoy_pct"),
                "revenue_growth_yoy": d.get("revenue_growth_yoy_pct"),

                # Price
                "current_price": d.get("price_last"),
                "previous_close": d.get("prev_close"),
                "52w_high": d.get("high_52w"),
                "52w_low": d.get("low_52w"),
                "50d_avg": d.get("sma50"),
                "200d_avg": d.get("sma200"),

                # Volume
                "avg_volume": d.get("avg_volume_1w"),

                # Other
                "beta": d.get("beta_1y"),
                "shares_outstanding": d.get("shares_outstanding"),
                "eps_ttm": d.get("eps_ttm"),

                # Revenue/Earnings (TTM)
                "revenue_ttm": d.get("revenue_ttm_cr"),
                "ebitda_ttm": d.get("ebitda_ttm_cr"),
                "net_income_ttm": d.get("net_income_ttm_cr"),
                "fcf_ttm": d.get("fcf_ttm_cr"),
                "fcf_yield": d.get("fcf_yield_pct"),

                # Quality Metrics
                "altman_z": d.get("altman_z"),
                "piotroski_f": d.get("piotroski_f"),

                # Scores (unique to Supabase)
                "fundamental_score": d.get("score_fundamental"),
                "technical_score": d.get("score_technical"),
                "quality_score": d.get("quality_score"),
                "overall_score": d.get("overall_score"),
            })

            # Only valid if we got at least price or PE
            if result.get("current_price") or result.get("pe_ratio"):
                logger.info(f"[{self.name}] Fetched fundamentals for {ticker}")
                return result
            return None

        except Exception as e:
            logger.debug(f"[{self.name}] Failed for {ticker}: {e}")
            return None


# =============================================================================
# 2. NSEPython Adapter (secondary — direct from NSE, no Yahoo)
# =============================================================================

class NSEPythonAdapter(FundamentalsAdapter):
    name = "nsepython"

    def fetch(self, ticker: str) -> Optional[Dict[str, Any]]:
        try:
            from nsepython import nse_eq
        except ImportError:
            logger.debug(f"[{self.name}] nsepython not installed")
            return None

        try:
            data = nse_eq(ticker)
            if not data or not isinstance(data, dict):
                return None

            metadata = data.get("metadata", {})
            price_info = data.get("priceInfo", {})
            security_info = data.get("securityInfo", {})
            industry_info = data.get("industryInfo", {})
            week_hl = price_info.get("weekHighLow", {})

            # Calculate market cap from face value, issued shares, and price
            issued_size = security_info.get("issuedSize")
            last_price = price_info.get("lastPrice")
            face_value = security_info.get("faceValue")
            market_cap = None
            if issued_size and last_price:
                market_cap = issued_size * last_price

            result = self._base_result(ticker)
            result.update({
                "company_name": metadata.get("companyName", ticker),
                "sector": industry_info.get("macro", "Unknown") if isinstance(industry_info, dict) else "Unknown",
                "industry": metadata.get("industry", "Unknown"),

                # Valuation
                "market_cap": market_cap,
                "pe_ratio": metadata.get("pdSymbolPe"),

                # Price
                "current_price": last_price,
                "previous_close": price_info.get("previousClose"),
                "52w_high": week_hl.get("max"),
                "52w_low": week_hl.get("min"),

                # Other
                "face_value": face_value,
                "shares_outstanding": issued_size,
            })

            # Enrich with financial results (margins, debt, revenue growth)
            self._enrich_from_results(ticker, result)

            # Enrich with shareholding pattern (promoter/public %)
            self._enrich_shareholding(ticker, result)

            # Enrich with pivot points (support & resistance)
            self._enrich_pivot_points(data, result)

            if result.get("current_price"):
                logger.info(f"[{self.name}] Fetched fundamentals for {ticker}")
                return result
            return None

        except Exception as e:
            logger.debug(f"[{self.name}] Failed for {ticker}: {e}")
            return None

    def _enrich_from_results(self, ticker: str, result: Dict[str, Any]) -> None:
        """Enrich result with financial statement data from nse_past_results()."""
        try:
            from nsepython import nse_past_results
            data = nse_past_results(ticker)
            if not data or not isinstance(data, dict):
                return

            results_list = data.get("resCmpData", [])
            if not results_list:
                return

            latest = results_list[0]

            # Revenue and profit
            revenue = self._to_float(latest.get("re_net_sale"))
            net_profit = self._to_float(latest.get("re_net_profit"))
            pbt = self._to_float(latest.get("re_pro_loss_bef_tax"))

            # Sanity check: skip margin calcs if data looks inconsistent
            # (e.g., net profit >> revenue due to unit mismatch or other income)
            data_sane = (
                revenue and revenue > 0
                and net_profit is not None
                and abs(net_profit) <= revenue * 5  # net profit shouldn't exceed 5x revenue
            )

            # Profit margin (only if data is sane)
            if data_sane:
                margin = round(net_profit / revenue, 4)
                if -1.0 <= margin <= 1.0:  # margin should be between -100% and 100%
                    result.setdefault("profit_margin", margin)

            # Operating margin estimate (PBT + other income adjustments)
            other_income = self._to_float(latest.get("re_oth_inc_new")) or 0
            if data_sane and pbt is not None:
                operating_profit = pbt - other_income
                op_margin = round(operating_profit / revenue, 4)
                if -1.0 <= op_margin <= 1.0:
                    result.setdefault("operating_margin", op_margin)

            # Debt to equity (directly available)
            de_ratio = self._to_float(latest.get("re_debt_eqt_rat"))
            if de_ratio is not None:
                result.setdefault("debt_to_equity", de_ratio)

            # Revenue growth YoY (compare latest vs previous period)
            if len(results_list) > 1:
                prev_revenue = self._to_float(results_list[1].get("re_net_sale"))
                if revenue and prev_revenue and prev_revenue > 0:
                    growth = round((revenue - prev_revenue) / prev_revenue * 100, 2)
                    result.setdefault("revenue_growth_yoy", growth)

            # Interest coverage = EBIT / Interest expense
            interest_exp = self._to_float(latest.get("re_int_expd")) or 0
            if interest_exp and interest_exp > 0 and pbt is not None:
                ebit = pbt + interest_exp
                ic = round(ebit / interest_exp, 2)
                if 0 < ic < 1000:  # sanity: IC shouldn't be astronomical
                    result.setdefault("interest_coverage", ic)

            # ROE = Net Profit / Shareholder Equity (if equity data available)
            equity = self._to_float(latest.get("re_net_worth"))
            if equity and equity > 0 and net_profit is not None:
                roe_val = round(net_profit / equity, 4)
                if -2.0 <= roe_val <= 2.0:  # ROE between -200% and 200%
                    result.setdefault("roe", roe_val)

            # ROCE = EBIT / Capital Employed (Equity + Debt)
            total_debt = self._to_float(latest.get("re_borrow")) or 0
            if equity and equity > 0 and pbt is not None:
                ebit = pbt + (interest_exp or 0)
                capital_employed = equity + total_debt
                if capital_employed > 0:
                    roce_val = round(ebit / capital_employed, 4)
                    if -2.0 <= roce_val <= 2.0:
                        result.setdefault("roce", roce_val)

        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"[{self.name}] nse_past_results failed for {ticker}: {e}")

    def _enrich_pivot_points(self, nse_data: dict, result: Dict[str, Any]) -> None:
        """Compute standard pivot points from NSE intraday high/low/close."""
        try:
            price_info = nse_data.get("priceInfo", {})
            intraday = price_info.get("intraDayHighLow", {})

            high = intraday.get("max")
            low = intraday.get("min")
            close = price_info.get("lastPrice") or price_info.get("previousClose")

            if not all([high, low, close]):
                return

            high, low, close = float(high), float(low), float(close)
            pp = round((high + low + close) / 3, 2)

            result.setdefault("pivot_point", pp)
            result.setdefault("resistance_1", round(2 * pp - low, 2))
            result.setdefault("resistance_2", round(pp + (high - low), 2))
            result.setdefault("resistance_3", round(high + 2 * (pp - low), 2))
            result.setdefault("support_1", round(2 * pp - high, 2))
            result.setdefault("support_2", round(pp - (high - low), 2))
            result.setdefault("support_3", round(low - 2 * (high - pp), 2))

            logger.debug(
                f"[{self.name}] Pivots: PP={pp}, "
                f"S1/S2/S3={result.get('support_1')}/{result.get('support_2')}/{result.get('support_3')}, "
                f"R1/R2/R3={result.get('resistance_1')}/{result.get('resistance_2')}/{result.get('resistance_3')}"
            )
        except Exception as e:
            logger.debug(f"[{self.name}] Pivot point calc failed: {e}")

    def _enrich_shareholding(self, ticker: str, result: Dict[str, Any]) -> None:
        """Enrich with promoter/public holding % and market-level FII/DII flows."""
        try:
            from nsepython import nsefetch

            # Stock-specific: promoter & public holding %
            master = nsefetch(
                "https://www.nseindia.com/api/corporate-share-holdings-master?index=equities"
            )
            if isinstance(master, list):
                entry = next((x for x in master if x.get("symbol") == ticker), None)
                if entry:
                    promoter = self._to_float(entry.get("pr_and_prgrp"))
                    public = self._to_float(entry.get("public_val"))
                    if promoter is not None:
                        result.setdefault("promoter_holding_pct", promoter)
                    if public is not None:
                        result.setdefault("public_holding_pct", public)
                    logger.debug(
                        f"[{self.name}] Shareholding for {ticker}: "
                        f"promoter={promoter}%, public={public}%"
                    )
        except Exception as e:
            logger.debug(f"[{self.name}] Shareholding fetch failed for {ticker}: {e}")

        # Market-level: FII/DII daily net flow (via nse_fiidii)
        try:
            from nsepython import nse_fiidii

            fiidii = nse_fiidii("list")
            if isinstance(fiidii, list):
                for item in fiidii:
                    cat = (item.get("category") or "").upper()
                    net = self._to_float(item.get("netValue"))
                    if "FII" in cat or "FPI" in cat:
                        result.setdefault("fii_net_value_cr", net)
                    elif "DII" in cat:
                        result.setdefault("dii_net_value_cr", net)
        except Exception as e:
            logger.debug(f"[{self.name}] FII/DII fetch failed: {e}")

    @staticmethod
    def _to_float(val) -> Optional[float]:
        """Safely convert a value to float."""
        if val is None or val == "" or val == "-":
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None


# =============================================================================
# 3. yfinance Adapter (tertiary — richest data, but rate-limited)
# =============================================================================

class YFinanceAdapter(FundamentalsAdapter):
    name = "yfinance"

    def fetch(self, ticker: str) -> Optional[Dict[str, Any]]:
        try:
            import yfinance as yf
        except ImportError:
            logger.debug(f"[{self.name}] yfinance not installed")
            return None

        yf_ticker = f"{ticker}.NS" if not ticker.endswith(".NS") else ticker

        # Retry up to 3 times with backoff for rate limits
        last_err = None
        for attempt in range(3):
            try:
                stock = yf.Ticker(yf_ticker)
                info = stock.info

                if not info or not info.get("symbol"):
                    return None

                result = self._base_result(ticker)
                result.update({
                    "company_name": info.get("longName") or info.get("shortName", ticker),
                    "sector": info.get("sector", "Unknown"),
                    "industry": info.get("industry", "Unknown"),

                    # Valuation
                    "market_cap": info.get("marketCap"),
                    "enterprise_value": info.get("enterpriseValue"),
                    "pe_ratio": info.get("trailingPE"),
                    "forward_pe": info.get("forwardPE"),
                    "pb_ratio": info.get("priceToBook"),
                    "ps_ratio": info.get("priceToSalesTrailing12Months"),
                    "peg_ratio": info.get("pegRatio"),
                    "ev_ebitda": info.get("enterpriseToEbitda"),

                    # Profitability
                    "roe": info.get("returnOnEquity"),
                    "roa": info.get("returnOnAssets"),
                    "gross_margin": info.get("grossMargins"),
                    "operating_margin": info.get("operatingMargins"),
                    "profit_margin": info.get("profitMargins"),

                    # Financial Health
                    "debt_to_equity": info.get("debtToEquity"),
                    "current_ratio": info.get("currentRatio"),
                    "quick_ratio": info.get("quickRatio"),

                    # Dividends
                    "dividend_yield": info.get("dividendYield"),
                    "dividend_rate": info.get("dividendRate"),
                    "payout_ratio": info.get("payoutRatio"),

                    # Price
                    "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                    "previous_close": info.get("previousClose"),
                    "52w_high": info.get("fiftyTwoWeekHigh"),
                    "52w_low": info.get("fiftyTwoWeekLow"),
                    "50d_avg": info.get("fiftyDayAverage"),
                    "200d_avg": info.get("twoHundredDayAverage"),

                    # Volume
                    "avg_volume": info.get("averageVolume"),
                    "avg_volume_10d": info.get("averageVolume10days"),

                    # Other
                    "beta": info.get("beta"),
                    "shares_outstanding": info.get("sharesOutstanding"),
                    "float_shares": info.get("floatShares"),
                })

                logger.info(f"[{self.name}] Fetched fundamentals for {ticker}")
                return result

            except Exception as e:
                err_str = str(e).lower()
                if "too many requests" in err_str or "rate limit" in err_str or "429" in err_str:
                    last_err = e
                    wait = 5 * (2 ** attempt)  # 5s, 10s, 20s
                    logger.warning(f"[{self.name}] Rate limited for {ticker}, retry {attempt+1}/3 in {wait}s")
                    import time
                    time.sleep(wait)
                    continue
                else:
                    logger.debug(f"[{self.name}] Failed for {ticker}: {e}")
                    return None

        logger.warning(f"[{self.name}] All retries exhausted for {ticker}: {last_err}")
        return None


# =============================================================================
# 4. Finnhub Adapter (optional — needs FINNHUB_API_KEY env var)
# =============================================================================

class FinnhubAdapter(FundamentalsAdapter):
    name = "finnhub"

    def fetch(self, ticker: str) -> Optional[Dict[str, Any]]:
        api_key = os.environ.get("FINNHUB_API_KEY")
        if not api_key:
            return None

        try:
            import finnhub
        except ImportError:
            logger.debug(f"[{self.name}] finnhub-python not installed")
            return None

        try:
            client = finnhub.Client(api_key=api_key)
            # Finnhub uses exchange prefix for Indian stocks
            symbol = f"{ticker}.NS"

            profile = client.company_profile2(symbol=symbol)
            metrics = client.company_basic_financials(symbol, "all")

            if not profile and not metrics:
                return None

            m = metrics.get("metric", {}) if metrics else {}

            result = self._base_result(ticker)
            result.update({
                "company_name": profile.get("name", ticker),
                "sector": profile.get("finnhubIndustry", "Unknown"),
                "industry": profile.get("finnhubIndustry", "Unknown"),

                # Valuation
                "market_cap": profile.get("marketCapitalization"),
                "pe_ratio": m.get("peBasicExclExtraTTM"),
                "pb_ratio": m.get("pbQuarterly"),
                "ps_ratio": m.get("psAnnual"),

                # Profitability
                "roe": m.get("roeTTM"),
                "roa": m.get("roaTTM"),
                "gross_margin": m.get("grossMarginTTM"),
                "operating_margin": m.get("operatingMarginTTM"),
                "profit_margin": m.get("netProfitMarginTTM"),

                # Financial Health
                "debt_to_equity": m.get("totalDebt/totalEquityQuarterly"),
                "current_ratio": m.get("currentRatioQuarterly"),
                "quick_ratio": m.get("quickRatioQuarterly"),

                # Dividends
                "dividend_yield": m.get("dividendYieldIndicatedAnnual"),

                # Price
                "current_price": profile.get("marketCapitalization"),  # approx
                "52w_high": m.get("52WeekHigh"),
                "52w_low": m.get("52WeekLow"),
                "50d_avg": m.get("50DayMovingAverage"),
                "200d_avg": m.get("200DayMovingAverage"),

                # Other
                "beta": m.get("beta"),
                "shares_outstanding": profile.get("shareOutstanding"),
            })

            logger.info(f"[{self.name}] Fetched fundamentals for {ticker}")
            return result

        except Exception as e:
            logger.debug(f"[{self.name}] Failed for {ticker}: {e}")
            return None


# =============================================================================
# Adapter Registry & Cascade Logic
# =============================================================================

# Default cascade: Supabase + nsepython only.
# yfinance is excluded by default because it is permanently rate-limited on
# Render's shared IP, adding 35s of failed retries that cause analysis timeouts.
# To re-enable, set FUNDAMENTALS_SOURCES=supabase,nsepython,yfinance,finnhub
DEFAULT_ADAPTERS: List[FundamentalsAdapter] = [
    SupabaseAdapter(),
    NSEPythonAdapter(),
]

# All available adapters (used when FUNDAMENTALS_SOURCES env var is set)
ALL_ADAPTERS: List[FundamentalsAdapter] = [
    SupabaseAdapter(),
    NSEPythonAdapter(),
    YFinanceAdapter(),
    FinnhubAdapter(),
]


def _get_adapter_chain() -> List[FundamentalsAdapter]:
    """
    Get ordered list of adapters based on FUNDAMENTALS_SOURCES env var.

    Env var format: comma-separated adapter names, e.g. "supabase,nsepython,yfinance"
    If not set, uses DEFAULT_ADAPTERS.
    """
    sources_env = os.environ.get("FUNDAMENTALS_SOURCES", "").strip()
    if not sources_env:
        return DEFAULT_ADAPTERS

    name_map = {a.name: a for a in ALL_ADAPTERS}
    chain = []
    for name in sources_env.split(","):
        name = name.strip().lower()
        if name in name_map:
            chain.append(name_map[name])
        else:
            logger.warning(f"Unknown fundamentals source: {name}")
    return chain or DEFAULT_ADAPTERS


def get_fundamentals(ticker: str) -> Dict[str, Any]:
    """
    Fetch stock fundamentals using a cascade of data sources.

    Tries each adapter in order. The first successful response is used as
    the base, then subsequent adapters fill in any missing (None) fields.
    This gives the best of all worlds: fast response + rich data.

    Args:
        ticker: NSE stock symbol (e.g., 'RELIANCE' or 'COALINDIA')

    Returns:
        Dict with standard fundamentals schema. Always includes 'ticker',
        'data_source' (comma-separated list of sources used), and 'timestamp'.
    """
    ticker_clean = ticker.replace(".NS", "").upper().strip()
    adapters = _get_adapter_chain()

    base_result: Optional[Dict[str, Any]] = None
    sources_used: List[str] = []

    for adapter in adapters:
        try:
            data = adapter.fetch(ticker_clean)
        except Exception as e:
            logger.warning(f"[{adapter.name}] Unexpected error for {ticker_clean}: {e}")
            continue

        if not data:
            logger.debug(f"[{adapter.name}] No data for {ticker_clean}")
            continue

        # Count non-None fields this adapter provides
        filled_fields = [k for k, v in data.items()
                         if k not in ("data_source", "timestamp", "ticker") and v is not None]

        if base_result is None:
            # First successful source becomes the base
            base_result = data
            sources_used.append(adapter.name)
            logger.info(f"[{adapter.name}] Base for {ticker_clean}: {len(filled_fields)} fields")
        else:
            # Merge: fill in any None fields from this source
            merged_fields = []
            for key, val in data.items():
                if key in ("data_source", "timestamp"):
                    continue
                if base_result.get(key) is None and val is not None:
                    base_result[key] = val
                    merged_fields.append(key)
            if merged_fields:
                sources_used.append(adapter.name)
                logger.info(
                    f"[{adapter.name}] Merged {len(merged_fields)} fields for {ticker_clean}: "
                    f"{', '.join(merged_fields[:10])}"
                    f"{'...' if len(merged_fields) > 10 else ''}"
                )

        # NOTE: We intentionally do NOT stop early. Even if basic fields
        # (price, PE, sector) are filled by Supabase/nsepython, we continue
        # the cascade so yfinance/Finnhub can contribute deep fundamentals
        # like margins, debt_to_equity, ROE, ROCE, dividends, beta, etc.

    if base_result:
        base_result["data_source"] = ",".join(sources_used)
        base_result["timestamp"] = datetime.now().isoformat()
        # Log final coverage summary
        key_fields = ["pe_ratio", "roe", "profit_margin", "operating_margin",
                       "debt_to_equity", "dividend_yield", "revenue_growth_yoy", "beta"]
        coverage = {f: (base_result.get(f) is not None) for f in key_fields}
        missing = [f for f, v in coverage.items() if not v]
        logger.info(
            f"Fundamentals for {ticker_clean} from [{base_result['data_source']}] — "
            f"missing: {missing if missing else 'none'}"
        )
        return base_result

    # All adapters failed
    logger.error(f"All fundamentals adapters failed for {ticker_clean}")
    return {
        "error": f"No fundamental data available for {ticker_clean}",
        "ticker": ticker_clean,
        "data_source": "none",
        "timestamp": datetime.now().isoformat(),
    }
