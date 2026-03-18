import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get('type') || 'daily';
    const periods = parseInt(searchParams.get('periods') || '5', 10);
    const top = parseInt(searchParams.get('top') || '10', 10);

    if (!['daily', 'weekly', 'monthly'].includes(type)) {
        return NextResponse.json({ error: 'Invalid type. Use daily, weekly, or monthly.' }, { status: 400 });
    }

    if (periods < 1 || periods > 30) {
        return NextResponse.json({ error: 'Periods must be between 1 and 30.' }, { status: 400 });
    }

    try {
        // 1. Get distinct period dates
        const { data: dateRows, error: dateError } = await supabase
            .from('score_history')
            .select('period_date')
            .eq('period_type', type)
            .order('period_date', { ascending: false });

        if (dateError) throw dateError;
        if (!dateRows || dateRows.length === 0) {
            return NextResponse.json({ periods: [], rankings: [], consistentTickers: [] });
        }

        // Deduplicate and take the requested number of periods
        const uniqueDates = [...new Set(dateRows.map(r => r.period_date))].slice(0, periods);

        // 2. Fetch all rows for those dates
        const { data: rows, error: rowsError } = await supabase
            .from('score_history')
            .select('*')
            .eq('period_type', type)
            .in('period_date', uniqueDates)
            .order('overall_score', { ascending: false });

        if (rowsError) throw rowsError;

        // 3. Group by period_date and take top N per period
        const byDate: Record<string, typeof rows> = {};
        for (const row of rows || []) {
            const d = row.period_date;
            if (!byDate[d]) byDate[d] = [];
            byDate[d].push(row);
        }

        // Rank within each period and take top N
        const topPerPeriod: Record<string, Set<string>> = {};
        const tickerScores: Record<string, Record<string, { score: number; rank: number }>> = {};

        for (const date of uniqueDates) {
            const periodRows = (byDate[date] || [])
                .filter(r => r.overall_score != null)
                .sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0));

            topPerPeriod[date] = new Set();

            periodRows.slice(0, top).forEach((row, idx) => {
                const ticker = row.ticker;
                topPerPeriod[date].add(ticker);

                if (!tickerScores[ticker]) tickerScores[ticker] = {};
                tickerScores[ticker][date] = {
                    score: Math.round((row.overall_score || 0) * 100) / 100,
                    rank: idx + 1,
                };
            });
        }

        // 4. Build rankings: union of all tickers that appeared in any period's top N
        const allTickers = Object.keys(tickerScores);
        const rankings = allTickers.map(ticker => {
            const scores = tickerScores[ticker];
            const appearances = Object.keys(scores).length;
            const avgScore = Object.values(scores).reduce((sum, s) => sum + s.score, 0) / appearances;
            const sector = (rows || []).find(r => r.ticker === ticker)?.sector || '';

            return {
                ticker,
                sector,
                scores,  // { [date]: { score, rank } }
                avgScore: Math.round(avgScore * 100) / 100,
                frequency: appearances,
                frequencyLabel: `${appearances}/${uniqueDates.length}`,
            };
        });

        // Sort by frequency desc, then avgScore desc
        rankings.sort((a, b) => b.frequency - a.frequency || b.avgScore - a.avgScore);

        // 5. Consistent tickers: appear in >= 60% of periods
        const threshold = Math.ceil(uniqueDates.length * 0.6);
        const consistentTickers = rankings
            .filter(r => r.frequency >= threshold)
            .map(r => r.ticker);

        return NextResponse.json({
            periods: uniqueDates,
            rankings,
            consistentTickers,
        });
    } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        return NextResponse.json({ error: message }, { status: 500 });
    }
}
