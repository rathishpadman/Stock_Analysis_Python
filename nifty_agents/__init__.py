"""
NIFTY Agents - AI-powered stock analysis for Indian equities.

This module provides a multi-agent system for deep-dive stock analysis
using specialized AI agents for fundamental, technical, sentiment,
macro-economic, and regulatory analysis.

Quick Start:
    >>> from nifty_agents import analyze_stock
    >>> report = analyze_stock("RELIANCE")
    >>> print(report["recommendation"])

API Server:
    uvicorn nifty_agents.api:app --reload --port 8000
"""

__version__ = "1.0.0"
__author__ = "Stock Analysis Dashboard"

# Load environment variables from .env.local at package import
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env.local from the nifty_agents directory
_env_file = Path(__file__).parent / ".env.local"
if _env_file.exists():
    load_dotenv(_env_file)

# Also try loading from project root
_root_env = Path(__file__).parent.parent / ".env.local"
if _root_env.exists():
    load_dotenv(_root_env, override=False)

# Convenience imports
from .agents.orchestrator import (
    NiftyAgentOrchestrator,
    analyze_stock,
    analyze_stock_async
)

from .tools.nifty_fetcher import (
    get_stock_fundamentals,
    get_stock_quote,
    get_price_history
)

from .tools.india_macro_fetcher import (
    get_macro_indicators,
    get_india_vix,
    get_rbi_rates
)

from .tools.india_news_fetcher import (
    get_stock_news,
    analyze_sentiment_aggregate,
    get_market_news
)

from .tools.supabase_fetcher import (
    get_stock_scores,
    get_comprehensive_stock_data,
    get_top_stocks
)

__all__ = [
    # Orchestrator
    "NiftyAgentOrchestrator",
    "analyze_stock",
    "analyze_stock_async",
    # Stock data
    "get_stock_fundamentals",
    "get_stock_quote", 
    "get_price_history",
    # Macro data
    "get_macro_indicators",
    "get_india_vix",
    "get_rbi_rates",
    # News & sentiment
    "get_stock_news",
    "analyze_sentiment_aggregate",
    "get_market_news",
    # Supabase data
    "get_stock_scores",
    "get_comprehensive_stock_data",
    "get_top_stocks"
]
