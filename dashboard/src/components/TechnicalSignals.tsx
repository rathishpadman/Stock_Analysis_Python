'use client';

import React from 'react';
import { AlertTriangle, TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface Stock {
    ticker: string;
    company_name?: string;
    price_last?: number;
    rsi14?: number;
    macd_line?: number;
    macd_signal?: number;
    macd_hist?: number;
    sma20?: number;
    sma50?: number;
    sma200?: number;
    adx14?: number;
    stoch_k?: number;
    stoch_d?: number;
    bb_upper?: number;
    bb_lower?: number;
}

interface TechnicalSignalsProps {
    stocks: Stock[];
    onSelectStock: (ticker: string) => void;
}

export default function TechnicalSignals({ stocks, onSelectStock }: TechnicalSignalsProps) {
    // RSI Overbought (>70)
    const overbought = stocks
        .filter(s => s.rsi14 && s.rsi14 > 70)
        .sort((a, b) => (b.rsi14 || 0) - (a.rsi14 || 0))
        .slice(0, 8);

    // RSI Oversold (<30)
    const oversold = stocks
        .filter(s => s.rsi14 && s.rsi14 < 30)
        .sort((a, b) => (a.rsi14 || 0) - (b.rsi14 || 0))
        .slice(0, 8);

    // MACD Bullish Crossover (MACD > Signal and histogram positive)
    const macdBullish = stocks
        .filter(s => s.macd_line && s.macd_signal && s.macd_line > s.macd_signal && (s.macd_hist || 0) > 0)
        .sort((a, b) => (b.macd_hist || 0) - (a.macd_hist || 0))
        .slice(0, 8);

    // MACD Bearish (MACD < Signal)
    const macdBearish = stocks
        .filter(s => s.macd_line && s.macd_signal && s.macd_line < s.macd_signal && (s.macd_hist || 0) < 0)
        .sort((a, b) => (a.macd_hist || 0) - (b.macd_hist || 0))
        .slice(0, 8);

    // Golden Cross (SMA50 > SMA200 and price > SMA200)
    const goldenCross = stocks
        .filter(s => s.sma50 && s.sma200 && s.price_last && s.sma50 > s.sma200 && s.price_last > s.sma200)
        .slice(0, 8);

    // Death Cross (SMA50 < SMA200)
    const deathCross = stocks
        .filter(s => s.sma50 && s.sma200 && s.sma50 < s.sma200)
        .slice(0, 8);

    // Strong Trend (ADX > 25)
    const strongTrend = stocks
        .filter(s => s.adx14 && s.adx14 > 25)
        .sort((a, b) => (b.adx14 || 0) - (a.adx14 || 0))
        .slice(0, 8);

    // Bollinger Band Breakouts
    const bbBreakoutUp = stocks
        .filter(s => s.price_last && s.bb_upper && s.price_last > s.bb_upper)
        .slice(0, 8);

    const bbBreakoutDown = stocks
        .filter(s => s.price_last && s.bb_lower && s.price_last < s.bb_lower)
        .slice(0, 8);

    const SignalCard = ({ 
        title, 
        icon: Icon, 
        color, 
        bgColor,
        data, 
        metric, 
        metricLabel 
    }: { 
        title: string; 
        icon: React.ComponentType<{ className?: string }>; 
        color: string;
        bgColor: string;
        data: Stock[]; 
        metric: (s: Stock) => number | undefined;
        metricLabel: string;
    }) => (
        <div className={`bg-[#0a101f] border border-white/5 rounded-lg p-3`}>
            <h4 className={`text-[10px] font-black uppercase tracking-widest mb-2 flex items-center gap-1 ${color}`}>
                <Icon className="h-3 w-3" />
                {title}
                <span className="ml-auto bg-slate-800 px-1.5 py-0.5 rounded text-slate-400">{data.length}</span>
            </h4>
            <div className="space-y-1 max-h-32 overflow-y-auto">
                {data.map(stock => (
                    <div
                        key={stock.ticker}
                        onClick={() => onSelectStock(stock.ticker)}
                        className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors ${bgColor}`}
                    >
                        <span className="text-[11px] font-bold text-white">{stock.ticker}</span>
                        <span className={`text-[10px] font-mono ${color}`}>
                            {metric(stock)?.toFixed(1)} {metricLabel}
                        </span>
                    </div>
                ))}
                {data.length === 0 && (
                    <p className="text-slate-600 text-[10px] text-center py-2">None detected</p>
                )}
            </div>
        </div>
    );

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
                <Activity className="h-5 w-5 text-blue-500" />
                <h3 className="text-sm font-bold text-white">TECHNICAL SIGNALS SCANNER</h3>
                <span className="text-[10px] text-slate-500 ml-2">Real-time pattern detection across {stocks.length} stocks</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <SignalCard
                    title="RSI OVERBOUGHT"
                    icon={AlertTriangle}
                    color="text-rose-400"
                    bgColor="hover:bg-rose-500/10"
                    data={overbought}
                    metric={s => s.rsi14}
                    metricLabel="RSI"
                />
                <SignalCard
                    title="RSI OVERSOLD"
                    icon={AlertTriangle}
                    color="text-emerald-400"
                    bgColor="hover:bg-emerald-500/10"
                    data={oversold}
                    metric={s => s.rsi14}
                    metricLabel="RSI"
                />
                <SignalCard
                    title="MACD BULLISH"
                    icon={TrendingUp}
                    color="text-emerald-400"
                    bgColor="hover:bg-emerald-500/10"
                    data={macdBullish}
                    metric={s => s.macd_hist}
                    metricLabel="Hist"
                />
                <SignalCard
                    title="MACD BEARISH"
                    icon={TrendingDown}
                    color="text-rose-400"
                    bgColor="hover:bg-rose-500/10"
                    data={macdBearish}
                    metric={s => s.macd_hist}
                    metricLabel="Hist"
                />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <SignalCard
                    title="GOLDEN CROSS"
                    icon={TrendingUp}
                    color="text-amber-400"
                    bgColor="hover:bg-amber-500/10"
                    data={goldenCross}
                    metric={s => s.sma50 && s.sma200 ? ((s.sma50 / s.sma200 - 1) * 100) : 0}
                    metricLabel="%"
                />
                <SignalCard
                    title="DEATH CROSS"
                    icon={TrendingDown}
                    color="text-slate-400"
                    bgColor="hover:bg-slate-500/10"
                    data={deathCross}
                    metric={s => s.sma50 && s.sma200 ? ((s.sma50 / s.sma200 - 1) * 100) : 0}
                    metricLabel="%"
                />
                <SignalCard
                    title="STRONG TREND"
                    icon={Activity}
                    color="text-blue-400"
                    bgColor="hover:bg-blue-500/10"
                    data={strongTrend}
                    metric={s => s.adx14}
                    metricLabel="ADX"
                />
                <SignalCard
                    title="BB BREAKOUT ↑"
                    icon={TrendingUp}
                    color="text-purple-400"
                    bgColor="hover:bg-purple-500/10"
                    data={bbBreakoutUp}
                    metric={s => s.price_last && s.bb_upper ? ((s.price_last / s.bb_upper - 1) * 100) : 0}
                    metricLabel="%"
                />
            </div>
        </div>
    );
}
