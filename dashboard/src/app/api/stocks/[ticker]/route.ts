import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(
    request: Request,
    props: { params: Promise<{ ticker: string }> }
) {
    const params = await props.params;
    const { ticker } = params;

    // Get days parameter from query string (default 90, max 365)
    const url = new URL(request.url);
    const daysParam = url.searchParams.get('days');
    const days = Math.min(Math.max(parseInt(daysParam || '90', 10), 7), 365);

    // Fetch historical data for the specific ticker
    const { data, error } = await supabase
        .from('daily_stocks')
        .select('date, price:price_last, rsi:rsi14, sma20, sma50, sma200, macd_line, macd_signal, macd_hist, return_1d')
        .eq('ticker', ticker)
        .order('date', { ascending: true })
        .limit(days);

    if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json(data);
}
