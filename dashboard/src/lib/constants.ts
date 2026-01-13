export const ALL_FIELDS = [
    { id: 'ticker', label: 'Ticker', group: 'Basic' },
    { id: 'company_name', label: 'Company', group: 'Basic' },
    { id: 'price_last', label: 'Price', group: 'Price' },
    { id: 'return_1d', label: '1D Return %', group: 'Price' },
    { id: 'return_1w', label: '1W Return %', group: 'Price' },
    { id: 'return_1m', label: '1M Return %', group: 'Price' },
    { id: 'high_52w', label: '52W High', group: 'Price' },
    { id: 'low_52w', label: '52W Low', group: 'Price' },

    { id: 'pe_ttm', label: 'P/E (TTM)', group: 'Fundamental' },
    { id: 'pb', label: 'P/B', group: 'Fundamental' },
    { id: 'roe_ttm', label: 'ROE TTM %', group: 'Fundamental' },
    { id: 'debt_equity', label: 'Debt/Equity', group: 'Fundamental' },
    { id: 'market_cap_cr', label: 'Market Cap (Cr)', group: 'Fundamental' },

    { id: 'rsi14', label: 'RSI(14)', group: 'Technical' },
    { id: 'sma20', label: 'SMA 20', group: 'Technical' },
    { id: 'sma50', label: 'SMA 50', group: 'Technical' },
    { id: 'sma200', label: 'SMA 200', group: 'Technical' },

    { id: 'score_fundamental', label: 'Fund. Score', group: 'Scores' },
    { id: 'score_technical', label: 'Tech. Score', group: 'Scores' },
    { id: 'overall_score', label: 'Overall Score', group: 'Scores' },

    { id: 'sector', label: 'Sector', group: 'Metadata' },
    { id: 'industry', label: 'Industry', group: 'Metadata' },
];

export const DEFAULT_COLUMNS = ['ticker', 'company_name', 'price_last', 'return_1d', 'overall_score', 'rsi14', 'sector'];
