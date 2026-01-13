# 📑 INDEX: Sector Median Analysis & Conditional Formatting

## 🎯 Quick Navigation

### 📌 START HERE
**[VISUAL_SUMMARY.md](./VISUAL_SUMMARY.md)** ← Best for visual learners (5 min read)
- Problem: Why is Sector P/E blank?
- Solution: How to add conditional formatting
- Before/After comparison
- Step-by-step execution

---

## 📚 Detailed Documentation

### 1. Analysis Documents

**[SECTOR_MEDIAN_ANALYSIS.md](../SECTOR_MEDIAN_ANALYSIS.md)**
- ✓ Root cause analysis (why column is blank)
- ✓ Current vs. needed code flow
- ✓ Solution approach with code example
- ✓ Impact assessment
- **Read if:** You want to understand the gap deeply

**[ANALYSIS_SUMMARY.md](../ANALYSIS_SUMMARY.md)**
- ✓ Executive summary of both issues
- ✓ Quick fix for sector median P/E
- ✓ 15 metrics with thresholds table
- ✓ Next steps checklist
- **Read if:** You want a quick overview

### 2. Implementation Guides

**[CONDITIONAL_FORMATTING_GUIDE.md](./CONDITIONAL_FORMATTING_GUIDE.md)**
- ✓ How to set up conditional formatting
- ✓ Step-by-step installation
- ✓ What the script does
- ✓ Troubleshooting section
- **Read if:** You're implementing the formatter

**[FORMATTING_QUICK_REFERENCE.md](./FORMATTING_QUICK_REFERENCE.md)**
- ✓ Color legend (Green/Yellow/Red)
- ✓ All 15 metrics with thresholds
- ✓ How to read the formatted template
- ✓ Practical examples
- **Read if:** You want a handy reference sheet

---

## 💻 Implementation Files

### Configuration Files

**`conditional_format_rules.csv`**
```
Purpose: Defines all formatting rules (Good/Neutral/Poor thresholds)
Columns: Metric Category, Parameter, Good, Neutral, Poor, Rationale
Rows: 15 metrics with industry context
Usage: Read by apply_conditional_formatting.py
```

### Python Scripts

**`apply_conditional_formatting.py`**
```
Purpose: Applies Excel conditional formatting to template
Input: Stocks_Analysis_Template_v3.xlsx + conditional_format_rules.csv
Output: Updated template with colors + Legend sheet
Usage: python apply_conditional_formatting.py
```

---

## 🔧 How to Use

### Scenario 1: Apply Formatting Now
```
1. cd Stock_Analysis_Python
2. python apply_conditional_formatting.py
3. Open Stocks_Analysis_Template_v3.xlsx
4. Verify "Legend" sheet exists
5. Run pipeline: python run_refresh.py ...
6. See colored output!
```

### Scenario 2: Understand the Gap
```
1. Read: VISUAL_SUMMARY.md (5 min)
2. Read: SECTOR_MEDIAN_ANALYSIS.md (10 min)
3. Decide: Implement sector median fix? (optional)
4. Code example provided in ANALYSIS_SUMMARY.md
```

### Scenario 3: Quick Reference
```
1. Open: FORMATTING_QUICK_REFERENCE.md
2. Look up metric thresholds
3. Understand Green/Yellow/Red colors
4. Reference while analyzing Excel output
```

---

## 📊 The 15 Metrics

| Category | Metrics |
|----------|---------|
| **Valuation** | P/E (TTM), P/S Ratio, P/B |
| **Profitability** | ROA %, ROE TTM %, Gross Margin % |
| **Leverage** | Debt/Equity, Interest Coverage, Current Ratio |
| **Growth** | Revenue Growth YoY %, EPS Growth YoY % |
| **Technical** | RSI14, MACD Hist |
| **Income** | Dividend Yield % |

See each markdown file for specific thresholds.

---

## ❓ FAQ

**Q: Why is "Sector P/E (Median)" blank in my output?**  
A: See `SECTOR_MEDIAN_ANALYSIS.md` — no sector aggregation logic implemented yet.

**Q: How do I apply the conditional formatting?**  
A: Run `python apply_conditional_formatting.py` — see `CONDITIONAL_FORMATTING_GUIDE.md`

**Q: What do the colors mean?**  
A: 🟢 Good, 🟡 Neutral, 🔴 Poor — see `FORMATTING_QUICK_REFERENCE.md`

**Q: Can I customize the thresholds?**  
A: Yes! Edit `conditional_format_rules.csv` and re-run the script.

**Q: Will the formatting work with my existing data?**  
A: Yes, apply the script first, then populate data. Colors update automatically.

**Q: How hard is it to fix the Sector P/E column?**  
A: Easy! 3 lines of code in `pipeline.py` — see `ANALYSIS_SUMMARY.md`

---

## 🚀 Recommended Reading Order

### For Visual Learners
1. VISUAL_SUMMARY.md (start here)
2. FORMATTING_QUICK_REFERENCE.md (reference)
3. CONDITIONAL_FORMATTING_GUIDE.md (how-to)

### For Technical Readers
1. SECTOR_MEDIAN_ANALYSIS.md (deep dive)
2. ANALYSIS_SUMMARY.md (implementation)
3. CONDITIONAL_FORMATTING_GUIDE.md (setup)

### For Decision Makers
1. ANALYSIS_SUMMARY.md (executive summary)
2. CONDITIONAL_FORMATTING_GUIDE.md (time/effort)
3. FORMATTING_QUICK_REFERENCE.md (benefits)

---

## 📋 File Locations

### In Root Folder (Equity research/)
```
SECTOR_MEDIAN_ANALYSIS.md
ANALYSIS_SUMMARY.md
VISUAL_SUMMARY.md
README_FORMATTING.md (this file)
```

### In Stock_Analysis_Python/
```
conditional_format_rules.csv
apply_conditional_formatting.py
CONDITIONAL_FORMATTING_GUIDE.md
FORMATTING_QUICK_REFERENCE.md
```

---

## ✅ Checklist: Next Steps

- [ ] Read VISUAL_SUMMARY.md (5 min)
- [ ] Run `apply_conditional_formatting.py` (1 min)
- [ ] Open template, check "Legend" sheet (2 min)
- [ ] Run pipeline with formatted template (4 sec)
- [ ] Open output, verify colors are showing (1 min)
- [ ] (Optional) Implement sector median P/E fix (10 min)

**Total Time: ~20 minutes** ⏱️

---

## 🎯 Key Decisions

### Should I apply conditional formatting?
✅ YES
- Takes 1 minute
- Makes output professional
- Enables quick visual scanning
- Zero risk (doesn't change data)

### Should I fix the Sector P/E column?
✅ OPTIONAL
- Takes 10 minutes
- Enables sector-relative valuation
- High impact for analysis
- 3 lines of code

### Should I customize the thresholds?
🤔 AS NEEDED
- Easy to edit CSV
- Industry-specific adjustments possible
- Re-run script to apply
- No code changes needed

---

## 💡 Benefits

| Feature | Benefit |
|---------|---------|
| **Conditional Formatting** | Instant visual feedback on metrics |
| **Sector P/E Median** | Benchmark individual stocks vs. peers |
| **Color Coding** | Easy identification of outliers |
| **Legend Sheet** | Quick reference for thresholds |
| **CSV Rules** | Easy customization without coding |

---

## 🔗 Related Files in Repo

```
Stock_Analysis_Python/
├── run_refresh.py              ← Main pipeline runner
├── run_equity_pipeline.bat     ← Batch file
├── equity_engine/
│   ├── pipeline.py             ← Core pipeline (where sector median could be added)
│   ├── data_sources.py         ← Data fetching
│   ├── indicators.py           ← Technical indicators
│   └── scoring.py              ← Scoring logic
├── Stocks_Analysis_Template_v3.xlsx  ← Template to format
├── conditional_format_rules.csv      ← Rules (new!)
└── apply_conditional_formatting.py   ← Formatter (new!)
```

---

## 📞 Support

**Error running formatter?**
→ See "Troubleshooting" in `CONDITIONAL_FORMATTING_GUIDE.md`

**Don't understand thresholds?**
→ See "Practical Example" in `FORMATTING_QUICK_REFERENCE.md`

**Want to add Sector P/E?**
→ See "Fix Sector P/E Median" section in `ANALYSIS_SUMMARY.md`

**Need background on the gap?**
→ Read `SECTOR_MEDIAN_ANALYSIS.md` for full technical details

---

**Created:** October 20, 2025  
**Status:** Ready to implement ✅  
**Effort:** 20 minutes total  
**Impact:** High (professional formatting + data insights)  

