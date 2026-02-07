"""
Tools module for NIFTY Agents.

Contains data fetchers for Indian stock market data:
- nifty_fetcher: Stock price and fundamental data via yfinance/nsetools
- india_macro_fetcher: RBI rates, India VIX, FII/DII flows
- india_news_fetcher: Economic Times RSS, corporate announcements
- supabase_fetcher: Leverage existing scored data from Supabase
"""

from .nifty_fetcher import (
    get_stock_fundamentals,
    get_stock_quote,
    get_price_history,
    get_index_quote,
)
from .india_macro_fetcher import (
    get_macro_indicators,
    get_india_vix,
    get_rbi_rates,
)
from .india_news_fetcher import (
    get_stock_news,
    get_corporate_announcements,
    analyze_sentiment_aggregate,
)
from .supabase_fetcher import (
    get_daily_stock_data,
    get_weekly_analysis,
    get_monthly_analysis,
    get_seasonality_data,
    get_index_weekly_data,
    get_weekly_analysis_enhanced,
)

__all__ = [
    "get_stock_fundamentals",
    "get_stock_quote",
    "get_price_history",
    "get_index_quote",
    "get_macro_indicators",
    "get_india_vix",
    "get_rbi_rates",
    "get_stock_news",
    "get_corporate_announcements",
    "analyze_sentiment_aggregate",
    "get_daily_stock_data",
    "get_weekly_analysis",
    "get_monthly_analysis",
    "get_seasonality_data",
    "get_index_weekly_data",
    "get_weekly_analysis_enhanced",
]
