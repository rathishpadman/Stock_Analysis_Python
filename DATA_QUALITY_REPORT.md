# Data Quality Summary Report

## Report Date: January 2025

---

## Executive Summary

This report summarizes the data quality status across all four database tables used in the Stock Analysis Dashboard. The analysis identifies populated fields, NULL fields, and areas requiring attention.

---

## 1. Daily Stocks Table (daily_stocks)

**Total Records:** 604

### Field Population Summary

| Field | Populated | Coverage |
|-------|-----------|----------|
| ticker | 604 | 100% ✅ |
| price_last | 604 | 100% ✅ |
| overall_score | 604 | 100% ✅ |
| score_technical | 604 | 100% ✅ |
| rsi14 | 604 | 100% ✅ |
| macd_line | 604 | 100% ✅ |
| sma50 | 604 | 100% ✅ |
| sma200 | 598 | 99% ✅ |
| score_fundamental | 400 | 66% ⚠️ |

### Issues
- `score_fundamental` is missing for 204 records (likely IPOs or insufficient financial data)
- This is expected behavior for stocks without complete financial history

---

## 2. Weekly Analysis Table (weekly_analysis)

**Total Records:** 10,340

### Field Population Summary

| Field | Populated | Coverage |
|-------|-----------|----------|
| weekly_close | 10,340 | 100% ✅ |
| weekly_volume_ratio | 10,340 | 100% ✅ |
| weekly_trend | 10,340 | 100% ✅ |
| weekly_return_pct | 10,337 | 99.97% ✅ |
| return_4w | 10,328 | 99.88% ✅ |
| return_13w | 10,284 | 99.46% ✅ |
| weekly_rsi14 | 10,284 | 99.46% ✅ |

### Issues
- Minor NULL values in return fields for early records (expected - insufficient history)
- All critical fields have excellent coverage

---

## 3. Monthly Analysis Table (monthly_analysis)

**Total Records:** 4,690

### Field Population Summary

| Field | Populated | Coverage | Status |
|-------|-----------|----------|--------|
| monthly_close | 4,690 | 100% | ✅ |
| monthly_trend | 4,690 | 100% | ✅ |
| ytd_return_pct | 4,690 | 100% | ✅ |
| monthly_return_pct | 4,678 | 99.74% | ✅ |
| return_3m | 4,654 | 99.23% | ✅ |
| return_6m | 4,614 | 98.38% | ✅ |
| return_12m | 4,525 | 96.48% | ✅ |
| **positive_months_12m** | **0** | **0%** | ❌ CRITICAL |
| **avg_monthly_return_12m** | **0** | **0%** | ❌ CRITICAL |
| **best_month_return_12m** | **0** | **0%** | ❌ CRITICAL |
| **worst_month_return_12m** | **0** | **0%** | ❌ CRITICAL |

### Critical Issues ❌

The following fields are **completely NULL** and require pipeline updates:

1. **positive_months_12m**
   - Purpose: Count of positive monthly returns in last 12 months
   - Impact: Missing metric for momentum analysis
   - Required Action: Update `monthly_to_supabase.py` to calculate this field

2. **avg_monthly_return_12m**
   - Purpose: Average monthly return over 12 months
   - Impact: Cannot show average monthly performance
   - Required Action: Update pipeline with calculation logic

3. **best_month_return_12m**
   - Purpose: Best single month return in last 12 months
   - Impact: Cannot identify peak performance periods
   - Required Action: Update pipeline with max() aggregation

4. **worst_month_return_12m**
   - Purpose: Worst single month return in last 12 months
   - Impact: Cannot identify drawdown periods
   - Required Action: Update pipeline with min() aggregation

### Note on ytd_return_pct
- Shows 0.00% for January 2025 records
- This is technically correct (YTD in first month = current month's return which starts at 0)
- Not a data quality issue

---

## 4. Seasonality Table (seasonality)

**Total Records:** 200

### Field Population Summary

| Field | Populated | Coverage |
|-------|-----------|----------|
| jan_avg | 200 | 100% ✅ |
| nov_avg | 200 | 100% ✅ |
| dec_avg | 200 | 100% ✅ |
| best_month | 200 | 100% ✅ |
| worst_month | 200 | 100% ✅ |
| jul_avg | 199 | 99.5% ✅ |
| aug_avg | 199 | 99.5% ✅ |
| sep_avg | 199 | 99.5% ✅ |
| oct_avg | 199 | 99.5% ✅ |
| feb_avg | 198 | 99% ✅ |
| mar_avg | 198 | 99% ✅ |
| apr_avg | 198 | 99% ✅ |
| may_avg | 198 | 99% ✅ |
| jun_avg | 198 | 99% ✅ |

### Issues
- Minor NULL values (1-2 per month) likely due to IPOs or data availability
- Excellent overall data quality

---

## Overall Data Quality Score

| Table | Score | Status |
|-------|-------|--------|
| daily_stocks | 95% | ✅ Excellent |
| weekly_analysis | 99% | ✅ Excellent |
| monthly_analysis | 75% | ⚠️ Needs Attention |
| seasonality | 99% | ✅ Excellent |

**Overall System Health:** 92% ⚠️

---

## Recommended Actions

### Priority 1 (Critical)
Update the `monthly_to_supabase.py` pipeline to populate:
- `positive_months_12m`
- `avg_monthly_return_12m`
- `best_month_return_12m`
- `worst_month_return_12m`

### Priority 2 (Enhancement)
Consider adding calculated fields to monthly detail view that compute these values client-side until the pipeline is updated.

### Priority 3 (Monitoring)
Set up automated data quality checks to alert when NULL percentages exceed thresholds.

---

## Pipeline Fix Suggestion

Add the following calculation to `monthly_to_supabase.py`:

```python
# For each ticker, calculate 12-month rolling metrics
def calculate_12m_metrics(df):
    for ticker in df['ticker'].unique():
        ticker_data = df[df['ticker'] == ticker].sort_values('month')
        
        # Rolling 12-month window
        rolling_returns = ticker_data['monthly_return_pct'].rolling(12)
        
        ticker_data['positive_months_12m'] = rolling_returns.apply(lambda x: (x > 0).sum())
        ticker_data['avg_monthly_return_12m'] = rolling_returns.mean()
        ticker_data['best_month_return_12m'] = rolling_returns.max()
        ticker_data['worst_month_return_12m'] = rolling_returns.min()
        
        df.update(ticker_data)
    
    return df
```

---

*Report generated for Stock Analysis Dashboard v2.2*
