import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const ticker = searchParams.get('ticker');

    let query = supabase.from('monthly_analysis').select('*');

    if (ticker) {
        query = query.eq('ticker', ticker);
    }

    const { data, error } = await query.order('month', { ascending: false });

    if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json(data);
}
