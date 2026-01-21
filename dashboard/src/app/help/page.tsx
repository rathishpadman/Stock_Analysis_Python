'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ChevronLeft, ChevronDown, ChevronRight, BarChart3, TrendingUp, Calendar, Activity, Brain, FileJson, Download, HelpCircle, Info, Table, Layers } from 'lucide-react';

export default function HelpPage() {
    return (
        <div className="min-h-screen bg-[#05080f] text-slate-100 p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/" className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
                        <ChevronLeft className="w-5 h-5 text-slate-400" />
                    </Link>
                    <div>
                        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                            <HelpCircle className="w-8 h-8 text-blue-500" />
                            Help & Documentation
                        </h1>
                        <p className="text-slate-400 mt-1">Complete guide to the Antigravity Terminal</p>
                    </div>
                </div>

                <div className="space-y-4">
                    {/* Overview Section */}
                    <CollapsibleSection title="Overview" icon={<Info className="w-5 h-5" />} defaultOpen>
                        <p className="text-slate-300 leading-relaxed mb-4">
                            The <strong>Antigravity Terminal</strong> is a professional-grade stock analysis dashboard
                            that provides comprehensive insights into NIFTY 200 stocks. It combines traditional
                            quantitative metrics with AI-powered multi-agent analysis.
                        </p>
                        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                            <h4 className="font-medium text-white mb-2">Quick Navigation</h4>
                            <ul className="text-sm text-slate-400 space-y-1">
                                <li>• <strong>Daily Screener</strong>: Real-time scores and signals</li>
                                <li>• <strong>Weekly/Monthly</strong>: Trend analysis and performance</li>
                                <li>• <strong>Seasonality</strong>: Historical monthly patterns</li>
                                <li>• <strong>AI Analysis</strong>: Click "Analyze" button on any stock</li>
                            </ul>
                        </div>
                    </CollapsibleSection>

                    {/* Daily Screener */}
                    <CollapsibleSection title="Daily Screener Fields" icon={<Table className="w-5 h-5" />}>
                        <div className="space-y-4">
                            <FieldGroup title="Score Columns">
                                <Field name="Overall Score" description="Composite score (0-100) combining fundamental, technical, momentum, and quality factors. Higher = better investment opportunity." />
                                <Field name="Fundamental Score" description="Based on PE, PB, ROE, debt levels, and profitability metrics. High score = undervalued with strong fundamentals." />
                                <Field name="Technical Score" description="Derived from RSI, MACD, SMA positions, and trend strength. High score = bullish technical setup." />
                                <Field name="Momentum Score" description="Measures recent price momentum across 1D, 1W, 1M returns. High score = strong upward momentum." />
                                <Field name="Quality Score" description="Evaluates earnings quality, governance, and consistency. High score = reliable quality stock." />
                            </FieldGroup>

                            <FieldGroup title="Price & Return Columns">
                                <Field name="Close" description="Latest closing price from BSE/NSE." />
                                <Field name="Change %" description="Percentage change from previous close." />
                                <Field name="1D/1W/1M Return" description="Returns over 1 day, 1 week, or 1 month. Toggle at top-right of table." />
                                <Field name="52W High/Low" description="Highest and lowest prices in the past 52 weeks." />
                                <Field name="Distance from 52W High" description="How far current price is from 52-week high (negative = below)." />
                            </FieldGroup>

                            <FieldGroup title="Technical Indicators">
                                <Field name="RSI(14)" description="Relative Strength Index (14-day). &gt;70 = overbought, &lt;30 = oversold, 40-60 = neutral." />
                                <Field name="MACD Signal" description="Moving Average Convergence Divergence direction. Bullish = uptrend, Bearish = downtrend." />
                                <Field name="SMA 20/50/200" description="Simple Moving Averages. Price above SMA = bullish, below = bearish. Golden cross (50 &gt; 200) = strong buy." />
                                <Field name="Trend" description="Primary price trend: BULLISH, BEARISH, or SIDEWAYS based on moving average positions." />
                            </FieldGroup>

                            <FieldGroup title="Fundamental Metrics">
                                <Field name="PE Ratio" description="Price to Earnings. Lower = potentially undervalued. Compare to sector average." />
                                <Field name="PB Ratio" description="Price to Book. Lower = potentially undervalued. &lt;1 may indicate deep value." />
                                <Field name="ROE %" description="Return on Equity. Higher = better capital efficiency. &gt;15% is generally good." />
                                <Field name="Debt/Equity" description="Leverage ratio. Lower = less risky. &gt;1 means more debt than equity." />
                                <Field name="Dividend Yield %" description="Annual dividend as % of price. Higher = better income, but check sustainability." />
                                <Field name="Market Cap" description="Company size. Large cap (&gt;₹20K Cr) = stable, Mid cap = growth potential, Small cap = higher risk/reward." />
                            </FieldGroup>
                        </div>
                    </CollapsibleSection>

                    {/* Weekly Report */}
                    <CollapsibleSection title="Weekly Report Fields" icon={<Calendar className="w-5 h-5" />}>
                        <div className="space-y-4">
                            <FieldGroup title="Weekly Metrics">
                                <Field name="Week High/Low" description="Highest and lowest prices during the current week." />
                                <Field name="Weekly Return %" description="Percentage change from last week's close to this week's close." />
                                <Field name="Weekly Trend" description="UP = higher highs/lows, DOWN = lower highs/lows, NEUTRAL = consolidating." />
                                <Field name="Volume Ratio" description="Current week's volume vs 4-week average. &gt;1.5 = high activity, &lt;0.5 = low interest." />
                                <Field name="SMA 10/20" description="Short-term weekly moving averages. Price above both = strong uptrend." />
                                <Field name="Week RSI" description="Weekly RSI for longer-term momentum. Smooths out daily noise." />
                            </FieldGroup>
                        </div>
                    </CollapsibleSection>

                    {/* Monthly Report */}
                    <CollapsibleSection title="Monthly Report Fields" icon={<BarChart3 className="w-5 h-5" />}>
                        <div className="space-y-4">
                            <FieldGroup title="Monthly Metrics">
                                <Field name="Month High/Low" description="Highest and lowest prices during the current month." />
                                <Field name="Monthly Return %" description="Percentage change from last month's close to this month's close." />
                                <Field name="YTD Return %" description="Year-to-date return from January 1st." />
                                <Field name="3M/6M/12M Return" description="Rolling returns over 3, 6, and 12 months. Shows medium-term performance." />
                                <Field name="SMA 3/6/12" description="Monthly moving averages (in months). Price above all three = strong uptrend." />
                                <Field name="Monthly Trend" description="Based on monthly candle patterns and SMA positions." />
                            </FieldGroup>
                        </div>
                    </CollapsibleSection>

                    {/* Seasonality */}
                    <CollapsibleSection title="Seasonality Analysis" icon={<Layers className="w-5 h-5" />}>
                        <div className="space-y-4">
                            <FieldGroup title="Seasonality Metrics">
                                <Field name="Best Month" description="Historically best-performing calendar month based on 5+ years of data." />
                                <Field name="Worst Month" description="Historically worst-performing calendar month." />
                                <Field name="Win Rate %" description="Percentage of years with positive returns for each month. &gt;60% = reliable pattern." />
                                <Field name="Avg Return %" description="Mean monthly return across all years in the dataset." />
                                <Field name="Max Gain/Loss %" description="Best and worst single-month performance in history." />
                                <Field name="Volatility" description="Standard deviation of monthly returns. Higher = more unpredictable." />
                            </FieldGroup>
                            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 text-sm text-blue-300">
                                💡 <strong>Tip</strong>: Use seasonality for timing entries. If a stock historically performs well in March and poorly in October,
                                consider buying in February and reducing exposure in September.
                            </div>
                        </div>
                    </CollapsibleSection>

                    {/* AI Agent Analysis */}
                    <CollapsibleSection title="AI Agent Analysis" icon={<Brain className="w-5 h-5" />} defaultOpen>
                        <p className="text-slate-300 mb-4">
                            Click the <span className="px-2 py-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded text-xs font-medium">Analyze</span> button
                            on any stock to run a comprehensive AI analysis powered by <strong>Google Gemini 2.0 Flash</strong>.
                        </p>

                        <h4 className="font-medium text-white mb-3">The 5 Specialist Agents</h4>
                        <div className="grid grid-cols-1 gap-3 mb-4">
                            <AgentCard
                                emoji="📈"
                                name="Fundamental Agent"
                                score="fundamental_score"
                                description="Analyzes PE ratio, PB ratio, ROE, debt levels, profitability, and growth metrics. Outputs financial health assessment and fair value estimate."
                            />
                            <AgentCard
                                emoji="📉"
                                name="Technical Agent"
                                score="technical_score"
                                description="Evaluates RSI, MACD, moving averages, support/resistance levels, chart patterns. Provides entry/exit price targets and stop-loss levels."
                            />
                            <AgentCard
                                emoji="📰"
                                name="Sentiment Agent"
                                score="sentiment_score"
                                description="Assesses news sentiment from ET/Moneycontrol, social buzz, upcoming events (earnings, dividends), and FII/DII activity."
                            />
                            <AgentCard
                                emoji="🌍"
                                name="Macro Agent"
                                score="macro_score"
                                description="Considers India VIX, RBI policy, INR movements, sector trends, global market conditions. Rates market regime as bullish/bearish/neutral."
                            />
                            <AgentCard
                                emoji="⚖️"
                                name="Regulatory Agent"
                                score="compliance_score"
                                description="Reviews SEBI compliance, corporate governance, promoter holding patterns, past regulatory issues. Flags ESG and governance risks."
                            />
                        </div>

                        <h4 className="font-medium text-white mb-3">Understanding Agent Output</h4>
                        <div className="space-y-2">
                            <Field name="Score (0-100)" description="Each agent outputs a score. &gt;70 = Bullish, 50-70 = Neutral, &lt;50 = Bearish. Click agent card to see detailed reasoning." />
                            <Field name="Signal" description="Quick summary: BUY, HOLD, SELL, BULLISH, BEARISH, etc." />
                            <Field name="Reasoning" description="Click any agent card to expand and see the full analysis text explaining why the score was given." />
                            <Field name="Key Risks" description="Identified risk factors that could impact the stock negatively." />
                            <Field name="Key Catalysts" description="Positive factors that could drive the stock higher." />
                        </div>

                        <h4 className="font-medium text-white mt-4 mb-3">Final Synthesis</h4>
                        <div className="space-y-2">
                            <Field name="Recommendation" description="BUY / HOLD / SELL - synthesized from all 5 agents with appropriate weighting." />
                            <Field name="Composite Score" description="Weighted average of all agent scores (0-100)." />
                            <Field name="Target Price" description="AI-estimated fair value based on fundamental and technical analysis." />
                            <Field name="Confidence Level" description="HIGH / MEDIUM / LOW based on data quality and agent agreement." />
                            <Field name="AI Summary" description="Natural language explanation synthesizing all agent perspectives." />
                        </div>

                        <h4 className="font-medium text-white mt-4 mb-3">Export Options</h4>
                        <div className="flex gap-4">
                            <div className="flex items-center gap-2 text-slate-300">
                                <FileJson className="w-4 h-4 text-blue-400" />
                                <span><strong>JSON</strong>: Full structured data for programmatic use</span>
                            </div>
                            <div className="flex items-center gap-2 text-slate-300">
                                <Download className="w-4 h-4 text-purple-400" />
                                <span><strong>PDF</strong>: Printable report for documentation</span>
                            </div>
                        </div>
                    </CollapsibleSection>

                    {/* Stock Detail View */}
                    <CollapsibleSection title="Stock Detail View (Charts)" icon={<TrendingUp className="w-5 h-5" />}>
                        <p className="text-slate-300 mb-4">
                            Click on any stock in the sidebar to switch to Detail view with interactive charts.
                        </p>
                        <div className="space-y-2">
                            <Field name="Price Chart" description="Historical price with SMA 20/50/200 overlays. Identify support/resistance visually." />
                            <Field name="RSI Chart" description="Momentum indicator with overbought (70) and oversold (30) zones marked." />
                            <Field name="MACD Chart" description="Shows MACD line, signal line, and histogram for trend momentum." />
                            <Field name="Volume Chart" description="Trading volume over time. Spikes indicate significant activity or news." />
                            <Field name="Returns Chart" description="Bar chart showing period-over-period return distribution." />
                            <Field name="Key Metrics Panel" description="All available data fields for the selected stock in one view." />
                        </div>
                    </CollapsibleSection>

                    {/* Controls & Filters */}
                    <CollapsibleSection title="Controls & Navigation" icon={<Activity className="w-5 h-5" />}>
                        <div className="space-y-2">
                            <Field name="Date Selector" description="Choose analysis date (Daily view only). Shows data as of that date." />
                            <Field name="Search" description="Filter stocks by ticker symbol or company name. Instant filter as you type." />
                            <Field name="Column Picker (⚙️)" description="Customize which columns are visible in the table. Your selection persists." />
                            <Field name="Timeframe Toggle (1D/1W/1M)" description="Switch between 1-day, 1-week, and 1-month return periods in the table." />
                            <Field name="View Toggle (Grid/Detail)" description="Switch between table view (all stocks) and chart view (single stock detail)." />
                            <Field name="Report Tabs" description="Switch between Daily, Weekly, Monthly, and Seasonality views." />
                            <Field name="Help Icon (❓)" description="Opens this help page." />
                            <Field name="Logout (🚪)" description="Sign out of the application." />
                        </div>
                    </CollapsibleSection>

                    {/* Caching */}
                    <CollapsibleSection title="Caching & Performance" icon={<Activity className="w-5 h-5" />}>
                        <div className="space-y-2">
                            <Field name="Cache Duration" description="AI analysis results are cached for 24 hours to improve performance and reduce API costs." />
                            <Field name="Cache Indicator" description="Shows 'Cached (Xm ago)' when using cached results. Fresh analysis runs when cache expires." />
                            <Field name="Cost Display" description="Shows token usage and estimated cost per analysis (~$0.01-0.03 per analysis)." />
                        </div>
                        <div className="mt-3 bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 text-sm text-amber-300">
                            ⚠️ <strong>Note</strong>: To force a fresh analysis before cache expires, use the API to clear cache manually:
                            <code className="block mt-1 text-xs bg-slate-900 p-2 rounded">DELETE /api/agent/cache/TICKER</code>
                        </div>
                    </CollapsibleSection>

                    {/* Back to Dashboard */}
                    <div className="pt-8 border-t border-slate-800">
                        <Link
                            href="/"
                            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-medium transition-colors"
                        >
                            <ChevronLeft className="w-4 h-4" />
                            Back to Dashboard
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Collapsible Section Component
function CollapsibleSection({
    title,
    icon,
    children,
    defaultOpen = false
}: {
    title: string;
    icon: React.ReactNode;
    children: React.ReactNode;
    defaultOpen?: boolean;
}) {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    return (
        <section className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-4 hover:bg-slate-800/50 transition-colors"
            >
                <div className="flex items-center gap-3">
                    <span className="text-blue-500">{icon}</span>
                    <span className="text-lg font-semibold text-white">{title}</span>
                </div>
                {isOpen ? (
                    <ChevronDown className="w-5 h-5 text-slate-400" />
                ) : (
                    <ChevronRight className="w-5 h-5 text-slate-400" />
                )}
            </button>
            {isOpen && (
                <div className="px-6 pb-6 animate-in slide-in-from-top-2 duration-200">
                    {children}
                </div>
            )}
        </section>
    );
}

// Field Group Component
function FieldGroup({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <div>
            <h4 className="text-sm font-medium text-slate-300 uppercase tracking-wide mb-2 pb-1 border-b border-slate-700">
                {title}
            </h4>
            <div className="space-y-2">
                {children}
            </div>
        </div>
    );
}

// Field Component
function Field({ name, description }: { name: string; description: string }) {
    return (
        <div className="flex gap-2 text-sm">
            <span className="font-medium text-blue-400 min-w-32 shrink-0">{name}:</span>
            <span className="text-slate-400">{description}</span>
        </div>
    );
}

// Agent Card Component
function AgentCard({ emoji, name, score, description }: { emoji: string; name: string; score: string; description: string }) {
    return (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <div className="flex items-start gap-3">
                <span className="text-2xl">{emoji}</span>
                <div>
                    <div className="font-semibold text-white">{name}</div>
                    <div className="text-xs text-slate-500 mb-1">Output: {score}</div>
                    <p className="text-sm text-slate-400">{description}</p>
                </div>
            </div>
        </div>
    );
}
