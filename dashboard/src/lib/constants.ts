export const ALL_FIELDS = [
    // Basic Metadata
    { id: 'ticker', label: 'Ticker', group: 'Basic' },
    { id: 'company_name', label: 'Company', group: 'Basic' },
    { id: 'isin', label: 'ISIN', group: 'Basic' },
    { id: 'exchange', label: 'Exchange', group: 'Basic' },
    { id: 'sector', label: 'Sector', group: 'Basic' },
    { id: 'industry', label: 'Industry', group: 'Basic' },
    { id: 'currency', label: 'Currency', group: 'Basic' },

    // Price & Returns
    { id: 'price_last', label: 'Price', group: 'Price' },
    { id: 'high_52w', label: '52W High', group: 'Price' },
    { id: 'low_52w', label: '52W Low', group: 'Price' },
    { id: 'return_1d', label: '1D Return %', group: 'Price' },
    { id: 'return_1w', label: '1W Return %', group: 'Price' },
    { id: 'return_1m', label: '1M Return %', group: 'Price' },
    { id: 'return_3m', label: '3M Return %', group: 'Price' },
    { id: 'return_6m', label: '6M Return %', group: 'Price' },
    { id: 'return_1y', label: '1Y Return %', group: 'Price' },
    { id: 'cagr_3y_pct', label: '3Y CAGR %', group: 'Price' },
    { id: 'cagr_5y_pct', label: '5Y CAGR %', group: 'Price' },

    // Fundamental - Size & Value
    { id: 'market_cap_cr', label: 'Market Cap (Cr)', group: 'Fundamental' },
    { id: 'enterprise_value_cr', label: 'EV (Cr)', group: 'Fundamental' },
    { id: 'shares_outstanding', label: 'Shares Out.', group: 'Fundamental' },
    { id: 'free_float_pct', label: 'Free Float %', group: 'Fundamental' },
    { id: 'pe_ttm', label: 'P/E (TTM)', group: 'Fundamental' },
    { id: 'pb', label: 'P/B', group: 'Fundamental' },
    { id: 'ps_ratio', label: 'P/S Ratio', group: 'Fundamental' },
    { id: 'ev_ebitda_ttm', label: 'EV/EBITDA', group: 'Fundamental' },
    { id: 'peg_ratio', label: 'PEG Ratio', group: 'Fundamental' },
    { id: 'dividend_yield_pct', label: 'Div. Yield %', group: 'Fundamental' },

    // Fundamental - Performance & Health
    { id: 'revenue_ttm_cr', label: 'Revenue TTM (Cr)', group: 'Fundamental' },
    { id: 'ebitda_ttm_cr', label: 'EBITDA TTM (Cr)', group: 'Fundamental' },
    { id: 'net_income_ttm_cr', label: 'Net Income TTM (Cr)', group: 'Fundamental' },
    { id: 'eps_ttm', label: 'EPS TTM', group: 'Fundamental' },
    { id: 'roe_ttm', label: 'ROE TTM %', group: 'Fundamental' },
    { id: 'roa_pct', label: 'ROA %', group: 'Fundamental' },
    { id: 'debt_equity', label: 'Debt/Equity', group: 'Fundamental' },
    { id: 'interest_coverage', label: 'Interest Cov.', group: 'Fundamental' },
    { id: 'revenue_growth_yoy_pct', label: 'Rev. Growth YoY %', group: 'Fundamental' },
    { id: 'eps_growth_yoy_pct', label: 'EPS Growth YoY %', group: 'Fundamental' },
    { id: 'gross_profit_margin_pct', label: 'Gross Margin %', group: 'Fundamental' },
    { id: 'operating_profit_margin_pct', label: 'Op. Margin %', group: 'Fundamental' },
    { id: 'net_profit_margin_pct', label: 'Net Margin %', group: 'Fundamental' },

    // Cash Flow
    { id: 'ocf_ttm_cr', label: 'OCF TTM (Cr)', group: 'Fundamental' },
    { id: 'capex_ttm_cr', label: 'CapEx TTM (Cr)', group: 'Fundamental' },
    { id: 'fcf_ttm_cr', label: 'FCF TTM (Cr)', group: 'Fundamental' },
    { id: 'fcf_yield_pct', label: 'FCF Yield %', group: 'Fundamental' },

    // Technical Indicators
    { id: 'sma20', label: 'SMA 20', group: 'Technical' },
    { id: 'sma50', label: 'SMA 50', group: 'Technical' },
    { id: 'sma200', label: 'SMA 200', group: 'Technical' },
    { id: 'rsi14', label: 'RSI(14)', group: 'Technical' },
    { id: 'macd_line', label: 'MACD Line', group: 'Technical' },
    { id: 'macd_signal', label: 'MACD Signal', group: 'Technical' },
    { id: 'macd_hist', label: 'MACD Hist', group: 'Technical' },
    { id: 'adx14', label: 'ADX(14)', group: 'Technical' },
    { id: 'atr14', label: 'ATR(14)', group: 'Technical' },
    { id: 'bb_upper', label: 'BB Upper', group: 'Technical' },
    { id: 'bb_lower', label: 'BB Lower', group: 'Technical' },
    { id: 'aroon_up', label: 'Aroon Up', group: 'Technical' },
    { id: 'aroon_down', label: 'Aroon Down', group: 'Technical' },
    { id: 'stoch_k', label: 'Stoch %K', group: 'Technical' },
    { id: 'stoch_d', label: 'Stoch %D', group: 'Technical' },
    { id: 'obv', label: 'OBV', group: 'Technical' },

    // Volume & Liquidity
    { id: 'avg_volume_1w', label: 'Avg Vol (1W)', group: 'Technical' },
    { id: 'volume_vs_3m_avg_pct', label: 'Vol vs 3M Avg %', group: 'Technical' },
    { id: 'avg_daily_turnover_3m_cr', label: 'Daily Turnover (Cr)', group: 'Technical' },

    // Scores & Analysis
    { id: 'overall_score', label: 'Overall Score', group: 'Scores' },
    { id: 'score_fundamental', label: 'Fundamental Score', group: 'Scores' },
    { id: 'score_technical', label: 'Technical Score', group: 'Scores' },
    { id: 'score_risk', label: 'Risk Score', group: 'Scores' },
    { id: 'score_sentiment', label: 'Sentiment Score', group: 'Scores' },
    { id: 'score_macro', label: 'Macro Score', group: 'Scores' },
    { id: 'macro_composite', label: 'Macro Composite', group: 'Scores' },

    // Analyst & Market Sentiment
    { id: 'recommendation', label: 'Recommendation', group: 'Sentiment' },
    { id: 'consensus_rating', label: 'Consensus (1-5)', group: 'Sentiment' },
    { id: 'target_price', label: 'Target Price', group: 'Sentiment' },
    { id: 'upside_pct', label: 'Upside %', group: 'Sentiment' },
    { id: 'num_analysts', label: '# Analysts', group: 'Sentiment' },
    { id: 'news_sentiment_score', label: 'News Sentiment', group: 'Sentiment' },
    { id: 'social_sentiment', label: 'Social Sentiment', group: 'Sentiment' },

    // Deep Analysis & Quality
    { id: 'quality_score', label: 'Quality Score', group: 'Analysis' },
    { id: 'momentum_score', label: 'Momentum Score', group: 'Analysis' },
    { id: 'alpha_1y_pct', label: 'Alpha 1Y %', group: 'Analysis' },
    { id: 'sortino_1y', label: 'Sortino 1Y', group: 'Analysis' },
    { id: 'economic_moat_score', label: 'Economic Moat Score', group: 'Analysis' },
    { id: 'altman_z', label: 'Altman Z-Score', group: 'Analysis' },
    { id: 'piotroski_f', label: 'Piotroski F-Score', group: 'Analysis' },
    { id: 'esg_score', label: 'ESG Score', group: 'Analysis' },

    // Qualitative Notes
    { id: 'moat_notes', label: 'Moat Notes', group: 'Deep Dive' },
    { id: 'risk_notes', label: 'Risk Notes', group: 'Deep Dive' },
    { id: 'catalysts', label: 'Catalysts', group: 'Deep Dive' },
    { id: 'sector_notes', label: 'Sector Notes', group: 'Deep Dive' },
];

export const DEFAULT_COLUMNS = ['ticker', 'price_last', 'return_1d', 'overall_score', 'pe_ttm', 'market_cap_cr', 'rsi14', 'sector'];

// Weekly-specific fields for column picker
export const WEEKLY_FIELDS = [
    { id: 'ticker', label: 'Ticker', group: 'Basic' },
    { id: 'company_name', label: 'Company', group: 'Basic' },
    { id: 'week_ending', label: 'Week Ending', group: 'Basic' },
    { id: 'weekly_open', label: 'Weekly Open', group: 'Price' },
    { id: 'weekly_high', label: 'Weekly High', group: 'Price' },
    { id: 'weekly_low', label: 'Weekly Low', group: 'Price' },
    { id: 'weekly_close', label: 'Weekly Close', group: 'Price' },
    { id: 'weekly_return_pct', label: 'Weekly Return %', group: 'Returns' },
    { id: 'return_4w', label: '4W Return %', group: 'Returns' },
    { id: 'return_13w', label: '13W Return %', group: 'Returns' },
    { id: 'weekly_volume', label: 'Weekly Volume', group: 'Volume' },
    { id: 'weekly_volume_ratio', label: 'Volume Ratio', group: 'Volume' },
    { id: 'weekly_rsi14', label: 'RSI(14)', group: 'Technical' },
    { id: 'weekly_sma10', label: 'SMA 10', group: 'Technical' },
    { id: 'weekly_sma20', label: 'SMA 20', group: 'Technical' },
    { id: 'weekly_trend', label: 'Trend', group: 'Technical' },
];

export const DEFAULT_WEEKLY_COLUMNS = ['ticker', 'company_name', 'weekly_close', 'weekly_return_pct', 'return_4w', 'weekly_rsi14', 'weekly_trend'];

// Monthly-specific fields for column picker
export const MONTHLY_FIELDS = [
    { id: 'ticker', label: 'Ticker', group: 'Basic' },
    { id: 'company_name', label: 'Company', group: 'Basic' },
    { id: 'month', label: 'Month', group: 'Basic' },
    { id: 'monthly_open', label: 'Monthly Open', group: 'Price' },
    { id: 'monthly_high', label: 'Monthly High', group: 'Price' },
    { id: 'monthly_low', label: 'Monthly Low', group: 'Price' },
    { id: 'monthly_close', label: 'Monthly Close', group: 'Price' },
    { id: 'monthly_return_pct', label: 'Monthly Return %', group: 'Returns' },
    { id: 'return_3m', label: '3M Return %', group: 'Returns' },
    { id: 'return_6m', label: '6M Return %', group: 'Returns' },
    { id: 'return_12m', label: '12M Return %', group: 'Returns' },
    { id: 'ytd_return_pct', label: 'YTD Return %', group: 'Returns' },
    { id: 'monthly_volume', label: 'Monthly Volume', group: 'Volume' },
    { id: 'monthly_sma3', label: 'SMA 3', group: 'Technical' },
    { id: 'monthly_sma6', label: 'SMA 6', group: 'Technical' },
    { id: 'monthly_sma12', label: 'SMA 12', group: 'Technical' },
    { id: 'monthly_trend', label: 'Trend', group: 'Technical' },
];

export const DEFAULT_MONTHLY_COLUMNS = ['ticker', 'company_name', 'monthly_close', 'monthly_return_pct', 'return_3m', 'return_12m', 'monthly_trend'];

// Seasonality-specific fields for column picker
export const SEASONALITY_FIELDS = [
    { id: 'ticker', label: 'Ticker', group: 'Basic' },
    { id: 'company_name', label: 'Company', group: 'Basic' },
    { id: 'jan_avg', label: 'January Avg %', group: 'Q1' },
    { id: 'feb_avg', label: 'February Avg %', group: 'Q1' },
    { id: 'mar_avg', label: 'March Avg %', group: 'Q1' },
    { id: 'apr_avg', label: 'April Avg %', group: 'Q2' },
    { id: 'may_avg', label: 'May Avg %', group: 'Q2' },
    { id: 'jun_avg', label: 'June Avg %', group: 'Q2' },
    { id: 'jul_avg', label: 'July Avg %', group: 'Q3' },
    { id: 'aug_avg', label: 'August Avg %', group: 'Q3' },
    { id: 'sep_avg', label: 'September Avg %', group: 'Q3' },
    { id: 'oct_avg', label: 'October Avg %', group: 'Q4' },
    { id: 'nov_avg', label: 'November Avg %', group: 'Q4' },
    { id: 'dec_avg', label: 'December Avg %', group: 'Q4' },
    { id: 'best_month', label: 'Best Month', group: 'Summary' },
    { id: 'worst_month', label: 'Worst Month', group: 'Summary' },
];

export const DEFAULT_SEASONALITY_COLUMNS = ['ticker', 'company_name', 'jan_avg', 'apr_avg', 'jul_avg', 'oct_avg', 'best_month', 'worst_month'];

