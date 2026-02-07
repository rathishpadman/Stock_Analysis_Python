# Weekly AI Outlook Fix - Execution & Test Plan

## Document Info
- **Created**: 2026-02-07
- **Status**: ✅ IMPLEMENTED & TESTED
- **Risk Level**: Medium (involves data pipeline and AI agents)
- **Implementation Date**: 2026-02-07

---

## 🎯 Objectives

1. ✅ **Fix incomplete NIFTY50 data** - Added index data sourcing via yfinance fallback
2. ⏳ **Differentiate Weekly/Monthly/Seasonal outputs** - Pending further testing after deploy
3. ✅ **Improve error handling** - Graceful fallbacks when Supabase data is missing
4. ✅ **Maintain backward compatibility** - Existing stock data flows unchanged

---

## 📋 Pre-Implementation Checklist

- [x] Render environment updated with new GOOGLE_API_KEY
- [ ] Backup current working state
- [ ] Verify Supabase connection works locally
- [ ] Verify current dashboard loads without errors

---

## 🔄 Execution Plan

### Phase 1: Add NIFTY50 Index Data Fallback (Primary Fix)

**Goal**: Ensure the AI agents can get NIFTY50 index data even if not in `weekly_analysis` table.

#### Step 1.1: Enhance `supabase_fetcher.py` - Add Index Data Alternative
**File**: `nifty_agents/tools/supabase_fetcher.py`
**Changes**:
- Add `get_index_weekly_data()` function to fetch index data from yfinance as fallback
- Modify `get_weekly_analysis()` to handle index requests specially
- Add caching to avoid repeated API calls

**Risk**: Low - Adding new function, not modifying existing logic

#### Step 1.2: Update `temporal_crews.py` - Use Enhanced Data Fetching
**File**: `nifty_agents/agents/temporal_crews.py`
**Changes**:
- In `WeeklyAnalysisCrew.analyze()`, use the enhanced data fetching
- Add market breadth aggregation from existing stock data as fallback
- Improve error handling for missing data scenarios

**Risk**: Medium - Modifying existing analysis flow

### Phase 2: Differentiate Analysis Outputs

**Goal**: Ensure Weekly/Monthly/Seasonal produce distinct, time-horizon-appropriate analyses.

#### Step 2.1: Review and Enhance Agent Prompts
**File**: `nifty_agents/agents/temporal_crews.py`
**Changes**:
- Verify WEEKLY_AGENT_PROMPTS are clearly weekly-focused
- Verify MONTHLY_AGENT_PROMPTS are clearly monthly-focused
- Verify SEASONALITY_AGENT_PROMPTS focus on historical patterns

**Risk**: Low - Prompt refinement only

#### Step 2.2: Add Data Context Differentiation
**File**: `nifty_agents/agents/temporal_crews.py`
**Changes**:
- Weekly: Use 4-week data window, focus on immediate technicals
- Monthly: Use 6-month data window, focus on macro trends
- Seasonality: Use historical patterns, focus on calendar effects

**Risk**: Low - Adding more specific data filtering

### Phase 3: Improve Error Handling & Observability

**Goal**: Better diagnostics when issues occur.

#### Step 3.1: Add Detailed Logging
**File**: `nifty_agents/agents/temporal_crews.py`
**Changes**:
- Add logging for data fetch success/failure
- Log data availability before LLM call
- Log fallback usage

**Risk**: Low - Logging only

---

## 🧪 Test Plan (E2E)

### Stage 1: Unit Tests (Pre-Implementation Baseline)

```bash
# Run from project root
cd c:\Rathish\Root Folder\Equity research\Stock_Analysis_Python

# Test 1.1: Verify Python environment
python -c "import equity_engine; print('equity_engine OK')"
python -c "from nifty_agents.tools.supabase_fetcher import get_supabase_client; print('supabase_fetcher OK')"

# Test 1.2: Verify Supabase connection
python -c "
from nifty_agents.tools.supabase_fetcher import get_market_breadth
result = get_market_breadth()
print(f'Market Breadth: {result}')
"

# Test 1.3: Check current weekly analysis data
python -c "
from nifty_agents.tools.supabase_fetcher import get_weekly_analysis
result = get_weekly_analysis('RELIANCE', weeks=2)
print(f'RELIANCE Weekly Data: {result}')
"
```

### Stage 2: Integration Tests (Post-Implementation)

```bash
# Test 2.1: Test enhanced index data fetching (new function)
python -c "
from nifty_agents.tools.supabase_fetcher import get_index_weekly_data
result = get_index_weekly_data('NIFTY50')
print(f'NIFTY50 Index Data: {result}')
"

# Test 2.2: Test weekly outlook data gathering
python -c "
from nifty_agents.agents.temporal_crews import WeeklyAnalysisCrew
crew = WeeklyAnalysisCrew()
# Test data gathering only (no LLM call)
trend_data = crew._get_market_breadth_data()
print(f'Market Breadth Data: {trend_data}')
"
```

### Stage 3: Local API Tests

```bash
# Start local API server (in separate terminal)
cd c:\Rathish\Root Folder\Equity research\Stock_Analysis_Python\nifty_agents
set GOOGLE_API_KEY=<your_key>
uvicorn api:app --reload --port 8000

# Test 3.1: Check temporal status endpoint
curl http://localhost:8000/api/agent/temporal/status

# Expected response:
# {
#   "temporal_crews_available": true,
#   "api_key_configured": true,
#   ...
# }

# Test 3.2: Test weekly outlook (short timeout - check it starts)
curl --max-time 30 http://localhost:8000/api/agent/weekly-outlook

# Test 3.3: Test monthly thesis
curl --max-time 30 http://localhost:8000/api/agent/monthly-thesis

# Test 3.4: Test seasonality
curl --max-time 30 http://localhost:8000/api/agent/seasonality
```

### Stage 4: Dashboard E2E Tests

```bash
# Start dashboard (in separate terminal)
cd c:\Rathish\Root Folder\Equity research\Stock_Analysis_Python\dashboard
npm run dev

# Then in browser:
# 1. Navigate to http://localhost:3000
# 2. Verify dashboard loads without errors
# 3. Navigate to the page with Weekly AI Outlook
# 4. Click "Generate" button
# 5. Verify no 429 error appears
# 6. Verify data is populated (not all zeros)
# 7. Repeat for Monthly and Seasonality
# 8. Verify outputs are different for each type
```

### Stage 5: Production Verification (Post-Deploy)

```bash
# Test 5.1: Test Render API directly
curl https://nifty-agents-api.onrender.com/api/agent/temporal/status

# Test 5.2: Test weekly outlook via Render
curl --max-time 120 https://nifty-agents-api.onrender.com/api/agent/weekly-outlook
```

---

## ✅ Success Criteria

| Criterion | Description | How to Verify |
|-----------|-------------|---------------|
| No 429 Errors | LLM calls succeed | Dashboard shows analysis without error |
| NIFTY50 Data Present | Index values populated | Trend Analysis shows non-zero values |
| Distinct Outputs | Weekly ≠ Monthly ≠ Seasonal | Compare analysis headlines and stances |
| Backward Compatible | Existing features work | Dashboard loads, stocks show data |
| Error Handling | Graceful fallbacks | If one data source fails, analysis still works |

---

## 🔙 Rollback Plan

If issues occur after implementation:

1. **Git Revert**: 
   ```bash
   git revert HEAD~N  # Where N is number of commits to revert
   ```

2. **Key Files to Restore**:
   - `nifty_agents/tools/supabase_fetcher.py`
   - `nifty_agents/agents/temporal_crews.py`

3. **Render Rollback**:
   - Render Dashboard → nifty-agents-api → Deploys → Select previous working deploy → Redeploy

---

## 📁 Files to Modify

| File | Changes | Risk |
|------|---------|------|
| `nifty_agents/tools/supabase_fetcher.py` | Add `get_index_weekly_data()` function | Low |
| `nifty_agents/agents/temporal_crews.py` | Use enhanced data fetching, improve prompts | Medium |
| `nifty_agents/tools/__init__.py` | Export new function | Low |

---

## 🚀 Implementation Order

1. **Run baseline tests** (Stage 1)
2. **Implement Step 1.1** - Add index data function
3. **Run integration test 2.1** - Verify new function works
4. **Implement Step 1.2** - Update temporal_crews
5. **Run integration test 2.2** - Verify data gathering
6. **Start local API and run Stage 3 tests**
7. **Run Stage 4 dashboard tests**
8. **Commit and push to GitHub**
9. **Render auto-deploys, run Stage 5 tests**
10. **Document results**

---

## 📝 Notes

- All changes are additive (new functions) or defensive (fallbacks)
- Existing code paths remain unchanged for stocks
- Only NIFTY50/index handling is enhanced
- LLM prompts may need iteration based on output quality
