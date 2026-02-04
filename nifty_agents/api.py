"""
NIFTY Agent API

FastAPI backend providing REST endpoints for the multi-agent
stock analysis system.

Endpoints:
- GET /api/agent/analyze/{ticker} - Full agent analysis
- GET /api/agent/quick/{ticker} - Quick summary
- GET /api/agent/batch - Analyze multiple tickers
- GET /api/agent/health - Service health check
"""

# Load environment variables FIRST before any other imports
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

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
import logging
import json
import os
import asyncio

# Import orchestrator
from .agents.orchestrator import NiftyAgentOrchestrator, analyze_stock

# Import observability
from .observability import (
    get_observability, 
    view_recent_logs, 
    view_finops_logs,
    view_llm_traces,
    get_trace_details,
    get_log_paths,
    print_cost_report,
    get_available_models,
    estimate_analysis_cost,
    get_model_from_env,
    generate_test_logs,
    TOTAL_TOKENS_PER_ANALYSIS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NIFTY Agent Analysis API",
    description="""
    Multi-agent AI system for comprehensive analysis of NIFTY stocks.
    
    ## Features
    - 6 specialized AI agents (Fundamental, Technical, Sentiment, Macro, Regulatory, Predictor)
    - Parallel execution for fast analysis
    - Integration with existing Supabase data pipeline
    - Indian market specific context and data sources
    
    ## Usage
    1. Call `/api/agent/analyze/{ticker}` for full analysis
    2. Call `/api/agent/quick/{ticker}` for quick scores
    3. Use `/api/agent/batch` for multiple tickers
    """,
    version="1.0.0",
    docs_url="/api/agent/docs",
    redoc_url="/api/agent/redoc"
)

# CORS middleware for frontend integration
# Note: FastAPI's CORSMiddleware doesn't support wildcard patterns in domains
# Using ["*"] to allow all origins (for API that's publicly accessible)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public API
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize orchestrator (singleton)
orchestrator = NiftyAgentOrchestrator()


# ============================================================================
# Request/Response Models
# ============================================================================

class AnalysisRequest(BaseModel):
    """Request model for batch analysis."""
    tickers: List[str] = Field(..., description="List of stock tickers to analyze")
    quick_mode: bool = Field(False, description="Use quick mode (no LLM calls)")


class AnalysisResponse(BaseModel):
    """Response model for analysis."""
    ticker: str
    company_name: Optional[str]
    current_price: Optional[float]
    recommendation: Optional[str]
    composite_score: Optional[float]
    target_price: Optional[float]
    confidence: Optional[str]
    analysis_timestamp: str
    analysis_duration_seconds: Optional[float]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    genai_configured: bool
    supabase_configured: bool
    version: str


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    ticker: Optional[str]
    timestamp: str


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/api/agent/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Check API health and configuration status.
    
    Returns:
        Health status with configuration flags
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        genai_configured=bool(os.environ.get("GOOGLE_API_KEY")),
        supabase_configured=bool(
            os.environ.get("SUPABASE_URL") or 
            os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        ),
        version="1.0.0"
    )


@app.get("/health", tags=["Health"])
async def health():
    """Simple health check for Cloud Run."""
    return {"status": "healthy"}


# ============================================================================
# Cache Management Endpoints
# ============================================================================

@app.get("/api/agent/cache/stats", tags=["Cache"], summary="Get Cache Statistics")
async def cache_stats():
    """
    Get cache statistics including cached tickers and TTL.
    
    Returns:
        Cache size, cached tickers, and TTL configuration
    """
    cache_entries = []
    for ticker, entry in orchestrator.cache.items():
        cache_age = (datetime.now() - entry.get("timestamp", datetime.min)).seconds
        cache_entries.append({
            "ticker": ticker,
            "cache_age_seconds": cache_age,
            "expires_in_seconds": max(0, 86400 - cache_age),
            "cached_at": entry.get("timestamp", datetime.min).isoformat()
        })
    
    return {
        "cache_enabled": orchestrator.enable_caching,
        "cache_ttl_seconds": 86400,  # 24 hours
        "cache_ttl_hours": 24,
        "entries_count": len(orchestrator.cache),
        "entries": cache_entries
    }


@app.delete("/api/agent/cache/{ticker}", tags=["Cache"], summary="Clear Cache for Ticker")
async def clear_cache(ticker: str):
    """
    Clear cached analysis for a specific ticker.
    
    Args:
        ticker: Stock ticker to clear from cache
        
    Returns:
        Confirmation of cache clearance
    """
    ticker_clean = ticker.upper().strip()
    if ticker_clean in orchestrator.cache:
        del orchestrator.cache[ticker_clean]
        return {
            "cleared": True,
            "ticker": ticker_clean,
            "message": f"Cache cleared for {ticker_clean}"
        }
    return {
        "cleared": False,
        "ticker": ticker_clean,
        "message": f"{ticker_clean} was not in cache"
    }


@app.delete("/api/agent/cache", tags=["Cache"], summary="Clear All Cache")
async def clear_all_cache():
    """
    Clear all cached analyses.
    
    Returns:
        Number of entries cleared
    """
    count = len(orchestrator.cache)
    orchestrator.cache.clear()
    return {
        "cleared": True,
        "entries_cleared": count,
        "message": f"Cleared {count} cached entries"
    }


@app.get("/api/agent/history/{ticker}", tags=["Cache"], summary="Get Cached Analysis Summary")
async def get_analysis_history(ticker: str):
    """
    Get cached analysis summary for a ticker (for hover tooltip display).
    
    Args:
        ticker: Stock ticker to check
        
    Returns:
        Cached analysis metadata including score, date, and recommendation
    """
    ticker_clean = ticker.upper().strip()
    
    if ticker_clean in orchestrator.cache:
        entry = orchestrator.cache[ticker_clean]
        cache_age = (datetime.now() - entry.get("timestamp", datetime.min)).seconds
        result = entry.get("result", {})
        
        # Extract key fields for tooltip display
        synthesis = result.get("synthesis", {})
        
        return {
            "has_cached": True,
            "ticker": ticker_clean,
            "analyzed_at": entry.get("timestamp", datetime.min).isoformat(),
            "cache_age_seconds": cache_age,
            "cache_age_hours": round(cache_age / 3600, 1),
            "composite_score": result.get("composite_score"),
            "recommendation": synthesis.get("overall_recommendation") or synthesis.get("recommendation"),
            "signal": synthesis.get("action_signal") or result.get("signal"),
            "expires_in_hours": round(max(0, 24 - cache_age / 3600), 1)
        }
    
    return {
        "has_cached": False,
        "ticker": ticker_clean,
        "message": f"No cached analysis for {ticker_clean}"
    }


@app.get(
    "/api/agent/analyze/{ticker}",
    response_model=Dict[str, Any],
    tags=["Analysis"],
    summary="Full Agent Analysis"
)
async def analyze_ticker(ticker: str):
    """
    Perform comprehensive multi-agent analysis on a stock.
    
    This endpoint:
    1. Validates the ticker against NSE
    2. Gathers data from multiple sources
    3. Runs 5 specialist agents in parallel
    4. Synthesizes results with predictor agent
    5. Returns comprehensive report
    
    **Response includes:**
    - Agent analyses (fundamental, technical, sentiment, macro, regulatory)
    - Synthesized recommendation
    - Target price and confidence level
    - Risk factors and key monitorables
    
    **Example:**
    ```
    GET /api/agent/analyze/RELIANCE
    ```
    
    Args:
        ticker: NSE stock ticker (e.g., RELIANCE, TCS, INFY)
        
    Returns:
        Comprehensive analysis report
    """
    try:
        report = await orchestrator.analyze_async(ticker)
        
        if "error" in report and report.get("ticker"):
            raise HTTPException(
                status_code=404,
                detail=report.get("error")
            )
        
        return JSONResponse(content=report)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# ============================================================================
# SSE Streaming Endpoint for Real-time Agent Updates
# ============================================================================

async def stream_analysis_events(ticker: str) -> AsyncGenerator[str, None]:
    """
    Generator that yields SSE events during analysis.
    
    Events:
    - start: Analysis started
    - orchestrator: Orchestrator status update
    - agent_start: Agent started processing
    - agent_complete: Agent finished with result
    - agent_error: Agent encountered error  
    - predictor_start: Predictor started
    - predictor_complete: Final result ready
    - complete: All done
    - error: Error occurred
    """
    import time
    start_time = time.time()
    
    def emit_event(event_type: str, data: dict) -> str:
        """Format SSE event."""
        data["elapsed_seconds"] = round(time.time() - start_time, 2)
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    
    try:
        # Start event
        yield emit_event("start", {
            "ticker": ticker.upper(),
            "timestamp": datetime.now().isoformat(),
            "message": f"Starting analysis for {ticker.upper()}"
        })
        await asyncio.sleep(0.1)
        
        # Orchestrator starting
        yield emit_event("orchestrator", {
            "status": "active",
            "message": "Fetching base data and initializing agents..."
        })
        
        # Get base data first (run in thread since it's synchronous)
        base_data = await asyncio.to_thread(orchestrator._gather_base_data, ticker)
        if not base_data:
            yield emit_event("error", {
                "message": f"Could not find stock data for {ticker}"
            })
            return
            
        yield emit_event("orchestrator", {
            "status": "active",
            "message": f"Data loaded: {base_data.get('Company_Name', ticker)} @ ₹{base_data.get('Last_Close', 'N/A')}"
        })
        await asyncio.sleep(0.1)
        
        # Run agents in parallel with progress tracking
        agents_config = [
            ("fundamental", orchestrator.fundamental_agent, "📈"),
            ("technical", orchestrator.technical_agent, "📉"),
            ("sentiment", orchestrator.sentiment_agent, "📰"),
            ("macro", orchestrator.macro_agent, "🌍"),
            ("regulatory", orchestrator.regulatory_agent, "⚖️"),
        ]
        
        # Emit agent start events
        for agent_name, _, emoji in agents_config:
            yield emit_event("agent_start", {
                "agent": agent_name,
                "emoji": emoji,
                "message": f"{agent_name.capitalize()} agent starting..."
            })
        await asyncio.sleep(0.1)
        
        # Create tasks for all agents
        async def run_agent_with_tracking(name: str, agent, emoji: str):
            """Run agent and track completion."""
            agent_start = time.time()
            try:
                result = await asyncio.to_thread(agent.analyze, ticker, base_data)
                agent_duration = time.time() - agent_start
                return {
                    "name": name,
                    "emoji": emoji,
                    "result": result,
                    "duration": round(agent_duration, 2),
                    "error": None
                }
            except Exception as e:
                return {
                    "name": name,
                    "emoji": emoji,
                    "result": None,
                    "duration": round(time.time() - agent_start, 2),
                    "error": str(e)
                }
        
        # Run all agents concurrently
        tasks = [
            run_agent_with_tracking(name, agent, emoji) 
            for name, agent, emoji in agents_config
        ]
        
        agent_results = {}
        for coro in asyncio.as_completed(tasks):
            result = await coro
            agent_name = result["name"]
            
            if result["error"]:
                yield emit_event("agent_error", {
                    "agent": agent_name,
                    "emoji": result["emoji"],
                    "error": result["error"],
                    "duration_seconds": result["duration"]
                })
            else:
                analysis = result["result"]
                score = analysis.get("score") or analysis.get("overall_score") or "--"
                yield emit_event("agent_complete", {
                    "agent": agent_name,
                    "emoji": result["emoji"],
                    "score": score,
                    "duration_seconds": result["duration"],
                    "message": f"{agent_name.capitalize()} complete: Score {score}"
                })
                agent_results[f"{agent_name}_agent"] = analysis
        
        await asyncio.sleep(0.1)
        
        # Predictor phase
        yield emit_event("predictor_start", {
            "message": "All agents complete. Synthesizing final recommendation..."
        })
        
        predictor_start = time.time()
        try:
            final_result = await asyncio.to_thread(
                orchestrator.predictor_agent.synthesize,
                ticker, base_data, agent_results
            )
            predictor_duration = time.time() - predictor_start
            
            yield emit_event("predictor_complete", {
                "recommendation": final_result.get("recommendation", "hold"),
                "composite_score": final_result.get("composite_score", 50),
                "target_price": final_result.get("target_price"),
                "confidence": final_result.get("confidence", "medium"),
                "duration_seconds": round(predictor_duration, 2)
            })
        except Exception as e:
            yield emit_event("predictor_error", {
                "error": str(e),
                "duration_seconds": round(time.time() - predictor_start, 2)
            })
        
        # Get observability stats
        obs = get_observability()
        total_duration = time.time() - start_time
        
        # Final complete event
        yield emit_event("complete", {
            "ticker": ticker.upper(),
            "total_duration_seconds": round(total_duration, 2),
            "recommendation": final_result.get("recommendation", "hold") if 'final_result' in dir() else "hold",
            "composite_score": final_result.get("composite_score", 50) if 'final_result' in dir() else 50,
            "total_tokens": obs.session_input_tokens + obs.session_output_tokens,
            "total_cost_usd": round(obs.session_cost, 6),
            "message": "Analysis complete!"
        })
        
    except Exception as e:
        logger.error(f"Stream analysis error: {e}")
        yield emit_event("error", {
            "message": str(e),
            "ticker": ticker
        })


@app.get(
    "/api/agent/analyze/{ticker}/stream",
    tags=["Analysis"],
    summary="Streaming Analysis with SSE"
)
async def analyze_ticker_stream(ticker: str):
    """
    Stream analysis progress via Server-Sent Events (SSE).
    
    This endpoint streams real-time updates as each agent completes.
    Perfect for building live progress UIs.
    
    **Event Types:**
    - `start` - Analysis initiated
    - `orchestrator` - Orchestrator status
    - `agent_start` - Agent began processing
    - `agent_complete` - Agent finished with score
    - `agent_error` - Agent encountered error
    - `predictor_start` - Synthesis phase began
    - `predictor_complete` - Final recommendation ready
    - `complete` - All done with summary
    - `error` - Error occurred
    
    **Usage (JavaScript):**
    ```javascript
    const evtSource = new EventSource('/api/agent/analyze/RELIANCE/stream');
    evtSource.addEventListener('agent_complete', (e) => {
        const data = JSON.parse(e.data);
        console.log(`${data.agent} scored ${data.score}`);
    });
    ```
    
    Args:
        ticker: NSE stock ticker
        
    Returns:
        SSE stream of analysis events
    """
    return StreamingResponse(
        stream_analysis_events(ticker),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@app.get(
    "/api/agent/quick/{ticker}",
    response_model=Dict[str, Any],
    tags=["Analysis"],
    summary="Quick Summary"
)
async def quick_analysis(ticker: str):
    """
    Get quick summary without full agent analysis.
    
    This is faster and doesn't use LLM API calls.
    Uses pre-computed data from Supabase.
    
    **Good for:**
    - Screening multiple stocks quickly
    - When API rate limits are a concern
    - Getting pre-computed scores
    
    Args:
        ticker: NSE stock ticker
        
    Returns:
        Quick summary with scores
    """
    try:
        summary = orchestrator.get_quick_summary(ticker)
        return JSONResponse(content=summary)
        
    except Exception as e:
        logger.error(f"Quick analysis failed for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quick analysis failed: {str(e)}"
        )


@app.post(
    "/api/agent/batch",
    response_model=List[Dict[str, Any]],
    tags=["Analysis"],
    summary="Batch Analysis"
)
async def batch_analysis(request: AnalysisRequest):
    """
    Analyze multiple stocks in batch.
    
    **Note:** Full analysis mode is rate-limited to 3 parallel requests.
    For screening many stocks, use `quick_mode=True`.
    
    Args:
        request: Batch analysis request with tickers list
        
    Returns:
        List of analysis reports
    """
    if len(request.tickers) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 tickers per batch request"
        )
    
    try:
        if request.quick_mode:
            results = [
                orchestrator.get_quick_summary(ticker)
                for ticker in request.tickers
            ]
        else:
            results = orchestrator.batch_analyze(
                request.tickers,
                max_parallel=3
            )
        
        return JSONResponse(content=results)
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch analysis failed: {str(e)}"
        )


@app.get(
    "/api/agent/scores/{ticker}",
    response_model=Dict[str, Any],
    tags=["Data"],
    summary="Get Stock Scores"
)
async def get_scores(ticker: str):
    """
    Get pre-computed scores from Supabase.
    
    Returns scores without running agent analysis.
    
    Args:
        ticker: NSE stock ticker
        
    Returns:
        Stock scores and ratings
    """
    from .tools.supabase_fetcher import get_stock_scores
    
    try:
        scores = get_stock_scores(ticker)
        return JSONResponse(content=scores)
        
    except Exception as e:
        logger.error(f"Failed to get scores for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get(
    "/api/agent/macro",
    response_model=Dict[str, Any],
    tags=["Data"],
    summary="Get Macro Indicators"
)
async def get_macro():
    """
    Get current macro-economic indicators.
    
    Returns:
    - RBI rates (repo, CRR, SLR)
    - India VIX
    - NIFTY valuations
    - Market regime
    
    Returns:
        Macro indicators
    """
    from .tools.india_macro_fetcher import get_macro_indicators
    
    try:
        macro = get_macro_indicators()
        return JSONResponse(content=macro)
        
    except Exception as e:
        logger.error(f"Failed to get macro indicators: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get(
    "/api/agent/news/{ticker}",
    response_model=Dict[str, Any],
    tags=["Data"],
    summary="Get Stock News Sentiment"
)
async def get_news_sentiment(
    ticker: str,
    max_items: int = Query(10, ge=1, le=50)
):
    """
    Get news sentiment analysis for a stock.
    
    Args:
        ticker: NSE stock ticker
        max_items: Maximum news items to analyze
        
    Returns:
        News items with sentiment scores
    """
    from .tools.india_news_fetcher import analyze_sentiment_aggregate, get_stock_news
    
    try:
        sentiment = analyze_sentiment_aggregate(ticker)
        news = get_stock_news(ticker, max_items=max_items)
        
        return JSONResponse(content={
            "sentiment_summary": sentiment,
            "news_items": news
        })
        
    except Exception as e:
        logger.error(f"Failed to get news for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get(
    "/api/agent/top-stocks",
    response_model=List[Dict[str, Any]],
    tags=["Data"],
    summary="Get Top Stocks"
)
async def get_top_stocks(
    index: str = Query("NIFTY_50", description="Index name"),
    sort_by: str = Query("composite_score", description="Sort field"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get top-ranked stocks from an index.
    
    Args:
        index: Index name (NIFTY_50, NIFTY_200, NIFTY_500)
        sort_by: Field to sort by
        limit: Number of stocks to return
        
    Returns:
        List of top stocks with scores
    """
    from .tools.supabase_fetcher import get_top_stocks as fetch_top
    
    try:
        top = fetch_top(index, sort_by, limit)
        return JSONResponse(content=top)
        
    except Exception as e:
        logger.error(f"Failed to get top stocks: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================================
# Observability & FinOps Endpoints
# ============================================================================

@app.get(
    "/api/agent/observability/logs",
    response_model=Dict[str, Any],
    tags=["Observability"],
    summary="View Recent Agent Logs"
)
async def get_agent_logs(n: int = Query(50, description="Number of recent log entries")):
    """
    Retrieve recent agent execution logs.
    
    Logs include:
    - Trace IDs for correlation
    - Agent names and execution times
    - Token usage (estimated)
    - Errors and status
    
    Args:
        n: Number of recent entries to return (default: 50)
    """
    try:
        logs = view_recent_logs(n)
        paths = get_log_paths()
        
        return {
            "count": len(logs),
            "log_file": paths["agent_logs"],
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/agent/observability/finops",
    response_model=Dict[str, Any],
    tags=["Observability"],
    summary="View FinOps Cost Data"
)
async def get_finops_data(n: int = Query(100, description="Number of recent cost entries")):
    """
    Retrieve API cost tracking data.
    
    Returns:
    - Cost per API call
    - Token usage (input/output)
    - Model used
    - Cumulative costs
    
    Args:
        n: Number of recent entries to return (default: 100)
    """
    try:
        finops = view_finops_logs(n)
        paths = get_log_paths()
        
        # Calculate totals
        total_cost = sum(e.get("total_cost_usd", 0) for e in finops)
        total_input_tokens = sum(e.get("input_tokens", 0) for e in finops)
        total_output_tokens = sum(e.get("output_tokens", 0) for e in finops)
        
        return {
            "count": len(finops),
            "log_file": paths["finops_logs"],
            "summary": {
                "total_cost_usd": round(total_cost, 6),
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "avg_cost_per_call": round(total_cost / max(len(finops), 1), 6)
            },
            "entries": finops
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/agent/observability/metrics",
    response_model=Dict[str, Any],
    tags=["Observability"],
    summary="Get Aggregated Metrics"
)
async def get_metrics():
    """
    Retrieve aggregated analysis metrics.
    
    Includes:
    - Total analyses run
    - Success/failure counts
    - Total costs
    - Daily cost breakdown
    - Cost per agent
    """
    try:
        obs = get_observability()
        metrics = obs.get_metrics_summary()
        
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/agent/observability/cost-report",
    response_model=Dict[str, Any],
    tags=["Observability"],
    summary="Get Cost Report"
)
async def get_cost_report(days: int = Query(7, description="Number of days for report")):
    """
    Generate a cost report for the specified period.
    
    Args:
        days: Number of days to include (default: 7)
        
    Returns:
        Cost breakdown with daily and per-analysis averages
    """
    try:
        obs = get_observability()
        report = obs.get_cost_report(days=days)
        
        return {
            "status": "success",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/agent/observability/log-paths",
    response_model=Dict[str, str],
    tags=["Observability"],
    summary="Get Log File Paths"
)
async def get_paths():
    """
    Get the paths to all log files for direct access.
    
    Returns:
        Dictionary of log type to file path
    """
    return get_log_paths()


@app.get(
    "/api/agent/observability/llm-traces",
    response_model=Dict[str, Any],
    tags=["Observability"],
    summary="View LLM Request/Response Traces"
)
async def get_llm_traces(
    n: int = Query(20, description="Number of traces to return"),
    trace_id: str = Query(None, description="Filter by trace ID")
):
    """
    View detailed LLM request/response traces.
    
    Includes:
    - Full system and user prompts
    - Complete LLM responses (raw and parsed)
    - Token counts and latency
    - Reasoning extracted from responses
    
    Args:
        n: Number of traces to return (default: 20)
        trace_id: Optional filter by specific trace ID
    """
    try:
        traces = view_llm_traces(n, trace_id)
        paths = get_log_paths()
        
        return {
            "count": len(traces),
            "log_file": paths.get("llm_traces"),
            "traces": traces
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/agent/observability/trace/{trace_id}",
    response_model=Dict[str, Any],
    tags=["Observability"],
    summary="Get Complete Trace Details"
)
async def get_full_trace(trace_id: str):
    """
    Get all logs and details for a specific trace ID.
    
    Returns:
    - All events in chronological order
    - All LLM request/response pairs
    - Any errors that occurred
    - Summary statistics
    
    Args:
        trace_id: The trace ID to retrieve
    """
    try:
        details = get_trace_details(trace_id)
        
        if not details["events"]:
            raise HTTPException(
                status_code=404, 
                detail=f"No trace found with ID: {trace_id}"
            )
        
        return {
            "status": "success",
            "trace": details
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/agent/observability/models",
    response_model=Dict[str, Any],
    tags=["Observability"],
    summary="Get Available Models & Pricing"
)
async def get_models():
    """
    Get all available Gemini models with pricing info.
    
    Returns model comparison for cost optimization.
    """
    current_model = get_model_from_env()
    current_estimate = estimate_analysis_cost(current_model)
    
    return {
        "current_model": current_model,
        "current_cost_per_analysis_usd": current_estimate["total_cost_usd"],
        "tokens_per_analysis": TOTAL_TOKENS_PER_ANALYSIS,
        "available_models": get_available_models(),
        "recommendation": {
            "high_volume": "gemini-1.5-flash-8b",
            "balanced": "gemini-2.0-flash-exp",
            "quality": "gemini-1.5-pro",
            "free_experimental": "gemini-2.0-flash-thinking-exp"
        }
    }


@app.get(
    "/api/agent/observability/estimate",
    response_model=Dict[str, Any],
    tags=["Observability"],
    summary="Estimate Analysis Cost"
)
async def estimate_cost(model: str = Query(None, description="Model to estimate for")):
    """
    Estimate the cost of a single stock analysis.
    
    Args:
        model: Model name (uses current model if not specified)
        
    Returns:
        Token breakdown and cost estimate
    """
    return estimate_analysis_cost(model)


@app.post(
    "/api/agent/observability/test",
    response_model=Dict[str, Any],
    tags=["Observability"],
    summary="Generate Test Logs"
)
async def create_test_logs(ticker: str = Query("RELIANCE", description="Ticker for test logs")):
    """
    Generate sample observability logs for testing.
    
    This creates realistic log entries for all 6 agents without making actual LLM calls.
    Useful for:
    - Testing the dashboard
    - Verifying log files are created correctly
    - Demo purposes
    
    Args:
        ticker: Stock ticker to use in test logs
        
    Returns:
        Summary of generated test data with trace_id
    """
    try:
        result = generate_test_logs(ticker)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Failed to generate test logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/api/agent/observability/clear",
    response_model=Dict[str, Any],
    tags=["Observability"],
    summary="Clear All Logs"
)
async def clear_logs():
    """
    Clear all log files. Use with caution!
    
    Returns:
        Confirmation of cleared files
    """
    try:
        paths = get_log_paths()
        cleared = []
        
        for name, path in paths.items():
            if name != "logs_directory" and Path(path).exists():
                if name == "metrics":
                    # Reset metrics to empty state
                    with open(path, 'w') as f:
                        json.dump({
                            "total_analyses": 0,
                            "successful_analyses": 0,
                            "failed_analyses": 0,
                            "total_cost_usd": 0.0,
                            "total_input_tokens": 0,
                            "total_output_tokens": 0,
                            "avg_duration_seconds": 0.0,
                            "last_updated": "",
                            "costs_by_agent": {},
                            "costs_by_date": {}
                        }, f, indent=2)
                else:
                    # Clear JSONL files
                    with open(path, 'w') as f:
                        pass  # Empty the file
                cleared.append(name)
        
        return {
            "status": "success",
            "message": "Logs cleared",
            "cleared_files": cleared
        }
    except Exception as e:
        logger.error(f"Failed to clear logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Temporal Analysis Endpoints (Weekly, Monthly, Seasonality)
# ============================================================================

# Import temporal crews
try:
    from .agents.temporal_crews import (
        WeeklyAnalysisCrew,
        MonthlyAnalysisCrew,
        SeasonalityAnalysisCrew,
        get_weekly_outlook,
        get_monthly_thesis,
        get_seasonality_insights
    )
    TEMPORAL_CREWS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Temporal crews not available: {e}")
    TEMPORAL_CREWS_AVAILABLE = False


@app.get(
    "/api/agent/weekly-outlook",
    tags=["Temporal Analysis"],
    summary="Get Weekly Market Outlook"
)
async def weekly_outlook():
    """
    Get AI-generated weekly market outlook for Indian equities.
    
    Uses multiple specialized agents:
    - Trend Agent: Technical analysis of weekly patterns
    - Sector Rotation Agent: Money flow analysis
    - Risk Regime Agent: Market risk assessment
    - Weekly Synthesizer: Combines all insights
    
    Returns:
        Complete weekly analysis with stance, insights, and recommendations
    """
    if not TEMPORAL_CREWS_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Temporal analysis crews not available"
        )
    
    try:
        result = await get_weekly_outlook()
        
        # Make response JSON-serializable
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(v) for v in obj]
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return make_serializable(obj.__dict__)
            else:
                try:
                    json.dumps(obj)
                    return obj
                except (TypeError, ValueError):
                    return str(obj)
        
        return JSONResponse(content=make_serializable(result))
        
    except Exception as e:
        logger.error(f"Weekly outlook failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/agent/monthly-thesis",
    tags=["Temporal Analysis"],
    summary="Get Monthly Investment Thesis"
)
async def monthly_thesis():
    """
    Get AI-generated monthly investment thesis for Indian markets.
    
    Uses multiple specialized agents:
    - Macro Cycle Agent: Economic cycle analysis
    - Fund Flow Agent: Institutional flow tracking
    - Valuation Regime Agent: Market-wide valuations
    - Monthly Strategist: Investment thesis synthesis
    
    Returns:
        Complete monthly analysis with thesis, asset allocation, and themes
    """
    if not TEMPORAL_CREWS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Temporal analysis crews not available"
        )
    
    try:
        result = await get_monthly_thesis()
        
        # Make response JSON-serializable
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(v) for v in obj]
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return make_serializable(obj.__dict__)
            else:
                try:
                    json.dumps(obj)
                    return obj
                except (TypeError, ValueError):
                    return str(obj)
        
        return JSONResponse(content=make_serializable(result))
        
    except Exception as e:
        logger.error(f"Monthly thesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/agent/seasonality",
    tags=["Temporal Analysis"],
    summary="Get Seasonality Insights"
)
async def seasonality_insights(
    ticker: Optional[str] = Query(None, description="Optional ticker for stock-specific seasonality"),
    sector: Optional[str] = Query(None, description="Optional sector to focus on")
):
    """
    Get AI-generated seasonality insights for Indian markets.
    
    Uses multiple specialized agents:
    - Historical Pattern Agent: Monthly return patterns analysis
    - Event Calendar Agent: Recurring event impacts
    - Sector Seasonality Agent: Sector-specific patterns
    - Seasonality Synthesizer: Actionable insights
    
    Args:
        ticker: Optional specific stock ticker for focused analysis
        sector: Optional sector for sector-specific patterns
    
    Returns:
        Seasonality analysis with probability, patterns, and recommendations
    """
    if not TEMPORAL_CREWS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Temporal analysis crews not available"
        )
    
    try:
        result = await get_seasonality_insights(ticker=ticker, sector=sector)
        
        # Make response JSON-serializable
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(v) for v in obj]
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return make_serializable(obj.__dict__)
            else:
                try:
                    json.dumps(obj)
                    return obj
                except (TypeError, ValueError):
                    return str(obj)
        
        return JSONResponse(content=make_serializable(result))
        
    except Exception as e:
        logger.error(f"Seasonality insights failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/agent/temporal/status",
    tags=["Temporal Analysis"],
    summary="Check Temporal Analysis Status"
)
async def temporal_status():
    """
    Check if temporal analysis crews are available and configured.
    
    Returns:
        Status of temporal analysis capabilities
    """
    return {
        "temporal_crews_available": TEMPORAL_CREWS_AVAILABLE,
        "available_endpoints": [
            "/api/agent/weekly-outlook",
            "/api/agent/monthly-thesis",
            "/api/agent/seasonality"
        ] if TEMPORAL_CREWS_AVAILABLE else [],
        "crews": {
            "weekly": "WeeklyAnalysisCrew - 4 agents",
            "monthly": "MonthlyAnalysisCrew - 4 agents",
            "seasonality": "SeasonalityAnalysisCrew - 4 agents"
        } if TEMPORAL_CREWS_AVAILABLE else {},
        "model": get_model_from_env(),
        "api_key_configured": bool(os.environ.get("GOOGLE_API_KEY"))
    }


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("NIFTY Agent API starting up...")
    
    # Check configuration
    if not os.environ.get("GOOGLE_API_KEY"):
        logger.warning("GOOGLE_API_KEY not set - LLM features disabled")
    
    if not (os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")):
        logger.warning("Supabase not configured - some features limited")
    
    # Log file paths
    paths = get_log_paths()
    logger.info(f"Agent logs: {paths['agent_logs']}")
    logger.info(f"FinOps logs: {paths['finops_logs']}")
    
    logger.info("NIFTY Agent API ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("NIFTY Agent API shutting down...")


# ============================================================================
# Run with uvicorn
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "nifty_agents.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
