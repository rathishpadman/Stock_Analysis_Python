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
} from 'recharts';

interface StockChartProps {
    data: {
        date: string;
        price: number;
        sma20?: number;
        sma50?: number;
        rsi?: number;
        volume?: number;
    }[];
    ticker: string;
}

export function PriceChart({ data, ticker }: StockChartProps) {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
                {ticker} Price Chart
            </h3>
            <ResponsiveContainer width="100%" height={300}>
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
            <ResponsiveContainer width="100%" height={150}>
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
