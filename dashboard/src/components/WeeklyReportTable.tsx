
'use client';

import React from 'react';

interface WeeklyData {
    ticker: string;
    week_ending: string;
    close_price: number;
    weekly_return: number;
    weekly_range_pct: number;
    distance_52w_high: number;
    distance_52w_low: number;
    weekly_trend: string;
    volatility_weekly?: number;
}

interface WeeklyReportTableProps {
    data: WeeklyData[];
    onSelectStock: (ticker: string) => void;
}

export default function WeeklyReportTable({ data, onSelectStock }: WeeklyReportTableProps) {
    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="border-b border-slate-700 text-slate-400 text-sm">
                        <th className="p-3 font-medium">Ticker</th>
                        <th className="p-3 font-medium">Trend</th>
                        <th className="p-3 font-medium text-right">Close</th>
                        <th className="p-3 font-medium text-right">Wk Return</th>
                        <th className="p-3 font-medium text-right">Range %</th>
                        <th className="p-3 font-medium text-right">Dist 52W High</th>
                        <th className="p-3 font-medium text-right">Dist 52W Low</th>
                    </tr>
                </thead>
                <tbody className="text-sm divide-y divide-slate-800">
                    {data.map((row) => (
                        <tr
                            key={row.ticker}
                            className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                            onClick={() => onSelectStock(row.ticker)}
                        >
                            <td className="p-3 font-medium text-white">{row.ticker}</td>
                            <td className="p-3">
                                <span className={`px-2 py-0.5 rounded text-xs ${row.weekly_trend === 'UP' ? 'bg-green-500/20 text-green-400' :
                                        row.weekly_trend === 'DOWN' ? 'bg-red-500/20 text-red-400' :
                                            'bg-slate-700 text-slate-300'
                                    }`}>
                                    {row.weekly_trend}
                                </span>
                            </td>
                            <td className="p-3 text-right text-slate-300">
                                ₹{row.close_price?.toFixed(2)}
                            </td>
                            <td className={`p-3 text-right font-medium ${(row.weekly_return || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                {(row.weekly_return || 0) > 0 ? '+' : ''}
                                {row.weekly_return?.toFixed(2)}%
                            </td>
                            <td className="p-3 text-right text-slate-300">
                                {row.weekly_range_pct?.toFixed(2)}%
                            </td>
                            <td className="p-3 text-right text-red-300">
                                {row.distance_52w_high?.toFixed(2)}%
                            </td>
                            <td className="p-3 text-right text-green-300">
                                {row.distance_52w_low?.toFixed(2)}%
                            </td>
                        </tr>
                    ))}
                    {data.length === 0 && (
                        <tr>
                            <td colSpan={7} className="p-8 text-center text-slate-500">
                                No weekly data available.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}
