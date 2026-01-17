import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import WeeklyReportTable from '@/components/WeeklyReportTable';

const mockWeeklyData = [
  {
    ticker: 'RELIANCE',
    week_ending: '2024-01-14',
    weekly_open: 2850.00,
    weekly_high: 2920.00,
    weekly_low: 2810.00,
    weekly_close: 2900.00,
    weekly_return_pct: 1.75,
    weekly_trend: 'bullish',
    weekly_rsi14: 62.5,
    return_4w: 4.2,
    return_13w: 8.5,
    sma20: 2875.00,
    sma50: 2800.00
  },
  {
    ticker: 'TCS',
    week_ending: '2024-01-14',
    weekly_open: 3950.00,
    weekly_high: 4050.00,
    weekly_low: 3900.00,
    weekly_close: 4000.00,
    weekly_return_pct: -0.5,
    weekly_trend: 'bearish',
    weekly_rsi14: 45.2,
    return_4w: -1.2,
    return_13w: 3.0,
    sma20: 3990.00,
    sma50: 3950.00
  }
];

describe('WeeklyReportTable', () => {
  it('renders the table with weekly data', () => {
    render(<WeeklyReportTable data={mockWeeklyData} />);
    
    expect(screen.getByText('RELIANCE')).toBeInTheDocument();
    expect(screen.getByText('TCS')).toBeInTheDocument();
  });

  it('displays weekly close prices correctly', () => {
    render(<WeeklyReportTable data={mockWeeklyData} />);
    
    expect(screen.getByText('₹2,900')).toBeInTheDocument();
    expect(screen.getByText('₹4,000')).toBeInTheDocument();
  });

  it('displays weekly returns with correct formatting', () => {
    render(<WeeklyReportTable data={mockWeeklyData} />);
    
    // Positive return
    expect(screen.getByText('+1.75%')).toBeInTheDocument();
    // Negative return
    expect(screen.getByText('-0.50%')).toBeInTheDocument();
  });

  it('displays RSI values', () => {
    render(<WeeklyReportTable data={mockWeeklyData} />);
    
    expect(screen.getByText('62.50')).toBeInTheDocument();
    expect(screen.getByText('45.20')).toBeInTheDocument();
  });

  it('displays trend indicators', () => {
    render(<WeeklyReportTable data={mockWeeklyData} />);
    
    expect(screen.getByText('bullish')).toBeInTheDocument();
    expect(screen.getByText('bearish')).toBeInTheDocument();
  });

  it('calls onSelectStock when a row is clicked', async () => {
    const mockOnSelectStock = jest.fn();
    const user = userEvent.setup();
    
    render(<WeeklyReportTable data={mockWeeklyData} onSelectStock={mockOnSelectStock} />);
    
    const relianceRow = screen.getByText('RELIANCE').closest('tr');
    if (relianceRow) {
      await user.click(relianceRow);
    }
    
    expect(mockOnSelectStock).toHaveBeenCalledWith('RELIANCE');
  });

  it('renders empty state when no data provided', () => {
    render(<WeeklyReportTable data={[]} />);
    
    // Table should still render but with no data rows
    expect(screen.queryByText('RELIANCE')).not.toBeInTheDocument();
  });

  it('displays 4-week and 13-week returns', () => {
    render(<WeeklyReportTable data={mockWeeklyData} />);
    
    // Check 4W column header
    expect(screen.getByText('4W')).toBeInTheDocument();
    // Check 13W column header
    expect(screen.getByText('13W')).toBeInTheDocument();
    
    // Check values
    expect(screen.getByText('+4.20%')).toBeInTheDocument();
    expect(screen.getByText('+8.50%')).toBeInTheDocument();
  });
});
