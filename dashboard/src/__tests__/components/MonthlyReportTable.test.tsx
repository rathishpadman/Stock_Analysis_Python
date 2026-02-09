import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MonthlyReportTable from '@/components/MonthlyReportTable';

const mockMonthlyData = [
  {
    ticker: 'RELIANCE',
    month: '2024-01-31',
    monthly_open: 2800.00,
    monthly_high: 2950.00,
    monthly_low: 2750.00,
    monthly_close: 2900.00,
    monthly_return_pct: 3.57,
    monthly_trend: 'UP',
    ytd_return_pct: 3.57,
    return_3m: 7.5,
    return_6m: 12.3,
    return_12m: 18.5,
    positive_months_12m: 8
  },
  {
    ticker: 'TCS',
    month: '2024-01-31',
    monthly_open: 4000.00,
    monthly_high: 4100.00,
    monthly_low: 3900.00,
    monthly_close: 3950.00,
    monthly_return_pct: -1.25,
    monthly_trend: 'DOWN',
    ytd_return_pct: -1.25,
    return_3m: 2.5,
    return_6m: 5.0,
    return_12m: 15.0,
    positive_months_12m: 7
  }
];

describe('MonthlyReportTable', () => {
  it('renders the table with monthly data', () => {
    render(<MonthlyReportTable data={mockMonthlyData} onSelectStock={() => { }} />);

    expect(screen.getByText('RELIANCE')).toBeInTheDocument();
    expect(screen.getByText('TCS')).toBeInTheDocument();
  });

  it('displays monthly close prices correctly', () => {
    render(<MonthlyReportTable data={mockMonthlyData} onSelectStock={() => { }} />);

    expect(screen.getByText(/2900/)).toBeInTheDocument();
    expect(screen.getByText(/3950/)).toBeInTheDocument();
  });

  it('displays monthly returns with correct formatting', () => {
    render(<MonthlyReportTable data={mockMonthlyData} onSelectStock={() => { }} />);

    // Positive return (using getAllByText because Mo Return and YTD might be same in Jan)
    expect(screen.getAllByText('+3.57%').length).toBeGreaterThan(0);
    // Negative return
    expect(screen.getAllByText('-1.25%').length).toBeGreaterThan(0);
  });

  it('displays trend indicators', () => {
    render(<MonthlyReportTable data={mockMonthlyData} onSelectStock={() => { }} />);

    expect(screen.getByText('UP')).toBeInTheDocument();
    expect(screen.getByText('DOWN')).toBeInTheDocument();
  });

  it('displays multi-period returns (3M, 6M, 12M)', () => {
    render(<MonthlyReportTable data={mockMonthlyData} onSelectStock={() => { }} />);

    expect(screen.getByText(/3M/)).toBeInTheDocument();
    expect(screen.getByText(/6M/)).toBeInTheDocument();
    expect(screen.getByText(/12M/)).toBeInTheDocument();
  });

  it('displays positive months count', () => {
    render(<MonthlyReportTable data={mockMonthlyData} onSelectStock={() => { }} />);

    expect(screen.getByText('8/12')).toBeInTheDocument();
    expect(screen.getByText('7/12')).toBeInTheDocument();
  });

  it('calls onSelectStock when a row is clicked', async () => {
    const mockOnSelectStock = jest.fn();
    const user = userEvent.setup();

    render(<MonthlyReportTable data={mockMonthlyData} onSelectStock={mockOnSelectStock} />);

    const relianceRow = screen.getByText('RELIANCE').closest('tr');
    if (relianceRow) {
      await user.click(relianceRow);
    }

    expect(mockOnSelectStock).toHaveBeenCalledWith('RELIANCE');
  });

  it('renders empty state when no data provided', () => {
    render(<MonthlyReportTable data={[]} onSelectStock={() => { }} />);

    expect(screen.queryByText('RELIANCE')).not.toBeInTheDocument();
  });
});
