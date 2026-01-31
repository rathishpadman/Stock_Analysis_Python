"""
Agents module for NIFTY stock analysis.

Contains specialized AI agents:
- FundamentalAgent: Analyzes financial health, valuations, growth
- TechnicalAgent: Analyzes price patterns, indicators, trends
- SentimentAgent: Analyzes news, announcements, market mood
- MacroAgent: Analyzes RBI policy, FII/DII flows, VIX
- RegulatoryAgent: Analyzes corporate actions, shareholding
- PredictorAgent: Synthesizes all signals into recommendation

Temporal Analysis Crews (NEW):
- WeeklyAnalysisCrew: Weekly market outlook with trend, sector rotation, risk analysis
- MonthlyAnalysisCrew: Monthly investment thesis with macro, flows, valuations
- SeasonalityAnalysisCrew: Historical patterns and event-driven insights
"""

# Export temporal crews for easy access
try:
    from .temporal_crews import (
        WeeklyAnalysisCrew,
        MonthlyAnalysisCrew,
        SeasonalityAnalysisCrew,
        get_weekly_outlook,
        get_monthly_thesis,
        get_seasonality_insights,
        get_weekly_outlook_sync,
        get_monthly_thesis_sync,
        get_seasonality_insights_sync
    )
    __all__ = [
        "WeeklyAnalysisCrew",
        "MonthlyAnalysisCrew", 
        "SeasonalityAnalysisCrew",
        "get_weekly_outlook",
        "get_monthly_thesis",
        "get_seasonality_insights",
        "get_weekly_outlook_sync",
        "get_monthly_thesis_sync",
        "get_seasonality_insights_sync"
    ]
except ImportError:
    __all__ = []
