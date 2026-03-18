'use client';

import React from 'react';
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ReferenceLine,
    BarChart,
    Bar,
    Cell,
    ComposedChart,
    Line,
} from 'recharts';

interface StockChartProps {
    data: {
        date: string;
        price: number;
        sma20?: number;
        sma50?: number;
        sma200?: number;
        rsi?: number;
        volume?: number;
        macd_line?: number;
        macd_signal?: number;
        macd_hist?: number;
        bb_upper?: number;
        bb_lower?: number;
        stoch_k?: number;
        stoch_d?: number;
    }[];
    ticker: string;
}

interface PivotData {
    pp: number;
    s1?: number;
    s2?: number;
    r1?: number;
    r2?: number;
}

export function PriceChart({ data, ticker, pivots }: StockChartProps & { pivots?: PivotData }) {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                {ticker} Price Chart
            </h3>
            <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="date"
                        stroke="#64748b"
                        fontSize={12}
                        tickLine={false}
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
                        formatter={(value: number | undefined) => value !== undefined ? [`₹${value.toFixed(2)}`, 'Price'] : ['N/A', 'Price']}
                    />
                    <Area
                        type="monotone"
                        dataKey="price"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        fill="url(#priceGradient)"
                    />
                    {data[0]?.sma20 && (
                        <Area
                            type="monotone"
                            dataKey="sma20"
                            stroke="#22c55e"
                            strokeWidth={1.5}
                            fill="none"
                            strokeDasharray="5 5"
                        />
                    )}
                    {data[0]?.sma50 && (
                        <Area
                            type="monotone"
                            dataKey="sma50"
                            stroke="#f59e0b"
                            strokeWidth={1.5}
                            fill="none"
                            strokeDasharray="5 5"
                        />
                    )}
                    {data[0]?.sma200 && (
                        <Area
                            type="monotone"
                            dataKey="sma200"
                            stroke="#ef4444"
                            strokeWidth={1.5}
                            fill="none"
                            strokeDasharray="5 5"
                        />
                    )}
                    {data[0]?.bb_upper && (
                        <Area
                            type="monotone"
                            dataKey="bb_upper"
                            stroke="#6366f1"
                            strokeWidth={1}
                            fill="none"
                            strokeDasharray="3 3"
                            strokeOpacity={0.6}
                        />
                    )}
                    {data[0]?.bb_lower && (
                        <Area
                            type="monotone"
                            dataKey="bb_lower"
                            stroke="#6366f1"
                            strokeWidth={1}
                            fill="none"
                            strokeDasharray="3 3"
                            strokeOpacity={0.6}
                        />
                    )}
                    {pivots?.pp && <ReferenceLine y={pivots.pp} stroke="#94a3b8" strokeDasharray="6 3" strokeWidth={1} label={{ value: 'PP', position: 'right', fill: '#94a3b8', fontSize: 9 }} />}
                    {pivots?.s1 && <ReferenceLine y={pivots.s1} stroke="#22c55e" strokeDasharray="4 4" strokeWidth={1} label={{ value: 'S1', position: 'right', fill: '#22c55e', fontSize: 9 }} />}
                    {pivots?.s2 && <ReferenceLine y={pivots.s2} stroke="#16a34a" strokeDasharray="4 4" strokeWidth={1} label={{ value: 'S2', position: 'right', fill: '#16a34a', fontSize: 9 }} />}
                    {pivots?.r1 && <ReferenceLine y={pivots.r1} stroke="#ef4444" strokeDasharray="4 4" strokeWidth={1} label={{ value: 'R1', position: 'right', fill: '#ef4444', fontSize: 9 }} />}
                    {pivots?.r2 && <ReferenceLine y={pivots.r2} stroke="#dc2626" strokeDasharray="4 4" strokeWidth={1} label={{ value: 'R2', position: 'right', fill: '#dc2626', fontSize: 9 }} />}
                </AreaChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-6 mt-2 text-xs">
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-blue-500 rounded" />
                    Price
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-green-500 rounded" style={{ borderStyle: 'dashed' }} />
                    SMA 20
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-amber-500 rounded" style={{ borderStyle: 'dashed' }} />
                    SMA 50
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-red-500 rounded" style={{ borderStyle: 'dashed' }} />
                    SMA 200
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-indigo-400 rounded" style={{ borderStyle: 'dashed' }} />
                    BB
                </span>
                {pivots?.pp && (
                    <>
                        <span className="flex items-center gap-1.5">
                            <span className="w-3 h-0.5 bg-slate-400 rounded" />
                            PP
                        </span>
                        <span className="flex items-center gap-1.5">
                            <span className="w-3 h-0.5 bg-green-500 rounded" />
                            S1/S2
                        </span>
                        <span className="flex items-center gap-1.5">
                            <span className="w-3 h-0.5 bg-red-500 rounded" />
                            R1/R2
                        </span>
                    </>
                )}
            </div>
        </div>
    );
}

export function RSIChart({ data, ticker }: StockChartProps) {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                RSI (14)
            </h3>
            <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="rsiGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="date"
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
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
                        formatter={(value: number | undefined) => value !== undefined ? [value.toFixed(1), 'RSI'] : ['N/A', 'RSI']}
                    />
                    <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" />
                    <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="3 3" />
                    <Area
                        type="monotone"
                        dataKey="rsi"
                        stroke="#8b5cf6"
                        strokeWidth={2}
                        fill="url(#rsiGradient)"
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

export function MACDChart({ data, ticker }: StockChartProps) {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                MACD Momentum
            </h3>
            <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="date"
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                    />
                    <YAxis
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                    />
                    <ReferenceLine y={0} stroke="#64748b" />

                    {/* MACD Line */}
                    <Area type="monotone" dataKey="macd_line" stroke="#3b82f6" fill="none" strokeWidth={2} />

                    {/* Signal Line */}
                    <Area type="monotone" dataKey="macd_signal" stroke="#f97316" fill="none" strokeWidth={2} />

                    {/* Histogram - using Bar chart inside ComposedChart is better, but Area can work if strictly positive/negative. 
                        Actually, let's just stick to line for simplicity or switch to ComposedChart if Recharts allows easily.
                        For now, plotting MACD and Signal is sufficient for MVP "Momentum. 
                        Let's add Histogram as a faint Area.
                    */}
                    <Area type="step" dataKey="macd_hist" stroke="none" fill="#6366f1" fillOpacity={0.3} />

                </AreaChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-6 mt-2 text-xs">
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-blue-500 rounded" />
                    MACD
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-orange-500 rounded" />
                    Signal
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 bg-indigo-500/50 rounded" />
                    Hist
                </span>
            </div>
        </div>
    );
}

export function VolumeChart({ data, ticker }: StockChartProps) {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                Volume
            </h3>
            <ResponsiveContainer width="100%" height={180}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="date"
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                    />
                    <YAxis
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                        tickFormatter={(v) => v >= 1e6 ? `${(v / 1e6).toFixed(1)}M` : v >= 1e3 ? `${(v / 1e3).toFixed(0)}K` : `${v}`}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                        formatter={(value: number | undefined) => value !== undefined ? [value.toLocaleString(), 'Volume'] : ['N/A', 'Volume']}
                    />
                    <Bar dataKey="volume" fill="#3b82f6" fillOpacity={0.6} radius={[2, 2, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

export function StochasticChart({ data, ticker }: StockChartProps) {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                Stochastic Oscillator
            </h3>
            <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="date"
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                    />
                    <YAxis
                        stroke="#64748b"
                        fontSize={10}
                        tickLine={false}
                        domain={[0, 100]}
                        ticks={[20, 50, 80]}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                    />
                    <ReferenceLine y={80} stroke="#ef4444" strokeDasharray="3 3" />
                    <ReferenceLine y={20} stroke="#22c55e" strokeDasharray="3 3" />
                    <Area type="monotone" dataKey="stoch_k" stroke="#f59e0b" fill="none" strokeWidth={2} />
                    <Area type="monotone" dataKey="stoch_d" stroke="#ec4899" fill="none" strokeWidth={1.5} strokeDasharray="5 5" />
                </AreaChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-6 mt-2 text-xs">
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-amber-500 rounded" />
                    %K
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-0.5 bg-pink-500 rounded" style={{ borderStyle: 'dashed' }} />
                    %D
                </span>
                <span className="text-slate-400">Overbought &gt; 80 | Oversold &lt; 20</span>
            </div>
        </div>
    );
}

export function ScoreBarChart({ stocks }: { stocks: { ticker: string; overall_score: number }[] }) {
    const top10 = [...stocks]
        .sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0))
        .slice(0, 10);

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                Top 10 by Overall Score
            </h3>
            <ResponsiveContainer width="100%" height={250}>
                <BarChart data={top10} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                    <XAxis type="number" domain={[0, 100]} stroke="#64748b" fontSize={10} />
                    <YAxis
                        type="category"
                        dataKey="ticker"
                        stroke="#64748b"
                        fontSize={11}
                        width={80}
                        tickLine={false}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                        formatter={(value: number | undefined) => value !== undefined ? [value.toFixed(1), 'Score'] : ['N/A', 'Score']}
                    />
                    <Bar dataKey="overall_score" radius={[0, 4, 4, 0]}>
                        {top10.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={entry.overall_score > 70 ? '#22c55e' : entry.overall_score > 50 ? '#3b82f6' : '#f59e0b'}
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

