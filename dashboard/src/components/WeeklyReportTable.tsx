
'use client';

import React from 'react';

interface WeeklyData {
    ticker: string;
    company_name?: string;
    week_ending: string;
    weekly_open?: number;
    weekly_high?: number;
    weekly_low?: number;
    weekly_close: number;
    weekly_return_pct: number;
    weekly_volume?: number;
    weekly_volume_ratio?: number;
    weekly_rsi14?: number;
    weekly_sma10?: number;
    weekly_sma20?: number;
    return_4w?: number;
    return_13w?: number;
    distance_52w_high: number;
    distance_52w_low: number;
    weekly_trend: string;
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
                        <th className="p-3 font-medium text-right">4W Return</th>
                        <th className="p-3 font-medium text-right">13W Return</th>
                        <th className="p-3 font-medium text-right">RSI(14)</th>
                        <th className="p-3 font-medium text-right">Dist 52W High</th>
                        <th className="p-3 font-medium text-right">Dist 52W Low</th>
                    </tr>
                </thead>
                <tbody className="text-sm divide-y divide-slate-800">
                    {data.map((row) => (
                        <tr
                            key={`${row.ticker}-${row.week_ending}`}
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
                                ₹{row.weekly_close?.toFixed(2)}
                            </td>
                            <td className={`p-3 text-right font-medium ${(row.weekly_return_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                {(row.weekly_return_pct || 0) > 0 ? '+' : ''}
                                {row.weekly_return_pct?.toFixed(2)}%
                            </td>
                            <td className={`p-3 text-right ${(row.return_4w || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {(row.return_4w || 0) > 0 ? '+' : ''}{row.return_4w?.toFixed(2)}%
                            </td>
                            <td className={`p-3 text-right ${(row.return_13w || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {(row.return_13w || 0) > 0 ? '+' : ''}{row.return_13w?.toFixed(2)}%
                            </td>
                            <td className={`p-3 text-right ${(row.weekly_rsi14 || 0) > 70 ? 'text-red-400' : (row.weekly_rsi14 || 0) < 30 ? 'text-green-400' : 'text-slate-300'}`}>
                                {row.weekly_rsi14?.toFixed(1)}
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
                            <td colSpan={9} className="p-8 text-center text-slate-500">
                                No weekly data available.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}
