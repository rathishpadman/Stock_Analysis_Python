'use client';

import React, { useState, useMemo } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown, Filter, X, Trophy, Calendar, Search } from 'lucide-react';

interface SeasonalityData {
    ticker: string;
    company_name?: string;
    jan_avg: number;
    feb_avg: number;
    mar_avg: number;
    apr_avg: number;
    may_avg: number;
    jun_avg: number;
    jul_avg: number;
    aug_avg: number;
    sep_avg: number;
    oct_avg: number;
    nov_avg: number;
    dec_avg: number;
    best_month?: string;
    worst_month?: string;
    // Calculated fields
    seasonality_rank?: number;
    annual_avg?: number;
    positive_months_count?: number;
}

interface SeasonalityHeatmapProps {
    data: SeasonalityData[];
    onSelectStock: (ticker: string) => void;
}

type SortField = 'ticker' | 'annual_avg' | 'positive_months_count' | 'seasonality_rank' | 'current_month';
type SortDirection = 'asc' | 'desc';

const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Get color class based on return value
function getReturnColor(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'bg-slate-800 text-slate-500';
    if (value >= 5) return 'bg-emerald-500/40 text-emerald-300';
    if (value >= 2) return 'bg-emerald-500/25 text-emerald-400';
    if (value >= 0) return 'bg-emerald-500/10 text-emerald-500';
    if (value >= -2) return 'bg-rose-500/10 text-rose-500';
    if (value >= -5) return 'bg-rose-500/25 text-rose-400';
    return 'bg-rose-500/40 text-rose-300';
}

// Calculate seasonality rank based on consistency and opportunity
function calculateSeasonalityRank(data: SeasonalityData[]): SeasonalityData[] {
    const currentMonth = new Date().getMonth(); // 0-11
    
    const scored = data.map(stock => {
        const monthValues = MONTHS.map(m => stock[`${m}_avg` as keyof SeasonalityData] as number || 0);
        
        // Count positive months
        const positiveMonths = monthValues.filter(v => v > 0).length;
        
        // Calculate annual average
        const annualAvg = monthValues.reduce((a, b) => a + b, 0) / 12;
        
        // Current month performance (for timing)
        const currentMonthReturn = monthValues[currentMonth] || 0;
        
        // Next 3 months average (forward-looking)
        const next3Months = [0, 1, 2].map(i => monthValues[(currentMonth + i) % 12]);
        const next3Avg = next3Months.reduce((a, b) => a + b, 0) / 3;
        
        // Scoring:
        // 1. Consistency (positive months) - 30%
        // 2. Annual average return - 30%
        // 3. Current month return - 20%
        // 4. Next 3 months outlook - 20%
        
        const consistencyScore = (positiveMonths / 12) * 100 * 0.30;
        const annualScore = annualAvg * 0.30;
        const currentScore = currentMonthReturn * 0.20;
        const outlookScore = next3Avg * 0.20;
        
        const totalScore = consistencyScore + annualScore + currentScore + outlookScore;
        
        return {
            ...stock,
            annual_avg: annualAvg,
            positive_months_count: positiveMonths,
            _seasonalityScore: totalScore
        };
    });
    
    // Sort and rank
    const sorted = [...scored].sort((a, b) => (b._seasonalityScore || 0) - (a._seasonalityScore || 0));
    
    return sorted.map((stock, index) => ({
        ...stock,
        seasonality_rank: index + 1,
        _seasonalityScore: undefined
    }));
}

export default function SeasonalityHeatmapV2({ data, onSelectStock }: SeasonalityHeatmapProps) {
    const [sortField, setSortField] = useState<SortField>('seasonality_rank');
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
    const [showFilters, setShowFilters] = useState(false);
    const [minPositiveMonths, setMinPositiveMonths] = useState<string>('');
    const [highlightMonth, setHighlightMonth] = useState<string>('current');
    const [searchQuery, setSearchQuery] = useState<string>('');
    
    // Pagination state
    const [currentPage, setCurrentPage] = useState(1);
    const [rowsPerPage, setRowsPerPage] = useState(25);

    const currentMonth = new Date().getMonth();

    // Calculate ranks
    const rankedData = useMemo(() => calculateSeasonalityRank(data), [data]);

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

        // Apply positive months filter
        if (minPositiveMonths !== '') {
            const min = parseInt(minPositiveMonths);
            result = result.filter(r => (r.positive_months_count || 0) >= min);
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
                case 'annual_avg':
                    aVal = a.annual_avg || 0;
                    bVal = b.annual_avg || 0;
                    break;
                case 'positive_months_count':
                    aVal = a.positive_months_count || 0;
                    bVal = b.positive_months_count || 0;
                    break;
                case 'seasonality_rank':
                    aVal = a.seasonality_rank || 999;
                    bVal = b.seasonality_rank || 999;
                    break;
                case 'current_month':
                    const monthKey = `${MONTHS[currentMonth]}_avg` as keyof SeasonalityData;
                    aVal = (a[monthKey] as number) || 0;
                    bVal = (b[monthKey] as number) || 0;
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
    }, [rankedData, sortField, sortDirection, searchQuery, minPositiveMonths, currentMonth]);

    // Pagination calculations
    const totalPages = Math.ceil(filteredAndSortedData.length / rowsPerPage);
    const paginatedData = useMemo(() => {
        const startIndex = (currentPage - 1) * rowsPerPage;
        return filteredAndSortedData.slice(startIndex, startIndex + rowsPerPage);
    }, [filteredAndSortedData, currentPage, rowsPerPage]);

    // Reset to first page when filters change
    useMemo(() => {
        setCurrentPage(1);
    }, [minPositiveMonths]);

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection(field === 'seasonality_rank' ? 'asc' : 'desc');
        }
    };

    const SortIcon = ({ field }: { field: SortField }) => {
        if (sortField !== field) return <ArrowUpDown className="w-3 h-3 text-slate-600" />;
        return sortDirection === 'asc' 
            ? <ArrowUp className="w-3 h-3 text-blue-400" />
            : <ArrowDown className="w-3 h-3 text-blue-400" />;
    };

    const clearFilters = () => {
        setMinPositiveMonths('');
        setHighlightMonth('current');
    };

    const activeFiltersCount = [
        minPositiveMonths !== ''
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
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 text-xs">
                        <Calendar className="w-3 h-3 text-blue-400" />
                        <span className="text-slate-400">Current: </span>
                        <span className="text-white font-medium">{MONTH_LABELS[currentMonth]}</span>
                    </div>
                    <div className="text-xs text-slate-500">
                        {filteredAndSortedData.length} stocks
                    </div>
                </div>
            </div>

            {/* Filter Panel */}
            {showFilters && (
                <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4 grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div>
                        <label className="text-xs text-slate-400 block mb-1">Min Positive Months</label>
                        <input
                            type="number"
                            value={minPositiveMonths}
                            onChange={(e) => setMinPositiveMonths(e.target.value)}
                            placeholder="6"
                            min="0"
                            max="12"
                            className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white"
                        />
                    </div>
                    <div>
                        <label className="text-xs text-slate-400 block mb-1">Highlight Month</label>
                        <select
                            value={highlightMonth}
                            onChange={(e) => setHighlightMonth(e.target.value)}
                            className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white"
                        >
                            <option value="current">Current ({MONTH_LABELS[currentMonth]})</option>
                            {MONTH_LABELS.map((m, i) => (
                                <option key={m} value={MONTHS[i]}>{m}</option>
                            ))}
                        </select>
                    </div>
                </div>
            )}

            {/* Color Legend */}
            <div className="flex items-center gap-4 text-xs">
                <span className="text-slate-400">Returns:</span>
                <div className="flex items-center gap-1">
                    <span className="w-4 h-4 rounded bg-rose-500/40"></span>
                    <span className="text-slate-500">&lt;-5%</span>
                </div>
                <div className="flex items-center gap-1">
                    <span className="w-4 h-4 rounded bg-rose-500/10"></span>
                    <span className="text-slate-500">-5 to 0%</span>
                </div>
                <div className="flex items-center gap-1">
                    <span className="w-4 h-4 rounded bg-emerald-500/10"></span>
                    <span className="text-slate-500">0 to 2%</span>
                </div>
                <div className="flex items-center gap-1">
                    <span className="w-4 h-4 rounded bg-emerald-500/25"></span>
                    <span className="text-slate-500">2 to 5%</span>
                </div>
                <div className="flex items-center gap-1">
                    <span className="w-4 h-4 rounded bg-emerald-500/40"></span>
                    <span className="text-slate-500">&gt;5%</span>
                </div>
            </div>

            {/* Heatmap Table */}
            <div className="overflow-x-auto pb-2">
                <table className="w-full text-left border-collapse min-w-[900px]">
                    <thead>
                        <tr className="border-b border-slate-700 text-slate-400 text-xs">
                            <th 
                                className="p-2 font-medium cursor-pointer hover:text-white transition-colors sticky left-0 bg-[#05080f] z-10"
                                onClick={() => handleSort('seasonality_rank')}
                            >
                                <div className="flex items-center gap-1">
                                    <Trophy className="w-3 h-3 text-amber-500" />
                                    <SortIcon field="seasonality_rank" />
                                </div>
                            </th>
                            <th 
                                className="p-2 font-medium cursor-pointer hover:text-white transition-colors sticky left-10 bg-[#05080f] z-10"
                                onClick={() => handleSort('ticker')}
                            >
                                <div className="flex items-center gap-1">
                                    Ticker
                                    <SortIcon field="ticker" />
                                </div>
                            </th>
                            {MONTH_LABELS.map((m, i) => (
                                <th 
                                    key={m}
                                    className={`p-2 font-medium text-center min-w-[50px] ${
                                        i === currentMonth ? 'bg-blue-600/20 text-blue-400' : ''
                                    }`}
                                >
                                    {m}
                                </th>
                            ))}
                            <th 
                                className="p-2 font-medium text-center cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('annual_avg')}
                            >
                                <div className="flex items-center justify-center gap-1">
                                    Avg
                                    <SortIcon field="annual_avg" />
                                </div>
                            </th>
                            <th 
                                className="p-2 font-medium text-center cursor-pointer hover:text-white transition-colors"
                                onClick={() => handleSort('positive_months_count')}
                            >
                                <div className="flex items-center justify-center gap-1">
                                    +ve
                                    <SortIcon field="positive_months_count" />
                                </div>
                            </th>
                        </tr>
                    </thead>
                    <tbody className="text-xs divide-y divide-slate-800">
                        {paginatedData.map((row) => (
                            <tr
                                key={row.ticker}
                                className="hover:bg-slate-800/30 cursor-pointer transition-colors"
                                onClick={() => onSelectStock(row.ticker)}
                            >
                                <td className="p-2 sticky left-0 bg-[#05080f]">
                                    <span className={`inline-flex items-center justify-center w-6 h-5 rounded text-[10px] font-bold ${
                                        row.seasonality_rank && row.seasonality_rank <= 10 
                                            ? 'bg-amber-500/20 text-amber-400' 
                                            : row.seasonality_rank && row.seasonality_rank <= 25
                                            ? 'bg-blue-500/20 text-blue-400'
                                            : 'bg-slate-800 text-slate-500'
                                    }`}>
                                        {row.seasonality_rank}
                                    </span>
                                </td>
                                <td className="p-2 font-medium text-white sticky left-10 bg-[#05080f]">
                                    {row.ticker}
                                </td>
                                {MONTHS.map((m, i) => {
                                    const val = row[`${m}_avg` as keyof SeasonalityData] as number;
                                    const isCurrentMonth = i === currentMonth;
                                    return (
                                        <td 
                                            key={m}
                                            className={`p-2 text-center ${getReturnColor(val)} ${
                                                isCurrentMonth ? 'ring-1 ring-blue-500' : ''
                                            }`}
                                        >
                                            {val !== null && val !== undefined ? `${val >= 0 ? '+' : ''}${val.toFixed(1)}` : '-'}
                                        </td>
                                    );
                                })}
                                <td className={`p-2 text-center font-medium ${
                                    (row.annual_avg || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                    {row.annual_avg?.toFixed(1)}%
                                </td>
                                <td className={`p-2 text-center ${
                                    (row.positive_months_count || 0) >= 8 ? 'text-green-400' :
                                    (row.positive_months_count || 0) >= 6 ? 'text-slate-300' : 'text-red-400'
                                }`}>
                                    {row.positive_months_count}/12
                                </td>
                            </tr>
                        ))}
                        {paginatedData.length === 0 && (
                            <tr>
                                <td colSpan={16} className="p-8 text-center text-slate-500">
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
                    <strong className="text-slate-300">Seasonality Rank</strong> is calculated using: 
                    Consistency (30%) + Annual Avg Return (30%) + Current Month (20%) + Next 3 Months Outlook (20%)
                </div>
            </div>
        </div>
    );
}
