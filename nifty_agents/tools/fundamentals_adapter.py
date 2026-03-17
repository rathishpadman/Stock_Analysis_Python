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
                "market_cap": d.get("market_cap"),
                "pe_ratio": d.get("pe_ttm"),
                "pb_ratio": d.get("pb"),

                # Profitability
                "roe": d.get("roe_ttm"),

                # Price
                "current_price": d.get("price_last"),
                "previous_close": d.get("prev_close"),
                "52w_high": d.get("high_52w"),
                "52w_low": d.get("low_52w"),
                "200d_avg": d.get("sma200"),

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

            if result.get("current_price"):
                logger.info(f"[{self.name}] Fetched fundamentals for {ticker}")
                return result
            return None

        except Exception as e:
            logger.debug(f"[{self.name}] Failed for {ticker}: {e}")
            return None


# =============================================================================
# 3. yfinance Adapter (tertiary — richest data, but rate-limited)
# =============================================================================

class YFinanceAdapter(FundamentalsAdapter):
    name = "yfinance"

    def fetch(self, ticker: str) -> Optional[Dict[str, Any]]:
        try:
            import yfinance as yf
            from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
        except ImportError:
            logger.debug(f"[{self.name}] yfinance not installed")
            return None

        yf_ticker = f"{ticker}.NS" if not ticker.endswith(".NS") else ticker

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
                logger.warning(f"[{self.name}] Rate limited for {ticker}")
            else:
                logger.debug(f"[{self.name}] Failed for {ticker}: {e}")
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

# Default cascade order — can be overridden via FUNDAMENTALS_SOURCES env var
DEFAULT_ADAPTERS: List[FundamentalsAdapter] = [
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

    name_map = {a.name: a for a in DEFAULT_ADAPTERS}
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
            continue

        if base_result is None:
            # First successful source becomes the base
            base_result = data
            sources_used.append(adapter.name)
        else:
            # Merge: fill in any None fields from this source
            merged = False
            for key, val in data.items():
                if key in ("data_source", "timestamp"):
                    continue
                if base_result.get(key) is None and val is not None:
                    base_result[key] = val
                    merged = True
            if merged:
                sources_used.append(adapter.name)

        # If we have all critical fields, stop early
        critical = ("current_price", "pe_ratio", "sector", "industry", "market_cap")
        if base_result and all(base_result.get(k) is not None for k in critical):
            break

    if base_result:
        base_result["data_source"] = ",".join(sources_used)
        base_result["timestamp"] = datetime.now().isoformat()
        return base_result

    # All adapters failed
    logger.error(f"All fundamentals adapters failed for {ticker_clean}")
    return {
        "error": f"No fundamental data available for {ticker_clean}",
        "ticker": ticker_clean,
        "data_source": "none",
        "timestamp": datetime.now().isoformat(),
    }
