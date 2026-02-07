"""
Supabase Data Fetcher

Fetches pre-computed data from existing Supabase tables:
- daily_stocks: Daily price, scores, technicals
- weekly_analysis: Weekly metrics and trends
- monthly_analysis: Monthly performance data
- seasonality: Historical seasonality patterns

This leverages the existing data pipeline that already computes
fundamental scores, technical indicators, and rankings.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
import logging
import pandas as pd

# Try to import yfinance for index data fallback
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# Try to import supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

logger = logging.getLogger(__name__)


def _get_supabase_client() -> Optional[Any]:
    """
    Get Supabase client using environment variables.
    
    Expects:
    - SUPABASE_URL or NEXT_PUBLIC_SUPABASE_URL
    - SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY
    
    Returns:
        Supabase client or None if not configured
    """
    if not SUPABASE_AVAILABLE:
        logger.warning("supabase-py not installed. Run: pip install supabase")
        return None
    
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        logger.warning("Supabase credentials not found in environment")
        return None
    
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None


# Public alias for external imports
def get_supabase_client() -> Optional[Any]:
    """Public wrapper for _get_supabase_client."""
    return _get_supabase_client()


def get_daily_stock_data(
    ticker: str,
    limit: int = 1
) -> Dict[str, Any]:
    """
    Get latest daily stock data from Supabase.
    
    The daily_stocks table contains:
    - Price data (open, high, low, close, volume)
    - Technical scores (technical_score, trend_score)
    - Fundamental scores (fundamental_score, quality_score)
    - Composite rankings
    
    Args:
        ticker: Stock ticker (e.g., "RELIANCE", "TCS")
        limit: Number of recent records to fetch
        
    Returns:
        Dict with latest stock data and scores
        
    Example:
        >>> data = get_daily_stock_data("RELIANCE")
        >>> print(f"Score: {data['composite_score']}")
    """
    ticker_clean = ticker.replace(".NS", "").upper()
    
    client = _get_supabase_client()
    if not client:
        return {
            "error": "Supabase not configured",
            "ticker": ticker_clean
        }
    
    try:
        response = client.table("daily_stocks") \
            .select("*") \
            .eq("ticker", ticker_clean) \
            .order("date", desc=True) \
            .limit(limit) \
            .execute()
        
        if not response.data:
            return {
                "error": f"No data found for {ticker_clean}",
                "ticker": ticker_clean
            }
        
        data = response.data[0] if limit == 1 else response.data
        
        return {
            "ticker": ticker_clean,
            "data": data,
            "source": "supabase_daily_stocks",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching daily data for {ticker}: {e}")
        return {
            "error": str(e),
            "ticker": ticker_clean
        }


def get_weekly_analysis(
    ticker: str,
    weeks: int = 4
) -> Dict[str, Any]:
    """
    Get weekly analysis data from Supabase.
    
    The weekly_analysis table contains:
    - Weekly returns and volatility
    - Moving average signals
    - Momentum indicators
    - Volume trends
    
    Args:
        ticker: Stock ticker
        weeks: Number of weeks to fetch
        
    Returns:
        Dict with weekly analysis data
    """
    ticker_clean = ticker.replace(".NS", "").upper()
    
    client = _get_supabase_client()
    if not client:
        return {"error": "Supabase not configured", "ticker": ticker_clean}
    
    try:
        response = client.table("weekly_analysis") \
            .select("*") \
            .eq("ticker", ticker_clean) \
            .order("week_ending", desc=True) \
            .limit(weeks) \
            .execute()
        
        if not response.data:
            return {
                "error": f"No weekly data for {ticker_clean}",
                "ticker": ticker_clean
            }
        
        # Calculate trends from weekly data
        data = response.data
        if len(data) >= 2:
            recent_week = data[0]
            prev_week = data[1]
            
            # Calculate weekly change (using actual column names)
            if recent_week.get("weekly_close") and prev_week.get("weekly_close"):
                weekly_change = (
                    (recent_week["weekly_close"] - prev_week["weekly_close"]) 
                    / prev_week["weekly_close"] * 100
                )
            else:
                # Use pre-computed weekly return if available
                weekly_change = recent_week.get("weekly_return_pct")
        else:
            weekly_change = data[0].get("weekly_return_pct") if data else None
        
        return {
            "ticker": ticker_clean,
            "weeks_data": data,
            "weekly_change_pct": round(weekly_change, 2) if weekly_change else None,
            "source": "supabase_weekly_analysis",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching weekly data for {ticker}: {e}")
        return {"error": str(e), "ticker": ticker_clean}


def get_monthly_analysis(
    ticker: str,
    months: int = 6
) -> Dict[str, Any]:
    """
    Get monthly analysis data from Supabase.
    
    The monthly_analysis table contains:
    - Monthly returns
    - YTD performance
    - 52-week high/low proximity
    - Long-term trends
    
    Args:
        ticker: Stock ticker
        months: Number of months to fetch
        
    Returns:
        Dict with monthly analysis data
    """
    ticker_clean = ticker.replace(".NS", "").upper()
    
    client = _get_supabase_client()
    if not client:
        return {"error": "Supabase not configured", "ticker": ticker_clean}
    
    try:
        response = client.table("monthly_analysis") \
            .select("*") \
            .eq("ticker", ticker_clean) \
            .order("month", desc=True) \
            .limit(months) \
            .execute()
        
        if not response.data:
            return {
                "error": f"No monthly data for {ticker_clean}",
                "ticker": ticker_clean
            }
        
        data = response.data
        
        # Calculate monthly performance summary (using actual column names)
        if len(data) >= 2:
            returns = []
            for i in range(len(data) - 1):
                # Use pre-computed monthly_return_pct if available
                if data[i].get("monthly_return_pct") is not None:
                    returns.append(float(data[i]["monthly_return_pct"]))
                elif data[i].get("monthly_close") and data[i+1].get("monthly_close"):
                    ret = (float(data[i]["monthly_close"]) - float(data[i+1]["monthly_close"])) / float(data[i+1]["monthly_close"]) * 100
                    returns.append(ret)
            
            avg_monthly_return = sum(returns) / len(returns) if returns else None
        else:
            avg_monthly_return = data[0].get("avg_monthly_return_12m") if data else None
        
        return {
            "ticker": ticker_clean,
            "months_data": data,
            "avg_monthly_return_pct": round(avg_monthly_return, 2) if avg_monthly_return else None,
            "source": "supabase_monthly_analysis",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching monthly data for {ticker}: {e}")
        return {"error": str(e), "ticker": ticker_clean}


def get_seasonality_data(
    ticker: str
) -> Dict[str, Any]:
    """
    Get seasonality patterns from Supabase.
    
    The seasonality table contains:
    - Historical monthly performance patterns
    - Best/worst months historically
    - Seasonal trading signals
    
    Args:
        ticker: Stock ticker
        
    Returns:
        Dict with seasonality data
    """
    ticker_clean = ticker.replace(".NS", "").upper()
    
    client = _get_supabase_client()
    if not client:
        return {"error": "Supabase not configured", "ticker": ticker_clean}
    
    try:
        response = client.table("seasonality") \
            .select("*") \
            .eq("ticker", ticker_clean) \
            .execute()
        
        if not response.data:
            return {
                "error": f"No seasonality data for {ticker_clean}",
                "ticker": ticker_clean
            }
        
        data = response.data[0] if len(response.data) == 1 else response.data
        
        return {
            "ticker": ticker_clean,
            "seasonality": data,
            "source": "supabase_seasonality",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching seasonality for {ticker}: {e}")
        return {"error": str(e), "ticker": ticker_clean}


def get_stock_scores(
    ticker: str
) -> Dict[str, Any]:
    """
    Get all computed scores for a stock.
    
    Aggregates scores from daily_stocks:
    - Fundamental Score (0-100)
    - Technical Score (0-100)
    - Quality Score (0-100)
    - Momentum Score (0-100)
    - Composite Score (weighted average)
    
    Args:
        ticker: Stock ticker
        
    Returns:
        Dict with all scores and rankings
        
    Example:
        >>> scores = get_stock_scores("TCS")
        >>> print(f"Composite: {scores['composite_score']}")
    """
    daily_data = get_daily_stock_data(ticker, limit=1)
    
    if "error" in daily_data:
        return daily_data
    
    data = daily_data.get("data", {})
    ticker_clean = ticker.replace(".NS", "").upper()
    
    # Extract scores (using actual column names from Supabase)
    scores = {
        "ticker": ticker_clean,
        "fundamental_score": data.get("score_fundamental"),
        "technical_score": data.get("score_technical"),
        "quality_score": data.get("quality_score"),
        "momentum_score": data.get("momentum_score"),
        "risk_score": data.get("score_risk"),
        "composite_score": data.get("overall_score"),
        "sentiment_score": data.get("score_sentiment"),
        "macro_score": data.get("score_macro"),
        "date": data.get("date"),
        "price": data.get("price_last"),
        "pe_ttm": data.get("pe_ttm"),
        "pb": data.get("pb"),
        "roe": data.get("roe_ttm"),
        "rsi": data.get("rsi14"),
        # Add MACD indicators
        "macd_line": data.get("macd_line"),
        "macd_signal": data.get("macd_signal"),
        "macd_hist": data.get("macd_hist"),
        "source": "supabase_scores",
        "timestamp": datetime.now().isoformat()
    }
    
    # Add interpretation
    composite = scores.get("composite_score")
    if composite:
        if composite >= 80:
            scores["rating"] = "Strong Buy"
            scores["rating_description"] = "Excellent fundamentals and technicals"
        elif composite >= 65:
            scores["rating"] = "Buy"
            scores["rating_description"] = "Good overall metrics"
        elif composite >= 50:
            scores["rating"] = "Hold"
            scores["rating_description"] = "Average performance"
        elif composite >= 35:
            scores["rating"] = "Reduce"
            scores["rating_description"] = "Below average metrics"
        else:
            scores["rating"] = "Sell"
            scores["rating_description"] = "Poor fundamentals or technicals"
    
    return scores


def get_top_stocks(
    index: str = "NIFTY_50",
    sort_by: str = "composite_score",
    limit: int = 10,
    ascending: bool = False
) -> List[Dict[str, Any]]:
    """
    Get top-ranked stocks from an index.
    
    Args:
        index: Index name (NIFTY_50, NIFTY_200, etc.)
        sort_by: Score to sort by
        limit: Number of stocks to return
        ascending: Sort ascending (True) or descending (False)
        
    Returns:
        List of top stocks with scores
        
    Example:
        >>> top = get_top_stocks("NIFTY_50", "composite_score", 5)
        >>> for stock in top:
        ...     print(f"{stock['ticker']}: {stock['composite_score']}")
    """
    client = _get_supabase_client()
    if not client:
        return [{"error": "Supabase not configured"}]
    
    try:
        # Get the most recent date's data
        response = client.table("daily_stocks") \
            .select("*") \
            .eq("index", index) \
            .order("date", desc=True) \
            .limit(1) \
            .execute()
        
        if not response.data:
            return [{"error": f"No data for index {index}"}]
        
        latest_date = response.data[0].get("date")
        
        # Get all stocks for that date, sorted
        response = client.table("daily_stocks") \
            .select("*") \
            .eq("index", index) \
            .eq("date", latest_date) \
            .order(sort_by, desc=not ascending) \
            .limit(limit) \
            .execute()
        
        return response.data if response.data else []
        
    except Exception as e:
        logger.error(f"Error fetching top stocks: {e}")
        return [{"error": str(e)}]


def get_comprehensive_stock_data(
    ticker: str
) -> Dict[str, Any]:
    """
    Get all available data for a stock from Supabase.
    
    Combines:
    - Daily data with scores
    - Weekly analysis
    - Monthly analysis
    - Seasonality patterns
    
    This is the main function agents should use to get
    pre-computed data from the existing pipeline.
    
    Args:
        ticker: Stock ticker
        
    Returns:
        Comprehensive data dict
        
    Example:
        >>> data = get_comprehensive_stock_data("RELIANCE")
        >>> print(f"Score: {data['scores']['composite_score']}")
        >>> print(f"Weekly Change: {data['weekly']['weekly_change_pct']}%")
    """
    ticker_clean = ticker.replace(".NS", "").upper()
    
    result = {
        "ticker": ticker_clean,
        "timestamp": datetime.now().isoformat()
    }
    
    # Get scores
    try:
        result["scores"] = get_stock_scores(ticker_clean)
    except Exception as e:
        result["scores"] = {"error": str(e)}
    
    # Get weekly analysis
    try:
        result["weekly"] = get_weekly_analysis(ticker_clean, weeks=4)
    except Exception as e:
        result["weekly"] = {"error": str(e)}
    
    # Get monthly analysis
    try:
        result["monthly"] = get_monthly_analysis(ticker_clean, months=6)
    except Exception as e:
        result["monthly"] = {"error": str(e)}
    
    # Get seasonality
    try:
        result["seasonality"] = get_seasonality_data(ticker_clean)
    except Exception as e:
        result["seasonality"] = {"error": str(e)}
    
    return result


def search_stocks(
    query: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Search stocks based on criteria.
    
    Args:
        query: Dict with search criteria
            - min_composite_score: Minimum composite score
            - min_fundamental_score: Minimum fundamental score
            - sector: Filter by sector
            - index: Filter by index (NIFTY_50, NIFTY_200)
            
    Returns:
        List of matching stocks
        
    Example:
        >>> stocks = search_stocks({
        ...     "min_composite_score": 70,
        ...     "index": "NIFTY_50"
        ... })
    """
    client = _get_supabase_client()
    if not client:
        return [{"error": "Supabase not configured"}]
    
    try:
        # Start query
        q = client.table("daily_stocks").select("*")
        
        # Apply filters
        if "index" in query:
            q = q.eq("index", query["index"])
        
        if "min_composite_score" in query:
            q = q.gte("composite_score", query["min_composite_score"])
        
        if "min_fundamental_score" in query:
            q = q.gte("fundamental_score", query["min_fundamental_score"])
        
        if "sector" in query:
            q = q.eq("sector", query["sector"])
        
        # Get latest date and filter
        q = q.order("date", desc=True).limit(200)
        
        response = q.execute()
        
        # Filter to latest date only
        if response.data:
            latest_date = response.data[0].get("date")
            return [d for d in response.data if d.get("date") == latest_date]
        
        return []
        
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        return [{"error": str(e)}]


# =============================================================================
# INDEX DATA FALLBACK (for NIFTY50, BANKNIFTY, etc.)
# =============================================================================

# Yahoo Finance symbols for Indian indices
INDEX_SYMBOLS = {
    "NIFTY50": "^NSEI",
    "NIFTY_50": "^NSEI",
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "BANK_NIFTY": "^NSEBANK",
    "NIFTY_BANK": "^NSEBANK",
    "NIFTY_IT": "^CNXIT",
    "NIFTY_MIDCAP": "^NSEMDCP50",
}


def get_index_weekly_data(
    index_name: str,
    weeks: int = 4
) -> Dict[str, Any]:
    """
    Fetch index data directly from yfinance when not available in Supabase.
    
    This is a fallback for indices like NIFTY50 that may not be in the
    weekly_analysis table.
    
    Args:
        index_name: Index name (e.g., "NIFTY50", "BANKNIFTY")
        weeks: Number of weeks of data to fetch
        
    Returns:
        Dict with index weekly data including OHLCV and basic technicals
    """
    if not YFINANCE_AVAILABLE:
        logger.warning("yfinance not available for index data fallback")
        return {"error": "yfinance not installed", "index": index_name}
    
    # Map index name to Yahoo symbol
    index_clean = index_name.upper().replace(" ", "_").replace("-", "_")
    yahoo_symbol = INDEX_SYMBOLS.get(index_clean)
    
    if not yahoo_symbol:
        # Try common patterns
        if "NIFTY" in index_clean and "50" in index_clean:
            yahoo_symbol = "^NSEI"
        elif "BANK" in index_clean:
            yahoo_symbol = "^NSEBANK"
        else:
            return {"error": f"Unknown index: {index_name}", "index": index_name}
    
    try:
        logger.info(f"Fetching index data for {index_name} ({yahoo_symbol}) from yfinance")
        
        # Fetch daily data for enough history
        days_needed = weeks * 7 + 14  # Extra buffer for weekends/holidays
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_needed)
        
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            return {"error": f"No data returned for {yahoo_symbol}", "index": index_name}
        
        # Resample to weekly
        df_weekly = df.resample('W-FRI').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        if df_weekly.empty:
            return {"error": "No weekly data after resampling", "index": index_name}
        
        # Calculate basic technicals
        df_weekly['Weekly_Return_Pct'] = df_weekly['Close'].pct_change() * 100
        
        # RSI calculation (14 periods)
        delta = df_weekly['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df_weekly['RSI_14'] = 100 - (100 / (1 + rs))
        
        # SMAs
        df_weekly['SMA_10'] = df_weekly['Close'].rolling(window=10).mean()
        df_weekly['SMA_20'] = df_weekly['Close'].rolling(window=20).mean()
        
        # Get last N weeks
        df_weekly = df_weekly.tail(weeks)
        
        # Convert to list of dicts
        weeks_data = []
        for idx, row in df_weekly.iterrows():
            weeks_data.append({
                "week_ending": idx.strftime('%Y-%m-%d'),
                "weekly_open": round(row['Open'], 2),
                "weekly_high": round(row['High'], 2),
                "weekly_low": round(row['Low'], 2),
                "weekly_close": round(row['Close'], 2),
                "weekly_volume": int(row['Volume']),
                "weekly_return_pct": round(row['Weekly_Return_Pct'], 2) if pd.notna(row['Weekly_Return_Pct']) else None,
                "rsi_14": round(row['RSI_14'], 2) if pd.notna(row['RSI_14']) else None,
                "sma_10": round(row['SMA_10'], 2) if pd.notna(row['SMA_10']) else None,
                "sma_20": round(row['SMA_20'], 2) if pd.notna(row['SMA_20']) else None,
            })
        
        # Latest week data
        latest = df_weekly.iloc[-1] if len(df_weekly) > 0 else None
        prev = df_weekly.iloc[-2] if len(df_weekly) > 1 else None
        
        weekly_change = None
        if latest is not None and prev is not None:
            weekly_change = round((latest['Close'] - prev['Close']) / prev['Close'] * 100, 2)
        
        return {
            "index": index_name,
            "yahoo_symbol": yahoo_symbol,
            "weeks_data": weeks_data,
            "weekly_change_pct": weekly_change,
            "latest_close": round(latest['Close'], 2) if latest is not None else None,
            "latest_rsi": round(latest['RSI_14'], 2) if latest is not None and pd.notna(latest['RSI_14']) else None,
            "source": "yfinance_index",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching index data for {index_name}: {e}")
        return {"error": str(e), "index": index_name}


def get_weekly_analysis_enhanced(
    ticker: str,
    weeks: int = 4
) -> Dict[str, Any]:
    """
    Enhanced weekly analysis that handles both stocks and indices.
    
    For stocks: Uses Supabase data
    For indices (NIFTY50, etc.): Uses yfinance fallback
    
    Args:
        ticker: Stock ticker or index name
        weeks: Number of weeks to fetch
        
    Returns:
        Dict with weekly analysis data
    """
    ticker_clean = ticker.replace(".NS", "").upper()
    
    # Check if this is an index
    is_index = any(idx in ticker_clean for idx in ["NIFTY", "BANKNIFTY", "INDEX", "SENSEX"])
    
    if is_index:
        # Use yfinance fallback for indices
        index_data = get_index_weekly_data(ticker_clean, weeks)
        if "error" not in index_data:
            return {
                "ticker": ticker_clean,
                "is_index": True,
                "weeks_data": index_data.get("weeks_data", []),
                "weekly_change_pct": index_data.get("weekly_change_pct"),
                "latest_close": index_data.get("latest_close"),
                "latest_rsi": index_data.get("latest_rsi"),
                "source": "yfinance_index",
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.warning(f"Index fallback failed for {ticker_clean}: {index_data.get('error')}")
    
    # Default: Try Supabase for regular stocks
    return get_weekly_analysis(ticker_clean, weeks)


# =============================================================================
# Additional Helper Functions for Temporal Analysis
# =============================================================================

def get_sector_performance(
    sectors: List[str] = None,
    period: str = "1W"
) -> Dict[str, Any]:
    """
    Get sector-wise performance data.
    
    Args:
        sectors: List of sector names (if None, gets all)
        period: Time period ("1W", "1M", "3M")
        
    Returns:
        Dict with sector performance metrics
    """
    client = _get_supabase_client()
    if not client:
        return {"error": "Supabase not configured"}
    
    try:
        # Get latest data grouped by sector - using correct column names from schema
        response = client.table("daily_stocks") \
            .select("sector, return_1w, return_1m, score_technical, overall_score") \
            .order("date", desc=True) \
            .limit(500) \
            .execute()
        
        if not response.data:
            return {"sectors": {}, "note": "No data available"}
        
        # Get latest date's data
        latest_date = response.data[0].get("date")
        latest_data = [d for d in response.data if d.get("date") == latest_date]
        
        # Aggregate by sector
        sector_data = {}
        for row in latest_data:
            sector = row.get("sector", "Unknown")
            if sectors and sector not in sectors:
                continue
            
            if sector not in sector_data:
                sector_data[sector] = {
                    "stocks": [],
                    "return_1w": [],
                    "return_1m": [],
                    "avg_score": []
                }
            
            if row.get("return_1w") is not None:
                sector_data[sector]["return_1w"].append(row["return_1w"])
            if row.get("return_1m") is not None:
                sector_data[sector]["return_1m"].append(row["return_1m"])
            if row.get("overall_score") is not None:
                sector_data[sector]["avg_score"].append(row["overall_score"])
        
        # Compute averages
        result = {}
        for sector, data in sector_data.items():
            result[sector] = {
                "avg_return_1w": sum(data["return_1w"]) / len(data["return_1w"]) if data["return_1w"] else 0,
                "avg_return_1m": sum(data["return_1m"]) / len(data["return_1m"]) if data["return_1m"] else 0,
                "avg_overall_score": sum(data["avg_score"]) / len(data["avg_score"]) if data["avg_score"] else 0,
                "stock_count": len(data["return_1w"])
            }
        
        # Sort by weekly return
        sorted_sectors = sorted(result.items(), key=lambda x: x[1]["avg_return_1w"], reverse=True)
        
        return {
            "sectors": dict(sorted_sectors),
            "top_sectors": [s[0] for s in sorted_sectors[:3]],
            "lagging_sectors": [s[0] for s in sorted_sectors[-3:]],
            "period": period
        }
        
    except Exception as e:
        logger.error(f"Error fetching sector performance: {e}")
        return {"error": str(e)}


def get_market_breadth() -> Dict[str, Any]:
    """
    Get market breadth indicators.
    
    Returns:
        Dict with advance/decline data and breadth metrics
    """
    client = _get_supabase_client()
    if not client:
        return {"error": "Supabase not configured"}
    
    try:
        # Get latest day's data - using correct column names from schema
        response = client.table("daily_stocks") \
            .select("ticker, return_1d, price_last, sma200, rsi14") \
            .order("date", desc=True) \
            .limit(500) \
            .execute()
        
        if not response.data:
            return {"error": "No data available"}
        
        # Get latest date only
        latest_date = response.data[0].get("date") if response.data else None
        latest_data = [d for d in response.data if d.get("date") == latest_date]
        
        advances = 0
        declines = 0
        unchanged = 0
        above_200dma = 0
        oversold_rsi = 0
        overbought_rsi = 0
        
        for row in latest_data:
            ret = row.get("return_1d", 0) or 0
            price = row.get("price_last", 0) or 0
            sma_200 = row.get("sma200", 0) or 0
            rsi = row.get("rsi14", 50) or 50
            
            # A/D count
            if ret > 0.1:
                advances += 1
            elif ret < -0.1:
                declines += 1
            else:
                unchanged += 1
            
            # Above 200 DMA
            if price > 0 and sma_200 > 0 and price > sma_200:
                above_200dma += 1
            
            # RSI extremes
            if rsi < 30:
                oversold_rsi += 1
            elif rsi > 70:
                overbought_rsi += 1
        
        total = advances + declines + unchanged
        
        return {
            "advances": advances,
            "declines": declines,
            "unchanged": unchanged,
            "ad_ratio": round(advances / max(declines, 1), 2),
            "advance_pct": round(100 * advances / max(total, 1), 1),
            "above_200dma": above_200dma,
            "above_200dma_pct": round(100 * above_200dma / max(total, 1), 1),
            "oversold_count": oversold_rsi,
            "overbought_count": overbought_rsi,
            "breadth_signal": "bullish" if advances > declines * 1.5 else ("bearish" if declines > advances * 1.5 else "neutral"),
            "total_stocks": total
        }
        
    except Exception as e:
        logger.error(f"Error fetching market breadth: {e}")
        return {"error": str(e)}


def get_index_summary(
    index: str = "NIFTY_200"
) -> Dict[str, Any]:
    """
    Get index-level summary statistics.
    
    Args:
        index: Index name (NIFTY_50, NIFTY_200, NIFTY_500)
        
    Returns:
        Dict with index summary metrics
    """
    client = _get_supabase_client()
    if not client:
        return {"error": "Supabase not configured"}
    
    try:
        response = client.table("daily_stocks") \
            .select("ticker, overall_score, score_technical, score_fundamental, return_1d, return_1w, return_1m") \
            .order("date", desc=True) \
            .limit(500) \
            .execute()
        
        if not response.data:
            return {"error": f"No data available"}
        
        # Get latest date
        latest_date = response.data[0].get("date")
        latest_data = [d for d in response.data if d.get("date") == latest_date]
        
        # Compute stats
        overall_scores = [d.get("overall_score", 0) or 0 for d in latest_data]
        returns_1d = [d.get("return_1d", 0) or 0 for d in latest_data]
        returns_1w = [d.get("return_1w", 0) or 0 for d in latest_data]
        
        return {
            "index": index,
            "stock_count": len(latest_data),
            "avg_overall_score": round(sum(overall_scores) / len(overall_scores), 1) if overall_scores else 0,
            "avg_return_1d": round(sum(returns_1d) / len(returns_1d), 2) if returns_1d else 0,
            "avg_return_1w": round(sum(returns_1w) / len(returns_1w), 2) if returns_1w else 0,
            "high_score_count": len([s for s in overall_scores if s >= 70]),
            "low_score_count": len([s for s in overall_scores if s <= 30])
        }
        
    except Exception as e:
        logger.error(f"Error fetching index summary: {e}")
        return {"error": str(e)}


# =============================================================================
# NIFTY 200 AGGREGATE FUNCTIONS (for AI Outlook)
# =============================================================================

def get_nifty200_weekly_summary() -> Dict[str, Any]:
    """
    Get aggregated weekly summary for all NIFTY 200 stocks.
    
    Uses weekly_analysis table to compute:
    - Market-level returns and breadth
    - Sector performance breakdown
    - Technical distribution (RSI, trends)
    - Top gainers and losers
    
    Returns:
        Dict with comprehensive NIFTY 200 weekly summary
        
    Example:
        >>> summary = get_nifty200_weekly_summary()
        >>> print(f"Avg Weekly Return: {summary['market_summary']['avg_weekly_return']}%")
        >>> print(f"Advances: {summary['market_summary']['advances']}")
    """
    client = _get_supabase_client()
    if not client:
        return {"error": "Supabase not configured"}
    
    try:
        # Get latest week data
        response = client.table("weekly_analysis") \
            .select("*") \
            .order("week_ending", desc=True) \
            .limit(200) \
            .execute()
        
        if not response.data:
            return {"error": "No weekly data available"}
        
        # Get latest week_ending date
        latest_week = response.data[0].get("week_ending")
        week_data = [d for d in response.data if d.get("week_ending") == latest_week]
        
        # Get sector mapping from daily_stocks
        sector_response = client.table("daily_stocks") \
            .select("ticker, sector") \
            .order("date", desc=True) \
            .limit(500) \
            .execute()
        
        # Build sector map
        sector_map = {}
        if sector_response.data:
            for row in sector_response.data:
                if row.get("ticker") and row.get("sector"):
                    sector_map[row["ticker"]] = row["sector"]
        
        # Compute market summary
        returns = [float(d.get("weekly_return_pct", 0) or 0) for d in week_data]
        rsi_values = [float(d.get("weekly_rsi14", 50) or 50) for d in week_data]
        
        advances = sum(1 for r in returns if r > 0)
        declines = sum(1 for r in returns if r < 0)
        unchanged = len(returns) - advances - declines
        
        overbought = sum(1 for r in rsi_values if r > 70)
        oversold = sum(1 for r in rsi_values if r < 30)
        
        trend_up = sum(1 for d in week_data if d.get("weekly_trend") == "UP")
        trend_down = sum(1 for d in week_data if d.get("weekly_trend") == "DOWN")
        trend_sideways = len(week_data) - trend_up - trend_down
        
        # Sector performance
        sector_returns = {}
        for d in week_data:
            ticker = d.get("ticker", "")
            sector = sector_map.get(ticker, "Other")
            ret = float(d.get("weekly_return_pct", 0) or 0)
            
            if sector not in sector_returns:
                sector_returns[sector] = {"returns": [], "advances": 0, "declines": 0}
            
            sector_returns[sector]["returns"].append(ret)
            if ret > 0:
                sector_returns[sector]["advances"] += 1
            elif ret < 0:
                sector_returns[sector]["declines"] += 1
        
        sector_perf = []
        for sector, data in sector_returns.items():
            if data["returns"]:
                avg_ret = sum(data["returns"]) / len(data["returns"])
                sector_perf.append({
                    "sector": sector,
                    "avg_return": round(avg_ret, 2),
                    "stocks": len(data["returns"]),
                    "advances": data["advances"],
                    "declines": data["declines"]
                })
        
        sector_perf.sort(key=lambda x: x["avg_return"], reverse=True)
        
        # Top gainers and losers
        sorted_stocks = sorted(week_data, key=lambda x: float(x.get("weekly_return_pct", 0) or 0), reverse=True)
        
        top_gainers = [{
            "ticker": d.get("ticker"),
            "return_pct": round(float(d.get("weekly_return_pct", 0) or 0), 2),
            "weekly_close": d.get("weekly_close"),
            "sector": sector_map.get(d.get("ticker", ""), "Other")
        } for d in sorted_stocks[:10]]
        
        top_losers = [{
            "ticker": d.get("ticker"),
            "return_pct": round(float(d.get("weekly_return_pct", 0) or 0), 2),
            "weekly_close": d.get("weekly_close"),
            "sector": sector_map.get(d.get("ticker", ""), "Other")
        } for d in sorted_stocks[-10:]]
        
        # 4-week and 13-week returns
        return_4w = [float(d.get("return_4w", 0) or 0) for d in week_data]
        return_13w = [float(d.get("return_13w", 0) or 0) for d in week_data]
        
        return {
            "week_ending": latest_week,
            "total_stocks": len(week_data),
            "market_summary": {
                "avg_weekly_return": round(sum(returns) / len(returns), 2) if returns else 0,
                "median_return": round(sorted(returns)[len(returns)//2], 2) if returns else 0,
                "advances": advances,
                "declines": declines,
                "unchanged": unchanged,
                "ad_ratio": round(advances / max(declines, 1), 2),
                "avg_rsi": round(sum(rsi_values) / len(rsi_values), 1) if rsi_values else 50,
                "overbought_count": overbought,
                "oversold_count": oversold,
                "avg_4w_return": round(sum(return_4w) / len(return_4w), 2) if return_4w else 0,
                "avg_13w_return": round(sum(return_13w) / len(return_13w), 2) if return_13w else 0
            },
            "trend_distribution": {
                "up": trend_up,
                "down": trend_down,
                "sideways": trend_sideways
            },
            "sector_performance": sector_perf,
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "source": "weekly_analysis"
        }
        
    except Exception as e:
        logger.error(f"Error fetching NIFTY 200 weekly summary: {e}")
        return {"error": str(e)}


def get_nifty200_monthly_summary() -> Dict[str, Any]:
    """
    Get aggregated monthly summary for all NIFTY 200 stocks.
    
    Uses monthly_analysis table to compute:
    - Monthly returns and YTD
    - 3M/6M/12M performance
    - Trend distribution
    
    Returns:
        Dict with comprehensive NIFTY 200 monthly summary
    """
    client = _get_supabase_client()
    if not client:
        return {"error": "Supabase not configured"}
    
    try:
        # Get latest month data
        response = client.table("monthly_analysis") \
            .select("*") \
            .order("month", desc=True) \
            .limit(200) \
            .execute()
        
        if not response.data:
            return {"error": "No monthly data available"}
        
        # Get latest month
        latest_month = response.data[0].get("month")
        month_data = [d for d in response.data if d.get("month") == latest_month]
        
        # Compute aggregates
        monthly_returns = [float(d.get("monthly_return_pct", 0) or 0) for d in month_data]
        ytd_returns = [float(d.get("ytd_return_pct", 0) or 0) for d in month_data]
        return_3m = [float(d.get("return_3m", 0) or 0) for d in month_data]
        return_6m = [float(d.get("return_6m", 0) or 0) for d in month_data]
        return_12m = [float(d.get("return_12m", 0) or 0) for d in month_data]
        
        trend_up = sum(1 for d in month_data if d.get("monthly_trend") == "UP")
        trend_down = sum(1 for d in month_data if d.get("monthly_trend") == "DOWN")
        trend_sideways = len(month_data) - trend_up - trend_down
        
        advances = sum(1 for r in monthly_returns if r > 0)
        declines = sum(1 for r in monthly_returns if r < 0)
        
        return {
            "month": latest_month,
            "total_stocks": len(month_data),
            "market_summary": {
                "avg_monthly_return": round(sum(monthly_returns) / len(monthly_returns), 2) if monthly_returns else 0,
                "avg_ytd_return": round(sum(ytd_returns) / len(ytd_returns), 2) if ytd_returns else 0,
                "avg_3m_return": round(sum(return_3m) / len(return_3m), 2) if return_3m else 0,
                "avg_6m_return": round(sum(return_6m) / len(return_6m), 2) if return_6m else 0,
                "avg_12m_return": round(sum(return_12m) / len(return_12m), 2) if return_12m else 0,
                "advances": advances,
                "declines": declines,
                "ad_ratio": round(advances / max(declines, 1), 2)
            },
            "trend_distribution": {
                "up": trend_up,
                "down": trend_down,
                "sideways": trend_sideways
            },
            "source": "monthly_analysis"
        }
        
    except Exception as e:
        logger.error(f"Error fetching NIFTY 200 monthly summary: {e}")
        return {"error": str(e)}


def get_nifty200_seasonality_summary(target_month: Optional[int] = None) -> Dict[str, Any]:
    """
    Get seasonality summary for NIFTY 200 stocks.
    
    Uses seasonality table to compute:
    - Average return for target month across all stocks
    - Stocks where this is best/worst month
    - Sector-level seasonality
    
    Args:
        target_month: Month to analyze (1-12). Defaults to current month.
        
    Returns:
        Dict with seasonality analysis
    """
    client = _get_supabase_client()
    if not client:
        return {"error": "Supabase not configured"}
    
    # Default to current month
    if target_month is None:
        target_month = datetime.now().month
    
    # Month column mapping
    month_cols = {
        1: "jan_avg", 2: "feb_avg", 3: "mar_avg", 4: "apr_avg",
        5: "may_avg", 6: "jun_avg", 7: "jul_avg", 8: "aug_avg",
        9: "sep_avg", 10: "oct_avg", 11: "nov_avg", 12: "dec_avg"
    }
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }
    
    target_col = month_cols.get(target_month, "jan_avg")
    target_name = month_names.get(target_month, "Jan")
    
    try:
        # Get all seasonality data
        response = client.table("seasonality") \
            .select("*") \
            .execute()
        
        if not response.data:
            return {"error": "No seasonality data available"}
        
        data = response.data
        
        # Get sector mapping
        sector_response = client.table("daily_stocks") \
            .select("ticker, sector") \
            .order("date", desc=True) \
            .limit(500) \
            .execute()
        
        sector_map = {}
        if sector_response.data:
            for row in sector_response.data:
                if row.get("ticker") and row.get("sector"):
                    sector_map[row["ticker"]] = row["sector"]
        
        # Compute monthly returns
        month_returns = []
        for d in data:
            val = d.get(target_col)
            if val is not None:
                month_returns.append(float(val))
        
        # Count best/worst
        best_this_month = sum(1 for d in data if d.get("best_month") == target_name)
        worst_this_month = sum(1 for d in data if d.get("worst_month") == target_name)
        
        positive_stocks = sum(1 for r in month_returns if r > 0)
        negative_stocks = sum(1 for r in month_returns if r < 0)
        
        # Get all months for comparison
        all_months_avg = {}
        for m, col in month_cols.items():
            vals = [float(d.get(col, 0) or 0) for d in data if d.get(col) is not None]
            if vals:
                all_months_avg[month_names[m]] = round(sum(vals) / len(vals), 2)
        
        # Sector-level seasonality
        sector_seasonality = {}
        for d in data:
            ticker = d.get("ticker", "")
            sector = sector_map.get(ticker, "Other")
            val = d.get(target_col)
            
            if val is not None:
                if sector not in sector_seasonality:
                    sector_seasonality[sector] = []
                sector_seasonality[sector].append(float(val))
        
        sector_summary = []
        for sector, returns in sector_seasonality.items():
            if returns:
                sector_summary.append({
                    "sector": sector,
                    "avg_return": round(sum(returns) / len(returns), 2),
                    "stocks": len(returns),
                    "positive_pct": round(100 * sum(1 for r in returns if r > 0) / len(returns), 1)
                })
        
        sector_summary.sort(key=lambda x: x["avg_return"], reverse=True)
        
        return {
            "target_month": target_name,
            "target_month_num": target_month,
            "total_stocks": len(data),
            "stocks_with_data": len(month_returns),
            "month_summary": {
                "avg_return": round(sum(month_returns) / len(month_returns), 2) if month_returns else 0,
                "median_return": round(sorted(month_returns)[len(month_returns)//2], 2) if month_returns else 0,
                "positive_stocks": positive_stocks,
                "negative_stocks": negative_stocks,
                "positive_pct": round(100 * positive_stocks / len(month_returns), 1) if month_returns else 0,
                "best_month_count": best_this_month,
                "worst_month_count": worst_this_month
            },
            "all_months_comparison": all_months_avg,
            "sector_seasonality": sector_summary,
            "historical_bias": "bullish" if positive_stocks > negative_stocks * 1.2 else ("bearish" if negative_stocks > positive_stocks * 1.2 else "neutral"),
            "source": "seasonality"
        }
        
    except Exception as e:
        logger.error(f"Error fetching NIFTY 200 seasonality summary: {e}")
        return {"error": str(e)}


def get_sector_weekly_performance() -> Dict[str, Any]:
    """
    Get sector-wise weekly performance for NIFTY 200.
    
    Returns:
        Dict with sector breakdown including returns and breadth
    """
    client = _get_supabase_client()
    if not client:
        return {"error": "Supabase not configured"}
    
    try:
        # Get latest weekly data with sector join
        weekly_response = client.table("weekly_analysis") \
            .select("ticker, weekly_return_pct, weekly_trend, weekly_rsi14") \
            .order("week_ending", desc=True) \
            .limit(200) \
            .execute()
        
        sector_response = client.table("daily_stocks") \
            .select("ticker, sector") \
            .order("date", desc=True) \
            .limit(500) \
            .execute()
        
        if not weekly_response.data or not sector_response.data:
            return {"error": "No data available"}
        
        # Get latest week
        # Build sector map
        sector_map = {}
        for row in sector_response.data:
            if row.get("ticker") and row.get("sector"):
                sector_map[row["ticker"]] = row["sector"]
        
        # Aggregate by sector
        sector_data = {}
        for d in weekly_response.data:
            ticker = d.get("ticker", "")
            sector = sector_map.get(ticker, "Other")
            ret = float(d.get("weekly_return_pct", 0) or 0)
            trend = d.get("weekly_trend", "SIDEWAYS")
            
            if sector not in sector_data:
                sector_data[sector] = {
                    "returns": [],
                    "trends": {"UP": 0, "DOWN": 0, "SIDEWAYS": 0}
                }
            
            sector_data[sector]["returns"].append(ret)
            sector_data[sector]["trends"][trend] = sector_data[sector]["trends"].get(trend, 0) + 1
        
        # Build output
        sectors = []
        for sector, data in sector_data.items():
            returns = data["returns"]
            advances = sum(1 for r in returns if r > 0)
            declines = sum(1 for r in returns if r < 0)
            
            sectors.append({
                "sector": sector,
                "avg_return": round(sum(returns) / len(returns), 2) if returns else 0,
                "stocks": len(returns),
                "advances": advances,
                "declines": declines,
                "ad_ratio": round(advances / max(declines, 1), 2),
                "uptrend_count": data["trends"].get("UP", 0),
                "downtrend_count": data["trends"].get("DOWN", 0)
            })
        
        sectors.sort(key=lambda x: x["avg_return"], reverse=True)
        
        return {
            "sectors": sectors,
            "top_sector": sectors[0]["sector"] if sectors else None,
            "bottom_sector": sectors[-1]["sector"] if sectors else None,
            "source": "weekly_analysis + daily_stocks"
        }
        
    except Exception as e:
        logger.error(f"Error fetching sector performance: {e}")
        return {"error": str(e)}
