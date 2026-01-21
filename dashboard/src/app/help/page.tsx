'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ChevronLeft, ChevronDown, ChevronRight, BarChart3, TrendingUp, Calendar, Activity, Brain, FileJson, Download, HelpCircle, Info, Table, Layers, LineChart } from 'lucide-react';

export default function HelpPage() {
    return (
        <div className="min-h-screen bg-[#05080f] text-slate-100 p-6">
            <div className="max-w-5xl mx-auto">
                {/* Header */}
                <div className="flex items-center gap-4 mb-6">
                    <Link href="/" className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
                        <ChevronLeft className="w-5 h-5 text-slate-400" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                            <HelpCircle className="w-7 h-7 text-blue-500" />
                            Help & Documentation
                        </h1>
                        <p className="text-slate-400 text-sm">Complete field reference for Antigravity Terminal</p>
                    </div>
                </div>

                <div className="space-y-3">
                    {/* Overview */}
                    <CollapsibleSection title="Overview" icon={<Info className="w-5 h-5" />} defaultOpen>
                        <p className="text-slate-300 text-sm mb-3">
                            The <strong>Antigravity Terminal</strong> provides comprehensive stock analysis for NIFTY 200 stocks
                            with AI-powered insights. Use the tabs to switch between Daily, Weekly, Monthly, and Seasonality views.
                        </p>
                        <div className="grid grid-cols-4 gap-2 text-xs">
                            <div className="bg-slate-800/50 p-2 rounded border border-slate-700">
                                <div className="text-blue-400 font-medium">113 Fields</div>
                                <div className="text-slate-500">Daily Screener</div>
                            </div>
                            <div className="bg-slate-800/50 p-2 rounded border border-slate-700">
                                <div className="text-cyan-400 font-medium">17 Fields</div>
                                <div className="text-slate-500">Weekly Report</div>
                            </div>
                            <div className="bg-slate-800/50 p-2 rounded border border-slate-700">
                                <div className="text-purple-400 font-medium">18 Fields</div>
                                <div className="text-slate-500">Monthly Report</div>
                            </div>
                            <div className="bg-slate-800/50 p-2 rounded border border-slate-700">
                                <div className="text-amber-400 font-medium">16 Fields</div>
                                <div className="text-slate-500">Seasonality</div>
                            </div>
                        </div>
                    </CollapsibleSection>

                    {/* DAILY SCREENER - ALL FIELDS */}
                    <CollapsibleSection title="Daily Screener Fields (113)" icon={<Table className="w-5 h-5" />}>
                        <div className="space-y-4 text-sm">
                            {/* Basic */}
                            <FieldGroup title="Basic Metadata (7)">
                                <Field name="ticker" desc="Stock symbol (e.g., RELIANCE, TCS)" />
                                <Field name="company_name" desc="Full company name" />
                                <Field name="isin" desc="International Securities ID Number" />
                                <Field name="exchange" desc="Exchange (NSE/BSE)" />
                                <Field name="sector" desc="Industry sector classification" />
                                <Field name="industry" desc="Specific industry within sector" />
                                <Field name="currency" desc="Trading currency (INR)" />
                            </FieldGroup>

                            {/* Price & Returns */}
                            <FieldGroup title="Price & Returns (10)">
                                <Field name="price_last" desc="Latest closing price" />
                                <Field name="high_52w" desc="52-week high price" />
                                <Field name="low_52w" desc="52-week low price" />
                                <Field name="return_1d" desc="1-day return %" />
                                <Field name="return_1w" desc="1-week return %" />
                                <Field name="return_1m" desc="1-month return %" />
                                <Field name="return_3m" desc="3-month return %" />
                                <Field name="return_6m" desc="6-month return %" />
                                <Field name="return_1y" desc="1-year return %" />
                                <Field name="cagr_3y_pct" desc="3-year compound annual growth rate" />
                                <Field name="cagr_5y_pct" desc="5-year compound annual growth rate" />
                            </FieldGroup>

                            {/* Fundamental - Size & Value */}
                            <FieldGroup title="Fundamental - Size & Valuation (10)">
                                <Field name="market_cap_cr" desc="Market capitalization in Crores" />
                                <Field name="enterprise_value_cr" desc="Enterprise value (MCap + Debt - Cash)" />
                                <Field name="shares_outstanding" desc="Total shares issued" />
                                <Field name="free_float_pct" desc="% of shares available for trading" />
                                <Field name="pe_ttm" desc="Price/Earnings (Trailing 12M). Lower = potentially undervalued" />
                                <Field name="pb" desc="Price/Book. < 1 = trading below book value" />
                                <Field name="ps_ratio" desc="Price/Sales ratio" />
                                <Field name="ev_ebitda_ttm" desc="EV/EBITDA. Lower = potentially undervalued" />
                                <Field name="peg_ratio" desc="PE/Growth. < 1 = growth at reasonable price" />
                                <Field name="dividend_yield_pct" desc="Annual dividend as % of price" />
                            </FieldGroup>

                            {/* Fundamental - Performance */}
                            <FieldGroup title="Fundamental - Performance & Health (13)">
                                <Field name="revenue_ttm_cr" desc="Revenue (Trailing 12M) in Crores" />
                                <Field name="ebitda_ttm_cr" desc="EBITDA (Trailing 12M) in Crores" />
                                <Field name="net_income_ttm_cr" desc="Net Income (Trailing 12M) in Crores" />
                                <Field name="eps_ttm" desc="Earnings Per Share (Trailing 12M)" />
                                <Field name="roe_ttm" desc="Return on Equity %. > 15% = good" />
                                <Field name="roa_pct" desc="Return on Assets %" />
                                <Field name="debt_equity" desc="Debt/Equity ratio. < 1 = conservative" />
                                <Field name="interest_coverage" desc="EBIT/Interest. > 3 = safe" />
                                <Field name="revenue_growth_yoy_pct" desc="Year-over-year revenue growth %" />
                                <Field name="eps_growth_yoy_pct" desc="Year-over-year EPS growth %" />
                                <Field name="gross_profit_margin_pct" desc="Gross profit margin %" />
                                <Field name="operating_profit_margin_pct" desc="Operating profit margin %" />
                                <Field name="net_profit_margin_pct" desc="Net profit margin %" />
                            </FieldGroup>

                            {/* Cash Flow */}
                            <FieldGroup title="Cash Flow (4)">
                                <Field name="ocf_ttm_cr" desc="Operating Cash Flow (Trailing 12M)" />
                                <Field name="capex_ttm_cr" desc="Capital Expenditure (Trailing 12M)" />
                                <Field name="fcf_ttm_cr" desc="Free Cash Flow = OCF - CapEx" />
                                <Field name="fcf_yield_pct" desc="FCF / Market Cap %" />
                            </FieldGroup>

                            {/* Technical Indicators */}
                            <FieldGroup title="Technical Indicators (19)">
                                <Field name="sma20" desc="20-day Simple Moving Average" />
                                <Field name="sma50" desc="50-day SMA. Price > SMA50 = bullish" />
                                <Field name="sma200" desc="200-day SMA. Golden cross = SMA50 > SMA200" />
                                <Field name="rsi14" desc="RSI(14). > 70 = overbought, < 30 = oversold" />
                                <Field name="macd_line" desc="MACD line value" />
                                <Field name="macd_signal" desc="MACD signal line" />
                                <Field name="macd_hist" desc="MACD histogram (line - signal)" />
                                <Field name="adx14" desc="ADX(14). > 25 = trending, < 20 = ranging" />
                                <Field name="atr14" desc="Average True Range. Volatility measure" />
                                <Field name="bb_upper" desc="Bollinger Band upper (2 std dev)" />
                                <Field name="bb_lower" desc="Bollinger Band lower (2 std dev)" />
                                <Field name="aroon_up" desc="Aroon Up (0-100). > 70 = uptrend" />
                                <Field name="aroon_down" desc="Aroon Down (0-100). > 70 = downtrend" />
                                <Field name="stoch_k" desc="Stochastic %K (fast)" />
                                <Field name="stoch_d" desc="Stochastic %D (slow signal)" />
                                <Field name="obv" desc="On-Balance Volume for trend confirmation" />
                                <Field name="avg_volume_1w" desc="Average volume last week" />
                                <Field name="volume_vs_3m_avg_pct" desc="Current volume vs 3M average %" />
                                <Field name="avg_daily_turnover_3m_cr" desc="Avg daily turnover in Crores" />
                            </FieldGroup>

                            {/* Scores */}
                            <FieldGroup title="Scores (7)">
                                <Field name="overall_score" desc="Composite score (0-100) combining all factors" />
                                <Field name="score_fundamental" desc="Fundamental health score (0-100)" />
                                <Field name="score_technical" desc="Technical strength score (0-100)" />
                                <Field name="score_risk" desc="Risk score. Lower = less risky" />
                                <Field name="score_sentiment" desc="Market sentiment score (0-100)" />
                                <Field name="score_macro" desc="Macro environment score (0-100)" />
                                <Field name="macro_composite" desc="Combined macro indicator" />
                            </FieldGroup>

                            {/* Sentiment */}
                            <FieldGroup title="Analyst & Sentiment (7)">
                                <Field name="recommendation" desc="Consensus: Strong Buy/Buy/Hold/Sell" />
                                <Field name="consensus_rating" desc="Average analyst rating (1-5)" />
                                <Field name="target_price" desc="Analyst consensus target price" />
                                <Field name="upside_pct" desc="Potential upside to target %" />
                                <Field name="num_analysts" desc="Number of covering analysts" />
                                <Field name="news_sentiment_score" desc="News sentiment (-1 to +1)" />
                                <Field name="social_sentiment" desc="Social media sentiment score" />
                            </FieldGroup>

                            {/* Analysis */}
                            <FieldGroup title="Deep Analysis & Quality (8)">
                                <Field name="quality_score" desc="Earnings quality & consistency (0-100)" />
                                <Field name="momentum_score" desc="Price momentum strength (0-100)" />
                                <Field name="alpha_1y_pct" desc="1-year alpha vs benchmark %" />
                                <Field name="sortino_1y" desc="Sortino ratio (downside risk-adjusted)" />
                                <Field name="economic_moat_score" desc="Competitive advantage score" />
                                <Field name="altman_z" desc="Altman Z-Score. > 3 = safe, < 1.8 = distress" />
                                <Field name="piotroski_f" desc="Piotroski F-Score (0-9). > 7 = strong" />
                                <Field name="esg_score" desc="Environmental/Social/Governance score" />
                            </FieldGroup>

                            {/* Deep Dive */}
                            <FieldGroup title="Qualitative Notes (4)">
                                <Field name="moat_notes" desc="Competitive advantage analysis" />
                                <Field name="risk_notes" desc="Key risk factors identified" />
                                <Field name="catalysts" desc="Upcoming potential catalysts" />
                                <Field name="sector_notes" desc="Sector-specific observations" />
                            </FieldGroup>
                        </div>
                    </CollapsibleSection>

                    {/* WEEKLY FIELDS */}
                    <CollapsibleSection title="Weekly Report Fields (17)" icon={<Calendar className="w-5 h-5" />}>
                        <div className="space-y-4 text-sm">
                            <FieldGroup title="Basic (3)">
                                <Field name="ticker" desc="Stock symbol" />
                                <Field name="company_name" desc="Company name" />
                                <Field name="week_ending" desc="Week ending date" />
                            </FieldGroup>
                            <FieldGroup title="Price (4)">
                                <Field name="weekly_open" desc="Opening price of the week" />
                                <Field name="weekly_high" desc="Highest price during week" />
                                <Field name="weekly_low" desc="Lowest price during week" />
                                <Field name="weekly_close" desc="Closing price of the week" />
                            </FieldGroup>
                            <FieldGroup title="Returns (3)">
                                <Field name="weekly_return_pct" desc="This week's return %" />
                                <Field name="return_4w" desc="4-week rolling return %" />
                                <Field name="return_13w" desc="13-week (quarterly) return %" />
                            </FieldGroup>
                            <FieldGroup title="Volume (2)">
                                <Field name="weekly_volume" desc="Total volume for the week" />
                                <Field name="weekly_volume_ratio" desc="Volume vs 4-week average" />
                            </FieldGroup>
                            <FieldGroup title="Technical (5)">
                                <Field name="weekly_rsi14" desc="Weekly RSI(14)" />
                                <Field name="weekly_sma10" desc="10-week SMA" />
                                <Field name="weekly_sma20" desc="20-week SMA" />
                                <Field name="weekly_trend" desc="UP/DOWN/NEUTRAL based on price action" />
                            </FieldGroup>
                        </div>
                    </CollapsibleSection>

                    {/* MONTHLY FIELDS */}
                    <CollapsibleSection title="Monthly Report Fields (18)" icon={<BarChart3 className="w-5 h-5" />}>
                        <div className="space-y-4 text-sm">
                            <FieldGroup title="Basic (3)">
                                <Field name="ticker" desc="Stock symbol" />
                                <Field name="company_name" desc="Company name" />
                                <Field name="month" desc="Month (YYYY-MM format)" />
                            </FieldGroup>
                            <FieldGroup title="Price (4)">
                                <Field name="monthly_open" desc="Opening price of month" />
                                <Field name="monthly_high" desc="Highest price during month" />
                                <Field name="monthly_low" desc="Lowest price during month" />
                                <Field name="monthly_close" desc="Closing price of month" />
                            </FieldGroup>
                            <FieldGroup title="Returns (5)">
                                <Field name="monthly_return_pct" desc="This month's return %" />
                                <Field name="return_3m" desc="3-month rolling return %" />
                                <Field name="return_6m" desc="6-month rolling return %" />
                                <Field name="return_12m" desc="12-month rolling return %" />
                                <Field name="ytd_return_pct" desc="Year-to-date return %" />
                            </FieldGroup>
                            <FieldGroup title="Volume & Technical (5)">
                                <Field name="monthly_volume" desc="Total volume for month" />
                                <Field name="monthly_sma3" desc="3-month SMA" />
                                <Field name="monthly_sma6" desc="6-month SMA" />
                                <Field name="monthly_sma12" desc="12-month SMA" />
                                <Field name="monthly_trend" desc="Long-term trend direction" />
                            </FieldGroup>
                        </div>
                    </CollapsibleSection>

                    {/* SEASONALITY FIELDS */}
                    <CollapsibleSection title="Seasonality Fields (16)" icon={<Layers className="w-5 h-5" />}>
                        <div className="space-y-4 text-sm">
                            <FieldGroup title="Basic (2)">
                                <Field name="ticker" desc="Stock symbol" />
                                <Field name="company_name" desc="Company name" />
                            </FieldGroup>
                            <FieldGroup title="Monthly Averages - Q1 (3)">
                                <Field name="jan_avg" desc="January historical avg return %" />
                                <Field name="feb_avg" desc="February historical avg return %" />
                                <Field name="mar_avg" desc="March historical avg return %" />
                            </FieldGroup>
                            <FieldGroup title="Monthly Averages - Q2 (3)">
                                <Field name="apr_avg" desc="April historical avg return %" />
                                <Field name="may_avg" desc="May historical avg return %" />
                                <Field name="jun_avg" desc="June historical avg return %" />
                            </FieldGroup>
                            <FieldGroup title="Monthly Averages - Q3 (3)">
                                <Field name="jul_avg" desc="July historical avg return %" />
                                <Field name="aug_avg" desc="August historical avg return %" />
                                <Field name="sep_avg" desc="September historical avg return %" />
                            </FieldGroup>
                            <FieldGroup title="Monthly Averages - Q4 (3)">
                                <Field name="oct_avg" desc="October historical avg return %" />
                                <Field name="nov_avg" desc="November historical avg return %" />
                                <Field name="dec_avg" desc="December historical avg return %" />
                            </FieldGroup>
                            <FieldGroup title="Summary (2)">
                                <Field name="best_month" desc="Best performing month historically" />
                                <Field name="worst_month" desc="Worst performing month historically" />
                            </FieldGroup>
                        </div>
                    </CollapsibleSection>

                    {/* CHARTS */}
                    <CollapsibleSection title="Chart Components (6)" icon={<LineChart className="w-5 h-5" />}>
                        <div className="space-y-4 text-sm">
                            <FieldGroup title="Daily Charts">
                                <Field name="Price Chart" desc="Candlestick/line chart with SMA 20/50/200 overlays" />
                                <Field name="RSI Chart" desc="RSI(14) with overbought (70) and oversold (30) zones" />
                                <Field name="MACD Chart" desc="MACD line, signal line, and histogram" />
                                <Field name="Score Bar" desc="Bar chart comparing fundamental, technical, risk scores" />
                            </FieldGroup>
                            <FieldGroup title="Weekly/Monthly Charts">
                                <Field name="Volume Chart" desc="Volume bars with average line overlay" />
                                <Field name="Returns Chart" desc="Period returns bar chart with color coding" />
                            </FieldGroup>
                            <FieldGroup title="Seasonality Charts">
                                <Field name="Seasonality Heatmap" desc="12-month grid colored by avg return" />
                                <Field name="Radar Chart" desc="Quarterly performance radar visualization" />
                            </FieldGroup>
                        </div>
                    </CollapsibleSection>

                    {/* AI ANALYSIS */}
                    <CollapsibleSection title="AI Agent Analysis" icon={<Brain className="w-5 h-5" />}>
                        <div className="space-y-4 text-sm">
                            <p className="text-slate-300">
                                Click <span className="px-1.5 py-0.5 bg-gradient-to-r from-blue-600 to-purple-600 rounded text-xs">Analyze</span> on any stock.
                                Click agent cards to expand detailed analysis with reasoning.
                            </p>
                            <FieldGroup title="5 Specialist Agents">
                                <Field name="📈 Fundamental" desc="PE, PB, ROE, debt, profitability → fundamental_score" />
                                <Field name="📉 Technical" desc="RSI, MACD, SMA, patterns → technical_score" />
                                <Field name="📰 Sentiment" desc="News, social buzz, events → sentiment_score" />
                                <Field name="🌍 Macro" desc="VIX, RBI, sector trends → macro_score" />
                                <Field name="⚖️ Regulatory" desc="SEBI, governance, compliance → regulatory_score" />
                            </FieldGroup>
                            <FieldGroup title="Synthesis Output">
                                <Field name="Recommendation" desc="BUY/HOLD/SELL synthesized from all agents" />
                                <Field name="Composite Score" desc="Weighted average of agent scores (0-100)" />
                                <Field name="Target Price" desc="AI-estimated fair value" />
                                <Field name="Confidence" desc="HIGH/MEDIUM/LOW based on data quality" />
                            </FieldGroup>
                            <FieldGroup title="Export Options">
                                <Field name="JSON" desc="Full structured data for programmatic use" />
                                <Field name="PDF" desc="Printable report with all analysis" />
                            </FieldGroup>
                        </div>
                    </CollapsibleSection>

                    {/* Controls */}
                    <CollapsibleSection title="Controls & Navigation" icon={<Activity className="w-5 h-5" />}>
                        <div className="space-y-2 text-sm">
                            <Field name="Report Tabs" desc="Switch: Daily | Weekly | Monthly | Seasonality" />
                            <Field name="Date Selector" desc="Pick analysis date (Daily view)" />
                            <Field name="Search" desc="Filter by ticker or company name" />
                            <Field name="Column Picker (⚙️)" desc="Show/hide columns in table" />
                            <Field name="Timeframe Toggle" desc="1D/1W/1M return period" />
                            <Field name="View Toggle" desc="Grid (table) or Detail (charts)" />
                            <Field name="Help (❓)" desc="Opens this documentation" />
                        </div>
                    </CollapsibleSection>

                    {/* Back */}
                    <div className="pt-4">
                        <Link href="/" className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white text-sm font-medium transition-colors">
                            <ChevronLeft className="w-4 h-4" /> Back to Dashboard
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Collapsible Section
function CollapsibleSection({ title, icon, children, defaultOpen = false }: { title: string; icon: React.ReactNode; children: React.ReactNode; defaultOpen?: boolean }) {
    const [isOpen, setIsOpen] = useState(defaultOpen);
    return (
        <section className="bg-slate-900/50 border border-slate-800 rounded-lg overflow-hidden">
            <button onClick={() => setIsOpen(!isOpen)} className="w-full flex items-center justify-between p-3 hover:bg-slate-800/50 transition-colors">
                <div className="flex items-center gap-2">
                    <span className="text-blue-500">{icon}</span>
                    <span className="font-medium text-white text-sm">{title}</span>
                </div>
                {isOpen ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
            </button>
            {isOpen && <div className="px-4 pb-4">{children}</div>}
        </section>
    );
}

// Field Group
function FieldGroup({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <div>
            <h4 className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1.5 pb-1 border-b border-slate-700/50">{title}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-1">{children}</div>
        </div>
    );
}

// Field
function Field({ name, desc }: { name: string; desc: string }) {
    return (
        <div className="flex gap-2 text-xs py-0.5">
            <code className="font-mono text-blue-400 min-w-24 shrink-0">{name}</code>
            <span className="text-slate-500">{desc}</span>
        </div>
    );
}
