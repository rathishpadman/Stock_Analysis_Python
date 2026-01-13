# Setup Guide: Conditional Formatting & Analysis

## 📋 Files Created

### 1. **`conditional_format_rules.csv`**
   - Contains all 15 metrics with their Good/Neutral/Poor thresholds
   - Includes rationale for each metric
   - Referenced by the formatting script

### 2. **`apply_conditional_formatting.py`**
   - Python script that applies color coding to Excel template
   - Reads rules from `conditional_format_rules.csv`
   - Creates a "Legend" sheet showing all rules
   - Uses openpyxl to add conditional formatting rules

### 3. **`SECTOR_MEDIAN_ANALYSIS.md`**
   - Detailed analysis of why "Sector P/E (Median)" is blank
   - Root cause: No sector-level aggregation logic implemented
   - Includes solution approach

---

## 🎯 How to Use the Conditional Formatting Script

### Step 1: Ensure Dependencies
```bash
pip install openpyxl pandas
```

### Step 2: Run the Script
```bash
cd "c:\Rathish\Root Folder\Equity research\Stock_Analysis_Python"
python apply_conditional_formatting.py
```

### Step 3: What It Does
✅ Reads `conditional_format_rules.csv`  
✅ Opens your `Stocks_Analysis_Template_v3.xlsx`  
✅ Applies color formatting to the NIFTY50 sheet:
   - **Green**: Metric in "Good" range
   - **Yellow**: Metric in "Neutral" range
   - **Red**: Metric in "Poor" range
✅ Creates a "Legend" sheet with all rules  
✅ Saves the updated template

### Step 4: Result
When you run the pipeline and populate data, the Excel output will show:
- **Green cells** for healthy metrics
- **Yellow cells** for average metrics
- **Red cells** for concerning metrics

---

## 📊 Conditional Formatting Rules Applied

| Metric | Good | Neutral | Poor |
|--------|------|---------|------|
| **P/E (TTM)** | < 15 | 15-25 | > 25 |
| **P/S Ratio** | < 2.0 | 2.0-4.0 | > 4.0 |
| **P/B** | < 1.5 | 1.5-3.0 | > 3.0 |
| **ROA %** | > 10% | 5-10% | < 5% |
| **ROE TTM %** | > 20% | 10-20% | < 10% |
| **Gross Profit Margin %** | > 40% | 20-40% | < 20% |
| **Debt/Equity** | < 1.0 | 1.0-2.0 | > 2.0 |
| **Interest Coverage** | > 5 | 3-5 | < 3 |
| **Current Ratio** | 1.2-2.5 | 1.0-1.2 | <1.0 or >3.0 |
| **Revenue Growth YoY %** | > 15% | 5-15% | < 5% |
| **EPS Growth YoY %** | > 20% | 10-20% | < 10% |
| **RSI14** | < 30 | 30-70 | > 70 |
| **MACD Hist** | > 0 (rising) | Near 0 (flat) | < 0 (falling) |
| **Dividend Yield %** | > 3.5% | 2.0-3.5% | < 2.0% |

---

## ❓ Why "Sector P/E (Median)" is Blank

### Root Cause
The column is **defined in the template** but there's **no code that calculates it**.

Currently, the pipeline:
1. ✅ Fetches 50 stocks
2. ✅ Calculates individual stock P/E ratios
3. ❌ Does NOT group stocks by sector
4. ❌ Does NOT compute sector-level statistics

### Example of What's Needed
```python
# After stocks are merged with metadata
sector_medians = merged_final.groupby("Sector")["P/E (TTM)"].median()
merged_final["Sector P/E (Median)"] = merged_final["Sector"].map(sector_medians)
```

### Impact
- Without sector median P/E, you can't benchmark individual stocks against their peers
- Example: RELIANCE at P/E 25 looks expensive in isolation, but may be fair if Financial Services sector median is 28x

---

## 🚀 Next Steps

### Immediate (1-2 minutes):
```bash
python apply_conditional_formatting.py
```
This updates your template with color coding rules.

### Optional (10-15 minutes):
To populate "Sector P/E (Median)" column, add this to `pipeline.py` after the metadata merge:

```python
# Around line 355 in run_pipeline(), after:
# merged_final = stocks.merge(meta_subset, on="symbol", how="left", suffixes=("", "_meta"))

# Add sector-level aggregations:
sector_stats = merged_final.groupby("Sector").agg({
    "P/E (TTM)": "median"
}).rename(columns={"P/E (TTM)": "Sector P/E (Median)"})

# Join back to each stock
merged_final = merged_final.merge(sector_stats, left_on="Sector", right_index=True, how="left")
```

---

## 📌 Important Notes

1. **Conditional Formatting** applies to the template BEFORE data is populated
2. **Colors will update automatically** when you fill in data values
3. **Legend sheet** shows all rules for reference in Excel
4. **Sector P/E Median** requires code changes to implement (not yet wired)

---

## ✅ Verification Checklist

After running `apply_conditional_formatting.py`:
- [ ] Script completed without errors
- [ ] Excel template opens without issues
- [ ] "Legend" sheet visible in Excel
- [ ] P/E (TTM) column shows formatting rules active
- [ ] Run pipeline: `python run_refresh.py --template Stocks_Analysis_Template_v3.xlsx --out Stocks_Analysis_Populated.xlsx`
- [ ] Output Excel shows **Green/Yellow/Red colors** for populated metrics

---

## 📞 Troubleshooting

**Error: "conditional_format_rules.csv not found"**
→ Ensure CSV file is in same directory as `apply_conditional_formatting.py`

**Error: "Sheet 'NIFTY50' not found"**
→ Check your template sheet name (should be "NIFTY50")

**Colors not showing in output**
→ Run the formatting script BEFORE populating data
→ Or, run it again after each pipeline run

