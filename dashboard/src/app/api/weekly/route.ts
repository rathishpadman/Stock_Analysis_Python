import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const ticker = searchParams.get('ticker');
        const limit = searchParams.get('limit');

        let query = supabase.from('weekly_analysis').select('*');

        if (ticker) {
            query = query.eq('ticker', ticker);
        }

        // Default to latest week's data only for performance
        const { data: latestWeek } = await supabase
            .from('weekly_analysis')
            .select('week_ending')
            .order('week_ending', { ascending: false })
            .limit(1);

        if (latestWeek && latestWeek.length > 0 && !ticker) {
            query = query.eq('week_ending', latestWeek[0].week_ending);
        }

        query = query.order('weekly_return_pct', { ascending: false });

        if (limit) {
            query = query.limit(parseInt(limit));
        } else {
            query = query.limit(200);
        }

        const { data, error } = await query;

        if (error) {
            console.error('Weekly API Error:', error);
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        return NextResponse.json(data || []);
    } catch (err) {
        console.error('Weekly API Exception:', err);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
