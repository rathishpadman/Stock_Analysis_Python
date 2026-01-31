# NIFTY Agent System - Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Agentic AI Fundamentals](#agentic-ai-fundamentals)
3. [Design Pattern Deep Dive](#design-pattern-deep-dive)
4. [Architecture](#architecture)
5. [Agent Flow Explained](#agent-flow-explained-for-beginners)
6. [Tool Calling Architecture](#tool-calling-architecture)
7. [Memory & State Management](#memory--state-management)
8. [Agent Personas & System Prompts](#agent-personas--system-prompts)
9. [Advanced Design Elements](#advanced-design-elements)
10. [Components](#components)
11. [Data Sources](#data-sources)
12. [API Reference](#api-reference)
13. [Setup & Installation](#setup--installation)
14. [Usage Examples](#usage-examples)
15. [Testing](#testing)
16. [Troubleshooting](#troubleshooting)

---

## Overview

The NIFTY Agent System is a **multi-agent AI solution** for comprehensive analysis of Indian equities (NSE-listed stocks). It uses 6 specialized AI agents, each expert in a different aspect of stock analysis, to provide deep-dive investment insights.

### What Problem Does It Solve?

Traditional stock analysis requires expertise in multiple domains:
- Financial statement analysis
- Technical chart reading
- News sentiment interpretation
- Macro-economic understanding
- Regulatory compliance awareness

Our system automates this by having **specialized AI agents** collaborate to analyze a stock from every angle, then synthesize a final recommendation.

### Key Features

- ✅ **6 Specialized Agents**: Each focused on one analysis domain
- ✅ **Parallel Execution**: Agents run simultaneously for fast results
- ✅ **Indian Market Focus**: Tailored for NSE/BSE listed stocks
- ✅ **Multiple Data Sources**: yfinance, RSS feeds, Supabase
- ✅ **REST API**: Easy integration with any frontend
- ✅ **Caching**: Reduces API calls and improves response time
- ✅ **Observability**: Full tracing, token accounting, and cost tracking
- ✅ **Centralized Context**: All agents share the same data snapshot

---

## Agentic AI Fundamentals

Before diving into our implementation, let's understand the core concepts of Agentic AI that this system leverages.

### What is an "Agent" vs a "Workflow"?

| Aspect | Workflow (Deterministic) | Agent (Autonomous) |
|--------|--------------------------|-------------------|
| **Control Flow** | Pre-defined, step-by-step | Dynamic, decided at runtime |
| **Decision Making** | Hardcoded conditionals | LLM reasoning |
| **Tool Selection** | Pre-mapped to steps | Agent chooses tools |
| **Error Handling** | Try/catch blocks | Self-correction loops |
| **Example** | ETL Pipeline | ChatGPT with plugins |

### Where Does NIFTY Fit?

**NIFTY is a Hybrid System**: It combines **workflow orchestration** with **agentic reasoning**.

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                              │
│                    (Workflow: Deterministic)                     │
│                                                                  │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │  STEP 1: Validate ticker         [Code Logic]             │ │
│   │  STEP 2: Fetch data in parallel  [Code Logic]             │ │
│   │  STEP 3: Dispatch to agents      [Code Logic]             │ │
│   │  STEP 4: Collect responses       [Code Logic]             │ │
│   │  STEP 5: Call predictor          [Code Logic]             │ │
│   │  STEP 6: Cache and return        [Code Logic]             │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │              SPECIALIST AGENTS                             │ │
│   │             (Agentic: LLM Reasoning)                       │ │
│   │                                                            │ │
│   │   Each agent receives data and uses LLM to:                │ │
│   │   • Interpret financial metrics                            │ │
│   │   • Identify patterns in price data                        │ │
│   │   • Synthesize news sentiment                              │ │
│   │   • Generate structured recommendations                    │ │
│   └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Why this hybrid approach?**
- **Reliability**: The outer workflow ensures predictable execution order
- **Intelligence**: The inner agents apply sophisticated reasoning
- **Performance**: Deterministic data fetching is faster than agent tool loops
- **Cost**: Pre-fetching data reduces LLM token usage vs. letting agents call tools iteratively

### Agentic Design Patterns Overview

The Agentic AI community has identified several design patterns. Here's how NIFTY uses them:

| Pattern | NIFTY Usage | Location |
|---------|-------------|----------|
| **Multi-Agent Collaboration** | ✅ 6 specialized agents | `orchestrator.py` |
| **Supervisor-Worker** | ✅ Orchestrator supervises agents | `_call_agent()` method |
| **Parallelization** | ✅ Fan-out/Fan-in execution | `ThreadPoolExecutor` |
| **Tool Use** | ✅ Data fetchers as tools | `tools/` directory |
| **Centralized Memory** | ✅ Shared `base_data` context | `_gather_base_data()` |
| **Reflection** | ⚠️ Partial (Predictor reviews) | Predictor synthesis |
| **Planning** | ❌ Not implemented | N/A |
| **ReAct Loop** | ❌ Not implemented (by design) | N/A |

---

## Design Pattern Deep Dive

### Pattern 1: Multi-Agent Collaboration (Core Pattern)

**What it is**: Multiple specialized AI agents work together on a complex task, each contributing unique expertise.

**NIFTY Implementation**:
```
User Query: "Analyze RELIANCE"
          │
          ▼
    ┌─────────────────────────────────────────────────────────┐
    │              ORCHESTRATOR (Coordinator)                  │
    └───────────┬────────┬────────┬────────┬────────┬────────┘
                │        │        │        │        │
                ▼        ▼        ▼        ▼        ▼
         ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐
         │FUNDAMENTAL││TECHNICAL ││SENTIMENT ││  MACRO   ││REGULATORY│
         │  AGENT   ││  AGENT   ││  AGENT   ││  AGENT   ││  AGENT   │
         │          ││          ││          ││          ││          │
         │ "P/E=25, ││ "RSI=55, ││ "3 +ve   ││ "VIX=15, ││ "No SEBI │
         │  ROE=12%"││  bullish"││  news"   ││  benign" ││  issues" │
         └────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘
              │           │           │           │           │
              └───────────┴───────────┼───────────┴───────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │   PREDICTOR AGENT      │
                         │   (Synthesizer)        │
                         │                        │
                         │   Weighs all signals:  │
                         │   → BUY @ 72/100       │
                         └────────────────────────┘
```

**Code Location**: `orchestrator.py` lines 850-920

```python
# Fan-out: All specialists run in parallel
agent_names = ["fundamental_agent", "technical_agent", "sentiment_agent", 
               "macro_agent", "regulatory_agent"]

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(self._call_agent, name, base_data, trace_id): name
               for name in agent_names}
    # ... collect results
    
# Fan-in: Predictor synthesizes all responses
prediction = self._call_predictor(ticker_clean, agent_analyses, trace_id)
```

**Why Multi-Agent?**
1. **Separation of Concerns**: Each agent focuses on one domain, reducing hallucination
2. **Parallelism**: 5x speedup by running agents simultaneously
3. **Explainability**: Each agent's reasoning is independently auditable
4. **Modularity**: Add/remove agents without affecting others

---

### Pattern 2: Supervisor-Worker Hierarchy

**What it is**: A supervisor agent coordinates worker agents, deciding when to invoke them and how to handle their outputs.

**NIFTY Implementation**:
- **Supervisor**: The `NiftyAgentOrchestrator` class (deterministic Python code)
- **Workers**: The 6 LLM-based agents

Unlike pure agentic systems where an LLM supervisor decides which agents to call, NIFTY uses **deterministic orchestration** for reliability:

```python
class NiftyAgentOrchestrator:
    """
    SUPERVISOR RESPONSIBILITIES:
    1. Validates input (ticker symbol check)
    2. Gathers all required data
    3. Decides which agents to invoke (all 5 specialists)
    4. Sets timeout boundaries (30s default)
    5. Handles failures gracefully
    6. Invokes synthesizer (Predictor)
    """
    
    def _call_agent(self, agent_name: str, base_data: Dict, trace_id: str):
        """
        WORKER INVOCATION:
        - Retrieves agent-specific configuration
        - Filters data for the agent (token optimization)
        - Sends prompt to LLM
        - Parses and validates response
        - Logs to observability system
        """
```

**Supervisor vs. Pure Agentic Comparison**:

| Aspect | Pure Agentic (LLM Supervisor) | NIFTY (Code Supervisor) |
|--------|-------------------------------|-------------------------|
| Routing | LLM decides agents | All agents always called |
| Reliability | Variable (LLM may skip) | 100% predictable |
| Speed | Slower (routing overhead) | Faster (direct dispatch) |
| Cost | Higher (supervisor tokens) | Lower (no supervisor LLM) |

---

### Pattern 3: Parallelization (Fan-out/Fan-in)

**What it is**: Execute multiple independent tasks simultaneously, then aggregate results.

**NIFTY Implementation**:

```
                    ┌─────────────────┐
                    │   BASE DATA     │
                    │  (Shared Input) │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
  ┌───────────┐        ┌───────────┐        ┌───────────┐
  │  Agent 1  │        │  Agent 2  │        │  Agent 3  │
  │   (3.2s)  │        │   (2.8s)  │        │   (3.1s)  │
  └─────┬─────┘        └─────┬─────┘        └─────┬─────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   AGGREGATION   │
                    │  (max: 3.2s)    │
                    └─────────────────┘
```

**Two Levels of Parallelization**:

1. **Data Fetching** (Level 1):
```python
def _gather_base_data(self, ticker: str) -> Dict[str, Any]:
    """6 data sources fetched in parallel"""
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(get_stock_fundamentals, ticker): "fundamentals",
            executor.submit(get_stock_quote, ticker): "quote",
            executor.submit(get_price_history, ticker): "price_history",
            executor.submit(get_macro_indicators): "macro",
            executor.submit(get_stock_news, ticker): "sentiment",
            executor.submit(get_comprehensive_stock_data, ticker): "supabase_data"
        }
```

2. **Agent Execution** (Level 2):
```python
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(self._call_agent, name, base_data): name
               for name in agent_names}
```

**Performance Impact**:
- Sequential: ~15 seconds (5 agents × 3s each)
- Parallel: ~3-5 seconds (wall clock time = slowest agent)
- **Result: 70% reduction in latency**

---

### Pattern 4: Tool Use (Data Fetchers as Tools)

**What it is**: Agents invoke external tools to gather information or take actions.

**NIFTY's Approach - Pre-fetched Tools**:

Unlike typical ReAct patterns where agents iteratively call tools:
```
# Traditional ReAct (NOT used in NIFTY):
Agent thinks → Calls tool → Observes result → Thinks again → Calls another tool...
```

NIFTY uses **Centralized Tool Invocation**:
```
# NIFTY Pattern:
Orchestrator calls ALL tools → Gathers data → Passes to agents → Agents reason
```

**Tool Definitions** (`tools/` directory):

| Tool | File | Function | Data Returned |
|------|------|----------|---------------|
| Stock Fundamentals | `nifty_fetcher.py` | `get_stock_fundamentals()` | P/E, ROE, debt ratios |
| Live Quote | `nifty_fetcher.py` | `get_stock_quote()` | Current price, volume |
| Price History | `nifty_fetcher.py` | `get_price_history()` | 250 days OHLCV |
| Macro Indicators | `india_macro_fetcher.py` | `get_macro_indicators()` | VIX, RBI rates |
| News & Sentiment | `india_news_fetcher.py` | `get_stock_news()` | Headlines, sentiment scores |
| Pipeline Scores | `supabase_fetcher.py` | `get_comprehensive_stock_data()` | Pre-computed scores |

**Why Pre-fetching?**

| Approach | Tokens Used | Latency | Cost |
|----------|-------------|---------|------|
| Agent Tool Loops | ~50k/request | 15-30s | $0.15 |
| Pre-fetched Data | ~12k/request | 3-5s | $0.04 |

**Trade-off**: We sacrifice dynamic tool selection for efficiency. Our use case (stock analysis) has a fixed set of required data, making pre-fetching optimal.

---

### Pattern 5: Centralized Context (Shared Memory)

**What it is**: A central memory store that all agents can read from, ensuring consistency.

**NIFTY Implementation**:

```python
def _gather_base_data(self, ticker: str) -> Dict[str, Any]:
    """
    CENTRALIZED CONTEXT BUILDER
    
    Creates a single source of truth that all agents share:
    - Same price data timestamp
    - Same news articles
    - Same macro indicators
    
    This prevents "context drift" where agents might see
    different data if they fetched independently.
    """
    base_data = {
        "ticker": ticker,
        "timestamp": datetime.now().isoformat(),
        "fundamentals": {...},
        "quote": {...},
        "price_history": {...},
        "macro": {...},
        "sentiment": {...},
        "supabase_data": {...}
    }
    return base_data
```

**Context Filtering for Token Efficiency**:

Not all agents need all data. The orchestrator filters data per-agent:

```python
def _get_agent_specific_data(self, agent_name: str, base_data: Dict) -> Dict:
    """
    TOKEN OPTIMIZATION: Each agent gets only what it needs
    
    Technical Agent: 50 days price data (not 250)
    Macro Agent: No price data at all
    Sentiment Agent: News + VIX only
    """
    if agent_name == "technical_agent":
        price_data = base_data["price_history"]["data"][:50]  # Only 50 days
        return {...}
    elif agent_name == "macro_agent":
        # Macro doesn't need price history!
        return {"macro": base_data["macro"], "sector": ...}
```

**Token Savings**:
- Full data to all agents: ~25,000 tokens/request
- Filtered data: ~11,500 tokens/request
- **Savings: 54%**

---

### Pattern 6: Reflection (Predictor Synthesis)

**What it is**: An agent reviews and critiques its own or others' outputs before finalizing.

**NIFTY's Partial Reflection**:

The **Predictor Agent** acts as a reflection layer:

```python
def _call_predictor(self, ticker: str, agent_analyses: Dict) -> Dict:
    """
    The Predictor reviews all specialist outputs and:
    1. Identifies conflicting signals
    2. Weighs based on market regime
    3. Synthesizes a final recommendation
    
    This is "reflection" but on OTHER agents' outputs,
    not self-reflection loops.
    """
    prompt = f"""
    You have received analyses from 5 specialized agents for {ticker}.
    Synthesize these into a final investment recommendation.
    
    AGENT ANALYSES:
    {json.dumps(cleaned_analyses, indent=2)}
    
    WEIGHTING GUIDANCE:
    - In high VIX (>20): Weight sentiment/macro higher
    - In low VIX (<15): Weight fundamentals/technicals higher
    - Flag any strong disagreements between agents
    """
```

**What NIFTY Doesn't Have (Yet)**:
- **Self-Reflection Loops**: Agents don't critique and revise their own outputs
- **Iterative Refinement**: No "try again" mechanism for poor quality outputs
- **Debate Pattern**: Agents don't argue with each other

---

### Patterns NOT Used (and Why)

#### ReAct (Reasoning + Acting) Loop

**What it is**: Agent thinks, acts (calls tool), observes result, thinks again, loops until done.

**Why NIFTY Doesn't Use It**:
- Our use case has **fixed data requirements** - we always need the same 6 data types
- ReAct adds **latency** (multiple LLM calls) without benefit for structured analysis
- **Cost**: Each ReAct iteration costs tokens; pre-fetching is cheaper

#### Planning Pattern

**What it is**: Agent creates a step-by-step plan before execution.

**Why NIFTY Doesn't Use It**:
- Our execution plan is **deterministic** (always same 5 agents → predictor)
- Planning adds overhead without flexibility benefit
- Future consideration: Could use for custom analysis requests

#### Debate/Adversarial Pattern

**What it is**: Agents argue opposing viewpoints to stress-test conclusions.

**Why NIFTY Doesn't Use It** (Yet):
- Increases latency and cost significantly
- Could be valuable for high-stakes analysis (e.g., "Devil's advocate" agent)
- Marked for future enhancement

---

### Granular Execution Flow: "Analyze" Button Click

When a user clicks the **"Analyze"** button on the dashboard, the following sequence of operations occurs across the front-end, back-end, and database layers:

#### 1. Front-End Trigger (`AnalyzeButton.tsx`)
- **Action**: Hovering over the button triggers `fetchCachedInfo()`.
- **Logic**: It calls `/api/agent/history/{ticker}` on the Render backend to check for recent analysis.
- **State**: If found, it shows the **"View"** state with a preview of the score and recommendation in a tooltip.
- **Click**: Tapping the button calls the `onAnalyze(ticker)` callback, passing the symbol to the parent `StockTable` which opens the `AIAnalysisModal`.

#### 2. API Request Preparation (`AIAnalysisModal.tsx`)
- **Action**: The modal initializes and immediately hits the analysis endpoint.
- **URL**: `GET https://nifty-agent-api.onrender.com/api/agent/analyze/{ticker}`
- **UI**: Shows real-time progress steps: *"Gathering data..."*, *"Agents analyzing..."*, *"Synthesizing results..."*.

#### 3. Orchestration Logic (`orchestrator.py`)
The `analyze_async()` method in the `NiftyAgentOrchestrator` class manages the core logic:

```python
async def analyze_async(self, ticker: str):
    # Step A: Validate Ticker (NSE check)
    ticker_clean = self._validate_ticker(ticker)
    
    # Step B: Gather Base Data (Parallel Fetching)
    base_data = await self._gather_base_data(ticker_clean)
    # Fetches: yfinance, RSS News, Supabase Pipeline Scores, Macro Indicators
    
    # Step C: Dispatch Specialist Agents (Simultaneous)
    tasks = [self._call_agent(name, base_data) for name in AGENT_NAMES]
    agent_responses = await asyncio.gather(*tasks)
    
    # Step D: Synthesis (Predictor)
    report = await self._call_predictor(ticker_clean, agent_responses)
    
    # Step E: Persistence & Cache
    self._store_analysis_to_supabase(ticker_clean, report) # New!
    self.cache[ticker_clean] = report
    
    return report
```

#### 4. Database Persistence (`ai_analysis_history`)
- **Table**: Results are saved to Supabase to enable historical tracking and tooltips.
- **Schema**:
    - `ticker`: Stock code
    - `composite_score`: Overall 0-100 rating
    - `recommendation`: Final signal (Buy/Hold/Sell)
    - `full_response`: Complete JSON of all agent reasoning
    - `cost_usd`: Token-based API cost tracking

#### 5. User View Delivery
- The report is rendered in a premium glassmorphic modal with expandable reasoning for each agent.
- Export options (PDF/JSON) allow saving the finalized AI research.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER REQUEST                                       │
│                     (e.g., "Analyze RELIANCE")                              │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR                                       │
│                                                                              │
│  1. Validate ticker                                                          │
│  2. Gather base data from all sources                                        │
│  3. Dispatch to specialist agents (in parallel)                              │
│  4. Collect responses                                                        │
│  5. Send to Predictor for synthesis                                          │
│  6. Return final report                                                      │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  DATA FETCHERS  │  │  DATA FETCHERS  │  │  DATA FETCHERS  │
│                 │  │                 │  │                 │
│ nifty_fetcher   │  │ india_macro     │  │ india_news      │
│ (yfinance,NSE)  │  │ (RBI, VIX)      │  │ (RSS, Sentiment)│
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SPECIALIST AGENTS (Parallel)                          │
│                                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐│
│  │ FUNDAMENTAL │ │  TECHNICAL  │ │  SENTIMENT  │ │    MACRO    │ │REGULATORY││
│  │   AGENT     │ │   AGENT     │ │   AGENT     │ │   AGENT     │ │  AGENT  ││
│  │             │ │             │ │             │ │             │ │         ││
│  │ Financials  │ │ Chart Patt- │ │ News Senti- │ │ RBI Policy  │ │ SEBI    ││
│  │ Valuation   │ │ erns, RSI,  │ │ ment, Social│ │ VIX, FII    │ │ Compli- ││
│  │ Quality     │ │ MACD, MA    │ │ buzz, Events│ │ GDP, Crude  │ │ ance    ││
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └────┬────┘│
│         │               │               │               │              │     │
└─────────┼───────────────┼───────────────┼───────────────┼──────────────┼─────┘
          │               │               │               │              │
          └───────────────┼───────────────┼───────────────┼──────────────┘
                          │               │               │
                          └───────────────┼───────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PREDICTOR AGENT                                    │
│                                                                              │
│  • Synthesizes all 5 agent analyses                                          │
│  • Weighs conflicting signals                                                │
│  • Generates final recommendation (Buy/Hold/Sell)                            │
│  • Provides target price, stop-loss, risk-reward                             │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FINAL ANALYSIS REPORT                                 │
│                                                                              │
│  {                                                                           │
│    "ticker": "RELIANCE",                                                     │
│    "recommendation": "buy",                                                  │
│    "composite_score": 72,                                                    │
│    "target_price": 2800,                                                     │
│    "confidence": "medium",                                                   │
│    "agent_analyses": { ... }                                                 │
│  }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tool Calling Architecture

### Understanding "Tools" in Agentic Systems

In agentic AI, **tools** are external functions that agents can invoke to gather information or take actions. Think of them as APIs the agent can call.

### NIFTY's Tool Design Philosophy

NIFTY implements **Orchestrator-Managed Tools** rather than **Agent-Invoked Tools**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TOOL ARCHITECTURE COMPARISON                             │
├─────────────────────────────────┬───────────────────────────────────────────┤
│    AGENT-INVOKED (LangChain)    │    ORCHESTRATOR-MANAGED (NIFTY)           │
├─────────────────────────────────┼───────────────────────────────────────────┤
│                                 │                                           │
│  Agent                          │  Orchestrator                             │
│    │                            │    │                                      │
│    ├──▶ "I need stock data"     │    ├──▶ Fetch ALL data upfront           │
│    │    ├──▶ Call yfinance      │    │    ├──▶ yfinance                    │
│    │    ◀── Result              │    │    ├──▶ macro data                  │
│    │                            │    │    ├──▶ news data                   │
│    ├──▶ "I need news"           │    │    └──▶ pipeline scores             │
│    │    ├──▶ Call news API      │    │                                      │
│    │    ◀── Result              │    ▼                                      │
│    │                            │  ┌─────────────────────────┐              │
│    ├──▶ "I need macro data"     │  │   CENTRALIZED CONTEXT   │              │
│    │    ├──▶ Call macro API     │  │   (base_data dict)      │              │
│    │    ◀── Result              │  └───────────┬─────────────┘              │
│    │                            │              │                            │
│    ▼                            │    ┌─────────┼─────────┐                  │
│  Final Response                 │    ▼         ▼         ▼                  │
│  (After multiple LLM calls)     │  Agent1   Agent2   Agent3                 │
│                                 │  (Single LLM call each)                   │
├─────────────────────────────────┼───────────────────────────────────────────┤
│  Pros: Dynamic, flexible        │  Pros: Fast, efficient, consistent        │
│  Cons: Slow, expensive          │  Cons: Fixed data scope                   │
└─────────────────────────────────┴───────────────────────────────────────────┘
```

### Tool Registry

Each data fetcher in `tools/` is a tool:

```python
# tools/nifty_fetcher.py
def get_stock_fundamentals(ticker: str) -> Dict[str, Any]:
    """
    TOOL: Fetch fundamental data for a stock
    
    INPUT: ticker (str) - e.g., "RELIANCE"
    OUTPUT: {
        "pe_ratio": 25.3,
        "pb_ratio": 2.1,
        "roe": 12.5,
        "debt_to_equity": 0.45,
        "market_cap": 1800000000000,
        "sector": "Energy",
        ...
    }
    
    SOURCE: Yahoo Finance (yfinance library)
    RATE_LIMIT: ~2000 requests/hour
    CACHE: LRU cache with 5-minute TTL
    """

def get_stock_quote(ticker: str) -> Dict[str, Any]:
    """
    TOOL: Fetch real-time quote
    
    INPUT: ticker (str)
    OUTPUT: {
        "last_price": 2650.50,
        "change_percent": 1.25,
        "volume": 5000000,
        "52w_high": 2900,
        "52w_low": 2200
    }
    """

def get_price_history(ticker: str, days: int = 250) -> Dict[str, Any]:
    """
    TOOL: Fetch historical OHLCV data
    
    INPUT: ticker (str), days (int)
    OUTPUT: {
        "data": [
            {"date": "2024-01-15", "open": 2640, "high": 2660, ...},
            ...
        ],
        "52w_high": 2900,
        "52w_low": 2200
    }
    """
```

```python
# tools/india_macro_fetcher.py
def get_macro_indicators() -> Dict[str, Any]:
    """
    TOOL: Fetch India macro indicators
    
    OUTPUT: {
        "india_vix": {"value": 15.2, "change": -0.5},
        "rbi_repo_rate": 6.5,
        "usd_inr": 83.25,
        "market_regime": "bullish",
        "nifty50": {"value": 22500, "change_pct": 0.8}
    }
    """
```

```python
# tools/india_news_fetcher.py
def get_stock_news(ticker: str, max_items: int = 20) -> Dict[str, Any]:
    """
    TOOL: Fetch news with sentiment analysis
    
    OUTPUT: {
        "headlines": [
            {"title": "Reliance Q3 results beat...", "sentiment": "positive"},
            ...
        ],
        "overall_sentiment": "positive",
        "sentiment_score": 0.65,
        "positive_count": 5,
        "negative_count": 2
    }
    
    SOURCES: Economic Times, Moneycontrol, Business Standard (RSS)
    """
```

### Tool Invocation Flow

```python
def _gather_base_data(self, ticker: str) -> Dict[str, Any]:
    """
    ORCHESTRATOR: Invoke all tools in parallel
    
    This is the "Tool Calling" phase, but managed by code,
    not by the LLM deciding which tools to call.
    """
    with ThreadPoolExecutor(max_workers=6) as executor:
        # Submit all tool calls simultaneously
        futures = {
            executor.submit(get_stock_fundamentals, ticker): "fundamentals",
            executor.submit(get_stock_quote, ticker): "quote", 
            executor.submit(get_price_history, ticker, 250): "price_history",
            executor.submit(get_macro_indicators): "macro",
            executor.submit(get_stock_news, ticker, 20): "sentiment",
            executor.submit(get_comprehensive_stock_data, ticker): "supabase_data"
        }
        
        # Collect results as they complete
        base_data = {"ticker": ticker, "timestamp": datetime.now().isoformat()}
        for future in as_completed(futures, timeout=30):
            key = futures[future]
            try:
                base_data[key] = future.result()
            except Exception as e:
                base_data[key] = {"error": str(e)}
        
        return base_data
```

---

## Memory & State Management

### Memory Types in Agentic Systems

| Memory Type | Description | NIFTY Implementation |
|-------------|-------------|----------------------|
| **Short-term** | Within single request | `base_data` dict |
| **Working Memory** | Intermediate reasoning | Agent prompts + responses |
| **Long-term** | Across requests | Supabase `ai_analysis_history` |
| **Episodic** | Past interactions | Cache + history API |

### Short-term Memory (Request Scope)

During a single analysis request, all agents share the same context:

```python
# This dict IS the short-term memory
base_data = {
    "ticker": "RELIANCE",
    "timestamp": "2024-01-15T10:30:00",
    "fundamentals": {...},
    "quote": {...},
    "price_history": {...},
    "macro": {...},
    "sentiment": {...},
    "supabase_data": {...}
}

# Every agent receives this (filtered) context
fundamental_agent(base_data)  # Sees fundamentals, quote, scores
technical_agent(base_data)    # Sees price_history, indicators
sentiment_agent(base_data)    # Sees sentiment, vix
# ... etc
```

### Working Memory (Agent Reasoning)

Each agent's prompt + response forms its working memory:

```python
user_prompt = f"""
Analyze the following stock data and provide your expert analysis.

TICKER: {agent_data.get('ticker')}
COMPANY: {agent_data.get('company_name')}
CURRENT PRICE: {agent_data.get('current_price')}

DATA PROVIDED:
{json.dumps(agent_data, indent=2, default=str)}

Please provide your analysis in the following JSON format:
{json.dumps(output_format, indent=2)}

IMPORTANT: Include a "reasoning" field explaining your analysis logic.
"""

# The LLM's response includes reasoning (working memory trace)
response = {
    "score": 72,
    "signal": "bullish",
    "reasoning": "P/E of 25 is below sector average of 28. ROE of 12% is healthy..."
}
```

### Long-term Memory (Supabase Persistence)

Analysis results are stored for historical tracking:

```python
def _store_analysis_to_supabase(self, ticker: str, report: Dict):
    """
    LONG-TERM MEMORY: Persist analysis to database
    
    Table: ai_analysis_history
    
    This enables:
    1. Hover tooltips showing past analyses
    2. Tracking recommendation changes over time
    3. Backtesting agent accuracy
    """
    data = {
        "ticker": ticker,
        "composite_score": report.get("composite_score"),
        "recommendation": report.get("recommendation"),
        "full_response": json.dumps(report),
        "cost_usd": report.get("observability", {}).get("total_cost_usd"),
        "created_at": datetime.now().isoformat()
    }
    self.supabase.table("ai_analysis_history").insert(data).execute()
```

### Caching Layer (Episodic Memory)

In-memory cache prevents redundant analysis:

```python
class NiftyAgentOrchestrator:
    def __init__(self):
        self.cache = {}  # In-memory cache
        self.enable_caching = True
    
    async def analyze_async(self, ticker: str):
        # Check episodic memory (cache)
        if self.enable_caching and ticker in self.cache:
            cache_entry = self.cache[ticker]
            cache_age = (datetime.now() - cache_entry["timestamp"]).seconds
            
            # 24-hour cache validity
            if cache_age < 86400:
                logger.info(f"Returning cached analysis (age: {cache_age}s)")
                cached_report = cache_entry["report"].copy()
                cached_report["cached"] = True
                cached_report["cache_age_seconds"] = cache_age
                return cached_report
        
        # ... perform fresh analysis ...
        
        # Store in episodic memory
        self.cache[ticker] = {
            "report": report,
            "timestamp": datetime.now()
        }
```

### Memory Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MEMORY ARCHITECTURE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  USER REQUEST                    ORCHESTRATOR                    DATABASE
       │                              │                               │
       │  "Analyze RELIANCE"          │                               │
       ├─────────────────────────────▶│                               │
       │                              │                               │
       │                    ┌─────────┴─────────┐                     │
       │                    │ CHECK CACHE       │                     │
       │                    │ (Episodic Memory) │                     │
       │                    └─────────┬─────────┘                     │
       │                              │                               │
       │                    ┌─────────▼─────────┐                     │
       │                    │ GATHER BASE_DATA  │                     │
       │                    │ (Short-term Mem)  │                     │
       │                    └─────────┬─────────┘                     │
       │                              │                               │
       │            ┌─────────────────┼─────────────────┐             │
       │            ▼                 ▼                 ▼             │
       │     ┌──────────┐      ┌──────────┐      ┌──────────┐        │
       │     │ Agent 1  │      │ Agent 2  │      │ Agent 3  │        │
       │     │ (Working │      │ (Working │      │ (Working │        │
       │     │  Memory) │      │  Memory) │      │  Memory) │        │
       │     └────┬─────┘      └────┬─────┘      └────┬─────┘        │
       │          │                 │                 │               │
       │          └─────────────────┼─────────────────┘               │
       │                            │                                 │
       │                  ┌─────────▼─────────┐                       │
       │                  │    PREDICTOR      │                       │
       │                  │  (Synthesis)      │                       │
       │                  └─────────┬─────────┘                       │
       │                            │                                 │
       │                  ┌─────────▼─────────┐                       │
       │                  │   UPDATE CACHE    │                       │
       │                  │ (Episodic Memory) │                       │
       │                  └─────────┬─────────┘                       │
       │                            │                                 │
       │                            │  PERSIST                        │
       │                            ├────────────────────────────────▶│
       │                            │                     ai_analysis │
       │  ◀─────────────────────────┤                        _history │
       │  FINAL REPORT              │                                 │
       │                            │                                 │
```

---

## Agent Flow Explained (For Beginners)

### Think of it like a Investment Committee Meeting

Imagine you're the CEO of an investment firm. Before making a decision about buying a stock, you call a meeting with 6 experts:

1. **The Accountant (Fundamental Agent)**
   - Reviews the company's financial statements
   - Calculates P/E ratio, debt levels, profit margins
   - Answers: "Is this company financially healthy?"

2. **The Chart Reader (Technical Agent)**
   - Looks at price charts and patterns
   - Checks if price is near support/resistance levels
   - Answers: "Is this a good time to buy based on price patterns?"

3. **The News Reporter (Sentiment Agent)**
   - Reads all recent news about the company
   - Gauges public opinion and social media buzz
   - Answers: "What's the market's mood about this stock?"

4. **The Economist (Macro Agent)**
   - Looks at interest rates, inflation, RBI policy
   - Checks India VIX (fear index) and FII flows
   - Answers: "Is the overall economy favorable for this stock?"

5. **The Compliance Officer (Regulatory Agent)**
   - Checks for any SEBI actions or legal issues
   - Reviews corporate governance
   - Answers: "Are there any regulatory red flags?"

6. **The Chief Investment Officer (Predictor Agent)**
   - Listens to all 5 experts
   - Weighs their opinions
   - Makes the final call: "Buy at ₹2650, target ₹2800, stop-loss ₹2500"

### Step-by-Step Flow

```
Step 1: User Request
────────────────────
User asks: "Analyze RELIANCE"

Step 2: Validation
────────────────────
Orchestrator checks if "RELIANCE" is a valid NSE stock ✓

Step 3: Data Collection
────────────────────
Orchestrator fetches data from:
  • yfinance: Price history, fundamentals
  • RSS feeds: Recent news articles
  • Supabase: Pre-computed scores from our pipeline

Step 4: Parallel Agent Execution
────────────────────
All 5 specialist agents receive the data and analyze simultaneously:

  Fundamental Agent thinks: "PE of 25 is reasonable, ROE is 12%..."
  Technical Agent thinks: "Price above 50-DMA, RSI at 55..."
  Sentiment Agent thinks: "3 positive news articles, 1 negative..."
  Macro Agent thinks: "VIX at 15 (low fear), RBI on hold..."
  Regulatory Agent thinks: "No recent SEBI actions..."

Step 5: Synthesis
────────────────────
Predictor Agent receives all analyses:

  "Fundamental: 70/100 - Good financials
   Technical: 65/100 - Neutral trend
   Sentiment: 72/100 - Positive news
   Macro: 68/100 - Supportive environment
   Regulatory: 85/100 - Clean record"

  Predictor concludes: "COMPOSITE: 72/100 - BUY with medium confidence"

Step 6: Final Report
────────────────────
User receives:
  • Recommendation: BUY
  • Target Price: ₹2800
  • Stop Loss: ₹2500
  • Confidence: Medium
  • All detailed analyses
```

### Why Parallel Execution Matters

Instead of waiting for each agent sequentially:
```
Sequential (Slow):
  Fundamental (3s) → Technical (3s) → Sentiment (3s) → Macro (3s) → Regulatory (3s)
  Total: 15 seconds
```

We run them in parallel:
```
Parallel (Fast):
  ┌─ Fundamental (3s) ─┐
  ├─ Technical (3s) ───┤
  ├─ Sentiment (3s) ───┼──► All complete in ~3s
  ├─ Macro (3s) ───────┤
  └─ Regulatory (3s) ──┘
  Total: ~3-5 seconds
```

---

## Agent Personas & System Prompts

The intelligence of the NIFTY Agent system lies in its **specialized system prompts**. Each agent is "primed" with a specific persona, expert knowledge base, and Indian market context.

### Design Philosophy
1. **Domain Isolation**: Each agent only analyzes data relevant to its expertise to prevent "hallucination dilution."
2. **Indian Market Context Injection**: Prompts include specific NSE/BSE and SEBI context (e.g., T+1 settlement, Promoter holding importance).
3. **Structured Reasoning**: Agents are forced to provide scores (0-100) and structured JSON responses for consistent dashboard rendering.

### 1. The Fundamental Analyst
*   **Persona**: A conservative Chartered Accountant/CFA focusing on long-term value.
*   **Expertise**: Ind AS accounting, ROE/ROCE, Debt-to-Equity, and Promoter Integrity.
*   **Prompt Logic**:
    ```python
    "Focus on promoter integrity and shareholding pattern. Express confidence levels. 
    Acknowledge missing data rather than fabricating."
    ```
*   **Key Output**: Financial Health Score, Valuation vs Peers, and Moat Quality.

### 2. The Technical Analyst
*   **Persona**: A disciplined momentum trader focusing on price action and charts.
*   **Expertise**: Candlestick patterns, 20/50/200 DMA, RSI/MACD, and Support/Resistance.
*   **Prompt Logic**:
    ```python
    "Identify the primary trend (bullish/bearish). Provide specific price levels for 
    entries, targets, and stop-losses. Consider Nifty direction."
    ```
*   **Key Output**: Trend Strength, Momentum Divergences, and Specific Trading Levels.

### 3. The Sentiment Analyst
*   **Persona**: A news junkie monitoring "street buzz" and institutional flows.
*   **Expertise**: News aggregation (RSS), Social Media Sentiment, and India VIX Interpretation.
*   **Prompt Logic**:
    ```python
    "Separate facts from rumors. Note recency (focus on 1-2 weeks). 
    Monitor FII/DII daily data shifts."
    ```
*   **Key Output**: Net Sentiment Score (-1 to +1), Market Buzz meter, and Narrative themes.

### 4. The Macro Economist
*   **Persona**: An analyst tracking high-frequency indicators and central bank policies.
*   **Expertise**: RBI Monetary Policy, CPI/WPI Inflation, INR/USD relations, and Crude Oil impacts.
*   **Prompt Logic**:
    ```python
    "Connect macro factors to specific sector impacts. India has unique dynamics 
    (Monsoon, Budget) - avoid generic global analysis."
    ```
*   **Key Output**: Market Regime (Bullish/Bearish/Cautious), India VIX fear gauge, and RBI Policy stance.

### 5. The Regulatory Expert
*   **Persona**: A legal consultant focusing on SEBI compliance and corporate law.
*   **Expertise**: Companies Act 2013, Insider Trading regs, and SEBI Enforcement.
*   **Prompt Logic**:
    ```python
    "Regulatory risk is binary. Check for past issues with promoters. 
    ESG mandates are now critical."
    ```
*   **Key Output**: Compliance Status (Clean/Red Flags), Pending Litigations, and ESG score.

### 6. The Investment Predictor (The Synthesizer)
*   **Persona**: A Senior Fund Manager making the "Final Call."
*   **Expertise**: Conflict resolution between specialists and final risk-reward math.
*   **Prompt Logic**:
    ```python
    "Integrate all 5 perspectives. Weigh conflicting signals. Identify consensus. 
    Weight factors based on current market regime."
    ```
*   **Key Output**: Recommendation (Buy/Hold/Sell/Reduce), Final Composite Score, Upside/Downside potential, and Key Thesis.

---

## Advanced Design Elements

Beyond system prompts, the NIFTY Agent system implements several "production-grade" design patterns to bridge the gap between AI prototypes and reliable financial tools.

### 1. Token Optimization (Efficiency)
To manage costs and latency, the system implements **Tiered Data Filtering** in the orchestrator (`_get_agent_specific_data`). 
- **The Problem**: Passing 250 days of price history and full fundamentals to 6 agents simultaneously consumes massive context windows (~15k tokens per run).
- **The Fix**: The orchestrator filters the `base_data` for each agent:
    - **Technical Agent**: Receives only the most recent **50 days** of price data (sufficient for candlestick/indicator analysis).
    - **Macro Agent**: Does not receive price history at all (focuses on economic indicators).
    - **Result**: Direct token usage reduction of **~54%** per analysis.

### 2. Parallel Orchestration (Speed)
The system uses a **Fan-out/Fan-in Architecture** to achieve high responsiveness (3-5s per full analysis):
- **Specialist Phase (Fan-out)**: All 5 analysis agents (Fundamental, Tech, etc.) are dispatched in parallel using `asyncio.gather`.
- **Synthesis Phase (Fan-in)**: The Predictor agent waits for all specialists to finish, then integrates the signals.
- **Fail-Safe**: If one specialist agent fails, the orchestrator proceeds with an "error badge" rather than crashing the entire analysis.

### 3. Centralized Tool Context (Memory)
Unlike simple "React" agents that loop through tool calls (Slow/Costly), NIFTY uses **Centralized Context Sharing**:
- The Orchestrator acts as the "System Memory." 
- It pre-fetches all shared data (Fundamentals, News, Macro) once and caches it for the duration of the request.
- This ensures all agents are looking at the *exact same data snapshot*, preventing "logic drift" where different specialists might see slightly different prices or news due to time gaps between tool calls.

### 4. FinOps & Telemetry (Observability)
The `observability.py` module implements a sophisticated tracing and cost-tracking layer:
- **Tracing**: Every request is assigned a `trace_id`. Each agent execution within that request is a `span_id`.
- **Token Accounting**: Actual token usage (from Gemini's `usage_metadata`) is logged for every call.
- **Cost Attribution**: Costs are calculated in **USD** in real-time based on the selected Gemini model pricing.
- **Data Redaction**: Sensitive data like API keys and PII are automatically stripped from logs using regex filters.
- **Summarization**: Large data structures are summarized in logs (keys + previews) to keep log files readable and efficient.

### 5. Predictor Weighted Synthesis
The final recommendation isn't a simple average. The **Predictor Agent** is designed to weigh signals based on the **Market Regime**:
- In "High VIX" (fearful) markets, it's instructed to weigh Macro and Sentiment signals more heavily.
- In "Low VIX" (stable) markets, Fundamental and Technical signals take priority.

---

## LLM Integration & Prompt Engineering

### Gemini Model Configuration

NIFTY uses Google's Gemini models for all LLM inference:

```python
# Model Selection Hierarchy
1. Environment variable: GEMINI_MODEL
2. Render.yaml default: gemini-2.0-flash
3. Code fallback: gemini-2.0-flash

# Why not hardcode in code?
# - Allows switching models without code changes
# - Different environments can use different models
# - Easy A/B testing of model performance
```

**Supported Models**:

| Model | Cost (Input) | Cost (Output) | Use Case |
|-------|--------------|---------------|----------|
| `gemini-2.0-flash` | $0.10/1M | $0.40/1M | Default, balanced |
| `gemini-1.5-flash` | $0.075/1M | $0.30/1M | Cost-sensitive |
| `gemini-1.5-pro` | $1.25/1M | $5.00/1M | Complex analysis |

### Prompt Structure

Each agent prompt follows a consistent structure:

```python
# System Prompt (in nifty_prompts.py)
system_prompt = """
You are a {PERSONA} specializing in {DOMAIN}.

CONTEXT:
- You analyze Indian equities (NSE/BSE listed)
- All prices are in INR
- Regulatory context: SEBI, Companies Act 2013

YOUR EXPERTISE:
- {SPECIFIC_SKILLS}
- {ANALYSIS_METHODS}

OUTPUT REQUIREMENTS:
- Always provide a score (0-100)
- Always explain reasoning
- Acknowledge data gaps explicitly

CONSTRAINTS:
- Never fabricate data
- Express confidence levels
- Stay within your domain
"""

# User Prompt (in orchestrator.py)
user_prompt = f"""
Analyze the following stock data:

TICKER: {ticker}
COMPANY: {company_name}
CURRENT PRICE: {current_price}

DATA:
{json.dumps(filtered_data)}

Respond in JSON format:
{json.dumps(output_schema)}
"""
```

### Output Schema Enforcement

All agents return structured JSON:

```python
# Example: Fundamental Agent Output Schema
{
    "financial_health_score": 72,        # 0-100
    "signal": "bullish",                 # bullish/neutral/bearish
    "valuation_assessment": "fairly_valued",
    "key_metrics": {
        "pe_ratio": 25.3,
        "roe": 12.5,
        "debt_to_equity": 0.45
    },
    "strengths": ["Strong cash flow", "Low debt"],
    "concerns": ["High PE vs peers"],
    "reasoning": "PE of 25 is below sector average..."
}
```

---

## Observability & FinOps

### Tracing Architecture

Every analysis request is fully traced:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OBSERVABILITY TRACE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  trace_id: "tr_abc123"                                                       │
│  ticker: "RELIANCE"                                                          │
│  timestamp: "2024-01-15T10:30:00Z"                                           │
│                                                                              │
│  ├─ span_id: "sp_001" [fundamental_agent]                                    │
│  │  ├─ start_time: 10:30:01.000                                              │
│  │  ├─ llm_request: {prompt_tokens: 1500, model: "gemini-2.0-flash"}         │
│  │  ├─ llm_response: {completion_tokens: 450, latency_ms: 2100}              │
│  │  ├─ end_time: 10:30:03.100                                                │
│  │  └─ cost_usd: 0.00033                                                     │
│  │                                                                           │
│  ├─ span_id: "sp_002" [technical_agent]                                      │
│  │  ├─ start_time: 10:30:01.000  (parallel)                                  │
│  │  ├─ llm_request: {prompt_tokens: 2200, model: "gemini-2.0-flash"}         │
│  │  ├─ llm_response: {completion_tokens: 520, latency_ms: 2400}              │
│  │  ├─ end_time: 10:30:03.400                                                │
│  │  └─ cost_usd: 0.00043                                                     │
│  │                                                                           │
│  ├─ span_id: "sp_003" [sentiment_agent] ...                                  │
│  ├─ span_id: "sp_004" [macro_agent] ...                                      │
│  ├─ span_id: "sp_005" [regulatory_agent] ...                                 │
│  │                                                                           │
│  └─ span_id: "sp_006" [predictor_agent]                                      │
│     ├─ start_time: 10:30:03.500  (after specialists)                         │
│     ├─ llm_request: {prompt_tokens: 3200}                                    │
│     └─ cost_usd: 0.00055                                                     │
│                                                                              │
│  TOTALS:                                                                     │
│  ├─ total_duration_ms: 4800                                                  │
│  ├─ total_input_tokens: 12,500                                               │
│  ├─ total_output_tokens: 2,800                                               │
│  └─ total_cost_usd: $0.0042                                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cost Tracking Implementation

```python
# observability.py
GEMINI_PRICING = {
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},  # per 1M tokens
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00}
}

def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Calculate cost in USD for an LLM call"""
    pricing = GEMINI_PRICING.get(model, GEMINI_PRICING["gemini-2.0-flash"])
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost
```

### Data Redaction for Security

Logs automatically redact sensitive information:

```python
REDACT_PATTERNS = [
    r'(api[_-]?key["\']?\s*[:=]\s*["\']?)[a-zA-Z0-9_-]+',
    r'(password["\']?\s*[:=]\s*["\']?)[^\s"\']+',
    r'(bearer\s+)[a-zA-Z0-9_.-]+',
]

def redact_sensitive_data(data: str) -> str:
    """Remove API keys, passwords from log output"""
    for pattern in REDACT_PATTERNS:
        data = re.sub(pattern, r'\1[REDACTED]', data, flags=re.IGNORECASE)
    return data
```

---

## Comparison: NIFTY vs Other Frameworks

### NIFTY vs LangGraph

| Feature | LangGraph | NIFTY |
|---------|-----------|-------|
| Graph-based routing | ✅ Full DAG support | ❌ Linear flow |
| Conditional branching | ✅ LLM decides next node | ❌ All agents always run |
| State persistence | ✅ Built-in checkpoints | ✅ Supabase + cache |
| Tool calling | ✅ Agent-invoked | ✅ Orchestrator-managed |
| Complexity | High | Low |
| Latency | Variable | Predictable |

**When to use LangGraph**: Complex, dynamic workflows where routing decisions need LLM reasoning.

**When to use NIFTY pattern**: Fixed analysis pipelines where speed and consistency matter.

### NIFTY vs CrewAI

| Feature | CrewAI | NIFTY |
|---------|--------|-------|
| Agent communication | Agents can message each other | Agents don't communicate |
| Task delegation | Agents delegate to each other | Orchestrator controls all |
| Role-playing | Strong persona enforcement | Moderate persona prompts |
| Process types | Sequential, Hierarchical | Parallel only |
| Built-in memory | ✅ Short/Long term | ✅ Manual implementation |

**When to use CrewAI**: When agents need to collaborate, debate, or delegate tasks dynamically.

**When to use NIFTY pattern**: When analysis is embarrassingly parallel (no inter-agent dependencies).

### NIFTY vs Google ADK (Agent Development Kit)

| Feature | Google ADK | NIFTY |
|---------|------------|-------|
| Agent types | LlmAgent, LoopAgent, SequentialAgent, ParallelAgent | Custom orchestrator |
| Built-in tools | Google Search, Code Execution | Custom data fetchers |
| Session management | InMemorySessionService | Manual cache |
| Model support | Gemini native | Gemini via SDK |
| Maturity | Preview (evolving) | Production |

**When to use Google ADK**: Greenfield projects wanting Google's opinionated framework.

**When to use NIFTY pattern**: When you need full control and custom data sources.

---

## Components

### Directory Structure

```
nifty_agents/
├── __init__.py              # Module exports
├── api.py                   # FastAPI REST endpoints
├── requirements_agents.txt  # Dependencies
│
├── agents/
│   ├── __init__.py
│   └── orchestrator.py      # Main orchestrator class
│
├── config/
│   ├── __init__.py
│   └── nifty_prompts.py     # Agent system prompts
│
├── tools/
│   ├── __init__.py
│   ├── nifty_fetcher.py     # Stock data (yfinance, nsetools)
│   ├── india_macro_fetcher.py   # RBI rates, VIX
│   ├── india_news_fetcher.py    # RSS news, sentiment
│   └── supabase_fetcher.py      # Existing pipeline data
│
└── tests/
    ├── __init__.py
    ├── test_nifty_fetcher.py
    ├── test_india_macro_fetcher.py
    ├── test_india_news_fetcher.py
    ├── test_supabase_fetcher.py
    └── test_e2e.py          # Integration tests
```

### Core Files Explained

| File | Purpose |
|------|---------|
| `orchestrator.py` | Coordinates all agents, manages parallel execution |
| `nifty_prompts.py` | System prompts defining each agent's expertise |
| `nifty_fetcher.py` | Fetches stock price and fundamentals |
| `india_macro_fetcher.py` | Fetches RBI rates, VIX, macro indicators |
| `india_news_fetcher.py` | Fetches news and performs sentiment analysis |
| `supabase_fetcher.py` | Retrieves pre-computed scores from database |
| `api.py` | REST API for frontend integration |

---

## Data Sources

### 1. yfinance (Primary)
- **What**: Yahoo Finance Python library
- **Data**: Price history, fundamentals, company info
- **Usage**: `get_stock_fundamentals()`, `get_price_history()`
- **Rate Limits**: Generally permissive for personal use

### 2. nsetools (Optional)
- **What**: NSE India scraper library
- **Data**: Live quotes, index data, India VIX
- **Usage**: `get_stock_quote()`, `get_index_quote()`
- **Note**: May have intermittent availability

### 3. RSS Feeds (News)
- **Sources**:
  - Economic Times Markets
  - Moneycontrol
  - Business Standard
- **Data**: Headlines, summaries for sentiment analysis
- **Usage**: `fetch_rss_news()`, `get_stock_news()`

### 4. Supabase (Existing Pipeline)
- **What**: Our pre-computed analysis database
- **Tables**:
  - `daily_stocks`: Scores, rankings
  - `weekly_analysis`: Weekly metrics
  - `monthly_analysis`: Monthly trends
  - `seasonality`: Historical patterns
- **Advantage**: Already computed scores, no API calls needed

---

## API Reference

### Base URL
```
http://localhost:8000/api/agent
```

### Endpoints

#### 1. Health Check
```http
GET /api/agent/health
```
Returns service status and configuration.

#### 2. Full Analysis
```http
GET /api/agent/analyze/{ticker}
```
Performs comprehensive multi-agent analysis.

**Parameters:**
- `ticker`: NSE stock symbol (e.g., RELIANCE, TCS)

**Response:**
```json
{
  "ticker": "RELIANCE",
  "company_name": "Reliance Industries Limited",
  "current_price": 2650.50,
  "recommendation": "buy",
  "composite_score": 72,
  "target_price": 2800,
  "confidence": "medium",
  "agent_analyses": {
    "fundamental": { ... },
    "technical": { ... },
    "sentiment": { ... },
    "macro": { ... },
    "regulatory": { ... }
  },
  "synthesis": { ... }
}
```

```

#### 3. Analysis History
```http
GET /api/agent/history/{ticker}
```
Checks for existing analysis in Supabase. Used for the dashboard **Hover Tooltip**.

**Benefits**:
- Instant UI feedback with `has_cached: true`.
- Reduces unnecessary LLM costs if a fresh analysis isn't needed.

#### 4. Quick Summary
```http
POST /api/agent/batch
Content-Type: application/json

{
  "tickers": ["RELIANCE", "TCS", "INFY"],
  "quick_mode": false
}
```

#### 5. Macro Indicators
```http
GET /api/agent/macro
```
Returns current market-wide indicators (VIX, RBI rates, market regime).

#### 6. Stock News
```http
GET /api/agent/news/{ticker}?max_items=10
```
Returns news with sentiment analysis for a stock.

---

## Setup & Installation

### Prerequisites
- Python 3.9+
- pip
- Google API key (for Gemini LLM)
- Supabase credentials (optional, for existing data)

### Step 1: Install Dependencies
```bash
cd Stock_Analysis_Python
pip install -r nifty_agents/requirements_agents.txt
```

### Step 2: Environment Variables
Create a `.env` file:
```env
GOOGLE_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
```

### Step 3: Start the API
```bash
uvicorn nifty_agents.api:app --reload --port 8000
```

### Step 4: Test
```bash
# Health check
curl http://localhost:8000/api/agent/health

# Analyze a stock
curl http://localhost:8000/api/agent/analyze/RELIANCE
```

---

## Usage Examples

### Python Direct Usage
```python
from nifty_agents import analyze_stock

# Full analysis
report = analyze_stock("RELIANCE")
print(f"Recommendation: {report['recommendation']}")
print(f"Target: {report['target_price']}")

# Quick check
from nifty_agents import get_stock_scores
scores = get_stock_scores("TCS")
print(f"Composite Score: {scores['composite_score']}")
```

### Async Usage
```python
import asyncio
from nifty_agents import analyze_stock_async

async def main():
    report = await analyze_stock_async("INFY")
    print(report)

asyncio.run(main())
```

### Batch Analysis
```python
from nifty_agents import NiftyAgentOrchestrator

orch = NiftyAgentOrchestrator()
reports = orch.batch_analyze(["RELIANCE", "TCS", "INFY"], max_parallel=3)
for r in reports:
    print(f"{r['ticker']}: {r['recommendation']}")
```

### Frontend Integration (Next.js)
```typescript
// In your Next.js API route or component
const analyzeStock = async (ticker: string) => {
  const response = await fetch(`/api/agent/analyze/${ticker}`);
  const data = await response.json();
  return data;
};

// Usage
const report = await analyzeStock('RELIANCE');
console.log(report.recommendation);
```

---

## Testing

### Run All Tests
```bash
pytest nifty_agents/tests/ -v
```

### Run Specific Tests
```bash
# Unit tests
pytest nifty_agents/tests/test_nifty_fetcher.py -v

# Integration tests
pytest nifty_agents/tests/test_e2e.py -v

# With coverage
pytest nifty_agents/tests/ --cov=nifty_agents --cov-report=html
```

### Test Without API Keys
Most tests use mocking, so they work without real API keys:
```bash
pytest nifty_agents/tests/ -v -m "not live"
```

---

## Troubleshooting

### Common Issues

#### 1. "nsetools not installed"
This is a warning, not an error. The system falls back to yfinance:
```bash
pip install nsetools
```

#### 2. "GOOGLE_API_KEY not set"
LLM features require a Google API key:
```bash
export GOOGLE_API_KEY=your_key_here
```
Without it, you can still use `get_quick_summary()` which uses pre-computed data.

#### 3. "Supabase not configured"
For full functionality with existing pipeline data:
```bash
export SUPABASE_URL=your_url
export SUPABASE_ANON_KEY=your_key
```

#### 4. Rate Limiting
If you hit API limits:
- Use `quick_mode=True` for batch operations
- Increase caching (`enable_caching=True`)
- Use pre-computed Supabase data

#### 5. Slow Response Times
- Check network connectivity
- Use `get_quick_summary()` for faster results
- Enable caching to avoid repeated API calls

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from nifty_agents import analyze_stock
report = analyze_stock("RELIANCE")  # Will show debug output
```

---

## Future Enhancements

### Planned Agentic Improvements

1. **Self-Reflection Loop**
   - Allow agents to critique and revise their own outputs
   - Implement "confidence threshold" that triggers re-analysis
   
2. **Devil's Advocate Agent**
   - Add a 6th specialist that argues against the consensus
   - Stress-tests bullish/bearish thesis

3. **Dynamic Tool Selection**
   - Let agents request additional data sources mid-analysis
   - Implement lazy loading for expensive data

4. **Memory Improvements**
   - Vector database for semantic search of past analyses
   - Learn from analyst feedback over time

5. **Planning Agent**
   - For custom queries: "What should I analyze for this IPO?"
   - Dynamically select which specialists to invoke

### Technical Roadmap

1. **Real-time Streaming**: WebSocket support for live analysis updates
2. **Custom Agents**: Allow users to define custom analysis agents
3. **Historical Backtesting**: Test recommendations against historical data
4. **Portfolio Analysis**: Analyze entire portfolios, not just individual stocks
5. **Alert System**: Notify when recommendation changes

---

## Glossary: Agentic AI Terms

| Term | Definition | NIFTY Example |
|------|------------|---------------|
| **Agent** | An AI system that can perceive, reason, and act autonomously | Each specialist (Fundamental, Technical, etc.) |
| **Tool** | External function an agent can call | `get_stock_fundamentals()`, `get_stock_news()` |
| **Orchestrator** | Component that coordinates multiple agents | `NiftyAgentOrchestrator` class |
| **System Prompt** | Instructions that define agent behavior | Prompts in `nifty_prompts.py` |
| **Context Window** | Max tokens an LLM can process | ~128k for Gemini 1.5/2.0 |
| **Token** | Unit of text (roughly 4 characters) | Used for cost/latency calculation |
| **Span** | A single operation within a trace | One agent's execution |
| **Trace** | Full request lifecycle | Complete analysis request |
| **Fan-out** | Dispatch multiple parallel tasks | 5 specialists running together |
| **Fan-in** | Collect results from parallel tasks | Predictor gathering all analyses |
| **ReAct** | Reasoning + Acting loop pattern | NOT used (by design) |
| **Reflection** | Agent reviewing/critiquing output | Predictor reviewing specialists |
| **Supervisor** | Agent/code that controls other agents | Orchestrator managing specialists |
| **Worker** | Agent controlled by supervisor | Specialist agents |
| **Short-term Memory** | Data within single request | `base_data` dict |
| **Long-term Memory** | Persistent storage across requests | Supabase `ai_analysis_history` |
| **Hallucination** | LLM generating false information | Mitigated by domain isolation |
| **Grounding** | Providing factual context to LLM | Pre-fetched data from APIs |

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Submit a pull request

---

## License

MIT License - See LICENSE file for details.

---

*Last Updated: January 2026*
*Version: 2.0.0*
*Documentation covers: Agentic Design Patterns, Tool Architecture, Memory Management, Observability*
