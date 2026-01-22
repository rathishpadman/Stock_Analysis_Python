import React, { useState, useMemo } from 'react';
import { ALL_FIELDS } from '@/lib/constants';
import { ChevronUp, ChevronDown } from 'lucide-react';
import AnalyzeButton from './AnalyzeButton';

interface Stock {
    ticker: string;
    company_name: string;
    [key: string]: any;
}

interface StockTableProps {
    stocks: Stock[];
    visibleColumns: string[];
    onSelectStock?: (ticker: string) => void;
    onRequestAnalysis?: (ticker: string) => void;  // New: AI Analysis callback
    timeframe?: '1d' | '1w' | '1m';
}

export default function StockTable({ stocks, visibleColumns, onSelectStock, onRequestAnalysis, timeframe = '1d' }: StockTableProps) {
    const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
    const [selectedTicker, setSelectedTicker] = useState<string | null>(null);

    // Pagination state
    const [currentPage, setCurrentPage] = useState(1);
    const [rowsPerPage, setRowsPerPage] = useState(25);

    const columns = ALL_FIELDS.filter(f => visibleColumns.includes(f.id));

    const sortedStocks = useMemo(() => {
        if (!sortConfig) return stocks;
        return [...stocks].sort((a, b) => {
            const aVal = a[sortConfig.key];
            const bVal = b[sortConfig.key];
            if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
            return 0;
        });
    }, [stocks, sortConfig]);

    // Pagination calculations
    const totalPages = Math.ceil(sortedStocks.length / rowsPerPage);
    const paginatedStocks = useMemo(() => {
        const startIndex = (currentPage - 1) * rowsPerPage;
        return sortedStocks.slice(startIndex, startIndex + rowsPerPage);
    }, [sortedStocks, currentPage, rowsPerPage]);

    const requestSort = (key: string) => {
        let direction: 'asc' | 'desc' = 'asc';
        if (sortConfig?.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    return (
        <div className="space-y-4">
            <div className="overflow-x-auto rounded-lg border border-slate-700 bg-slate-900 shadow-xl pb-2">
                <table className="min-w-full divide-y divide-slate-700">
                    <thead className="bg-slate-800/50 backdrop-blur-sm sticky top-0">
                        <tr>
                            {columns.map(col => (
                                <th
                                    key={col.id}
                                    onClick={() => requestSort(col.id)}
                                    className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-slate-400 whitespace-nowrap cursor-pointer hover:text-white transition-colors group"
                                >
                                    <div className="flex items-center gap-2">
                                        {col.label}
                                        <span className="opacity-0 group-hover:opacity-100 transition-opacity">
                                            {sortConfig?.key === col.id ? (
                                                sortConfig.direction === 'asc' ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />
                                            ) : (
                                                <ChevronUp className="h-3 w-3 text-slate-600" />
                                            )}
                                        </span>
                                    </div>
                                </th>
                            ))}
                            {/* Actions column for AI Analysis */}
                            {onRequestAnalysis && (
                                <th className="px-4 py-4 text-center text-xs font-bold uppercase tracking-wider text-slate-400 whitespace-nowrap">
                                    AI Analysis
                                </th>
                            )}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 bg-slate-900">
                        {paginatedStocks.map((stock) => (
                            <tr
                                key={stock.ticker}
                                onClick={() => {
                                    setSelectedTicker(stock.ticker);
                                    onSelectStock?.(stock.ticker);
                                }}
                                className={`hover:bg-slate-800/60 transition-colors cursor-pointer group ${selectedTicker === stock.ticker ? 'bg-blue-900/20 border-l-2 border-l-blue-600' : ''}`}
                            >
                                {columns.map(col => (
                                    <td key={col.id} className="whitespace-nowrap px-6 py-4 text-sm font-medium">
                                        {renderCell(stock, col.id, timeframe)}
                                    </td>
                                ))}
                                {/* AI Analysis Button */}
                                {onRequestAnalysis && (
                                    <td className="whitespace-nowrap px-4 py-4 text-center">
                                        <AnalyzeButton
                                            ticker={stock.ticker}
                                            onAnalyze={onRequestAnalysis}
                                        />
                                    </td>
                                )}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between bg-slate-900/30 border border-slate-800 rounded-lg p-3">
                <div className="flex items-center gap-4">
                    <span className="text-xs text-slate-400">
                        Showing {((currentPage - 1) * rowsPerPage) + 1} - {Math.min(currentPage * rowsPerPage, sortedStocks.length)} of {sortedStocks.length}
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
        </div>
    );
}

function renderCell(stock: any, colId: string, timeframe: '1d' | '1w' | '1m' = '1d') {
    // Dynamic override for Return column
    let lookupId = colId;
    if (colId === 'return_1d') {
        if (timeframe === '1w') lookupId = 'return_1w';
        if (timeframe === '1m') lookupId = 'return_1m';
    }
    const value = stock[lookupId];

    if (colId === 'ticker') return <span className="font-bold text-white tracking-tight group-hover:text-blue-400 transition-colors">{value}</span>;
    if (colId === 'company_name') return <span className="text-slate-300 group-hover:text-white transition-colors">{value}</span>;

    if (colId === 'overall_score') {
        return (
            <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold shadow-sm ${(value ?? 0) > 70 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                (value ?? 0) > 40 ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                    'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                {value?.toFixed(1) ?? '-'}
            </span>
        );
    }

    if (colId.toLowerCase().includes('return') || colId === 'roi') {
        const isPos = (value ?? 0) >= 0;
        return (
            <span className={`font-mono ${isPos ? 'text-emerald-400' : 'text-rose-400'}`}>
                {isPos ? '+' : ''}{value?.toFixed(2)}%
            </span>
        );
    }

    if (typeof value === 'number') return <span className="text-slate-100 font-mono">{value.toLocaleString()}</span>;

    return <span className="text-slate-400">{value ?? '-'}</span>;
}
