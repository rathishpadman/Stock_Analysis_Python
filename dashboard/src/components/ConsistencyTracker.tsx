'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ChevronDown, ChevronUp, Trophy, Flame } from 'lucide-react';

interface ScoreEntry {
    score: number;
    rank: number;
}

interface RankingRow {
    ticker: string;
    sector: string;
    scores: Record<string, ScoreEntry>;
    avgScore: number;
    frequency: number;
    frequencyLabel: string;
}

interface ConsistencyData {
    periods: string[];
    rankings: RankingRow[];
    consistentTickers: string[];
}

interface ConsistencyTrackerProps {
    type: 'daily' | 'weekly' | 'monthly';
    onSelectStock: (ticker: string) => void;
    onConsistentTickers?: (tickers: Set<string>) => void;
}

const PERIOD_OPTIONS: Record<string, number[]> = {
    daily: [5, 10, 15],
    weekly: [4, 8, 12],
    monthly: [3, 6, 12],
};

const PERIOD_LABELS: Record<string, string> = {
    daily: 'days',
    weekly: 'weeks',
    monthly: 'months',
};

function formatDate(dateStr: string, type: string): string {
    const d = new Date(dateStr + 'T00:00:00');
    if (type === 'monthly') {
        return d.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' });
    }
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
}

function getRankColor(rank: number): string {
    if (rank <= 3) return 'bg-emerald-500/20 text-emerald-400';
    if (rank <= 7) return 'bg-amber-500/20 text-amber-400';
    return 'bg-slate-700/30 text-slate-500';
}

export default function ConsistencyTracker({ type, onSelectStock, onConsistentTickers }: ConsistencyTrackerProps) {
    const [expanded, setExpanded] = useState(false);
    const [periods, setPeriods] = useState(PERIOD_OPTIONS[type][0]);
    const [data, setData] = useState<ConsistencyData | null>(null);
    const [loading, setLoading] = useState(false);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await fetch(`/api/consistency?type=${type}&periods=${periods}&top=10`);
            if (!res.ok) throw new Error('Failed to fetch');
            const json: ConsistencyData = await res.json();
            setData(json);
            if (onConsistentTickers) {
                onConsistentTickers(new Set(json.consistentTickers));
            }
        } catch {
            setData(null);
        } finally {
            setLoading(false);
        }
    }, [type, periods, onConsistentTickers]);

    useEffect(() => {
        if (expanded) {
            fetchData();
        }
    }, [expanded, fetchData]);

    // Also fetch on mount (collapsed) to get consistentTickers for badges
    useEffect(() => {
        fetchData();
    }, [type, periods]); // eslint-disable-line react-hooks/exhaustive-deps

    const periodOptions = PERIOD_OPTIONS[type];

    return (
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
            {/* Header */}
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-700/30 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <Trophy className="w-4 h-4 text-amber-400" />
                    <span className="text-sm font-semibold text-slate-200">
                        Top 10 Consistency
                    </span>
                    <span className="text-xs text-slate-500">
                        (Last {periods} {PERIOD_LABELS[type]})
                    </span>
                    {data && !expanded && (
                        <span className="text-xs text-emerald-400 ml-2">
                            {data.consistentTickers.length} consistent picks
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-3">
                    {/* Period selector — stop propagation so click doesn't toggle */}
                    <div onClick={e => e.stopPropagation()} className="flex items-center gap-1">
                        {periodOptions.map(opt => (
                            <button
                                key={opt}
                                onClick={() => setPeriods(opt)}
                                className={`px-2 py-0.5 text-xs rounded transition-colors ${
                                    periods === opt
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                                }`}
                            >
                                {opt}
                            </button>
                        ))}
                    </div>
                    {expanded ? (
                        <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                </div>
            </button>

            {/* Expanded content */}
            {expanded && (
                <div className="border-t border-slate-700 overflow-x-auto">
                    {loading ? (
                        <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400" />
                            <span className="ml-3 text-sm text-slate-400">Loading consistency data...</span>
                        </div>
                    ) : !data || data.rankings.length === 0 ? (
                        <div className="text-center py-8 text-slate-500 text-sm">
                            No historical data available for consistency tracking.
                        </div>
                    ) : (
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="bg-slate-800/80">
                                    <th className="sticky left-0 bg-slate-800 z-10 px-3 py-2 text-left text-xs font-medium text-slate-400 uppercase">
                                        Ticker
                                    </th>
                                    {data.periods.map(date => (
                                        <th key={date} className="px-2 py-2 text-center text-xs font-medium text-slate-400">
                                            {formatDate(date, type)}
                                        </th>
                                    ))}
                                    <th className="px-2 py-2 text-center text-xs font-medium text-amber-400 uppercase">
                                        Avg
                                    </th>
                                    <th className="px-2 py-2 text-center text-xs font-medium text-blue-400 uppercase">
                                        Freq
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.rankings.map((row, idx) => (
                                    <tr
                                        key={row.ticker}
                                        className={`border-t border-slate-700/50 hover:bg-slate-700/30 cursor-pointer transition-colors ${
                                            idx < 3 ? 'bg-emerald-500/5' : ''
                                        }`}
                                        onClick={() => onSelectStock(row.ticker)}
                                    >
                                        <td className="sticky left-0 bg-slate-800 z-10 px-3 py-2 font-medium text-slate-200 whitespace-nowrap">
                                            <div className="flex items-center gap-1.5">
                                                {data.consistentTickers.includes(row.ticker) && (
                                                    <Flame className="w-3.5 h-3.5 text-orange-400" />
                                                )}
                                                <span>{row.ticker}</span>
                                                <span className="text-xs text-slate-500 hidden sm:inline">
                                                    {row.sector}
                                                </span>
                                            </div>
                                        </td>
                                        {data.periods.map(date => {
                                            const entry = row.scores[date];
                                            if (!entry) {
                                                return (
                                                    <td key={date} className="px-2 py-2 text-center text-slate-600">
                                                        —
                                                    </td>
                                                );
                                            }
                                            return (
                                                <td key={date} className="px-2 py-2 text-center">
                                                    <span className={`inline-block px-1.5 py-0.5 rounded text-xs font-mono ${getRankColor(entry.rank)}`}>
                                                        {entry.score.toFixed(1)}
                                                    </span>
                                                </td>
                                            );
                                        })}
                                        <td className="px-2 py-2 text-center text-amber-300 font-mono text-xs">
                                            {row.avgScore.toFixed(1)}
                                        </td>
                                        <td className="px-2 py-2 text-center">
                                            <span className={`text-xs font-mono ${
                                                row.frequency === data.periods.length
                                                    ? 'text-emerald-400 font-bold'
                                                    : row.frequency >= Math.ceil(data.periods.length * 0.6)
                                                        ? 'text-blue-400'
                                                        : 'text-slate-500'
                                            }`}>
                                                {row.frequencyLabel}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}
        </div>
    );
}
