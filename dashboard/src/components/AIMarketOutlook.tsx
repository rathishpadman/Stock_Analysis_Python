'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
    RefreshCw,
    ChevronDown,
    ChevronRight,
    TrendingUp,
    TrendingDown,
    AlertTriangle,
    Loader2,
    Sparkles,
    Calendar,
    BarChart2,
    Target,
    Shield,
    Zap,
    Clock,
    DollarSign,
    Cpu,
    History as HistoryIcon
} from 'lucide-react';

// Use same pattern as AIAnalysisModal - direct call to Render
const API_BASE = process.env.NEXT_PUBLIC_AGENT_API_URL || 'https://nifty-agents-api.onrender.com';

// Types for different analysis types
interface WeeklyAnalysis {
    analysis_type: 'weekly';
    weekly_stance?: string;
    headline?: string;
    agent_analyses?: {
        trend?: TrendAnalysis;
        sector_rotation?: SectorRotationAnalysis;
        risk_regime?: RiskRegimeAnalysis;
    };
    synthesis?: WeeklySynthesis;
    duration_seconds?: number;
    observability?: ObservabilityData;
}

interface MonthlyAnalysis {
    analysis_type: 'monthly';
    monthly_thesis?: string;
    market_stance?: string;
    month?: string;
    agent_analyses?: {
        macro_cycle?: MacroCycleAnalysis;
        fund_flows?: FundFlowAnalysis;
        valuations?: ValuationAnalysis;
    };
    synthesis?: MonthlySynthesis;
    duration_seconds?: number;
    observability?: ObservabilityData;
}

interface SeasonalityAnalysis {
    analysis_type: 'seasonality';
    current_month?: string;
    seasonality_verdict?: string;
    probability_positive?: string;
    agent_analyses?: {
        historical_patterns?: PatternAnalysis;
        event_calendar?: EventCalendarAnalysis;
        sector_seasonality?: SectorSeasonalityAnalysis;
    };
    synthesis?: SeasonalitySynthesis;
    duration_seconds?: number;
    observability?: ObservabilityData;
}

type AnalysisResult = WeeklyAnalysis | MonthlyAnalysis | SeasonalityAnalysis;

// Sub-types for agent outputs
interface TrendAnalysis {
    primary_trend?: string;
    trend_strength?: string;
    weekly_outlook?: string;
    confidence?: number;
}

interface SectorRotationAnalysis {
    leading_sectors?: string[];
    lagging_sectors?: string[];
    rotation_direction?: string;
    sector_outlook?: string;
    confidence?: number;
}

interface RiskRegimeAnalysis {
    risk_regime?: string;
    vix_signal?: string;
    market_breadth?: string;
    risk_adjusted_advice?: string;
    confidence?: number;
}

interface WeeklySynthesis {
    weekly_stance?: string;
    headline?: string;
    key_insights?: string[];
    sector_focus?: {
        buy?: string[];
        avoid?: string[];
    };
    risk_guidance?: string;
    events_to_watch?: string[];
    composite_confidence?: number;
}

interface MacroCycleAnalysis {
    economic_cycle_phase?: string;
    inflation_outlook?: string;
    rbi_policy_bias?: string;
    monthly_macro_outlook?: string;
    confidence?: number;
}

interface FundFlowAnalysis {
    fii_stance?: string;
    dii_stance?: string;
    institutional_consensus?: string;
    flow_outlook?: string;
    confidence?: number;
}

interface ValuationAnalysis {
    market_valuation?: string;
    pe_percentile?: string;
    valuation_advice?: string;
    confidence?: number;
}

interface MonthlySynthesis {
    monthly_thesis?: string;
    market_stance?: string;
    asset_allocation?: Record<string, string>;
    top_themes?: string[];
    avoid_themes?: string[];
    key_risks?: string[];
    action_items?: string[];
    composite_confidence?: number;
}

interface PatternAnalysis {
    historical_avg_return?: string;
    historical_win_rate?: string;
    pattern_strength?: string;
    seasonality_signal?: string;
    confidence?: number;
}

interface EventCalendarAnalysis {
    upcoming_events?: Array<{
        event: string;
        date: string;
        expected_impact: string;
    }>;
    event_based_outlook?: string;
    confidence?: number;
}

interface SectorSeasonalityAnalysis {
    top_seasonal_picks?: string[];
    sectors_to_avoid_seasonally?: string[];
    confidence?: number;
}

interface SeasonalitySynthesis {
    seasonality_verdict?: string;
    probability_of_positive_month?: string;
    seasonal_alpha_opportunity?: string;
    sector_positioning?: {
        overweight?: string[];
        underweight?: string[];
    };
    event_opportunities?: string[];
    seasonal_risks?: string[];
    actionable_insight?: string;
    composite_confidence?: number;
}

interface ObservabilityData {
    trace_id?: string;
    duration_seconds?: number;
    total_tokens?: number;
    total_cost_usd?: number;
}

interface AIMarketOutlookProps {
    type: 'weekly' | 'monthly' | 'seasonality';
    ticker?: string;
    sector?: string;
}

// Stance badge component
function StanceBadge({ stance }: { stance?: string }) {
    if (!stance) return null;

    const stanceConfig: Record<string, { bg: string; text: string; icon: React.ReactNode }> = {
        bullish: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400', icon: <TrendingUp className="w-4 h-4" /> },
        bearish: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400', icon: <TrendingDown className="w-4 h-4" /> },
        neutral: { bg: 'bg-gray-100 dark:bg-gray-700', text: 'text-gray-700 dark:text-gray-300', icon: <BarChart2 className="w-4 h-4" /> },
        cautious: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-400', icon: <AlertTriangle className="w-4 h-4" /> },
        favorable: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400', icon: <TrendingUp className="w-4 h-4" /> },
        unfavorable: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400', icon: <TrendingDown className="w-4 h-4" /> },
        overweight_equity: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400', icon: <TrendingUp className="w-4 h-4" /> },
        underweight_equity: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400', icon: <TrendingDown className="w-4 h-4" /> },
    };

    const config = stanceConfig[stance.toLowerCase()] || stanceConfig.neutral;

    return (
        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text}`}>
            {config.icon}
            {stance.replace(/_/g, ' ').toUpperCase()}
        </span>
    );
}

// --- Enhanced UI Components ---

function Gauge({ value, max = 10, label, colorOverride }: { value: number; max?: number; label?: string; colorOverride?: string }) {
    const percentage = Math.min(100, Math.max(0, (value / max) * 100));
    const getColor = () => {
        if (colorOverride) return colorOverride;
        if (percentage >= 70) return 'text-green-500';
        if (percentage >= 40) return 'text-yellow-500';
        return 'text-red-500';
    };

    return (
        <div className="flex flex-col items-center">
            <div className="relative w-12 h-12">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                    <circle
                        className="text-gray-200 dark:text-gray-700 stroke-current"
                        strokeWidth="3"
                        fill="none"
                        cx="18"
                        cy="18"
                        r="16"
                    />
                    <circle
                        className={`${getColor()} stroke-current transition-all duration-1000`}
                        strokeWidth="3"
                        strokeDasharray={`${percentage}, 100`}
                        strokeLinecap="round"
                        fill="none"
                        cx="18"
                        cy="18"
                        r="16"
                    />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-[10px] font-bold text-gray-900 dark:text-gray-100">
                        {Math.round(value)}
                    </span>
                </div>
            </div>
            {label && <span className="text-[9px] uppercase tracking-wider text-gray-500 mt-1 font-bold">{label}</span>}
        </div>
    );
}

function StatCard({ label, value, subValue, trend, icon: Icon }: {
    label: string;
    value: string | number;
    subValue?: string;
    trend?: 'up' | 'down' | 'neutral';
    icon?: React.ElementType;
}) {
    return (
        <div className="bg-gray-50 dark:bg-gray-800/40 p-3 rounded-xl border border-gray-100 dark:border-gray-700/50">
            <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">{label}</span>
                {Icon && <Icon className="w-3 h-3 text-gray-400" />}
            </div>
            <div className="flex items-baseline gap-2">
                <span className="text-base font-bold text-gray-900 dark:text-gray-100">{value}</span>
                {trend && (
                    <span className={`text-xs ${trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-gray-500'}`}>
                        {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '▶'}
                    </span>
                )}
            </div>
            {subValue && <div className="text-[10px] text-gray-400 mt-0.5 truncate">{subValue}</div>}
        </div>
    );
}

function MiniTab({ active, label, onClick, color }: { active: boolean; label: string; onClick: () => void; color: string }) {
    const activeColors: Record<string, string> = {
        blue: 'text-blue-500 border-blue-500',
        purple: 'text-purple-500 border-purple-500',
        indigo: 'text-indigo-500 border-indigo-500'
    };

    return (
        <button
            onClick={onClick}
            className={`px-4 py-2 text-[10px] font-bold uppercase tracking-widest transition-all border-b-2 ${active
                ? `${activeColors[color] || activeColors.blue}`
                : 'text-gray-500 border-transparent hover:text-gray-300'
                }`}
        >
            {label}
        </button>
    );
}

// Confidence meter component
function ConfidenceMeter({ value }: { value?: number }) {
    if (value === undefined || value === null) return null;

    const percentage = Math.round(value * 100);
    const color = percentage >= 70 ? 'bg-green-500' : percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500';

    return (
        <div className="flex items-center gap-2">
            <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                    className={`h-full ${color} transition-all duration-500`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
            <span className="text-xs text-gray-500">{percentage}%</span>
        </div>
    );
}

// Agent card component
function AgentCard({
    title,
    icon,
    children,
    confidence
}: {
    title: string;
    icon: React.ReactNode;
    children: React.ReactNode;
    confidence?: number;
}) {
    const [isExpanded, setIsExpanded] = useState(true);

    return (
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
            >
                <div className="flex items-center gap-2">
                    {icon}
                    <span className="font-medium text-gray-900 dark:text-gray-100">{title}</span>
                </div>
                <div className="flex items-center gap-3">
                    {confidence !== undefined && <ConfidenceMeter value={confidence} />}
                    {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </div>
            </button>
            {isExpanded && (
                <div className="p-4 space-y-2 text-sm text-gray-700 dark:text-gray-300">
                    {children}
                </div>
            )}
        </div>
    );
}

// Helper to format price ranges
function formatPriceRange(zone: unknown): string {
    if (!zone || typeof zone !== 'object') return String(zone ?? '');
    const z = zone as Record<string, unknown>;
    const low = z.low ?? z.min ?? z.entry_low;
    const high = z.high ?? z.max ?? z.entry_high;
    if (low === 'N/A' && high === 'N/A') return 'N/A';
    if (low && high && low !== 'N/A' && high !== 'N/A') return `₹${low} - ₹${high}`;
    if (low && low !== 'N/A') return `₹${low}`;
    if (high && high !== 'N/A') return `₹${high}`;
    return 'N/A';
}

// Helper to format nested objects as readable key-value pairs
function formatObject(obj: Record<string, unknown>, indent = 0): React.ReactNode {
    const entries = Object.entries(obj).filter(([, v]) => v != null);
    if (entries.length === 0) return null;

    return (
        <div className={indent > 0 ? 'ml-4 border-l-2 border-gray-200 dark:border-gray-700 pl-3' : ''}>
            {entries.map(([key, value]) => {
                const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                if (typeof value === 'object' && !Array.isArray(value) && value !== null) {
                    return (
                        <div key={key} className="mb-2">
                            <span className="font-medium text-gray-600 dark:text-gray-400">{label}:</span>
                            {formatObject(value as Record<string, unknown>, indent + 1)}
                        </div>
                    );
                }

                return (
                    <div key={key} className="flex flex-wrap gap-1 py-0.5">
                        <span className="font-medium text-gray-600 dark:text-gray-400">{label}:</span>
                        <span className="text-gray-800 dark:text-gray-200">{renderValue(value)}</span>
                    </div>
                );
            })}
        </div>
    );
}

// Helper to safely render any value
function renderValue(value: unknown): React.ReactNode {
    if (value === null || value === undefined) return null;
    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
        return String(value);
    }
    if (Array.isArray(value)) {
        // Check if it's an array of simple values or objects
        const hasObjects = value.some(v => typeof v === 'object' && v !== null);
        if (!hasObjects) {
            return value.map((v, i) => (
                <span key={i} className="inline-block px-2 py-0.5 mr-1 mb-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    {String(v)}
                </span>
            ));
        }
        // For arrays of objects, render each as a mini-card
        return (
            <div className="space-y-1 mt-1">
                {value.map((v, i) => (
                    <div key={i} className="text-xs bg-gray-50 dark:bg-gray-800 p-2 rounded">
                        {typeof v === 'object' ? formatObject(v as Record<string, unknown>) : String(v)}
                    </div>
                ))}
            </div>
        );
    }
    if (typeof value === 'object') {
        return formatObject(value as Record<string, unknown>);
    }
    return String(value);
}

// Generic key-value renderer for dynamic data
function DataSection({ title, data, icon }: { title: string; data: Record<string, unknown>; icon?: React.ReactNode }) {
    if (!data || Object.keys(data).length === 0) return null;

    return (
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-800">
                {icon}
                <span className="font-medium text-gray-900 dark:text-gray-100">{title}</span>
            </div>
            <div className="p-3 space-y-2 text-sm">
                {Object.entries(data).map(([key, value]) => {
                    if (value === null || value === undefined) return null;
                    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    return (
                        <div key={key} className="flex flex-wrap gap-2">
                            <span className="font-medium text-gray-600 dark:text-gray-400 min-w-[120px]">{formattedKey}:</span>
                            <span className="text-gray-800 dark:text-gray-200">{renderValue(value)}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

// Render weekly analysis - handles both old and new formats
function WeeklyAnalysisView({ data }: { data: WeeklyAnalysis }) {
    const { agent_analyses, synthesis } = data;
    const syn = (synthesis as any) || {};
    const agents = (agent_analyses as any) || {};
    const [activeTab, setActiveTab] = useState<'overview' | 'sectors' | 'risk' | 'agents'>('overview');

    return (
        <div className="space-y-6">
            {/* Layer 1: Executive Layer */}
            <div className="bg-gradient-to-br from-blue-500 to-blue-700 dark:from-blue-600 dark:to-blue-900 p-6 rounded-2xl shadow-xl text-white relative overflow-hidden">
                <div className="absolute right-0 top-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 blur-2xl" />
                <div className="relative z-10 flex flex-col md:flex-row justify-between gap-6">
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                            <Sparkles className="w-5 h-5 text-blue-200" />
                            <span className="text-xs font-bold uppercase tracking-widest text-blue-100 opacity-80">Weekly AI Thesis</span>
                        </div>
                        <h3 className="text-2xl font-bold leading-tight mb-2">
                            {syn.executive_summary?.headline || syn.headline || 'Market Analysis'}
                        </h3>
                        <p className="text-blue-50 text-sm opacity-90 max-w-2xl leading-relaxed">
                            {syn.executive_summary?.one_liner || syn.weekly_thesis?.narrative || syn.executive_summary?.narrative || 'Detailed market outlook generated by AI agents.'}
                        </p>
                    </div>

                    <div className="flex items-center gap-6 px-6 py-4 bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
                        <Gauge
                            value={syn.executive_summary?.conviction_score || syn.composite_confidence * 10 || 5}
                            label="Conviction"
                            colorOverride="text-white"
                        />
                        <div className="h-10 w-[1px] bg-white/20" />
                        <div className="text-center">
                            <div className="text-[10px] uppercase tracking-widest text-blue-200 font-bold mb-1">Stance</div>
                            <StanceBadge stance={syn.weekly_stance || syn.executive_summary?.stance} />
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex items-center gap-2 border-b border-gray-100 dark:border-gray-800">
                <MiniTab active={activeTab === 'overview'} label="Overview" onClick={() => setActiveTab('overview')} color="blue" />
                <MiniTab active={activeTab === 'sectors'} label="Sectors" onClick={() => setActiveTab('sectors')} color="blue" />
                <MiniTab active={activeTab === 'risk'} label="Risk" onClick={() => setActiveTab('risk')} color="blue" />
                <MiniTab active={activeTab === 'agents'} label="Agent Details" onClick={() => setActiveTab('agents')} color="blue" />
            </div>

            {/* Layer 2: Content Layer */}
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
                {activeTab === 'overview' && (
                    <div className="space-y-6">
                        {/* Quick Pulse Stats */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <StatCard
                                label="Primary Trend"
                                value={agents.trend?.primary_trend || 'N/A'}
                                subValue={agents.trend?.trend_strength ? `Strength: ${agents.trend.trend_strength}` : undefined}
                                icon={TrendingUp}
                            />
                            <StatCard
                                label="Breadth"
                                value={agents.trend?.market_breadth?.ad_ratio || 'N/A'}
                                subValue={`${agents.trend?.market_breadth?.advances || 0} Adv / ${agents.trend?.market_breadth?.declines || 0} Dec`}
                                trend={(agents.trend?.market_breadth?.ad_ratio > 1) ? 'up' : 'down'}
                                icon={BarChart2}
                            />
                            <StatCard
                                label="Risk Regime"
                                value={agents.risk_regime?.risk_regime || 'N/A'}
                                subValue={`VIX: ${agents.risk_regime?.vix_analysis?.current_level || 'N/A'}`}
                                icon={Shield}
                            />
                            <StatCard
                                label="Net Flow"
                                value={agents.risk_regime?.flow_analysis?.net_flow_signal || 'N/A'}
                                subValue={`FII: ${agents.risk_regime?.flow_analysis?.fii_5day_cr || 0} Cr`}
                                icon={DollarSign}
                            />
                        </div>

                        {/* Top Actionable Ideas */}
                        {syn.top_3_actionable_ideas && (
                            <div className="grid md:grid-cols-3 gap-4">
                                {syn.top_3_actionable_ideas.map((idea: any, i: number) => (
                                    <div key={i} className="group p-4 bg-white dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700/50 rounded-2xl hover:shadow-lg transition-all">
                                        <div className="flex items-center justify-between mb-3">
                                            <span className="w-8 h-8 flex items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-bold text-xs italic">
                                                #{i + 1}
                                            </span>
                                            {idea.risk_reward && (
                                                <span className="text-[10px] font-bold px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 rounded-lg">
                                                    R:R {idea.risk_reward}
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">{idea.type || 'Opportunity'}</div>
                                        <div className="font-bold text-gray-900 dark:text-gray-100 mb-2 truncate group-hover:text-blue-500 transition-colors">
                                            {idea.name || idea.sector}
                                        </div>
                                        <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed mb-4 line-clamp-3 italic">
                                            &quot;{idea.rationale || idea.action}&quot;
                                        </p>
                                        <div className="pt-3 border-t border-gray-50 dark:border-gray-700/50 grid grid-cols-2 gap-2 mt-auto">
                                            <div>
                                                <div className="text-[9px] uppercase text-gray-400 font-bold">Entry Zone</div>
                                                <div className="text-[11px] font-bold text-gray-700 dark:text-gray-300 truncate">{formatPriceRange(idea.entry_zone)}</div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-[9px] uppercase text-gray-400 font-bold">Target</div>
                                                <div className="text-[11px] font-bold text-green-500">{idea.target_pct}%</div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="grid md:grid-cols-2 gap-6">
                            {/* Events & Checklist Split */}
                            <div className="space-y-4">
                                <div className="bg-gray-50 dark:bg-gray-800/30 rounded-2xl p-4 border border-gray-200/50 dark:border-gray-700/50">
                                    <h4 className="flex items-center gap-2 text-sm font-bold text-gray-900 dark:text-gray-100 mb-4">
                                        <Calendar className="w-4 h-4 text-blue-500" />
                                        Events This Week
                                    </h4>
                                    <div className="space-y-2">
                                        {syn.events_calendar?.map((event: any, i: number) => (
                                            <div key={i} className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 rounded-lg text-xs">
                                                <div className="flex flex-col">
                                                    <span className="font-bold text-gray-700 dark:text-gray-300">{event.event}</span>
                                                    <span className="text-[10px] text-gray-500">{event.date}</span>
                                                </div>
                                                <span className={`px-2 py-0.5 rounded uppercase font-bold text-[9px] ${event.expected_impact === 'bullish' ? 'bg-green-100 text-green-700' :
                                                    event.expected_impact === 'bearish' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'
                                                    }`}>
                                                    {event.expected_impact}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="bg-gray-50 dark:bg-gray-800/30 rounded-2xl p-4 border border-gray-200/50 dark:border-gray-700/50">
                                <h4 className="flex items-center gap-2 text-sm font-bold text-gray-900 dark:text-gray-100 mb-4">
                                    <Zap className="w-4 h-4 text-yellow-500" />
                                    Weekly Checklist
                                </h4>
                                <div className="space-y-3">
                                    {syn.monday_checklist?.map((item: string, i: number) => (
                                        <div key={i} className="flex items-start gap-3 group">
                                            <div className="mt-1 w-4 h-4 flex items-center justify-center rounded border border-gray-300 dark:border-gray-600 group-hover:border-blue-500 transition-colors" />
                                            <span className="text-xs text-gray-600 dark:text-gray-400">{item}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'sectors' && (
                    <div className="space-y-6">
                        <div className="grid md:grid-cols-3 gap-6">
                            <div className="md:col-span-2">
                                <h4 className="text-sm font-bold mb-4 flex items-center gap-2">
                                    <BarChart2 className="w-4 h-4 text-purple-500" />
                                    Sector Allocation Matrix
                                </h4>
                                <div className="bg-white dark:bg-gray-800/50 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
                                    <table className="w-full text-xs text-left">
                                        <thead className="bg-gray-50 dark:bg-gray-800/80 uppercase text-[9px] font-bold text-gray-500">
                                            <tr>
                                                <th className="px-4 py-3">Sector</th>
                                                <th className="px-4 py-3">1W Ret</th>
                                                <th className="px-4 py-3">RS Ratio</th>
                                                <th className="px-4 py-3">Stance</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                                            {syn.sector_allocation?.map((sec: any, i: number) => (
                                                <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                                    <td className="px-4 py-3 font-bold text-gray-900 dark:text-gray-100">{sec.sector}</td>
                                                    <td className={`px-4 py-3 font-bold ${sec.return_1w_pct >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                                        {sec.return_1w_pct >= 0 ? '+' : ''}{sec.return_1w_pct}%
                                                    </td>
                                                    <td className="px-4 py-3 text-gray-500">{sec.relative_strength_vs_nifty || 100}</td>
                                                    <td className="px-4 py-3">
                                                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase ${sec.stance === 'overweight' ? 'bg-green-100 text-green-700' :
                                                            sec.stance === 'underweight' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'
                                                            }`}>
                                                            {sec.stance}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <h4 className="text-sm font-bold mb-4">Rotation Signal</h4>
                                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-2xl">
                                    <div className="text-[10px] font-bold text-purple-600 uppercase mb-2">Direction</div>
                                    <div className="text-xl font-bold text-purple-900 dark:text-purple-100 mb-1">
                                        {syn.sector_rotation?.direction || 'Neutral'}
                                    </div>
                                    <p className="text-[11px] text-purple-700 dark:text-purple-300 leading-relaxed mb-4">
                                        Moving from {syn.sector_rotation?.from_sectors?.join(', ')} to {syn.sector_rotation?.to_sectors?.join(', ')}.
                                    </p>
                                    <Gauge value={syn.sector_rotation?.rotation_strength * 2 || 5} label="Rotation Strength" />
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'risk' && (
                    <div className="space-y-6">
                        <div className="grid md:grid-cols-3 gap-6">
                            <div className="bg-orange-50 dark:bg-orange-900/20 p-6 rounded-2xl border border-orange-200 dark:border-orange-800 flex flex-col items-center">
                                <Shield className="w-12 h-12 text-orange-500 mb-4 opacity-50" />
                                <div className="text-center">
                                    <div className="text-[10px] font-bold text-orange-600 uppercase tracking-widest mb-1">Current Risk Regime</div>
                                    <div className="text-2xl font-bold text-orange-900 dark:text-orange-100 mb-4 uppercase">
                                        {agents.risk_regime?.risk_regime || 'Moderate'}
                                    </div>
                                    <Gauge value={agents.risk_regime?.risk_regime_score || 5} label="Risk Intensity" />
                                </div>
                            </div>

                            <div className="md:col-span-2 space-y-4">
                                <h4 className="text-sm font-bold">Position Guidelines</h4>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/30 border border-gray-100 dark:border-gray-700">
                                        <div className="text-[10px] font-bold text-gray-400 uppercase mb-1">Equity Allocation</div>
                                        <div className="text-xl font-bold">{syn.risk_management?.position_sizing?.recommendation?.match(/\d+%/)?.[0] || '65%'}</div>
                                    </div>
                                    <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/30 border border-gray-100 dark:border-gray-700">
                                        <div className="text-[10px] font-bold text-gray-400 uppercase mb-1">Index Stop Loss</div>
                                        <div className="text-xl font-bold font-mono">{syn.risk_management?.stop_loss_guidance?.index_stop_loss || 'Dynamic'}</div>
                                    </div>
                                </div>
                                <div className="p-4 rounded-xl bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
                                    <h5 className="text-xs font-bold text-yellow-700 dark:text-yellow-400 flex items-center gap-2 mb-2">
                                        <AlertTriangle className="w-3 h-3" />
                                        Key Risk Factors
                                    </h5>
                                    <ul className="space-y-2">
                                        {syn.risk_management?.key_risk_factors?.map((risk: any, i: number) => (
                                            <li key={i} className="text-xs text-yellow-800 dark:text-yellow-200 flex justify-between gap-4">
                                                <span>{risk.risk}</span>
                                                <span className="font-bold whitespace-nowrap">{risk.probability || 'low'} prob</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'agents' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {agents.trend && (
                            <AgentCard title="Trend Strategist" icon={<TrendingUp className="w-4 h-4 text-blue-500" />} confidence={0.85}>
                                {formatObject(agents.trend)}
                            </AgentCard>
                        )}
                        {agents.sector_rotation && (
                            <AgentCard title="Rotation Analyst" icon={<BarChart2 className="w-4 h-4 text-purple-500" />} confidence={0.78}>
                                {formatObject(agents.sector_rotation)}
                            </AgentCard>
                        )}
                        {agents.risk_regime && (
                            <AgentCard title="Risk Manager" icon={<Shield className="w-4 h-4 text-orange-500" />} confidence={0.92}>
                                {formatObject(agents.risk_regime)}
                            </AgentCard>
                        )}
                    </div>
                )}
            </div>

            {/* Fallback: Legacy format key_insights */}
            {syn.key_insights && syn.key_insights.length > 0 && (
                <div className="space-y-2 mt-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Zap className="w-4 h-4 text-yellow-500" />
                        Key Insights
                    </h4>
                    <ul className="space-y-1">
                        {syn.key_insights.map((insight: string, i: number) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                                <span className="text-blue-500 mt-1">•</span>
                                {insight}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

// Render monthly analysis - handles both old and new formats
function MonthlyAnalysisView({ data }: { data: MonthlyAnalysis }) {
    const { agent_analyses, synthesis } = data;
    const syn = (synthesis as any) || {};
    const agents = (agent_analyses as any) || {};
    const [activeTab, setActiveTab] = useState<'strategy' | 'allocation' | 'macro' | 'agents'>('strategy');

    return (
        <div className="space-y-6">
            {/* Layer 1: Strategic Layer */}
            <div className="bg-gradient-to-br from-purple-600 to-indigo-800 p-6 rounded-2xl shadow-xl text-white relative overflow-hidden">
                <div className="absolute right-0 bottom-0 w-48 h-48 bg-white/5 rounded-full -mr-24 -mb-24 blur-3xl" />
                <div className="relative z-10 flex flex-col md:flex-row justify-between gap-6">
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2 text-purple-200">
                            <Sparkles className="w-5 h-5" />
                            <span className="text-xs font-bold uppercase tracking-widest opacity-80">Monthly Investment Strategy</span>
                        </div>
                        <h3 className="text-2xl font-bold leading-tight mb-2">
                            {syn.monthly_thesis?.headline || 'Monthly Outlook'}
                        </h3>
                        <p className="text-purple-50 text-sm opacity-90 max-w-2xl leading-relaxed">
                            {syn.monthly_thesis?.narrative || 'Comprehensive monthly tactical allocation and theme analysis.'}
                        </p>
                    </div>

                    <div className="flex items-center gap-6 px-6 py-4 bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
                        <Gauge
                            value={syn.monthly_thesis?.conviction_score || syn.composite_confidence * 10 || 5}
                            label="Confidence"
                            colorOverride="text-white"
                        />
                        <div className="h-10 w-[1px] bg-white/20" />
                        <div className="text-center">
                            <div className="text-[10px] uppercase tracking-widest text-purple-200 font-bold mb-1">Stance</div>
                            <StanceBadge stance={syn.market_stance || syn.monthly_thesis?.stance} />
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex items-center gap-2 border-b border-gray-100 dark:border-gray-800">
                <MiniTab active={activeTab === 'strategy'} label="Strategy" onClick={() => setActiveTab('strategy')} color="purple" />
                <MiniTab active={activeTab === 'allocation'} label="Allocation" onClick={() => setActiveTab('allocation')} color="purple" />
                <MiniTab active={activeTab === 'macro'} label="Macro/Flows" onClick={() => setActiveTab('macro')} color="purple" />
                <MiniTab active={activeTab === 'agents'} label="Agent Details" onClick={() => setActiveTab('agents')} color="purple" />
            </div>

            <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
                {activeTab === 'strategy' && (
                    <div className="space-y-6">
                        {/* Summary Metrics */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <StatCard
                                label="Macro Cycle"
                                value={agents.macro_cycle?.economic_cycle_phase || agents.macro_cycle?.cycle_phase || 'N/A'}
                                icon={TrendingUp}
                            />
                            <StatCard
                                label="Valuation"
                                value={agents.valuations?.market_valuation || 'N/A'}
                                subValue={agents.valuations?.pe_percentile ? `PE Perc: ${agents.valuations.pe_percentile}` : undefined}
                                icon={BarChart2}
                            />
                            <StatCard
                                label="FII Flow"
                                value={agents.fund_flows?.fii_stance || 'N/A'}
                                icon={DollarSign}
                            />
                            <StatCard
                                label="DII Flow"
                                value={agents.fund_flows?.dii_stance || 'N/A'}
                                icon={RefreshCw}
                            />
                        </div>

                        {/* Top Themes & Ideas */}
                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <h4 className="text-sm font-bold flex items-center gap-2">
                                    <Target className="w-4 h-4 text-green-500" />
                                    Top Actionable Themes
                                </h4>
                                <div className="grid gap-3">
                                    {(syn.top_monthly_ideas || syn.top_themes)?.map((idea: any, i: number) => (
                                        <div key={i} className="p-4 bg-white dark:bg-gray-800/40 border border-gray-100 dark:border-gray-700/50 rounded-xl">
                                            <div className="flex justify-between mb-1">
                                                <span className="font-bold text-gray-900 dark:text-gray-100 text-sm">{typeof idea === 'string' ? idea : idea.name || idea.theme}</span>
                                                {idea.risk_reward && <span className="text-[10px] font-bold text-green-600">R:R {idea.risk_reward}</span>}
                                            </div>
                                            {(idea.rationale || idea.action) && <p className="text-[11px] text-gray-500 italic leading-relaxed">{idea.rationale || idea.action}</p>}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <h4 className="text-sm font-bold flex items-center gap-2">
                                    <AlertTriangle className="w-4 h-4 text-red-500" />
                                    Key Risks & To-Avoid
                                </h4>
                                <div className="p-4 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30 rounded-xl">
                                    <ul className="space-y-3">
                                        {(syn.key_risks || syn.avoid_themes)?.map((risk: string, i: number) => (
                                            <li key={i} className="flex items-start gap-3 text-xs text-red-800 dark:text-red-300">
                                                <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
                                                {risk}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'allocation' && (
                    <div className="space-y-6">
                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <h4 className="text-sm font-bold">Asset Mix</h4>
                                <div className="grid grid-cols-2 gap-3">
                                    {syn.asset_allocation && Object.entries(syn.asset_allocation).filter(([k]) => k.includes('pct')).map(([key, val]: [string, any]) => (
                                        <div key={key} className="p-4 bg-gray-50 dark:bg-gray-800/40 rounded-xl border border-gray-200/50">
                                            <div className="text-[10px] uppercase font-bold text-gray-400 mb-1">{key.replace('_pct', '')}</div>
                                            <div className="text-2xl font-bold">{val}%</div>
                                        </div>
                                    ))}
                                </div>
                                {syn.asset_allocation?.rationale && (
                                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 text-xs rounded-xl">
                                        <strong>Rationale:</strong> {syn.asset_allocation.rationale}
                                    </div>
                                )}
                            </div>

                            <div className="space-y-4">
                                <h4 className="text-sm font-bold">Sector Weights</h4>
                                <div className="bg-white dark:bg-gray-800/50 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
                                    <table className="w-full text-[11px] text-left">
                                        <thead className="bg-gray-50 dark:bg-gray-800/80 uppercase text-[9px] font-bold text-gray-500">
                                            <tr>
                                                <th className="px-4 py-2">Sector</th>
                                                <th className="px-4 py-2 text-center">Weight</th>
                                                <th className="px-4 py-2 text-right">Stance</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                                            {syn.sector_allocation?.map((sec: any, i: number) => (
                                                <tr key={i}>
                                                    <td className="px-4 py-2 font-bold">{sec.sector}</td>
                                                    <td className="px-4 py-2 text-center">{sec.weight_pct}%</td>
                                                    <td className="px-4 py-2 text-right">
                                                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase ${sec.vs_benchmark === 'overweight' ? 'bg-green-100 text-green-700' :
                                                            sec.vs_benchmark === 'underweight' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'
                                                            }`}>
                                                            {sec.vs_benchmark}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'macro' && (
                    <div className="grid md:grid-cols-3 gap-6">
                        <div className="p-4 bg-gray-50 dark:bg-gray-800/30 rounded-2xl border border-gray-200/50">
                            <h5 className="text-xs font-bold uppercase text-gray-400 mb-4">Economic Pulse</h5>
                            <div className="space-y-4">
                                <div>
                                    <div className="text-[10px] font-bold text-blue-500 uppercase">Cycle Phase</div>
                                    <div className="text-sm font-bold">{agents.macro_cycle?.economic_cycle_phase || agents.macro_cycle?.cycle_phase || 'N/A'}</div>
                                </div>
                                <div>
                                    <div className="text-[10px] font-bold text-orange-500 uppercase">Inflation</div>
                                    <div className="text-sm font-bold">{agents.macro_cycle?.inflation_outlook || 'N/A'}</div>
                                </div>
                                <div>
                                    <div className="text-[10px] font-bold text-purple-500 uppercase">Monetary Policy</div>
                                    <div className="text-sm font-bold">{agents.macro_cycle?.rbi_policy_bias || 'N/A'}</div>
                                </div>
                            </div>
                        </div>

                        <div className="p-4 bg-gray-50 dark:bg-gray-800/30 rounded-2xl border border-gray-200/50">
                            <h5 className="text-xs font-bold uppercase text-gray-400 mb-4">Valuation Matrix</h5>
                            <div className="space-y-4">
                                <div>
                                    <div className="text-[10px] font-bold text-gray-500 uppercase">Market P/E</div>
                                    <div className="text-sm font-bold">{agents.valuations?.pe_percentile || 'N/A'}</div>
                                </div>
                                <div>
                                    <div className="text-[10px] font-bold text-gray-500 uppercase">EY/BY Gap</div>
                                    <div className="text-sm font-bold">{agents.valuations?.earnings_yield_vs_bond_yield || 'N/A'}</div>
                                </div>
                                <div className="pt-2">
                                    <div className="text-[10px] font-bold text-gray-500 uppercase mb-2">Attractiveness</div>
                                    <Gauge value={agents.valuations?.attractiveness_score || 5} />
                                </div>
                            </div>
                        </div>

                        <div className="p-4 bg-gray-50 dark:bg-gray-800/30 rounded-2xl border border-gray-200/50">
                            <h5 className="text-xs font-bold uppercase text-gray-400 mb-4">Fund Dynamics</h5>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-xs text-gray-500">FII Sentiment</span>
                                    <span className={`text-xs font-bold ${agents.fund_flows?.fii_stance?.toLowerCase().includes('bull') || agents.fund_flows?.fii_stance?.toLowerCase().includes('buy') ? 'text-green-500' : 'text-red-500'}`}>
                                        {agents.fund_flows?.fii_stance || 'N/A'}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-xs text-gray-500">DII Support</span>
                                    <span className={`text-xs font-bold ${agents.fund_flows?.dii_stance?.toLowerCase().includes('bull') || agents.fund_flows?.dii_stance?.toLowerCase().includes('buy') ? 'text-green-500' : 'text-red-500'}`}>
                                        {agents.fund_flows?.dii_stance || 'N/A'}
                                    </span>
                                </div>
                                <p className="text-[10px] text-gray-400 italic mt-4 leading-relaxed">
                                    {agents.fund_flows?.institutional_consensus}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'agents' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {agents.macro_cycle && (
                            <AgentCard title="Macro Strategist" icon={<TrendingUp className="w-4 h-4 text-blue-500" />} confidence={0.88}>
                                {formatObject(agents.macro_cycle)}
                            </AgentCard>
                        )}
                        {agents.fund_flows && (
                            <AgentCard title="Flow Monitor" icon={<DollarSign className="w-4 h-4 text-green-500" />} confidence={0.82}>
                                {formatObject(agents.fund_flows)}
                            </AgentCard>
                        )}
                        {agents.valuations && (
                            <AgentCard title="Value Quant" icon={<BarChart2 className="w-4 h-4 text-purple-500" />} confidence={0.94}>
                                {formatObject(agents.valuations)}
                            </AgentCard>
                        )}
                    </div>
                )}
            </div>

            {/* Monthly Action Items */}
            {syn.action_items && syn.action_items.length > 0 && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/30 rounded-2xl">
                    <h4 className="text-sm font-bold text-blue-900 dark:text-blue-100 mb-3 flex items-center gap-2">
                        <Zap className="w-4 h-4" />
                        Execution Checklist
                    </h4>
                    <div className="grid md:grid-cols-2 gap-x-6 gap-y-2">
                        {syn.action_items.map((item: string, i: number) => (
                            <div key={i} className="flex items-start gap-2 text-[11px] text-blue-800 dark:text-blue-300">
                                <div className="w-3.5 h-3.5 mt-0.5 rounded border border-blue-300 dark:border-blue-700 flex-shrink-0" />
                                {item}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

// Render seasonality analysis - handles both old and new formats
function SeasonalityAnalysisView({ data }: { data: SeasonalityAnalysis }) {
    const { agent_analyses, synthesis, current_month } = data;
    const syn = (synthesis as any) || {};
    const agents = (agent_analyses as any) || {};
    const [activeTab, setActiveTab] = useState<'outlook' | 'playbook' | 'calendar' | 'agents'>('outlook');

    return (
        <div className="space-y-6">
            {/* Layer 1: Seasonality Executive Header */}
            <div className="bg-gradient-to-br from-indigo-500 to-purple-700 p-6 rounded-2xl shadow-xl text-white relative overflow-hidden">
                <div className="absolute right-0 top-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32 blur-3xl opacity-50" />
                <div className="relative z-10 flex flex-col md:flex-row justify-between gap-6">
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2 text-indigo-100">
                            <Sparkles className="w-5 h-5" />
                            <span className="text-xs font-bold uppercase tracking-widest opacity-80">{current_month} Seasonal Edge Analysis</span>
                        </div>
                        <h3 className="text-2xl font-bold leading-tight mb-2">
                            {syn.seasonality_thesis?.headline || `${current_month} Market Seasonality`}
                        </h3>
                        <p className="text-indigo-50 text-sm opacity-90 max-w-2xl leading-relaxed">
                            {syn.seasonality_thesis?.statistical_backing || syn.actionable_insight || 'Statistical pattern recognition for the current calendar window.'}
                        </p>
                    </div>

                    <div className="flex items-center gap-6 px-6 py-4 bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
                        <Gauge
                            value={syn.seasonality_thesis?.probability_of_positive_month_pct || syn.probability_of_positive_month || 50}
                            max={100}
                            label="Win Prob"
                            colorOverride="text-white"
                        />
                        <div className="h-10 w-[1px] bg-white/20" />
                        <div className="text-center">
                            <div className="text-[10px] uppercase tracking-widest text-indigo-200 font-bold mb-1">Verdict</div>
                            <StanceBadge stance={syn.seasonality_verdict || (syn.composite_seasonal_score?.composite_score > 60 ? 'bullish' : 'neutral')} />
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex items-center gap-2 border-b border-gray-100 dark:border-gray-800">
                <MiniTab active={activeTab === 'outlook'} label="Edge Outlook" onClick={() => setActiveTab('outlook')} color="indigo" />
                <MiniTab active={activeTab === 'playbook'} label="Tactical Playbook" onClick={() => setActiveTab('playbook')} color="indigo" />
                <MiniTab active={activeTab === 'calendar'} label="Action Calendar" onClick={() => setActiveTab('calendar')} color="indigo" />
                <MiniTab active={activeTab === 'agents'} label="Pattern Details" onClick={() => setActiveTab('agents')} color="indigo" />
            </div>

            <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
                {activeTab === 'outlook' && (
                    <div className="space-y-6">
                        {/* Composite Seasonal Score Grid */}
                        {syn.composite_seasonal_score && (
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <StatCard
                                    label="Historical Pattern"
                                    value={`${syn.composite_seasonal_score.historical_pattern_score}/10`}
                                    icon={HistoryIcon}
                                />
                                <StatCard
                                    label="Event Calendar"
                                    value={`${syn.composite_seasonal_score.event_calendar_score}/10`}
                                    icon={Calendar}
                                />
                                <StatCard
                                    label="Sector Tailwinds"
                                    value={`${syn.composite_seasonal_score.sector_seasonality_score}/10`}
                                    icon={TrendingUp}
                                />
                                <div className="p-4 bg-indigo-600 rounded-2xl shadow-lg shadow-indigo-200 dark:shadow-none text-white flex flex-col items-center justify-center">
                                    <div className="text-[10px] uppercase font-bold opacity-80 mb-1">Composite Score</div>
                                    <div className="text-2xl font-black">{syn.composite_seasonal_score.composite_score}</div>
                                </div>
                            </div>
                        )}

                        <div className="grid md:grid-cols-2 gap-6">
                            {/* Performance Parameters */}
                            <div className="space-y-4">
                                <h4 className="text-sm font-bold flex items-center gap-2">
                                    <BarChart2 className="w-4 h-4 text-indigo-500" />
                                    Expected Performance
                                </h4>
                                <div className="bg-white dark:bg-gray-800/40 p-4 rounded-2xl border border-gray-100 dark:border-gray-700/50 space-y-4">
                                    <div className="flex justify-between items-center pb-2 border-b border-gray-50 dark:border-gray-700">
                                        <span className="text-xs text-gray-500">Expected Range</span>
                                        <span className="text-sm font-bold text-indigo-600">
                                            {syn.seasonality_thesis?.expected_return_range_pct?.low}% to {syn.seasonality_thesis?.expected_return_range_pct?.high}%
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center pb-2 border-b border-gray-50 dark:border-gray-700">
                                        <span className="text-xs text-gray-500">Historical Median Return</span>
                                        <span className="text-sm font-bold">
                                            {(syn.monthly_action_calendar?.find((m: any) => m.month === current_month)?.historical_return_pct) || 'N/A'}%
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs text-gray-500">Volatility Regime</span>
                                        <span className="text-sm font-bold px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-[10px] uppercase">Moderate</span>
                                    </div>
                                </div>
                            </div>

                            {/* Bottom Line Summary */}
                            {syn.bottom_line && (
                                <div className="space-y-4">
                                    <h4 className="text-sm font-bold flex items-center gap-2">
                                        <Zap className="w-4 h-4 text-yellow-500" />
                                        The Bottom Line
                                    </h4>
                                    <div className="p-5 bg-indigo-50 dark:bg-indigo-900/10 border border-indigo-100 dark:border-indigo-900/30 rounded-2xl relative">
                                        <div className="absolute top-0 right-0 p-3">
                                            <div className="text-[9px] font-bold text-indigo-400 uppercase tracking-tighter">Confidence: {syn.bottom_line.confidence}</div>
                                        </div>
                                        <p className="text-sm font-medium text-indigo-900 dark:text-indigo-200 leading-relaxed italic">
                                            &ldquo;{syn.bottom_line.one_liner}&rdquo;
                                        </p>
                                        <div className="mt-4 flex items-center gap-3">
                                            <div className="px-3 py-1 bg-white dark:bg-indigo-800 rounded-full text-[10px] font-bold border border-indigo-100 dark:border-indigo-700 shadow-sm">
                                                Horizon: {syn.bottom_line.time_horizon}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {activeTab === 'playbook' && syn.current_month_playbook && (
                    <div className="space-y-6">
                        {/* Strategy Box */}
                        <div className="p-4 bg-gray-900 text-gray-100 rounded-2xl shadow-xl">
                            <h5 className="text-[10px] uppercase font-bold text-indigo-400 mb-2">Core Strategy</h5>
                            <p className="text-sm leading-relaxed">{syn.current_month_playbook.primary_strategy}</p>
                        </div>

                        <div className="grid md:grid-cols-2 gap-6">
                            {/* Position Sizing */}
                            <div className="space-y-4">
                                <h4 className="text-sm font-bold">Scaling Guidelines</h4>
                                <div className="grid grid-cols-3 gap-3">
                                    <div className="p-3 bg-white dark:bg-gray-800/40 border border-gray-100 dark:border-gray-700/50 rounded-xl text-center">
                                        <div className="text-[9px] uppercase font-bold text-gray-400 mb-1">Base</div>
                                        <div className="text-lg font-bold">{syn.current_month_playbook.position_sizing?.base_equity_pct}%</div>
                                    </div>
                                    <div className="p-3 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30 rounded-xl text-center">
                                        <div className="text-[9px] uppercase font-bold text-indigo-500 mb-1">Seasonal Adj</div>
                                        <div className="text-lg font-bold text-indigo-600">
                                            {syn.current_month_playbook.position_sizing?.seasonal_adjustment_pct > 0 ? '+' : ''}
                                            {syn.current_month_playbook.position_sizing?.seasonal_adjustment_pct}%
                                        </div>
                                    </div>
                                    <div className="p-3 bg-green-500 rounded-xl text-center text-white shadow-lg shadow-green-100 dark:shadow-none">
                                        <div className="text-[9px] uppercase font-bold opacity-80 mb-1">Final Exp</div>
                                        <div className="text-lg font-black">{syn.current_month_playbook.position_sizing?.final_equity_pct}%</div>
                                    </div>
                                </div>
                            </div>

                            {/* Sector Tilts */}
                            <div className="space-y-4">
                                <h4 className="text-sm font-bold">Sector Orientations</h4>
                                <div className="grid grid-cols-2 gap-2">
                                    {syn.current_month_playbook.sector_tilts?.map((tilt: any, i: number) => (
                                        <div key={i} className={`px-3 py-2 rounded-lg border flex justify-between items-center ${tilt.action === 'overweight' ? 'bg-green-50 border-green-100 text-green-800 dark:bg-green-900/10 dark:border-green-800' :
                                            tilt.action === 'underweight' ? 'bg-red-50 border-red-100 text-red-800 dark:bg-red-900/10 dark:border-red-800' :
                                                'bg-gray-50 border-gray-100 text-gray-800 dark:bg-gray-800/10 dark:border-gray-700'
                                            }`}>
                                            <span className="text-[11px] font-bold">{tilt.sector}</span>
                                            <span className="text-[10px] opacity-70">{tilt.size_pct}%</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Event Trades */}
                        {syn.current_month_playbook.event_trades && syn.current_month_playbook.event_trades.length > 0 && (
                            <div className="space-y-3">
                                <h4 className="text-sm font-bold flex items-center gap-2">
                                    <Clock className="w-4 h-4 text-purple-500" />
                                    Specific Event Setups
                                </h4>
                                <div className="grid md:grid-cols-2 gap-3">
                                    {syn.current_month_playbook.event_trades.map((trade: any, i: number) => (
                                        <div key={i} className="group p-4 bg-white dark:bg-gray-800/40 border border-gray-100 dark:border-gray-700/50 rounded-2xl hover:border-indigo-200 transition-all">
                                            <div className="flex justify-between items-start mb-2">
                                                <h6 className="text-[11px] font-bold text-indigo-600 uppercase tracking-tight">{trade.event}</h6>
                                                <span className="text-[9px] font-black px-1.5 py-0.5 bg-indigo-100 dark:bg-indigo-900 text-indigo-700 rounded-full">R:R {trade.risk_reward}</span>
                                            </div>
                                            <p className="text-xs font-bold text-gray-900 dark:text-gray-100 mb-2">{trade.trade}</p>
                                            <div className="flex justify-between text-[10px] text-gray-400">
                                                <span>Entry: {trade.entry_date}</span>
                                                <span>Exit: {trade.exit_date}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'calendar' && syn.monthly_action_calendar && (
                    <div className="space-y-6">
                        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 overflow-hidden shadow-sm">
                            <table className="w-full text-left">
                                <thead className="bg-gray-50 dark:bg-gray-800/50">
                                    <tr>
                                        <th className="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase">Window</th>
                                        <th className="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase text-center">Bias</th>
                                        <th className="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase text-center">Hist. Return</th>
                                        <th className="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase text-center">Alloc %</th>
                                        <th className="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase">Sector Leaders</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                                    {syn.monthly_action_calendar.map((m: any, i: number) => (
                                        <tr key={i} className={m.month === current_month ? 'bg-indigo-50/50 dark:bg-indigo-900/10' : ''}>
                                            <td className="px-6 py-4">
                                                <div className="text-sm font-bold flex items-center gap-2">
                                                    {m.month}
                                                    {m.month === current_month && <span className="text-[9px] bg-indigo-600 text-white px-1.5 py-0.5 rounded-full uppercase">Current</span>}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-center">
                                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${m.seasonal_bias === 'bullish' ? 'bg-green-100 text-green-700' :
                                                    m.seasonal_bias === 'bearish' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'
                                                    }`}>
                                                    {m.seasonal_bias}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-center font-mono text-sm">{m.historical_return_pct}%</td>
                                            <td className="px-6 py-4 text-center font-bold text-sm">{m.recommended_equity_allocation_pct}%</td>
                                            <td className="px-6 py-4">
                                                <div className="flex flex-wrap gap-1">
                                                    {m.sector_leaders?.map((s: string, j: number) => (
                                                        <span key={j} className="text-[10px] bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded border border-gray-200 dark:border-gray-700">{s}</span>
                                                    ))}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'agents' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {agents.historical_patterns && (
                            <AgentCard title="Historical Analyst" icon={<HistoryIcon className="w-4 h-4 text-blue-500" />} confidence={0.92}>
                                {formatObject(agents.historical_patterns)}
                            </AgentCard>
                        )}
                        {agents.event_calendar && (
                            <AgentCard title="Event Tracker" icon={<Calendar className="w-4 h-4 text-purple-500" />} confidence={0.85}>
                                {formatObject(agents.event_calendar)}
                            </AgentCard>
                        )}
                        {agents.sector_seasonality && (
                            <AgentCard title="Sector Specialist" icon={<TrendingUp className="w-4 h-4 text-green-500" />} confidence={0.89}>
                                {formatObject(agents.sector_seasonality)}
                            </AgentCard>
                        )}
                    </div>
                )}
            </div>

            {/* Final Risk Warnings */}
            {syn.risk_warnings && syn.risk_warnings.length > 0 && (
                <div className="p-4 bg-orange-50 dark:bg-orange-900/10 border border-orange-100 dark:border-orange-900/30 rounded-2xl">
                    <h4 className="text-sm font-bold text-orange-900 dark:text-orange-200 mb-3 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        Critical Pattern Risks
                    </h4>
                    <div className="grid md:grid-cols-2 gap-x-6 gap-y-3">
                        {syn.risk_warnings.map((risk: any, i: number) => (
                            <div key={i} className="flex items-start gap-3">
                                <div className="p-1 bg-orange-100 dark:bg-orange-800 rounded text-[10px] font-black text-orange-700 dark:text-orange-200 leading-none">
                                    {risk.probability_pct}% Prob
                                </div>
                                <div className="text-[11px] text-orange-800 dark:text-orange-300 font-medium">
                                    {risk.risk}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

// Main component
export default function AIMarketOutlook({ type, ticker, sector }: AIMarketOutlookProps) {
    const [data, setData] = useState<AnalysisResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isExpanded, setIsExpanded] = useState(false);
    const [lastFetchType, setLastFetchType] = useState<string | null>(null);

    // Reset data when type/context changes
    useEffect(() => {
        if (type !== lastFetchType || !data) {
            setData(null);
            setIsExpanded(false);
            setLastFetchType(null); // Reset until next fetch
        }
    }, [type, ticker, sector]);

    const fetchAnalysis = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            // Map type to Render API endpoint (same pattern as AIAnalysisModal)
            let endpoint: string;
            switch (type) {
                case 'weekly':
                    endpoint = '/api/agent/weekly-outlook';
                    break;
                case 'monthly':
                    endpoint = '/api/agent/monthly-thesis';
                    break;
                case 'seasonality':
                    endpoint = '/api/agent/seasonality';
                    break;
                default:
                    throw new Error(`Unknown analysis type: ${type}`);
            }

            // Build URL with query params for seasonality
            let url = `${API_BASE}${endpoint}`;
            if (type === 'seasonality' && (ticker || sector)) {
                const params = new URLSearchParams();
                if (ticker) params.set('ticker', ticker);
                if (sector) params.set('sector', sector);
                url += `?${params.toString()}`;
            }

            console.log(`[AIMarketOutlook] Fetching from: ${url}`);

            const response = await fetch(url, {
                headers: { 'Accept': 'application/json' }
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(`API error ${response.status}: ${errText}`);
            }

            const result = await response.json();
            setData(result);
            setLastFetchType(type);
            setIsExpanded(true);

        } catch (err) {
            console.error('[AIMarketOutlook] Error:', err);
            setError(err instanceof Error ? err.message : 'Failed to fetch analysis');
        } finally {
            setLoading(false);
        }
    }, [type, ticker, sector]);

    const typeLabels: Record<string, { title: string; icon: React.ReactNode; color: string }> = {
        weekly: {
            title: 'Weekly AI Outlook',
            icon: <Calendar className="w-5 h-5" />,
            color: 'blue'
        },
        monthly: {
            title: 'Monthly AI Thesis',
            icon: <BarChart2 className="w-5 h-5" />,
            color: 'purple'
        },
        seasonality: {
            title: 'Seasonality AI Insights',
            icon: <Sparkles className="w-5 h-5" />,
            color: 'indigo'
        },
    };

    const config = typeLabels[type];
    const stance = data?.analysis_type === 'weekly'
        ? (data as WeeklyAnalysis).synthesis?.weekly_stance
        : data?.analysis_type === 'monthly'
            ? (data as MonthlyAnalysis).synthesis?.market_stance
            : data?.analysis_type === 'seasonality'
                ? (data as SeasonalityAnalysis).synthesis?.seasonality_verdict
                : undefined;

    return (
        <div className={`border border-${config.color}-200 dark:border-${config.color}-800 rounded-lg overflow-hidden bg-white dark:bg-gray-900`}>
            {/* Header */}
            <div className={`flex items-center justify-between p-4 bg-${config.color}-50 dark:bg-${config.color}-900/20`}>
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-${config.color}-100 dark:bg-${config.color}-800`}>
                        {config.icon}
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                            {config.title}
                        </h3>
                        {data?.observability?.duration_seconds && (
                            <div className="flex items-center gap-2 text-xs text-gray-500">
                                <Clock className="w-3 h-3" />
                                {data.observability.duration_seconds.toFixed(1)}s
                                {data.observability.total_cost_usd && (
                                    <>
                                        <DollarSign className="w-3 h-3 ml-2" />
                                        ${data.observability.total_cost_usd.toFixed(4)}
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {stance && <StanceBadge stance={stance} />}

                    <button
                        onClick={fetchAnalysis}
                        disabled={loading}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg bg-${config.color}-600 hover:bg-${config.color}-700 text-white font-medium transition-colors disabled:opacity-50`}
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-4 h-4" />
                                {data ? 'Refresh' : 'Generate'}
                            </>
                        )}
                    </button>

                    {data && (
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        >
                            {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                        </button>
                    )}
                </div>
            </div>

            {/* Error state */}
            {error && (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300">
                    <div className="flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        {error}
                    </div>
                </div>
            )}

            {/* Content */}
            {isExpanded && data && (
                <div className="p-4">
                    {data.analysis_type === 'weekly' && <WeeklyAnalysisView data={data as WeeklyAnalysis} />}
                    {data.analysis_type === 'monthly' && <MonthlyAnalysisView data={data as MonthlyAnalysis} />}
                    {data.analysis_type === 'seasonality' && <SeasonalityAnalysisView data={data as SeasonalityAnalysis} />}
                </div>
            )}

            {/* Loading state */}
            {loading && !data && (
                <div className="p-8 flex flex-col items-center justify-center text-gray-500">
                    <Loader2 className="w-8 h-8 animate-spin mb-2" />
                    <p className="text-sm">Running AI analysis...</p>
                    <p className="text-xs text-gray-400 mt-1">This may take 30-60 seconds</p>
                </div>
            )}

            {/* Empty state */}
            {!loading && !data && !error && (
                <div className="p-8 text-center text-gray-500">
                    <Cpu className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                    <p className="text-sm">Click &quot;Generate&quot; to run AI analysis</p>
                    <p className="text-xs text-gray-400 mt-1">Multiple specialized agents will analyze the market</p>
                </div>
            )}
        </div>
    );
}
