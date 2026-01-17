import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function GET(
    request: Request,
    { params }: { params: Promise<{ ticker: string }> }
) {
    try {
        const { ticker } = await params;
        const { searchParams } = new URL(request.url);
        const weeks = parseInt(searchParams.get('weeks') || '52');

        const { data, error } = await supabase
            .from('weekly_analysis')
            .select('*')
            .eq('ticker', ticker.toUpperCase())
            .order('week_ending', { ascending: false })
            .limit(weeks);

        if (error) {
            console.error('Error fetching weekly data:', error);
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        return NextResponse.json(data || []);
    } catch (error) {
        console.error('Weekly ticker API error:', error);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
