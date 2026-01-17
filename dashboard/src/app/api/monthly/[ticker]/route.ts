import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(
    request: Request,
    { params }: { params: Promise<{ ticker: string }> }
) {
    try {
        const { ticker } = await params;
        const url = new URL(request.url);
        const months = parseInt(url.searchParams.get('months') || '24');

        const { data, error } = await supabase
            .from('monthly_analysis')
            .select('*')
            .eq('ticker', ticker.toUpperCase())
            .order('month', { ascending: false })
            .limit(months);

        if (error) {
            console.error('Supabase error:', error);
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        return NextResponse.json(data || []);
    } catch (error) {
        console.error('API error:', error);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
