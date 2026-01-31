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

// Render weekly analysis
function WeeklyAnalysisView({ data }: { data: WeeklyAnalysis }) {
    const { agent_analyses, synthesis } = data;
    
    return (
        <div className="space-y-4">
            {/* Headline */}
            {synthesis?.headline && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <p className="text-lg font-medium text-blue-800 dark:text-blue-200">
                        {synthesis.headline}
                    </p>
                </div>
            )}
            
            {/* Key Insights */}
            {synthesis?.key_insights && synthesis.key_insights.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Zap className="w-4 h-4 text-yellow-500" />
                        Key Insights
                    </h4>
                    <ul className="space-y-1">
                        {synthesis.key_insights.map((insight, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                                <span className="text-blue-500 mt-1">•</span>
                                {insight}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            
            {/* Sector Focus */}
            {synthesis?.sector_focus && (
                <div className="grid grid-cols-2 gap-4">
                    {synthesis.sector_focus.buy && synthesis.sector_focus.buy.length > 0 && (
                        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                            <h5 className="text-sm font-medium text-green-700 dark:text-green-400 mb-2">
                                Sectors to Accumulate
                            </h5>
                            <div className="flex flex-wrap gap-1">
                                {synthesis.sector_focus.buy.map((sector, i) => (
                                    <span key={i} className="px-2 py-0.5 bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200 text-xs rounded">
                                        {sector}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                    {synthesis.sector_focus.avoid && synthesis.sector_focus.avoid.length > 0 && (
                        <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                            <h5 className="text-sm font-medium text-red-700 dark:text-red-400 mb-2">
                                Sectors to Avoid
                            </h5>
                            <div className="flex flex-wrap gap-1">
                                {synthesis.sector_focus.avoid.map((sector, i) => (
                                    <span key={i} className="px-2 py-0.5 bg-red-100 dark:bg-red-800 text-red-800 dark:text-red-200 text-xs rounded">
                                        {sector}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
            
            {/* Agent Details */}
            <div className="space-y-3 mt-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100">Agent Analyses</h4>
                
                {agent_analyses?.trend && (
                    <AgentCard 
                        title="Trend Analysis" 
                        icon={<TrendingUp className="w-4 h-4 text-blue-500" />}
                        confidence={agent_analyses.trend.confidence}
                    >
                        <p><strong>Primary Trend:</strong> {agent_analyses.trend.primary_trend}</p>
                        <p><strong>Trend Strength:</strong> {agent_analyses.trend.trend_strength}</p>
                        <p>{agent_analyses.trend.weekly_outlook}</p>
                    </AgentCard>
                )}
                
                {agent_analyses?.sector_rotation && (
                    <AgentCard 
                        title="Sector Rotation" 
                        icon={<BarChart2 className="w-4 h-4 text-purple-500" />}
                        confidence={agent_analyses.sector_rotation.confidence}
                    >
                        <p><strong>Rotation Direction:</strong> {agent_analyses.sector_rotation.rotation_direction}</p>
                        <p><strong>Leading:</strong> {agent_analyses.sector_rotation.leading_sectors?.join(', ')}</p>
                        <p><strong>Lagging:</strong> {agent_analyses.sector_rotation.lagging_sectors?.join(', ')}</p>
                        <p>{agent_analyses.sector_rotation.sector_outlook}</p>
                    </AgentCard>
                )}
                
                {agent_analyses?.risk_regime && (
                    <AgentCard 
                        title="Risk Assessment" 
                        icon={<Shield className="w-4 h-4 text-orange-500" />}
                        confidence={agent_analyses.risk_regime.confidence}
                    >
                        <p><strong>Risk Regime:</strong> {agent_analyses.risk_regime.risk_regime}</p>
                        <p><strong>VIX Signal:</strong> {agent_analyses.risk_regime.vix_signal}</p>
                        <p><strong>Market Breadth:</strong> {agent_analyses.risk_regime.market_breadth}</p>
                        <p>{agent_analyses.risk_regime.risk_adjusted_advice}</p>
                    </AgentCard>
                )}
            </div>
            
            {/* Risk Guidance */}
            {synthesis?.risk_guidance && (
                <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <h5 className="text-sm font-medium text-yellow-700 dark:text-yellow-400 mb-1 flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        Risk Management
                    </h5>
                    <p className="text-sm text-yellow-800 dark:text-yellow-200">{synthesis.risk_guidance}</p>
                </div>
            )}
            
            {/* Events to Watch */}
            {synthesis?.events_to_watch && synthesis.events_to_watch.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        Events to Watch
                    </h4>
                    <div className="flex flex-wrap gap-2">
                        {synthesis.events_to_watch.map((event, i) => (
                            <span key={i} className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded">
                                {event}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

// Render monthly analysis
function MonthlyAnalysisView({ data }: { data: MonthlyAnalysis }) {
    const { agent_analyses, synthesis } = data;
    
    return (
        <div className="space-y-4">
            {/* Monthly Thesis */}
            {synthesis?.monthly_thesis && (
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                    <h4 className="font-medium text-purple-800 dark:text-purple-200 mb-2">Investment Thesis</h4>
                    <p className="text-sm text-purple-700 dark:text-purple-300">
                        {synthesis.monthly_thesis}
                    </p>
                </div>
            )}
            
            {/* Asset Allocation */}
            {synthesis?.asset_allocation && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Target className="w-4 h-4 text-blue-500" />
                        Recommended Asset Allocation
                    </h4>
                    <div className="grid grid-cols-4 gap-2">
                        {Object.entries(synthesis.asset_allocation).map(([asset, allocation]) => (
                            <div key={asset} className="p-2 bg-gray-100 dark:bg-gray-700 rounded text-center">
                                <div className="text-lg font-bold text-gray-900 dark:text-gray-100">{allocation}</div>
                                <div className="text-xs text-gray-500 capitalize">{asset}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            
            {/* Themes */}
            <div className="grid grid-cols-2 gap-4">
                {synthesis?.top_themes && synthesis.top_themes.length > 0 && (
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <h5 className="text-sm font-medium text-green-700 dark:text-green-400 mb-2">
                            Top Themes
                        </h5>
                        <ul className="space-y-1">
                            {synthesis.top_themes.map((theme, i) => (
                                <li key={i} className="text-sm text-green-800 dark:text-green-200 flex items-start gap-2">
                                    <span className="text-green-500">✓</span>
                                    {theme}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
                {synthesis?.avoid_themes && synthesis.avoid_themes.length > 0 && (
                    <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                        <h5 className="text-sm font-medium text-red-700 dark:text-red-400 mb-2">
                            Avoid These
                        </h5>
                        <ul className="space-y-1">
                            {synthesis.avoid_themes.map((theme, i) => (
                                <li key={i} className="text-sm text-red-800 dark:text-red-200 flex items-start gap-2">
                                    <span className="text-red-500">✗</span>
                                    {theme}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
            
            {/* Agent Details */}
            <div className="space-y-3 mt-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100">Agent Analyses</h4>
                
                {agent_analyses?.macro_cycle && (
                    <AgentCard 
                        title="Macro Cycle" 
                        icon={<BarChart2 className="w-4 h-4 text-blue-500" />}
                        confidence={agent_analyses.macro_cycle.confidence}
                    >
                        <p><strong>Economic Phase:</strong> {agent_analyses.macro_cycle.economic_cycle_phase}</p>
                        <p><strong>Inflation:</strong> {agent_analyses.macro_cycle.inflation_outlook}</p>
                        <p><strong>RBI Bias:</strong> {agent_analyses.macro_cycle.rbi_policy_bias}</p>
                        <p>{agent_analyses.macro_cycle.monthly_macro_outlook}</p>
                    </AgentCard>
                )}
                
                {agent_analyses?.fund_flows && (
                    <AgentCard 
                        title="Fund Flows" 
                        icon={<DollarSign className="w-4 h-4 text-green-500" />}
                        confidence={agent_analyses.fund_flows.confidence}
                    >
                        <p><strong>FII Stance:</strong> {agent_analyses.fund_flows.fii_stance}</p>
                        <p><strong>DII Stance:</strong> {agent_analyses.fund_flows.dii_stance}</p>
                        <p><strong>Consensus:</strong> {agent_analyses.fund_flows.institutional_consensus}</p>
                        <p>{agent_analyses.fund_flows.flow_outlook}</p>
                    </AgentCard>
                )}
                
                {agent_analyses?.valuations && (
                    <AgentCard 
                        title="Valuations" 
                        icon={<Target className="w-4 h-4 text-purple-500" />}
                        confidence={agent_analyses.valuations.confidence}
                    >
                        <p><strong>Market Valuation:</strong> {agent_analyses.valuations.market_valuation}</p>
                        <p><strong>P/E Percentile:</strong> {agent_analyses.valuations.pe_percentile}</p>
                        <p>{agent_analyses.valuations.valuation_advice}</p>
                    </AgentCard>
                )}
            </div>
            
            {/* Key Risks */}
            {synthesis?.key_risks && synthesis.key_risks.length > 0 && (
                <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <h5 className="text-sm font-medium text-yellow-700 dark:text-yellow-400 mb-2 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        Key Risks
                    </h5>
                    <ul className="space-y-1">
                        {synthesis.key_risks.map((risk, i) => (
                            <li key={i} className="text-sm text-yellow-800 dark:text-yellow-200 flex items-start gap-2">
                                <span className="text-yellow-500">⚠</span>
                                {risk}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            
            {/* Action Items */}
            {synthesis?.action_items && synthesis.action_items.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Zap className="w-4 h-4 text-blue-500" />
                        Action Items
                    </h4>
                    <ul className="space-y-1">
                        {synthesis.action_items.map((action, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                                <span className="text-blue-500 font-bold">{i + 1}.</span>
                                {action}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

// Render seasonality analysis
function SeasonalityAnalysisView({ data }: { data: SeasonalityAnalysis }) {
    const { agent_analyses, synthesis, current_month } = data;
    
    return (
        <div className="space-y-4">
            {/* Seasonality Verdict */}
            {synthesis?.actionable_insight && (
                <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-indigo-600 dark:text-indigo-400">
                            {current_month} Seasonality
                        </span>
                        {synthesis.probability_of_positive_month && (
                            <span className="text-sm font-medium text-indigo-700 dark:text-indigo-300">
                                {synthesis.probability_of_positive_month} probability of positive month
                            </span>
                        )}
                    </div>
                    <p className="text-sm text-indigo-700 dark:text-indigo-300">
                        {synthesis.actionable_insight}
                    </p>
                </div>
            )}
            
            {/* Seasonal Alpha */}
            {synthesis?.seasonal_alpha_opportunity && (
                <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                    <h5 className="text-sm font-medium text-green-700 dark:text-green-400 mb-1 flex items-center gap-2">
                        <Sparkles className="w-4 h-4" />
                        Alpha Opportunity
                    </h5>
                    <p className="text-sm text-green-800 dark:text-green-200">{synthesis.seasonal_alpha_opportunity}</p>
                </div>
            )}
            
            {/* Sector Positioning */}
            {synthesis?.sector_positioning && (
                <div className="grid grid-cols-2 gap-4">
                    {synthesis.sector_positioning.overweight && synthesis.sector_positioning.overweight.length > 0 && (
                        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                            <h5 className="text-sm font-medium text-green-700 dark:text-green-400 mb-2">
                                Overweight (Seasonal Tailwinds)
                            </h5>
                            <div className="flex flex-wrap gap-1">
                                {synthesis.sector_positioning.overweight.map((sector, i) => (
                                    <span key={i} className="px-2 py-0.5 bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200 text-xs rounded">
                                        {sector}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                    {synthesis.sector_positioning.underweight && synthesis.sector_positioning.underweight.length > 0 && (
                        <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                            <h5 className="text-sm font-medium text-red-700 dark:text-red-400 mb-2">
                                Underweight (Seasonal Headwinds)
                            </h5>
                            <div className="flex flex-wrap gap-1">
                                {synthesis.sector_positioning.underweight.map((sector, i) => (
                                    <span key={i} className="px-2 py-0.5 bg-red-100 dark:bg-red-800 text-red-800 dark:text-red-200 text-xs rounded">
                                        {sector}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
            
            {/* Event Opportunities */}
            {synthesis?.event_opportunities && synthesis.event_opportunities.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-purple-500" />
                        Event-Driven Opportunities
                    </h4>
                    <div className="flex flex-wrap gap-2">
                        {synthesis.event_opportunities.map((opp, i) => (
                            <span key={i} className="px-2 py-1 bg-purple-100 dark:bg-purple-800 text-purple-700 dark:text-purple-200 text-sm rounded">
                                {opp}
                            </span>
                        ))}
                    </div>
                </div>
            )}
            
            {/* Agent Details */}
            <div className="space-y-3 mt-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100">Agent Analyses</h4>
                
                {agent_analyses?.historical_patterns && (
                    <AgentCard 
                        title="Historical Patterns" 
                        icon={<BarChart2 className="w-4 h-4 text-blue-500" />}
                        confidence={agent_analyses.historical_patterns.confidence}
                    >
                        <p><strong>Avg Return:</strong> {agent_analyses.historical_patterns.historical_avg_return}</p>
                        <p><strong>Win Rate:</strong> {agent_analyses.historical_patterns.historical_win_rate}</p>
                        <p><strong>Pattern Strength:</strong> {agent_analyses.historical_patterns.pattern_strength}</p>
                        <p><strong>Signal:</strong> {agent_analyses.historical_patterns.seasonality_signal}</p>
                    </AgentCard>
                )}
                
                {agent_analyses?.event_calendar && (
                    <AgentCard 
                        title="Event Calendar" 
                        icon={<Calendar className="w-4 h-4 text-purple-500" />}
                        confidence={agent_analyses.event_calendar.confidence}
                    >
                        {agent_analyses.event_calendar.upcoming_events?.map((event, i) => (
                            <div key={i} className="flex items-center justify-between py-1 border-b border-gray-200 dark:border-gray-700 last:border-0">
                                <span>{event.event}</span>
                                <span className={`px-2 py-0.5 rounded text-xs ${
                                    event.expected_impact === 'bullish' ? 'bg-green-100 text-green-700' :
                                    event.expected_impact === 'bearish' ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-700'
                                }`}>
                                    {event.expected_impact}
                                </span>
                            </div>
                        ))}
                        <p className="mt-2">{agent_analyses.event_calendar.event_based_outlook}</p>
                    </AgentCard>
                )}
                
                {agent_analyses?.sector_seasonality && (
                    <AgentCard 
                        title="Sector Seasonality" 
                        icon={<TrendingUp className="w-4 h-4 text-green-500" />}
                        confidence={agent_analyses.sector_seasonality.confidence}
                    >
                        <p><strong>Top Picks:</strong> {agent_analyses.sector_seasonality.top_seasonal_picks?.join(', ')}</p>
                        <p><strong>Avoid:</strong> {agent_analyses.sector_seasonality.sectors_to_avoid_seasonally?.join(', ')}</p>
                    </AgentCard>
                )}
            </div>
            
            {/* Seasonal Risks */}
            {synthesis?.seasonal_risks && synthesis.seasonal_risks.length > 0 && (
                <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <h5 className="text-sm font-medium text-yellow-700 dark:text-yellow-400 mb-2 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        Seasonal Risks
                    </h5>
                    <ul className="space-y-1">
                        {synthesis.seasonal_risks.map((risk, i) => (
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
            const params = new URLSearchParams({ type });
            if (ticker) params.set('ticker', ticker);
            if (sector) params.set('sector', sector);
            
            const response = await fetch(`/api/ai-outlook?${params.toString()}`);
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            setData(result);
            setIsExpanded(true);
            
        } catch (err) {
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
