'use client';

import React from 'react';
import Link from 'next/link';
import { ChevronLeft, BarChart3, TrendingUp, Calendar, Activity, Brain, FileJson, Download, HelpCircle, Info } from 'lucide-react';

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

                <div className="space-y-8">
                    {/* Overview Section */}
                    <Section title="Overview" icon={<Info className="w-5 h-5" />}>
                        <p className="text-slate-300 leading-relaxed">
                            The <strong>Antigravity Terminal</strong> is a professional-grade stock analysis dashboard
                            that provides comprehensive insights into NIFTY 200 stocks. It combines traditional
                            quantitative metrics with AI-powered multi-agent analysis.
                        </p>
                    </Section>

                    {/* Report Views */}
                    <Section title="Report Views" icon={<BarChart3 className="w-5 h-5" />}>
                        <div className="space-y-4">
                            <SubSection title="Daily Screener">
                                <ul className="list-disc list-inside space-y-2 text-slate-300">
                                    <li>Real-time daily stock data with scoring system</li>
                                    <li><strong>Overall Score</strong>: Composite score (0-100) combining fundamental, technical, and momentum factors</li>
                                    <li><strong>Return columns</strong>: Toggle between 1D, 1W, and 1M returns</li>
                                    <li><strong>Top Movers</strong>: Quick view of best/worst performers</li>
                                    <li><strong>Technical Signals</strong>: RSI overbought/oversold, MACD crossovers, Golden/Death crosses</li>
                                </ul>
                            </SubSection>

                            <SubSection title="Weekly Intelligence">
                                <ul className="list-disc list-inside space-y-2 text-slate-300">
                                    <li>Weekly aggregated data with trend analysis</li>
                                    <li><strong>Weekly Trend</strong>: UP/DOWN/NEUTRAL based on price action</li>
                                    <li><strong>Volume Ratio</strong>: Current week volume vs average</li>
                                    <li><strong>RSI(14)</strong>: Weekly RSI for momentum assessment</li>
                                    <li><strong>SMA 10/20</strong>: Short-term moving average signals</li>
                                </ul>
                            </SubSection>

                            <SubSection title="Monthly Analysis">
                                <ul className="list-disc list-inside space-y-2 text-slate-300">
                                    <li>Monthly performance metrics and long-term trends</li>
                                    <li><strong>YTD Return</strong>: Year-to-date performance</li>
                                    <li><strong>3M/6M/12M Returns</strong>: Rolling period returns</li>
                                    <li><strong>SMA 3/6/12</strong>: Monthly moving averages for trend identification</li>
                                </ul>
                            </SubSection>

                            <SubSection title="Seasonality Patterns">
                                <ul className="list-disc list-inside space-y-2 text-slate-300">
                                    <li>Historical monthly performance patterns based on 5+ years of data</li>
                                    <li><strong>Best/Worst Months</strong>: Historically best and worst performing months</li>
                                    <li><strong>Win Rate</strong>: Percentage of positive returns per month</li>
                                    <li><strong>Average Returns</strong>: Mean monthly returns for each calendar month</li>
                                </ul>
                            </SubSection>
                        </div>
                    </Section>

                    {/* AI Analysis Feature */}
                    <Section title="AI Agent Analysis" icon={<Brain className="w-5 h-5" />}>
                        <p className="text-slate-300 mb-4">
                            Click the <span className="px-2 py-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded text-xs font-medium">Analyze</span> button
                            on any stock to run a comprehensive AI analysis powered by Google Gemini 2.0 Flash.
                        </p>

                        <SubSection title="The 5 Specialist Agents">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <AgentCard emoji="📈" name="Fundamental Agent" description="Analyzes PE ratio, PB ratio, ROE, debt levels, and profitability metrics" />
                                <AgentCard emoji="📉" name="Technical Agent" description="Evaluates RSI, MACD, moving averages, support/resistance, and chart patterns" />
                                <AgentCard emoji="📰" name="Sentiment Agent" description="Assesses market sentiment, news flow, and social media buzz" />
                                <AgentCard emoji="🌍" name="Macro Agent" description="Considers sector trends, economic indicators, and market conditions" />
                                <AgentCard emoji="⚖️" name="Regulatory Agent" description="Reviews compliance, corporate governance, and regulatory risks" />
                            </div>
                        </SubSection>

                        <SubSection title="Analysis Output">
                            <ul className="list-disc list-inside space-y-2 text-slate-300">
                                <li><strong>Recommendation</strong>: BUY / HOLD / SELL signal</li>
                                <li><strong>Composite Score</strong>: Weighted average of all agent scores (0-100)</li>
                                <li><strong>Target Price</strong>: AI-estimated fair value</li>
                                <li><strong>Confidence Level</strong>: HIGH / MEDIUM / LOW based on data quality</li>
                                <li><strong>AI Summary</strong>: Natural language explanation of the analysis</li>
                            </ul>
                        </SubSection>

                        <SubSection title="Export Options">
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
                        </SubSection>
                    </Section>

                    {/* Detail View */}
                    <Section title="Stock Detail View" icon={<TrendingUp className="w-5 h-5" />}>
                        <p className="text-slate-300 mb-4">
                            Click on any stock in the sidebar or table to open the detailed view with interactive charts.
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-slate-300">
                            <li><strong>Price Chart</strong>: Historical price with SMA overlays</li>
                            <li><strong>RSI Chart</strong>: Momentum indicator with overbought/oversold zones</li>
                            <li><strong>Volume Chart</strong>: Trading volume patterns</li>
                            <li><strong>Returns Chart</strong>: Period-over-period return distribution</li>
                            <li><strong>Key Metrics</strong>: All available data fields for the selected stock</li>
                        </ul>
                    </Section>

                    {/* UI Controls */}
                    <Section title="Controls & Filters" icon={<Calendar className="w-5 h-5" />}>
                        <ul className="list-disc list-inside space-y-2 text-slate-300">
                            <li><strong>Date Selector</strong>: Choose analysis date (Daily view only)</li>
                            <li><strong>Search</strong>: Filter stocks by ticker or company name</li>
                            <li><strong>Column Picker</strong>: Customize visible columns in the table</li>
                            <li><strong>Timeframe Toggle</strong>: Switch between 1D/1W/1M return periods</li>
                            <li><strong>View Toggle</strong>: Switch between GRID (table) and DETAIL (charts) views</li>
                        </ul>
                    </Section>

                    {/* Caching */}
                    <Section title="Caching & Performance" icon={<Activity className="w-5 h-5" />}>
                        <p className="text-slate-300 mb-4">
                            AI analysis results are cached for 24 hours to improve performance and reduce costs.
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-slate-300">
                            <li><strong>Cache Indicator</strong>: Shows "Cached (Xm ago)" when using cached results</li>
                            <li><strong>Fresh Analysis</strong>: Wait 24 hours or use API to clear cache for fresh analysis</li>
                            <li><strong>Cost Display</strong>: Shows token usage and estimated cost per analysis</li>
                        </ul>
                    </Section>

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

// Helper Components
function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
    return (
        <section className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white flex items-center gap-3 mb-4">
                <span className="text-blue-500">{icon}</span>
                {title}
            </h2>
            {children}
        </section>
    );
}

function SubSection({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <div className="mt-4 first:mt-0">
            <h3 className="text-lg font-semibold text-slate-200 mb-2">{title}</h3>
            {children}
        </div>
    );
}

function AgentCard({ emoji, name, description }: { emoji: string; name: string; description: string }) {
    return (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">{emoji}</span>
                <span className="font-semibold text-white">{name}</span>
            </div>
            <p className="text-sm text-slate-400">{description}</p>
        </div>
    );
}
