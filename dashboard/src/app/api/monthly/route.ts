import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const ticker = searchParams.get('ticker');
        const limit = searchParams.get('limit');

        let query = supabase.from('monthly_analysis').select('*');

        if (ticker) {
            query = query.eq('ticker', ticker);
        }

        // Default to latest month's data only for performance
        const { data: latestMonth } = await supabase
            .from('monthly_analysis')
            .select('month')
            .order('month', { ascending: false })
            .limit(1);

        if (latestMonth && latestMonth.length > 0 && !ticker) {
            query = query.eq('month', latestMonth[0].month);
        }

        query = query.order('monthly_return_pct', { ascending: false });

        if (limit) {
            query = query.limit(parseInt(limit));
        } else {
            query = query.limit(200);
        }

        const { data, error } = await query;

        if (error) {
            console.error('Monthly API Error:', error);
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        return NextResponse.json(data || []);
    } catch (err) {
        console.error('Monthly API Exception:', err);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
