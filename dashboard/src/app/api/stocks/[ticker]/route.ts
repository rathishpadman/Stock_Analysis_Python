import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(
    request: Request,
    props: { params: Promise<{ ticker: string }> }
) {
    const params = await props.params;
    const { ticker } = params;

    // Fetch last 90 days of data for the specific ticker
    const { data, error } = await supabase
        .from('daily_stocks')
        .select('date, price:price_last, rsi:rsi14, sma20, sma50, sma200, macd_line, macd_signal')
        .eq('ticker', ticker)
        .order('date', { ascending: true })
        .limit(90);

    if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json(data);
}
