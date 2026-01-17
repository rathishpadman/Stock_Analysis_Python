'use client';

import React from 'react';

interface MonthlyData {
    ticker: string;
    company_name?: string;
    month: string;
    monthly_open?: number;
    monthly_high?: number;
    monthly_low?: number;
    monthly_close: number;
    monthly_return_pct: number;
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
    best_month_return_12m?: number;
    worst_month_return_12m?: number;
    monthly_trend: string;
}

interface MonthlyReportTableProps {
    data: MonthlyData[];
    onSelectStock: (ticker: string) => void;
}

export default function MonthlyReportTable({ data, onSelectStock }: MonthlyReportTableProps) {
    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="border-b border-slate-700 text-slate-400 text-sm">
                        <th className="p-3 font-medium">Ticker</th>
                        <th className="p-3 font-medium">Month</th>
                        <th className="p-3 font-medium">Trend</th>
                        <th className="p-3 font-medium text-right">Close</th>
                        <th className="p-3 font-medium text-right">Mo Return</th>
                        <th className="p-3 font-medium text-right">YTD</th>
                        <th className="p-3 font-medium text-right">3M Return</th>
                        <th className="p-3 font-medium text-right">6M Return</th>
                        <th className="p-3 font-medium text-right">12M Return</th>
                        <th className="p-3 font-medium text-right">Pos Months</th>
                    </tr>
                </thead>
                <tbody className="text-sm divide-y divide-slate-800">
                    {data.map((row) => (
                        <tr
                            key={`${row.ticker}-${row.month}`}
                            className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                            onClick={() => onSelectStock(row.ticker)}
                        >
                            <td className="p-3 font-medium text-white">{row.ticker}</td>
                            <td className="p-3 text-slate-400 font-mono text-xs">{row.month}</td>
                            <td className="p-3">
                                <span className={`px-2 py-0.5 rounded text-xs ${
                                    row.monthly_trend === 'UP' ? 'bg-green-500/20 text-green-400' :
                                    row.monthly_trend === 'DOWN' ? 'bg-red-500/20 text-red-400' :
                                    'bg-slate-700 text-slate-300'
                                }`}>
                                    {row.monthly_trend}
                                </span>
                            </td>
                            <td className="p-3 text-right text-slate-300">
                                ₹{row.monthly_close?.toFixed(2)}
                            </td>
                            <td className={`p-3 text-right font-medium ${
                                (row.monthly_return_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                                {(row.monthly_return_pct || 0) > 0 ? '+' : ''}
                                {row.monthly_return_pct?.toFixed(2)}%
                            </td>
                            <td className={`p-3 text-right ${
                                (row.ytd_return_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                                {(row.ytd_return_pct || 0) > 0 ? '+' : ''}{row.ytd_return_pct?.toFixed(2)}%
                            </td>
                            <td className={`p-3 text-right ${
                                (row.return_3m || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                                {(row.return_3m || 0) > 0 ? '+' : ''}{row.return_3m?.toFixed(2)}%
                            </td>
                            <td className={`p-3 text-right ${
                                (row.return_6m || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                                {(row.return_6m || 0) > 0 ? '+' : ''}{row.return_6m?.toFixed(2)}%
                            </td>
                            <td className={`p-3 text-right ${
                                (row.return_12m || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                                {(row.return_12m || 0) > 0 ? '+' : ''}{row.return_12m?.toFixed(2)}%
                            </td>
                            <td className="p-3 text-right">
                                <span className={`font-mono ${
                                    (row.positive_months_12m || 0) >= 8 ? 'text-green-400' :
                                    (row.positive_months_12m || 0) >= 6 ? 'text-amber-400' :
                                    'text-red-400'
                                }`}>
                                    {row.positive_months_12m || 0}/12
                                </span>
                            </td>
                        </tr>
                    ))}
                    {data.length === 0 && (
                        <tr>
                            <td colSpan={10} className="p-8 text-center text-slate-500">
                                No monthly data available. Run the monthly pipeline to populate data.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}
