'use client';

import React, { useState, useMemo } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown, Filter, X, Trophy } from 'lucide-react';

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
    distance_52w_high?: number;
    distance_52w_low?: number;
    weekly_trend: string;
    // Calculated rank
    momentum_rank?: number;
}

interface WeeklyReportTableProps {
    data: WeeklyData[];
    onSelectStock: (ticker: string) => void;
}

type SortField = 'ticker' | 'weekly_close' | 'weekly_return_pct' | 'return_4w' | 'return_13w' | 'weekly_rsi14' | 'momentum_rank';
type SortDirection = 'asc' | 'desc';
type TrendFilter = 'ALL' | 'UP' | 'DOWN' | 'SIDEWAYS';

// Calculate momentum rank based on market-accepted business logic
// Momentum Score = (Weight * 4W Return) + (Weight * 13W Return) + RSI adjustment
function calculateMomentumRank(data: WeeklyData[]): WeeklyData[] {
    const scored = data.map(stock => {
        // Momentum scoring factors (industry standard weights)
        const return4w = stock.return_4w || 0;
        const return13w = stock.return_13w || 0;
        const rsi = stock.weekly_rsi14 || 50;
        const volumeRatio = stock.weekly_volume_ratio || 1;

        // Momentum Score Components:
        // 1. Short-term momentum (4W return) - 30% weight
        // 2. Medium-term momentum (13W return) - 40% weight  
        // 3. RSI Zone bonus/penalty - 20% weight (optimal 40-60 zone)
        // 4. Volume confirmation - 10% weight

        const shortTermScore = return4w * 0.30;
        const mediumTermScore = return13w * 0.40;
        
        // RSI adjustment: penalize overbought (>70) and oversold (<30)
        let rsiScore = 0;
        if (rsi >= 40 && rsi <= 60) {
            rsiScore = 10; // Optimal zone bonus
        } else if (rsi > 60 && rsi <= 70) {
            rsiScore = 5; // Slightly overbought
        } else if (rsi >= 30 && rsi < 40) {
            rsiScore = 5; // Slightly oversold - potential bounce
        } else if (rsi > 70) {
            rsiScore = -5; // Overbought penalty
        } else {
            rsiScore = 0; // Deeply oversold - risky
        }
        
        // Volume confirmation bonus
        const volumeScore = volumeRatio > 1.2 ? 5 : volumeRatio > 1 ? 2 : 0;

        const totalScore = shortTermScore + mediumTermScore + (rsiScore * 0.20) + (volumeScore * 0.10);

        return {
            ...stock,
            _momentumScore: totalScore
        };
    });

    // Sort by momentum score and assign ranks
    const sorted = [...scored].sort((a, b) => (b._momentumScore || 0) - (a._momentumScore || 0));
    
    return sorted.map((stock, index) => ({
        ...stock,
        momentum_rank: index + 1,
        _momentumScore: undefined // Remove internal score
    }));
}

export default function WeeklyReportTable({ data, onSelectStock }: WeeklyReportTableProps) {
    const [sortField, setSortField] = useState<SortField>('momentum_rank');
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
    const [trendFilter, setTrendFilter] = useState<TrendFilter>('ALL');
    const [showFilters, setShowFilters] = useState(false);
    const [minReturn, setMinReturn] = useState<string>('');
    const [maxReturn, setMaxReturn] = useState<string>('');
    const [rsiFilter, setRsiFilter] = useState<'ALL' | 'OVERSOLD' | 'NEUTRAL' | 'OVERBOUGHT'>('ALL');
    
    // Pagination state
    const [currentPage, setCurrentPage] = useState(1);
    const [rowsPerPage, setRowsPerPage] = useState(25);

    // Calculate momentum ranks
    const rankedData = useMemo(() => calculateMomentumRank(data), [data]);

    // Apply filters and sorting
    const filteredAndSortedData = useMemo(() => {
        let result = [...rankedData];

        // Apply trend filter
        if (trendFilter !== 'ALL') {
            result = result.filter(r => r.weekly_trend === trendFilter);
        }

        // Apply return filters
        if (minReturn !== '') {
            const min = parseFloat(minReturn);
            result = result.filter(r => (r.weekly_return_pct || 0) >= min);
        }
        if (maxReturn !== '') {
            const max = parseFloat(maxReturn);
            result = result.filter(r => (r.weekly_return_pct || 0) <= max);
        }

        // Apply RSI filter
        if (rsiFilter === 'OVERSOLD') {
            result = result.filter(r => (r.weekly_rsi14 || 50) < 30);
        } else if (rsiFilter === 'OVERBOUGHT') {
            result = result.filter(r => (r.weekly_rsi14 || 50) > 70);
        } else if (rsiFilter === 'NEUTRAL') {
            result = result.filter(r => {
                const rsi = r.weekly_rsi14 || 50;
                return rsi >= 30 && rsi <= 70;
            });
        }

        // Apply sorting
        result.sort((a, b) => {
            let aVal: number | string = 0;
            let bVal: number | string = 0;

            switch (sortField) {
                case 'ticker':
                    aVal = a.ticker;
                    bVal = b.ticker;
                    break;
                case 'weekly_close':
                    aVal = a.weekly_close || 0;
                    bVal = b.weekly_close || 0;
                    break;
                case 'weekly_return_pct':
                    aVal = a.weekly_return_pct || 0;
                    bVal = b.weekly_return_pct || 0;
                    break;
                case 'return_4w':
                    aVal = a.return_4w || 0;
                    bVal = b.return_4w || 0;
                    break;
                case 'return_13w':
                    aVal = a.return_13w || 0;
                    bVal = b.return_13w || 0;
                    break;
                case 'weekly_rsi14':
                    aVal = a.weekly_rsi14 || 0;
                    bVal = b.weekly_rsi14 || 0;
                    break;
                case 'momentum_rank':
                    aVal = a.momentum_rank || 999;
                    bVal = b.momentum_rank || 999;
                    break;
            }

            if (typeof aVal === 'string') {
                return sortDirection === 'asc' 
                    ? aVal.localeCompare(bVal as string)
                    : (bVal as string).localeCompare(aVal);
            }
            
            return sortDirection === 'asc' ? aVal - (bVal as number) : (bVal as number) - aVal;
        });

        return result;
    }, [rankedData, sortField, sortDirection, trendFilter, minReturn, maxReturn, rsiFilter]);

    // Pagination calculations
    const totalPages = Math.ceil(filteredAndSortedData.length / rowsPerPage);
    const paginatedData = useMemo(() => {
        const startIndex = (currentPage - 1) * rowsPerPage;
        return filteredAndSortedData.slice(startIndex, startIndex + rowsPerPage);
    }, [filteredAndSortedData, currentPage, rowsPerPage]);

    // Reset to first page when filters change
    useMemo(() => {
        setCurrentPage(1);
    }, [trendFilter, minReturn, maxReturn, rsiFilter]);

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection(field === 'momentum_rank' ? 'asc' : 'desc');
        }
    };

    const SortIcon = ({ field }: { field: SortField }) => {
        if (sortField !== field) return <ArrowUpDown className="w-3 h-3 text-slate-600" />;
        return sortDirection === 'asc' 
            ? <ArrowUp className="w-3 h-3 text-blue-400" />
            : <ArrowDown className="w-3 h-3 text-blue-400" />;
    };

    const clearFilters = () => {
        setTrendFilter('ALL');
        setMinReturn('');
        setMaxReturn('');
        setRsiFilter('ALL');
    };

    const activeFiltersCount = [
        trendFilter !== 'ALL',
        minReturn !== '',
        maxReturn !== '',
        rsiFilter !== 'ALL'
    ].filter(Boolean).length;

    return (
        <div className="space-y-4">
            {/* Filter Controls */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowFilters(!showFilters)}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-all ${
                            showFilters || activeFiltersCount > 0
                                ? 'bg-blue-600 text-white'
                                : 'bg-slate-800 text-slate-400 hover:text-white'
                        }`}
                    >
                        <Filter className="w-3 h-3" />
                        Filters {activeFiltersCount > 0 && `(${activeFiltersCount})`}
                    </button>
                    {activeFiltersCount > 0 && (
                        <button
                            onClick={clearFilters}
                            className="flex items-center gap-1 px-2 py-1.5 rounded text-xs text-slate-400 hover:text-white"
                        >
                            <X className="w-3 h-3" />
                            Clear
                        </button>
                    )}
                </div>
                <div className="text-xs text-slate-500">
                    Showing {filteredAndSortedData.length} of {data.length} stocks
                </div>
            </div>

            {/* Filter Panel */}
            {showFilters && (
                <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                        <label className="text-xs text-slate-400 block mb-1">Trend</label>
                        <select
                            value={trendFilter}
                            onChange={(e) => setTrendFilter(e.target.value as TrendFilter)}
                            className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white"
                        >
                            <option value="ALL">All Trends</option>
                            <option value="UP">Uptrend</option>
                            <option value="DOWN">Downtrend</option>
                            <option value="SIDEWAYS">Sideways</option>
                        </select>
                    </div>
                    <div>
                        <label className="text-xs text-slate-400 block mb-1">RSI Zone</label>
                        <select
                            value={rsiFilter}
                            onChange={(e) => setRsiFilter(e.target.value as typeof rsiFilter)}
                            className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white"
                        >
                            <option value="ALL">All</option>
                            <option value="OVERSOLD">Oversold (&lt;30)</option>
                            <option value="NEUTRAL">Neutral (30-70)</option>
                            <option value="OVERBOUGHT">Overbought (&gt;70)</option>
                        </select>
                    </div>
                    <div>
                        <label className="text-xs text-slate-400 block mb-1">Min Return %</label>
                        <input
                            type="number"
                            value={minReturn}
                            onChange={(e) => setMinReturn(e.target.value)}
                            placeholder="-10"
                            className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white"
                        />
                    </div>
                    <div>
                        <label className="text-xs text-slate-400 block mb-1">Max Return %</label>
                        <input
                            type="number"
                            value={maxReturn}
                            onChange={(e) => setMaxReturn(e.target.value)}
                            placeholder="10"
                            className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white"
                        />
                    </div>
                </div>
            )}

            {/* Table */}
            <div className="overflow-x-auto pb-2">
                <table className="w-full text-left border-collapse min-w-[1200px]">
                    <thead>
                        <tr className="border-b border-slate-700 text-slate-400 text-xs">
                            <th 
                                className="p-3 font-medium cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('momentum_rank')}
                            >
                                <div className="flex items-center gap-1">
                                    <Trophy className="w-3 h-3 text-amber-500" />
                                    Rank
                                    <SortIcon field="momentum_rank" />
                                </div>
                            </th>
                            <th 
                                className="p-3 font-medium cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('ticker')}
                            >
                                <div className="flex items-center gap-1">
                                    Ticker
                                    <SortIcon field="ticker" />
                                </div>
                            </th>
                            <th className="p-3 font-medium">Trend</th>
                            <th 
                                className="p-3 font-medium text-right cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('weekly_close')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    Close
                                    <SortIcon field="weekly_close" />
                                </div>
                            </th>
                            <th 
                                className="p-3 font-medium text-right cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('weekly_return_pct')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    Wk Return
                                    <SortIcon field="weekly_return_pct" />
                                </div>
                            </th>
                            <th 
                                className="p-3 font-medium text-right cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('return_4w')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    4W
                                    <SortIcon field="return_4w" />
                                </div>
                            </th>
                            <th 
                                className="p-3 font-medium text-right cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('return_13w')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    13W
                                    <SortIcon field="return_13w" />
                                </div>
                            </th>
                            <th 
                                className="p-3 font-medium text-right cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('weekly_rsi14')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    RSI(14)
                                    <SortIcon field="weekly_rsi14" />
                                </div>
                            </th>
                            <th className="p-3 font-medium text-right">Volume Ratio</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm divide-y divide-slate-800">
                        {paginatedData.map((row) => (
                            <tr
                                key={`${row.ticker}-${row.week_ending}`}
                                className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                                onClick={() => onSelectStock(row.ticker)}
                            >
                                <td className="p-3">
                                    <span className={`inline-flex items-center justify-center w-8 h-6 rounded text-xs font-bold ${
                                        row.momentum_rank && row.momentum_rank <= 10 
                                            ? 'bg-amber-500/20 text-amber-400' 
                                            : row.momentum_rank && row.momentum_rank <= 25
                                            ? 'bg-blue-500/20 text-blue-400'
                                            : 'bg-slate-800 text-slate-400'
                                    }`}>
                                        #{row.momentum_rank}
                                    </span>
                                </td>
                                <td className="p-3 font-medium text-white">{row.ticker}</td>
                                <td className="p-3">
                                    <span className={`px-2 py-0.5 rounded text-xs ${
                                        row.weekly_trend === 'UP' ? 'bg-green-500/20 text-green-400' :
                                        row.weekly_trend === 'DOWN' ? 'bg-red-500/20 text-red-400' :
                                        'bg-slate-700 text-slate-300'
                                    }`}>
                                        {row.weekly_trend}
                                    </span>
                                </td>
                                <td className="p-3 text-right text-slate-300">
                                    ₹{row.weekly_close?.toFixed(2)}
                                </td>
                                <td className={`p-3 text-right font-medium ${
                                    (row.weekly_return_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                    {(row.weekly_return_pct || 0) > 0 ? '+' : ''}
                                    {row.weekly_return_pct?.toFixed(2)}%
                                </td>
                                <td className={`p-3 text-right ${
                                    (row.return_4w || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                    {(row.return_4w || 0) > 0 ? '+' : ''}{row.return_4w?.toFixed(2)}%
                                </td>
                                <td className={`p-3 text-right ${
                                    (row.return_13w || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                    {(row.return_13w || 0) > 0 ? '+' : ''}{row.return_13w?.toFixed(2)}%
                                </td>
                                <td className={`p-3 text-right ${
                                    (row.weekly_rsi14 || 0) > 70 ? 'text-red-400' : 
                                    (row.weekly_rsi14 || 0) < 30 ? 'text-green-400' : 'text-slate-300'
                                }`}>
                                    {row.weekly_rsi14?.toFixed(1)}
                                </td>
                                <td className={`p-3 text-right ${
                                    (row.weekly_volume_ratio || 0) > 1.5 ? 'text-blue-400' : 'text-slate-400'
                                }`}>
                                    {row.weekly_volume_ratio?.toFixed(2)}x
                                </td>
                            </tr>
                        ))}
                        {paginatedData.length === 0 && (
                            <tr>
                                <td colSpan={9} className="p-8 text-center text-slate-500">
                                    No stocks match the current filters.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between bg-slate-900/30 border border-slate-800 rounded-lg p-3">
                <div className="flex items-center gap-4">
                    <span className="text-xs text-slate-400">
                        Showing {((currentPage - 1) * rowsPerPage) + 1} - {Math.min(currentPage * rowsPerPage, filteredAndSortedData.length)} of {filteredAndSortedData.length}
                    </span>
                    <select
                        value={rowsPerPage}
                        onChange={(e) => { setRowsPerPage(Number(e.target.value)); setCurrentPage(1); }}
                        className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white"
                    >
                        <option value={10}>10 per page</option>
                        <option value={25}>25 per page</option>
                        <option value={50}>50 per page</option>
                        <option value={100}>100 per page</option>
                    </select>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setCurrentPage(1)}
                        disabled={currentPage === 1}
                        className="px-2 py-1 text-xs bg-slate-800 border border-slate-700 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700 text-slate-300"
                    >
                        First
                    </button>
                    <button
                        onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                        disabled={currentPage === 1}
                        className="px-3 py-1 text-xs bg-slate-800 border border-slate-700 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700 text-slate-300"
                    >
                        ←
                    </button>
                    <span className="text-xs text-slate-400 px-2">
                        Page {currentPage} of {totalPages}
                    </span>
                    <button
                        onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                        disabled={currentPage === totalPages}
                        className="px-3 py-1 text-xs bg-slate-800 border border-slate-700 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700 text-slate-300"
                    >
                        →
                    </button>
                    <button
                        onClick={() => setCurrentPage(totalPages)}
                        disabled={currentPage === totalPages}
                        className="px-2 py-1 text-xs bg-slate-800 border border-slate-700 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700 text-slate-300"
                    >
                        Last
                    </button>
                </div>
            </div>

            {/* Ranking Legend */}
            <div className="bg-slate-900/30 border border-slate-800 rounded-lg p-3">
                <div className="text-xs text-slate-400">
                    <strong className="text-slate-300">Momentum Rank</strong> is calculated using: 
                    4-Week Return (30%) + 13-Week Return (40%) + RSI Zone Score (20%) + Volume Confirmation (10%)
                </div>
            </div>
        </div>
    );
}
