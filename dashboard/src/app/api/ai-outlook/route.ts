/**
 * AI Outlook API Route
 * 
 * Proxies requests to the NIFTY Agents FastAPI backend for temporal analysis:
 * - Weekly market outlook
 * - Monthly investment thesis
 * - Seasonality insights
 */

import { NextResponse } from 'next/server';

// Agent API base URL - defaults to local development, configure for production
const AGENT_API_URL = process.env.AGENT_API_URL || 'http://localhost:8000';

interface AgentResponse {
    analysis_type: string;
    timestamp: string;
    duration_seconds?: number;
    agent_analyses?: Record<string, unknown>;
    synthesis?: Record<string, unknown>;
    error?: string;
    observability?: Record<string, unknown>;
}

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const type = searchParams.get('type') || 'weekly';
        const ticker = searchParams.get('ticker');
        const sector = searchParams.get('sector');

        // Map type to endpoint
        let endpoint: string;
        switch (type) {
            case 'weekly':
                endpoint = '/api/agent/weekly-outlook';
                break;
            case 'monthly':
                endpoint = '/api/agent/monthly-thesis';
                break;
            case 'seasonality':
                endpoint = '/api/agent/seasonality';
                break;
            default:
                return NextResponse.json(
                    { error: `Unknown analysis type: ${type}` },
                    { status: 400 }
                );
        }

        // Build URL with query params for seasonality
        let url = `${AGENT_API_URL}${endpoint}`;
        if (type === 'seasonality') {
            const params = new URLSearchParams();
            if (ticker) params.set('ticker', ticker);
            if (sector) params.set('sector', sector);
            if (params.toString()) {
                url += `?${params.toString()}`;
            }
        }

        console.log(`[AI Outlook] Fetching ${type} analysis from: ${url}`);

        // Call the agent API with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 min timeout

        try {
            const response = await fetch(url, {
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                },
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`[AI Outlook] Agent API error: ${response.status} - ${errorText}`);
                return NextResponse.json(
                    { 
                        error: `Agent API error: ${response.status}`,
                        details: errorText,
                        type 
                    },
                    { status: response.status }
                );
            }

            const data: AgentResponse = await response.json();
            
            // Add metadata
            return NextResponse.json({
                ...data,
                _meta: {
                    source: 'agent_api',
                    type,
                    fetched_at: new Date().toISOString(),
                }
            });

        } catch (fetchError) {
            clearTimeout(timeoutId);
            
            if (fetchError instanceof Error && fetchError.name === 'AbortError') {
                return NextResponse.json(
                    { error: 'Analysis timeout - please try again', type },
                    { status: 504 }
                );
            }
            throw fetchError;
        }

    } catch (err) {
        console.error('[AI Outlook] Exception:', err);
        return NextResponse.json(
            { 
                error: 'Internal server error',
                details: err instanceof Error ? err.message : 'Unknown error'
            },
            { status: 500 }
        );
    }
}

/**
 * POST endpoint for triggering fresh analysis
 */
export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { type = 'weekly', force_refresh = false } = body;

        // Same logic as GET but can be used to force refresh
        const response = await GET(new Request(
            `${request.url}?type=${type}`,
            { method: 'GET' }
        ));

        return response;

    } catch (err) {
        console.error('[AI Outlook POST] Exception:', err);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}
