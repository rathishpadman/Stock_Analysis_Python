'use client';

import React from 'react';

interface DateRangeSelectorProps {
    selectedRange: string;
    onRangeChange: (range: string) => void;
}

const RANGE_OPTIONS = [
    { label: '1W', value: '1w', days: 7 },
    { label: '1M', value: '1m', days: 30 },
    { label: '3M', value: '3m', days: 90 },
    { label: '6M', value: '6m', days: 180 },
    { label: '1Y', value: '1y', days: 365 },
    { label: 'ALL', value: 'all', days: 365 },
];

export function rangeToDays(range: string): number {
    const option = RANGE_OPTIONS.find(o => o.value === range);
    return option?.days || 90;
}

export default function DateRangeSelector({ selectedRange, onRangeChange }: DateRangeSelectorProps) {
    return (
        <div className="flex bg-slate-900/50 border border-white/10 rounded-lg p-1 gap-1">
            {RANGE_OPTIONS.map((option) => (
                <button
                    key={option.value}
                    onClick={() => onRangeChange(option.value)}
                    className={`px-3 py-1.5 rounded text-xs font-bold transition-all ${selectedRange === option.value
                            ? 'bg-blue-600 text-white'
                            : 'text-slate-400 hover:text-white hover:bg-slate-800'
                        }`}
                >
                    {option.label}
                </button>
            ))}
        </div>
    );
}
