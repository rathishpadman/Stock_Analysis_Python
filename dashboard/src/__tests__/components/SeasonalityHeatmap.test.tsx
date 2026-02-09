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
    render(<SeasonalityHeatmap data={mockSeasonalityData} onSelectStock={() => { }} />);

    expect(screen.getByText('RELIANCE')).toBeInTheDocument();
    expect(screen.getByText('TCS')).toBeInTheDocument();
  });

  it('displays all 12 month columns', () => {
    render(<SeasonalityHeatmap data={mockSeasonalityData} onSelectStock={() => { }} />);

    expect(screen.getAllByText('Jan').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Dec').length).toBeGreaterThan(0);
  });

  it('displays best and worst month indicators', () => {
    render(<SeasonalityHeatmap data={mockSeasonalityData} onSelectStock={() => { }} />);

    expect(screen.getAllByText('Best').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Worst').length).toBeGreaterThan(0);
  });

  it('displays correct return values for specific months', () => {
    render(<SeasonalityHeatmap data={mockSeasonalityData} onSelectStock={() => { }} />);

    expect(screen.getAllByText('+2.5%').length).toBeGreaterThan(0);
    expect(screen.getAllByText('-1.2%').length).toBeGreaterThan(0);
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
    render(<SeasonalityHeatmap data={mockSeasonalityData} onSelectStock={() => { }} />);

    expect(screen.getByText(/Returns Legend/)).toBeInTheDocument();
  });

  it('renders empty state when no data provided', () => {
    render(<SeasonalityHeatmap data={[]} onSelectStock={() => { }} />);

    expect(screen.queryByText('RELIANCE')).not.toBeInTheDocument();
  });

  it('applies correct color coding for positive returns', () => {
    const { container } = render(<SeasonalityHeatmap data={mockSeasonalityData} onSelectStock={() => { }} />);

    // Positive returns should have green colored cells
    const greenCells = container.querySelectorAll('[class*="green"]');
    expect(greenCells.length).toBeGreaterThan(0);
  });

  it('applies correct color coding for negative returns', () => {
    const { container } = render(<SeasonalityHeatmap data={mockSeasonalityData} onSelectStock={() => { }} />);

    const redCells = container.querySelectorAll('[class*="red"]');
    expect(redCells.length).toBeGreaterThan(0);
  });
});
