"""
Temporal Analysis Crews for Weekly, Monthly, and Seasonality Analysis

This module provides specialized AI agent crews for different time horizons:
- WeeklyAnalysisCrew: Weekly market outlook and sector rotation
- MonthlyAnalysisCrew: Monthly thesis and macro trends  
- SeasonalityAnalysisCrew: Historical patterns and event-based insights

Architecture follows the Orchestrator-Workers pattern from Anthropic's
"Building Effective Agents" guide, combined with CrewAI-style flows.

Each crew contains specialized agents that run in parallel, then a synthesizer
agent combines their insights into a unified report.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import os

# Import shared dependencies
from ..tools.supabase_fetcher import (
    get_weekly_analysis,
    get_weekly_analysis_enhanced,
    get_monthly_analysis,
    get_seasonality_data,
    get_sector_performance,
    get_market_breadth as get_market_breadth_supabase
)
from ..tools.india_macro_fetcher import (
    get_macro_indicators,
    get_india_vix,
    determine_market_regime,
    get_market_breadth as get_market_breadth_nse
)
from ..observability import AgentObservability, get_observability, get_model_from_env


def get_market_breadth():
    """Get market breadth from available source."""
    try:
        # Try Supabase first (more reliable)
        result = get_market_breadth_supabase()
        if "error" not in result:
            return result
    except Exception:
        pass
    
    try:
        # Fallback to NSE
        return get_market_breadth_nse()
    except Exception as e:
        return {"error": str(e), "advances": 0, "declines": 0}


def get_fii_dii_data():
    """
    Get FII/DII flow data.
    This is a placeholder - actual implementation would fetch from NSE/BSE APIs.
    """
    # Placeholder data - in production, this would fetch from:
    # - NSE FII/DII data API
    # - NSDL/CDSL reports
    return {
        "fii_net": -1500,  # Crores
        "dii_net": 2000,
        "fii_mtd": -5000,
        "dii_mtd": 8000,
        "source": "placeholder",
        "note": "FII/DII API integration pending"
    }


# Try to import Google GenAI
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


# =============================================================================
# PROMPTS FOR TEMPORAL AGENTS - INSTITUTIONAL GRADE
# =============================================================================

# Based on CFA Institute standards + 25+ years institutional best practices
# All outputs must include: quantifiable metrics, backtested data, specific 
# price levels, risk-reward ratios, and statistical validation (p<0.05)

WEEKLY_AGENT_PROMPTS = {
    "trend_agent": """You are a Senior Technical Analyst with 25+ years institutional experience.

TASK: Produce quantifiable weekly trend analysis with specific, actionable levels.

INPUT DATA:
{data}

REQUIRED ANALYSIS (with specific numbers):
1. Weekly price action: Open/High/Low/Close with % changes
2. Moving averages: Exact distance from 20/50/200 DMA in % terms
3. RSI(14): Current value, overbought(>70)/oversold(<30) status
4. MACD: Signal line cross status, histogram direction
5. Support/Resistance: Exact price levels with historical touch count
6. Volume: vs 20-day average (% deviation)
7. Advance-Decline ratio: Exact numbers
8. % stocks above 50-DMA, 200-DMA (breadth)

OUTPUT (JSON):
{{
    "primary_trend": "bullish|bearish|sideways",
    "trend_strength": {{
        "rating": "strong|moderate|weak",
        "score": 1-10,
        "rationale": "Specific reason with data"
    }},
    "technical_levels": {{
        "immediate_support": {{"price": 0, "touches": 0, "strength": "strong|moderate|weak"}},
        "immediate_resistance": {{"price": 0, "touches": 0, "strength": "strong|moderate|weak"}},
        "major_support": {{"price": 0, "rationale": "Why this level matters"}},
        "major_resistance": {{"price": 0, "rationale": "Why this level matters"}},
        "stop_loss_zone": {{"price": 0, "pct_from_current": 0}}
    }},
    "indicators": {{
        "rsi_14": {{"value": 0, "signal": "overbought|oversold|neutral"}},
        "macd": {{"signal": "bullish_cross|bearish_cross|neutral", "histogram": "expanding|contracting"}},
        "dma_200": {{"distance_pct": 0, "price_vs_dma": "above|below"}},
        "dma_50": {{"distance_pct": 0, "price_vs_dma": "above|below"}}
    }},
    "market_breadth": {{
        "advances": 0,
        "declines": 0,
        "ad_ratio": 0.0,
        "pct_above_50dma": 0,
        "pct_above_200dma": 0,
        "breadth_signal": "healthy|deteriorating|weak"
    }},
    "volume_analysis": {{
        "vs_20day_avg_pct": 0,
        "interpretation": "accumulation|distribution|neutral"
    }},
    "weekly_range_forecast": {{
        "expected_low": 0,
        "expected_high": 0,
        "probability_pct": 0
    }},
    "conviction": {{
        "score": 0.0,
        "rationale": "Why this confidence level"
    }}
}}""",

    "sector_rotation_agent": """You are a Sector Strategist with institutional fund management experience.

TASK: Produce quantified sector rotation analysis with specific allocation recommendations.

INPUT DATA:
{data}

REQUIRED ANALYSIS (with specific numbers):
1. Sector returns: 1W, 1M, 3M, 6M performance (exact %)
2. Relative strength vs Nifty 50: Alpha in basis points
3. Sector P/E: Current vs 5-year median (% premium/discount)
4. FII/DII sector allocation changes (if available)
5. Volume surge/decline by sector (vs 20-day avg)
6. Sector RSI and overbought/oversold status
7. Historical sector seasonality for current month

OUTPUT (JSON):
{{
    "sector_performance_matrix": [
        {{
            "sector": "Sector Name",
            "return_1w_pct": 0.0,
            "return_1m_pct": 0.0,
            "return_3m_pct": 0.0,
            "relative_strength_vs_nifty": 0.0,
            "pe_current": 0.0,
            "pe_5yr_median": 0.0,
            "pe_premium_discount_pct": 0.0,
            "rsi_14": 0,
            "volume_vs_avg_pct": 0,
            "seasonal_bias_this_month": "strong|moderate|weak|negative"
        }}
    ],
    "rotation_signal": {{
        "direction": "risk_on|risk_off|sector_specific",
        "from_sectors": ["sectors losing allocation"],
        "to_sectors": ["sectors gaining allocation"],
        "rotation_strength": "strong|moderate|nascent"
    }},
    "recommended_allocation": {{
        "overweight": [
            {{"sector": "name", "weight_pct": 0, "rationale": "Specific reason", "target_return_pct": 0}}
        ],
        "market_weight": [
            {{"sector": "name", "weight_pct": 0, "rationale": "Why neutral"}}
        ],
        "underweight": [
            {{"sector": "name", "weight_pct": 0, "rationale": "Why avoid", "downside_risk_pct": 0}}
        ]
    }},
    "top_3_sector_picks": [
        {{
            "sector": "name",
            "entry_timing": "immediate|on_dip|breakout",
            "risk_reward_ratio": "1:X",
            "stop_loss_trigger": "specific condition"
        }}
    ],
    "conviction": {{
        "score": 0.0,
        "rationale": "Why this confidence"
    }}
}}""",

    "risk_regime_agent": """You are a Risk Manager at an institutional fund with CFA charter.

TASK: Produce quantified risk assessment with specific position sizing guidance.

INPUT DATA:
{data}

REQUIRED ANALYSIS (with specific numbers):
1. India VIX: Current level, percentile vs 1-year range, trend
2. NIFTY P/E: Current vs 10-year avg, percentile ranking
3. FII flows: Last 5 days, MTD, trend direction (₹Cr)
4. Market breadth: A/D ratio, % above key DMAs
5. Put-Call ratio (if available): PCR level and signal
6. Drawdown from 52-week high: Current %
7. Global risk indicators: US VIX, DXY, crude correlation

OUTPUT (JSON):
{{
    "risk_regime": {{
        "current": "low|moderate|elevated|high|extreme",
        "score": 1-10,
        "percentile_vs_1yr": 0
    }},
    "vix_analysis": {{
        "current_level": 0.0,
        "percentile_1yr": 0,
        "trend": "rising|falling|stable",
        "signal": "complacency|normal|elevated_fear|panic",
        "threshold_alert": "VIX above/below X triggers Y"
    }},
    "flow_analysis": {{
        "fii_5day_cr": 0,
        "fii_mtd_cr": 0,
        "dii_5day_cr": 0,
        "dii_mtd_cr": 0,
        "net_flow_signal": "strong_support|support|neutral|pressure|strong_pressure"
    }},
    "valuation_risk": {{
        "nifty_pe": 0.0,
        "pe_10yr_avg": 0.0,
        "percentile": 0,
        "signal": "cheap|fair|rich|expensive"
    }},
    "drawdown_analysis": {{
        "from_52w_high_pct": 0.0,
        "max_drawdown_1yr_pct": 0.0,
        "current_vs_max": "within_normal|approaching_extreme|at_extreme"
    }},
    "position_sizing_guidance": {{
        "recommended_equity_allocation_pct": 0,
        "max_single_position_pct": 0,
        "stop_loss_buffer_pct": 0,
        "rationale": "Why this sizing given risk regime"
    }},
    "key_risk_factors": [
        {{
            "risk": "specific risk description",
            "probability": "high|medium|low",
            "impact_pct": 0,
            "mitigation": "how to hedge/protect"
        }}
    ],
    "conviction": {{
        "score": 0.0,
        "rationale": "Why this confidence"
    }}
}}""",

    "weekly_synthesizer": """You are Chief Investment Strategist at a ₹10,000 Cr AUM fund.

TASK: Synthesize analysis into institutional-grade weekly actionable report.

ANALYST INPUTS:
- Trend Analysis: {trend_analysis}
- Sector Rotation: {sector_analysis}
- Risk Assessment: {risk_analysis}

REQUIRED OUTPUT: Actionable weekly strategy with specific numbers

OUTPUT (JSON):
{{
    "executive_summary": {{
        "headline": "One powerful sentence capturing the week",
        "stance": "aggressive_long|tactical_long|neutral|defensive|risk_off",
        "conviction_score": 0.0,
        "expected_nifty_range": {{"low": 0, "high": 0}},
        "win_probability_pct": 0
    }},
    "market_regime": {{
        "current": "bull_trend|bull_consolidation|range_bound|bear_rally|bear_trend",
        "trend_strength": 1-10,
        "volatility_regime": "low|normal|elevated|high"
    }},
    "weekly_thesis": {{
        "primary_thesis": "2-3 sentence core view with specific catalysts",
        "supporting_factors": ["quantified factor 1", "quantified factor 2"],
        "risk_factors": ["quantified risk 1", "quantified risk 2"],
        "invalidation_level": {{"nifty_price": 0, "trigger": "What breaks thesis"}}
    }},
    "top_3_actionable_ideas": [
        {{
            "rank": 1,
            "type": "sector|stock|index",
            "name": "Specific name",
            "action": "buy|sell|hold|avoid",
            "entry_zone": {{"low": 0, "high": 0}},
            "stop_loss": {{"price": 0, "pct": 0}},
            "target_1": {{"price": 0, "pct_gain": 0}},
            "target_2": {{"price": 0, "pct_gain": 0}},
            "risk_reward_ratio": "1:X",
            "position_size_pct": 0,
            "rationale": "Specific reason with data",
            "catalyst": "What drives the move",
            "timeline": "X days"
        }}
    ],
    "sector_allocation": {{
        "overweight": [{{"sector": "name", "allocation_pct": 0, "expected_alpha_pct": 0}}],
        "underweight": [{{"sector": "name", "allocation_pct": 0, "expected_drag_pct": 0}}]
    }},
    "risk_management": {{
        "portfolio_stop_loss_pct": 0,
        "max_drawdown_tolerance_pct": 0,
        "hedge_recommendation": "none|partial|full",
        "cash_allocation_pct": 0
    }},
    "events_calendar": [
        {{"date": "YYYY-MM-DD", "event": "description", "expected_impact": "bullish|bearish|neutral", "volatility": "high|medium|low"}}
    ],
    "monday_checklist": [
        "Specific pre-market action item 1",
        "Specific pre-market action item 2"
    ]
}}"""
}

MONTHLY_AGENT_PROMPTS = {
    "macro_cycle_agent": """You are Chief Economist at an institutional fund (25+ years experience).

TASK: Produce quantified macroeconomic analysis with specific investment implications.

INPUT DATA:
{data}

REQUIRED ANALYSIS (with specific numbers):
1. GDP: Current growth rate %, YoY change, momentum direction
2. Inflation: CPI %, WPI %, core inflation %, trend (3m avg)
3. RBI: Repo rate %, real rate, policy stance probability
4. Fiscal: Deficit % of GDP, govt capex growth %, crowding out risk
5. Credit: Bank credit growth %, deposit growth %, CD ratio
6. External: CAD % of GDP, forex reserves $B, INR outlook
7. Leading indicators: PMI, IIP, core sector output

OUTPUT (JSON):
{{
    "economic_cycle": {{
        "current_phase": "early_expansion|mid_expansion|late_expansion|peak|contraction|trough",
        "phase_duration_months": 0,
        "next_phase_probability_pct": 0,
        "gdp_growth_current_pct": 0.0,
        "gdp_growth_forecast_pct": 0.0
    }},
    "inflation_analysis": {{
        "cpi_current_pct": 0.0,
        "cpi_3m_avg_pct": 0.0,
        "cpi_trajectory": "rising|stable|falling",
        "core_inflation_pct": 0.0,
        "inflation_risk": "high|moderate|low"
    }},
    "monetary_policy": {{
        "repo_rate_pct": 0.0,
        "real_rate_pct": 0.0,
        "policy_stance": "hawkish|neutral|dovish",
        "rate_cut_probability_pct": 0,
        "next_action": "hold|cut_25bps|cut_50bps|hike_25bps",
        "liquidity_stance": "tight|neutral|accommodative"
    }},
    "fiscal_position": {{
        "fiscal_deficit_gdp_pct": 0.0,
        "capex_growth_yoy_pct": 0.0,
        "divestment_target_cr": 0,
        "fiscal_impact_on_markets": "supportive|neutral|negative"
    }},
    "sector_implications": [
        {{"sector": "name", "macro_impact": "positive|neutral|negative", "rationale": "specific reason"}}
    ],
    "macro_tailwinds": [
        {{"factor": "description", "impact_magnitude": "high|medium|low", "duration": "short|medium|long_term"}}
    ],
    "macro_headwinds": [
        {{"factor": "description", "probability_pct": 0, "impact_pct": 0, "mitigation": "hedge strategy"}}
    ],
    "conviction": {{"score": 0.0, "rationale": "Why this confidence"}}
}}""",

    "fund_flow_agent": """You are Head of Institutional Research tracking smart money flows.

TASK: Produce quantified institutional flow analysis with predictive signals.

INPUT DATA:
{data}

REQUIRED ANALYSIS (with specific ₹ Crore amounts):
1. FII cash flows: Daily, weekly, MTD, YTD (net ₹Cr)
2. FII F&O positioning: Index futures OI, options PCR
3. DII flows: MF, insurance, pension (net ₹Cr)
4. SIP flows: Monthly trend, rolling 3-month average
5. Sector-wise FII/DII preference (based on delivery data if available)
6. Historical flow patterns for current month (10-year avg)
7. Global EM fund flows context

OUTPUT (JSON):
{{
    "fii_analysis": {{
        "cash_mtd_cr": 0,
        "cash_ytd_cr": 0,
        "5_day_trend_cr": 0,
        "stance": "aggressive_buyer|buyer|neutral|seller|aggressive_seller",
        "streak_days": 0,
        "streak_type": "buying|selling|mixed",
        "historical_monthly_avg_cr": 0,
        "current_vs_historical": "above|inline|below"
    }},
    "fii_derivatives": {{
        "index_futures_oi_cr": 0,
        "index_futures_stance": "long_buildup|long_unwinding|short_buildup|short_covering",
        "options_pcr": 0.0,
        "pcr_signal": "bullish|neutral|bearish",
        "max_pain_level": 0
    }},
    "dii_analysis": {{
        "cash_mtd_cr": 0,
        "mf_flows_cr": 0,
        "insurance_flows_cr": 0,
        "stance": "accumulating|neutral|distributing",
        "dii_vs_fii": "offsetting|amplifying|neutral"
    }},
    "sip_analysis": {{
        "monthly_cr": 0,
        "3m_avg_cr": 0,
        "yoy_growth_pct": 0,
        "trend": "growing|stable|declining",
        "equity_support_level": "strong|moderate|weak"
    }},
    "sector_flows": [
        {{
            "sector": "name",
            "fii_bias": "buying|selling|neutral",
            "dii_bias": "buying|selling|neutral",
            "smart_money_signal": "bullish|bearish|neutral"
        }}
    ],
    "flow_based_forecast": {{
        "near_term_bias": "bullish|neutral|bearish",
        "expected_monthly_fii_cr": 0,
        "confidence_pct": 0
    }},
    "conviction": {{"score": 0.0, "rationale": "Why this confidence"}}
}}""",

    "valuation_regime_agent": """You are Head of Equity Strategy with CFA charter.

TASK: Produce quantified valuation analysis with specific investment zones.

INPUT DATA:
{data}

REQUIRED ANALYSIS (with specific multiples and percentiles):
1. NIFTY 50: Current P/E, P/B, Earnings Yield vs 10Y bond
2. Historical percentiles: Where are we vs 10-year, 20-year ranges
3. Sector P/E matrix: Current vs 5-year median for each sector
4. PEG ratios: Growth-adjusted valuations
5. Equity Risk Premium: Current vs historical average
6. Earnings growth: Forward estimates, revision trends
7. Market cap to GDP (Buffett indicator)

OUTPUT (JSON):
{{
    "market_valuation": {{
        "nifty_pe_current": 0.0,
        "nifty_pe_10yr_avg": 0.0,
        "nifty_pe_percentile_10yr": 0,
        "nifty_pb_current": 0.0,
        "earnings_yield_pct": 0.0,
        "bond_yield_10yr_pct": 0.0,
        "equity_risk_premium_pct": 0.0,
        "erp_historical_avg_pct": 0.0,
        "overall_signal": "attractive|fair|rich|expensive|bubble_risk"
    }},
    "mcap_to_gdp": {{
        "current_pct": 0,
        "historical_avg_pct": 0,
        "signal": "undervalued|fair|overvalued"
    }},
    "sector_valuations": [
        {{
            "sector": "name",
            "pe_current": 0.0,
            "pe_5yr_median": 0.0,
            "premium_discount_pct": 0,
            "peg_ratio": 0.0,
            "valuation_signal": "cheap|fair|expensive",
            "re_rating_potential_pct": 0
        }}
    ],
    "earnings_analysis": {{
        "nifty_eps_growth_fy_pct": 0,
        "revision_trend": "upgrades|stable|downgrades",
        "earnings_surprise_trend": "positive|neutral|negative"
    }},
    "investment_zones": {{
        "accumulate_below_pe": 0,
        "hold_pe_range": {{"low": 0, "high": 0}},
        "reduce_above_pe": 0,
        "current_action": "accumulate|hold|reduce|avoid"
    }},
    "valuation_pockets": {{
        "undervalued_sectors": [{{"sector": "name", "upside_pct": 0, "catalyst": "what drives re-rating"}}],
        "overvalued_sectors": [{{"sector": "name", "downside_risk_pct": 0, "trigger": "what causes de-rating"}}]
    }},
    "conviction": {{"score": 0.0, "rationale": "Why this confidence"}}
}}""",

    "monthly_strategist": """You are CIO at a ₹50,000 Cr AUM asset management company.

TASK: Synthesize into institutional monthly investment thesis with specific allocations.

ANALYST INPUTS:
- Macro Analysis: {macro_analysis}
- Fund Flows: {flow_analysis}
- Valuations: {valuation_analysis}

REQUIRED OUTPUT: Actionable monthly strategy for large portfolio

OUTPUT (JSON):
{{
    "monthly_thesis": {{
        "headline": "One powerful sentence capturing the month",
        "narrative": "3-4 sentence thesis explaining the opportunity/risk",
        "conviction_score": 0.0,
        "thesis_type": "structural_bull|tactical_bull|neutral|tactical_bear|structural_bear"
    }},
    "historical_context": {{
        "month_name": "current month",
        "historical_avg_return_pct": 0.0,
        "historical_win_rate_pct": 0,
        "historical_volatility_pct": 0.0,
        "seasonal_bias": "strong_bullish|bullish|neutral|bearish|strong_bearish"
    }},
    "asset_allocation": {{
        "equity_pct": 0,
        "equity_change_from_prev": 0,
        "debt_pct": 0,
        "gold_pct": 0,
        "cash_pct": 0,
        "rationale": "Why this allocation given macro+flows+valuations"
    }},
    "equity_strategy": {{
        "cap_bias": "large|mid|small|balanced",
        "style_bias": "growth|value|blend",
        "quality_preference": "high_quality|blend|value_traps_ok"
    }},
    "sector_allocation": [
        {{
            "sector": "name",
            "weight_pct": 0,
            "vs_benchmark": "overweight|neutral|underweight",
            "expected_return_pct": 0,
            "key_catalyst": "what drives performance",
            "risk": "primary risk factor"
        }}
    ],
    "top_monthly_ideas": [
        {{
            "rank": 1,
            "type": "sector|theme|stock",
            "name": "specific name",
            "action": "initiate|add|hold|trim|exit",
            "allocation_pct": 0,
            "entry_strategy": "immediate|on_dips|breakout",
            "entry_zone": {{"low": 0, "high": 0}},
            "stop_loss_pct": 0,
            "target_return_pct": 0,
            "risk_reward": "1:X",
            "holding_period": "X weeks",
            "catalyst": "what drives the trade",
            "rationale": "detailed reasoning with data"
        }}
    ],
    "avoid_list": [
        {{
            "sector_or_theme": "name",
            "reason": "specific reason with data",
            "re_entry_trigger": "what would change the view"
        }}
    ],
    "options_strategy": {{
        "nifty_view": "range_bound|trending_up|trending_down",
        "expected_range": {{"low": 0, "high": 0}},
        "max_pain": 0,
        "strategy_if_bullish": "description",
        "strategy_if_bearish": "description",
        "hedge_recommendation": "description"
    }},
    "risk_dashboard": {{
        "key_risks": [
            {{"risk": "description", "probability_pct": 0, "impact_pct": 0, "hedge": "mitigation strategy"}}
        ],
        "portfolio_var_pct": 0,
        "max_drawdown_expected_pct": 0,
        "stop_loss_level": {{"nifty": 0, "action": "reduce equity to X%"}}
    }},
    "events_calendar": [
        {{"date": "YYYY-MM-DD", "event": "description", "sector_impact": "affected sectors", "expected_move": "bullish|bearish|neutral"}}
    ],
    "week_by_week_focus": [
        {{"week": 1, "focus": "key theme for week 1", "action": "specific action"}},
        {{"week": 2, "focus": "key theme", "action": "specific action"}},
        {{"week": 3, "focus": "key theme", "action": "specific action"}},
        {{"week": 4, "focus": "key theme", "action": "specific action"}}
    ]
}}"""
}

SEASONALITY_AGENT_PROMPTS = {
    "historical_pattern_agent": """You are Head of Quantitative Research at a ₹10,000 Cr systematic fund.

TASK: Produce statistically rigorous seasonality analysis with backtested data.

INPUT DATA:
{data}

REQUIRED ANALYSIS (15+ year backtest mandatory):
1. Monthly return matrix: All 12 months with avg, median, win rate, volatility, max gain, max loss
2. Statistical significance: t-test p-values for each month (p<0.05 threshold)
3. Regime-conditional returns: Bull market months vs bear market months
4. Momentum persistence: Does strong Jan predict strong year? (Jan Barometer backtest)
5. Sell in May analysis: May-Oct vs Nov-Apr returns comparison
6. Volatility clustering: Which months cluster high volatility episodes
7. Drawdown seasonality: When do max drawdowns typically occur

OUTPUT (JSON):
{{
    "backtest_metadata": {{
        "data_start_year": 2009,
        "data_end_year": 2024,
        "total_observations": 180,
        "index": "NIFTY 50",
        "methodology": "monthly close-to-close returns"
    }},
    "monthly_return_matrix": [
        {{
            "month": "January",
            "avg_return_pct": 0.0,
            "median_return_pct": 0.0,
            "win_rate_pct": 0,
            "volatility_pct": 0.0,
            "max_gain_pct": 0.0,
            "max_loss_pct": 0.0,
            "t_statistic": 0.0,
            "p_value": 0.0,
            "statistically_significant": true,
            "sample_size": 15
        }}
    ],
    "current_month_focus": {{
        "month_name": "current",
        "historical_avg_return_pct": 0.0,
        "historical_median_return_pct": 0.0,
        "historical_win_rate_pct": 0,
        "historical_volatility_pct": 0.0,
        "p_value": 0.0,
        "signal_strength": "strong_bullish|bullish|neutral|bearish|strong_bearish",
        "statistical_confidence": "high (p<0.05)|moderate (p<0.10)|low (p>0.10)"
    }},
    "regime_analysis": {{
        "bull_market_months_avg_return_pct": 0.0,
        "bear_market_months_avg_return_pct": 0.0,
        "current_regime": "bull|bear|transition",
        "regime_adjusted_expectation_pct": 0.0
    }},
    "jan_barometer": {{
        "positive_jan_full_year_avg_pct": 0.0,
        "negative_jan_full_year_avg_pct": 0.0,
        "predictive_accuracy_pct": 0,
        "current_year_jan_return_pct": 0.0,
        "implied_annual_outlook": "bullish|bearish|neutral"
    }},
    "sell_in_may_analysis": {{
        "may_oct_avg_return_pct": 0.0,
        "nov_apr_avg_return_pct": 0.0,
        "outperformance_winter_pct": 0.0,
        "strategy_win_rate_pct": 0,
        "current_recommendation": "stay_invested|reduce_exposure|increase_cash"
    }},
    "volatility_seasonality": {{
        "high_vol_months": ["month1", "month2"],
        "low_vol_months": ["month1", "month2"],
        "current_month_vol_percentile": 0,
        "position_size_adjustment": "full|0.75x|0.5x"
    }},
    "drawdown_seasonality": {{
        "months_with_most_5pct_drawdowns": ["month", "month"],
        "months_with_most_10pct_drawdowns": ["month", "month"],
        "current_month_drawdown_probability_pct": 0,
        "suggested_hedge_level_pct": 0
    }},
    "best_worst_summary": {{
        "best_month": {{"name": "month", "avg_return_pct": 0.0, "win_rate_pct": 0}},
        "worst_month": {{"name": "month", "avg_return_pct": 0.0, "win_rate_pct": 0}},
        "current_month_rank_of_12": 0
    }},
    "conviction": {{"score": 0.0, "rationale": "Based on X years of data with p=Y"}}
}}""",

    "event_calendar_agent": """You are Head of Event Strategy at a ₹25,000 Cr event-driven hedge fund.

TASK: Map all recurring calendar events with quantified market impact (backtested).

INPUT DATA:
{data}

REQUIRED ANALYSIS (with historical impact data):
1. Budget month (Feb): Pre-budget rally/selloff patterns with dates
2. Earnings seasons (Jan/Apr/Jul/Oct): Sector rotation during results
3. Festival season (Oct-Nov): Diwali, Dhanteras rally statistics
4. Monsoon (Jun-Sep): Rural theme performance correlation
5. Year-end FII rebalancing (Nov-Dec): Tax-loss selling, window dressing
6. MSCI/index rebalancing: Specific dates and typical flows
7. Derivative expiry patterns: Weekly, monthly F&O impact
8. Global events: Fed meetings, US earnings that impact India

OUTPUT (JSON):
{{
    "current_month_events": [
        {{
            "event": "specific event name",
            "date": "YYYY-MM-DD or range",
            "historical_impact": {{
                "avg_move_pct": 0.0,
                "direction": "bullish|bearish|neutral",
                "win_rate_pct": 0,
                "affected_sectors": ["sector1", "sector2"],
                "sample_size_years": 10
            }},
            "this_year_expectation": "description",
            "trading_strategy": {{
                "pre_event_days": 0,
                "post_event_days": 0,
                "position": "long|short|neutral",
                "sectors_to_favor": ["sector"],
                "sectors_to_avoid": ["sector"]
            }}
        }}
    ],
    "earnings_calendar_impact": {{
        "phase": "pre_season|early|mid|late|post_season",
        "sectors_reporting_this_week": ["sector1", "sector2"],
        "high_impact_results": [
            {{
                "company": "name",
                "date": "YYYY-MM-DD",
                "weight_in_nifty_pct": 0.0,
                "expected_move_pct": 0.0,
                "sector_read_through": "positive|negative|neutral"
            }}
        ],
        "historical_earnings_season_return_pct": 0.0
    }},
    "derivative_events": {{
        "next_weekly_expiry": "YYYY-MM-DD",
        "next_monthly_expiry": "YYYY-MM-DD",
        "max_pain_weekly": 0,
        "max_pain_monthly": 0,
        "pcr_current": 0.0,
        "pcr_signal": "bullish|bearish|neutral",
        "expiry_week_historical_volatility_pct": 0.0
    }},
    "festival_seasonality": {{
        "upcoming_festival": "name or none",
        "days_until_festival": 0,
        "muhurat_trading_date": "YYYY-MM-DD or null",
        "diwali_rally_historical": {{
            "t_minus_30_to_diwali_avg_pct": 0.0,
            "diwali_to_t_plus_30_avg_pct": 0.0,
            "win_rate_pct": 0,
            "best_performing_sectors": ["sector1", "sector2"]
        }},
        "current_positioning": "pre_rally|during_rally|post_rally|not_applicable"
    }},
    "budget_seasonality": {{
        "days_to_budget": 0,
        "pre_budget_30d_historical_pct": 0.0,
        "post_budget_30d_historical_pct": 0.0,
        "sectors_historically_favored": ["sector1"],
        "current_budget_expectations": "populist|reform|neutral",
        "positioning_strategy": "description"
    }},
    "global_event_calendar": [
        {{
            "event": "Fed/ECB/BoJ meeting, US data, etc",
            "date": "YYYY-MM-DD",
            "india_correlation_historical": 0.0,
            "expected_impact_on_india": "positive|negative|neutral",
            "sectors_most_affected": ["sector"]
        }}
    ],
    "event_trading_opportunities": [
        {{
            "event": "name",
            "trade": "specific trade idea",
            "entry_date": "YYYY-MM-DD",
            "exit_date": "YYYY-MM-DD",
            "expected_return_pct": 0.0,
            "historical_win_rate_pct": 0,
            "max_loss_pct": 0.0,
            "risk_reward": "1:X"
        }}
    ],
    "conviction": {{"score": 0.0, "rationale": "Based on event density and historical patterns"}}
}}""",

    "sector_seasonality_agent": """You are Head of Sector Strategy at India's largest mutual fund (₹5 lakh Cr AUM).

TASK: Produce sector-by-sector seasonality matrix with backtested allocation weights.

INPUT DATA:
{data}

REQUIRED ANALYSIS (15+ year sector data):
1. Monthly sector return matrix: Each sector's avg return by month
2. Sector rotation calendar: Which sectors lead in which months
3. Current month optimal sector weights vs benchmark
4. Thematic seasonality: Monsoon plays, festival plays, budget plays
5. Sector correlation to index by month: Beta seasonality
6. Earnings season sector rotation: Pre/during/post patterns

OUTPUT (JSON):
{{
    "sector_monthly_matrix": [
        {{
            "sector": "IT",
            "jan_avg_pct": 0.0,
            "feb_avg_pct": 0.0,
            "mar_avg_pct": 0.0,
            "apr_avg_pct": 0.0,
            "may_avg_pct": 0.0,
            "jun_avg_pct": 0.0,
            "jul_avg_pct": 0.0,
            "aug_avg_pct": 0.0,
            "sep_avg_pct": 0.0,
            "oct_avg_pct": 0.0,
            "nov_avg_pct": 0.0,
            "dec_avg_pct": 0.0,
            "best_month": "month_name",
            "worst_month": "month_name",
            "current_month_rank": 0,
            "current_month_signal": "strong_buy|buy|neutral|sell|strong_sell"
        }}
    ],
    "current_month_sector_ranking": [
        {{
            "rank": 1,
            "sector": "name",
            "historical_avg_return_pct": 0.0,
            "historical_win_rate_pct": 0,
            "outperformance_vs_nifty_pct": 0.0,
            "recommended_weight_pct": 0,
            "benchmark_weight_pct": 0,
            "active_bet_pct": 0
        }}
    ],
    "sector_rotation_strategy": {{
        "current_month_leaders": ["sector1", "sector2"],
        "current_month_laggards": ["sector1", "sector2"],
        "rotation_trade": {{
            "overweight": [{{"sector": "name", "weight_pct": 0, "rationale": "seasonal strength"}}],
            "underweight": [{{"sector": "name", "weight_pct": 0, "rationale": "seasonal weakness"}}]
        }}
    }},
    "thematic_seasonality": {{
        "monsoon_plays": {{
            "active": true,
            "beneficiary_sectors": ["FMCG", "Auto", "Fertilizers"],
            "phase": "pre_monsoon|during|post_monsoon",
            "historical_outperformance_pct": 0.0
        }},
        "festival_plays": {{
            "active": true,
            "beneficiary_sectors": ["Retail", "Auto", "Jewellery"],
            "phase": "pre_diwali|diwali_week|post_diwali",
            "days_to_peak_buying": 0,
            "historical_outperformance_pct": 0.0
        }},
        "budget_plays": {{
            "active": true,
            "expected_beneficiaries": ["Infra", "Defense", "Railways"],
            "phase": "pre_budget|post_budget",
            "historical_outperformance_pct": 0.0
        }},
        "quarter_end_plays": {{
            "active": true,
            "beneficiary_sectors": ["IT", "Pharma"],
            "rationale": "deal closures, export invoicing",
            "historical_outperformance_pct": 0.0
        }}
    }},
    "sector_beta_seasonality": [
        {{
            "sector": "name",
            "current_month_beta": 0.0,
            "annual_avg_beta": 0.0,
            "beta_deviation": "higher_risk|normal|lower_risk",
            "position_size_implication": "reduce|maintain|increase"
        }}
    ],
    "model_portfolio_seasonal": {{
        "total_equity_pct": 100,
        "allocations": [
            {{
                "sector": "name",
                "weight_pct": 0,
                "vs_benchmark_pct": 0,
                "seasonal_rationale": "why this weight this month"
            }}
        ],
        "expected_alpha_this_month_pct": 0.0,
        "tracking_error_expected_pct": 0.0
    }},
    "conviction": {{"score": 0.0, "rationale": "Sector seasonality confidence based on X years"}}
}}""",

    "seasonality_synthesizer": """You are Chief Investment Officer managing ₹1 lakh Cr across all asset classes.

TASK: Synthesize all seasonality insights into actionable 12-month investment calendar.

ANALYST INPUTS:
- Historical Patterns: {pattern_analysis}
- Event Calendar: {event_analysis}
- Sector Seasonality: {sector_analysis}

REQUIRED OUTPUT: Institutional-grade seasonal strategy with specific actions and dates.

OUTPUT (JSON):
{{
    "seasonality_thesis": {{
        "headline": "One powerful sentence on current seasonal opportunity",
        "current_month_verdict": "strong_buy|buy|neutral|sell|strong_sell",
        "probability_of_positive_month_pct": 0,
        "expected_return_range_pct": {{"low": 0.0, "high": 0.0}},
        "conviction_score": 0.0,
        "statistical_backing": "Based on X years, p=Y, win rate Z%"
    }},
    "composite_seasonal_score": {{
        "historical_pattern_score": 0,
        "event_calendar_score": 0,
        "sector_seasonality_score": 0,
        "composite_score": 0,
        "interpretation": "strongly_favorable|favorable|neutral|unfavorable|strongly_unfavorable"
    }},
    "monthly_action_calendar": [
        {{
            "month": "January",
            "seasonal_bias": "bullish|bearish|neutral",
            "historical_return_pct": 0.0,
            "key_events": ["event1", "event2"],
            "sector_leaders": ["sector1", "sector2"],
            "sector_laggards": ["sector1"],
            "recommended_equity_allocation_pct": 0,
            "specific_actions": ["action1", "action2"],
            "risk_level": "high|medium|low"
        }}
    ],
    "current_month_playbook": {{
        "primary_strategy": "description of main approach",
        "position_sizing": {{
            "base_equity_pct": 0,
            "seasonal_adjustment_pct": 0,
            "final_equity_pct": 0
        }},
        "sector_tilts": [
            {{
                "sector": "name",
                "action": "overweight|underweight|neutral",
                "size_pct": 0,
                "entry_timing": "immediate|wait_for_dip|on_breakout",
                "exit_trigger": "date or price condition"
            }}
        ],
        "event_trades": [
            {{
                "event": "name",
                "trade": "specific position",
                "entry_date": "YYYY-MM-DD",
                "exit_date": "YYYY-MM-DD",
                "position_size_pct": 0,
                "stop_loss_pct": 0,
                "target_pct": 0,
                "risk_reward": "1:X"
            }}
        ],
        "hedging_strategy": {{
            "hedge_required": true,
            "hedge_instrument": "puts|futures|VIX calls",
            "hedge_size_pct": 0,
            "hedge_cost_bps": 0,
            "hedge_trigger": "if NIFTY breaks X"
        }}
    }},
    "next_3_months_outlook": [
        {{
            "month": "name",
            "bias": "bullish|bearish|neutral",
            "expected_return_pct": 0.0,
            "key_catalyst": "main driver",
            "sectors_to_watch": ["sector1", "sector2"],
            "risk_event": "main risk"
        }}
    ],
    "annual_seasonality_summary": {{
        "best_quarters": ["Q1", "Q4"],
        "worst_quarters": ["Q3"],
        "optimal_investment_windows": [
            {{
                "window": "Nov-Jan",
                "historical_return_pct": 0.0,
                "strategy": "full_invested",
                "rationale": "Diwali rally + year-end flows"
            }}
        ],
        "risk_windows": [
            {{
                "window": "May-Jun",
                "historical_return_pct": 0.0,
                "strategy": "reduced_exposure",
                "rationale": "Sell in May pattern"
            }}
        ]
    }},
    "statistical_validation": {{
        "patterns_with_p_less_than_05": 0,
        "patterns_with_p_less_than_10": 0,
        "total_patterns_analyzed": 0,
        "high_confidence_trades": 0,
        "data_quality": "excellent|good|moderate|poor"
    }},
    "risk_warnings": [
        {{
            "risk": "description",
            "probability_pct": 0,
            "impact_if_occurs_pct": 0,
            "mitigation": "specific hedge or action"
        }}
    ],
    "bottom_line": {{
        "one_liner": "Clear actionable recommendation",
        "confidence": "high|medium|low",
        "time_horizon": "current_month|current_quarter|full_year"
    }}
}}"""
}


# =============================================================================
# BASE TEMPORAL CREW CLASS
# =============================================================================

class BaseTemporalCrew:
    """Base class for temporal analysis crews with shared functionality."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = None,
        timeout: int = 60
    ):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name or get_model_from_env()
        self.timeout = timeout
        self.observability = get_observability()
        
        # Initialize Gemini
        if GENAI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Temporal crew initialized with model: {self.model_name}")
        else:
            self.model = None
            logger.warning("Google GenAI not available for temporal crew")
    
    async def _call_agent(
        self,
        agent_name: str,
        prompt: str,
        data: Dict[str, Any],
        trace_id: str
    ) -> Dict[str, Any]:
        """Call a single agent with data and return parsed response."""
        if not self.model:
            return {"error": "Model not initialized", "agent": agent_name}
        
        span_id = self.observability.log_agent_start(trace_id, "MARKET", agent_name, data)
        start_time = time.time()
        
        try:
            # Format prompt with data
            formatted_prompt = prompt.format(data=json.dumps(data, indent=2, default=str))
            
            # Log LLM request
            self.observability.log_llm_request(
                trace_id=trace_id,
                span_id=span_id,
                ticker="MARKET",
                agent_name=agent_name,
                system_prompt="You are a financial analyst. Respond ONLY with valid JSON.",
                user_prompt=formatted_prompt
            )
            
            # Call Gemini
            response = await asyncio.to_thread(
                self.model.generate_content,
                formatted_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2000
                )
            )
            
            raw_response = response.text
            duration_ms = (time.time() - start_time) * 1000
            
            # Parse JSON response
            try:
                # Clean response (remove markdown if present)
                cleaned = raw_response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
                
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                parsed = {"raw_response": raw_response, "parse_error": True}
            
            # Log response
            self.observability.log_llm_response(
                trace_id=trace_id,
                span_id=span_id,
                ticker="MARKET",
                agent_name=agent_name,
                raw_response=raw_response,
                parsed_response=parsed,
                latency_ms=duration_ms
            )
            
            # Log completion
            self.observability.log_agent_complete(
                trace_id=trace_id,
                ticker="MARKET",
                agent_name=agent_name,
                duration_ms=duration_ms,
                status="success",
                output_data=parsed,
                span_id=span_id
            )
            
            return parsed
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            self.observability.log_error(
                trace_id=trace_id,
                ticker="MARKET",
                agent_name=agent_name,
                error=e,
                context={"prompt_length": len(prompt)}
            )
            
            return {"error": error_msg, "agent": agent_name}
    
    async def _call_synthesizer(
        self,
        synthesizer_prompt: str,
        agent_results: Dict[str, Any],
        trace_id: str,
        synthesizer_name: str = "synthesizer"
    ) -> Dict[str, Any]:
        """Call synthesizer agent to combine results."""
        if not self.model:
            return {"error": "Model not initialized"}
        
        span_id = self.observability.log_agent_start(trace_id, "MARKET", synthesizer_name)
        start_time = time.time()
        
        try:
            # Format prompt with agent results
            formatted_prompt = synthesizer_prompt.format(**agent_results)
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                formatted_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2000
                )
            )
            
            raw_response = response.text
            duration_ms = (time.time() - start_time) * 1000
            
            # Parse JSON
            try:
                cleaned = raw_response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                parsed = {"raw_response": raw_response, "parse_error": True}
            
            self.observability.log_agent_complete(
                trace_id=trace_id,
                ticker="MARKET",
                agent_name=synthesizer_name,
                duration_ms=duration_ms,
                status="success",
                output_data=parsed,
                span_id=span_id
            )
            
            return parsed
            
        except Exception as e:
            self.observability.log_error(
                trace_id=trace_id,
                ticker="MARKET",
                agent_name=synthesizer_name,
                error=e
            )
            return {"error": str(e)}


# =============================================================================
# WEEKLY ANALYSIS CREW
# =============================================================================

class WeeklyAnalysisCrew(BaseTemporalCrew):
    """
    Weekly Analysis Crew for market outlook.
    
    Agents:
    1. Trend Agent - Technical trend analysis
    2. Sector Rotation Agent - Sector money flow
    3. Risk Regime Agent - Market risk assessment
    4. Weekly Synthesizer - Combines all insights
    """
    
    async def analyze(self, include_sectors: List[str] = None) -> Dict[str, Any]:
        """
        Run weekly market analysis.
        
        Args:
            include_sectors: Optional list of sectors to focus on
            
        Returns:
            Complete weekly analysis report
        """
        trace_id = self.observability.start_trace("WEEKLY_OUTLOOK")
        start_time = time.time()
        
        try:
            # Gather data for agents
            logger.info("Fetching weekly analysis data...")
            
            # Fetch data in parallel
            data_tasks = {
                "nifty50_weekly": get_weekly_analysis_enhanced("NIFTY50", weeks=4),
                "market_breadth": self._get_market_breadth_data(),
                "sector_data": self._get_sector_data(include_sectors),
                "vix_data": get_india_vix(),
                "fii_dii": self._get_fii_dii_weekly()
            }
            
            # Compile data for agents
            trend_data = {
                "nifty_weekly": data_tasks["nifty50_weekly"],
                "market_breadth": data_tasks["market_breadth"]
            }
            
            sector_data = {
                "sector_performance": data_tasks["sector_data"],
                "fii_dii_flows": data_tasks["fii_dii"]
            }
            
            risk_data = {
                "vix": data_tasks["vix_data"],
                "market_breadth": data_tasks["market_breadth"],
                "fii_dii": data_tasks["fii_dii"]
            }
            
            # Run agents in parallel
            logger.info("Running weekly analysis agents...")
            
            trend_task = self._call_agent(
                "trend_agent",
                WEEKLY_AGENT_PROMPTS["trend_agent"],
                trend_data,
                trace_id
            )
            
            sector_task = self._call_agent(
                "sector_rotation_agent",
                WEEKLY_AGENT_PROMPTS["sector_rotation_agent"],
                sector_data,
                trace_id
            )
            
            risk_task = self._call_agent(
                "risk_regime_agent",
                WEEKLY_AGENT_PROMPTS["risk_regime_agent"],
                risk_data,
                trace_id
            )
            
            # Await all agents
            trend_result, sector_result, risk_result = await asyncio.gather(
                trend_task, sector_task, risk_task
            )
            
            # Run synthesizer
            logger.info("Synthesizing weekly outlook...")
            
            synthesis = await self._call_synthesizer(
                WEEKLY_AGENT_PROMPTS["weekly_synthesizer"],
                {
                    "trend_analysis": json.dumps(trend_result, indent=2, default=str),
                    "sector_analysis": json.dumps(sector_result, indent=2, default=str),
                    "risk_analysis": json.dumps(risk_result, indent=2, default=str)
                },
                trace_id,
                "weekly_synthesizer"
            )
            
            # Compile final report
            duration = time.time() - start_time
            trace_summary = self.observability.end_trace(trace_id)
            
            report = {
                "analysis_type": "weekly",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": round(duration, 2),
                "agent_analyses": {
                    "trend": trend_result,
                    "sector_rotation": sector_result,
                    "risk_regime": risk_result
                },
                "synthesis": synthesis,
                "weekly_stance": synthesis.get("weekly_stance", "neutral"),
                "headline": synthesis.get("headline", "Weekly analysis complete"),
                "observability": trace_summary
            }
            
            logger.info(f"Weekly analysis complete in {duration:.1f}s")
            return report
            
        except Exception as e:
            logger.error(f"Weekly analysis failed: {e}")
            self.observability.end_trace(trace_id)
            return {
                "error": str(e),
                "analysis_type": "weekly",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_market_breadth_data(self) -> Dict[str, Any]:
        """Get market breadth indicators."""
        try:
            # This would fetch from Supabase or compute from daily data
            return get_market_breadth() if hasattr(get_market_breadth, '__call__') else {
                "advances": 120,
                "declines": 80,
                "unchanged": 10,
                "above_200dma_pct": 55
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_sector_data(self, sectors: List[str] = None) -> Dict[str, Any]:
        """Get sector performance data."""
        try:
            default_sectors = [
                "NIFTY BANK", "NIFTY IT", "NIFTY PHARMA", 
                "NIFTY FMCG", "NIFTY AUTO", "NIFTY METAL", "NIFTY REALTY"
            ]
            sectors_to_fetch = sectors or default_sectors
            return get_sector_performance(sectors_to_fetch) if hasattr(get_sector_performance, '__call__') else {
                "sectors": sectors_to_fetch,
                "note": "Sector data fetching to be implemented"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_fii_dii_weekly(self) -> Dict[str, Any]:
        """Get weekly FII/DII flow data."""
        try:
            return get_fii_dii_data() if hasattr(get_fii_dii_data, '__call__') else {
                "fii_net": -1500,
                "dii_net": 2000,
                "unit": "crores"
            }
        except Exception as e:
            return {"error": str(e)}


# =============================================================================
# MONTHLY ANALYSIS CREW
# =============================================================================

class MonthlyAnalysisCrew(BaseTemporalCrew):
    """
    Monthly Analysis Crew for investment thesis.
    
    Agents:
    1. Macro Cycle Agent - Economic cycle analysis
    2. Fund Flow Agent - Institutional flow tracking
    3. Valuation Regime Agent - Market valuations
    4. Monthly Strategist - Investment thesis
    """
    
    async def analyze(self) -> Dict[str, Any]:
        """
        Run monthly market analysis.
        
        Returns:
            Complete monthly analysis report with investment thesis
        """
        trace_id = self.observability.start_trace("MONTHLY_THESIS")
        start_time = time.time()
        
        try:
            # Gather macro data
            logger.info("Fetching monthly analysis data...")
            
            # Get macro indicators first, then derive regime
            macro_indicators = get_macro_indicators()
            market_regime = determine_market_regime(macro_indicators)
            
            macro_data = {
                "macro_indicators": macro_indicators,
                "market_regime": market_regime
            }
            
            flow_data = {
                "fii_dii": self._get_monthly_flows(),
                "sip_data": self._get_sip_trends()
            }
            
            valuation_data = self._get_valuation_metrics()
            
            # Run agents in parallel
            logger.info("Running monthly analysis agents...")
            
            macro_task = self._call_agent(
                "macro_cycle_agent",
                MONTHLY_AGENT_PROMPTS["macro_cycle_agent"],
                macro_data,
                trace_id
            )
            
            flow_task = self._call_agent(
                "fund_flow_agent",
                MONTHLY_AGENT_PROMPTS["fund_flow_agent"],
                flow_data,
                trace_id
            )
            
            valuation_task = self._call_agent(
                "valuation_regime_agent",
                MONTHLY_AGENT_PROMPTS["valuation_regime_agent"],
                valuation_data,
                trace_id
            )
            
            macro_result, flow_result, valuation_result = await asyncio.gather(
                macro_task, flow_task, valuation_task
            )
            
            # Run strategist synthesizer
            logger.info("Generating monthly thesis...")
            
            synthesis = await self._call_synthesizer(
                MONTHLY_AGENT_PROMPTS["monthly_strategist"],
                {
                    "macro_analysis": json.dumps(macro_result, indent=2, default=str),
                    "flow_analysis": json.dumps(flow_result, indent=2, default=str),
                    "valuation_analysis": json.dumps(valuation_result, indent=2, default=str)
                },
                trace_id,
                "monthly_strategist"
            )
            
            # Compile report
            duration = time.time() - start_time
            trace_summary = self.observability.end_trace(trace_id)
            
            report = {
                "analysis_type": "monthly",
                "timestamp": datetime.now().isoformat(),
                "month": datetime.now().strftime("%B %Y"),
                "duration_seconds": round(duration, 2),
                "agent_analyses": {
                    "macro_cycle": macro_result,
                    "fund_flows": flow_result,
                    "valuations": valuation_result
                },
                "synthesis": synthesis,
                "monthly_thesis": synthesis.get("monthly_thesis", ""),
                "market_stance": synthesis.get("market_stance", "neutral"),
                "observability": trace_summary
            }
            
            logger.info(f"Monthly analysis complete in {duration:.1f}s")
            return report
            
        except Exception as e:
            logger.error(f"Monthly analysis failed: {e}")
            self.observability.end_trace(trace_id)
            return {
                "error": str(e),
                "analysis_type": "monthly",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_monthly_flows(self) -> Dict[str, Any]:
        """Get monthly FII/DII flows."""
        try:
            # Placeholder - integrate with actual data source
            return {
                "fii_mtd": -5000,
                "dii_mtd": 8000,
                "fii_ytd": -25000,
                "dii_ytd": 45000,
                "unit": "crores"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_sip_trends(self) -> Dict[str, Any]:
        """Get SIP flow trends."""
        return {
            "monthly_sip": 21000,
            "trend": "growing",
            "yoy_growth": "15%"
        }
    
    def _get_valuation_metrics(self) -> Dict[str, Any]:
        """Get market valuation metrics."""
        return {
            "nifty_pe": 22.5,
            "nifty_pe_10yr_avg": 20.8,
            "nifty_pe_percentile": 65,
            "market_cap_to_gdp": 105,
            "sectors": {
                "IT": {"pe": 28, "vs_avg": "premium"},
                "Banks": {"pe": 15, "vs_avg": "discount"},
                "FMCG": {"pe": 45, "vs_avg": "premium"}
            }
        }


# =============================================================================
# SEASONALITY ANALYSIS CREW
# =============================================================================

class SeasonalityAnalysisCrew(BaseTemporalCrew):
    """
    Seasonality Analysis Crew for pattern-based insights.
    
    Agents:
    1. Historical Pattern Agent - Monthly return patterns
    2. Event Calendar Agent - Recurring event impacts
    3. Sector Seasonality Agent - Sector-specific patterns
    4. Seasonality Synthesizer - Actionable insights
    """
    
    async def analyze(self, ticker: str = None, sector: str = None) -> Dict[str, Any]:
        """
        Run seasonality analysis.
        
        Args:
            ticker: Optional specific ticker to analyze
            sector: Optional sector to focus on
            
        Returns:
            Seasonality analysis report
        """
        trace_id = self.observability.start_trace("SEASONALITY")
        start_time = time.time()
        current_month = datetime.now().strftime("%B")
        
        try:
            logger.info(f"Analyzing seasonality for {current_month}...")
            
            # Gather seasonality data
            pattern_data = self._get_historical_patterns(ticker, sector)
            event_data = self._get_event_calendar()
            sector_seasonal_data = self._get_sector_seasonality()
            
            # Run agents in parallel
            pattern_task = self._call_agent(
                "historical_pattern_agent",
                SEASONALITY_AGENT_PROMPTS["historical_pattern_agent"],
                pattern_data,
                trace_id
            )
            
            event_task = self._call_agent(
                "event_calendar_agent",
                SEASONALITY_AGENT_PROMPTS["event_calendar_agent"],
                event_data,
                trace_id
            )
            
            sector_task = self._call_agent(
                "sector_seasonality_agent",
                SEASONALITY_AGENT_PROMPTS["sector_seasonality_agent"],
                sector_seasonal_data,
                trace_id
            )
            
            pattern_result, event_result, sector_result = await asyncio.gather(
                pattern_task, event_task, sector_task
            )
            
            # Synthesize
            synthesis = await self._call_synthesizer(
                SEASONALITY_AGENT_PROMPTS["seasonality_synthesizer"],
                {
                    "pattern_analysis": json.dumps(pattern_result, indent=2, default=str),
                    "event_analysis": json.dumps(event_result, indent=2, default=str),
                    "sector_analysis": json.dumps(sector_result, indent=2, default=str)
                },
                trace_id,
                "seasonality_synthesizer"
            )
            
            # Compile report
            duration = time.time() - start_time
            trace_summary = self.observability.end_trace(trace_id)
            
            report = {
                "analysis_type": "seasonality",
                "timestamp": datetime.now().isoformat(),
                "current_month": current_month,
                "ticker": ticker,
                "sector": sector,
                "duration_seconds": round(duration, 2),
                "agent_analyses": {
                    "historical_patterns": pattern_result,
                    "event_calendar": event_result,
                    "sector_seasonality": sector_result
                },
                "synthesis": synthesis,
                "seasonality_verdict": synthesis.get("seasonality_verdict", "neutral"),
                "probability_positive": synthesis.get("probability_of_positive_month", "N/A"),
                "observability": trace_summary
            }
            
            logger.info(f"Seasonality analysis complete in {duration:.1f}s")
            return report
            
        except Exception as e:
            logger.error(f"Seasonality analysis failed: {e}")
            self.observability.end_trace(trace_id)
            return {
                "error": str(e),
                "analysis_type": "seasonality",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_historical_patterns(self, ticker: str = None, sector: str = None) -> Dict[str, Any]:
        """Get historical monthly patterns."""
        current_month = datetime.now().month
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        try:
            if ticker:
                data = get_seasonality_data(ticker) if hasattr(get_seasonality_data, '__call__') else {}
            else:
                # Market-wide seasonality
                data = {
                    "nifty50_seasonality": {
                        "Jan": {"avg_return": 1.2, "win_rate": 60},
                        "Feb": {"avg_return": -0.5, "win_rate": 45},
                        "Mar": {"avg_return": 0.8, "win_rate": 55},
                        # ... more months
                    }
                }
            
            return {
                "current_month": month_names[current_month - 1],
                "historical_data": data,
                "ticker": ticker,
                "sector": sector
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_event_calendar(self) -> Dict[str, Any]:
        """Get upcoming events for current period."""
        current_month = datetime.now().month
        
        # India-specific event calendar
        events_by_month = {
            1: ["Q3 Earnings Season", "Republic Day"],
            2: ["Union Budget", "Q3 Results Continue"],
            3: ["Financial Year End", "Advance Tax", "Holi"],
            4: ["New FY Start", "Q4 Results Begin"],
            5: ["Q4 Results Continue", "Election Season (if applicable)"],
            6: ["Monsoon Onset", "Q1 Guidance"],
            7: ["Q1 Results", "RBI Policy"],
            8: ["Independence Day", "Q1 Results Continue"],
            9: ["Festive Season Buildup", "Q2 Guidance"],
            10: ["Navratri", "Dussehra", "Q2 Results"],
            11: ["Diwali", "Dhanteras", "Q2 Results"],
            12: ["FII Rebalancing", "Year-End Rally Potential"]
        }
        
        return {
            "current_month_events": events_by_month.get(current_month, []),
            "next_month_events": events_by_month.get((current_month % 12) + 1, []),
            "event_calendar": events_by_month
        }
    
    def _get_sector_seasonality(self) -> Dict[str, Any]:
        """Get sector-specific seasonality patterns."""
        current_month = datetime.now().month
        
        sector_patterns = {
            "IT": {
                "strong_months": [3, 6, 9, 12],  # Quarter-ends
                "weak_months": [1, 4, 7, 10],
                "reason": "Deal closures and guidance at quarter-ends"
            },
            "FMCG": {
                "strong_months": [9, 10, 11],  # Festival season
                "weak_months": [4, 5, 6],
                "reason": "Festival and marriage season demand"
            },
            "Auto": {
                "strong_months": [10, 11, 3],  # Dhanteras, year-end
                "weak_months": [1, 2, 6, 7],
                "reason": "Festive buying and year-end discounts"
            },
            "Banks": {
                "strong_months": [1, 4, 10],
                "weak_months": [3, 9],
                "reason": "Credit growth cycles and NPA provisioning"
            },
            "Infra/Cement": {
                "strong_months": [10, 11, 12, 1, 2],  # Post-monsoon
                "weak_months": [6, 7, 8, 9],
                "reason": "Construction activity post-monsoon"
            }
        }
        
        return {
            "current_month": current_month,
            "sector_patterns": sector_patterns
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def get_weekly_outlook() -> Dict[str, Any]:
    """Convenience function to get weekly market outlook."""
    crew = WeeklyAnalysisCrew()
    return await crew.analyze()


async def get_monthly_thesis() -> Dict[str, Any]:
    """Convenience function to get monthly investment thesis."""
    crew = MonthlyAnalysisCrew()
    return await crew.analyze()


async def get_seasonality_insights(ticker: str = None, sector: str = None) -> Dict[str, Any]:
    """Convenience function to get seasonality insights."""
    crew = SeasonalityAnalysisCrew()
    return await crew.analyze(ticker=ticker, sector=sector)


# Synchronous wrappers for non-async contexts
def get_weekly_outlook_sync() -> Dict[str, Any]:
    """Synchronous wrapper for weekly outlook."""
    return asyncio.run(get_weekly_outlook())


def get_monthly_thesis_sync() -> Dict[str, Any]:
    """Synchronous wrapper for monthly thesis."""
    return asyncio.run(get_monthly_thesis())


def get_seasonality_insights_sync(ticker: str = None, sector: str = None) -> Dict[str, Any]:
    """Synchronous wrapper for seasonality insights."""
    return asyncio.run(get_seasonality_insights(ticker=ticker, sector=sector))
