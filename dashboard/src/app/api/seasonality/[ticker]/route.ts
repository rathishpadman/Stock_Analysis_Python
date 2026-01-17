import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(
    request: Request,
    { params }: { params: Promise<{ ticker: string }> }
) {
    try {
        const { ticker } = await params;
        const tickerUpper = ticker.toUpperCase();
        
        // Try exact match first
        let { data, error } = await supabase
            .from('seasonality')
            .select('*')
            .eq('ticker', tickerUpper)
            .single();

        // If not found, try without .NS suffix
        if (!data && tickerUpper.endsWith('.NS')) {
            const tickerWithoutSuffix = tickerUpper.replace('.NS', '');
            const result = await supabase
                .from('seasonality')
                .select('*')
                .eq('ticker', tickerWithoutSuffix)
                .single();
            data = result.data;
            error = result.error;
        }

        // If still not found, try with .NS suffix
        if (!data && !tickerUpper.endsWith('.NS')) {
            const tickerWithSuffix = tickerUpper + '.NS';
            const result = await supabase
                .from('seasonality')
                .select('*')
                .eq('ticker', tickerWithSuffix)
                .single();
            data = result.data;
            error = result.error;
        }

        if (error && !data) {
            console.error('Supabase error:', error);
            return NextResponse.json(null);
        }

        return NextResponse.json(data || null);
    } catch (error) {
        console.error('API error:', error);
        return NextResponse.json(null);
    }
}
