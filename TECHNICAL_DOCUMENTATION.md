# Stock Analysis Dashboard - Technical Documentation

## Project Overview

A comprehensive equity analysis platform built with Next.js frontend and Python backend, using Supabase (PostgreSQL) as the database. The system provides daily, weekly, monthly analysis and seasonality patterns for Indian equities.

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

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Data processing pipeline |
| Pandas | 2+ | Data manipulation |
| NumPy | 1.2+ | Numerical computations |
| yFinance | - | Market data source |

### Database
| Technology | Purpose |
|------------|---------|
| Supabase | Managed PostgreSQL with REST API |
| PostgreSQL | Relational database |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Vercel | Frontend hosting |
| GitHub | Version control |

---

## Project Structure

```
Stock_Analysis_Python/
├── dashboard/                    # Next.js Frontend Application
│   ├── src/
│   │   ├── app/                 # App Router pages and API routes
│   │   │   ├── page.tsx         # Main dashboard page
│   │   │   ├── layout.tsx       # Root layout
│   │   │   └── api/             # API route handlers
│   │   │       ├── stocks/      # Daily stocks API
│   │   │       ├── weekly/      # Weekly analysis API
│   │   │       ├── monthly/     # Monthly analysis API
│   │   │       └── seasonality/ # Seasonality data API
│   │   ├── components/          # React components
│   │   ├── context/             # React context providers
│   │   └── lib/                 # Utilities and constants
│   └── public/                  # Static assets
│
├── equity_engine/               # Python Analysis Engine
│   ├── scoring.py              # Scoring algorithms
│   ├── pipeline.py             # Main data pipeline
│   ├── technical.py            # Technical indicators
│   ├── indicators.py           # Additional indicators
│   ├── monthly_analysis.py     # Monthly aggregation
│   ├── weekly_analysis.py      # Weekly aggregation
│   └── config.py               # Configuration
│
├── pipeline/                    # Data Pipeline Scripts
│   ├── daily_to_supabase.py    # Daily data upload
│   ├── weekly_to_supabase.py   # Weekly data upload
│   ├── monthly_to_supabase.py  # Monthly data upload
│   └── tests/                  # Pipeline tests
│
├── supabase/                    # Database Migrations
│   └── migrations/
│       └── 001_initial_schema.sql
│
└── tools/                       # Utility scripts
```

---

## Database Schema

### 1. daily_stocks
Primary table containing daily stock analysis data with 110+ fields.

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

**Note:** The following fields are currently NULL in the database and require pipeline updates:
- `positive_months_12m`
- `avg_monthly_return_12m`
- `best_month_return_12m`
- `worst_month_return_12m`

### 4. seasonality
Historical monthly return patterns by ticker.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Auto-increment ID |
| ticker | VARCHAR(20) | Stock symbol |
| company_name | VARCHAR(255) | Company name |
| jan_avg | DECIMAL | January average return % |
| feb_avg | DECIMAL | February average return % |
| mar_avg | DECIMAL | March average return % |
| apr_avg | DECIMAL | April average return % |
| may_avg | DECIMAL | May average return % |
| jun_avg | DECIMAL | June average return % |
| jul_avg | DECIMAL | July average return % |
| aug_avg | DECIMAL | August average return % |
| sep_avg | DECIMAL | September average return % |
| oct_avg | DECIMAL | October average return % |
| nov_avg | DECIMAL | November average return % |
| dec_avg | DECIMAL | December average return % |
| best_month | VARCHAR(20) | Best performing month |
| worst_month | VARCHAR(20) | Worst performing month |

---

## Frontend Components

### Page Components

#### [page.tsx](dashboard/src/app/page.tsx)
Main dashboard page with the following features:
- Tab navigation (Daily, Weekly, Monthly, Seasonality)
- Table view with sorting, filtering, search
- Detail view with charts when a stock is selected
- Tab-specific column picker

### Table Components

#### [StockTable.tsx](dashboard/src/components/StockTable.tsx)
Daily stocks data table with:
- Sortable columns
- Search functionality
- Score-based coloring

#### [WeeklyReportTableV2.tsx](dashboard/src/components/WeeklyReportTableV2.tsx)
Weekly analysis table with:
- Momentum ranking system
- Trend filtering (UP/DOWN/SIDEWAYS)
- RSI zone filtering (Oversold/Neutral/Overbought)
- Return range filters

#### [MonthlyReportTableV2.tsx](dashboard/src/components/MonthlyReportTableV2.tsx)
Monthly analysis table with:
- Monthly momentum ranking
- Return-based filtering
- Trend visualization

#### [SeasonalityHeatmapV2.tsx](dashboard/src/components/SeasonalityHeatmapV2.tsx)
Seasonality heatmap with:
- Color-coded monthly returns
- Best/worst month highlighting
- Quarterly aggregation

### Chart Components

#### [Charts.tsx](dashboard/src/components/Charts.tsx)
Daily chart components:
- `PriceChart` - Candlestick with SMA overlays
- `RSIChart` - RSI with overbought/oversold zones
- `MACDChart` - MACD with signal line
- `ScoreBarChart` - Score breakdown visualization

#### [WeeklyCharts.tsx](dashboard/src/components/WeeklyCharts.tsx)
Weekly chart components:
- `WeeklyPriceChart` - Weekly OHLC with SMA10/20
- `WeeklyRSIChart` - Weekly RSI indicator
- `WeeklyReturnsChart` - 4W/13W returns comparison
- `WeeklyVolumeChart` - Volume with ratio indicator
- `WeeklyStats` - Summary statistics card

#### [MonthlyCharts.tsx](dashboard/src/components/MonthlyCharts.tsx)
Monthly chart components:
- `MonthlyPriceChart` - Monthly OHLC with SMA3/6/12
- `MonthlyReturnsChart` - Monthly return bars
- `RollingReturnsChart` - 3M/6M/12M rolling returns
- `MonthlyVolumeChart` - Monthly volume bars
- `MonthlyStats` - 24-month summary statistics

#### [SeasonalityCharts.tsx](dashboard/src/components/SeasonalityCharts.tsx)
Seasonality visualization:
- `SeasonalityBarChart` - Monthly average returns
- `SeasonalityRadarChart` - Polar area chart
- `QuarterlyBreakdown` - Quarterly aggregation
- `SeasonalityStats` - Pattern analysis

### API Routes

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

---

## Ranking Methodology

### 1. Overall Score (Backend - Daily)

The overall score is a weighted composite of five sub-scores:

```
Overall Score = (wF × Fundamental) + (wT × Technical) + (wS × Sentiment) + (wM × Macro) + (wR × Risk)
```

**Default Weights:**
| Component | Weight | Description |
|-----------|--------|-------------|
| Fundamental | 40% | Financial health metrics |
| Technical | 25% | Price momentum & trends |
| Sentiment | 15% | Analyst & news sentiment |
| Macro | 10% | Economic environment |
| Risk | 10% | Volatility & safety |

#### Fundamental Score Components
| Metric | Direction | Weight |
|--------|-----------|--------|
| ROE TTM % | Higher is better | Equal |
| ROA % | Higher is better | Equal |
| Net Profit Margin % | Higher is better | Equal |
| Gross Profit Margin % | Higher is better | Equal |
| Operating Profit Margin % | Higher is better | Equal |
| EPS Growth YoY % | Higher is better | Equal |
| Revenue Growth YoY % | Higher is better | Equal |
| Dividend Yield % | Higher is better | Equal |
| FCF Yield % | Higher is better | Equal |
| Interest Coverage | Higher is better | Equal |
| Altman Z-Score | Higher is better | Equal |
| Piotroski F-Score | Higher is better | Equal |
| P/E (TTM) | Lower is better | Equal |
| P/B | Lower is better | Equal |
| P/S Ratio | Lower is better | Equal |
| Debt/Equity | Lower is better | Equal |
| PEG Ratio | Lower is better | Equal |

#### Technical Score Components
| Metric | Direction | Weight |
|--------|-----------|--------|
| Return 21d % | Higher is better | Equal |
| Return 63d % | Higher is better | Equal |
| Return 126d % | Higher is better | Equal |
| Return 252d % | Higher is better | Equal |
| Price > SMA50 | Binary bonus | +100 if true |
| Price > SMA200 | Binary bonus | +100 if true |
| ADX14 | Higher is better | Equal |

#### Risk Score Components (Inverted - Lower Risk = Higher Score)
| Metric | Direction | Weight |
|--------|-----------|--------|
| Volatility 90D % | Lower is better | Equal |
| Volatility 30D % | Lower is better | Equal |
| Max Drawdown 1Y % | Lower is better | Equal |
| Debt/Equity | Lower is better | Equal |
| Beta 1Y | Lower is better | Equal |
| Sharpe 1Y | Higher is better | Equal |
| Sortino 1Y | Higher is better | Equal |

### 2. Momentum Rank (Frontend - Weekly)

The weekly momentum rank is calculated client-side using:

```
Momentum Score = (0.30 × 4W Return) + (0.40 × 13W Return) + (0.20 × RSI Adjustment) + (0.10 × Volume Bonus)
```

**RSI Adjustment:**
| RSI Range | Score |
|-----------|-------|
| 40-60 (Optimal) | +10 |
| 60-70 (Slightly Overbought) | +5 |
| 30-40 (Slightly Oversold) | +5 |
| >70 (Overbought) | -5 |
| <30 (Deeply Oversold) | 0 |

**Volume Bonus:**
| Volume Ratio | Score |
|--------------|-------|
| >1.2 (High volume) | +5 |
| 1.0-1.2 (Normal+) | +2 |
| <1.0 (Low volume) | 0 |

### 3. Monthly Momentum Rank (Frontend - Monthly)

Similar to weekly but uses:
- Monthly return (30% weight)
- 3-month return (40% weight)
- 6-month return (20% weight)
- 12-month return (10% weight)

### 4. Seasonality Analysis

Based on historical monthly return averages:
- Calculates average return for each month over available history
- Identifies best and worst performing months
- Groups into quarterly patterns

---

## Data Flow

### Daily Pipeline
```
yFinance API → Python Pipeline → Calculate Indicators → Score Stocks → Supabase
```

### Weekly Aggregation
```
daily_stocks → Aggregate by Week → Calculate Weekly Metrics → weekly_analysis
```

### Monthly Aggregation
```
daily_stocks → Aggregate by Month → Calculate Monthly Metrics → monthly_analysis
```

### Seasonality Calculation
```
monthly_analysis → Group by Month of Year → Calculate Averages → seasonality
```

---

## Authentication

- **Provider:** Google OAuth via Supabase Auth
- **Session Management:** JWT tokens stored in cookies
- **Protected Routes:** All API routes require authentication

---

## Environment Variables

### Frontend (Vercel)
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Backend (Python)
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Known Issues & Data Quality

### NULL Fields in monthly_analysis
The following fields are NULL for all records and require pipeline updates:
1. `positive_months_12m` - Count of positive months in last 12
2. `avg_monthly_return_12m` - Average monthly return over 12 months
3. `best_month_return_12m` - Best month return in 12 months
4. `worst_month_return_12m` - Worst month return in 12 months

### YTD Return
The `ytd_return_pct` field shows 0.00% for January records, which is technically correct (no YTD return in first month of year).

---

## Performance Considerations

1. **API Pagination:** Use `limit` parameter to control response size
2. **Client-side Ranking:** Momentum ranking is calculated client-side to allow real-time filtering
3. **Lazy Loading:** Monthly/Weekly/Seasonality data fetched only when tab is selected
4. **Chart Data:** Historical data fetched on-demand when detail view is opened

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| Jan 2025 | 2.0 | Added V2 table components with ranking |
| Jan 2025 | 2.1 | Added tab-specific charts (Weekly/Monthly/Seasonality) |
| Jan 2025 | 2.2 | Added tab-specific column pickers |

---

*Last Updated: January 2025*
