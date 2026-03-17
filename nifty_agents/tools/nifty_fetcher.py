"""
NIFTY Stock Data Fetcher

Fetches stock data for Indian equities using:
- Adapter cascade for fundamentals: Supabase -> nsepython -> yfinance -> Finnhub
- nsetools: Live quotes, index data
- yfinance: Price history (with retry on rate limits)

Supports NIFTY 50/200/500 stocks with .NS suffix handling.
"""

import yfinance as yf
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Try to import nsetools, provide fallback
try:
    from nsetools import Nse
    NSETOOLS_AVAILABLE = True
except ImportError:
    NSETOOLS_AVAILABLE = False
    logging.warning("nsetools not installed. Live quotes will use yfinance fallback.")

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when a Yahoo Finance request is rate-limited."""
    pass


def _yf_retry_decorator(func):
    """Apply tenacity retry with exponential backoff for rate-limited yfinance calls."""
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=5, max=60),
        retry=retry_if_exception_type(RateLimitError),
        reraise=True,
        before_sleep=lambda rs: logger.warning(
            f"Rate limited, retrying in {rs.next_action.sleep:.0f}s "
            f"(attempt {rs.attempt_number}/5)"
        ),
    )
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def _normalize_ticker(ticker: str) -> tuple[str, str]:
    """
    Normalize ticker symbol.

    Args:
        ticker: Stock symbol (with or without .NS suffix)

    Returns:
        Tuple of (ticker_for_yfinance, ticker_for_nse)
        yfinance needs .NS suffix, nsetools needs bare symbol
    """
    ticker = ticker.upper().strip()

    if ticker.endswith(".NS"):
        yf_ticker = ticker
        nse_ticker = ticker.replace(".NS", "")
    else:
        yf_ticker = f"{ticker}.NS"
        nse_ticker = ticker

    return yf_ticker, nse_ticker


def get_stock_fundamentals(ticker: str) -> Dict[str, Any]:
    """
    Get fundamental financial data for a NIFTY stock.

    Uses the adapter cascade: Supabase -> nsepython -> yfinance -> Finnhub.
    Each source fills in missing fields, so even if Yahoo is rate-limited,
    agents still get usable data from faster sources.

    Args:
        ticker: NSE stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS')

    Returns:
        Dict containing ticker, valuation ratios, profitability metrics,
        price info, and metadata. 'data_source' shows which sources contributed.

    Example:
        >>> result = get_stock_fundamentals("RELIANCE")
        >>> print(result["pe_ratio"])
        25.5
    """
    from .fundamentals_adapter import get_fundamentals
    return get_fundamentals(ticker)


@_yf_retry_decorator
def get_stock_quote(ticker: str) -> Dict[str, Any]:
    """
    Get real-time/live quote for a NIFTY stock.

    Uses nsetools for live NSE data, falls back to yfinance if unavailable.
    Retries automatically on rate-limit (429) errors with exponential backoff.

    Args:
        ticker: NSE stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS')

    Returns:
        Dict containing:
        - last_price: Current/last traded price
        - change: Price change from previous close
        - change_pct: Percentage change
        - open, high, low, close: OHLC data
        - volume: Trading volume
        - vwap: Volume weighted average price
        - bid, ask: Best bid/ask prices

    Example:
        >>> quote = get_stock_quote("TCS")
        >>> print(f"TCS: ₹{quote['last_price']}")
    """
    yf_ticker, nse_ticker = _normalize_ticker(ticker)

    # Try nsetools first for live NSE data
    if NSETOOLS_AVAILABLE:
        try:
            nse = Nse()
            quote_data = nse.get_quote(nse_ticker)

            if quote_data:
                return {
                    "ticker": nse_ticker,
                    "last_price": quote_data.get("lastPrice"),
                    "change": quote_data.get("change"),
                    "change_pct": quote_data.get("pChange"),
                    "previous_close": quote_data.get("previousClose"),
                    "open": quote_data.get("open"),
                    "close": quote_data.get("close"),
                    "vwap": quote_data.get("vwap"),
                    "high": quote_data.get("intraDayHighLow", {}).get("max"),
                    "low": quote_data.get("intraDayHighLow", {}).get("min"),
                    "52w_high": quote_data.get("weekHighLow", {}).get("max"),
                    "52w_low": quote_data.get("weekHighLow", {}).get("min"),
                    "upper_circuit": quote_data.get("upperCP"),
                    "lower_circuit": quote_data.get("lowerCP"),
                    "data_source": "nsetools",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning(f"nsetools failed for {ticker}, falling back to yfinance: {e}")

    # Fallback to yfinance
    try:
        stock = yf.Ticker(yf_ticker)
        info = stock.info

        return {
            "ticker": nse_ticker,
            "last_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "change": info.get("regularMarketChange"),
            "change_pct": info.get("regularMarketChangePercent"),
            "previous_close": info.get("previousClose"),
            "open": info.get("regularMarketOpen"),
            "high": info.get("regularMarketDayHigh"),
            "low": info.get("regularMarketDayLow"),
            "volume": info.get("regularMarketVolume"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "data_source": "yfinance",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        err_str = str(e).lower()
        if "too many requests" in err_str or "rate limit" in err_str or "429" in err_str:
            logger.warning(f"Rate limited fetching quote for {ticker}, will retry...")
            raise RateLimitError(f"Rate limited for {ticker}: {e}") from e
        logger.error(f"Error fetching quote for {ticker}: {e}")
        return {
            "error": f"Error fetching quote: {str(e)}",
            "ticker": nse_ticker,
            "timestamp": datetime.now().isoformat()
        }


@_yf_retry_decorator
def get_price_history(
    ticker: str,
    days: int = 365,
    interval: str = "1d"
) -> Dict[str, Any]:
    """
    Get historical price and volume data for a NIFTY stock.

    Retries automatically on rate-limit (429) errors with exponential backoff.

    Args:
        ticker: NSE stock symbol
        days: Number of days of history (default: 365)
        interval: Data interval - '1d', '1wk', '1mo' (default: '1d')

    Returns:
        Dict containing:
        - ticker: Stock symbol
        - interval: Data frequency
        - data: List of OHLCV records with date
        - count: Number of data points

    Example:
        >>> history = get_price_history("INFY", days=30)
        >>> for record in history["data"][-5:]:
        ...     print(f"{record['date']}: {record['close']}")
    """
    yf_ticker, nse_ticker = _normalize_ticker(ticker)

    try:
        stock = yf.Ticker(yf_ticker)

        # Calculate period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Fetch history
        hist = stock.history(start=start_date, end=end_date, interval=interval)

        if hist.empty:
            return {
                "error": f"No price history available for {ticker}",
                "ticker": nse_ticker,
                "timestamp": datetime.now().isoformat()
            }

        # Convert to list of dicts
        data = []
        for date_idx, row in hist.iterrows():
            data.append({
                "date": date_idx.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"]),
            })

        return {
            "ticker": nse_ticker,
            "interval": interval,
            "data": data,
            "count": len(data),
            "start_date": data[0]["date"] if data else None,
            "end_date": data[-1]["date"] if data else None,
            "data_source": "yfinance",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        err_str = str(e).lower()
        if "too many requests" in err_str or "rate limit" in err_str or "429" in err_str:
            logger.warning(f"Rate limited fetching price history for {ticker}, will retry...")
            raise RateLimitError(f"Rate limited for {ticker}: {e}") from e
        logger.error(f"Error fetching price history for {ticker}: {e}")
        return {
            "error": f"Error fetching price history: {str(e)}",
            "ticker": nse_ticker,
            "timestamp": datetime.now().isoformat()
        }


def get_index_quote(index_name: str = "NIFTY 50") -> Dict[str, Any]:
    """
    Get real-time quote for an NSE index.

    Args:
        index_name: Index name (e.g., 'NIFTY 50', 'NIFTY BANK', 'INDIA VIX')

    Returns:
        Dict containing:
        - index: Index name
        - last: Current index value
        - change: Point change
        - change_pct: Percentage change
        - pe, pb, dy: Valuation metrics (for equity indices)
        - advances, declines: Market breadth

    Example:
        >>> nifty = get_index_quote("NIFTY 50")
        >>> print(f"NIFTY: {nifty['last']} ({nifty['change_pct']}%)")
    """
    if not NSETOOLS_AVAILABLE:
        return {
            "error": "nsetools not installed. Install with: pip install nsetools",
            "index": index_name,
            "timestamp": datetime.now().isoformat()
        }

    try:
        nse = Nse()
        quote_data = nse.get_index_quote(index_name)

        if not quote_data:
            return {
                "error": f"No data available for index: {index_name}",
                "index": index_name,
                "timestamp": datetime.now().isoformat()
            }

        return {
            "index": quote_data.get("index", index_name),
            "last": quote_data.get("last"),
            "change": quote_data.get("variation"),
            "change_pct": quote_data.get("percentChange"),
            "open": quote_data.get("open"),
            "high": quote_data.get("high"),
            "low": quote_data.get("low"),
            "previous_close": quote_data.get("previousClose"),
            "year_high": quote_data.get("yearHigh"),
            "year_low": quote_data.get("yearLow"),
            "pe": quote_data.get("pe"),
            "pb": quote_data.get("pb"),
            "dividend_yield": quote_data.get("dy"),
            "advances": quote_data.get("advances"),
            "declines": quote_data.get("declines"),
            "unchanged": quote_data.get("unchanged"),
            "data_source": "nsetools",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching index quote for {index_name}: {e}")
        return {
            "error": f"Error fetching index quote: {str(e)}",
            "index": index_name,
            "timestamp": datetime.now().isoformat()
        }


def get_stocks_in_index(index_name: str = "NIFTY 50") -> List[str]:
    """
    Get list of stock symbols in an NSE index.

    Args:
        index_name: Index name (e.g., 'NIFTY 50', 'NIFTY BANK')

    Returns:
        List of stock symbols

    Example:
        >>> stocks = get_stocks_in_index("NIFTY BANK")
        >>> print(stocks[:5])
        ['HDFCBANK', 'ICICIBANK', 'KOTAKBANK', 'AXISBANK', 'SBIN']
    """
    if not NSETOOLS_AVAILABLE:
        return []

    try:
        nse = Nse()
        return nse.get_stocks_in_index(index_name)
    except Exception as e:
        logger.error(f"Error getting stocks in {index_name}: {e}")
        return []
