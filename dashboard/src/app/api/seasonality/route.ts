import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const ticker = searchParams.get('ticker');
        const limit = searchParams.get('limit');

        let query = supabase.from('seasonality').select('*');

        if (ticker) {
            query = query.eq('ticker', ticker);
        }

        // Order by ticker for consistent display
        query = query.order('ticker', { ascending: true });

        if (limit) {
            query = query.limit(parseInt(limit));
        } else {
            query = query.limit(200);
        }

        const { data, error } = await query;

        if (error) {
            console.error('Seasonality API Error:', error);
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        return NextResponse.json(data || []);
    } catch (err) {
        console.error('Seasonality API Exception:', err);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
