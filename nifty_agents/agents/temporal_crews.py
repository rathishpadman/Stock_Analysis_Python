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
# PROMPTS FOR TEMPORAL AGENTS
# =============================================================================

WEEKLY_AGENT_PROMPTS = {
    "trend_agent": """You are a Technical Trend Analyst specializing in weekly patterns for Indian equities.

TASK: Analyze the weekly price data and identify key trends.

INPUT DATA:
{data}

ANALYZE:
1. Weekly price action (open/high/low/close)
2. Moving average positions (20, 50, 200 DMA vs weekly close)
3. RSI and momentum indicators
4. Support and resistance levels
5. Chart patterns forming

OUTPUT (JSON):
{{
    "primary_trend": "bullish|bearish|sideways",
    "trend_strength": "strong|moderate|weak",
    "key_levels": {{
        "support": [level1, level2],
        "resistance": [level1, level2]
    }},
    "moving_average_signal": "bullish|bearish|neutral",
    "momentum_signal": "overbought|oversold|neutral",
    "weekly_outlook": "Short 2-3 sentence summary",
    "confidence": 0.0-1.0
}}""",

    "sector_rotation_agent": """You are a Sector Rotation Analyst for Indian markets.

TASK: Analyze sector performance and identify money flow patterns.

INPUT DATA:
{data}

ANALYZE:
1. Sector-wise weekly returns (NIFTY Bank, IT, Pharma, FMCG, Auto, Metal, Realty, etc.)
2. Relative strength of sectors vs NIFTY 50
3. Volume patterns by sector
4. FII/DII sector preferences
5. Rotation from defensive to cyclical or vice versa

OUTPUT (JSON):
{{
    "leading_sectors": ["sector1", "sector2"],
    "lagging_sectors": ["sector1", "sector2"],
    "rotation_direction": "risk_on|risk_off|neutral",
    "fii_preference": "Description of FII sector preference",
    "recommended_sector_allocation": {{
        "overweight": ["sectors"],
        "underweight": ["sectors"],
        "neutral": ["sectors"]
    }},
    "sector_outlook": "Short summary",
    "confidence": 0.0-1.0
}}""",

    "risk_regime_agent": """You are a Market Risk Analyst for Indian equities.

TASK: Assess the current market risk environment.

INPUT DATA:
{data}

ANALYZE:
1. India VIX level and trend
2. Advance-decline ratio
3. Market breadth (stocks above 200 DMA)
4. FII flow direction (net buyers/sellers)
5. Global risk indicators (if available)

OUTPUT (JSON):
{{
    "risk_regime": "low_risk|moderate_risk|high_risk|extreme_risk",
    "vix_signal": "complacency|normal|fear|panic",
    "market_breadth": "healthy|deteriorating|weak",
    "fii_flow_signal": "bullish|bearish|neutral",
    "risk_adjusted_advice": "Recommendation based on risk",
    "key_risks": ["risk1", "risk2"],
    "confidence": 0.0-1.0
}}""",

    "weekly_synthesizer": """You are a Senior Market Strategist synthesizing weekly analysis.

TASK: Combine insights from multiple analysts into a cohesive weekly outlook.

ANALYST INPUTS:
- Trend Analysis: {trend_analysis}
- Sector Rotation: {sector_analysis}
- Risk Assessment: {risk_analysis}

SYNTHESIZE:
1. Overall market stance for the week
2. Key actionable insights
3. Sectors to focus on
4. Risk management guidance
5. Key events to watch

OUTPUT (JSON):
{{
    "weekly_stance": "bullish|bearish|neutral|cautious",
    "headline": "One-line summary for the week",
    "key_insights": [
        "insight1",
        "insight2",
        "insight3"
    ],
    "sector_focus": {{
        "buy": ["sectors to accumulate"],
        "avoid": ["sectors to reduce"]
    }},
    "risk_guidance": "How to manage risk this week",
    "events_to_watch": ["event1", "event2"],
    "composite_confidence": 0.0-1.0
}}"""
}

MONTHLY_AGENT_PROMPTS = {
    "macro_cycle_agent": """You are a Macro Economist analyzing Indian economic cycles.

TASK: Assess the current macroeconomic environment and its impact on markets.

INPUT DATA:
{data}

ANALYZE:
1. GDP growth trajectory
2. Inflation trends (CPI, WPI)
3. RBI monetary policy stance
4. Fiscal policy indicators
5. Global macro spillovers

OUTPUT (JSON):
{{
    "economic_cycle_phase": "expansion|peak|contraction|trough",
    "inflation_outlook": "rising|stable|falling",
    "rbi_policy_bias": "hawkish|neutral|dovish",
    "growth_momentum": "accelerating|stable|decelerating",
    "macro_tailwinds": ["factor1", "factor2"],
    "macro_headwinds": ["factor1", "factor2"],
    "monthly_macro_outlook": "Summary",
    "confidence": 0.0-1.0
}}""",

    "fund_flow_agent": """You are a Fund Flow Analyst tracking institutional money.

TASK: Analyze FII/DII/MF flows and their market impact.

INPUT DATA:
{data}

ANALYZE:
1. Monthly FII net flows (cash + derivatives)
2. DII net flows (mutual funds + insurance)
3. SIP flow trends
4. IPO/FPO activity
5. Sector-wise institutional preference

OUTPUT (JSON):
{{
    "fii_stance": "accumulating|distributing|neutral",
    "dii_stance": "accumulating|distributing|neutral",
    "sip_trend": "growing|stable|declining",
    "institutional_consensus": "bullish|bearish|mixed",
    "smart_money_sectors": ["sector1", "sector2"],
    "flow_outlook": "Summary of expected flows",
    "confidence": 0.0-1.0
}}""",

    "valuation_regime_agent": """You are a Valuation Analyst for Indian markets.

TASK: Assess market-wide and sector valuations.

INPUT DATA:
{data}

ANALYZE:
1. NIFTY 50 P/E vs historical average
2. Sector P/E multiples vs history
3. Earnings yield vs bond yield (equity risk premium)
4. Market cap to GDP ratio
5. Small/Mid vs Large cap valuations

OUTPUT (JSON):
{{
    "market_valuation": "cheap|fair|expensive|bubble",
    "pe_percentile": "X percentile vs 10-year history",
    "equity_risk_premium": "attractive|neutral|unattractive",
    "valuation_pockets": {{
        "undervalued": ["sectors/themes"],
        "fairly_valued": ["sectors/themes"],
        "overvalued": ["sectors/themes"]
    }},
    "valuation_advice": "Investment guidance based on valuations",
    "confidence": 0.0-1.0
}}""",

    "monthly_strategist": """You are a Chief Investment Strategist creating monthly thesis.

TASK: Synthesize macro, flows, and valuations into monthly investment thesis.

ANALYST INPUTS:
- Macro Analysis: {macro_analysis}
- Fund Flows: {flow_analysis}
- Valuations: {valuation_analysis}

SYNTHESIZE:
1. Overall monthly investment stance
2. Asset allocation guidance
3. Sector/theme recommendations
4. Key risks and mitigants
5. Portfolio positioning advice

OUTPUT (JSON):
{{
    "monthly_thesis": "One paragraph investment thesis",
    "market_stance": "overweight_equity|neutral|underweight_equity",
    "asset_allocation": {{
        "equity": "X%",
        "debt": "Y%",
        "gold": "Z%",
        "cash": "W%"
    }},
    "top_themes": ["theme1", "theme2", "theme3"],
    "avoid_themes": ["theme1", "theme2"],
    "key_risks": ["risk1", "risk2"],
    "action_items": ["action1", "action2"],
    "composite_confidence": 0.0-1.0
}}"""
}

SEASONALITY_AGENT_PROMPTS = {
    "historical_pattern_agent": """You are a Quantitative Analyst specializing in seasonality patterns.

TASK: Analyze historical monthly return patterns.

INPUT DATA:
{data}

ANALYZE:
1. Average returns by month (Jan-Dec)
2. Win rate (% positive months) by month
3. Standard deviation by month
4. Best/worst performing months historically
5. Statistical significance of patterns

OUTPUT (JSON):
{{
    "current_month": "Month name",
    "historical_avg_return": "X%",
    "historical_win_rate": "Y%",
    "pattern_strength": "strong|moderate|weak",
    "statistical_significance": "p < 0.05|not significant",
    "historical_context": "Description of pattern",
    "seasonality_signal": "bullish|bearish|neutral",
    "confidence": 0.0-1.0
}}""",

    "event_calendar_agent": """You are an Event-Driven Analyst for Indian markets.

TASK: Identify recurring events that impact market seasonality.

INPUT DATA:
{data}

ANALYZE:
1. Budget month impact (Feb)
2. Earnings season patterns (Apr, Jul, Oct, Jan)
3. Festival season impact (Oct-Nov: Diwali, Dhanteras)
4. Monsoon dependency (Jun-Sep for rural/FMCG)
5. Year-end FII rebalancing (Dec)
6. Tax-related selling (Mar)

OUTPUT (JSON):
{{
    "upcoming_events": [
        {{"event": "name", "date": "approx date", "expected_impact": "bullish|bearish|neutral"}}
    ],
    "event_driven_sectors": {{
        "positive_impact": ["sectors"],
        "negative_impact": ["sectors"]
    }},
    "event_based_outlook": "Summary",
    "confidence": 0.0-1.0
}}""",

    "sector_seasonality_agent": """You are a Sector Seasonality Specialist.

TASK: Analyze sector-specific seasonal patterns.

INPUT DATA:
{data}

ANALYZE:
1. IT sector: Quarter-end strength (deal closures)
2. FMCG: Festival and marriage season boost
3. Auto: Marriage season, year-end discounts
4. Cement/Infra: Post-monsoon construction pickup
5. Pharma: Seasonal illness patterns
6. Banks: Credit growth cycles

OUTPUT (JSON):
{{
    "sector_seasonality": {{
        "sector_name": {{
            "current_seasonal_phase": "favorable|unfavorable|neutral",
            "historical_pattern": "description",
            "recommendation": "overweight|underweight|neutral"
        }}
    }},
    "top_seasonal_picks": ["sector1", "sector2"],
    "sectors_to_avoid_seasonally": ["sector1"],
    "confidence": 0.0-1.0
}}""",

    "seasonality_synthesizer": """You are a Seasonality Strategist combining pattern insights.

TASK: Create actionable seasonality-based investment guidance.

ANALYST INPUTS:
- Historical Patterns: {pattern_analysis}
- Event Calendar: {event_analysis}
- Sector Seasonality: {sector_analysis}

SYNTHESIZE:
1. Overall seasonality signal
2. Probability-based outlook
3. Sector positioning based on seasonality
4. Event-driven opportunities
5. Risk from seasonal patterns

OUTPUT (JSON):
{{
    "seasonality_verdict": "favorable|unfavorable|neutral",
    "probability_of_positive_month": "X%",
    "seasonal_alpha_opportunity": "Description of opportunity",
    "sector_positioning": {{
        "overweight": ["sectors"],
        "underweight": ["sectors"]
    }},
    "event_opportunities": ["opportunity1", "opportunity2"],
    "seasonal_risks": ["risk1"],
    "actionable_insight": "Clear recommendation",
    "composite_confidence": 0.0-1.0
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
                "nifty50_weekly": get_weekly_analysis("NIFTY50", weeks=4),
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
            
            macro_data = {
                "macro_indicators": get_macro_indicators(),
                "market_regime": determine_market_regime()
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
