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
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        logger.warning("Supabase credentials not found in environment")
        return None
    
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None


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
