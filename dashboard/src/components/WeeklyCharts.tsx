'use client';

import React from 'react';
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ReferenceLine,
    BarChart,
    Bar,
    Cell,
    ComposedChart,
} from 'recharts';

interface WeeklyChartData {
    week_ending: string;
    weekly_close: number;
    weekly_high?: number;
    weekly_low?: number;
    weekly_open?: number;
    weekly_return_pct?: number;
    weekly_rsi14?: number;
    weekly_sma10?: number;
    weekly_sma20?: number;
    weekly_volume?: number;
    return_4w?: number;
    return_13w?: number;
}

interface WeeklyChartProps {
    data: WeeklyChartData[];
    ticker: string;
}

export function WeeklyPriceChart({ data, ticker }: WeeklyChartProps) {
    // Sort data by date ascending for proper charting
    const sortedData = [...data].sort((a, b) => 
        new Date(a.week_ending).getTime() - new Date(b.week_ending).getTime()
    );

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                {ticker} Weekly Price (52 Weeks)
            </h3>
            <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={sortedData}>
                    <defs>
                        <linearGradient id="weeklyPriceGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="week_ending"
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return `${date.getDate()}/${date.getMonth() + 1}`;
                        }}
                    />
                    <YAxis
                        stroke="#64748b"
                        fontSize={12}
                        tickLine={false}
                        domain={['auto', 'auto']}
                        tickFormatter={(value) => `₹${value}`}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                        labelFormatter={(label) => `Week: ${label}`}
                        formatter={(value: number, name: string) => [
                            `₹${value?.toFixed(2)}`,
                            name === 'weekly_close' ? 'Close' : 
                            name === 'weekly_sma10' ? 'SMA 10' : 
                            name === 'weekly_sma20' ? 'SMA 20' : name
                        ]}
                    />
                    <Area
                        type="monotone"
                        dataKey="weekly_close"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        fill="url(#weeklyPriceGradient)"
                    />
                    <Line
                        type="monotone"
                        dataKey="weekly_sma10"
                        stroke="#22c55e"
                        strokeWidth={1.5}
                        dot={false}
                        strokeDasharray="5 5"
                    />
                    <Line
                        type="monotone"
                        dataKey="weekly_sma20"
                        stroke="#f59e0b"
                        strokeWidth={1.5}
                        dot={false}
                        strokeDasharray="5 5"
                    />
                </ComposedChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-6 mt-2 text-xs">
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-blue-500 rounded" />
                    Close
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-green-500 rounded" />
                    SMA 10
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-amber-500 rounded" />
                    SMA 20
                </span>
            </div>
        </div>
    );
}

export function WeeklyRSIChart({ data, ticker }: WeeklyChartProps) {
    const sortedData = [...data].sort((a, b) => 
        new Date(a.week_ending).getTime() - new Date(b.week_ending).getTime()
    );

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                Weekly RSI (14)
            </h3>
            <ResponsiveContainer width="100%" height={150}>
                <AreaChart data={sortedData}>
                    <defs>
                        <linearGradient id="weeklyRsiGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="week_ending"
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return `${date.getDate()}/${date.getMonth() + 1}`;
                        }}
                    />
                    <YAxis
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                        domain={[0, 100]}
                        ticks={[30, 50, 70]}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                        labelFormatter={(label) => `Week: ${label}`}
                        formatter={(value: number) => [value?.toFixed(1), 'RSI']}
                    />
                    <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" />
                    <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="3 3" />
                    <Area
                        type="monotone"
                        dataKey="weekly_rsi14"
                        stroke="#8b5cf6"
                        strokeWidth={2}
                        fill="url(#weeklyRsiGradient)"
                    />
                </AreaChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-6 mt-2 text-xs text-slate-400">
                <span>Overbought &gt; 70</span>
                <span>Oversold &lt; 30</span>
            </div>
        </div>
    );
}

export function WeeklyReturnsChart({ data, ticker }: WeeklyChartProps) {
    const sortedData = [...data].sort((a, b) => 
        new Date(a.week_ending).getTime() - new Date(b.week_ending).getTime()
    );

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                Weekly Returns %
            </h3>
            <ResponsiveContainer width="100%" height={150}>
                <BarChart data={sortedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="week_ending"
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return `${date.getDate()}/${date.getMonth() + 1}`;
                        }}
                    />
                    <YAxis
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                        tickFormatter={(value) => `${value}%`}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                        labelFormatter={(label) => `Week: ${label}`}
                        formatter={(value: number) => [`${value?.toFixed(2)}%`, 'Return']}
                    />
                    <ReferenceLine y={0} stroke="#64748b" />
                    <Bar dataKey="weekly_return_pct" radius={[2, 2, 0, 0]}>
                        {sortedData.map((entry, index) => (
                            <Cell 
                                key={`cell-${index}`} 
                                fill={(entry.weekly_return_pct || 0) >= 0 ? '#22c55e' : '#ef4444'} 
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

export function WeeklyVolumeChart({ data, ticker }: WeeklyChartProps) {
    const sortedData = [...data].sort((a, b) => 
        new Date(a.week_ending).getTime() - new Date(b.week_ending).getTime()
    );

    // Calculate average volume
    const avgVolume = sortedData.reduce((sum, d) => sum + (d.weekly_volume || 0), 0) / sortedData.length;

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                Weekly Volume
            </h3>
            <ResponsiveContainer width="100%" height={120}>
                <BarChart data={sortedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="week_ending"
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return `${date.getDate()}/${date.getMonth() + 1}`;
                        }}
                    />
                    <YAxis
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                        tickFormatter={(value) => {
                            if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
                            if (value >= 1000) return `${(value / 1000).toFixed(0)}K`;
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
                        labelFormatter={(label) => `Week: ${label}`}
                        formatter={(value: number) => [value?.toLocaleString(), 'Volume']}
                    />
                    <ReferenceLine y={avgVolume} stroke="#f59e0b" strokeDasharray="3 3" />
                    <Bar dataKey="weekly_volume" fill="#64748b" radius={[2, 2, 0, 0]}>
                        {sortedData.map((entry, index) => (
                            <Cell 
                                key={`cell-${index}`} 
                                fill={(entry.weekly_volume || 0) > avgVolume ? '#3b82f6' : '#64748b'} 
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
            <div className="text-center text-xs text-slate-400 mt-2">
                Avg Volume: {avgVolume.toLocaleString()}
            </div>
        </div>
    );
}

// Summary Stats Component
export function WeeklyStats({ data, ticker }: WeeklyChartProps) {
    if (data.length === 0) return null;

    const latest = data[0];
    const prices = data.map(d => d.weekly_close).filter(Boolean);
    const high52w = Math.max(...prices);
    const low52w = Math.min(...prices);
    const distFromHigh = ((latest.weekly_close - high52w) / high52w * 100);
    const distFromLow = ((latest.weekly_close - low52w) / low52w * 100);
    
    // Calculate average return
    const returns = data.map(d => d.weekly_return_pct).filter(Boolean) as number[];
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const positiveWeeks = returns.filter(r => r > 0).length;
    const winRate = (positiveWeeks / returns.length * 100);

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                52-Week Statistics
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                    <div className="text-2xl font-bold text-white">₹{high52w.toFixed(2)}</div>
                    <div className="text-xs text-slate-400">52W High</div>
                </div>
                <div className="text-center">
                    <div className="text-2xl font-bold text-white">₹{low52w.toFixed(2)}</div>
                    <div className="text-xs text-slate-400">52W Low</div>
                </div>
                <div className="text-center">
                    <div className={`text-2xl font-bold ${distFromHigh >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {distFromHigh.toFixed(1)}%
                    </div>
                    <div className="text-xs text-slate-400">From 52W High</div>
                </div>
                <div className="text-center">
                    <div className={`text-2xl font-bold ${distFromLow >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        +{distFromLow.toFixed(1)}%
                    </div>
                    <div className="text-xs text-slate-400">From 52W Low</div>
                </div>
                <div className="text-center">
                    <div className={`text-2xl font-bold ${avgReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {avgReturn >= 0 ? '+' : ''}{avgReturn.toFixed(2)}%
                    </div>
                    <div className="text-xs text-slate-400">Avg Weekly Return</div>
                </div>
                <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">{winRate.toFixed(0)}%</div>
                    <div className="text-xs text-slate-400">Win Rate</div>
                </div>
                <div className="text-center">
                    <div className={`text-2xl font-bold ${(latest.return_4w || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {(latest.return_4w || 0) >= 0 ? '+' : ''}{latest.return_4w?.toFixed(2)}%
                    </div>
                    <div className="text-xs text-slate-400">4W Return</div>
                </div>
                <div className="text-center">
                    <div className={`text-2xl font-bold ${(latest.return_13w || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {(latest.return_13w || 0) >= 0 ? '+' : ''}{latest.return_13w?.toFixed(2)}%
                    </div>
                    <div className="text-xs text-slate-400">13W Return</div>
                </div>
            </div>
        </div>
    );
}
