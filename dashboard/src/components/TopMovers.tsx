'use client';

import React from 'react';
import { TrendingUp, TrendingDown, Flame } from 'lucide-react';

interface Stock {
    ticker: string;
    company_name?: string;
    price_last?: number;
    return_1d?: number;
    return_1w?: number;
    volume_vs_3m_avg_pct?: number;
}

interface TopMoversProps {
    stocks: Stock[];
    onSelectStock: (ticker: string) => void;
}

export default function TopMovers({ stocks, onSelectStock }: TopMoversProps) {
    // Calculate top gainers and losers
    const sortedByReturn = [...stocks].filter(s => s.return_1d !== null && s.return_1d !== undefined);
    const topGainers = sortedByReturn.sort((a, b) => (b.return_1d || 0) - (a.return_1d || 0)).slice(0, 5);
    const topLosers = sortedByReturn.sort((a, b) => (a.return_1d || 0) - (b.return_1d || 0)).slice(0, 5);
    
    // High volume stocks
    const highVolume = [...stocks]
        .filter(s => s.volume_vs_3m_avg_pct && s.volume_vs_3m_avg_pct > 100)
        .sort((a, b) => (b.volume_vs_3m_avg_pct || 0) - (a.volume_vs_3m_avg_pct || 0))
        .slice(0, 5);

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Top Gainers */}
            <div className="bg-[#0a101f] border border-white/5 rounded-xl p-4">
                <h3 className="text-xs font-black text-emerald-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    TOP GAINERS
                </h3>
                <div className="space-y-2">
                    {topGainers.map((stock, idx) => (
                        <div
                            key={stock.ticker}
                            onClick={() => onSelectStock(stock.ticker)}
                            className="flex items-center justify-between p-2 rounded hover:bg-emerald-500/10 cursor-pointer transition-colors"
                        >
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-bold text-slate-600 w-4">{idx + 1}</span>
                                <div>
                                    <span className="text-sm font-bold text-white">{stock.ticker}</span>
                                    <span className="text-[10px] text-slate-500 ml-2">₹{stock.price_last?.toLocaleString()}</span>
                                </div>
                            </div>
                            <span className="text-sm font-mono font-bold text-emerald-400">
                                +{stock.return_1d?.toFixed(2)}%
                            </span>
                        </div>
                    ))}
                    {topGainers.length === 0 && (
                        <p className="text-slate-500 text-xs text-center py-4">No data available</p>
                    )}
                </div>
            </div>

            {/* Top Losers */}
            <div className="bg-[#0a101f] border border-white/5 rounded-xl p-4">
                <h3 className="text-xs font-black text-rose-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <TrendingDown className="h-4 w-4" />
                    TOP LOSERS
                </h3>
                <div className="space-y-2">
                    {topLosers.map((stock, idx) => (
                        <div
                            key={stock.ticker}
                            onClick={() => onSelectStock(stock.ticker)}
                            className="flex items-center justify-between p-2 rounded hover:bg-rose-500/10 cursor-pointer transition-colors"
                        >
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-bold text-slate-600 w-4">{idx + 1}</span>
                                <div>
                                    <span className="text-sm font-bold text-white">{stock.ticker}</span>
                                    <span className="text-[10px] text-slate-500 ml-2">₹{stock.price_last?.toLocaleString()}</span>
                                </div>
                            </div>
                            <span className="text-sm font-mono font-bold text-rose-400">
                                {stock.return_1d?.toFixed(2)}%
                            </span>
                        </div>
                    ))}
                    {topLosers.length === 0 && (
                        <p className="text-slate-500 text-xs text-center py-4">No data available</p>
                    )}
                </div>
            </div>

            {/* High Volume */}
            <div className="bg-[#0a101f] border border-white/5 rounded-xl p-4">
                <h3 className="text-xs font-black text-amber-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <Flame className="h-4 w-4" />
                    HIGH VOLUME
                </h3>
                <div className="space-y-2">
                    {highVolume.map((stock, idx) => (
                        <div
                            key={stock.ticker}
                            onClick={() => onSelectStock(stock.ticker)}
                            className="flex items-center justify-between p-2 rounded hover:bg-amber-500/10 cursor-pointer transition-colors"
                        >
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-bold text-slate-600 w-4">{idx + 1}</span>
                                <div>
                                    <span className="text-sm font-bold text-white">{stock.ticker}</span>
                                    <span className={`text-[10px] ml-2 ${(stock.return_1d || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                        {(stock.return_1d || 0) >= 0 ? '+' : ''}{stock.return_1d?.toFixed(2)}%
                                    </span>
                                </div>
                            </div>
                            <span className="text-sm font-mono font-bold text-amber-400">
                                {stock.volume_vs_3m_avg_pct?.toFixed(0)}%
                            </span>
                        </div>
                    ))}
                    {highVolume.length === 0 && (
                        <p className="text-slate-500 text-xs text-center py-4">No unusual volume</p>
                    )}
                </div>
            </div>
        </div>
    );
}
