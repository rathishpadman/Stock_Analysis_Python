"""
NIFTY Stock Data Fetcher

Fetches stock data for Indian equities using:
- yfinance: Price history, fundamentals, financials
- nsetools: Live quotes, index data

Supports NIFTY 50/200/500 stocks with .NS suffix handling.
"""

import yfinance as yf
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

# Try to import nsetools, provide fallback
try:
    from nsetools import Nse
    NSETOOLS_AVAILABLE = True
except ImportError:
    NSETOOLS_AVAILABLE = False
    logging.warning("nsetools not installed. Live quotes will use yfinance fallback.")

logger = logging.getLogger(__name__)


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
    
    Uses yfinance to fetch company info, financials, and key ratios.
    
    Args:
        ticker: NSE stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS')
    
    Returns:
        Dict containing:
        - ticker: Normalized ticker symbol
        - company_name: Full company name
        - sector, industry: Classification
        - market_cap: Market capitalization in INR
        - pe_ratio, pb_ratio: Valuation ratios
        - roe, roa: Profitability metrics
        - debt_to_equity: Leverage ratio
        - dividend_yield: Dividend yield %
        - margins: Gross, operating, profit margins
        - 52w_high, 52w_low: Year range
        - current_price: Latest price
        
    Example:
        >>> result = get_stock_fundamentals("RELIANCE")
        >>> print(result["pe_ratio"])
        25.5
    """
    yf_ticker, nse_ticker = _normalize_ticker(ticker)
    
    try:
        stock = yf.Ticker(yf_ticker)
        info = stock.info
        
        # Check if we got valid data
        if not info or not info.get("symbol"):
            return {
                "error": f"No fundamental data available for {ticker}",
                "ticker": nse_ticker,
                "timestamp": datetime.now().isoformat()
            }
        
        fundamentals = {
            "ticker": nse_ticker,
            "yf_ticker": yf_ticker,
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
            
            # Price Info
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
            
            # Metadata
            "currency": info.get("currency", "INR"),
            "exchange": info.get("exchange", "NSE"),
            "data_source": "yfinance",
            "timestamp": datetime.now().isoformat()
        }
        
        return fundamentals
        
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker}: {e}")
        return {
            "error": f"Error fetching fundamentals: {str(e)}",
            "ticker": nse_ticker,
            "timestamp": datetime.now().isoformat()
        }


def get_stock_quote(ticker: str) -> Dict[str, Any]:
    """
    Get real-time/live quote for a NIFTY stock.
    
    Uses nsetools for live NSE data, falls back to yfinance if unavailable.
    
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
        logger.error(f"Error fetching quote for {ticker}: {e}")
        return {
            "error": f"Error fetching quote: {str(e)}",
            "ticker": nse_ticker,
            "timestamp": datetime.now().isoformat()
        }


def get_price_history(
    ticker: str,
    days: int = 365,
    interval: str = "1d"
) -> Dict[str, Any]:
    """
    Get historical price and volume data for a NIFTY stock.
    
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
