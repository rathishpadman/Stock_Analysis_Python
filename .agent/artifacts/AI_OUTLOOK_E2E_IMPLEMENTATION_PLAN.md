# AI Outlook Enhancement - E2E Implementation & Test Plan

## Status: PHASE 1, 2 & 3 COMPLETE ✅ 
## Created: 2026-02-07
## Last Updated: 2026-02-07 13:20

---

## 🎯 OBJECTIVE

Enhance Weekly/Monthly/Seasonality AI Outlook to:
1. Use NIFTY 200 stock data (not NIFTY 50 index)
2. Replace placeholder FII/DII with real data from nsepython
3. Differentiate outputs for each time horizon
4. Ensure no code breakage or deployment issues

---

## 📋 PRE-IMPLEMENTATION CHECKLIST

### Data Sources Verified ✅
- [x] `weekly_analysis` table: 200 stocks, 55 weeks
- [x] `monthly_analysis` table: 200 stocks, 24 months  
- [x] `seasonality` table: 200 stocks, 12 months avg
- [x] `daily_stocks` table: 200 stocks, 11 sectors
- [x] `nsepython.nse_fiidii()`: Live FII/DII data
- [x] `nsepython.indiavix()`: Live VIX
- [x] `nsepython.nse_events()`: 856 upcoming events

### Current Code Baseline
- [x] `nifty_agents/agents/temporal_crews.py` - Main crew logic
- [x] `nifty_agents/tools/supabase_fetcher.py` - Data fetching
- [x] `nifty_agents/tools/india_macro_fetcher.py` - Macro data
- [x] `nifty_agents/api.py` - FastAPI endpoints

---

## 📝 TODO LIST

### Phase 1: Create New Data Fetching Module (Non-Breaking)
**Goal**: Add new functions without modifying existing ones

| # | Task | File | Status | Test |
|---|------|------|--------|------|
| 1.1 | Create `get_nifty200_weekly_summary()` | supabase_fetcher.py | ⬜ TODO | Unit test |
| 1.2 | Create `get_nifty200_monthly_summary()` | supabase_fetcher.py | ⬜ TODO | Unit test |
| 1.3 | Create `get_nifty200_seasonality_summary()` | supabase_fetcher.py | ⬜ TODO | Unit test |
| 1.4 | Create `get_sector_weekly_performance()` | supabase_fetcher.py | ⬜ TODO | Unit test |
| 1.5 | Create `get_live_market_data()` (nsepython wrapper) | NEW: nse_live_fetcher.py | ⬜ TODO | Unit test |

### Phase 2: Create Test Scripts
**Goal**: Verify all new functions work before integration

| # | Task | File | Status |
|---|------|------|--------|
| 2.1 | Create test for weekly summary function | test_new_data_functions.py | ⬜ TODO |
| 2.2 | Create test for monthly summary function | test_new_data_functions.py | ⬜ TODO |
| 2.3 | Create test for seasonality function | test_new_data_functions.py | ⬜ TODO |
| 2.4 | Create test for live market data | test_new_data_functions.py | ⬜ TODO |
| 2.5 | Run all tests locally | - | ⬜ TODO |

### Phase 3: Integrate with Temporal Crews (Careful Modification)
**Goal**: Update crews to use new data sources

| # | Task | File | Status | Rollback Plan |
|---|------|------|--------|---------------|
| 3.1 | Update `WeeklyAnalysisCrew.analyze()` | temporal_crews.py | ⬜ TODO | Keep old code commented |
| 3.2 | Update `MonthlyAnalysisCrew.analyze()` | temporal_crews.py | ⬜ TODO | Keep old code commented |
| 3.3 | Update `SeasonalityAnalysisCrew.analyze()` | temporal_crews.py | ⬜ TODO | Keep old code commented |
| 3.4 | Replace placeholder `get_fii_dii_data()` | temporal_crews.py | ⬜ TODO | Feature flag |

### Phase 4: Local E2E Testing
**Goal**: Test complete flow before deployment

| # | Task | Test Command | Expected Result |
|---|------|--------------|-----------------|
| 4.1 | Start local API | `python -m nifty_agents.api` | Server starts on 8000 |
| 4.2 | Test weekly endpoint | `curl localhost:8000/api/agent/weekly-outlook` | Valid JSON with NIFTY200 data |
| 4.3 | Test monthly endpoint | `curl localhost:8000/api/agent/monthly-thesis` | Valid JSON with monthly data |
| 4.4 | Test seasonality endpoint | `curl localhost:8000/api/agent/seasonality` | Valid JSON with calendar data |
| 4.5 | Verify FII/DII in output | Check JSON response | Real FII/DII values (not placeholder) |
| 4.6 | Verify no errors in logs | Check console | No exceptions |

### Phase 5: Deployment Preparation
**Goal**: Ensure production-ready

| # | Task | Status |
|---|------|--------|
| 5.1 | Add `nsepython` to requirements.txt | ⬜ TODO |
| 5.2 | Verify Render has all env vars | ⬜ TODO |
| 5.3 | Test on Render (after push) | ⬜ TODO |
| 5.4 | Verify dashboard works with new API | ⬜ TODO |

---

## 🔧 DETAILED IMPLEMENTATION SPECS

### 1.1 `get_nifty200_weekly_summary()`

```python
def get_nifty200_weekly_summary() -> Dict[str, Any]:
    """
    Get aggregated weekly summary for NIFTY 200 stocks.
    
    Returns:
        {
            "week_ending": "2026-02-06",
            "total_stocks": 200,
            "market_summary": {
                "avg_weekly_return": 1.92,
                "advances": 129,
                "declines": 71,
                "ad_ratio": 1.82,
                "avg_rsi": 50.74,
                "overbought_count": 9,
                "oversold_count": 5
            },
            "sector_performance": [
                {"sector": "Utilities", "avg_return": 5.66, "advances": 12, "declines": 2},
                ...
            ],
            "top_gainers": [...],
            "top_losers": [...],
            "trend_distribution": {"UP": 53, "DOWN": 64, "SIDEWAYS": 83}
        }
    """
```

### 1.5 `get_live_market_data()`

```python
def get_live_market_data() -> Dict[str, Any]:
    """
    Get live market data from nsepython.
    
    Returns:
        {
            "fii_dii": {
                "fii_net": 1950.77,
                "dii_net": -1265.06,
                "date": "06-Feb-2026"
            },
            "india_vix": 11.94,
            "market_status": {...},
            "upcoming_events": [...]
        }
    """
```

---

## 🧪 TEST PLAN

### Unit Tests (Phase 2)

```python
# test_new_data_functions.py

def test_nifty200_weekly_summary():
    """Test weekly summary returns valid data."""
    result = get_nifty200_weekly_summary()
    assert result is not None
    assert "total_stocks" in result
    assert result["total_stocks"] == 200
    assert "market_summary" in result
    assert "advances" in result["market_summary"]
    assert "sector_performance" in result
    print("✅ Weekly summary test passed")

def test_nifty200_monthly_summary():
    """Test monthly summary returns valid data."""
    result = get_nifty200_monthly_summary()
    assert result is not None
    assert "avg_monthly_return" in result
    print("✅ Monthly summary test passed")

def test_live_market_data():
    """Test live market data from nsepython."""
    result = get_live_market_data()
    assert "fii_dii" in result
    assert result["fii_dii"]["fii_net"] != 0  # Not placeholder
    assert "india_vix" in result
    print("✅ Live market data test passed")
```

### Integration Tests (Phase 4)

```bash
# Test 1: API starts without errors
python -m nifty_agents.api &
sleep 5
curl -s http://localhost:8000/health | grep -q "ok"
echo "✅ API health check passed"

# Test 2: Weekly endpoint returns valid JSON
response=$(curl -s http://localhost:8000/api/agent/weekly-outlook)
echo $response | python -c "import json,sys; d=json.load(sys.stdin); assert 'synthesis' in d"
echo "✅ Weekly endpoint test passed"

# Test 3: FII/DII is real data (not placeholder)
echo $response | python -c "import json,sys; d=json.load(sys.stdin); assert d.get('agent_analyses',{}).get('risk_regime',{}).get('flow_analysis',{}).get('fii_5day_cr') != -1500"
echo "✅ FII/DII is real data"
```

---

## 🔄 ROLLBACK PLAN

### If Something Breaks:

1. **Immediate Rollback**: Revert to previous commit
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Feature Flag Approach**: Keep old code with flag
   ```python
   USE_NEW_DATA_SOURCES = os.environ.get("USE_NEW_DATA_SOURCES", "false") == "true"
   
   if USE_NEW_DATA_SOURCES:
       data = get_nifty200_weekly_summary()
   else:
       data = get_weekly_analysis("NIFTY50", weeks=4)  # Old way
   ```

3. **Gradual Rollout**: Test in Render preview before main

---

## 📊 SUCCESS CRITERIA

### Must Pass Before Merge:

| Criteria | Verification |
|----------|--------------|
| All unit tests pass | `python -m pytest test_new_data_functions.py` |
| API starts without errors | Server logs show no exceptions |
| Weekly endpoint returns NIFTY 200 data | `total_stocks == 200` in response |
| FII/DII shows real values | Not `-1500` or `2000` (placeholders) |
| VIX shows current value | Matches nsepython output |
| No import errors | All modules load correctly |
| Render deployment succeeds | Green status in Render dashboard |
| Dashboard displays data | UI shows correct values |

---

## 📁 FILES TO BE MODIFIED

| File | Type | Risk Level |
|------|------|------------|
| `nifty_agents/tools/supabase_fetcher.py` | Add new functions | 🟢 Low (additive) |
| `nifty_agents/tools/nse_live_fetcher.py` | NEW file | 🟢 Low (new) |
| `nifty_agents/agents/temporal_crews.py` | Modify analyze() | 🟡 Medium |
| `requirements.txt` | Add nsepython | 🟢 Low |
| `test_new_data_functions.py` | NEW file | 🟢 Low (test) |

---

## ⏱️ ESTIMATED TIMELINE

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: New data functions | 2 hours | 2 hours |
| Phase 2: Test scripts | 1 hour | 3 hours |
| Phase 3: Integration | 1.5 hours | 4.5 hours |
| Phase 4: Local E2E testing | 1 hour | 5.5 hours |
| Phase 5: Deployment | 0.5 hour | 6 hours |

---

## 🚀 EXECUTION COMMAND

When ready to proceed, run:
```
"Please proceed with Phase 1 of the AI Outlook implementation plan"
```

---

## NOTES

- All changes are additive first (new functions), then integrative
- Old code preserved as comments for easy rollback
- Each phase has verification before proceeding
- nsepython provides live data with no API key needed
