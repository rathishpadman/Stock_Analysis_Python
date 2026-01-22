import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
function getSupabaseClient() {
    const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!url || !key) {
        throw new Error('Supabase credentials not configured');
    }

    return createClient(url, key);
}

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ ticker: string }> }
) {
    try {
        const { ticker } = await params;
        const tickerClean = ticker.toUpperCase().replace('.NS', '');

        const supabase = getSupabaseClient();

        // Fetch analysis history for this ticker, most recent first
        const { data, error } = await supabase
            .from('ai_analysis_history')
            .select('id, ticker, analyzed_at, composite_score, recommendation, signal, cost_usd, synthesis')
            .eq('ticker', tickerClean)
            .order('analyzed_at', { ascending: false })
            .limit(10);

        if (error) {
            console.error('Supabase error:', error);
            return NextResponse.json(
                { error: 'Failed to fetch analysis history', details: error.message },
                { status: 500 }
            );
        }

        // Format the results
        const history = (data || []).map(item => ({
            id: item.id,
            ticker: item.ticker,
            analyzed_at: item.analyzed_at,
            composite_score: item.composite_score,
            recommendation: item.recommendation,
            signal: item.signal,
            cost_usd: item.cost_usd,
            synthesis_summary: item.synthesis?.overall_recommendation || item.synthesis?.recommendation
        }));

        return NextResponse.json({
            ticker: tickerClean,
            history_count: history.length,
            history
        });

    } catch (error) {
        console.error('Error fetching analysis history:', error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}
