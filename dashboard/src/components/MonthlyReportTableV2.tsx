'use client';

import React, { useState, useMemo } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown, Filter, X, Trophy, Search } from 'lucide-react';

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
    monthly_sma3?: number;
    monthly_sma6?: number;
    monthly_sma12?: number;
    monthly_trend?: string;
    return_3m?: number;
    return_6m?: number;
    return_12m?: number;
    ytd_return_pct?: number;
    positive_months_12m?: number;
    avg_monthly_return_12m?: number;
    best_month_return_12m?: number;
    worst_month_return_12m?: number;
    // Calculated rank
    performance_rank?: number;
}

interface MonthlyReportTableProps {
    data: MonthlyData[];
    onSelectStock: (ticker: string) => void;
}

type SortField = 'ticker' | 'monthly_close' | 'monthly_return_pct' | 'return_3m' | 'return_6m' | 'return_12m' | 'ytd_return_pct' | 'performance_rank';
type SortDirection = 'asc' | 'desc';
type TrendFilter = 'ALL' | 'UP' | 'DOWN' | 'SIDEWAYS';

// Calculate performance rank using industry-standard metrics
// Risk-adjusted return approach similar to Sharpe-like scoring
function calculatePerformanceRank(data: MonthlyData[]): MonthlyData[] {
    const scored = data.map(stock => {
        // Performance scoring factors
        const return3m = stock.return_3m || 0;
        const return6m = stock.return_6m || 0;
        const return12m = stock.return_12m || 0;
        const ytdReturn = stock.ytd_return_pct || 0;
        const positiveMonths = stock.positive_months_12m || 6;
        const avgMonthlyReturn = stock.avg_monthly_return_12m || 0;
        const bestMonth = stock.best_month_return_12m || 0;
        const worstMonth = stock.worst_month_return_12m || 0;

        // Consistency Score (positive months ratio) - 25% weight
        const consistencyScore = (positiveMonths / 12) * 100 * 0.25;

        // Medium-term momentum (6M return) - 25% weight
        const mediumTermScore = return6m * 0.25;

        // Long-term momentum (12M return) - 25% weight
        const longTermScore = return12m * 0.25;

        // Risk-adjusted score (drawdown consideration) - 25% weight
        // Lower drawdown (worst month) is better
        const drawdownPenalty = Math.abs(worstMonth || 0);
        const riskScore = (avgMonthlyReturn - (drawdownPenalty * 0.5)) * 0.25;

        const totalScore = consistencyScore + mediumTermScore + longTermScore + riskScore;

        return {
            ...stock,
            _performanceScore: totalScore
        };
    });

    // Sort by performance score and assign ranks
    const sorted = [...scored].sort((a, b) => (b._performanceScore || 0) - (a._performanceScore || 0));
    
    return sorted.map((stock, index) => ({
        ...stock,
        performance_rank: index + 1,
        _performanceScore: undefined
    }));
}

export default function MonthlyReportTableV2({ data, onSelectStock }: MonthlyReportTableProps) {
    const [sortField, setSortField] = useState<SortField>('performance_rank');
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
    const [trendFilter, setTrendFilter] = useState<TrendFilter>('ALL');
    const [showFilters, setShowFilters] = useState(false);
    const [minYtd, setMinYtd] = useState<string>('');
    const [minConsistency, setMinConsistency] = useState<string>('');
    const [searchQuery, setSearchQuery] = useState<string>('');
    
    // Pagination state
    const [currentPage, setCurrentPage] = useState(1);
    const [rowsPerPage, setRowsPerPage] = useState(25);

    // Calculate performance ranks
    const rankedData = useMemo(() => calculatePerformanceRank(data), [data]);

    // Apply filters and sorting
    const filteredAndSortedData = useMemo(() => {
        let result = [...rankedData];

        // Apply search filter
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            result = result.filter(r =>
                r.ticker.toLowerCase().includes(query) ||
                (r.company_name && r.company_name.toLowerCase().includes(query))
            );
        }

        // Apply trend filter
        if (trendFilter !== 'ALL') {
            result = result.filter(r => r.monthly_trend === trendFilter);
        }

        // Apply YTD filter
        if (minYtd !== '') {
            const min = parseFloat(minYtd);
            result = result.filter(r => (r.ytd_return_pct || 0) >= min);
        }

        // Apply consistency filter
        if (minConsistency !== '') {
            const min = parseInt(minConsistency);
            result = result.filter(r => (r.positive_months_12m || 0) >= min);
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
                case 'monthly_close':
                    aVal = a.monthly_close || 0;
                    bVal = b.monthly_close || 0;
                    break;
                case 'monthly_return_pct':
                    aVal = a.monthly_return_pct || 0;
                    bVal = b.monthly_return_pct || 0;
                    break;
                case 'return_3m':
                    aVal = a.return_3m || 0;
                    bVal = b.return_3m || 0;
                    break;
                case 'return_6m':
                    aVal = a.return_6m || 0;
                    bVal = b.return_6m || 0;
                    break;
                case 'return_12m':
                    aVal = a.return_12m || 0;
                    bVal = b.return_12m || 0;
                    break;
                case 'ytd_return_pct':
                    aVal = a.ytd_return_pct || 0;
                    bVal = b.ytd_return_pct || 0;
                    break;
                case 'performance_rank':
                    aVal = a.performance_rank || 999;
                    bVal = b.performance_rank || 999;
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
    }, [rankedData, sortField, sortDirection, searchQuery, trendFilter, minYtd, minConsistency]);

    // Pagination calculations
    const totalPages = Math.ceil(filteredAndSortedData.length / rowsPerPage);
    const paginatedData = useMemo(() => {
        const startIndex = (currentPage - 1) * rowsPerPage;
        return filteredAndSortedData.slice(startIndex, startIndex + rowsPerPage);
    }, [filteredAndSortedData, currentPage, rowsPerPage]);

    // Reset to first page when filters change
    useMemo(() => {
        setCurrentPage(1);
    }, [trendFilter, minYtd, minConsistency]);

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection(field === 'performance_rank' ? 'asc' : 'desc');
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
        setMinYtd('');
        setMinConsistency('');
    };

    const activeFiltersCount = [
        trendFilter !== 'ALL',
        minYtd !== '',
        minConsistency !== ''
    ].filter(Boolean).length;

    return (
        <div className="space-y-4">
            {/* Filter Controls */}
            <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                    {/* Search Bar */}
                    <div className="relative">
                        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Search ticker or company..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="bg-slate-800 border border-slate-700 rounded pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 w-48 focus:outline-none focus:border-blue-500"
                        />
                    </div>
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
                <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4 grid grid-cols-2 md:grid-cols-3 gap-4">
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
                        <label className="text-xs text-slate-400 block mb-1">Min YTD Return %</label>
                        <input
                            type="number"
                            value={minYtd}
                            onChange={(e) => setMinYtd(e.target.value)}
                            placeholder="0"
                            className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white"
                        />
                    </div>
                    <div>
                        <label className="text-xs text-slate-400 block mb-1">Min Positive Months (of 12)</label>
                        <input
                            type="number"
                            value={minConsistency}
                            onChange={(e) => setMinConsistency(e.target.value)}
                            placeholder="6"
                            min="0"
                            max="12"
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
                                onClick={() => handleSort('performance_rank')}
                            >
                                <div className="flex items-center gap-1">
                                    <Trophy className="w-3 h-3 text-amber-500" />
                                    Rank
                                    <SortIcon field="performance_rank" />
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
                                onClick={() => handleSort('monthly_close')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    Close
                                    <SortIcon field="monthly_close" />
                                </div>
                            </th>
                            <th 
                                className="p-3 font-medium text-right cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('monthly_return_pct')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    Month
                                    <SortIcon field="monthly_return_pct" />
                                </div>
                            </th>
                            <th 
                                className="p-3 font-medium text-right cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('return_3m')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    3M
                                    <SortIcon field="return_3m" />
                                </div>
                            </th>
                            <th 
                                className="p-3 font-medium text-right cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('return_6m')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    6M
                                    <SortIcon field="return_6m" />
                                </div>
                            </th>
                            <th 
                                className="p-3 font-medium text-right cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('return_12m')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    12M
                                    <SortIcon field="return_12m" />
                                </div>
                            </th>
                            <th 
                                className="p-3 font-medium text-right cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('ytd_return_pct')}
                            >
                                <div className="flex items-center justify-end gap-1">
                                    YTD
                                    <SortIcon field="ytd_return_pct" />
                                </div>
                            </th>
                            <th className="p-3 font-medium text-right">+ve Months</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm divide-y divide-slate-800">
                        {paginatedData.map((row) => (
                            <tr
                                key={`${row.ticker}-${row.month}`}
                                className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                                onClick={() => onSelectStock(row.ticker)}
                            >
                                <td className="p-3">
                                    <span className={`inline-flex items-center justify-center w-8 h-6 rounded text-xs font-bold ${
                                        row.performance_rank && row.performance_rank <= 10 
                                            ? 'bg-amber-500/20 text-amber-400' 
                                            : row.performance_rank && row.performance_rank <= 25
                                            ? 'bg-blue-500/20 text-blue-400'
                                            : 'bg-slate-800 text-slate-400'
                                    }`}>
                                        #{row.performance_rank}
                                    </span>
                                </td>
                                <td className="p-3 font-medium text-white">{row.ticker}</td>
                                <td className="p-3">
                                    <span className={`px-2 py-0.5 rounded text-xs ${
                                        row.monthly_trend === 'UP' ? 'bg-green-500/20 text-green-400' :
                                        row.monthly_trend === 'DOWN' ? 'bg-red-500/20 text-red-400' :
                                        'bg-slate-700 text-slate-300'
                                    }`}>
                                        {row.monthly_trend || 'N/A'}
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
                                <td className={`p-3 text-right font-medium ${
                                    (row.ytd_return_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                    {(row.ytd_return_pct || 0) > 0 ? '+' : ''}{row.ytd_return_pct?.toFixed(2)}%
                                </td>
                                <td className="p-3 text-right">
                                    <span className={`${
                                        (row.positive_months_12m || 0) >= 8 ? 'text-green-400' :
                                        (row.positive_months_12m || 0) >= 6 ? 'text-slate-300' :
                                        'text-red-400'
                                    }`}>
                                        {row.positive_months_12m || 0}/12
                                    </span>
                                </td>
                            </tr>
                        ))}
                        {paginatedData.length === 0 && (
                            <tr>
                                <td colSpan={10} className="p-8 text-center text-slate-500">
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
                    <strong className="text-slate-300">Performance Rank</strong> is calculated using: 
                    Consistency (25%) + 6M Return (25%) + 12M Return (25%) + Risk-Adjusted Score (25%)
                </div>
            </div>
        </div>
    );
}
