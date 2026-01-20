# Copilot Instructions - Stock Analysis Python

## Project Overview
This is an **Indian equity analysis platform** with three main components:
1. **equity_engine/** - Python data pipeline: fetches NSE index constituents, computes technicals, and generates composite scores
2. **dashboard/** - Next.js 14+ frontend with Supabase backend for visualization
3. **nifty_agents/** - Multi-agent AI system (6 specialized agents) for deep stock analysis

## Architecture & Data Flow

```
NSE Indexes → equity_engine.build_universe() → enrich_stock() → scoring → Excel/Supabase
                                                                           ↓
                                      dashboard (Next.js) ← API routes ← Supabase (PostgreSQL)
```

### Key Database Tables
- `daily_stocks` - 110+ fields with scores, technicals, returns (rolling 30-day)
- `weekly_analysis` - Weekly OHLCV, RSI, trend, volume ratios
- `monthly_analysis` - Monthly aggregations, YTD, rolling returns
- `seasonality` - Historical monthly return averages per ticker

## Critical Commands

```bash
# Run full pipeline (generates Excel + dated folder like JAN26/)
python run_refresh.py --template Stocks_Analysis_Template_v3.xlsx

# Upload to Supabase (requires SUPABASE_URL + SUPABASE_SERVICE_KEY in .env)
python pipeline/daily_to_supabase.py
python pipeline/weekly_to_supabase.py
python pipeline/monthly_to_supabase.py

# Start dashboard
cd dashboard && npm run dev

# Start agent API (port 8000)
cd nifty_agents && uvicorn api:app --reload
```

## Code Conventions

### Python (equity_engine/)
- **Column naming**: Template columns use spaces/special chars (`"Return 1D %"`, `"P/E (TTM)"`); DB columns use snake_case (`return_1d`, `pe_ttm`)
- **`_pick_series()`** in [pipeline.py](equity_engine/pipeline.py) handles column fallbacks - always check multiple names: `["Sector", "sector", "Sector_meta"]`
- **Scoring**: All scores are 0-100 scale. See [scoring.py](equity_engine/scoring.py) `_rank_0_100()` for percentile ranking
- **Yahoo suffix**: All tickers get `.NS` suffix via `to_yahoo()` for NSE stocks

### TypeScript (dashboard/)
- Use `@/` path alias for imports (maps to `src/`)
- Supabase client in [lib/supabase.ts](dashboard/src/lib/supabase.ts) - always check env vars
- API routes at `src/app/api/{stocks,weekly,monthly,seasonality}/route.ts`
- Charts use Recharts; table components have `*V2` suffix for latest version

### Environment Variables
```bash
# Required for pipeline
STOCK_INDEXES="NIFTY 200"  # Comma-separated: "NIFTY 50,NIFTY 200"
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx

# Required for dashboard
NEXT_PUBLIC_SUPABASE_URL=xxx
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx

# Optional tuning
MAX_WORKERS=10
HISTORY_YEARS=5
```

## Important Patterns

### Adding New Metrics
1. Add to `prepare_output_df()` in [pipeline.py](equity_engine/pipeline.py) with fallback names
2. Add field mapping in [daily_to_supabase.py](pipeline/daily_to_supabase.py) `field_map`
3. Add column to [001_initial_schema.sql](supabase/migrations/001_initial_schema.sql)
4. Create/update API route in dashboard

### Score Calculation (weighted composite)
```python
# Default weights in config.py
{"fundamental": 0.40, "technical": 0.25, "sentiment": 0.15, "macro": 0.10, "risk": 0.10}
```
Modify via `WEIGHTS_JSON` env var: `fundamental=0.5;technical=0.3;sentiment=0.2`

### Agent System (nifty_agents/)
- Orchestrator dispatches to 5 specialist agents in parallel, then synthesizes via Predictor
- Agents: Fundamental, Technical, Sentiment, Macro, Regulatory → Predictor
- API at `/api/agent/analyze/{ticker}` returns full multi-agent report

## Testing
```bash
# Python tests
pytest pipeline/tests/ -v

# Dashboard tests
cd dashboard && npm test
```

## Security Best Practices

### ⚠️ NEVER Commit Sensitive Files
```bash
# Files that MUST NEVER be committed:
.env                    # Contains API keys, secrets
.env.*                  # Any .env variants
*.env                   # All env files
nifty_agents/.env.local # Agent-specific secrets
dashboard/.env.local    # Dashboard secrets

# Always check before committing:
git status --ignored | grep "\.env"
```

### Environment Variables
- **NEVER** hardcode API keys in code
- Use `.env` files locally (already in `.gitignore`)
- Set secrets in Render.com/Vercel dashboard for production
- Required secrets:
  - `GOOGLE_API_KEY` - For Gemini LLM
  - `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` - For database
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` - For frontend

### Before Every Commit
1. ✅ Run `git status` - verify no `.env` files listed
2. ✅ Check `.gitignore` is up to date
3. ✅ Never use `git add .` blindly - be explicit
4. ✅ Review `git diff --staged` before pushing

## Common Pitfalls
- **NaN/Inf handling**: Always use `df.replace([np.inf, -np.inf], np.nan)` before JSON serialization
- **Date formats**: Supabase expects ISO dates; monthly uses `YYYY-MM` string format
- **Ticker format**: Strip `.NS` suffix when displaying, add back for yfinance calls
- **Column mismatch**: Debug with `_debug_output_df.csv` and `_debug_merged_final.csv` files generated during pipeline runs
