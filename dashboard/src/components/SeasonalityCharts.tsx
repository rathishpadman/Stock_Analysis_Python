'use client';

import React, { useMemo } from 'react';
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Cell,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    ReferenceLine
} from 'recharts';
import { Calendar, TrendingUp, TrendingDown, Sun, Snowflake } from 'lucide-react';

interface SeasonalityData {
    ticker: string;
    company_name?: string;
    jan_avg?: number;
    feb_avg?: number;
    mar_avg?: number;
    apr_avg?: number;
    may_avg?: number;
    jun_avg?: number;
    jul_avg?: number;
    aug_avg?: number;
    sep_avg?: number;
    oct_avg?: number;
    nov_avg?: number;
    dec_avg?: number;
    best_month?: string;
    worst_month?: string;
}

interface SeasonalityChartProps {
    data: SeasonalityData;
    ticker: string;
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const MONTH_FIELDS = ['jan_avg', 'feb_avg', 'mar_avg', 'apr_avg', 'may_avg', 'jun_avg', 'jul_avg', 'aug_avg', 'sep_avg', 'oct_avg', 'nov_avg', 'dec_avg'];

// Monthly Seasonality Bar Chart
export function SeasonalityBarChart({ data, ticker }: SeasonalityChartProps) {
    const chartData = useMemo(() => {
        return MONTHS.map((month, index) => ({
            month,
            value: Number(data[MONTH_FIELDS[index] as keyof SeasonalityData]) || 0,
            isBest: data.best_month?.toLowerCase() === month.toLowerCase(),
            isWorst: data.worst_month?.toLowerCase() === month.toLowerCase(),
            isCurrentMonth: new Date().getMonth() === index,
        }));
    }, [data]);

    if (!data) {
        return (
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 h-[300px] flex items-center justify-center">
                <p className="text-slate-500 text-sm">No seasonality data available</p>
            </div>
        );
    }

    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-blue-500" />
                    Monthly Seasonality Pattern
                </h3>
                <div className="flex gap-3 text-[10px]">
                    <span className="flex items-center gap-1"><span className="w-3 h-3 bg-emerald-500 rounded"></span>Best</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-3 bg-rose-500 rounded"></span>Worst</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-3 bg-blue-500 rounded"></span>Current</span>
                </div>
            </div>
            <ResponsiveContainer width="100%" height={280}>
                <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis
                        dataKey="month"
                        tick={{ fill: '#64748b', fontSize: 11 }}
                        tickLine={false}
                        axisLine={{ stroke: '#334155' }}
                    />
                    <YAxis
                        tick={{ fill: '#64748b', fontSize: 10 }}
                        tickLine={false}
                        axisLine={{ stroke: '#334155' }}
                        tickFormatter={(value) => `${value}%`}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                        formatter={(value) => [`${(value as number)?.toFixed(2) ?? '-'}%`, 'Avg Return']}
                    />
                    <ReferenceLine y={0} stroke="#64748b" />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {chartData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={
                                    entry.isBest ? '#22c55e' :
                                    entry.isWorst ? '#ef4444' :
                                    entry.isCurrentMonth ? '#3b82f6' :
                                    entry.value >= 0 ? '#10b981' : '#f43f5e'
                                }
                                stroke={entry.isCurrentMonth ? '#60a5fa' : 'transparent'}
                                strokeWidth={entry.isCurrentMonth ? 2 : 0}
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

// Radar Chart for Seasonality
export function SeasonalityRadarChart({ data, ticker }: SeasonalityChartProps) {
    const chartData = useMemo(() => {
        return MONTHS.map((month, index) => ({
            month,
            value: Number(data[MONTH_FIELDS[index] as keyof SeasonalityData]) || 0,
            // Normalize for radar display (shift negative to positive range)
            normalized: (Number(data[MONTH_FIELDS[index] as keyof SeasonalityData]) || 0) + 10,
        }));
    }, [data]);

    if (!data) {
        return (
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 h-[300px] flex items-center justify-center">
                <p className="text-slate-500 text-sm">No seasonality data available</p>
            </div>
        );
    }

    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2">
                    <Sun className="h-4 w-4 text-amber-500" />
                    Seasonality Radar
                </h3>
            </div>
            <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={chartData}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis
                        dataKey="month"
                        tick={{ fill: '#94a3b8', fontSize: 10 }}
                    />
                    <PolarRadiusAxis
                        angle={30}
                        domain={[0, 20]}
                        tick={{ fill: '#64748b', fontSize: 8 }}
                        tickFormatter={(value) => `${value - 10}%`}
                    />
                    <Radar
                        name="Avg Return"
                        dataKey="normalized"
                        stroke="#3b82f6"
                        fill="#3b82f6"
                        fillOpacity={0.3}
                        strokeWidth={2}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                        formatter={(value, name, props) => [`${props.payload.value?.toFixed(2)}%`, 'Avg Return']}
                    />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
}

// Quarterly Breakdown
export function QuarterlyBreakdown({ data, ticker }: SeasonalityChartProps) {
    const quarters = useMemo(() => {
        const q1 = ((Number(data.jan_avg) || 0) + (Number(data.feb_avg) || 0) + (Number(data.mar_avg) || 0)) / 3;
        const q2 = ((Number(data.apr_avg) || 0) + (Number(data.may_avg) || 0) + (Number(data.jun_avg) || 0)) / 3;
        const q3 = ((Number(data.jul_avg) || 0) + (Number(data.aug_avg) || 0) + (Number(data.sep_avg) || 0)) / 3;
        const q4 = ((Number(data.oct_avg) || 0) + (Number(data.nov_avg) || 0) + (Number(data.dec_avg) || 0)) / 3;

        return [
            { quarter: 'Q1 (Jan-Mar)', value: q1, months: 'Jan, Feb, Mar' },
            { quarter: 'Q2 (Apr-Jun)', value: q2, months: 'Apr, May, Jun' },
            { quarter: 'Q3 (Jul-Sep)', value: q3, months: 'Jul, Aug, Sep' },
            { quarter: 'Q4 (Oct-Dec)', value: q4, months: 'Oct, Nov, Dec' },
        ];
    }, [data]);

    const bestQuarter = quarters.reduce((a, b) => a.value > b.value ? a : b);
    const worstQuarter = quarters.reduce((a, b) => a.value < b.value ? a : b);

    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
            <h3 className="text-sm font-bold text-slate-300 mb-4">Quarterly Performance</h3>
            <div className="grid grid-cols-4 gap-3">
                {quarters.map((q, index) => (
                    <div
                        key={q.quarter}
                        className={`p-3 rounded-lg border ${
                            q === bestQuarter ? 'border-emerald-500/50 bg-emerald-500/10' :
                            q === worstQuarter ? 'border-rose-500/50 bg-rose-500/10' :
                            'border-slate-700 bg-slate-800/50'
                        }`}
                    >
                        <div className="text-[10px] text-slate-500 uppercase mb-1">{q.quarter}</div>
                        <div className={`text-xl font-bold ${q.value >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                            {q.value >= 0 ? '+' : ''}{q.value.toFixed(2)}%
                        </div>
                        <div className="text-[9px] text-slate-600">{q.months}</div>
                        {q === bestQuarter && <span className="text-[9px] text-emerald-400 mt-1 block">Best Quarter</span>}
                        {q === worstQuarter && <span className="text-[9px] text-rose-400 mt-1 block">Worst Quarter</span>}
                    </div>
                ))}
            </div>
        </div>
    );
}

// Seasonality Stats Summary
export function SeasonalityStats({ data, ticker }: SeasonalityChartProps) {
    const stats = useMemo(() => {
        const monthlyReturns = MONTH_FIELDS.map(field => Number(data[field as keyof SeasonalityData]) || 0);
        const positiveMonths = monthlyReturns.filter(r => r > 0).length;
        const negativeMonths = monthlyReturns.filter(r => r < 0).length;
        const avgReturn = monthlyReturns.reduce((a, b) => a + b, 0) / 12;
        const annualizedReturn = monthlyReturns.reduce((a, b) => a + b, 0);
        const bestReturn = Math.max(...monthlyReturns);
        const worstReturn = Math.min(...monthlyReturns);
        const volatility = Math.sqrt(monthlyReturns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / 12);

        // Current month outlook
        const currentMonthIndex = new Date().getMonth();
        const currentMonthAvg = monthlyReturns[currentMonthIndex];

        // Next 3 months outlook
        const next3Months = [0, 1, 2].map(i => monthlyReturns[(currentMonthIndex + i + 1) % 12]);
        const next3MonthsAvg = next3Months.reduce((a, b) => a + b, 0) / 3;

        return {
            positiveMonths,
            negativeMonths,
            avgReturn,
            annualizedReturn,
            bestReturn,
            worstReturn,
            volatility,
            currentMonthAvg,
            currentMonthName: MONTHS[currentMonthIndex],
            next3MonthsAvg,
            bestMonth: data.best_month,
            worstMonth: data.worst_month,
        };
    }, [data]);

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Best Month</div>
                <div className="text-lg font-bold text-emerald-500">{stats.bestMonth}</div>
                <div className="text-[10px] text-slate-400">+{stats.bestReturn?.toFixed(2)}% avg</div>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Worst Month</div>
                <div className="text-lg font-bold text-rose-500">{stats.worstMonth}</div>
                <div className="text-[10px] text-slate-400">{stats.worstReturn?.toFixed(2)}% avg</div>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Positive Months</div>
                <div className="text-lg font-bold text-blue-500">{stats.positiveMonths}/12</div>
                <div className="text-[10px] text-slate-400">{((stats.positiveMonths / 12) * 100).toFixed(0)}% win rate</div>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Avg Monthly</div>
                <div className={`text-lg font-bold ${stats.avgReturn >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                    {stats.avgReturn >= 0 ? '+' : ''}{stats.avgReturn?.toFixed(2)}%
                </div>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">{stats.currentMonthName} Outlook</div>
                <div className={`text-lg font-bold ${stats.currentMonthAvg >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                    {stats.currentMonthAvg >= 0 ? '+' : ''}{stats.currentMonthAvg?.toFixed(2)}%
                </div>
                <div className="text-[10px] text-slate-400">current month</div>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Next 3M Outlook</div>
                <div className={`text-lg font-bold ${stats.next3MonthsAvg >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                    {stats.next3MonthsAvg >= 0 ? '+' : ''}{stats.next3MonthsAvg?.toFixed(2)}%
                </div>
                <div className="text-[10px] text-slate-400">avg/month</div>
            </div>
        </div>
    );
}
