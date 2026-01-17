import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SeasonalityHeatmap from '@/components/SeasonalityHeatmap';

const mockSeasonalityData = [
  {
    ticker: 'RELIANCE',
    jan_avg: 2.5,
    feb_avg: -1.2,
    mar_avg: 3.8,
    apr_avg: 1.5,
    may_avg: -0.8,
    jun_avg: 2.1,
    jul_avg: 0.5,
    aug_avg: -2.3,
    sep_avg: 1.8,
    oct_avg: 3.2,
    nov_avg: -0.5,
    dec_avg: 4.1,
    best_month: 'Dec',
    worst_month: 'Aug',
    positive_months: 8
  },
  {
    ticker: 'TCS',
    jan_avg: 1.5,
    feb_avg: 2.2,
    mar_avg: -1.5,
    apr_avg: 3.0,
    may_avg: 1.8,
    jun_avg: -0.5,
    jul_avg: 2.5,
    aug_avg: 1.2,
    sep_avg: -2.0,
    oct_avg: 0.8,
    nov_avg: 3.5,
    dec_avg: 1.0,
    best_month: 'Nov',
    worst_month: 'Sep',
    positive_months: 9
  }
];

describe('SeasonalityHeatmap', () => {
  it('renders the heatmap with ticker data', () => {
    render(<SeasonalityHeatmap data={mockSeasonalityData} />);
    
    expect(screen.getByText('RELIANCE')).toBeInTheDocument();
    expect(screen.getByText('TCS')).toBeInTheDocument();
  });

  it('displays all 12 month columns', () => {
    render(<SeasonalityHeatmap data={mockSeasonalityData} />);
    
    expect(screen.getByText('Jan')).toBeInTheDocument();
    expect(screen.getByText('Feb')).toBeInTheDocument();
    expect(screen.getByText('Mar')).toBeInTheDocument();
    expect(screen.getByText('Apr')).toBeInTheDocument();
    expect(screen.getByText('May')).toBeInTheDocument();
    expect(screen.getByText('Jun')).toBeInTheDocument();
    expect(screen.getByText('Jul')).toBeInTheDocument();
    expect(screen.getByText('Aug')).toBeInTheDocument();
    expect(screen.getByText('Sep')).toBeInTheDocument();
    expect(screen.getByText('Oct')).toBeInTheDocument();
    expect(screen.getByText('Nov')).toBeInTheDocument();
    expect(screen.getByText('Dec')).toBeInTheDocument();
  });

  it('displays best and worst month indicators', () => {
    render(<SeasonalityHeatmap data={mockSeasonalityData} />);
    
    // Best month column header
    expect(screen.getByText('Best')).toBeInTheDocument();
    // Worst month column header
    expect(screen.getByText('Worst')).toBeInTheDocument();
  });

  it('displays monthly return values as percentages', () => {
    render(<SeasonalityHeatmap data={mockSeasonalityData} />);
    
    // Check for formatted percentage values
    expect(screen.getByText('2.5%')).toBeInTheDocument();
    expect(screen.getByText('-1.2%')).toBeInTheDocument();
  });

  it('displays positive months count', () => {
    render(<SeasonalityHeatmap data={mockSeasonalityData} />);
    
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('9')).toBeInTheDocument();
  });

  it('calls onSelectStock when a ticker is clicked', async () => {
    const mockOnSelectStock = jest.fn();
    const user = userEvent.setup();
    
    render(<SeasonalityHeatmap data={mockSeasonalityData} onSelectStock={mockOnSelectStock} />);
    
    const relianceRow = screen.getByText('RELIANCE').closest('tr');
    if (relianceRow) {
      await user.click(relianceRow);
    }
    
    expect(mockOnSelectStock).toHaveBeenCalledWith('RELIANCE');
  });

  it('renders color legend', () => {
    render(<SeasonalityHeatmap data={mockSeasonalityData} />);
    
    // Check for legend text
    expect(screen.getByText('Strong Sell')).toBeInTheDocument();
    expect(screen.getByText('Strong Buy')).toBeInTheDocument();
  });

  it('renders empty state when no data provided', () => {
    render(<SeasonalityHeatmap data={[]} />);
    
    expect(screen.queryByText('RELIANCE')).not.toBeInTheDocument();
  });

  it('applies correct color coding for positive returns', () => {
    const { container } = render(<SeasonalityHeatmap data={mockSeasonalityData} />);
    
    // Positive returns should have emerald/green colored cells
    const greenCells = container.querySelectorAll('[class*="emerald"]');
    expect(greenCells.length).toBeGreaterThan(0);
  });

  it('applies correct color coding for negative returns', () => {
    const { container } = render(<SeasonalityHeatmap data={mockSeasonalityData} />);
    
    // Negative returns should have rose/red colored cells
    const redCells = container.querySelectorAll('[class*="rose"]');
    expect(redCells.length).toBeGreaterThan(0);
  });
});
