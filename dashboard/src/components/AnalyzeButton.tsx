'use client';

import React, { useState, useCallback } from 'react';
import { Activity, Clock, CheckCircle, Loader2 } from 'lucide-react';

interface AnalyzeButtonProps {
    ticker: string;
    onAnalyze: (ticker: string) => void;
    apiBaseUrl?: string;
}

interface CachedAnalysis {
    has_cached: boolean;
    analyzed_at?: string;
    cache_age_hours?: number;
    composite_score?: number;
    recommendation?: string;
    expires_in_hours?: number;
}

export default function AnalyzeButton({ ticker, onAnalyze, apiBaseUrl = '' }: AnalyzeButtonProps) {
    const [isHovering, setIsHovering] = useState(false);
    const [cachedInfo, setCachedInfo] = useState<CachedAnalysis | null>(null);
    const [loading, setLoading] = useState(false);

    const fetchCachedInfo = useCallback(async () => {
        if (cachedInfo !== null) return; // Already fetched
        setLoading(true);
        try {
            const backendUrl = process.env.NEXT_PUBLIC_AGENT_API_URL || 'https://nifty-agent-api.onrender.com';
            const res = await fetch(`${backendUrl}/api/agent/history/${ticker}`);
            if (res.ok) {
                const data = await res.json();
                setCachedInfo(data);
            }
        } catch (error) {
            console.error('Failed to fetch cached analysis:', error);
            setCachedInfo({ has_cached: false });
        } finally {
            setLoading(false);
        }
    }, [ticker, cachedInfo]);

    const handleMouseEnter = () => {
        setIsHovering(true);
        fetchCachedInfo();
    };

    const handleMouseLeave = () => {
        setIsHovering(false);
    };

    const formatTimeAgo = (hours: number) => {
        if (hours < 1) return 'less than an hour ago';
        if (hours < 24) return `${Math.round(hours)} hour${hours >= 2 ? 's' : ''} ago`;
        const days = Math.round(hours / 24);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    };

    return (
        <div className="relative">
            <button
                onClick={(e) => {
                    e.stopPropagation();
                    onAnalyze(ticker);
                }}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-white transition-all shadow-lg ${cachedInfo?.has_cached
                        ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-emerald-500/20 hover:shadow-emerald-500/40'
                        : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 shadow-blue-500/20 hover:shadow-blue-500/40'
                    }`}
            >
                {cachedInfo?.has_cached ? (
                    <CheckCircle className="w-3.5 h-3.5" />
                ) : (
                    <Activity className="w-3.5 h-3.5" />
                )}
                {cachedInfo?.has_cached ? 'View' : 'Analyze'}
            </button>

            {/* Tooltip */}
            {isHovering && (
                <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 animate-in fade-in zoom-in-95 duration-200">
                    <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-xl p-3 text-xs">
                        {loading ? (
                            <div className="flex items-center gap-2 text-slate-400">
                                <Loader2 className="w-3 h-3 animate-spin" />
                                Checking...
                            </div>
                        ) : cachedInfo?.has_cached ? (
                            <div className="space-y-2">
                                <div className="flex items-center gap-1.5 text-emerald-400">
                                    <Clock className="w-3 h-3" />
                                    <span>Analyzed {formatTimeAgo(cachedInfo.cache_age_hours || 0)}</span>
                                </div>
                                {cachedInfo.composite_score !== undefined && (
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Score:</span>
                                        <span className={`font-bold ${(cachedInfo.composite_score || 0) >= 60 ? 'text-emerald-400' :
                                                (cachedInfo.composite_score || 0) >= 40 ? 'text-amber-400' : 'text-rose-400'
                                            }`}>
                                            {cachedInfo.composite_score?.toFixed(1)}
                                        </span>
                                    </div>
                                )}
                                {cachedInfo.recommendation && (
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Signal:</span>
                                        <span className={`font-bold uppercase ${cachedInfo.recommendation?.toLowerCase().includes('buy') ? 'text-emerald-400' :
                                                cachedInfo.recommendation?.toLowerCase().includes('sell') ? 'text-rose-400' : 'text-amber-400'
                                            }`}>
                                            {cachedInfo.recommendation}
                                        </span>
                                    </div>
                                )}
                                <div className="text-slate-500 text-[10px] pt-1 border-t border-slate-700">
                                    Click to view full analysis
                                </div>
                            </div>
                        ) : (
                            <div className="text-slate-400">
                                <div className="flex items-center gap-1.5">
                                    <Activity className="w-3 h-3" />
                                    <span>No cached analysis</span>
                                </div>
                                <div className="text-slate-500 text-[10px] mt-1">
                                    Click to run AI analysis
                                </div>
                            </div>
                        )}
                        {/* Arrow */}
                        <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-slate-700" />
                    </div>
                </div>
            )}
        </div>
    );
}
