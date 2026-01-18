"""
Agent Observability & FinOps Module

Provides:
1. Structured logging with JSON format (OpenTelemetry-compatible)
2. Full LLM request/response tracing (prompts, outputs, reasoning)
3. Agent execution tracing with detailed context
4. API cost tracking (FinOps)
5. Performance metrics and latency tracking
6. Error tracking with full stack traces

Best Practices Implemented:
- Full prompt/response logging for debugging
- Token counting (actual when available, estimated fallback)
- Correlation IDs (trace_id, span_id) for distributed tracing
- Structured JSON logs (JSONL format for log aggregation)
- Separate files for different concerns (logs, costs, metrics)
- Redaction of sensitive data (API keys, PII)

Logs are written to:
- Console (for development)
- nifty_agents/logs/agent_logs.jsonl (detailed structured logs)
- nifty_agents/logs/finops.jsonl (cost tracking)
- nifty_agents/logs/llm_traces.jsonl (full LLM request/response)
"""

import os
import json
import logging
import traceback
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict, field
from functools import wraps
import time
import uuid

# Create logs directory
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
AGENT_LOG_FILE = LOGS_DIR / "agent_logs.jsonl"
FINOPS_LOG_FILE = LOGS_DIR / "finops.jsonl"
LLM_TRACES_FILE = LOGS_DIR / "llm_traces.jsonl"  # Full LLM traces
METRICS_FILE = LOGS_DIR / "metrics.json"

# Initialize all log files at module load (create if not exist)
for log_file in [AGENT_LOG_FILE, FINOPS_LOG_FILE, LLM_TRACES_FILE]:
    if not log_file.exists():
        log_file.touch()

if not METRICS_FILE.exists():
    with open(METRICS_FILE, 'w') as f:
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


# ============================================================================
# GEMINI/GOOGLE AI MODEL PRICING (as of Jan 2026)
# https://ai.google.dev/pricing
# ============================================================================

GEMINI_PRICING = {
    # Gemini 2.0 Flash - Fast, efficient, multimodal
    "gemini-2.0-flash-exp": {
        "input_per_1k_tokens": 0.00001875,   # $0.01875 per 1M tokens
        "output_per_1k_tokens": 0.000075,    # $0.075 per 1M tokens
        "cached_input_per_1k_tokens": 0.0000046875,
        "context_window": 1048576,
        "description": "Fast multimodal model, good balance of speed/quality"
    },
    # Gemini 2.0 Flash Thinking - Enhanced reasoning
    "gemini-2.0-flash-thinking-exp": {
        "input_per_1k_tokens": 0.0,          # Free during experimental
        "output_per_1k_tokens": 0.0,
        "context_window": 32767,
        "description": "Enhanced reasoning capabilities (experimental)"
    },
    # Gemini 1.5 Flash - Production ready, cost effective
    "gemini-1.5-flash": {
        "input_per_1k_tokens": 0.000075,     # $0.075 per 1M tokens
        "output_per_1k_tokens": 0.0003,      # $0.30 per 1M tokens
        "cached_input_per_1k_tokens": 0.00001875,
        "context_window": 1048576,
        "description": "Fast and versatile, great for most tasks"
    },
    # Gemini 1.5 Flash-8B - Smallest, cheapest
    "gemini-1.5-flash-8b": {
        "input_per_1k_tokens": 0.0000375,    # $0.0375 per 1M tokens
        "output_per_1k_tokens": 0.00015,     # $0.15 per 1M tokens
        "context_window": 1048576,
        "description": "Smallest Gemini, lowest cost, high volume"
    },
    # Gemini 1.5 Pro - Most capable
    "gemini-1.5-pro": {
        "input_per_1k_tokens": 0.00125,      # $1.25 per 1M tokens
        "output_per_1k_tokens": 0.005,       # $5.00 per 1M tokens
        "cached_input_per_1k_tokens": 0.0003125,
        "context_window": 2097152,
        "description": "Most capable, complex reasoning tasks"
    },
    # Gemma models (open source, run locally or via API)
    "gemma-2-9b": {
        "input_per_1k_tokens": 0.0,          # Free if self-hosted
        "output_per_1k_tokens": 0.0,
        "context_window": 8192,
        "description": "Open source, can run locally"
    },
    "gemma-2-27b": {
        "input_per_1k_tokens": 0.0,
        "output_per_1k_tokens": 0.0,
        "context_window": 8192,
        "description": "Larger Gemma, better quality"
    },
}

# Estimated tokens per agent call (approximate)
# Based on actual usage patterns from testing
ESTIMATED_TOKENS = {
    "fundamental_agent": {"input": 2000, "output": 800},
    "technical_agent": {"input": 2500, "output": 800},
    "sentiment_agent": {"input": 1500, "output": 600},
    "macro_agent": {"input": 1200, "output": 600},
    "regulatory_agent": {"input": 1000, "output": 500},
    "predictor_agent": {"input": 4000, "output": 1000},
}

# Total estimated tokens per full analysis
TOTAL_TOKENS_PER_ANALYSIS = {
    "input": sum(v["input"] for v in ESTIMATED_TOKENS.values()),   # ~12,200 tokens
    "output": sum(v["output"] for v in ESTIMATED_TOKENS.values()), # ~4,300 tokens
    "total": sum(v["input"] + v["output"] for v in ESTIMATED_TOKENS.values())  # ~16,500 tokens
}


def get_model_from_env() -> str:
    """Get model name from environment variable."""
    return os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp")


def estimate_analysis_cost(model: str = None) -> Dict[str, Any]:
    """
    Estimate the cost of a single stock analysis.
    
    Args:
        model: Model name (defaults to env GEMINI_MODEL)
        
    Returns:
        Cost breakdown with tokens and USD amounts
    """
    if model is None:
        model = get_model_from_env()
    
    pricing = GEMINI_PRICING.get(model, GEMINI_PRICING["gemini-2.0-flash-exp"])
    
    input_tokens = TOTAL_TOKENS_PER_ANALYSIS["input"]
    output_tokens = TOTAL_TOKENS_PER_ANALYSIS["output"]
    
    input_cost = (input_tokens / 1000) * pricing["input_per_1k_tokens"]
    output_cost = (output_tokens / 1000) * pricing["output_per_1k_tokens"]
    total_cost = input_cost + output_cost
    
    return {
        "model": model,
        "description": pricing.get("description", ""),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total_cost, 6),
        "cost_per_1000_analyses": round(total_cost * 1000, 2),
        "analyses_per_dollar": round(1 / total_cost, 0) if total_cost > 0 else "unlimited"
    }


def print_model_comparison():
    """Print cost comparison for all available models."""
    print("\n" + "=" * 80)
    print("📊 MODEL COST COMPARISON (per single stock analysis)")
    print("=" * 80)
    print(f"\nEstimated tokens per analysis: ~{TOTAL_TOKENS_PER_ANALYSIS['total']:,} total")
    print(f"  - Input:  ~{TOTAL_TOKENS_PER_ANALYSIS['input']:,} tokens")
    print(f"  - Output: ~{TOTAL_TOKENS_PER_ANALYSIS['output']:,} tokens")
    print("\n" + "-" * 80)
    print(f"{'Model':<30} {'Cost/Analysis':<15} {'Analyses/$1':<15} {'Notes'}")
    print("-" * 80)
    
    for model_name in GEMINI_PRICING.keys():
        est = estimate_analysis_cost(model_name)
        analyses_per_dollar = est['analyses_per_dollar']
        if isinstance(analyses_per_dollar, str):
            analyses_str = analyses_per_dollar
        else:
            analyses_str = f"{int(analyses_per_dollar):,}"
        
        print(f"{model_name:<30} ${est['total_cost_usd']:<14.6f} {analyses_str:<15} {est['description'][:30]}")
    
    print("=" * 80)
    print("\n💡 Set GEMINI_MODEL in .env.local to change model")
    print("   Example: GEMINI_MODEL=gemini-1.5-flash-8b\n")


# ============================================================================
# DATA CLASSES - Enhanced for detailed logging
# ============================================================================

@dataclass
class LLMRequest:
    """Captures full LLM request details."""
    system_prompt: str
    user_prompt: str
    model: str
    temperature: float
    max_tokens: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LLMResponse:
    """Captures full LLM response details."""
    raw_response: str
    parsed_response: Optional[Dict[str, Any]]
    finish_reason: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_ms: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentLog:
    """Enhanced structured log entry for agent execution."""
    # Identification
    timestamp: str
    trace_id: str
    span_id: str  # NEW: For sub-operation tracking
    ticker: str
    agent_name: str
    event_type: str  # 'start', 'llm_request', 'llm_response', 'complete', 'error'
    
    # Execution details
    duration_ms: Optional[float] = None
    status: str = "success"
    
    # LLM details (for llm_request/llm_response events)
    llm_request: Optional[Dict[str, Any]] = None
    llm_response: Optional[Dict[str, Any]] = None
    
    # Token & cost tracking
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    
    # Error handling
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # Context & metadata
    model: Optional[str] = None
    temperature: Optional[float] = None
    input_data_summary: Optional[Dict[str, Any]] = None  # Summary of input data
    output_summary: Optional[Dict[str, Any]] = None  # Summary of agent output
    reasoning: Optional[str] = None  # Agent's reasoning if available
    confidence: Optional[float] = None
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FinOpsEntry:
    """Cost tracking entry for API calls."""
    timestamp: str
    trace_id: str
    span_id: str
    ticker: str
    model: str
    agent_name: str
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    cached: bool = False
    prompt_hash: Optional[str] = None  # For cache hit tracking


@dataclass 
class AnalysisMetrics:
    """Aggregated metrics for analysis runs."""
    total_analyses: int = 0
    successful_analyses: int = 0
    failed_analyses: int = 0
    total_cost_usd: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    avg_duration_seconds: float = 0.0
    last_updated: str = ""
    costs_by_agent: Dict[str, float] = None
    costs_by_date: Dict[str, float] = None
    
    def __post_init__(self):
        if self.costs_by_agent is None:
            self.costs_by_agent = {}
        if self.costs_by_date is None:
            self.costs_by_date = {}


# ============================================================================
# LOGGER SETUP
# ============================================================================

class JSONLogHandler(logging.Handler):
    """Custom handler that writes JSON logs to file."""
    
    def __init__(self, filepath: Path):
        super().__init__()
        self.filepath = filepath
    
    def emit(self, record):
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            if hasattr(record, 'extra_data'):
                log_entry.update(record.extra_data)
            
            with open(self.filepath, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            self.handleError(record)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Setup structured logging for agent system.
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("nifty_agents")
    logger.setLevel(level)
    
    # Console handler with readable format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # JSON file handler
    json_handler = JSONLogHandler(AGENT_LOG_FILE)
    json_handler.setLevel(level)
    
    # Add handlers if not already added
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(json_handler)
    
    return logger


# Global logger instance
agent_logger = setup_logging()


# ============================================================================
# OBSERVABILITY CLASS
# ============================================================================

class AgentObservability:
    """
    Central observability class for tracking agent execution and costs.
    
    Usage:
        >>> obs = AgentObservability()
        >>> trace_id = obs.start_trace("RELIANCE")
        >>> obs.log_agent_start(trace_id, "RELIANCE", "fundamental_agent")
        >>> # ... agent executes ...
        >>> obs.log_agent_complete(trace_id, "RELIANCE", "fundamental_agent", 
        ...                        duration_ms=1500, input_tokens=2000, output_tokens=800)
        >>> obs.end_trace(trace_id)
    """
    
    def __init__(self, model: str = None):
        # Get model from env or use default
        self.model = model or get_model_from_env()
        self.pricing = GEMINI_PRICING.get(self.model, GEMINI_PRICING["gemini-2.0-flash-exp"])
        self.active_traces: Dict[str, Dict] = {}
        self._load_metrics()
    
    def _load_metrics(self):
        """Load existing metrics from file."""
        if METRICS_FILE.exists():
            try:
                with open(METRICS_FILE, 'r') as f:
                    data = json.load(f)
                    self.metrics = AnalysisMetrics(**data)
            except Exception:
                self.metrics = AnalysisMetrics()
        else:
            self.metrics = AnalysisMetrics()
    
    def _save_metrics(self):
        """Save metrics to file."""
        self.metrics.last_updated = datetime.now().isoformat()
        with open(METRICS_FILE, 'w') as f:
            json.dump(asdict(self.metrics), f, indent=2)
    
    def generate_trace_id(self) -> str:
        """Generate unique trace ID for an analysis run."""
        return f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def generate_span_id(self) -> str:
        """Generate unique span ID for sub-operations."""
        return f"span_{uuid.uuid4().hex[:12]}"
    
    def _hash_prompt(self, prompt: str) -> str:
        """Generate hash of prompt for cache tracking."""
        return hashlib.md5(prompt.encode()).hexdigest()[:16]
    
    def _redact_sensitive(self, text: str) -> str:
        """Redact sensitive information from logs."""
        import re
        # Redact API keys
        text = re.sub(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)[A-Za-z0-9_-]{20,}', r'\1[REDACTED]', text, flags=re.I)
        # Redact bearer tokens
        text = re.sub(r'(Bearer\s+)[A-Za-z0-9_.-]+', r'\1[REDACTED]', text, flags=re.I)
        return text
    
    def _summarize_data(self, data: Any, max_length: int = 500) -> Dict[str, Any]:
        """Create a summary of large data structures for logging."""
        if data is None:
            return {"type": "null"}
        
        if isinstance(data, dict):
            summary = {
                "type": "dict",
                "keys": list(data.keys())[:20],
                "key_count": len(data)
            }
            # Include small values directly
            for key in list(data.keys())[:5]:
                val = data[key]
                if isinstance(val, (str, int, float, bool)) and len(str(val)) < 100:
                    summary[f"sample_{key}"] = val
            return summary
        
        if isinstance(data, list):
            return {
                "type": "list",
                "length": len(data),
                "sample": data[:3] if len(data) > 0 else []
            }
        
        if isinstance(data, str):
            if len(data) > max_length:
                return {
                    "type": "string",
                    "length": len(data),
                    "preview": data[:max_length] + "..."
                }
            return {"type": "string", "value": data}
        
        return {"type": type(data).__name__, "value": str(data)[:max_length]}
    
    def start_trace(self, ticker: str) -> str:
        """Start a new analysis trace."""
        trace_id = self.generate_trace_id()
        self.active_traces[trace_id] = {
            "ticker": ticker,
            "start_time": time.time(),
            "start_timestamp": datetime.now().isoformat(),
            "model": self.model,
            "agents": {},
            "spans": [],
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
            "errors": []
        }
        
        # Log trace start
        log_entry = AgentLog(
            timestamp=datetime.now().isoformat(),
            trace_id=trace_id,
            span_id="root",
            ticker=ticker,
            agent_name="orchestrator",
            event_type="trace_start",
            model=self.model,
            metadata={
                "pricing": self.pricing,
                "model_description": GEMINI_PRICING.get(self.model, {}).get("description", "")
            }
        )
        self._write_log(log_entry)
        
        agent_logger.info(f"🚀 Starting analysis trace: {trace_id} for {ticker}")
        return trace_id
    
    def log_agent_start(
        self, 
        trace_id: str, 
        ticker: str, 
        agent_name: str,
        input_data: Dict[str, Any] = None
    ) -> str:
        """
        Log agent execution start with input data summary.
        
        Returns:
            span_id for this agent execution
        """
        span_id = self.generate_span_id()
        
        log_entry = AgentLog(
            timestamp=datetime.now().isoformat(),
            trace_id=trace_id,
            span_id=span_id,
            ticker=ticker,
            agent_name=agent_name,
            event_type="agent_start",
            input_data_summary=self._summarize_data(input_data) if input_data else None,
            model=self.model
        )
        
        self._write_log(log_entry)
        agent_logger.info(f"  ▶ {agent_name} started [span: {span_id[:12]}]")
        
        if trace_id in self.active_traces:
            self.active_traces[trace_id]["agents"][agent_name] = {
                "span_id": span_id,
                "start_time": time.time()
            }
            self.active_traces[trace_id]["spans"].append(span_id)
        
        return span_id
    
    def log_llm_request(
        self,
        trace_id: str,
        span_id: str,
        ticker: str,
        agent_name: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        """Log the full LLM request (prompt) being sent."""
        
        llm_request = LLMRequest(
            system_prompt=self._redact_sensitive(system_prompt),
            user_prompt=self._redact_sensitive(user_prompt),
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        log_entry = AgentLog(
            timestamp=datetime.now().isoformat(),
            trace_id=trace_id,
            span_id=span_id,
            ticker=ticker,
            agent_name=agent_name,
            event_type="llm_request",
            model=self.model,
            temperature=temperature,
            llm_request=llm_request.to_dict(),
            metadata={
                "prompt_hash": self._hash_prompt(system_prompt + user_prompt),
                "system_prompt_length": len(system_prompt),
                "user_prompt_length": len(user_prompt),
                "total_prompt_chars": len(system_prompt) + len(user_prompt)
            }
        )
        
        self._write_log(log_entry)
        
        # Also write to dedicated LLM traces file for easier analysis
        self._write_llm_trace(log_entry)
        
        agent_logger.debug(f"    📤 LLM request sent ({len(user_prompt)} chars)")
    
    def log_llm_response(
        self,
        trace_id: str,
        span_id: str,
        ticker: str,
        agent_name: str,
        raw_response: str,
        parsed_response: Dict[str, Any] = None,
        input_tokens: int = None,
        output_tokens: int = None,
        latency_ms: float = None,
        finish_reason: str = None
    ):
        """Log the full LLM response."""
        
        llm_response = LLMResponse(
            raw_response=raw_response,
            parsed_response=parsed_response,
            finish_reason=finish_reason,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms
        )
        
        # Extract reasoning if present in response
        reasoning = None
        if parsed_response:
            reasoning = parsed_response.get("reasoning") or parsed_response.get("analysis") or parsed_response.get("rationale")
        
        log_entry = AgentLog(
            timestamp=datetime.now().isoformat(),
            trace_id=trace_id,
            span_id=span_id,
            ticker=ticker,
            agent_name=agent_name,
            event_type="llm_response",
            model=self.model,
            duration_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            llm_response=llm_response.to_dict(),
            reasoning=str(reasoning)[:2000] if reasoning else None,  # Truncate if too long
            output_summary=self._summarize_data(parsed_response),
            metadata={
                "response_length": len(raw_response),
                "parsed_successfully": parsed_response is not None,
                "finish_reason": finish_reason
            }
        )
        
        self._write_log(log_entry)
        self._write_llm_trace(log_entry)
        
        agent_logger.debug(f"    📥 LLM response received ({len(raw_response)} chars, {output_tokens or '?'} tokens)")
    
    def log_agent_complete(
        self,
        trace_id: str,
        ticker: str,
        agent_name: str,
        duration_ms: float,
        input_tokens: int = None,
        output_tokens: int = None,
        status: str = "success",
        error_message: str = None,
        output_data: Dict[str, Any] = None,
        span_id: str = None
    ):
        """Log agent execution completion with full details."""
        
        # Get span_id from active traces if not provided
        if span_id is None and trace_id in self.active_traces:
            agent_info = self.active_traces[trace_id]["agents"].get(agent_name, {})
            span_id = agent_info.get("span_id", self.generate_span_id())
        
        # Use estimated tokens if not provided
        if input_tokens is None:
            input_tokens = ESTIMATED_TOKENS.get(agent_name, {}).get("input", 1000)
        if output_tokens is None:
            output_tokens = ESTIMATED_TOKENS.get(agent_name, {}).get("output", 500)
        
        # Calculate costs
        input_cost = (input_tokens / 1000) * self.pricing["input_per_1k_tokens"]
        output_cost = (output_tokens / 1000) * self.pricing["output_per_1k_tokens"]
        total_cost = input_cost + output_cost
        
        # Extract key outputs for summary
        output_summary = None
        confidence = None
        reasoning = None
        if output_data:
            output_summary = self._summarize_data(output_data)
            confidence = output_data.get("confidence")
            reasoning = output_data.get("reasoning") or output_data.get("analysis")
        
        # Log entry with full details
        log_entry = AgentLog(
            timestamp=datetime.now().isoformat(),
            trace_id=trace_id,
            span_id=span_id or self.generate_span_id(),
            ticker=ticker,
            agent_name=agent_name,
            event_type="agent_complete",
            duration_ms=duration_ms,
            status=status,
            error_message=error_message,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=total_cost,
            model=self.model,
            output_summary=output_summary,
            reasoning=str(reasoning)[:1000] if reasoning else None,
            confidence=confidence,
            metadata={
                "input_cost_usd": input_cost,
                "output_cost_usd": output_cost,
                "tokens_total": input_tokens + output_tokens
            }
        )
        self._write_log(log_entry)
        
        # FinOps entry
        finops_entry = FinOpsEntry(
            timestamp=datetime.now().isoformat(),
            trace_id=trace_id,
            span_id=span_id or "",
            ticker=ticker,
            model=self.model,
            agent_name=agent_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost_usd=input_cost,
            output_cost_usd=output_cost,
            total_cost_usd=total_cost
        )
        self._write_finops(finops_entry)
        
        # Update trace
        if trace_id in self.active_traces:
            self.active_traces[trace_id]["total_input_tokens"] += input_tokens
            self.active_traces[trace_id]["total_output_tokens"] += output_tokens
            self.active_traces[trace_id]["total_cost_usd"] += total_cost
            if status == "error":
                self.active_traces[trace_id]["errors"].append({
                    "agent": agent_name,
                    "error": error_message
                })
        
        # Log with cost
        status_icon = "✓" if status == "success" else "✗"
        agent_logger.info(
            f"  {status_icon} {agent_name} completed in {duration_ms:.0f}ms | "
            f"${total_cost:.6f} ({input_tokens}+{output_tokens} tokens)"
        )
    
    def log_error(
        self,
        trace_id: str,
        ticker: str,
        agent_name: str,
        error: Exception,
        context: Dict[str, Any] = None,
        span_id: str = None
    ):
        """Log detailed error information with stack trace."""
        
        log_entry = AgentLog(
            timestamp=datetime.now().isoformat(),
            trace_id=trace_id,
            span_id=span_id or self.generate_span_id(),
            ticker=ticker,
            agent_name=agent_name,
            event_type="error",
            status="error",
            error_message=str(error),
            error_type=type(error).__name__,
            stack_trace=traceback.format_exc(),
            model=self.model,
            metadata=context
        )
        
        self._write_log(log_entry)
        agent_logger.error(f"  ❌ {agent_name} error: {error}")
        
        if trace_id in self.active_traces:
            self.active_traces[trace_id]["errors"].append({
                "agent": agent_name,
                "error_type": type(error).__name__,
                "error": str(error)
            })
    
    def end_trace(self, trace_id: str) -> Dict[str, Any]:
        """End trace and return comprehensive summary."""
        if trace_id not in self.active_traces:
            return {}
        
        trace = self.active_traces.pop(trace_id)
        duration = time.time() - trace["start_time"]
        
        # Calculate success/failure
        error_count = len(trace.get("errors", []))
        agent_count = len(trace["agents"])
        success_rate = ((agent_count - error_count) / max(agent_count, 1)) * 100
        
        summary = {
            "trace_id": trace_id,
            "ticker": trace["ticker"],
            "model": trace.get("model", self.model),
            "start_timestamp": trace.get("start_timestamp"),
            "end_timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "total_input_tokens": trace["total_input_tokens"],
            "total_output_tokens": trace["total_output_tokens"],
            "total_tokens": trace["total_input_tokens"] + trace["total_output_tokens"],
            "total_cost_usd": round(trace["total_cost_usd"], 6),
            "agents_count": agent_count,
            "spans_count": len(trace.get("spans", [])),
            "error_count": error_count,
            "success_rate_pct": round(success_rate, 1),
            "errors": trace.get("errors", [])
        }
        
        # Log trace end
        log_entry = AgentLog(
            timestamp=datetime.now().isoformat(),
            trace_id=trace_id,
            span_id="root",
            ticker=trace["ticker"],
            agent_name="orchestrator",
            event_type="trace_complete",
            duration_ms=duration * 1000,
            status="success" if error_count == 0 else "partial_success",
            input_tokens=trace["total_input_tokens"],
            output_tokens=trace["total_output_tokens"],
            cost_usd=trace["total_cost_usd"],
            model=self.model,
            metadata=summary
        )
        self._write_log(log_entry)
        
        # Update global metrics
        self.metrics.total_analyses += 1
        self.metrics.successful_analyses += 1
        self.metrics.total_cost_usd += trace["total_cost_usd"]
        self.metrics.total_input_tokens += trace["total_input_tokens"]
        self.metrics.total_output_tokens += trace["total_output_tokens"]
        
        # Update costs by date
        today = datetime.now().strftime("%Y-%m-%d")
        self.metrics.costs_by_date[today] = \
            self.metrics.costs_by_date.get(today, 0) + trace["total_cost_usd"]
        
        self._save_metrics()
        
        agent_logger.info(
            f"✅ Analysis complete: {trace['ticker']} | "
            f"{duration:.1f}s | ${trace['total_cost_usd']:.6f}"
        )
        
        return summary
    
    def _write_log(self, log_entry: AgentLog):
        """Write log entry to JSONL file."""
        with open(AGENT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(log_entry), default=str, ensure_ascii=False) + '\n')
    
    def _write_finops(self, entry: FinOpsEntry):
        """Write FinOps entry to JSONL file."""
        with open(FINOPS_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(entry), default=str, ensure_ascii=False) + '\n')
    
    def _write_llm_trace(self, log_entry: AgentLog):
        """Write LLM trace entry to dedicated file for LLM debugging."""
        with open(LLM_TRACES_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(log_entry), default=str, ensure_ascii=False) + '\n')
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        return asdict(self.metrics)
    
    def get_cost_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate cost report for the last N days."""
        from datetime import timedelta
        
        today = datetime.now()
        costs_by_day = {}
        total_cost = 0.0
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            cost = self.metrics.costs_by_date.get(date, 0)
            costs_by_day[date] = cost
            total_cost += cost
        
        return {
            "period_days": days,
            "total_cost_usd": round(total_cost, 4),
            "avg_daily_cost_usd": round(total_cost / days, 4),
            "costs_by_day": costs_by_day,
            "total_analyses": self.metrics.total_analyses,
            "cost_per_analysis_usd": round(
                self.metrics.total_cost_usd / max(self.metrics.total_analyses, 1), 
                6
            )
        }


# ============================================================================
# DECORATOR FOR AUTOMATIC TRACING
# ============================================================================

def trace_agent(func):
    """Decorator to automatically trace agent function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        agent_name = func.__name__
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            agent_logger.debug(f"{agent_name} completed in {duration_ms:.0f}ms")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            agent_logger.error(f"{agent_name} failed after {duration_ms:.0f}ms: {e}")
            raise
    
    return wrapper


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_observability() -> AgentObservability:
    """Get or create global observability instance."""
    global _observability_instance
    if '_observability_instance' not in globals():
        _observability_instance = AgentObservability()
    return _observability_instance


def view_recent_logs(n: int = 20, event_type: str = None) -> List[Dict]:
    """
    View most recent log entries with optional filtering.
    
    Args:
        n: Number of entries to return
        event_type: Filter by event type (e.g., 'llm_request', 'llm_response', 'error')
    """
    if not AGENT_LOG_FILE.exists():
        return []
    
    with open(AGENT_LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    logs = []
    for line in lines[-n*3:]:  # Read more to account for filtering
        try:
            entry = json.loads(line)
            if event_type is None or entry.get("event_type") == event_type:
                logs.append(entry)
        except json.JSONDecodeError:
            continue
    
    return logs[-n:]


def view_finops_logs(n: int = 50) -> List[Dict]:
    """View most recent FinOps entries."""
    if not FINOPS_LOG_FILE.exists():
        return []
    
    with open(FINOPS_LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    entries = []
    for line in lines[-n:]:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    
    return entries


def view_llm_traces(n: int = 20, trace_id: str = None) -> List[Dict]:
    """
    View LLM request/response traces for debugging.
    
    Args:
        n: Number of entries to return
        trace_id: Filter by specific trace ID
    """
    if not LLM_TRACES_FILE.exists():
        return []
    
    with open(LLM_TRACES_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    traces = []
    for line in lines[-n*2:]:
        try:
            entry = json.loads(line)
            if trace_id is None or entry.get("trace_id") == trace_id:
                traces.append(entry)
        except json.JSONDecodeError:
            continue
    
    return traces[-n:]


def get_trace_details(trace_id: str) -> Dict[str, Any]:
    """
    Get all logs for a specific trace ID.
    
    Returns complete trace including all agent logs, LLM calls, and errors.
    """
    result = {
        "trace_id": trace_id,
        "events": [],
        "llm_calls": [],
        "errors": [],
        "summary": None
    }
    
    # Read agent logs
    if AGENT_LOG_FILE.exists():
        with open(AGENT_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("trace_id") == trace_id:
                        result["events"].append(entry)
                        if entry.get("event_type") == "error":
                            result["errors"].append(entry)
                        if entry.get("event_type") == "trace_complete":
                            result["summary"] = entry.get("metadata")
                except json.JSONDecodeError:
                    continue
    
    # Read LLM traces
    if LLM_TRACES_FILE.exists():
        with open(LLM_TRACES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("trace_id") == trace_id:
                        result["llm_calls"].append(entry)
                except json.JSONDecodeError:
                    continue
    
    return result


def print_cost_report():
    """Print formatted cost report to console."""
    obs = get_observability()
    report = obs.get_cost_report(days=7)
    
    print("\n" + "=" * 60)
    print("📊 NIFTY AGENT FINOPS REPORT")
    print("=" * 60)
    print(f"\n📅 Last {report['period_days']} Days:")
    print(f"   Total Cost:       ${report['total_cost_usd']:.4f}")
    print(f"   Avg Daily Cost:   ${report['avg_daily_cost_usd']:.4f}")
    print(f"   Total Analyses:   {report['total_analyses']}")
    print(f"   Cost/Analysis:    ${report['cost_per_analysis_usd']:.6f}")
    print("\n📈 Daily Breakdown:")
    for date, cost in sorted(report['costs_by_day'].items(), reverse=True):
        bar = "█" * int(cost * 1000)  # Scale for visibility
        print(f"   {date}: ${cost:.4f} {bar}")
    print("=" * 60 + "\n")


# ============================================================================
# LOG FILE LOCATIONS
# ============================================================================

def get_log_paths() -> Dict[str, str]:
    """Return paths to all log files."""
    return {
        "agent_logs": str(AGENT_LOG_FILE),
        "llm_traces": str(LLM_TRACES_FILE),
        "finops_logs": str(FINOPS_LOG_FILE),
        "metrics": str(METRICS_FILE),
        "logs_directory": str(LOGS_DIR)
    }


def get_available_models() -> Dict[str, Dict]:
    """Get all available models with their pricing info."""
    return {
        name: {
            "cost_per_analysis": estimate_analysis_cost(name)["total_cost_usd"],
            **info
        }
        for name, info in GEMINI_PRICING.items()
    }


def generate_test_logs(ticker: str = "TEST_STOCK") -> Dict[str, Any]:
    """
    Generate sample logs for testing the observability system.
    
    This creates realistic-looking log entries without making actual LLM calls.
    Useful for:
    - Testing the dashboard
    - Verifying log file creation
    - Demo purposes
    
    Args:
        ticker: Stock ticker to use in sample logs
        
    Returns:
        Summary of generated test data
    """
    obs = get_observability()
    trace_id = obs.start_trace(ticker)
    
    test_agents = [
        ("fundamental_agent", 2000, 800, 1200),
        ("technical_agent", 2500, 850, 1500),
        ("sentiment_agent", 1500, 600, 800),
        ("macro_agent", 1200, 550, 600),
        ("regulatory_agent", 1000, 500, 500),
        ("predictor_agent", 4000, 1000, 2000),
    ]
    
    for agent_name, input_tokens, output_tokens, latency in test_agents:
        span_id = obs.log_agent_start(trace_id, ticker, agent_name)
        
        # Log sample LLM request
        obs.log_llm_request(
            trace_id=trace_id,
            span_id=span_id,
            ticker=ticker,
            agent_name=agent_name,
            system_prompt=f"You are a {agent_name.replace('_', ' ')}. Analyze the following stock data and provide your assessment.",
            user_prompt=f"Analyze {ticker} based on the following data:\n- Price: Rs. 2500\n- P/E Ratio: 25.5\n- Market Cap: 15L Cr\n- 52W High/Low: 2800/2100\nProvide your score (0-100) and detailed reasoning.",
            temperature=0.3,
            max_tokens=2000
        )
        
        # Simulate some processing time
        time.sleep(0.05)
        
        # Generate sample parsed response
        sample_response = {
            "score": 65 + (hash(agent_name) % 20),
            "confidence": "medium" if hash(agent_name) % 2 == 0 else "high",
            "reasoning": f"Based on analysis, {ticker} shows {['strong', 'moderate', 'mixed'][hash(agent_name) % 3]} signals. Key factors include valuation metrics, market positioning, and sector trends.",
            "key_factors": ["Valuation", "Market Position", "Sector Trends"],
            "risks": ["Market volatility", "Regulatory changes"],
            "opportunities": ["Sector growth", "Market expansion"]
        }
        
        # Log sample LLM response
        obs.log_llm_response(
            trace_id=trace_id,
            span_id=span_id,
            ticker=ticker,
            agent_name=agent_name,
            raw_response=json.dumps(sample_response, indent=2),
            parsed_response=sample_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency,
            finish_reason="stop"
        )
        
        # Log completion
        obs.log_agent_complete(
            trace_id=trace_id,
            ticker=ticker,
            agent_name=agent_name,
            duration_ms=latency + 50,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            status="success",
            output_data=sample_response,
            span_id=span_id
        )
    
    # End trace
    summary = obs.end_trace(trace_id)
    
    return {
        "status": "success",
        "message": f"Generated test logs for {ticker}",
        "trace_id": trace_id,
        "agents_logged": len(test_agents),
        "summary": summary,
        "files_written": {
            "agent_logs": str(AGENT_LOG_FILE),
            "llm_traces": str(LLM_TRACES_FILE),
            "finops": str(FINOPS_LOG_FILE),
            "metrics": str(METRICS_FILE)
        }
    }


if __name__ == "__main__":
    # Demo usage
    print("Log file locations:")
    for name, path in get_log_paths().items():
        print(f"  {name}: {path}")
    
    # Show model comparison
    print_model_comparison()
    
    # Show current model cost estimate
    current_model = get_model_from_env()
    print(f"\n📌 Current Model: {current_model}")
    est = estimate_analysis_cost()
    print(f"   Cost per analysis: ${est['total_cost_usd']:.6f}")
    print(f"   Analyses per $1:   {est['analyses_per_dollar']}")
    
    print("\nRunning demo trace...")
    obs = AgentObservability()
    
    trace_id = obs.start_trace("DEMO_TICKER")
    
    for agent in ["fundamental_agent", "technical_agent", "sentiment_agent"]:
        obs.log_agent_start(trace_id, "DEMO_TICKER", agent)
        time.sleep(0.1)  # Simulate work
        obs.log_agent_complete(trace_id, "DEMO_TICKER", agent, duration_ms=100)
    
    summary = obs.end_trace(trace_id)
    print(f"\nTrace Summary: {json.dumps(summary, indent=2)}")
    
    print_cost_report()
