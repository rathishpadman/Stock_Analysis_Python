import { render, screen } from '@testing-library/react';
import StockTable from '@/components/StockTable';

const mockStocks = [
    { ticker: 'RELIANCE', company_name: 'Reliance Industries', price_last: 1500, overall_score: 82, sector: 'Energy' },
    { ticker: 'TCS', company_name: 'Tata Consultancy Services', price_last: 3800, overall_score: 78, sector: 'IT' },
];

describe('StockTable', () => {
    const visibleColumns = ['ticker', 'company_name', 'price_last', 'overall_score', 'sector'];

    it('renders a table with stocks', () => {
        render(<StockTable stocks={mockStocks} visibleColumns={visibleColumns} />);

        expect(screen.getByText('RELIANCE')).toBeInTheDocument();
        expect(screen.getByText('TCS')).toBeInTheDocument();
    });

    it('displays company names', () => {
        render(<StockTable stocks={mockStocks} visibleColumns={visibleColumns} />);
        expect(screen.getByText('Reliance Industries')).toBeInTheDocument();
    });
});
