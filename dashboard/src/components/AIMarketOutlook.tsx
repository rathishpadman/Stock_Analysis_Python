'use client';

import React, { useState, useCallback } from 'react';
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
    Cpu
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
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const syn = synthesis as Record<string, any> || {};
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const agents = agent_analyses as Record<string, any> || {};
    
    return (
        <div className="space-y-4">
            {/* Executive Summary / Headline */}
            {(syn.executive_summary || syn.headline || syn.weekly_thesis) && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
                        {syn.executive_summary?.headline || syn.headline || 'Weekly Outlook'}
                    </h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                        {syn.executive_summary?.one_liner || syn.weekly_thesis?.narrative || syn.executive_summary?.narrative || ''}
                    </p>
                    {syn.executive_summary?.conviction_score !== undefined && (
                        <div className="mt-2 flex items-center gap-2">
                            <span className="text-xs text-blue-600">Conviction:</span>
                            <ConfidenceMeter value={syn.executive_summary.conviction_score / 10} />
                        </div>
                    )}
                </div>
            )}

            {/* Top Actionable Ideas */}
            {syn.top_3_actionable_ideas && syn.top_3_actionable_ideas.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Target className="w-4 h-4 text-green-500" />
                        Top Actionable Ideas
                    </h4>
                    <div className="grid gap-2">
                        {syn.top_3_actionable_ideas.map((idea: Record<string, unknown>, i: number) => (
                            <div key={i} className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="font-medium text-green-800 dark:text-green-200">
                                        #{String(idea.rank ?? i + 1)} {String(idea.type ?? '')} - {String(idea.name ?? idea.sector ?? '')}
                                    </span>
                                    {idea.risk_reward != null && (
                                        <span className="text-xs px-2 py-0.5 bg-green-200 dark:bg-green-800 rounded">
                                            R:R {String(idea.risk_reward)}
                                        </span>
                                    )}
                                </div>
                                <p className="text-sm text-green-700 dark:text-green-300">{String(idea.rationale ?? idea.action ?? '')}</p>
                                {(idea.entry_zone != null || idea.stop_loss_pct != null || idea.target_pct != null) && (
                                    <div className="mt-2 flex flex-wrap gap-3 text-xs">
                                        {idea.entry_zone != null && <span>Entry: {formatPriceRange(idea.entry_zone)}</span>}
                                        {idea.stop_loss_pct != null && <span className="text-red-600">SL: {String(idea.stop_loss_pct)}%</span>}
                                        {idea.target_pct != null && <span className="text-green-600">Target: {String(idea.target_pct)}%</span>}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Sector Allocation */}
            {syn.sector_allocation && syn.sector_allocation.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <BarChart2 className="w-4 h-4 text-purple-500" />
                        Sector Allocation
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                        {syn.sector_allocation.map((sec: Record<string, unknown>, i: number) => (
                            <div key={i} className={`p-2 rounded border ${
                                sec.stance === 'overweight' ? 'bg-green-50 dark:bg-green-900/20 border-green-200' :
                                sec.stance === 'underweight' ? 'bg-red-50 dark:bg-red-900/20 border-red-200' :
                                'bg-gray-50 dark:bg-gray-800 border-gray-200'
                            }`}>
                                <div className="font-medium text-sm">{String(sec.sector || '')}</div>
                                <div className="text-xs text-gray-500">{String(sec.stance || '')} ({String(sec.weight_pct || 0)}%)</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Risk Management */}
            {syn.risk_management && (
                <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <h5 className="text-sm font-medium text-yellow-700 dark:text-yellow-400 mb-2 flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        Risk Management
                    </h5>
                    <div className="text-sm text-yellow-800 dark:text-yellow-200 space-y-1">
                        {syn.risk_management.position_sizing && (
                            <p>Position Size: {syn.risk_management.position_sizing.recommendation}</p>
                        )}
                        {syn.risk_management.stop_loss_guidance && (
                            <p>Stop Loss: {syn.risk_management.stop_loss_guidance.index_stop_loss}</p>
                        )}
                        {syn.risk_management.hedging && (
                            <p>Hedge: {syn.risk_management.hedging.recommendation}</p>
                        )}
                    </div>
                </div>
            )}

            {/* Events Calendar */}
            {syn.events_calendar && syn.events_calendar.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        Events This Week
                    </h4>
                    <div className="flex flex-wrap gap-2">
                        {syn.events_calendar.map((event: Record<string, unknown>, i: number) => (
                            <span key={i} className={`px-2 py-1 text-sm rounded ${
                                event.expected_impact === 'bullish' ? 'bg-green-100 text-green-800' :
                                event.expected_impact === 'bearish' ? 'bg-red-100 text-red-800' :
                                'bg-gray-100 text-gray-800'
                            }`}>
                                {String(event.date || '')} - {String(event.event || '')}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Monday Checklist */}
            {syn.monday_checklist && syn.monday_checklist.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Zap className="w-4 h-4 text-yellow-500" />
                        Monday Checklist
                    </h4>
                    <ul className="space-y-1">
                        {syn.monday_checklist.map((item: string, i: number) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                                <span className="text-blue-500 mt-1">☐</span>
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Agent Details - Dynamic rendering */}
            <div className="space-y-3 mt-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100">Agent Analyses</h4>
                
                {agents.trend && (
                    <DataSection 
                        title="Trend Analysis" 
                        data={agents.trend}
                        icon={<TrendingUp className="w-4 h-4 text-blue-500" />}
                    />
                )}
                
                {agents.sector_rotation && (
                    <DataSection 
                        title="Sector Rotation" 
                        data={typeof agents.sector_rotation === 'object' && !agents.sector_rotation.raw_response 
                            ? agents.sector_rotation 
                            : { summary: 'See detailed sector data above' }}
                        icon={<BarChart2 className="w-4 h-4 text-purple-500" />}
                    />
                )}
                
                {agents.risk_regime && (
                    <DataSection 
                        title="Risk Assessment" 
                        data={agents.risk_regime}
                        icon={<Shield className="w-4 h-4 text-orange-500" />}
                    />
                )}
            </div>

            {/* Fallback: Legacy format key_insights */}
            {syn.key_insights && syn.key_insights.length > 0 && (
                <div className="space-y-2">
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
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const syn = synthesis as Record<string, any> || {};
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const agents = agent_analyses as Record<string, any> || {};
    
    return (
        <div className="space-y-4">
            {/* Monthly Thesis - new format */}
            {(syn.monthly_thesis?.headline || syn.monthly_thesis) && (
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                    <h4 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">
                        {syn.monthly_thesis?.headline || 'Investment Thesis'}
                    </h4>
                    <p className="text-sm text-purple-700 dark:text-purple-300">
                        {syn.monthly_thesis?.narrative || (typeof syn.monthly_thesis === 'string' ? syn.monthly_thesis : '')}
                    </p>
                    {syn.monthly_thesis?.conviction_score !== undefined && (
                        <div className="mt-2 flex items-center gap-2">
                            <span className="text-xs text-purple-600">Conviction:</span>
                            <ConfidenceMeter value={syn.monthly_thesis.conviction_score / 10} />
                        </div>
                    )}
                </div>
            )}
            
            {/* Asset Allocation - new format */}
            {syn.asset_allocation && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Target className="w-4 h-4 text-blue-500" />
                        Asset Allocation
                    </h4>
                    <div className="grid grid-cols-4 gap-2">
                        {syn.asset_allocation.equity_pct !== undefined && (
                            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded text-center">
                                <div className="text-lg font-bold text-blue-900 dark:text-blue-100">{syn.asset_allocation.equity_pct}%</div>
                                <div className="text-xs text-blue-600">Equity</div>
                            </div>
                        )}
                        {syn.asset_allocation.debt_pct !== undefined && (
                            <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded text-center">
                                <div className="text-lg font-bold text-gray-900 dark:text-gray-100">{syn.asset_allocation.debt_pct}%</div>
                                <div className="text-xs text-gray-500">Debt</div>
                            </div>
                        )}
                        {syn.asset_allocation.gold_pct !== undefined && (
                            <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded text-center">
                                <div className="text-lg font-bold text-yellow-900 dark:text-yellow-100">{syn.asset_allocation.gold_pct}%</div>
                                <div className="text-xs text-yellow-600">Gold</div>
                            </div>
                        )}
                        {syn.asset_allocation.cash_pct !== undefined && (
                            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded text-center">
                                <div className="text-lg font-bold text-green-900 dark:text-green-100">{syn.asset_allocation.cash_pct}%</div>
                                <div className="text-xs text-green-600">Cash</div>
                            </div>
                        )}
                    </div>
                    {syn.asset_allocation.rationale && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 italic">{syn.asset_allocation.rationale}</p>
                    )}
                </div>
            )}

            {/* Sector Allocation - new format */}
            {syn.sector_allocation && syn.sector_allocation.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <BarChart2 className="w-4 h-4 text-purple-500" />
                        Sector Allocation
                    </h4>
                    <div className="overflow-x-auto">
                        <table className="min-w-full text-sm">
                            <thead>
                                <tr className="bg-gray-50 dark:bg-gray-800">
                                    <th className="px-3 py-2 text-left">Sector</th>
                                    <th className="px-3 py-2 text-center">Weight</th>
                                    <th className="px-3 py-2 text-center">Stance</th>
                                    <th className="px-3 py-2 text-center">Exp. Return</th>
                                </tr>
                            </thead>
                            <tbody>
                                {syn.sector_allocation.map((sec: Record<string, unknown>, i: number) => (
                                    <tr key={i} className="border-b dark:border-gray-700">
                                        <td className="px-3 py-2 font-medium">{String(sec.sector || '')}</td>
                                        <td className="px-3 py-2 text-center">{String(sec.weight_pct || 0)}%</td>
                                        <td className="px-3 py-2 text-center">
                                            <span className={`px-2 py-0.5 rounded text-xs ${
                                                sec.vs_benchmark === 'overweight' ? 'bg-green-100 text-green-700' :
                                                sec.vs_benchmark === 'underweight' ? 'bg-red-100 text-red-700' :
                                                'bg-gray-100 text-gray-700'
                                            }`}>
                                                {String(sec.vs_benchmark || 'neutral')}
                                            </span>
                                        </td>
                                        <td className="px-3 py-2 text-center text-green-600">{String(sec.expected_return_pct || 0)}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Top Monthly Ideas - new format */}
            {syn.top_monthly_ideas && syn.top_monthly_ideas.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Target className="w-4 h-4 text-green-500" />
                        Top Monthly Ideas
                    </h4>
                    <div className="grid gap-2">
                        {syn.top_monthly_ideas.map((idea: Record<string, unknown>, i: number) => (
                            <div key={i} className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="font-medium text-green-800 dark:text-green-200">
                                        #{String(idea.rank ?? i + 1)} {String(idea.type ?? '')} - {String(idea.name ?? '')}
                                    </span>
                                    {idea.risk_reward != null && (
                                        <span className="text-xs px-2 py-0.5 bg-green-200 dark:bg-green-800 rounded">
                                            R:R {String(idea.risk_reward)}
                                        </span>
                                    )}
                                </div>
                                <p className="text-sm text-green-700 dark:text-green-300">{String(idea.rationale ?? '')}</p>
                                <div className="mt-2 flex flex-wrap gap-3 text-xs">
                                    {idea.entry_zone != null && <span>Entry: {JSON.stringify(idea.entry_zone)}</span>}
                                    {idea.stop_loss_pct != null && <span className="text-red-600">SL: {String(idea.stop_loss_pct)}%</span>}
                                    {idea.target_return_pct != null && <span className="text-green-600">Target: {String(idea.target_return_pct)}%</span>}
                                    {idea.holding_period != null && <span>Hold: {String(idea.holding_period)}</span>}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Week by Week Focus - new format */}
            {syn.week_by_week_focus && syn.week_by_week_focus.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-blue-500" />
                        Week-by-Week Focus
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {syn.week_by_week_focus.map((week: Record<string, unknown>, i: number) => (
                            <div key={i} className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
                                <div className="font-medium text-blue-800 dark:text-blue-200 text-sm">Week {String(week.week ?? i + 1)}</div>
                                <div className="text-xs text-blue-600 dark:text-blue-400">{String(week.focus ?? '')}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Risk Dashboard - new format */}
            {syn.risk_dashboard && (
                <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <h5 className="text-sm font-medium text-yellow-700 dark:text-yellow-400 mb-2 flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        Risk Dashboard
                    </h5>
                    <div className="grid grid-cols-3 gap-2 text-sm">
                        {syn.risk_dashboard.portfolio_var_pct !== undefined && (
                            <div className="text-center">
                                <div className="font-bold text-yellow-800">{syn.risk_dashboard.portfolio_var_pct}%</div>
                                <div className="text-xs text-yellow-600">Portfolio VAR</div>
                            </div>
                        )}
                        {syn.risk_dashboard.max_drawdown_expected_pct !== undefined && (
                            <div className="text-center">
                                <div className="font-bold text-red-600">{syn.risk_dashboard.max_drawdown_expected_pct}%</div>
                                <div className="text-xs text-yellow-600">Max Drawdown</div>
                            </div>
                        )}
                        {syn.risk_dashboard.stop_loss_level?.nifty && (
                            <div className="text-center">
                                <div className="font-bold text-yellow-800">{syn.risk_dashboard.stop_loss_level.nifty}</div>
                                <div className="text-xs text-yellow-600">NIFTY Stop</div>
                            </div>
                        )}
                    </div>
                    {syn.risk_dashboard.key_risks && syn.risk_dashboard.key_risks.length > 0 && (
                        <ul className="mt-2 space-y-1">
                            {syn.risk_dashboard.key_risks.map((risk: Record<string, unknown>, i: number) => (
                                <li key={i} className="text-xs text-yellow-800 dark:text-yellow-200">
                                    ⚠ {String(risk.risk ?? risk)} ({String(risk.probability_pct ?? 0)}% prob, {String(risk.impact_pct ?? 0)}% impact)
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}

            {/* Agent Details - Dynamic rendering */}
            <div className="space-y-3 mt-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100">Agent Analyses</h4>
                
                {agents.macro_cycle && (
                    <DataSection 
                        title="Macro Cycle" 
                        data={agents.macro_cycle}
                        icon={<BarChart2 className="w-4 h-4 text-blue-500" />}
                    />
                )}
                
                {agents.fund_flows && (
                    <DataSection 
                        title="Fund Flows" 
                        data={agents.fund_flows}
                        icon={<DollarSign className="w-4 h-4 text-green-500" />}
                    />
                )}
                
                {agents.valuations && (
                    <DataSection 
                        title="Valuations" 
                        data={agents.valuations}
                        icon={<Target className="w-4 h-4 text-purple-500" />}
                    />
                )}
            </div>

            {/* Fallback: Legacy formats */}
            {syn.top_themes && syn.top_themes.length > 0 && (
                <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <h5 className="text-sm font-medium text-green-700 dark:text-green-400 mb-2">Top Themes</h5>
                    <ul className="space-y-1">
                        {syn.top_themes.map((theme: string, i: number) => (
                            <li key={i} className="text-sm text-green-800 dark:text-green-200 flex items-start gap-2">
                                <span className="text-green-500">✓</span>{theme}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

// Render seasonality analysis - handles both old and new formats
function SeasonalityAnalysisView({ data }: { data: SeasonalityAnalysis }) {
    const { agent_analyses, synthesis, current_month } = data;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const syn = synthesis as Record<string, any> || {};
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const agents = agent_analyses as Record<string, any> || {};
    
    return (
        <div className="space-y-4">
            {/* Seasonality Thesis - new format */}
            {(syn.seasonality_thesis || syn.actionable_insight) && (
                <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-indigo-800 dark:text-indigo-200">
                            {syn.seasonality_thesis?.headline || `${current_month} Seasonality`}
                        </span>
                        {(syn.seasonality_thesis?.probability_of_positive_month_pct || syn.probability_of_positive_month) && (
                            <span className="text-sm font-medium px-2 py-0.5 bg-indigo-200 dark:bg-indigo-800 rounded">
                                {syn.seasonality_thesis?.probability_of_positive_month_pct || syn.probability_of_positive_month}% win probability
                            </span>
                        )}
                    </div>
                    <p className="text-sm text-indigo-700 dark:text-indigo-300">
                        {syn.seasonality_thesis?.statistical_backing || syn.actionable_insight || ''}
                    </p>
                    {syn.seasonality_thesis?.expected_return_range_pct && (
                        <p className="text-xs text-indigo-600 mt-1">
                            Expected range: {syn.seasonality_thesis.expected_return_range_pct.low}% to {syn.seasonality_thesis.expected_return_range_pct.high}%
                        </p>
                    )}
                </div>
            )}

            {/* Composite Score - new format */}
            {syn.composite_seasonal_score && (
                <div className="grid grid-cols-4 gap-2">
                    <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-center">
                        <div className="text-lg font-bold text-blue-800">{syn.composite_seasonal_score.historical_pattern_score}</div>
                        <div className="text-xs text-blue-600">Historical</div>
                    </div>
                    <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded text-center">
                        <div className="text-lg font-bold text-purple-800">{syn.composite_seasonal_score.event_calendar_score}</div>
                        <div className="text-xs text-purple-600">Events</div>
                    </div>
                    <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded text-center">
                        <div className="text-lg font-bold text-green-800">{syn.composite_seasonal_score.sector_seasonality_score}</div>
                        <div className="text-xs text-green-600">Sectors</div>
                    </div>
                    <div className="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded text-center border-2 border-indigo-300">
                        <div className="text-lg font-bold text-indigo-800">{syn.composite_seasonal_score.composite_score}</div>
                        <div className="text-xs text-indigo-600">Composite</div>
                    </div>
                </div>
            )}

            {/* Current Month Playbook - new format */}
            {syn.current_month_playbook && (
                <div className="space-y-3">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Zap className="w-4 h-4 text-yellow-500" />
                        Current Month Playbook
                    </h4>
                    
                    {syn.current_month_playbook.primary_strategy && (
                        <p className="text-sm bg-gray-50 dark:bg-gray-800 p-3 rounded">{syn.current_month_playbook.primary_strategy}</p>
                    )}

                    {/* Position Sizing */}
                    {syn.current_month_playbook.position_sizing && (
                        <div className="grid grid-cols-3 gap-2 text-sm">
                            <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded text-center">
                                <div className="font-bold">{syn.current_month_playbook.position_sizing.base_equity_pct}%</div>
                                <div className="text-xs text-gray-500">Base Equity</div>
                            </div>
                            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded text-center">
                                <div className="font-bold text-blue-700">{syn.current_month_playbook.position_sizing.seasonal_adjustment_pct > 0 ? '+' : ''}{syn.current_month_playbook.position_sizing.seasonal_adjustment_pct}%</div>
                                <div className="text-xs text-blue-600">Seasonal Adj</div>
                            </div>
                            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded text-center border-2 border-green-300">
                                <div className="font-bold text-green-700">{syn.current_month_playbook.position_sizing.final_equity_pct}%</div>
                                <div className="text-xs text-green-600">Final Equity</div>
                            </div>
                        </div>
                    )}

                    {/* Sector Tilts */}
                    {syn.current_month_playbook.sector_tilts && syn.current_month_playbook.sector_tilts.length > 0 && (
                        <div className="space-y-1">
                            <h5 className="text-sm font-medium">Sector Tilts</h5>
                            <div className="grid gap-1">
                                {syn.current_month_playbook.sector_tilts.map((tilt: Record<string, unknown>, i: number) => (
                                    <div key={i} className={`p-2 rounded text-sm flex justify-between ${
                                        tilt.action === 'overweight' ? 'bg-green-50' :
                                        tilt.action === 'underweight' ? 'bg-red-50' : 'bg-gray-50'
                                    }`}>
                                        <span className="font-medium">{String(tilt.sector)}</span>
                                        <span>{String(tilt.action)} ({String(tilt.size_pct)}%)</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Event Trades */}
                    {syn.current_month_playbook.event_trades && syn.current_month_playbook.event_trades.length > 0 && (
                        <div className="space-y-2">
                            <h5 className="text-sm font-medium">Event Trades</h5>
                            {syn.current_month_playbook.event_trades.map((trade: Record<string, unknown>, i: number) => (
                                <div key={i} className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded text-sm">
                                    <div className="font-medium">{String(trade.event)}</div>
                                    <div className="text-purple-700">{String(trade.trade)}</div>
                                    <div className="text-xs text-gray-500 mt-1">
                                        {String(trade.entry_date)} → {String(trade.exit_date)} | R:R {String(trade.risk_reward)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Monthly Action Calendar - new format */}
            {syn.monthly_action_calendar && syn.monthly_action_calendar.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-blue-500" />
                        Monthly Calendar
                    </h4>
                    <div className="overflow-x-auto">
                        <table className="min-w-full text-xs">
                            <thead>
                                <tr className="bg-gray-50 dark:bg-gray-800">
                                    <th className="px-2 py-1 text-left">Month</th>
                                    <th className="px-2 py-1 text-center">Bias</th>
                                    <th className="px-2 py-1 text-center">Hist. Return</th>
                                    <th className="px-2 py-1 text-center">Equity %</th>
                                    <th className="px-2 py-1 text-left">Leaders</th>
                                </tr>
                            </thead>
                            <tbody>
                                {syn.monthly_action_calendar.slice(0, 6).map((month: Record<string, unknown>, i: number) => (
                                    <tr key={i} className="border-b dark:border-gray-700">
                                        <td className="px-2 py-1 font-medium">{String(month.month || '')}</td>
                                        <td className="px-2 py-1 text-center">
                                            <span className={`px-1 rounded ${
                                                month.seasonal_bias === 'bullish' ? 'bg-green-100 text-green-700' :
                                                month.seasonal_bias === 'bearish' ? 'bg-red-100 text-red-700' :
                                                'bg-gray-100 text-gray-700'
                                            }`}>
                                                {String(month.seasonal_bias || '')}
                                            </span>
                                        </td>
                                        <td className="px-2 py-1 text-center">{String(month.historical_return_pct || 0)}%</td>
                                        <td className="px-2 py-1 text-center">{String(month.recommended_equity_allocation_pct || 0)}%</td>
                                        <td className="px-2 py-1">{Array.isArray(month.sector_leaders) ? month.sector_leaders.join(', ') : ''}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Bottom Line - new format */}
            {syn.bottom_line && (
                <div className="p-3 bg-blue-100 dark:bg-blue-900/30 border border-blue-300 dark:border-blue-700 rounded-lg">
                    <h5 className="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-1">Bottom Line</h5>
                    <p className="text-sm text-blue-700 dark:text-blue-300">{syn.bottom_line.one_liner}</p>
                    <div className="text-xs text-blue-600 mt-1">
                        Confidence: {syn.bottom_line.confidence} | Horizon: {syn.bottom_line.time_horizon}
                    </div>
                </div>
            )}

            {/* Fallback: Legacy sector positioning */}
            {syn.sector_positioning && (
                <div className="grid grid-cols-2 gap-4">
                    {syn.sector_positioning.overweight && syn.sector_positioning.overweight.length > 0 && (
                        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                            <h5 className="text-sm font-medium text-green-700 dark:text-green-400 mb-2">Overweight</h5>
                            <div className="flex flex-wrap gap-1">
                                {syn.sector_positioning.overweight.map((sector: string, i: number) => (
                                    <span key={i} className="px-2 py-0.5 bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200 text-xs rounded">
                                        {sector}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                    {syn.sector_positioning.underweight && syn.sector_positioning.underweight.length > 0 && (
                        <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                            <h5 className="text-sm font-medium text-red-700 dark:text-red-400 mb-2">Underweight</h5>
                            <div className="flex flex-wrap gap-1">
                                {syn.sector_positioning.underweight.map((sector: string, i: number) => (
                                    <span key={i} className="px-2 py-0.5 bg-red-100 dark:bg-red-800 text-red-800 dark:text-red-200 text-xs rounded">
                                        {sector}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Agent Details - Dynamic rendering */}
            <div className="space-y-3 mt-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100">Agent Analyses</h4>
                
                {agents.historical_patterns && (
                    <DataSection 
                        title="Historical Patterns" 
                        data={agents.historical_patterns}
                        icon={<BarChart2 className="w-4 h-4 text-blue-500" />}
                    />
                )}
                
                {agents.event_calendar && (
                    <DataSection 
                        title="Event Calendar" 
                        data={typeof agents.event_calendar === 'object' && !agents.event_calendar.raw_response 
                            ? agents.event_calendar 
                            : { summary: 'See event details above' }}
                        icon={<Calendar className="w-4 h-4 text-purple-500" />}
                    />
                )}
                
                {agents.sector_seasonality && (
                    <DataSection 
                        title="Sector Seasonality" 
                        data={typeof agents.sector_seasonality === 'object' && !agents.sector_seasonality.raw_response 
                            ? agents.sector_seasonality 
                            : { summary: 'See sector details above' }}
                        icon={<TrendingUp className="w-4 h-4 text-green-500" />}
                    />
                )}
            </div>

            {/* Risk Warnings - new format */}
            {syn.risk_warnings && syn.risk_warnings.length > 0 && (
                <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <h5 className="text-sm font-medium text-yellow-700 dark:text-yellow-400 mb-2 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        Risk Warnings
                    </h5>
                    <ul className="space-y-1">
                        {syn.risk_warnings.map((risk: Record<string, unknown>, i: number) => (
                            <li key={i} className="text-sm text-yellow-800 dark:text-yellow-200">
                                ⚠ {String(risk.risk ?? risk)} {risk.probability_pct != null ? `(${String(risk.probability_pct)}% prob)` : ''}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Fallback: Legacy seasonal_risks */}
            {syn.seasonal_risks && syn.seasonal_risks.length > 0 && !syn.risk_warnings && (
                <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <h5 className="text-sm font-medium text-yellow-700 dark:text-yellow-400 mb-2 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        Seasonal Risks
                    </h5>
                    <ul className="space-y-1">
                        {syn.seasonal_risks.map((risk: string, i: number) => (
                            <li key={i} className="text-sm text-yellow-800 dark:text-yellow-200 flex items-start gap-2">
                                <span className="text-yellow-500">⚠</span>
                                {risk}
                            </li>
                        ))}
                    </ul>
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
