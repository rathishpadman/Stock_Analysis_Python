import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TopMovers from '@/components/TopMovers';

const mockStocks = [
  { ticker: 'ADANIENT', company_name: 'Adani Enterprises', price_last: 2500, return_1d: 5.25, overall_score: 75, volume_vs_3m_avg_pct: 150 },
  { ticker: 'RELIANCE', company_name: 'Reliance Industries', price_last: 2900, return_1d: 3.15, overall_score: 82, volume_vs_3m_avg_pct: 80 },
  { ticker: 'TCS', company_name: 'Tata Consultancy', price_last: 4000, return_1d: -2.50, overall_score: 78, volume_vs_3m_avg_pct: 120 },
  { ticker: 'INFY', company_name: 'Infosys', price_last: 1800, return_1d: -4.10, overall_score: 72, volume_vs_3m_avg_pct: 200 },
  { ticker: 'HDFC', company_name: 'HDFC Bank', price_last: 1600, return_1d: 0.50, overall_score: 80, volume_vs_3m_avg_pct: 300 },
  { ticker: 'ICICI', company_name: 'ICICI Bank', price_last: 1050, return_1d: -0.25, overall_score: 76, volume_vs_3m_avg_pct: 95 },
];

describe('TopMovers', () => {
  it('renders all three sections', () => {
    render(<TopMovers stocks={mockStocks} onSelectStock={() => { }} />);

    expect(screen.getByText('TOP GAINERS')).toBeInTheDocument();
    expect(screen.getByText('TOP LOSERS')).toBeInTheDocument();
    expect(screen.getByText('HIGH VOLUME')).toBeInTheDocument();
  });

  it('displays top gainers correctly', () => {
    render(<TopMovers stocks={mockStocks} onSelectStock={() => { }} />);

    expect(screen.getAllByText('ADANIENT').length).toBeGreaterThan(0);
    expect(screen.getAllByText('+5.25%').length).toBeGreaterThan(0);
  });

  it('displays top losers correctly', () => {
    render(<TopMovers stocks={mockStocks} onSelectStock={() => { }} />);

    expect(screen.getAllByText('INFY').length).toBeGreaterThan(0);
    expect(screen.getAllByText('-4.10%').length).toBeGreaterThan(0);
  });

  it('displays high volume stocks correctly', () => {
    render(<TopMovers stocks={mockStocks} onSelectStock={() => { }} />);

    expect(screen.getAllByText('HDFC').length).toBeGreaterThan(0);
    expect(screen.getAllByText('300%').length).toBeGreaterThan(0);
  });

  it('calls onSelectStock when a stock is clicked', async () => {
    const mockOnSelectStock = jest.fn();
    const user = userEvent.setup();

    render(<TopMovers stocks={mockStocks} onSelectStock={mockOnSelectStock} />);

    const adaniElement = screen.getAllByText('ADANIENT')[0];
    await user.click(adaniElement);

    expect(mockOnSelectStock).toHaveBeenCalledWith('ADANIENT');
  });

  it('handles empty stocks array gracefully', () => {
    render(<TopMovers stocks={[]} onSelectStock={() => { }} />);

    expect(screen.getByText('TOP GAINERS')).toBeInTheDocument();
    expect(screen.getByText('TOP LOSERS')).toBeInTheDocument();
    expect(screen.getByText(/HIGH VOLUME/i)).toBeInTheDocument();
  });

  it('handles stocks with missing return_1d', () => {
    const stocksWithMissing = [
      { ticker: 'TEST1', company_name: 'Test', price_last: 100, overall_score: 70, volume_vs_3m_avg_pct: 100 },
      { ticker: 'TEST2', company_name: 'Test 2', price_last: 200, return_1d: 2.5, overall_score: 75, volume_vs_3m_avg_pct: 200 },
    ];

    render(<TopMovers stocks={stocksWithMissing} onSelectStock={() => { }} />);

    expect(screen.getByText('TOP GAINERS')).toBeInTheDocument();
  });
});
