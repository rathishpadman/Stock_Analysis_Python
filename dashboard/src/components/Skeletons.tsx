'use client';

import React from 'react';

interface SkeletonProps {
    className?: string;
    style?: React.CSSProperties;
}

export function Skeleton({ className = '', style }: SkeletonProps) {
    return (
        <div
            className={`animate-pulse bg-slate-700/50 rounded ${className}`}
            style={style}
        />
    );
}

export function ChartSkeleton({ height = 350 }: { height?: number }) {
    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <Skeleton className="h-5 w-48" />
                <Skeleton className="h-4 w-24" />
            </div>
            <Skeleton className={`w-full rounded-lg`} style={{ height: `${height}px` }} />
            <div className="flex justify-center gap-6 mt-4">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-3 w-16" />
            </div>
        </div>
    );
}

export function StockDetailSkeleton() {
    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Header Skeleton */}
            <div className="flex items-end justify-between border-b border-white/5 pb-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <Skeleton className="h-12 w-32" />
                        <Skeleton className="h-6 w-24 rounded-full" />
                    </div>
                    <Skeleton className="h-5 w-56" />
                </div>
                <div className="text-right">
                    <Skeleton className="h-10 w-28 mb-2" />
                    <Skeleton className="h-5 w-20 ml-auto" />
                </div>
            </div>

            {/* Charts Skeleton */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ChartSkeleton height={350} />
                <div className="space-y-6">
                    <ChartSkeleton height={180} />
                    <ChartSkeleton height={180} />
                </div>
            </div>

            {/* Analysis Matrix Skeleton */}
            <div className="space-y-6">
                <div className="flex items-center gap-4">
                    <Skeleton className="h-px flex-1" />
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-px flex-1" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                    {[1, 2, 3, 4].map(i => (
                        <div key={i} className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
                            <Skeleton className="h-4 w-24 mb-4" />
                            <div className="space-y-3">
                                {[1, 2, 3, 4, 5].map(j => (
                                    <div key={j} className="flex justify-between">
                                        <Skeleton className="h-3 w-20" />
                                        <Skeleton className="h-3 w-16" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export function TableRowSkeleton() {
    return (
        <tr className="animate-pulse">
            {[1, 2, 3, 4, 5, 6].map(i => (
                <td key={i} className="px-6 py-4">
                    <Skeleton className="h-4 w-full max-w-[100px]" />
                </td>
            ))}
        </tr>
    );
}

export function StatCardSkeleton() {
    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-3 animate-pulse">
            <Skeleton className="h-3 w-16 mb-2" />
            <Skeleton className="h-6 w-20" />
            <Skeleton className="h-2 w-12 mt-1" />
        </div>
    );
}

export function SeasonalityChartSkeleton() {
    return (
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <Skeleton className="h-5 w-48" />
                <div className="flex gap-3">
                    <Skeleton className="h-4 w-12" />
                    <Skeleton className="h-4 w-12" />
                    <Skeleton className="h-4 w-12" />
                </div>
            </div>
            <Skeleton className="w-full h-[300px] rounded-lg" />
        </div>
    );
}
