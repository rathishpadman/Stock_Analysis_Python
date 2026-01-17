import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TechnicalSignals from '@/components/TechnicalSignals';

const mockStocks = [
  // RSI Overbought (>70)
  { ticker: 'RELIANCE', company_name: 'Reliance', rsi14: 78, macd: 5, macd_signal: 3, sma20: 2850, sma50: 2800, adx: 35, bb_upper: 3000, bb_lower: 2700, price_last: 2900 },
  // RSI Oversold (<30)
  { ticker: 'TCS', company_name: 'TCS', rsi14: 25, macd: -2, macd_signal: 1, sma20: 4000, sma50: 4100, adx: 22, bb_upper: 4200, bb_lower: 3800, price_last: 3950 },
  // Golden Cross (SMA20 > SMA50)
  { ticker: 'INFY', company_name: 'Infosys', rsi14: 55, macd: 8, macd_signal: 4, sma20: 1850, sma50: 1750, adx: 28, bb_upper: 1900, bb_lower: 1700, price_last: 1800 },
  // Death Cross (SMA20 < SMA50)
  { ticker: 'HDFC', company_name: 'HDFC Bank', rsi14: 48, macd: -5, macd_signal: -2, sma20: 1550, sma50: 1650, adx: 25, bb_upper: 1700, bb_lower: 1500, price_last: 1600 },
  // Strong Trend (ADX > 30)
  { ticker: 'ICICI', company_name: 'ICICI Bank', rsi14: 62, macd: 3, macd_signal: 1, sma20: 1030, sma50: 1000, adx: 42, bb_upper: 1100, bb_lower: 950, price_last: 1050 },
  // BB Breakout Up
  { ticker: 'ADANI', company_name: 'Adani', rsi14: 68, macd: 10, macd_signal: 5, sma20: 2450, sma50: 2400, adx: 30, bb_upper: 2480, bb_lower: 2300, price_last: 2500 },
  // BB Breakout Down
  { ticker: 'WIPRO', company_name: 'Wipro', rsi14: 32, macd: -3, macd_signal: 0, sma20: 450, sma50: 470, adx: 20, bb_upper: 480, bb_lower: 420, price_last: 410 },
];

describe('TechnicalSignals', () => {
  it('renders all signal categories', () => {
    render(<TechnicalSignals stocks={mockStocks} />);
    
    expect(screen.getByText('RSI Overbought (>70)')).toBeInTheDocument();
    expect(screen.getByText('RSI Oversold (<30)')).toBeInTheDocument();
    expect(screen.getByText('MACD Bullish Cross')).toBeInTheDocument();
    expect(screen.getByText('MACD Bearish Cross')).toBeInTheDocument();
    expect(screen.getByText('Golden Cross (SMA)')).toBeInTheDocument();
    expect(screen.getByText('Death Cross (SMA)')).toBeInTheDocument();
    expect(screen.getByText('Strong Trend (ADX>30)')).toBeInTheDocument();
    expect(screen.getByText('BB Breakout')).toBeInTheDocument();
  });

  it('identifies RSI overbought stocks correctly', () => {
    render(<TechnicalSignals stocks={mockStocks} />);
    
    // RELIANCE has RSI 78 (>70)
    const relianceElements = screen.getAllByText('RELIANCE');
    expect(relianceElements.length).toBeGreaterThan(0);
  });

  it('identifies RSI oversold stocks correctly', () => {
    render(<TechnicalSignals stocks={mockStocks} />);
    
    // TCS has RSI 25 (<30)
    const tcsElements = screen.getAllByText('TCS');
    expect(tcsElements.length).toBeGreaterThan(0);
  });

  it('identifies golden cross stocks correctly', () => {
    render(<TechnicalSignals stocks={mockStocks} />);
    
    // INFY has SMA20 1850 > SMA50 1750
    const infyElements = screen.getAllByText('INFY');
    expect(infyElements.length).toBeGreaterThan(0);
  });

  it('identifies death cross stocks correctly', () => {
    render(<TechnicalSignals stocks={mockStocks} />);
    
    // HDFC has SMA20 1550 < SMA50 1650
    const hdfcElements = screen.getAllByText('HDFC');
    expect(hdfcElements.length).toBeGreaterThan(0);
  });

  it('identifies strong trend stocks correctly', () => {
    render(<TechnicalSignals stocks={mockStocks} />);
    
    // ICICI has ADX 42 (>30)
    const iciciElements = screen.getAllByText('ICICI');
    expect(iciciElements.length).toBeGreaterThan(0);
  });

  it('calls onSelectStock when clicking a stock', async () => {
    const mockOnSelectStock = jest.fn();
    const user = userEvent.setup();
    
    render(<TechnicalSignals stocks={mockStocks} onSelectStock={mockOnSelectStock} />);
    
    const relianceElements = screen.getAllByText('RELIANCE');
    await user.click(relianceElements[0]);
    
    expect(mockOnSelectStock).toHaveBeenCalledWith('RELIANCE');
  });

  it('handles empty stocks array gracefully', () => {
    render(<TechnicalSignals stocks={[]} />);
    
    // Should render all signal categories
    expect(screen.getByText('RSI Overbought (>70)')).toBeInTheDocument();
    expect(screen.getByText('RSI Oversold (<30)')).toBeInTheDocument();
  });

  it('displays signal count badges', () => {
    render(<TechnicalSignals stocks={mockStocks} />);
    
    // Each signal card should have a count
    const countBadges = screen.getAllByText(/^\d+$/);
    expect(countBadges.length).toBeGreaterThan(0);
  });

  it('handles stocks with missing technical indicators', () => {
    const incompleteStocks = [
      { ticker: 'TEST', company_name: 'Test', price_last: 100 },
    ];
    
    render(<TechnicalSignals stocks={incompleteStocks} />);
    
    // Should render without crashing
    expect(screen.getByText('RSI Overbought (>70)')).toBeInTheDocument();
  });
});
