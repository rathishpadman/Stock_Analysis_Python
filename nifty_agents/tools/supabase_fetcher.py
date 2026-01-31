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
