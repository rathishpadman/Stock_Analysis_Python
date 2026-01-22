# NIFTY Agent System - Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Agent Flow Explained](#agent-flow-explained-for-beginners)
4. [Agent Personas & System Prompts](#agent-personas--system-prompts)
5. [Components](#components)
6. [Data Sources](#data-sources)
7. [API Reference](#api-reference)
8. [Setup & Installation](#setup--installation)
9. [Usage Examples](#usage-examples)
10. [Testing](#testing)
11. [Troubleshooting](#troubleshooting)

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

1. **Real-time Streaming**: WebSocket support for live analysis updates
2. **Custom Agents**: Allow users to define custom analysis agents
3. **Historical Backtesting**: Test recommendations against historical data
4. **Portfolio Analysis**: Analyze entire portfolios, not just individual stocks
5. **Alert System**: Notify when recommendation changes

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
*Version: 1.0.0*
