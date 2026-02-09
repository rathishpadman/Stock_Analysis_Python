import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AIMarketOutlook from '@/components/AIMarketOutlook';

// Mock the global fetch
global.fetch = jest.fn();

const mockWeeklyResponse = {
    analysis_type: 'weekly',
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

describe('AIMarketOutlook', () => {
    beforeEach(() => {
        (global.fetch as jest.Mock).mockClear();
    });

    it('renders the initial state with a Generate button', () => {
        render(<AIMarketOutlook type="weekly" />);

        expect(screen.getByText(/Weekly AI Outlook/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Generate/i })).toBeInTheDocument();
    });

    it('shows loading state when Generate is clicked', async () => {
        (global.fetch as jest.Mock).mockImplementation(() =>
            new Promise(resolve => setTimeout(() => resolve({
                ok: true,
                json: async () => mockWeeklyResponse
            }), 100))
        );

        render(<AIMarketOutlook type="weekly" />);

        fireEvent.click(screen.getByRole('button', { name: /Generate/i }));

        expect(screen.getByText(/Running AI analysis/i)).toBeInTheDocument();
    });

    it('renders analysis results after successful fetch', async () => {
        (global.fetch as jest.Mock).mockResolvedValue({
            ok: true,
            json: async () => mockWeeklyResponse
        });

        render(<AIMarketOutlook type="weekly" />);

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
        (global.fetch as jest.Mock).mockResolvedValue({
            ok: false,
            status: 500,
            text: async () => 'Internal Server Error'
        });

        render(<AIMarketOutlook type="weekly" />);

        fireEvent.click(screen.getByRole('button', { name: /Generate/i }));

        await waitFor(() => {
            expect(screen.getByText(/API error 500: Internal Server Error/i)).toBeInTheDocument();
        });
    });
});
