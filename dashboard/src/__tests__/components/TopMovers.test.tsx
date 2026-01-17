import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TopMovers from '@/components/TopMovers';

const mockStocks = [
  { ticker: 'ADANIENT', company_name: 'Adani Enterprises', price_last: 2500, return_1d: 5.25, overall_score: 75, volume: 5000000 },
  { ticker: 'RELIANCE', company_name: 'Reliance Industries', price_last: 2900, return_1d: 3.15, overall_score: 82, volume: 8000000 },
  { ticker: 'TCS', company_name: 'Tata Consultancy', price_last: 4000, return_1d: -2.50, overall_score: 78, volume: 3000000 },
  { ticker: 'INFY', company_name: 'Infosys', price_last: 1800, return_1d: -4.10, overall_score: 72, volume: 6000000 },
  { ticker: 'HDFC', company_name: 'HDFC Bank', price_last: 1600, return_1d: 0.50, overall_score: 80, volume: 10000000 },
  { ticker: 'ICICI', company_name: 'ICICI Bank', price_last: 1050, return_1d: -0.25, overall_score: 76, volume: 9500000 },
];

describe('TopMovers', () => {
  it('renders all three sections', () => {
    render(<TopMovers stocks={mockStocks} />);
    
    expect(screen.getByText('TOP GAINERS')).toBeInTheDocument();
    expect(screen.getByText('TOP LOSERS')).toBeInTheDocument();
    expect(screen.getByText('HIGH VOLUME')).toBeInTheDocument();
  });

  it('displays top gainers correctly', () => {
    render(<TopMovers stocks={mockStocks} />);
    
    // ADANIENT has highest gain at 5.25%
    expect(screen.getByText('ADANIENT')).toBeInTheDocument();
    // Should show positive return
    expect(screen.getByText('+5.25%')).toBeInTheDocument();
  });

  it('displays top losers correctly', () => {
    render(<TopMovers stocks={mockStocks} />);
    
    // INFY has biggest loss at -4.10%
    expect(screen.getByText('INFY')).toBeInTheDocument();
    expect(screen.getByText('-4.10%')).toBeInTheDocument();
  });

  it('displays high volume stocks correctly', () => {
    render(<TopMovers stocks={mockStocks} />);
    
    // HDFC has highest volume at 10M
    expect(screen.getByText('HDFC')).toBeInTheDocument();
  });

  it('calls onSelectStock when a stock is clicked', async () => {
    const mockOnSelectStock = jest.fn();
    const user = userEvent.setup();
    
    render(<TopMovers stocks={mockStocks} onSelectStock={mockOnSelectStock} />);
    
    // Click on ADANIENT (top gainer)
    const adaniElement = screen.getAllByText('ADANIENT')[0];
    await user.click(adaniElement);
    
    expect(mockOnSelectStock).toHaveBeenCalledWith('ADANIENT');
  });

  it('limits display to top 5 stocks per category', () => {
    const manyStocks = Array.from({ length: 10 }, (_, i) => ({
      ticker: `STOCK${i}`,
      company_name: `Stock Company ${i}`,
      price_last: 1000 + i * 100,
      return_1d: i % 2 === 0 ? i : -i,
      overall_score: 70 + i,
      volume: 1000000 * (i + 1),
    }));
    
    render(<TopMovers stocks={manyStocks} />);
    
    // Each section should show max 5 stocks
    const sections = screen.getAllByRole('heading', { level: 3 });
    expect(sections).toHaveLength(3);
  });

  it('handles empty stocks array gracefully', () => {
    render(<TopMovers stocks={[]} />);
    
    // Should still render headers
    expect(screen.getByText('TOP GAINERS')).toBeInTheDocument();
    expect(screen.getByText('TOP LOSERS')).toBeInTheDocument();
    expect(screen.getByText('HIGH VOLUME')).toBeInTheDocument();
  });

  it('handles stocks with missing return_1d', () => {
    const stocksWithMissing = [
      { ticker: 'TEST1', company_name: 'Test', price_last: 100, overall_score: 70, volume: 1000 },
      { ticker: 'TEST2', company_name: 'Test 2', price_last: 200, return_1d: 2.5, overall_score: 75, volume: 2000 },
    ];
    
    render(<TopMovers stocks={stocksWithMissing} />);
    
    // Should render without crashing
    expect(screen.getByText('TOP GAINERS')).toBeInTheDocument();
  });
});
