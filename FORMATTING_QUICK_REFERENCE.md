# 🎨 Conditional Formatting Quick Reference

## Color Legend

| Color | Meaning | Example |
|-------|---------|---------|
| 🟢 **Green** | Healthy / Good metric | P/E < 15, ROE > 20% |
| 🟡 **Yellow** | Average / Neutral | P/E 15-25, ROE 10-20% |
| 🔴 **Red** | Poor / Concerning | P/E > 25, ROE < 10% |

---

## 📊 Metrics & Thresholds

### **Valuation Metrics**

**P/E (TTM)** — Price-to-Earnings
- 🟢 < 15 (Cheap)
- 🟡 15-25 (Fair)
- 🔴 > 25 (Expensive)

**P/S Ratio** — Price-to-Sales
- 🟢 < 2.0
- 🟡 2.0-4.0
- 🔴 > 4.0

**P/B** — Price-to-Book
- 🟢 < 1.5 (Below book value)
- 🟡 1.5-3.0 (Fair)
- 🔴 > 3.0 (Expensive)

---

### **Profitability Metrics**

**ROA %** — Return on Assets (Asset efficiency)
- 🟢 > 10% (Excellent)
- 🟡 5-10% (Good)
- 🔴 < 5% (Poor)

**ROE %** — Return on Equity (Shareholder returns)
- 🟢 > 20% (Excellent)
- 🟡 10-20% (Good)
- 🔴 < 10% (Poor)

**Gross Profit Margin %**
- 🟢 > 40% (Strong pricing power)
- 🟡 20-40% (Average)
- 🔴 < 20% (Weak margins)

---

### **Leverage & Solvency**

**Debt/Equity** — Financial leverage
- 🟢 < 1.0 (Conservative)
- 🟡 1.0-2.0 (Moderate)
- 🔴 > 2.0 (High risk)

**Interest Coverage** — Ability to pay interest
- 🟢 > 5x (Very safe)
- 🟡 3-5x (Adequate)
- 🔴 < 3x (At risk)

**Current Ratio** — Liquidity
- 🟢 1.2-2.5 (Healthy)
- 🟡 1.0-1.2 (Adequate)
- 🔴 < 1.0 or > 3.0 (Problem)

---

### **Growth Metrics**

**Revenue Growth YoY %**
- 🟢 > 15% (Strong growth)
- 🟡 5-15% (Modest growth)
- 🔴 < 5% (Sluggish)

**EPS Growth YoY %**
- 🟢 > 20% (Excellent)
- 🟡 10-20% (Good)
- 🔴 < 10% (Weak)

---

### **Technical Indicators**

**RSI14** — Relative Strength Index
- 🟢 < 30 (Oversold = Buying opportunity)
- 🟡 30-70 (Neutral zone)
- 🔴 > 70 (Overbought = Selling pressure)

**MACD Histogram**
- 🟢 > 0 & Rising (Strong bullish momentum)
- 🟡 Near 0 / Flattening (Neutral)
- 🔴 < 0 & Falling (Weak bearish momentum)

---

### **Income Metrics**

**Dividend Yield %**
- 🟢 > 3.5% (Attractive for income)
- 🟡 2.0-3.5% (Moderate)
- 🔴 < 2.0% (Low income)

---

## 🎯 How to Read Your Template

When you open the formatted Excel file:

1. **Scan for green cells** → These stocks/metrics look good
2. **Note yellow cells** → Monitor these metrics
3. **Flag red cells** → Investigate these concerns
4. **Cross-reference metrics** → Look for patterns (e.g., high P/E + low ROE = overvalued)

---

## 📈 Practical Example

| Stock | P/E | ROE | RSI | Assessment |
|-------|-----|-----|-----|------------|
| Stock A | 12 (🟢) | 22% (🟢) | 45 (🟡) | **Strong fundamentals, neutral technicals** |
| Stock B | 28 (🔴) | 18% (🟡) | 72 (🔴) | **Overbought, expensive, watch for pullback** |
| Stock C | 18 (🟡) | 8% (🔴) | 25 (🟢) | **Fair valuation, weak profitability, oversold** |

---

## ⚠️ Important Notes

1. **Context matters** — A P/E of 50 is expensive for retail but normal for tech startups
2. **Industry variations** — Pharma may have lower ROE than IT; this is normal
3. **Trend > Snapshot** — Look at 3-year trends, not just current quarters
4. **No single metric decides** — Use all metrics together for conviction

---

## 🔗 Related Files

- `SECTOR_MEDIAN_ANALYSIS.md` — Why sector benchmarking is blank
- `CONDITIONAL_FORMATTING_GUIDE.md` — Detailed setup instructions
- `conditional_format_rules.csv` — Rule definitions in CSV format

