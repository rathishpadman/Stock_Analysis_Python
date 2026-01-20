# Stock Analysis Dashboard - Technical Documentation

## Executive Summary

A comprehensive equity analysis platform built with Next.js frontend and Python backend, featuring a **Multi-Agent AI System** for deep-dive stock analysis. The platform uses Supabase (PostgreSQL) as the database and provides daily, weekly, monthly analysis with seasonality patterns for Indian equities (NIFTY 50/200/500).

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Multi-Agent AI System](#multi-agent-ai-system)
5. [Data Pipeline Architecture](#data-pipeline-architecture)
6. [Database Schema](#database-schema)
7. [Frontend Dashboard](#frontend-dashboard)
8. [API Reference](#api-reference)
9. [Infrastructure & Deployment](#infrastructure--deployment)
10. [Observability & FinOps](#observability--finops)
11. [Ranking Methodology](#ranking-methodology)
12. [Authentication](#authentication)
13. [Environment Variables](#environment-variables)
14. [Known Issues & Data Quality](#known-issues--data-quality)
15. [Version History](#version-history)

---

## Project Overview

### System Capabilities

| Feature | Description |
|---------|-------------|
| **Multi-Agent Analysis** | 6 specialized AI agents for comprehensive stock analysis |
| **Daily Enrichment** | Automated daily data pipeline with 110+ fields |
| **Weekly/Monthly Aggregation** | Time-series aggregations for trend analysis |
| **Seasonality Patterns** | Historical monthly return patterns |
| **Real-time Dashboard** | Interactive charts with filtering and search |
| **Observability** | Full LLM tracing, cost tracking, and metrics |

### Key Features

- ✅ **6 Specialized AI Agents**: Fundamental, Technical, Sentiment, Macro, Regulatory, Predictor
- ✅ **Parallel Agent Execution**: Fast 3-5 second analysis via concurrent processing
- ✅ **Indian Market Focus**: Tailored for NSE/BSE listed stocks
- ✅ **Multiple Data Sources**: yfinance, RSS feeds, Supabase, nsetools
- ✅ **REST API + SSE Streaming**: Real-time progress updates
- ✅ **FinOps Dashboard**: Token usage, cost tracking, model comparison
- ✅ **GitHub Actions**: Automated daily/weekly/monthly pipelines

---

## Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14+ | React framework with App Router |
| React | 18+ | UI component library |
| TypeScript | 5+ | Type safety |
| Tailwind CSS | 3+ | Utility-first styling |
| Recharts | 2+ | Data visualization charts |
| Lucide React | - | Icon library |

### Backend - Data Pipeline
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Data processing pipeline |
| Pandas | 2+ | Data manipulation |
| NumPy | 1.2+ | Numerical computations |
| yFinance | - | Market data source |
| Supabase-py | - | Database client |

### Backend - AI Agents
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | - | REST API framework |
| Google Gemini | 2.0 Flash | LLM backend |
| python-dotenv | - | Environment management |
| feedparser | - | RSS news parsing |
| nsetools | - | NSE India data (optional) |

### Database
| Technology | Purpose |
|------------|---------|
| Supabase | Managed PostgreSQL with REST API |
| PostgreSQL | Relational database with RLS |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Vercel | Frontend hosting |
| GitHub Actions | CI/CD pipelines |
| Docker | Containerization (optional) |

---

## Project Structure

```
Stock_Analysis_Python/
├── dashboard/                     # Next.js Frontend Application
│   ├── src/
│   │   ├── app/                  # App Router pages and API routes
│   │   │   ├── page.tsx          # Main dashboard page (968 lines)
│   │   │   ├── layout.tsx        # Root layout
│   │   │   └── api/              # API route handlers
│   │   │       ├── stocks/       # Daily stocks API
│   │   │       ├── weekly/       # Weekly analysis API
│   │   │       ├── monthly/      # Monthly analysis API
│   │   │       └── seasonality/  # Seasonality data API
│   │   ├── components/           # React components (14 files)
│   │   │   ├── Charts.tsx        # Daily price/RSI/MACD charts
│   │   │   ├── WeeklyCharts.tsx  # Weekly OHLC with SMA
│   │   │   ├── MonthlyCharts.tsx # Monthly trends
│   │   │   ├── SeasonalityCharts.tsx # Heatmaps and patterns
│   │   │   ├── StockTable.tsx    # Daily data table
│   │   │   ├── WeeklyReportTableV2.tsx # Weekly with momentum rank
│   │   │   ├── MonthlyReportTableV2.tsx # Monthly with trends
│   │   │   ├── SeasonalityHeatmapV2.tsx # Color-coded heatmap
│   │   │   ├── ObservabilityDashboard.tsx # Agent monitoring UI
│   │   │   └── ...
│   │   ├── context/              # React context providers
│   │   │   └── AuthContext.tsx   # Supabase auth
│   │   └── lib/                  # Utilities and constants
│   │       └── supabase.ts       # Supabase client
│   └── public/                   # Static assets
│
├── nifty_agents/                  # 🆕 Multi-Agent AI System
│   ├── __init__.py               # Module exports
│   ├── api.py                    # FastAPI endpoints (1072 lines)
│   ├── observability.py          # FinOps & tracing (1245 lines)
│   ├── requirements_agents.txt   # Agent-specific deps
│   ├── AGENT_DOCUMENTATION.md    # Agent system docs
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   └── orchestrator.py       # Main orchestrator (736 lines)
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── nifty_prompts.py      # Agent system prompts (400 lines)
│   │
│   ├── tools/                    # Data fetchers
│   │   ├── nifty_fetcher.py      # Stock fundamentals (yfinance)
│   │   ├── india_macro_fetcher.py # RBI rates, VIX
│   │   ├── india_news_fetcher.py  # RSS news, sentiment
│   │   └── supabase_fetcher.py    # Pre-computed scores
│   │
│   ├── logs/                     # Runtime logs
│   │   ├── agent_logs.jsonl      # Agent execution logs
│   │   ├── finops.jsonl          # Cost tracking
│   │   └── llm_traces.jsonl      # Full LLM traces
│   │
│   └── tests/                    # Test suite
│       ├── test_nifty_fetcher.py
│       ├── test_india_macro_fetcher.py
│       ├── test_india_news_fetcher.py
│       ├── test_supabase_fetcher.py
│       └── test_e2e.py
│
├── equity_engine/                 # Python Analysis Engine
│   ├── pipeline.py               # Main pipeline (780 lines)
│   ├── scoring.py                # Composite scoring
│   ├── technical.py              # Technical indicators
│   ├── indicators.py             # Additional indicators
│   ├── data_sources.py           # Data fetching
│   ├── normalizers.py            # Data normalization
│   ├── aggregators.py            # Weekly/monthly aggregation
│   ├── weekly_analysis.py        # Weekly metrics
│   ├── monthly_analysis.py       # Monthly metrics
│   ├── config.py                 # Configuration
│   └── logger.py                 # Logging
│
├── pipeline/                      # Data Pipeline Scripts
│   ├── daily_to_supabase.py      # Daily enrichment + upload
│   ├── weekly_to_supabase.py     # Weekly aggregation
│   ├── monthly_to_supabase.py    # Monthly aggregation
│   ├── backfill_history.py       # Historical data backfill
│   ├── fill_gaps.py              # Gap filling
│   └── tests/                    # Pipeline tests
│
├── .github/workflows/             # CI/CD Automation
│   ├── daily-pipeline.yml        # Daily at 4:00 PM IST (Mon-Fri)
│   ├── weekly-pipeline.yml       # Weekly aggregation
│   └── monthly-pipeline.yml      # Monthly aggregation
│
├── supabase/                      # Database Migrations
│   └── migrations/
│       └── 001_initial_schema.sql
│
├── tools/                         # Utility scripts
├── data/                          # Local data files
└── *.md                           # Documentation files
```

---

## Multi-Agent AI System

### Architecture Overview

The NIFTY Agent System is a **multi-agent AI solution** for comprehensive analysis of Indian equities. It uses 6 specialized AI agents, each expert in a different aspect of stock analysis.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER REQUEST                                       │
│                     (e.g., "Analyze RELIANCE")                              │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR                                       │
│                                                                              │
│  1. Validate ticker against NSE                                              │
│  2. Gather base data from all sources                                        │
│  3. Dispatch to specialist agents (in parallel)                              │
│  4. Collect responses                                                        │
│  5. Send to Predictor for synthesis                                          │
│  6. Return final report                                                      │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
                ▼                    ▼                    ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   DATA FETCHERS     │  │   DATA FETCHERS     │  │   DATA FETCHERS     │
│                     │  │                     │  │                     │
│ nifty_fetcher       │  │ india_macro         │  │ india_news          │
│ (yfinance, NSE)     │  │ (RBI, VIX)          │  │ (RSS, Sentiment)    │
└──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SPECIALIST AGENTS (Parallel Execution)                   │
│                                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐│
│  │ FUNDAMENTAL │ │  TECHNICAL  │ │  SENTIMENT  │ │    MACRO    │ │REGULATORY│
│  │   AGENT     │ │   AGENT     │ │   AGENT     │ │   AGENT     │ │  AGENT  ││
│  │             │ │             │ │             │ │             │ │         ││
│  │ Financials  │ │ Chart Pat-  │ │ News Senti- │ │ RBI Policy  │ │ SEBI    ││
│  │ Valuation   │ │ terns, RSI, │ │ ment, Social│ │ VIX, FII    │ │ Compli- ││
│  │ Quality     │ │ MACD, MA    │ │ buzz, Events│ │ GDP, Crude  │ │ ance    ││
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └────┬────┘│
└─────────┼───────────────┼───────────────┼───────────────┼──────────────┼─────┘
          │               │               │               │              │
          └───────────────┴───────────────┴───────────────┴──────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PREDICTOR AGENT                                    │
│                                                                              │
│  • Synthesizes all 5 agent analyses                                          │
│  • Weighs conflicting signals                                                │
│  • Generates final recommendation (Buy/Hold/Sell)                            │
│  • Provides target price, stop-loss, risk-reward                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FINAL ANALYSIS REPORT                                 │
│  { "ticker": "RELIANCE", "recommendation": "buy", "composite_score": 72,    │
│    "target_price": 2800, "confidence": "medium", "agent_analyses": {...} }  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Agent Descriptions

| Agent | Role | Key Focus Areas |
|-------|------|-----------------|
| **Fundamental Agent** | The Accountant | P/E, P/B, ROE, ROCE, debt levels, profit margins |
| **Technical Agent** | The Chart Reader | RSI, MACD, support/resistance, trend analysis |
| **Sentiment Agent** | The News Reporter | News sentiment, social buzz, upcoming events |
| **Macro Agent** | The Economist | RBI policy, India VIX, FII flows, INR impact |
| **Regulatory Agent** | The Compliance Officer | SEBI actions, litigation, corporate governance |
| **Predictor Agent** | The CIO | Synthesizes all analyses, final recommendation |

### Parallel Execution Performance

```
Sequential (Slow):
  Fundamental (3s) → Technical (3s) → Sentiment (3s) → Macro (3s) → Regulatory (3s)
  Total: 15 seconds

Parallel (Fast):
  ┌─ Fundamental (3s) ─┐
  ├─ Technical (3s) ───┤
  ├─ Sentiment (3s) ───┼──► All complete in ~3s
  ├─ Macro (3s) ───────┤
  └─ Regulatory (3s) ──┘
  Total: ~3-5 seconds
```

### Agent Configuration

Each agent is configured in `nifty_agents/config/nifty_prompts.py`:

| Agent | Model | Temperature | Max Tokens |
|-------|-------|-------------|------------|
| Fundamental | gemini-2.0-flash | 0.3 | 2000 |
| Technical | gemini-2.0-flash | 0.2 | 2000 |
| Sentiment | gemini-2.0-flash | 0.4 | 1500 |
| Macro | gemini-2.0-flash | 0.3 | 1500 |
| Regulatory | gemini-2.0-flash | 0.2 | 1500 |
| Predictor | gemini-2.0-flash | 0.4 | 2500 |

### Data Fetchers (Tools)

| Module | Data Source | Key Functions |
|--------|-------------|---------------|
| `nifty_fetcher.py` | yfinance, nsetools | `get_stock_fundamentals()`, `get_price_history()` |
| `india_macro_fetcher.py` | RBI, NSE | `get_rbi_rates()`, `get_india_vix()` |
| `india_news_fetcher.py` | ET, Moneycontrol RSS | `get_stock_news()`, `analyze_sentiment_aggregate()` |
| `supabase_fetcher.py` | Supabase | `get_stock_scores()`, `get_comprehensive_stock_data()` |

---

## A2A Communication Patterns

### Agent-to-Agent Communication Overview

The system uses a **Hub-and-Spoke Pattern** with the Orchestrator as the central hub:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          AGENT COMMUNICATION FLOW                                │
└─────────────────────────────────────────────────────────────────────────────────┘

  PHASE 1: Data Gathering                     PHASE 2: Parallel Analysis
  ───────────────────────                    ──────────────────────────
  
  ┌──────────────┐                           ┌───────────────────────┐
  │    Data      │                           │   SPECIALIST AGENTS   │
  │   Sources    │                           │   (Run in Parallel)   │
  ├──────────────┤                           ├───────────────────────┤
  │ • yFinance   │──┐                     ┌──│ Fundamental Agent     │
  │ • RSS Feeds  │  │                     │  │ Technical Agent       │
  │ • RBI Data   │  │  ┌──────────────┐   │  │ Sentiment Agent       │
  │ • Supabase   │──┼─▶│ ORCHESTRATOR │───┼──│ Macro Agent           │
  │ • NSE VIX    │  │  │   (Hub)      │   │  │ Regulatory Agent      │
  └──────────────┘  │  └──────┬───────┘   │  └───────────────────────┘
                    │         │           │
                    └─────────┤           │
                              │           │
                              ▼           │
  PHASE 3: Synthesis                      │
  ──────────────────                      │
                              ┌───────────┴────────────┐
                              │   PREDICTOR AGENT      │
                              │   (Receives all 5      │
                              │    agent analyses)     │
                              └───────────┬────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │   FINAL REPORT         │
                              │   (Recommendation +    │
                              │    Composite Score)    │
                              └────────────────────────┘
```

### Communication Protocol

| Phase | From | To | Data Exchanged |
|-------|------|----|----------------|
| 1 | Orchestrator | Data Fetchers | Ticker symbol |
| 2 | Data Fetchers | Orchestrator | Raw data (fundamentals, price history, news, macro, supabase) |
| 3 | Orchestrator | Specialist Agents | `base_data` dictionary + system prompt + output format |
| 4 | Specialist Agents | Orchestrator | JSON analysis with scores, reasoning, risks |
| 5 | Orchestrator | Predictor Agent | All 5 agent analyses combined |
| 6 | Predictor Agent | Orchestrator | Final recommendation, composite score, target price |

### Key Implementation Details

**Parallel Execution** (Lines 577-589 in `orchestrator.py`):
```python
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {
        executor.submit(self._call_agent, name, base_data, trace_id): name
        for name in agent_names
    }
```

**Predictor Synthesis** (Lines 403-415 in `orchestrator.py`):
```python
user_prompt = f"""
You have received analyses from 5 specialized agents for {ticker}.
Synthesize these into a final investment recommendation.

AGENT ANALYSES:
{json.dumps(agent_analyses, indent=2, default=str)}
"""
```

### No Direct Agent-to-Agent Communication

> [!IMPORTANT]
> Agents do **NOT** communicate directly with each other. All communication is mediated by the Orchestrator. This is by design for:
> - **Isolation**: Each agent is unaware of other agents
> - **Simplicity**: Clear data flow, easier debugging
> - **Flexibility**: Agents can be added/removed without affecting others

---

## Critical Issues Identified

> [!CAUTION]
> The following issues were identified from log analysis of `llm_traces.jsonl` and `agent_logs.jsonl`.

### 1. Bloated LLM Prompts (HIGH PRIORITY)

**Root Cause**: Line 225 in `orchestrator.py`:
```python
DATA PROVIDED:
{json.dumps(base_data, indent=2, default=str)}
```

This passes the **entire** `base_data` dictionary to **every** specialist agent, regardless of what data each agent actually needs.

**Evidence from Logs**:
| Agent | `user_prompt_length` | `input_tokens` | Issue |
|-------|---------------------|----------------|-------|
| `fundamental_agent` | ~56,586 chars | ~2,000 | Receives full 250-day price history (unnecessary) |
| `technical_agent` | ~56,586 chars | ~2,500 | Receives news sentiment data (unnecessary) |
| `sentiment_agent` | ~56,586 chars | ~1,800 | Receives macro/regulatory data (unnecessary) |

**Impact**:
- ❌ **Higher token usage**: ~12,200 input tokens per analysis vs. estimated ~6,000 if optimized
- ❌ **Increased cost**: Approximately 2x overspend on input tokens
- ❌ **Slower responses**: Larger prompts = longer LLM processing time
- ❌ **Context window risk**: Large prompts may hit limits with complex analyses

### 2. Environment Variable Warnings

**From Logs**:
```json
{"level": "WARNING", "message": "Google GenAI not available. Set GOOGLE_API_KEY."}
{"level": "WARNING", "message": "Supabase not configured - some features limited"}
```

**Impact**: 
- When `GOOGLE_API_KEY` is missing, the system returns mock analyses
- When Supabase is not configured, pre-computed scores are unavailable

### 3. Redundant Data in Predictor Prompt

The Predictor agent receives the **full JSON output** from all 5 agents, including:
- Internal metadata (`_agent`, `_timestamp`)
- Raw response fragments
- Verbose reasoning text

This inflates the predictor's input prompt unnecessarily.

---

## Optimization Recommendations

### 1. Agent-Specific Data Filtering ✅ IMPLEMENTED

The `_get_agent_specific_data()` method in `orchestrator.py` filters data for each agent:

```python
# BEFORE (full base_data to every agent):
DATA PROVIDED:
{json.dumps(base_data, indent=2, default=str)}  # ~55KB to each agent!

# AFTER (agent-specific filtering):
agent_data = self._get_agent_specific_data(agent_name, base_data)
DATA PROVIDED:
{json.dumps(agent_data, indent=2, default=str)}  # Only what agent needs
```

**Agent Data Allocation (as implemented)**:
| Agent | Data Included | Data Excluded |
|-------|---------------|---------------|
| Fundamental | fundamentals, quote, scores, sector | price_history, sentiment, macro |
| Technical | 50-day price_history, indicators, market_regime | fundamentals, sentiment (full), supabase weekly/monthly |
| Sentiment | sentiment, india_vix, market_regime, sector | price_history, fundamentals ratios |
| Macro | macro, sector, industry, pe_ratio, market_cap | price_history, full sentiment, full fundamentals |
| Regulatory | sector, industry, announcements, quality_score | price_history, sentiment scores, macro |

**Actual Token Savings (corrected estimates)**:
| Agent | Before | After | Savings |
|-------|--------|-------|---------|
| Fundamental | ~2,000 | ~1,000 | 50% |
| Technical | ~2,500 | ~2,000 | 20% (needs 50-day history) |
| Sentiment | ~1,800 | ~600 | 67% |
| Macro | ~1,500 | ~400 | 73% |
| Regulatory | ~1,200 | ~400 | 67% |
| **Total** | **~12,200** | **~5,600** | **~54%** |

### 2. Price History Summarization

Instead of passing 250 days of OHLCV data, pass summarized metrics:

```python
# BEFORE: 250 rows of daily OHLCV data (~15,000 chars)

# AFTER (implemented): Only 50 days sent to Technical agent
price_data_list = price_history.get("data", [])
recent_50_days = price_data_list[:50]  # 80% reduction!
```

> [!NOTE]
> Technical Agent still receives 50 days of price history (not just a summary) because chart pattern recognition requires actual OHLCV data. The 50-day cutoff balances pattern recognition needs with token efficiency.

### 3. Predictor Prompt Cleanup ✅ IMPLEMENTED

The `_clean_for_predictor()` method strips unnecessary fields before sending to predictor:

```python
def _clean_for_predictor(self, agent_analyses: Dict) -> Dict:
    """Remove internal metadata before synthesis."""
    exclude_fields = {"_agent", "_timestamp", "_raw_response", "error", "raw_response"}
    
    for agent_name, analysis in agent_analyses.items():
        # Remove metadata fields
        cleaned[agent_key] = {k: v for k, v in analysis.items() if k not in exclude_fields}
        
        # Truncate verbose reasoning to 200 chars
        if reasoning and len(reasoning) > 200:
            cleaned[agent_key]["reasoning_summary"] = reasoning[:200] + "..."
```

### 4. Render.com Deployment Checklist

For successful deployment to Render.com (based on `render.yaml`):

| Requirement | Status | Notes |
|-------------|--------|-------|
| `GOOGLE_API_KEY` | ❓ Manual | **Must set in Render dashboard** |
| `SUPABASE_URL` | ❓ Manual | Must set in Render dashboard |
| `SUPABASE_KEY` | ❓ Manual | Must set in Render dashboard |
| `GEMINI_MODEL` | ✅ Set | `gemini-2.0-flash-exp` |
| Health Check | ✅ Configured | `/health` endpoint |
| Region | ✅ Configured | Singapore (`singapore`) |
| Plan | ⚠️ Free | 30s cold start after 15min idle |

> [!TIP]
> To avoid cold starts on the free plan, consider implementing a keep-alive cron job that pings the `/health` endpoint every 10 minutes.

---

## Data Pipeline Architecture

### Pipeline Flow

```
                         ┌─────────────────┐
                         │   yFinance API  │
                         └────────┬────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    equity_engine/pipeline.py                         │
│                                                                      │
│  build_universe() → enrich_stock() → compute_subscores() → overall_score()
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
           │    Daily     │ │    Weekly    │ │   Monthly    │
           │   Pipeline   │ │   Pipeline   │ │   Pipeline   │
           └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
                  │                │                │
                  ▼                ▼                ▼
           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
           │ daily_stocks │ │weekly_analysis│ │monthly_analysis│
           │   (110+     │ │              │ │  + seasonality │
           │   fields)   │ │              │ │              │
           └──────────────┘ └──────────────┘ └──────────────┘
                         │        │        │
                         └────────┼────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │    Supabase (PostgreSQL) │
                    └─────────────────────────┘
```

### GitHub Actions Automation

| Workflow | Schedule | Description |
|----------|----------|-------------|
| `daily-pipeline.yml` | 4:00 PM IST (Mon-Fri) | Full stock enrichment for NIFTY 50/200/500 |
| `weekly-pipeline.yml` | Configurable | Weekly OHLC aggregation |
| `monthly-pipeline.yml` | Configurable | Monthly aggregation + seasonality |

```yaml
# daily-pipeline.yml
name: Daily Stock Enrichment
on:
  schedule:
    - cron: '30 10 * * 1-5' # 4:00 PM IST
  workflow_dispatch:
jobs:
  enrich:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Run Daily Pipeline
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        run: python pipeline/daily_to_supabase.py
```

---

## Database Schema

### 1. daily_stocks

Primary table containing daily stock analysis data with **110+ fields**.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Auto-increment ID |
| ticker | VARCHAR(20) | Stock symbol (e.g., RELIANCE.NS) |
| company_name | VARCHAR(255) | Full company name |
| date | DATE | Trading date |
| price_last | DECIMAL | Last traded price |
| return_1d | DECIMAL | 1-day return % |
| return_1w | DECIMAL | 1-week return % |
| return_1m | DECIMAL | 1-month return % |
| return_3m | DECIMAL | 3-month return % |
| return_6m | DECIMAL | 6-month return % |
| return_1y | DECIMAL | 1-year return % |
| overall_score | DECIMAL | Composite score (0-100) |
| score_fundamental | DECIMAL | Fundamental score (0-100) |
| score_technical | DECIMAL | Technical score (0-100) |
| score_sentiment | DECIMAL | Sentiment score (0-100) |
| score_risk | DECIMAL | Risk score (0-100) |
| rsi14 | DECIMAL | RSI 14-period |
| sma20 | DECIMAL | 20-day SMA |
| sma50 | DECIMAL | 50-day SMA |
| sma200 | DECIMAL | 200-day SMA |
| macd_line | DECIMAL | MACD line value |
| macd_signal | DECIMAL | MACD signal line |
| pe_ttm | DECIMAL | Price/Earnings TTM |
| pb | DECIMAL | Price/Book ratio |
| market_cap_cr | DECIMAL | Market cap (INR Cr) |
| ... | ... | 80+ additional fields |

### 2. weekly_analysis

Aggregated weekly data for each ticker.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Auto-increment ID |
| ticker | VARCHAR(20) | Stock symbol |
| company_name | VARCHAR(255) | Company name |
| week_ending | DATE | Week ending date |
| weekly_open | DECIMAL | Weekly opening price |
| weekly_high | DECIMAL | Weekly high price |
| weekly_low | DECIMAL | Weekly low price |
| weekly_close | DECIMAL | Weekly closing price |
| weekly_return_pct | DECIMAL | Weekly return % |
| weekly_volume | BIGINT | Total weekly volume |
| weekly_volume_ratio | DECIMAL | Volume vs avg ratio |
| weekly_rsi14 | DECIMAL | Weekly RSI |
| weekly_sma10 | DECIMAL | 10-week SMA |
| weekly_sma20 | DECIMAL | 20-week SMA |
| return_4w | DECIMAL | 4-week return % |
| return_13w | DECIMAL | 13-week return % |
| weekly_trend | VARCHAR(10) | UP/DOWN/SIDEWAYS |

### 3. monthly_analysis

Aggregated monthly data for each ticker.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Auto-increment ID |
| ticker | VARCHAR(20) | Stock symbol |
| company_name | VARCHAR(255) | Company name |
| month | VARCHAR(7) | Month (YYYY-MM format) |
| monthly_open | DECIMAL | Monthly opening price |
| monthly_high | DECIMAL | Monthly high price |
| monthly_low | DECIMAL | Monthly low price |
| monthly_close | DECIMAL | Monthly closing price |
| monthly_return_pct | DECIMAL | Monthly return % |
| monthly_volume | BIGINT | Total monthly volume |
| return_3m | DECIMAL | 3-month return % |
| return_6m | DECIMAL | 6-month return % |
| return_12m | DECIMAL | 12-month return % |
| ytd_return_pct | DECIMAL | Year-to-date return % |
| monthly_sma3 | DECIMAL | 3-month SMA |
| monthly_sma6 | DECIMAL | 6-month SMA |
| monthly_sma12 | DECIMAL | 12-month SMA |
| monthly_trend | VARCHAR(10) | UP/DOWN/SIDEWAYS |

### 4. seasonality

Historical monthly return patterns by ticker.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Auto-increment ID |
| ticker | VARCHAR(20) | Stock symbol |
| company_name | VARCHAR(255) | Company name |
| jan_avg - dec_avg | DECIMAL | Monthly average returns |
| best_month | VARCHAR(20) | Best performing month |
| worst_month | VARCHAR(20) | Worst performing month |

---

## Frontend Dashboard

### Page Structure

The main dashboard (`dashboard/src/app/page.tsx`) provides:
- **Tab navigation**: Daily, Weekly, Monthly, Seasonality
- **Table view**: Sortable, filterable, searchable
- **Detail view**: Charts when a stock is selected
- **Column picker**: Tab-specific column customization

### Table Components

| Component | Purpose |
|-----------|---------|
| `StockTable.tsx` | Daily stocks with score-based coloring |
| `WeeklyReportTableV2.tsx` | Weekly with momentum ranking, trend/RSI filtering |
| `MonthlyReportTableV2.tsx` | Monthly with return-based filtering |
| `SeasonalityHeatmapV2.tsx` | Color-coded monthly returns heatmap |

### Chart Components

| Component | Charts Included |
|-----------|-----------------|
| `Charts.tsx` | PriceChart (Candlestick), RSIChart, MACDChart, ScoreBarChart |
| `WeeklyCharts.tsx` | WeeklyPriceChart, WeeklyRSIChart, WeeklyReturnsChart, WeeklyVolumeChart |
| `MonthlyCharts.tsx` | MonthlyPriceChart, MonthlyReturnsChart, RollingReturnsChart |
| `SeasonalityCharts.tsx` | SeasonalityBarChart, SeasonalityRadarChart, QuarterlyBreakdown |

### Observability Dashboard

`ObservabilityDashboard.tsx` provides:
- Real-time agent execution logs
- FinOps cost tracking
- LLM trace viewer
- Model cost comparison
- Metrics aggregation

---

## API Reference

### Dashboard API Routes (Next.js)

| Route | Method | Description |
|-------|--------|-------------|
| `/api/stocks` | GET | Fetch daily stocks data |
| `/api/stocks/[ticker]` | GET | Fetch specific stock data |
| `/api/weekly` | GET | Fetch weekly analysis data |
| `/api/weekly/[ticker]` | GET | Fetch ticker weekly history |
| `/api/monthly` | GET | Fetch monthly analysis data |
| `/api/monthly/[ticker]` | GET | Fetch ticker monthly history |
| `/api/seasonality` | GET | Fetch seasonality data |
| `/api/seasonality/[ticker]` | GET | Fetch ticker seasonality |

### Agent API Endpoints (FastAPI)

Base URL: `http://localhost:8000/api/agent`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/analyze/{ticker}` | GET | Full multi-agent analysis |
| `/analyze/{ticker}/stream` | GET | SSE streaming analysis with real-time updates |
| `/quick/{ticker}` | GET | Quick summary (no LLM calls) |
| `/batch` | POST | Batch analysis for multiple tickers |
| `/scores/{ticker}` | GET | Pre-computed scores from Supabase |
| `/macro` | GET | Current macro indicators |
| `/news/{ticker}` | GET | News with sentiment analysis |
| `/top` | GET | Top-ranked stocks by index |

### Observability Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/observability/logs` | GET | Recent agent execution logs |
| `/observability/finops` | GET | Cost tracking data |
| `/observability/metrics` | GET | Aggregated analysis metrics |
| `/observability/cost-report` | GET | Cost report for period |
| `/observability/llm-traces` | GET | Full LLM request/response traces |
| `/observability/trace/{trace_id}` | GET | All details for specific trace |
| `/observability/models` | GET | Available models with pricing |
| `/observability/estimate-cost` | GET | Cost estimate per analysis |

### Example Response: Full Analysis

```json
{
  "ticker": "RELIANCE",
  "company_name": "Reliance Industries Limited",
  "current_price": 2650.50,
  "recommendation": "buy",
  "composite_score": 72,
  "target_price": 2800,
  "stop_loss": 2500,
  "confidence": "medium",
  "upside_potential": "5.6%",
  "risk_reward_ratio": "1.8:1",
  "analysis_timestamp": "2026-01-19T12:00:00Z",
  "analysis_duration_seconds": 4.2,
  "agent_analyses": {
    "fundamental": { "score": 70, "valuation": "fair", ... },
    "technical": { "score": 65, "trend": "bullish", ... },
    "sentiment": { "score": 72, "news_flow": "positive", ... },
    "macro": { "score": 68, "market_regime": "neutral", ... },
    "regulatory": { "score": 85, "compliance": "clean", ... }
  },
  "synthesis": {
    "key_thesis": "Strong fundamentals with positive momentum",
    "bull_case": "Retail and telecom growth",
    "bear_case": "Oil price volatility",
    "key_monitorables": ["Q4 results", "Jio subscriber growth"]
  }
}
```

---

## Infrastructure & Deployment

### Deployment Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Browser  │────▶│     Vercel      │────▶│    Supabase     │
│                 │     │  (Next.js App)  │     │  (PostgreSQL)   │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │                       ▲
                                 │                       │
                                 ▼                       │
                        ┌─────────────────┐              │
                        │  FastAPI Agent  │──────────────┘
                        │     Server      │
                        │  (localhost or  │
                        │   Cloud Run)    │
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Google AI     │
                        │   (Gemini 2.0)  │
                        └─────────────────┘
```

### Environment Setup

1. **Frontend (Vercel)**
   - Automatic deployments from GitHub
   - Environment variables set in Vercel dashboard

2. **Pipeline (GitHub Actions)**
   - Runs on schedule or manual trigger
   - Uses repository secrets

3. **Agent API (Local / Cloud Run)**
   - Start with: `uvicorn nifty_agents.api:app --reload --port 8000`
   - Configure via `.env.local`

---

## Observability & FinOps

### Logging Structure

All logs are written to `nifty_agents/logs/` in JSONL format:

| File | Purpose |
|------|---------|
| `agent_logs.jsonl` | Agent execution events |
| `finops.jsonl` | Cost tracking per call |
| `llm_traces.jsonl` | Full LLM request/response |
| `metrics.json` | Aggregated metrics |

### Cost Tracking

Gemini model pricing (tracked automatically):

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| gemini-2.0-flash-exp | $0.01875 | $0.075 |
| gemini-2.0-flash | $0.10 | $0.40 |
| gemini-1.5-flash | $0.075 | $0.30 |
| gemini-1.5-pro | $1.25 | $5.00 |

### Estimated Tokens per Analysis

| Agent | Input Tokens | Output Tokens |
|-------|--------------|---------------|
| Fundamental | ~2000 | ~800 |
| Technical | ~2500 | ~800 |
| Sentiment | ~1800 | ~700 |
| Macro | ~1500 | ~600 |
| Regulatory | ~1200 | ~600 |
| Predictor | ~3200 | ~800 |
| **Total** | **~12,200** | **~4,300** |

---

## Ranking Methodology

### 1. Overall Score (Backend - Daily)

Weighted composite of five sub-scores:

```
Overall Score = (wF × Fundamental) + (wT × Technical) + (wS × Sentiment) + (wM × Macro) + (wR × Risk)
```

| Component | Weight | Description |
|-----------|--------|-------------|
| Fundamental | 40% | Financial health metrics |
| Technical | 25% | Price momentum & trends |
| Sentiment | 15% | Analyst & news sentiment |
| Macro | 10% | Economic environment |
| Risk | 10% | Volatility & safety |

### 2. Momentum Rank (Frontend - Weekly)

```
Momentum Score = (0.30 × 4W Return) + (0.40 × 13W Return) + (0.20 × RSI Adjustment) + (0.10 × Volume Bonus)
```

### 3. Monthly Momentum Rank (Frontend - Monthly)

Similar to weekly with different weights:
- Monthly return: 30%
- 3-month return: 40%
- 6-month return: 20%
- 12-month return: 10%

---

## Authentication

- **Provider**: Google OAuth via Supabase Auth
- **Session Management**: JWT tokens stored in cookies
- **Protected Routes**: All API routes require authentication (configurable)

---

## Environment Variables

### Frontend (Vercel)
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_AGENT_API_URL=http://localhost:8000
```

### Backend - Pipeline (Python)
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Backend - Agents (Python)
```env
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your_supabase_key
```

---

## Known Issues & Data Quality

### NULL Fields in monthly_analysis
The following fields require pipeline updates:
1. `positive_months_12m` - Count of positive months in last 12
2. `avg_monthly_return_12m` - Average monthly return over 12 months
3. `best_month_return_12m` - Best month return in 12 months
4. `worst_month_return_12m` - Worst month return in 12 months

### YTD Return
The `ytd_return_pct` field shows 0.00% for January records (technically correct).

### nsetools Availability
Optional dependency - system falls back to yfinance if unavailable.

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| Jan 2025 | 2.0 | Added V2 table components with ranking |
| Jan 2025 | 2.1 | Added tab-specific charts (Weekly/Monthly/Seasonality) |
| Jan 2025 | 2.2 | Added tab-specific column pickers |
| Jan 2026 | 3.0 | **🆕 Multi-Agent AI System** with 6 specialized agents |
| Jan 2026 | 3.1 | **🆕 SSE Streaming** for real-time agent updates |
| Jan 2026 | 3.2 | **🆕 Observability & FinOps** with cost tracking |
| Jan 2026 | 3.3 | **🆕 ObservabilityDashboard** component |
| Jan 2026 | 3.4 | **🆕 A2A Patterns, Critical Issues & Optimizations** from log analysis |
| Jan 2026 | 3.5 | **✅ Token Optimization Implemented** - `_get_agent_specific_data()` & `_clean_for_predictor()` |

---

## Future Enhancements

1. **Real-time Streaming**: WebSocket support for live analysis updates
2. **Custom Agents**: Allow users to define custom analysis agents
3. **Historical Backtesting**: Test recommendations against historical data
4. **Portfolio Analysis**: Analyze entire portfolios, not just individual stocks
5. **Alert System**: Notify when recommendation changes
6. **Model A/B Testing**: Compare different LLM model outputs
7. **Cached Analysis**: Cache recent analyses to reduce API costs

---

*Last Updated: January 20, 2026*
*Version: 3.5.0*

