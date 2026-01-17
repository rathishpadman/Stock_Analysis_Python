'use client';

import React from 'react';

interface SeasonalityData {
    ticker: string;
    company_name?: string;
    jan_avg: number | null;
    feb_avg: number | null;
    mar_avg: number | null;
    apr_avg: number | null;
    may_avg: number | null;
    jun_avg: number | null;
    jul_avg: number | null;
    aug_avg: number | null;
    sep_avg: number | null;
    oct_avg: number | null;
    nov_avg: number | null;
    dec_avg: number | null;
    best_month?: string;
    worst_month?: string;
}

interface SeasonalityHeatmapProps {
    data: SeasonalityData[];
    onSelectStock: (ticker: string) => void;
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const MONTH_KEYS = ['jan_avg', 'feb_avg', 'mar_avg', 'apr_avg', 'may_avg', 'jun_avg', 'jul_avg', 'aug_avg', 'sep_avg', 'oct_avg', 'nov_avg', 'dec_avg'] as const;

function getHeatmapColor(value: number | null): string {
    if (value === null || value === undefined) return 'bg-slate-800 text-slate-600';
    
    if (value >= 5) return 'bg-green-600/80 text-white';
    if (value >= 3) return 'bg-green-500/60 text-white';
    if (value >= 1) return 'bg-green-400/40 text-green-100';
    if (value >= 0) return 'bg-slate-700 text-slate-300';
    if (value >= -1) return 'bg-red-400/40 text-red-100';
    if (value >= -3) return 'bg-red-500/60 text-white';
    return 'bg-red-600/80 text-white';
}

export default function SeasonalityHeatmap({ data, onSelectStock }: SeasonalityHeatmapProps) {
    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="border-b border-slate-700 text-slate-400 text-xs">
                        <th className="p-2 font-medium sticky left-0 bg-[#0a101f] z-10">Ticker</th>
                        {MONTHS.map(month => (
                            <th key={month} className="p-2 font-medium text-center w-16">{month}</th>
                        ))}
                        <th className="p-2 font-medium text-center">Best</th>
                        <th className="p-2 font-medium text-center">Worst</th>
                    </tr>
                </thead>
                <tbody className="text-xs divide-y divide-slate-800">
                    {data.map((row) => (
                        <tr
                            key={row.ticker}
                            className="hover:bg-slate-800/30 cursor-pointer transition-colors"
                            onClick={() => onSelectStock(row.ticker)}
                        >
                            <td className="p-2 font-medium text-white sticky left-0 bg-[#0a101f] z-10">
                                {row.ticker}
                            </td>
                            {MONTH_KEYS.map((key) => {
                                const value = row[key];
                                return (
                                    <td key={key} className="p-1 text-center">
                                        <span className={`inline-block w-full px-1 py-1 rounded text-[10px] font-mono ${getHeatmapColor(value)}`}>
                                            {value !== null ? `${value > 0 ? '+' : ''}${value.toFixed(1)}%` : '-'}
                                        </span>
                                    </td>
                                );
                            })}
                            <td className="p-2 text-center">
                                <span className="px-2 py-0.5 rounded bg-green-500/20 text-green-400 text-[10px] font-bold">
                                    {row.best_month || '-'}
                                </span>
                            </td>
                            <td className="p-2 text-center">
                                <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 text-[10px] font-bold">
                                    {row.worst_month || '-'}
                                </span>
                            </td>
                        </tr>
                    ))}
                    {data.length === 0 && (
                        <tr>
                            <td colSpan={15} className="p-8 text-center text-slate-500">
                                No seasonality data available. Run the monthly pipeline to populate data.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
            
            {/* Legend */}
            <div className="mt-4 flex items-center justify-center gap-4 text-[10px] text-slate-400">
                <span>Returns Legend:</span>
                <div className="flex items-center gap-1">
                    <span className="w-6 h-4 rounded bg-red-600/80"></span>
                    <span>&lt;-3%</span>
                </div>
                <div className="flex items-center gap-1">
                    <span className="w-6 h-4 rounded bg-red-400/40"></span>
                    <span>-1% to 0%</span>
                </div>
                <div className="flex items-center gap-1">
                    <span className="w-6 h-4 rounded bg-slate-700"></span>
                    <span>0% to 1%</span>
                </div>
                <div className="flex items-center gap-1">
                    <span className="w-6 h-4 rounded bg-green-400/40"></span>
                    <span>1% to 3%</span>
                </div>
                <div className="flex items-center gap-1">
                    <span className="w-6 h-4 rounded bg-green-600/80"></span>
                    <span>&gt;5%</span>
                </div>
            </div>
        </div>
    );
}
