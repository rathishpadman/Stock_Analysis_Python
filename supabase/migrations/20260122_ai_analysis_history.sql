-- Supabase Migration: AI Analysis History Table
-- Run this SQL in the Supabase Dashboard SQL Editor

-- Create ai_analysis_history table to store analysis results
CREATE TABLE IF NOT EXISTS ai_analysis_history (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    composite_score NUMERIC(5,2),
    recommendation VARCHAR(50),
    signal VARCHAR(20),
    cost_usd NUMERIC(10,6),
    cached_from_id INTEGER REFERENCES ai_analysis_history(id),
    full_response JSONB,
    agent_analyses JSONB,
    synthesis JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast lookups by ticker
CREATE INDEX IF NOT EXISTS idx_ai_analysis_history_ticker 
ON ai_analysis_history(ticker);

-- Create index for fast lookups by analyzed_at
CREATE INDEX IF NOT EXISTS idx_ai_analysis_history_analyzed_at 
ON ai_analysis_history(analyzed_at DESC);

-- Create unique constraint for ticker + date (prevent duplicates on same day)
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_analysis_history_ticker_date 
ON ai_analysis_history(ticker, DATE(analyzed_at));

-- Add RLS policies (optional but recommended)
ALTER TABLE ai_analysis_history ENABLE ROW LEVEL SECURITY;

-- Allow read access to all authenticated users
CREATE POLICY "Allow read access" ON ai_analysis_history
    FOR SELECT USING (true);

-- Allow insert from service role only
CREATE POLICY "Allow insert from service" ON ai_analysis_history
    FOR INSERT WITH CHECK (true);

-- Comment the table
COMMENT ON TABLE ai_analysis_history IS 'Stores AI analysis results for stock tickers';
COMMENT ON COLUMN ai_analysis_history.ticker IS 'Stock ticker symbol (e.g., RELIANCE)';
COMMENT ON COLUMN ai_analysis_history.composite_score IS 'Overall composite score from 0-100';
COMMENT ON COLUMN ai_analysis_history.recommendation IS 'Trading recommendation (BUY, HOLD, SELL, etc.)';
COMMENT ON COLUMN ai_analysis_history.signal IS 'Action signal derived from analysis';
COMMENT ON COLUMN ai_analysis_history.cost_usd IS 'API cost for this analysis in USD';
COMMENT ON COLUMN ai_analysis_history.full_response IS 'Complete JSON response from AI agents';
COMMENT ON COLUMN ai_analysis_history.agent_analyses IS 'Individual agent analysis results';
COMMENT ON COLUMN ai_analysis_history.synthesis IS 'Synthesized analysis output';
