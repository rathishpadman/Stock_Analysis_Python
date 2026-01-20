"""
NIFTY Stock Analysis Orchestrator

Coordinates multiple specialized AI agents to perform comprehensive
stock analysis for Indian equities (NSE-listed stocks).

Architecture:
- Uses Google Gemini 2.0 Flash as the LLM backend
- 6 specialized agents run in parallel
- Final synthesis by Predictor agent
- Results cached to reduce API calls
- Full observability with FinOps tracking

Agent Flow:
1. User requests analysis for a ticker (e.g., "RELIANCE")
2. Orchestrator validates ticker and fetches base data
3. 5 specialist agents analyze in parallel:
   - Fundamental Agent: Financials, valuation, quality
   - Technical Agent: Price patterns, indicators, levels
   - Sentiment Agent: News, social sentiment
   - Macro Agent: Economy, RBI policy, VIX
   - Regulatory Agent: Compliance, regulatory risk
4. Predictor Agent synthesizes all analyses
5. Orchestrator compiles final report

Observability:
- Logs: nifty_agents/logs/agent_logs.jsonl
- FinOps: nifty_agents/logs/finops.jsonl  
- Metrics: nifty_agents/logs/metrics.json
"""

# Load environment variables FIRST
from pathlib import Path
from dotenv import load_dotenv

_env_file = Path(__file__).parent.parent / ".env.local"
if _env_file.exists():
    load_dotenv(_env_file)

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Import agent tools
from ..tools.nifty_fetcher import (
    get_stock_fundamentals,
    get_stock_quote,
    get_price_history,
    get_index_quote
)
from ..tools.india_macro_fetcher import (
    get_macro_indicators,
    get_india_vix,
    get_rbi_rates,
    determine_market_regime
)
from ..tools.india_news_fetcher import (
    get_stock_news,
    analyze_sentiment_aggregate,
    get_market_news
)
from ..tools.supabase_fetcher import (
    get_stock_scores,
    get_comprehensive_stock_data,
    get_weekly_analysis,
    get_monthly_analysis
)
from ..config.nifty_prompts import (
    AGENT_CONFIG,
    get_agent_prompt,
    ORCHESTRATOR_SYSTEM_PROMPT
)

# Import observability
from ..observability import AgentObservability, get_observability, agent_logger, get_model_from_env

# Try to import Google GenAI
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class NiftyAgentOrchestrator:
    """
    Orchestrates multi-agent stock analysis for NIFTY stocks.
    
    Example:
        >>> orchestrator = NiftyAgentOrchestrator()
        >>> report = await orchestrator.analyze("RELIANCE")
        >>> print(report["recommendation"])
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = None,  # Now defaults to env var
        enable_caching: bool = True,
        timeout: int = 60
    ):
        """
        Initialize the orchestrator.
        
        Args:
            api_key: Google API key (or set GOOGLE_API_KEY env var)
            model_name: Gemini model to use (or set GEMINI_MODEL env var)
                       Options: gemini-2.0-flash-exp, gemini-1.5-flash, 
                                gemini-1.5-flash-8b, gemini-1.5-pro
            enable_caching: Cache agent responses
            timeout: Timeout in seconds for agent calls
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name or get_model_from_env()
        self.enable_caching = enable_caching
        self.timeout = timeout
        self.cache: Dict[str, Any] = {}
        
        # Initialize observability
        self.observability = get_observability()
        
        # Initialize Gemini
        if GENAI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Initialized with model: {self.model_name}")
        else:
            self.model = None
            logger.warning("Google GenAI not available. Set GOOGLE_API_KEY.")
    
    def _validate_ticker(self, ticker: str) -> Dict[str, Any]:
        """Validate that ticker is a valid NSE stock."""
        ticker_clean = ticker.replace(".NS", "").upper()
        
        # Get quote to validate
        quote = get_stock_quote(ticker_clean)
        
        if "error" in quote:
            return {
                "valid": False,
                "error": f"Invalid ticker: {ticker_clean}",
                "ticker": ticker_clean
            }
        
        return {
            "valid": True,
            "ticker": ticker_clean,
            "name": quote.get("company_name", ticker_clean),
            "current_price": quote.get("last_price")
        }
    
    def _gather_base_data(self, ticker: str) -> Dict[str, Any]:
        """Gather all base data needed for agents."""
        ticker_clean = ticker.replace(".NS", "").upper()
        
        data = {
            "ticker": ticker_clean,
            "timestamp": datetime.now().isoformat()
        }
        
        # Fetch data from various sources (parallel with threads)
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(get_stock_fundamentals, ticker_clean): "fundamentals",
                executor.submit(get_stock_quote, ticker_clean): "quote",
                executor.submit(get_price_history, ticker_clean, 365): "price_history",
                executor.submit(get_macro_indicators): "macro",
                executor.submit(analyze_sentiment_aggregate, ticker_clean): "sentiment",
                executor.submit(get_comprehensive_stock_data, ticker_clean): "supabase_data"
            }
            
            for future in as_completed(futures, timeout=30):
                key = futures[future]
                try:
                    data[key] = future.result()
                except Exception as e:
                    logger.error(f"Error fetching {key}: {e}")
                    data[key] = {"error": str(e)}
        
        return data
    
    def _get_agent_specific_data(
        self,
        agent_name: str,
        base_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Filter base_data to include only what each agent needs.
        
        This optimization reduces token usage by ~54% while preserving
        all critical data paths identified in the agent prompt analysis.
        
        Args:
            agent_name: Name of the agent
            base_data: Full data dictionary from _gather_base_data
            
        Returns:
            Filtered data dictionary specific to the agent's needs
        """
        ticker = base_data.get("ticker", "UNKNOWN")
        quote = base_data.get("quote", {})
        fundamentals = base_data.get("fundamentals", {})
        sentiment = base_data.get("sentiment", {})
        macro = base_data.get("macro", {})
        supabase_data = base_data.get("supabase_data", {})
        price_history = base_data.get("price_history", {})
        
        # Common fields all agents need
        common = {
            "ticker": ticker,
            "timestamp": base_data.get("timestamp"),
            "current_price": quote.get("last_price"),
            "company_name": quote.get("company_name", fundamentals.get("company_name"))
        }
        
        if agent_name == "fundamental_agent":
            # Needs: financials, valuation ratios, quality metrics
            # Prompt mentions: P/E, P/B, ROE, ROCE, Debt/Equity, promoter holding
            return {
                **common,
                "fundamentals": fundamentals,  # Full fundamentals needed
                "quote": {
                    "company_name": quote.get("company_name"),
                    "last_price": quote.get("last_price"),
                    "previous_close": quote.get("previous_close"),
                    "day_change_pct": quote.get("change_percent")
                },
                "scores": supabase_data.get("scores", {}),
                "sector": fundamentals.get("sector"),
                "industry": fundamentals.get("industry")
            }
        
        elif agent_name == "technical_agent":
            # Needs: Price history (50 days for patterns), indicators, volume
            # Prompt mentions: Chart patterns, S/R, MA, RSI, MACD, Volume, Nifty direction
            
            # Extract recent 50 days of price data (not full 250)
            price_data_list = price_history.get("data", [])
            recent_50_days = price_data_list[:50] if isinstance(price_data_list, list) else []
            
            # Extract VIX value safely
            india_vix_data = macro.get("india_vix", {})
            vix_value = india_vix_data.get("value") if isinstance(india_vix_data, dict) else None
            
            return {
                **common,
                # Volume data for volume analysis
                "volume": quote.get("volume"),
                "avg_volume": fundamentals.get("avg_volume"),
                "avg_volume_10d": fundamentals.get("avg_volume_10d"),
                # Recent 50 days for pattern recognition (not 250)
                "price_history": {
                    "data": recent_50_days,
                    "52w_high": price_history.get("52w_high") or quote.get("52w_high"),
                    "52w_low": price_history.get("52w_low") or quote.get("52w_low"),
                    "days_included": len(recent_50_days)
                },
                # Pre-computed indicators from pipeline (avoid LLM recomputing)
                "indicators": {
                    "rsi14": supabase_data.get("scores", {}).get("rsi14"),
                    "macd_signal": supabase_data.get("scores", {}).get("macd_signal"),
                    "sma20": supabase_data.get("daily", {}).get("sma20"),
                    "sma50": supabase_data.get("daily", {}).get("sma50") or fundamentals.get("50d_avg"),
                    "sma200": supabase_data.get("daily", {}).get("sma200") or fundamentals.get("200d_avg"),
                    "technical_score": supabase_data.get("scores", {}).get("score_technical")
                },
                # Market context for "consider Nifty direction"
                "market_regime": macro.get("market_regime"),
                "india_vix": vix_value
            }
        
        elif agent_name == "sentiment_agent":
            # Needs: News headlines, sentiment scores, VIX for fear/greed
            # Prompt mentions: News from ET/Moneycontrol, India VIX, FII/DII, events
            headlines = sentiment.get("headlines", [])
            
            # Extract VIX data safely
            india_vix_data = macro.get("india_vix", {})
            
            # Get sector from fundamentals (required for news filtering)
            sector = fundamentals.get("sector", "Unknown")
            
            return {
                **common,
                "sector": sector,
                "industry": fundamentals.get("industry", "Unknown"),
                "sentiment": {
                    "overall_sentiment": sentiment.get("overall_sentiment"),
                    "sentiment_score": sentiment.get("sentiment_score") or sentiment.get("confidence", 0),
                    "confidence": sentiment.get("confidence"),
                    "positive_count": sentiment.get("positive_count", 0),
                    "negative_count": sentiment.get("negative_count", 0),
                    "news_count": sentiment.get("news_count", 0),
                    "reason": sentiment.get("reason", ""),
                    "headlines": headlines[:10] if isinstance(headlines, list) else [],
                    "top_positive": sentiment.get("top_positive", [])[:3],
                    "top_negative": sentiment.get("top_negative", [])[:3]
                },
                # VIX for fear/greed cycles (full object for context)
                "india_vix": india_vix_data if isinstance(india_vix_data, dict) else {"value": None},
                "market_regime": macro.get("market_regime", "unknown")
            }
        
        elif agent_name == "macro_agent":
            # Needs: Full macro data, sector for connecting to stock
            # Prompt mentions: RBI, VIX, INR, FII, sector impacts
            # NOTE: Does NOT need price_history - macro doesn't analyze charts!
            
            # Get sector/industry (required for sector-specific impacts)
            sector = fundamentals.get("sector", "Unknown")
            industry = fundamentals.get("industry", "Unknown")
            
            return {
                **common,
                # Sector context for "connect macro to sector impacts" (REQUIRED)
                "sector": sector,
                "industry": industry,
                # Full macro data needed for RBI, VIX, etc.
                "macro": macro,
                # Basic valuation for macro overlay
                "pe_ratio": fundamentals.get("pe_ratio"),
                "market_cap": fundamentals.get("market_cap"),
                # Beta for market sensitivity
                "beta": fundamentals.get("beta")
            }
        
        elif agent_name == "regulatory_agent":
            # Needs: Corporate announcements, sector (for regulation type)
            # Prompt mentions: SEBI, RBI circulars, litigations, compliance
            # NOTE: Does NOT need price_history or detailed macro data!
            
            # Get sector/industry (REQUIRED for determining applicable regulations)
            sector = fundamentals.get("sector", "Unknown")
            industry = fundamentals.get("industry", "Unknown")
            
            return {
                **common,
                # Sector/Industry (REQUIRED for regulation type)
                "sector": sector,
                "industry": industry,
                # Company size for regulatory tier (large caps have different requirements)
                "market_cap": fundamentals.get("market_cap"),
                # Corporate announcements for regulatory filings
                "announcements": sentiment.get("announcements", []),
                "corporate_actions": sentiment.get("corporate_actions", []),
                # Scores hint at historical compliance
                "scores": {
                    "composite_score": supabase_data.get("scores", {}).get("composite_score"),
                    "quality_score": supabase_data.get("scores", {}).get("quality_score"),
                    "fundamental_score": supabase_data.get("scores", {}).get("score_fundamental")
                }
            }
        
        # Fallback: return full data (should not happen in normal flow)
        logger.warning(f"Unknown agent {agent_name}, returning full data")
        return base_data
    
    def _clean_for_predictor(
        self,
        agent_analyses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Clean agent analyses before sending to predictor.
        
        Removes:
        - Internal metadata (_agent, _timestamp)
        - Error/raw response fields
        - Verbose reasoning (predictor makes its own)
        
        Args:
            agent_analyses: Dict of all agent responses
            
        Returns:
            Cleaned dict with essential analysis data only
        """
        cleaned = {}
        
        # Fields to exclude from predictor input
        exclude_fields = {"_agent", "_timestamp", "_raw_response", "error", "raw_response"}
        
        for agent_name, analysis in agent_analyses.items():
            if not isinstance(analysis, dict):
                cleaned[agent_name] = analysis
                continue
            
            # Create cleaned version of this agent's output
            agent_key = agent_name.replace("_agent", "")
            cleaned[agent_key] = {
                k: v for k, v in analysis.items()
                if k not in exclude_fields
            }
            
            # Extract key metrics for quick synthesis
            if "reasoning" in cleaned[agent_key]:
                # Truncate verbose reasoning to first 200 chars
                reasoning = cleaned[agent_key]["reasoning"]
                if isinstance(reasoning, str) and len(reasoning) > 200:
                    cleaned[agent_key]["reasoning_summary"] = reasoning[:200] + "..."
                    del cleaned[agent_key]["reasoning"]
        
        return cleaned
    
    def _call_agent(
        self,
        agent_name: str,
        base_data: Dict[str, Any],
        trace_id: str = None
    ) -> Dict[str, Any]:
        """Call a single agent with the gathered data."""
        start_time = time.time()
        ticker = base_data.get('ticker', 'UNKNOWN')
        
        # Log agent start with input data
        span_id = None
        if trace_id:
            span_id = self.observability.log_agent_start(
                trace_id, ticker, agent_name, 
                input_data=base_data
            )
        
        if not self.model:
            return {"error": "GenAI not configured", "agent": agent_name}
        
        config = AGENT_CONFIG.get(agent_name, {})
        system_prompt = config.get("system_prompt", "")
        output_format = config.get("output_format", {})
        temperature = config.get("temperature", 0.3)
        max_tokens = config.get("max_tokens", 2000)
        
        # Get agent-specific data (token optimization)
        agent_data = self._get_agent_specific_data(agent_name, base_data)
        
        # Build the prompt with filtered data
        user_prompt = f"""
Analyze the following stock data and provide your expert analysis.

TICKER: {agent_data.get('ticker')}
COMPANY: {agent_data.get('company_name', 'N/A')}
CURRENT PRICE: {agent_data.get('current_price', 'N/A')}

DATA PROVIDED:
{json.dumps(agent_data, indent=2, default=str)}

Please provide your analysis in the following JSON format:
{json.dumps(output_format, indent=2)}

IMPORTANT: Include a "reasoning" field explaining your analysis logic.
Respond ONLY with valid JSON. No explanatory text outside the JSON.
"""

        
        # Log LLM request
        llm_start_time = time.time()
        if trace_id and span_id:
            self.observability.log_llm_request(
                trace_id=trace_id,
                span_id=span_id,
                ticker=ticker,
                agent_name=agent_name,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        try:
            # Call Gemini
            response = self.model.generate_content(
                [system_prompt, user_prompt],
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            
            llm_latency_ms = (time.time() - llm_start_time) * 1000
            
            # Parse response
            response_text = response.text.strip()
            raw_response = response_text  # Keep original for logging
            
            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Get token counts from response if available
            input_tokens = None
            output_tokens = None
            finish_reason = None
            try:
                if hasattr(response, 'usage_metadata'):
                    input_tokens = getattr(response.usage_metadata, 'prompt_token_count', None)
                    output_tokens = getattr(response.usage_metadata, 'candidates_token_count', None)
                if hasattr(response, 'candidates') and response.candidates:
                    finish_reason = str(response.candidates[0].finish_reason) if hasattr(response.candidates[0], 'finish_reason') else None
            except Exception:
                pass  # Token counting is optional
            
            try:
                parsed = json.loads(response_text)
                parsed["_agent"] = agent_name
                parsed["_timestamp"] = datetime.now().isoformat()
                
                # Log LLM response with full details
                if trace_id and span_id:
                    self.observability.log_llm_response(
                        trace_id=trace_id,
                        span_id=span_id,
                        ticker=ticker,
                        agent_name=agent_name,
                        raw_response=raw_response,
                        parsed_response=parsed,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        latency_ms=llm_latency_ms,
                        finish_reason=finish_reason
                    )
                
                # Log successful completion
                duration_ms = (time.time() - start_time) * 1000
                if trace_id:
                    self.observability.log_agent_complete(
                        trace_id, ticker, agent_name, 
                        duration_ms=duration_ms,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        status="success",
                        output_data=parsed,
                        span_id=span_id
                    )
                
                return parsed
            except json.JSONDecodeError as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Log LLM response even if parsing failed
                if trace_id and span_id:
                    self.observability.log_llm_response(
                        trace_id=trace_id,
                        span_id=span_id,
                        ticker=ticker,
                        agent_name=agent_name,
                        raw_response=raw_response,
                        parsed_response=None,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        latency_ms=llm_latency_ms,
                        finish_reason="parse_error"
                    )
                
                if trace_id:
                    self.observability.log_agent_complete(
                        trace_id, ticker, agent_name,
                        duration_ms=duration_ms,
                        status="error",
                        error_message=f"Failed to parse JSON response: {str(e)}",
                        span_id=span_id
                    )
                return {
                    "_agent": agent_name,
                    "_raw_response": response_text,
                    "error": "Failed to parse JSON response"
                }
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Agent {agent_name} failed: {e}")
            
            # Log detailed error
            if trace_id:
                self.observability.log_error(
                    trace_id=trace_id,
                    ticker=ticker,
                    agent_name=agent_name,
                    error=e,
                    context={"duration_ms": duration_ms},
                    span_id=span_id
                )
                self.observability.log_agent_complete(
                    trace_id, ticker, agent_name,
                    duration_ms=duration_ms,
                    status="error",
                    error_message=str(e),
                    span_id=span_id
                )
            
            return {
                "_agent": agent_name,
                "error": str(e)
            }
    
    def _call_predictor(
        self,
        ticker: str,
        agent_analyses: Dict[str, Any],
        trace_id: str = None
    ) -> Dict[str, Any]:
        """Call predictor agent to synthesize all analyses."""
        start_time = time.time()
        agent_name = "predictor_agent"
        
        # Log agent start with input analyses
        span_id = None
        if trace_id:
            span_id = self.observability.log_agent_start(
                trace_id, ticker, agent_name,
                input_data={"analyses_summary": list(agent_analyses.keys())}
            )
        
        if not self.model:
            return {"error": "GenAI not configured"}
        
        config = AGENT_CONFIG.get("predictor_agent", {})
        system_prompt = config.get("system_prompt", "")
        output_format = config.get("output_format", {})
        temperature = config.get("temperature", 0.4)
        max_tokens = config.get("max_tokens", 2500)
        
        # Clean agent analyses to reduce token usage
        cleaned_analyses = self._clean_for_predictor(agent_analyses)
        
        user_prompt = f"""
You have received analyses from 5 specialized agents for {ticker}.
Synthesize these into a final investment recommendation.

AGENT ANALYSES:
{json.dumps(cleaned_analyses, indent=2, default=str)}

Provide your synthesized recommendation in this JSON format:
{json.dumps(output_format, indent=2)}

IMPORTANT: Include a "reasoning" field explaining how you weighted each agent's analysis.
Respond ONLY with valid JSON.
"""

        
        # Log LLM request
        llm_start_time = time.time()
        if trace_id and span_id:
            self.observability.log_llm_request(
                trace_id=trace_id,
                span_id=span_id,
                ticker=ticker,
                agent_name=agent_name,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        try:
            response = self.model.generate_content(
                [system_prompt, user_prompt],
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            
            llm_latency_ms = (time.time() - llm_start_time) * 1000
            raw_response = response.text.strip()
            response_text = raw_response
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Get token counts
            input_tokens = None
            output_tokens = None
            finish_reason = None
            try:
                if hasattr(response, 'usage_metadata'):
                    input_tokens = getattr(response.usage_metadata, 'prompt_token_count', None)
                    output_tokens = getattr(response.usage_metadata, 'candidates_token_count', None)
                if hasattr(response, 'candidates') and response.candidates:
                    finish_reason = str(response.candidates[0].finish_reason) if hasattr(response.candidates[0], 'finish_reason') else None
            except Exception:
                pass
            
            try:
                parsed = json.loads(response_text)
                
                # Log LLM response
                if trace_id and span_id:
                    self.observability.log_llm_response(
                        trace_id=trace_id,
                        span_id=span_id,
                        ticker=ticker,
                        agent_name=agent_name,
                        raw_response=raw_response,
                        parsed_response=parsed,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        latency_ms=llm_latency_ms,
                        finish_reason=finish_reason
                    )
                
                # Log successful completion
                duration_ms = (time.time() - start_time) * 1000
                if trace_id:
                    self.observability.log_agent_complete(
                        trace_id, ticker, agent_name,
                        duration_ms=duration_ms,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        status="success",
                        output_data=parsed,
                        span_id=span_id
                    )
                
                return parsed
            except json.JSONDecodeError as e:
                duration_ms = (time.time() - start_time) * 1000
                if trace_id:
                    self.observability.log_agent_complete(
                        trace_id, ticker, agent_name,
                        duration_ms=duration_ms,
                        status="error",
                        error_message=f"Failed to parse JSON: {str(e)}",
                        span_id=span_id
                    )
                return {"_raw_response": response_text, "error": "Failed to parse"}
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Predictor failed: {e}")
            
            if trace_id:
                self.observability.log_error(
                    trace_id=trace_id,
                    ticker=ticker,
                    agent_name=agent_name,
                    error=e,
                    span_id=span_id
                )
                self.observability.log_agent_complete(
                    trace_id, ticker, agent_name,
                    duration_ms=duration_ms,
                    status="error",
                    error_message=str(e),
                    span_id=span_id
                )
            
            return {"error": str(e)}
    
    async def analyze_async(self, ticker: str) -> Dict[str, Any]:
        """
        Perform async analysis of a stock.
        
        Args:
            ticker: Stock ticker (e.g., "RELIANCE", "TCS.NS")
            
        Returns:
            Comprehensive analysis report
        """
        start_time = datetime.now()
        
        # Validate ticker
        validation = self._validate_ticker(ticker)
        if not validation.get("valid"):
            return {
                "error": validation.get("error"),
                "ticker": ticker
            }
        
        ticker_clean = validation.get("ticker")
        
        # Start observability trace
        trace_id = self.observability.start_trace(ticker_clean)
        
        # Check cache
        if self.enable_caching and ticker_clean in self.cache:
            cache_entry = self.cache[ticker_clean]
            cache_age = (datetime.now() - cache_entry.get("timestamp", datetime.min)).seconds
            if cache_age < 3600:  # 1 hour cache
                logger.info(f"Returning cached analysis for {ticker_clean}")
                self.observability.end_trace(trace_id)
                return cache_entry.get("report")
        
        # Gather base data
        logger.info(f"Gathering base data for {ticker_clean}")
        base_data = self._gather_base_data(ticker_clean)
        
        # Run specialist agents in parallel
        logger.info("Running specialist agents in parallel")
        agent_names = [
            "fundamental_agent",
            "technical_agent",
            "sentiment_agent",
            "macro_agent",
            "regulatory_agent"
        ]
        
        agent_analyses = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._call_agent, name, base_data, trace_id): name
                for name in agent_names
            }
            
            for future in as_completed(futures, timeout=self.timeout):
                name = futures[future]
                try:
                    agent_analyses[name] = future.result()
                except Exception as e:
                    logger.error(f"Agent {name} failed: {e}")
                    agent_analyses[name] = {"error": str(e)}
        
        # Call predictor for synthesis
        logger.info("Calling predictor agent for synthesis")
        prediction = self._call_predictor(ticker_clean, agent_analyses, trace_id)
        
        # Compile final report
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        report = {
            "ticker": ticker_clean,
            "company_name": validation.get("name"),
            "current_price": validation.get("current_price"),
            "analysis_timestamp": start_time.isoformat(),
            "analysis_duration_seconds": duration,
            "trace_id": trace_id,  # Include trace ID for log correlation
            "base_data_summary": {
                "has_fundamentals": "error" not in base_data.get("fundamentals", {}),
                "has_price_history": "error" not in str(base_data.get("price_history", {})),
                "has_sentiment": "error" not in base_data.get("sentiment", {}),
                "has_macro": "error" not in base_data.get("macro", {}),
                "has_supabase_data": "error" not in base_data.get("supabase_data", {})
            },
            "agent_analyses": {
                "fundamental": agent_analyses.get("fundamental_agent"),
                "technical": agent_analyses.get("technical_agent"),
                "sentiment": agent_analyses.get("sentiment_agent"),
                "macro": agent_analyses.get("macro_agent"),
                "regulatory": agent_analyses.get("regulatory_agent")
            },
            "synthesis": prediction,
            "recommendation": prediction.get("recommendation", "N/A"),
            "composite_score": prediction.get("composite_score"),
            "target_price": prediction.get("target_price"),
            "confidence": prediction.get("confidence")
        }
        
        # End trace and get summary
        trace_summary = self.observability.end_trace(trace_id)
        report["observability"] = trace_summary
        
        # Cache the report
        if self.enable_caching:
            self.cache[ticker_clean] = {
                "report": report,
                "timestamp": datetime.now()
            }
        
        return report
    
    def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for analyze_async.
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Comprehensive analysis report
        """
        return asyncio.run(self.analyze_async(ticker))
    
    def batch_analyze(
        self,
        tickers: List[str],
        max_parallel: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple stocks.
        
        Args:
            tickers: List of stock tickers
            max_parallel: Maximum parallel analyses
            
        Returns:
            List of analysis reports
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = {
                executor.submit(self.analyze, ticker): ticker
                for ticker in tickers
            }
            
            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Analysis failed for {ticker}: {e}")
                    results.append({"ticker": ticker, "error": str(e)})
        
        return results
    
    def get_quick_summary(self, ticker: str) -> Dict[str, Any]:
        """
        Get a quick summary without full agent analysis.
        
        Useful for screening or when API limits are a concern.
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Quick summary with scores
        """
        ticker_clean = ticker.replace(".NS", "").upper()
        
        # Get cached supabase data (pre-computed)
        supabase_data = get_comprehensive_stock_data(ticker_clean)
        quote = get_stock_quote(ticker_clean)
        
        return {
            "ticker": ticker_clean,
            "current_price": quote.get("last_price"),
            "scores": supabase_data.get("scores", {}),
            "weekly_change": supabase_data.get("weekly", {}).get("weekly_change_pct"),
            "timestamp": datetime.now().isoformat()
        }


def analyze_stock(ticker: str) -> Dict[str, Any]:
    """
    Convenience function for one-off analysis.
    
    Args:
        ticker: Stock ticker (e.g., "RELIANCE")
        
    Returns:
        Complete analysis report
        
    Example:
        >>> from nifty_agents import analyze_stock
        >>> report = analyze_stock("TCS")
        >>> print(report["recommendation"])
    """
    orchestrator = NiftyAgentOrchestrator()
    return orchestrator.analyze(ticker)


async def analyze_stock_async(ticker: str) -> Dict[str, Any]:
    """Async version of analyze_stock."""
    orchestrator = NiftyAgentOrchestrator()
    return await orchestrator.analyze_async(ticker)
