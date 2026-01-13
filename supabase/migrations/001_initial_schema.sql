-- Daily stock data (30-day rolling window)
CREATE TABLE daily_stocks (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    date DATE NOT NULL,
    
    -- Price data
    price_last DECIMAL(12,2),
    high_52w DECIMAL(12,2),
    low_52w DECIMAL(12,2),
    
    -- Returns
    return_1d DECIMAL(8,4),
    return_1w DECIMAL(8,4),
    return_1m DECIMAL(8,4),
    return_3m DECIMAL(8,4),
    return_6m DECIMAL(8,4),
    return_1y DECIMAL(8,4),
    
    -- Fundamentals
    pe_ttm DECIMAL(10,2),
    pb DECIMAL(10,2),
    roe_ttm DECIMAL(8,4),
    debt_equity DECIMAL(10,2),
    market_cap_cr DECIMAL(14,2),
    
    -- Technicals
    rsi14 DECIMAL(6,2),
    sma20 DECIMAL(12,2),
    sma50 DECIMAL(12,2),
    sma200 DECIMAL(12,2),
    macd_line DECIMAL(12,4),
    macd_signal DECIMAL(12,4),
    
    -- Volatility & Risk
    volatility_30d DECIMAL(8,4),
    volatility_90d DECIMAL(8,4),
    max_drawdown_1y DECIMAL(8,4),
    sharpe_1y DECIMAL(8,4),
    beta_1y DECIMAL(8,4),
    
    -- Scores
    score_fundamental DECIMAL(6,2),
    score_technical DECIMAL(6,2),
    score_risk DECIMAL(6,2),
    overall_score DECIMAL(6,2),
    
    -- Metadata
    sector VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(ticker, date)
);

-- Weekly analysis
CREATE TABLE weekly_analysis (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    week_ending DATE NOT NULL,
    
    weekly_open DECIMAL(12,2),
    weekly_high DECIMAL(12,2),
    weekly_low DECIMAL(12,2),
    weekly_close DECIMAL(12,2),
    weekly_return_pct DECIMAL(8,4),
    weekly_volume BIGINT,
    weekly_volume_ratio DECIMAL(8,4),
    
    weekly_rsi14 DECIMAL(6,2),
    weekly_sma10 DECIMAL(12,2),
    weekly_sma20 DECIMAL(12,2),
    
    return_4w DECIMAL(8,4),
    return_13w DECIMAL(8,4),
    distance_52w_high DECIMAL(8,4),
    distance_52w_low DECIMAL(8,4),
    weekly_trend VARCHAR(20),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(ticker, week_ending)
);

-- Monthly analysis
CREATE TABLE monthly_analysis (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    month VARCHAR(7) NOT NULL, -- YYYY-MM
    
    monthly_open DECIMAL(12,2),
    monthly_high DECIMAL(12,2),
    monthly_low DECIMAL(12,2),
    monthly_close DECIMAL(12,2),
    monthly_return_pct DECIMAL(8,4),
    monthly_volume BIGINT,
    
    ytd_return_pct DECIMAL(8,4),
    monthly_sma3 DECIMAL(12,2),
    monthly_sma6 DECIMAL(12,2),
    monthly_sma12 DECIMAL(12,2),
    
    return_3m DECIMAL(8,4),
    return_6m DECIMAL(8,4),
    return_12m DECIMAL(8,4),
    
    positive_months_12m INTEGER,
    avg_monthly_return_12m DECIMAL(8,4),
    best_month_return_12m DECIMAL(8,4),
    worst_month_return_12m DECIMAL(8,4),
    monthly_trend VARCHAR(20),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(ticker, month)
);

-- Seasonality (one row per stock)
CREATE TABLE seasonality (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    
    jan_avg DECIMAL(8,4),
    feb_avg DECIMAL(8,4),
    mar_avg DECIMAL(8,4),
    apr_avg DECIMAL(8,4),
    may_avg DECIMAL(8,4),
    jun_avg DECIMAL(8,4),
    jul_avg DECIMAL(8,4),
    aug_avg DECIMAL(8,4),
    sep_avg DECIMAL(8,4),
    oct_avg DECIMAL(8,4),
    nov_avg DECIMAL(8,4),
    dec_avg DECIMAL(8,4),
    
    best_month VARCHAR(3),
    worst_month VARCHAR(3),
    
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-cleanup old daily data (keep 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_daily_stocks()
RETURNS void AS $$
BEGIN
    DELETE FROM daily_stocks WHERE date < CURRENT_DATE - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Create indexes
CREATE INDEX idx_daily_stocks_ticker ON daily_stocks(ticker);
CREATE INDEX idx_daily_stocks_date ON daily_stocks(date);
CREATE INDEX idx_weekly_ticker ON weekly_analysis(ticker);
CREATE INDEX idx_monthly_ticker ON monthly_analysis(ticker);
