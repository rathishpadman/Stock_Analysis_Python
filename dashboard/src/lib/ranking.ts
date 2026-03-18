// Shared ranking utilities used by consistency tracker and table components

export interface MomentumInput {
    return_4w?: number;
    return_13w?: number;
    weekly_rsi14?: number;
    weekly_volume_ratio?: number;
}

export interface PerformanceInput {
    return_3m?: number;
    return_6m?: number;
    return_12m?: number;
    ytd_return_pct?: number;
    positive_months_12m?: number;
    avg_monthly_return_12m?: number;
    best_month_return_12m?: number;
    worst_month_return_12m?: number;
}

// Momentum Score = (0.30 * 4W Return) + (0.40 * 13W Return) + RSI adjustment + Volume confirmation
export function calculateMomentumScore(stock: MomentumInput): number {
    const return4w = stock.return_4w || 0;
    const return13w = stock.return_13w || 0;
    const rsi = stock.weekly_rsi14 || 50;
    const volumeRatio = stock.weekly_volume_ratio || 1;

    const shortTermScore = return4w * 0.30;
    const mediumTermScore = return13w * 0.40;

    let rsiScore = 0;
    if (rsi >= 40 && rsi <= 60) rsiScore = 10;
    else if (rsi > 60 && rsi <= 70) rsiScore = 5;
    else if (rsi >= 30 && rsi < 40) rsiScore = 5;
    else if (rsi > 70) rsiScore = -5;

    const volumeScore = volumeRatio > 1.2 ? 5 : volumeRatio > 1 ? 2 : 0;

    return shortTermScore + mediumTermScore + (rsiScore * 0.20) + (volumeScore * 0.10);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function calculateMomentumRank<T extends MomentumInput>(data: T[]): (T & { momentum_rank: number })[] {
    const scored = data.map(stock => ({
        stock,
        _score: calculateMomentumScore(stock),
    }));

    scored.sort((a, b) => b._score - a._score);

    return scored.map((item, index) => ({
        ...item.stock,
        momentum_rank: index + 1,
    }));
}

// Performance Score = Consistency (25%) + 6M return (25%) + 12M return (25%) + Risk-adjusted (25%)
export function calculatePerformanceScore(stock: PerformanceInput): number {
    const return6m = stock.return_6m || 0;
    const return12m = stock.return_12m || 0;
    const positiveMonths = stock.positive_months_12m || 6;
    const avgMonthlyReturn = stock.avg_monthly_return_12m || 0;
    const worstMonth = stock.worst_month_return_12m || 0;

    const consistencyScore = (positiveMonths / 12) * 100 * 0.25;
    const mediumTermScore = return6m * 0.25;
    const longTermScore = return12m * 0.25;
    const drawdownPenalty = Math.abs(worstMonth || 0);
    const riskScore = (avgMonthlyReturn - (drawdownPenalty * 0.5)) * 0.25;

    return consistencyScore + mediumTermScore + longTermScore + riskScore;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function calculatePerformanceRank<T extends PerformanceInput>(data: T[]): (T & { performance_rank: number })[] {
    const scored = data.map(stock => ({
        stock,
        _score: calculatePerformanceScore(stock),
    }));

    scored.sort((a, b) => b._score - a._score);

    return scored.map((item, index) => ({
        ...item.stock,
        performance_rank: index + 1,
    }));
}
