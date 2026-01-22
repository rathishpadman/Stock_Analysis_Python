'use client';

import React, { useMemo } from 'react';
import {
    ResponsiveContainer,
    ComposedChart,
    BarChart,
    LineChart,
    Area,
    Line,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ReferenceLine,
    Cell
} from 'recharts';
import { TrendingUp, TrendingDown, Calendar, BarChart3, Activity } from 'lucide-react';

interface MonthlyDataPoint {
    ticker: string;
    month: string;
    monthly_open?: number;
    monthly_high?: number;
    monthly_low?: number;
    monthly_close?: number;
    monthly_return_pct?: number;
    monthly_volume?: number;
    ytd_return_pct?: number;
    monthly_sma3?: number;
    monthly_sma6?: number;
    monthly_sma12?: number;
    return_3m?: number;
    return_6m?: number;
    return_12m?: number;
    positive_months_12m?: number;
    avg_monthly_return_12m?: number;
    monthly_trend?: string;
}

interface MonthlyChartProps {
    data: MonthlyDataPoint[];
    ticker: string;
}

// Monthly Price Chart with SMA overlays
export function MonthlyPriceChart({ data, ticker }: MonthlyChartProps) {
    const sortedData = useMemo(() => {
        return [...data]
            .sort((a, b) => new Date(a.month).getTime() - new Date(b.month).getTime())
            .slice(-24); // Last 24 months (2 years)
    }, [data]);

    if (!sortedData.length) {
        return (
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 h-[350px] flex items-center justify-center">
                <p className="text-slate-500 text-sm">No monthly price data available</p>
            </div>
        );
    }

    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-blue-500" />
                    Monthly Price (24M)
                </h3>
                <div className="flex gap-3 text-[10px]">
                    <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-blue-500"></span>Close</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-amber-500"></span>SMA 3</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-purple-500"></span>SMA 6</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-emerald-500"></span>SMA 12</span>
                </div>
            </div>
            <ResponsiveContainer width="100%" height={350}>
                <ComposedChart data={sortedData}>
                    <defs>
                        <linearGradient id="monthlyPriceGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis
                        dataKey="month"
                        tick={{ fill: '#64748b', fontSize: 10 }}
                        tickLine={false}
                        axisLine={{ stroke: '#334155' }}
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
                        }}
                    />
                    <YAxis
                        tick={{ fill: '#64748b', fontSize: 10 }}
                        tickLine={false}
                        axisLine={{ stroke: '#334155' }}
                        tickFormatter={(value) => `₹${value}`}
                        domain={['auto', 'auto']}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                        labelFormatter={(label) => `Month: ${label}`}
                        formatter={(value, name) => [
                            `₹${(value as number)?.toFixed(2) ?? '-'}`,
                            name === 'monthly_close' ? 'Close' :
                                name === 'monthly_sma3' ? 'SMA 3' :
                                    name === 'monthly_sma6' ? 'SMA 6' :
                                        name === 'monthly_sma12' ? 'SMA 12' : String(name)
                        ]}
                    />
                    <Area
                        type="monotone"
                        dataKey="monthly_close"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        fill="url(#monthlyPriceGradient)"
                    />
                    <Line
                        type="monotone"
                        dataKey="monthly_sma3"
                        stroke="#f59e0b"
                        strokeWidth={1.5}
                        dot={false}
                        strokeDasharray="3 3"
                    />
                    <Line
                        type="monotone"
                        dataKey="monthly_sma6"
                        stroke="#8b5cf6"
                        strokeWidth={1.5}
                        dot={false}
                        strokeDasharray="5 5"
                    />
                    <Line
                        type="monotone"
                        dataKey="monthly_sma12"
                        stroke="#22c55e"
                        strokeWidth={1.5}
                        dot={false}
                    />
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    );
}

// Monthly Returns Chart
export function MonthlyReturnsChart({ data, ticker }: MonthlyChartProps) {
    const sortedData = useMemo(() => {
        return [...data]
            .sort((a, b) => new Date(a.month).getTime() - new Date(b.month).getTime())
            .slice(-24);
    }, [data]);

    if (!sortedData.length) {
        return (
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 h-[200px] flex items-center justify-center">
                <p className="text-slate-500 text-sm">No monthly return data available</p>
            </div>
        );
    }

    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-emerald-500" />
                    Monthly Returns %
                </h3>
            </div>
            <ResponsiveContainer width="100%" height={180}>
                <BarChart data={sortedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis
                        dataKey="month"
                        tick={{ fill: '#64748b', fontSize: 9 }}
                        tickLine={false}
                        axisLine={{ stroke: '#334155' }}
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return date.toLocaleDateString('en-US', { month: 'short' });
                        }}
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
                        labelFormatter={(label) => `Month: ${label}`}
                        formatter={(value) => [`${(value as number)?.toFixed(2) ?? '-'}%`, 'Return']}
                    />
                    <ReferenceLine y={0} stroke="#64748b" />
                    <Bar dataKey="monthly_return_pct" radius={[2, 2, 0, 0]}>
                        {sortedData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={(entry.monthly_return_pct || 0) >= 0 ? '#22c55e' : '#ef4444'}
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

// Rolling Returns Comparison Chart
export function RollingReturnsChart({ data, ticker }: MonthlyChartProps) {
    const sortedData = useMemo(() => {
        return [...data]
            .sort((a, b) => new Date(a.month).getTime() - new Date(b.month).getTime())
            .slice(-12);
    }, [data]);

    if (!sortedData.length) {
        return (
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 h-[200px] flex items-center justify-center">
                <p className="text-slate-500 text-sm">No rolling returns data available</p>
            </div>
        );
    }

    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2">
                    <Activity className="h-4 w-4 text-purple-500" />
                    Rolling Returns
                </h3>
                <div className="flex gap-3 text-[10px]">
                    <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-blue-500"></span>3M</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-amber-500"></span>6M</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-emerald-500"></span>12M</span>
                </div>
            </div>
            <ResponsiveContainer width="100%" height={180}>
                <LineChart data={sortedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis
                        dataKey="month"
                        tick={{ fill: '#64748b', fontSize: 9 }}
                        tickLine={false}
                        axisLine={{ stroke: '#334155' }}
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return date.toLocaleDateString('en-US', { month: 'short' });
                        }}
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
                        labelFormatter={(label) => `Month: ${label}`}
                        formatter={(value, name) => [
                            `${(value as number)?.toFixed(2) ?? '-'}%`,
                            name === 'return_3m' ? '3M Return' :
                                name === 'return_6m' ? '6M Return' :
                                    name === 'return_12m' ? '12M Return' : String(name)
                        ]}
                    />
                    <ReferenceLine y={0} stroke="#64748b" strokeDasharray="3 3" />
                    <Line type="monotone" dataKey="return_3m" stroke="#3b82f6" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="return_6m" stroke="#f59e0b" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="return_12m" stroke="#22c55e" strokeWidth={2} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}

// Monthly Volume Chart
export function MonthlyVolumeChart({ data, ticker }: MonthlyChartProps) {
    const sortedData = useMemo(() => {
        return [...data]
            .sort((a, b) => new Date(a.month).getTime() - new Date(b.month).getTime())
            .slice(-24);
    }, [data]);

    const avgVolume = useMemo(() => {
        const volumes = sortedData.filter(d => d.monthly_volume).map(d => d.monthly_volume || 0);
        return volumes.length > 0 ? volumes.reduce((a, b) => a + b, 0) / volumes.length : 0;
    }, [sortedData]);

    if (!sortedData.length) {
        return (
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 h-[200px] flex items-center justify-center">
                <p className="text-slate-500 text-sm">No volume data available</p>
            </div>
        );
    }

    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-blue-500" />
                    Monthly Volume
                </h3>
                <span className="text-[10px] text-amber-500">Avg: {avgVolume.toLocaleString()}</span>
            </div>
            <ResponsiveContainer width="100%" height={150}>
                <BarChart data={sortedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis
                        dataKey="month"
                        tick={{ fill: '#64748b', fontSize: 9 }}
                        tickLine={false}
                        axisLine={{ stroke: '#334155' }}
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return date.toLocaleDateString('en-US', { month: 'short' });
                        }}
                    />
                    <YAxis
                        tick={{ fill: '#64748b', fontSize: 10 }}
                        tickLine={false}
                        axisLine={{ stroke: '#334155' }}
                        tickFormatter={(value) => {
                            if (value >= 1000000000) return `${(value / 1000000000).toFixed(1)}B`;
                            if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
                            if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
                            return value;
                        }}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                        labelFormatter={(label) => `Month: ${label}`}
                        formatter={(value) => [(value as number)?.toLocaleString() ?? '-', 'Volume']}
                    />
                    <ReferenceLine y={avgVolume} stroke="#f59e0b" strokeDasharray="3 3" />
                    <Bar dataKey="monthly_volume" fill="#64748b" radius={[2, 2, 0, 0]}>
                        {sortedData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={(entry.monthly_volume || 0) > avgVolume ? '#3b82f6' : '#64748b'}
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

// Monthly Stats Summary
export function MonthlyStats({ data, ticker }: MonthlyChartProps) {
    const stats = useMemo(() => {
        if (!data.length) return null;

        const sortedData = [...data].sort((a, b) => new Date(b.month).getTime() - new Date(a.month).getTime());
        const latestMonth = sortedData[0];

        const prices = data.filter(d => d.monthly_close).map(d => d.monthly_close || 0);
        const high24m = Math.max(...prices);
        const low24m = Math.min(...prices);

        const returns = data.filter(d => d.monthly_return_pct !== undefined).map(d => d.monthly_return_pct || 0);
        const positiveMonths = returns.filter(r => r > 0).length;
        const avgReturn = returns.length > 0 ? returns.reduce((a, b) => a + b, 0) / returns.length : 0;
        const bestReturn = Math.max(...returns);
        const worstReturn = Math.min(...returns);

        return {
            latestClose: latestMonth?.monthly_close,
            high24m,
            low24m,
            distFromHigh: latestMonth?.monthly_close ? ((latestMonth.monthly_close - high24m) / high24m * 100) : 0,
            distFromLow: latestMonth?.monthly_close ? ((latestMonth.monthly_close - low24m) / low24m * 100) : 0,
            positiveMonths,
            totalMonths: returns.length,
            winRate: returns.length > 0 ? (positiveMonths / returns.length * 100) : 0,
            avgReturn,
            bestReturn,
            worstReturn,
            ytdReturn: latestMonth?.ytd_return_pct,
            return3m: latestMonth?.return_3m,
            return6m: latestMonth?.return_6m,
            return12m: latestMonth?.return_12m,
            trend: latestMonth?.monthly_trend,
        };
    }, [data]);

    if (!stats) {
        return null;
    }

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">24M High</div>
                <div className="text-lg font-bold text-emerald-500">₹{stats.high24m?.toLocaleString()}</div>
                <div className="text-[10px] text-slate-400">{stats.distFromHigh?.toFixed(1)}% from high</div>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">24M Low</div>
                <div className="text-lg font-bold text-rose-500">₹{stats.low24m?.toLocaleString()}</div>
                <div className="text-[10px] text-slate-400">+{stats.distFromLow?.toFixed(1)}% from low</div>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Win Rate</div>
                <div className="text-lg font-bold text-blue-500">{stats.winRate?.toFixed(1)}%</div>
                <div className="text-[10px] text-slate-400">{stats.positiveMonths}/{stats.totalMonths} months</div>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Avg Monthly</div>
                <div className={`text-lg font-bold ${(stats.avgReturn || 0) >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                    {stats.avgReturn?.toFixed(2)}%
                </div>
                <div className="text-[10px] text-slate-400">per month</div>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Best Month</div>
                <div className="text-lg font-bold text-emerald-500">+{stats.bestReturn?.toFixed(2)}%</div>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Worst Month</div>
                <div className="text-lg font-bold text-rose-500">{stats.worstReturn?.toFixed(2)}%</div>
            </div>
        </div>
    );
}
