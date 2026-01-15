import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const dateParam = searchParams.get('date');

    let query = supabase
        .from('daily_stocks')
        .select('*');

    if (dateParam) {
        query = query.eq('date', dateParam);
    } else {
        // Get the most recent date available in the DB
        const { data: latestDateObj } = await supabase
            .from('daily_stocks')
            .select('date')
            .order('date', { ascending: false })
            .limit(1);

        if (latestDateObj && latestDateObj.length > 0) {
            query = query.eq('date', latestDateObj[0].date);
        }
    }

    const { data, error } = await query
        .order('overall_score', { ascending: false })
        .limit(250);

    if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json(data);
}
