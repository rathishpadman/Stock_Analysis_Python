import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import AIMarketOutlook from '@/components/AIMarketOutlook';

// Mock the global fetch
global.fetch = jest.fn();

const mockWeeklyResponse = {
    analysis_type: 'weekly',
    _cache_hit: false,
    synthesis: {
        headline: 'Bullish Continuation Expected',
        weekly_stance: 'bullish',
        key_insights: ['Insight 1', 'Insight 2'],
        composite_confidence: 0.85
    },
    agent_analyses: {
        trend: { primary_trend: 'Up', trend_strength: 'Strong' },
        risk_regime: { risk_regime: 'Low' }
    }
};

// Helper to return 404 for the cache endpoint and resolve actual data for generate
const mockFetchNoCacheHit = (fullResponse = mockWeeklyResponse) => {
    (global.fetch as jest.Mock).mockImplementation((url: string) => {
        if (url.includes('/api/agent/temporal/cached')) {
            return Promise.resolve({ ok: false, status: 404 });
        }
        return Promise.resolve({
            ok: true,
            json: async () => fullResponse
        });
    });
};

describe('AIMarketOutlook', () => {
    beforeEach(() => {
        (global.fetch as jest.Mock).mockClear();
        // Default: cache miss (404) so tests can control initial state
        mockFetchNoCacheHit();
    });

    it('renders the initial state with a Generate button', async () => {
        render(<AIMarketOutlook type="weekly" />);

        expect(screen.getByText(/Weekly AI Outlook/i)).toBeInTheDocument();
        // Wait for the auto-fetch to complete (404 = no cache) before asserting
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Generate/i })).toBeInTheDocument();
        });
    });

    it('shows loading state when Generate is clicked', async () => {
        (global.fetch as jest.Mock).mockImplementation((url: string) => {
            if (url.includes('/api/agent/temporal/cached')) {
                return Promise.resolve({ ok: false, status: 404 });
            }
            return new Promise(resolve => setTimeout(() => resolve({
                ok: true,
                json: async () => mockWeeklyResponse
            }), 100));
        });

        render(<AIMarketOutlook type="weekly" />);

        // Wait for auto-fetch to settle
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Generate/i })).not.toBeDisabled();
        });

        fireEvent.click(screen.getByRole('button', { name: /Generate/i }));

        expect(screen.getByText(/Running AI analysis/i)).toBeInTheDocument();
    });

    it('renders analysis results after successful fetch', async () => {
        render(<AIMarketOutlook type="weekly" />);

        // Wait for auto-fetch to settle (cache miss)
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Generate/i })).not.toBeDisabled();
        });

        fireEvent.click(screen.getByRole('button', { name: /Generate/i }));

        await waitFor(() => {
            expect(screen.getByText('Bullish Continuation Expected')).toBeInTheDocument();
        });

        // Check if Layer 1 components (StanceBadge) render
        expect(screen.getAllByText('BULLISH').length).toBeGreaterThan(0);

        // Check if Layer 2 Tabs appear
        expect(screen.getByText('Overview')).toBeInTheDocument();
        expect(screen.getByText('Sectors')).toBeInTheDocument();
    });

    it('handles API errors gracefully', async () => {
        (global.fetch as jest.Mock).mockImplementation((url: string) => {
            if (url.includes('/api/agent/temporal/cached')) {
                return Promise.resolve({ ok: false, status: 404 });
            }
            return Promise.resolve({
                ok: false,
                status: 500,
                text: async () => 'Internal Server Error'
            });
        });

        render(<AIMarketOutlook type="weekly" />);

        // Wait for auto-fetch to settle
        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Generate/i })).not.toBeDisabled();
        });

        fireEvent.click(screen.getByRole('button', { name: /Generate/i }));

        await waitFor(() => {
            expect(screen.getByText(/API error 500: Internal Server Error/i)).toBeInTheDocument();
        });
    });

    it('auto-loads from cache when server has cached data', async () => {
        (global.fetch as jest.Mock).mockImplementation((url: string) => {
            if (url.includes('/api/agent/temporal/cached')) {
                return Promise.resolve({
                    ok: true,
                    json: async () => ({ ...mockWeeklyResponse, _cache_hit: true })
                });
            }
            return Promise.resolve({
                ok: true,
                json: async () => mockWeeklyResponse
            });
        });

        await act(async () => {
            render(<AIMarketOutlook type="weekly" />);
        });

        await waitFor(() => {
            expect(screen.getByText('Bullish Continuation Expected')).toBeInTheDocument();
        });

        // Button should say 'Refresh Analysis' since data is loaded
        expect(screen.getByRole('button', { name: /Refresh Analysis/i })).toBeInTheDocument();
    });
});
