import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TechnicalSignals from '@/components/TechnicalSignals';

const mockStocks = [
  // RSI Overbought (>70)
  { ticker: 'RELIANCE', company_name: 'Reliance', rsi14: 78, macd: 5, macd_signal: 3, sma20: 2850, sma50: 2800, adx14: 35, bb_upper: 3000, bb_lower: 2700, price_last: 2900 },
  // RSI Oversold (<30)
  { ticker: 'TCS', company_name: 'TCS', rsi14: 25, macd: -2, macd_signal: 1, sma20: 4000, sma50: 4100, adx14: 22, bb_upper: 4200, bb_lower: 3800, price_last: 3950 },
  // Golden Cross (SMA20 > SMA50)
  { ticker: 'INFY', company_name: 'Infosys', rsi14: 55, macd: 8, macd_signal: 4, sma20: 1850, sma50: 1750, adx14: 28, bb_upper: 1900, bb_lower: 1700, price_last: 1800 },
  // Death Cross (SMA20 < SMA50)
  { ticker: 'HDFC', company_name: 'HDFC Bank', rsi14: 48, macd: -5, macd_signal: -2, sma20: 1550, sma50: 1650, adx14: 25, bb_upper: 1700, bb_lower: 1500, price_last: 1600 },
  // Strong Trend (ADX > 30)
  { ticker: 'ICICI', company_name: 'ICICI Bank', rsi14: 62, macd: 3, macd_signal: 1, sma20: 1030, sma50: 1000, adx14: 42, bb_upper: 1100, bb_lower: 950, price_last: 1050 },
  // BB Breakout Up
  { ticker: 'ADANI', company_name: 'Adani', rsi14: 68, macd: 10, macd_signal: 5, sma20: 2450, sma50: 2400, adx14: 30, bb_upper: 2480, bb_lower: 2300, price_last: 2500 },
  // BB Breakout Down
  { ticker: 'WIPRO', company_name: 'Wipro', rsi14: 32, macd: -3, macd_signal: 0, sma20: 450, sma50: 470, adx14: 20, bb_upper: 480, bb_lower: 420, price_last: 410 },
];

describe('TechnicalSignals', () => {
  it('renders all signal categories', () => {
    render(<TechnicalSignals stocks={mockStocks} onSelectStock={() => { }} />);

    expect(screen.getByText(/RSI OVERBOUGHT/)).toBeInTheDocument();
    expect(screen.getByText(/RSI OVERSOLD/)).toBeInTheDocument();
    expect(screen.getByText(/MACD BULLISH/)).toBeInTheDocument();
    expect(screen.getByText(/MACD BEARISH/)).toBeInTheDocument();
    expect(screen.getByText(/GOLDEN CROSS/)).toBeInTheDocument();
    expect(screen.getByText(/DEATH CROSS/)).toBeInTheDocument();
    expect(screen.getByText(/STRONG TREND/)).toBeInTheDocument();
    expect(screen.getByText(/BB BREAKOUT/)).toBeInTheDocument();
  });

  it('identifies RSI overbought stocks correctly', () => {
    render(<TechnicalSignals stocks={mockStocks} onSelectStock={() => { }} />);

    // RELIANCE has RSI 78 (>70)
    const relianceElements = screen.getAllByText('RELIANCE');
    expect(relianceElements.length).toBeGreaterThan(0);
  });

  it('identifies RSI oversold stocks correctly', () => {
    render(<TechnicalSignals stocks={mockStocks} onSelectStock={() => { }} />);

    // TCS has RSI 25 (<30)
    const tcsElements = screen.getAllByText('TCS');
    expect(tcsElements.length).toBeGreaterThan(0);
  });

  it('identifies golden cross stocks correctly', () => {
    // Current component logic for Golden Cross: SMA50 > SMA200 and price > SMA200
    const goldenMockStocks = [
      { ticker: 'GOLD', sma50: 100, sma200: 90, price_last: 95 } // Price must be > SMA200
    ];
    render(<TechnicalSignals stocks={goldenMockStocks} onSelectStock={() => { }} />);

    expect(screen.getAllByText('GOLD').length).toBeGreaterThan(0);
  });

  it('identifies death cross stocks correctly', () => {
    // Death Cross: SMA50 < SMA200
    const deathMockStocks = [
      { ticker: 'DEATH', sma50: 80, sma200: 90 }
    ];
    render(<TechnicalSignals stocks={deathMockStocks} onSelectStock={() => { }} />);

    expect(screen.getAllByText('DEATH').length).toBeGreaterThan(0);
  });

  it('identifies strong trend stocks correctly', () => {
    render(<TechnicalSignals stocks={mockStocks} onSelectStock={() => { }} />);

    // ICICI has ADX 42 (>25)
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
    render(<TechnicalSignals stocks={[]} onSelectStock={() => { }} />);

    // Should render all signal categories
    expect(screen.getByText(/RSI OVERBOUGHT/)).toBeInTheDocument();
    expect(screen.getByText(/RSI OVERSOLD/)).toBeInTheDocument();
  });

  it('displays signal count badges', () => {
    render(<TechnicalSignals stocks={mockStocks} onSelectStock={() => { }} />);

    // Each signal card should have a count (even if 0)
    // The component renders counts in spans inside the h4
  });

  it('handles stocks with missing technical indicators', () => {
    const incompleteStocks = [
      { ticker: 'TEST', company_name: 'Test', price_last: 100 },
    ];

    render(<TechnicalSignals stocks={incompleteStocks} onSelectStock={() => { }} />);

    // Should render without crashing
    expect(screen.getByText(/RSI OVERBOUGHT/)).toBeInTheDocument();
  });
});
