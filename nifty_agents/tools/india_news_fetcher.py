"""
India News & Sentiment Fetcher

Fetches financial news and corporate announcements for Indian equities:
- Economic Times RSS feeds
- Business Standard feeds
- Moneycontrol news
- BSE/NSE corporate announcements

Performs basic sentiment analysis using keyword matching.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import re

# Try to import feedparser for RSS
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

# Try to import jugaad-data for announcements
try:
    from jugaad_data.nse import NSEHistory
    JUGAAD_NSE_AVAILABLE = True
except ImportError:
    JUGAAD_NSE_AVAILABLE = False

logger = logging.getLogger(__name__)


# RSS Feed URLs for Indian financial news
RSS_FEEDS = {
    "economic_times_markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "economic_times_stocks": "https://economictimes.indiatimes.com/markets/stocks/news/rssfeeds/2146842.cms",
    "economic_times_india": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
    "moneycontrol_markets": "https://www.moneycontrol.com/rss/marketreports.xml",
    "moneycontrol_business": "https://www.moneycontrol.com/rss/business.xml",
    "business_standard_markets": "https://www.business-standard.com/rss/markets-106.rss",
}


# Sentiment keywords for basic analysis
POSITIVE_KEYWORDS = [
    "surge", "rally", "gain", "rise", "up", "high", "profit", "growth",
    "bullish", "outperform", "beat", "strong", "upgrade", "buy", "positive",
    "record", "jump", "soar", "boom", "opportunity", "breakout", "golden",
    "recovery", "expand", "dividend", "bonus", "split", "acquisition"
]

NEGATIVE_KEYWORDS = [
    "fall", "drop", "decline", "crash", "loss", "down", "low", "weak",
    "bearish", "underperform", "miss", "downgrade", "sell", "negative",
    "plunge", "slump", "tumble", "fear", "risk", "warning", "concern",
    "debt", "default", "fraud", "scam", "investigation", "penalty"
]


def _calculate_sentiment_score(text: str) -> Dict[str, Any]:
    """
    Calculate sentiment score using keyword matching.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dict with score (-1 to +1) and sentiment label
    """
    if not text:
        return {"score": 0.0, "sentiment": "neutral", "confidence": 0.0}
    
    text_lower = text.lower()
    
    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    
    total_keywords = positive_count + negative_count
    
    if total_keywords == 0:
        return {"score": 0.0, "sentiment": "neutral", "confidence": 0.0}
    
    # Score from -1 to +1
    score = (positive_count - negative_count) / total_keywords
    confidence = min(total_keywords / 5, 1.0)  # Max confidence at 5+ keywords
    
    if score > 0.2:
        sentiment = "positive"
    elif score < -0.2:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "score": round(score, 2),
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "positive_keywords": positive_count,
        "negative_keywords": negative_count
    }


def fetch_rss_news(
    feed_name: str = "economic_times_markets",
    max_items: int = 20
) -> List[Dict[str, Any]]:
    """
    Fetch news from RSS feed and analyze sentiment.
    
    Args:
        feed_name: Name of the feed from RSS_FEEDS dict
        max_items: Maximum number of items to fetch
        
    Returns:
        List of news items with sentiment analysis
        
    Example:
        >>> news = fetch_rss_news("economic_times_markets", max_items=10)
        >>> for item in news[:3]:
        ...     print(f"{item['title']} - {item['sentiment']['sentiment']}")
    """
    if not FEEDPARSER_AVAILABLE:
        return [{
            "error": "feedparser not installed. Run: pip install feedparser"
        }]
    
    feed_url = RSS_FEEDS.get(feed_name)
    if not feed_url:
        return [{"error": f"Unknown feed: {feed_name}. Available: {list(RSS_FEEDS.keys())}"}]
    
    try:
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:  # feedparser detected an error
            logger.warning(f"Feed parsing issue: {feed.bozo_exception}")
        
        news_items = []
        for entry in feed.entries[:max_items]:
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            
            # Combine title and summary for sentiment
            full_text = f"{title} {summary}"
            sentiment = _calculate_sentiment_score(full_text)
            
            news_item = {
                "title": title,
                "summary": summary[:500] if summary else "",
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": feed_name,
                "sentiment": sentiment
            }
            news_items.append(news_item)
        
        return news_items
        
    except Exception as e:
        logger.error(f"Error fetching RSS feed {feed_name}: {e}")
        return [{"error": f"Failed to fetch feed: {str(e)}"}]


def get_stock_news(
    ticker: str,
    max_items: int = 10
) -> List[Dict[str, Any]]:
    """
    Get news specifically related to a stock.
    
    Searches multiple RSS feeds for mentions of the stock/company.
    
    Args:
        ticker: Stock ticker (e.g., "RELIANCE", "TCS")
        max_items: Maximum items to return
        
    Returns:
        List of relevant news items with sentiment
        
    Example:
        >>> news = get_stock_news("RELIANCE", max_items=5)
        >>> avg_sentiment = sum(n['sentiment']['score'] for n in news) / len(news)
    """
    # Normalize ticker
    ticker_clean = ticker.replace(".NS", "").upper()
    
    # Company name variations to search for
    company_names = {
        "RELIANCE": ["reliance", "ril", "reliance industries", "mukesh ambani"],
        "TCS": ["tcs", "tata consultancy", "tata cs"],
        "INFY": ["infosys", "infy", "narayana murthy"],
        "HDFCBANK": ["hdfc bank", "hdfc", "hdfcbank"],
        "ICICIBANK": ["icici bank", "icici", "icicbank"],
        "WIPRO": ["wipro"],
        "BAJFINANCE": ["bajaj finance", "bajaj finserv", "baj finance"],
        "BHARTIARTL": ["airtel", "bharti airtel", "bharti"],
        "SBIN": ["sbi", "state bank", "sbin"],
        "ITC": ["itc", "itc limited"],
        "KOTAKBANK": ["kotak", "kotak mahindra", "kotak bank"],
        "LT": ["l&t", "larsen", "larsen & toubro"],
        "HINDUNILVR": ["hul", "hindustan unilever", "unilever india"],
        "ASIANPAINT": ["asian paints", "asianpaint"],
        "MARUTI": ["maruti", "maruti suzuki", "msil"],
        "TATAMOTORS": ["tata motors", "tatamotors", "jlr"],
        "SUNPHARMA": ["sun pharma", "sunpharma", "sun pharmaceutical"],
        "AXISBANK": ["axis bank", "axis", "axisbank"],
        "POWERGRID": ["power grid", "powergrid", "pgcil"],
        "TITAN": ["titan", "titan company", "tanishq"],
    }
    
    search_terms = company_names.get(ticker_clean, [ticker_clean.lower()])
    search_terms.append(ticker_clean.lower())  # Always include ticker
    
    relevant_news = []
    
    # Search through feeds
    feeds_to_check = ["economic_times_stocks", "economic_times_markets", "moneycontrol_markets"]
    
    for feed_name in feeds_to_check:
        news = fetch_rss_news(feed_name, max_items=50)
        
        for item in news:
            if "error" in item:
                continue
            
            # Check if any search term appears in title or summary
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            
            for term in search_terms:
                if term in text:
                    item["matched_term"] = term
                    relevant_news.append(item)
                    break
    
    # Remove duplicates by title and sort by relevance
    seen_titles = set()
    unique_news = []
    for item in relevant_news:
        title = item.get("title", "")
        if title not in seen_titles:
            seen_titles.add(title)
            unique_news.append(item)
    
    # Sort by sentiment confidence (most confident first)
    unique_news.sort(
        key=lambda x: x.get("sentiment", {}).get("confidence", 0),
        reverse=True
    )
    
    return unique_news[:max_items]


def get_market_news(max_items: int = 20) -> Dict[str, Any]:
    """
    Get general market news with sentiment summary.
    
    Returns:
        Dict with news items and overall market sentiment
    """
    all_news = []
    
    # Fetch from multiple sources
    for feed_name in ["economic_times_markets", "moneycontrol_markets"]:
        news = fetch_rss_news(feed_name, max_items=15)
        all_news.extend([n for n in news if "error" not in n])
    
    # Calculate overall sentiment
    sentiments = [n.get("sentiment", {}).get("score", 0) for n in all_news]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    
    if avg_sentiment > 0.2:
        overall_sentiment = "bullish"
    elif avg_sentiment < -0.2:
        overall_sentiment = "bearish"
    else:
        overall_sentiment = "neutral"
    
    return {
        "news_items": all_news[:max_items],
        "total_items": len(all_news),
        "average_sentiment_score": round(avg_sentiment, 2),
        "overall_sentiment": overall_sentiment,
        "timestamp": datetime.now().isoformat()
    }


def get_corporate_announcements(
    ticker: str,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get corporate announcements for a stock from NSE.
    
    Fetches:
    - Board meeting outcomes
    - Financial results
    - Corporate actions (dividends, bonuses, splits)
    - Material events
    
    Args:
        ticker: Stock ticker (e.g., "RELIANCE")
        days: Number of days to look back
        
    Returns:
        List of corporate announcements
    """
    ticker_clean = ticker.replace(".NS", "").upper()
    
    if not JUGAAD_NSE_AVAILABLE:
        return [{
            "error": "jugaad-data not installed. Run: pip install jugaad-data",
            "ticker": ticker_clean
        }]
    
    try:
        from_date = datetime.now() - timedelta(days=days)
        to_date = datetime.now()
        
        # This is a placeholder - jugaad-data has limited announcement support
        # In production, you might need to scrape NSE directly
        return [{
            "info": "Corporate announcement fetching via jugaad-data is limited",
            "suggestion": "Use NSE website for detailed announcements",
            "ticker": ticker_clean,
            "nse_url": f"https://www.nseindia.com/get-quotes/equity?symbol={ticker_clean}",
            "timestamp": datetime.now().isoformat()
        }]
        
    except Exception as e:
        logger.error(f"Error fetching announcements for {ticker}: {e}")
        return [{"error": str(e), "ticker": ticker_clean}]


def analyze_sentiment_aggregate(
    ticker: str
) -> Dict[str, Any]:
    """
    Aggregate sentiment analysis for a stock.
    
    Combines:
    - News sentiment from RSS feeds
    - Number of positive/negative mentions
    - Sentiment trend (if historical data available)
    
    Args:
        ticker: Stock ticker
        
    Returns:
        Comprehensive sentiment analysis
        
    Example:
        >>> sentiment = analyze_sentiment_aggregate("TCS")
        >>> print(f"Sentiment: {sentiment['overall_sentiment']}")
        >>> print(f"Confidence: {sentiment['confidence']}")
    """
    ticker_clean = ticker.replace(".NS", "").upper()
    
    # Get stock-specific news
    stock_news = get_stock_news(ticker_clean, max_items=15)
    
    if not stock_news:
        return {
            "ticker": ticker_clean,
            "overall_sentiment": "neutral",
            "confidence": 0.0,
            "reason": "No news found for this stock",
            "news_count": 0,
            "timestamp": datetime.now().isoformat()
        }
    
    # Calculate aggregate sentiment
    scores = [n.get("sentiment", {}).get("score", 0) for n in stock_news]
    avg_score = sum(scores) / len(scores)
    
    positive_news = sum(1 for s in scores if s > 0.2)
    negative_news = sum(1 for s in scores if s < -0.2)
    neutral_news = len(scores) - positive_news - negative_news
    
    # Determine overall sentiment
    if avg_score > 0.3:
        overall = "very_positive"
    elif avg_score > 0.1:
        overall = "positive"
    elif avg_score > -0.1:
        overall = "neutral"
    elif avg_score > -0.3:
        overall = "negative"
    else:
        overall = "very_negative"
    
    # Calculate confidence based on news volume
    confidence = min(len(stock_news) / 10, 1.0)
    
    return {
        "ticker": ticker_clean,
        "overall_sentiment": overall,
        "sentiment_score": round(avg_score, 2),
        "confidence": round(confidence, 2),
        "news_count": len(stock_news),
        "positive_mentions": positive_news,
        "negative_mentions": negative_news,
        "neutral_mentions": neutral_news,
        "recent_headlines": [n.get("title") for n in stock_news[:5]],
        "timestamp": datetime.now().isoformat()
    }


def get_sector_news(sector: str, max_items: int = 15) -> Dict[str, Any]:
    """
    Get news for a specific sector.
    
    Args:
        sector: Sector name (e.g., "banking", "it", "pharma")
        
    Returns:
        Dict with sector news and sentiment
    """
    sector_keywords = {
        "banking": ["bank", "rbi", "credit", "loan", "npa", "deposit", "interest rate"],
        "it": ["it", "software", "tech", "digital", "cloud", "ai", "saas", "outsourcing"],
        "pharma": ["pharma", "drug", "fda", "healthcare", "medicine", "biotech"],
        "auto": ["auto", "car", "vehicle", "ev", "electric vehicle", "automobile"],
        "fmcg": ["fmcg", "consumer", "retail", "food", "beverage"],
        "energy": ["oil", "gas", "energy", "power", "electricity", "renewable"],
        "metal": ["steel", "metal", "mining", "aluminum", "copper"],
        "infra": ["infrastructure", "construction", "real estate", "cement"],
        "telecom": ["telecom", "5g", "spectrum", "broadband", "mobile"],
    }
    
    keywords = sector_keywords.get(sector.lower(), [sector.lower()])
    
    all_news = []
    for feed_name in ["economic_times_markets", "economic_times_stocks"]:
        news = fetch_rss_news(feed_name, max_items=50)
        
        for item in news:
            if "error" in item:
                continue
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            if any(kw in text for kw in keywords):
                all_news.append(item)
    
    # Calculate sector sentiment
    sentiments = [n.get("sentiment", {}).get("score", 0) for n in all_news]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    
    return {
        "sector": sector,
        "news_items": all_news[:max_items],
        "news_count": len(all_news),
        "sentiment_score": round(avg_sentiment, 2),
        "timestamp": datetime.now().isoformat()
    }
