export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      daily_stocks: {
        Row: {
          adl: number | null
          adx14: number | null
          alpha_1y_pct: number | null
          altman_z: number | null
          aroon_down: number | null
          aroon_up: number | null
          atr14: number | null
          avg_daily_turnover_3m_cr: number | null
          avg_volume_1w: number | null
          bb_lower: number | null
          bb_upper: number | null
          beta_1y: number | null
          beta_3y: number | null
          cagr_3y_pct: number | null
          cagr_5y_pct: number | null
          capex_ttm_cr: number | null
          catalysts: string | null
          company_name: string | null
          consensus_rating: number | null
          created_at: string | null
          currency: string | null
          date: string
          debt_equity: number | null
          dividend_yield_pct: number | null
          ebitda_ttm_cr: number | null
          economic_moat_score: number | null
          enterprise_value_cr: number | null
          eps_growth_yoy_pct: number | null
          eps_ttm: number | null
          esg_score: number | null
          ev_ebitda_ttm: number | null
          exchange: string | null
          fcf_ttm_cr: number | null
          fcf_yield_pct: number | null
          free_float_pct: number | null
          gross_profit_margin_pct: number | null
          high_52w: number | null
          id: number
          industry: string | null
          interest_coverage: number | null
          isin: string | null
          leader_gap: number | null
          low_52w: number | null
          macd_hist: number | null
          macd_line: number | null
          macd_signal: number | null
          macro_composite: number | null
          market_cap_cr: number | null
          max_drawdown_1y: number | null
          moat_notes: string | null
          momentum_score: number | null
          net_income_ttm_cr: number | null
          net_profit_margin_pct: number | null
          news_sentiment_score: number | null
          num_analysts: number | null
          obv: number | null
          ocf_ttm_cr: number | null
          operating_profit_margin_pct: number | null
          overall_score: number | null
          pb: number | null
          pe_ttm: number | null
          peg_ratio: number | null
          piotroski_f: number | null
          price_last: number | null
          ps_ratio: number | null
          quality_score: number | null
          recommendation: string | null
          return_1d: number | null
          return_1m: number | null
          return_1w: number | null
          return_1y: number | null
          return_3m: number | null
          return_6m: number | null
          revenue_growth_yoy_pct: number | null
          revenue_ttm_cr: number | null
          risk_notes: string | null
          roa_pct: number | null
          roe_ttm: number | null
          rsi14: number | null
          score_fundamental: number | null
          score_macro: number | null
          score_risk: number | null
          score_sentiment: number | null
          score_technical: number | null
          sector: string | null
          sector_leader_ticker: string | null
          sector_notes: string | null
          sector_pe_median: number | null
          sector_relative_strength_6m_pct: number | null
          shares_outstanding: number | null
          sharpe_1y: number | null
          sma20: number | null
          sma200: number | null
          sma50: number | null
          social_sentiment: number | null
          sortino_1y: number | null
          stoch_d: number | null
          stoch_k: number | null
          target_price: number | null
          ticker: string
          upside_pct: number | null
          volatility_30d: number | null
          volatility_90d: number | null
          volume_vs_3m_avg_pct: number | null
        }
        Insert: {
          adl?: number | null
          adx14?: number | null
          alpha_1y_pct?: number | null
          altman_z?: number | null
          aroon_down?: number | null
          aroon_up?: number | null
          atr14?: number | null
          avg_daily_turnover_3m_cr?: number | null
          avg_volume_1w?: number | null
          bb_lower?: number | null
          bb_upper?: number | null
          beta_1y?: number | null
          beta_3y?: number | null
          cagr_3y_pct?: number | null
          cagr_5y_pct?: number | null
          capex_ttm_cr?: number | null
          catalysts?: string | null
          company_name?: string | null
          consensus_rating?: number | null
          created_at?: string | null
          currency?: string | null
          date: string
          debt_equity?: number | null
          dividend_yield_pct?: number | null
          ebitda_ttm_cr?: number | null
          economic_moat_score?: number | null
          enterprise_value_cr?: number | null
          eps_growth_yoy_pct?: number | null
          eps_ttm?: number | null
          esg_score?: number | null
          ev_ebitda_ttm?: number | null
          exchange?: string | null
          fcf_ttm_cr?: number | null
          fcf_yield_pct?: number | null
          free_float_pct?: number | null
          gross_profit_margin_pct?: number | null
          high_52w?: number | null
          id?: number
          industry?: string | null
          interest_coverage?: number | null
          isin?: string | null
          leader_gap?: number | null
          low_52w?: number | null
          macd_hist?: number | null
          macd_line?: number | null
          macd_signal?: number | null
          macro_composite?: number | null
          market_cap_cr?: number | null
          max_drawdown_1y?: number | null
          moat_notes?: string | null
          momentum_score?: number | null
          net_income_ttm_cr?: number | null
          net_profit_margin_pct?: number | null
          news_sentiment_score?: number | null
          num_analysts?: number | null
          obv?: number | null
          ocf_ttm_cr?: number | null
          operating_profit_margin_pct?: number | null
          overall_score?: number | null
          pb?: number | null
          pe_ttm?: number | null
          peg_ratio?: number | null
          piotroski_f?: number | null
          price_last?: number | null
          ps_ratio?: number | null
          quality_score?: number | null
          recommendation?: string | null
          return_1d?: number | null
          return_1m?: number | null
          return_1w?: number | null
          return_1y?: number | null
          return_3m?: number | null
          return_6m?: number | null
          revenue_growth_yoy_pct?: number | null
          revenue_ttm_cr?: number | null
          risk_notes?: string | null
          roa_pct?: number | null
          roe_ttm?: number | null
          rsi14?: number | null
          score_fundamental?: number | null
          score_macro?: number | null
          score_risk?: number | null
          score_sentiment?: number | null
          score_technical?: number | null
          sector?: string | null
          sector_leader_ticker?: string | null
          sector_notes?: string | null
          sector_pe_median?: number | null
          sector_relative_strength_6m_pct?: number | null
          shares_outstanding?: number | null
          sharpe_1y?: number | null
          sma20?: number | null
          sma200?: number | null
          sma50?: number | null
          social_sentiment?: number | null
          sortino_1y?: number | null
          stoch_d?: number | null
          stoch_k?: number | null
          target_price?: number | null
          ticker: string
          upside_pct?: number | null
          volatility_30d?: number | null
          volatility_90d?: number | null
          volume_vs_3m_avg_pct?: number | null
        }
        Update: {
          adl?: number | null
          adx14?: number | null
          alpha_1y_pct?: number | null
          altman_z?: number | null
          aroon_down?: number | null
          aroon_up?: number | null
          atr14?: number | null
          avg_daily_turnover_3m_cr?: number | null
          avg_volume_1w?: number | null
          bb_lower?: number | null
          bb_upper?: number | null
          beta_1y?: number | null
          beta_3y?: number | null
          cagr_3y_pct?: number | null
          cagr_5y_pct?: number | null
          capex_ttm_cr?: number | null
          catalysts?: string | null
          company_name?: string | null
          consensus_rating?: number | null
          created_at?: string | null
          currency?: string | null
          date?: string
          debt_equity?: number | null
          dividend_yield_pct?: number | null
          ebitda_ttm_cr?: number | null
          economic_moat_score?: number | null
          enterprise_value_cr?: number | null
          eps_growth_yoy_pct?: number | null
          eps_ttm?: number | null
          esg_score?: number | null
          ev_ebitda_ttm?: number | null
          exchange?: string | null
          fcf_ttm_cr?: number | null
          fcf_yield_pct?: number | null
          free_float_pct?: number | null
          gross_profit_margin_pct?: number | null
          high_52w?: number | null
          id?: number
          industry?: string | null
          interest_coverage?: number | null
          isin?: string | null
          leader_gap?: number | null
          low_52w?: number | null
          macd_hist?: number | null
          macd_line?: number | null
          macd_signal?: number | null
          macro_composite?: number | null
          market_cap_cr?: number | null
          max_drawdown_1y?: number | null
          moat_notes?: string | null
          momentum_score?: number | null
          net_income_ttm_cr?: number | null
          net_profit_margin_pct?: number | null
          news_sentiment_score?: number | null
          num_analysts?: number | null
          obv?: number | null
          ocf_ttm_cr?: number | null
          operating_profit_margin_pct?: number | null
          overall_score?: number | null
          pb?: number | null
          pe_ttm?: number | null
          peg_ratio?: number | null
          piotroski_f?: number | null
          price_last?: number | null
          ps_ratio?: number | null
          quality_score?: number | null
          recommendation?: string | null
          return_1d?: number | null
          return_1m?: number | null
          return_1w?: number | null
          return_1y?: number | null
          return_3m?: number | null
          return_6m?: number | null
          revenue_growth_yoy_pct?: number | null
          revenue_ttm_cr?: number | null
          risk_notes?: string | null
          roa_pct?: number | null
          roe_ttm?: number | null
          rsi14?: number | null
          score_fundamental?: number | null
          score_macro?: number | null
          score_risk?: number | null
          score_sentiment?: number | null
          score_technical?: number | null
          sector?: string | null
          sector_leader_ticker?: string | null
          sector_notes?: string | null
          sector_pe_median?: number | null
          sector_relative_strength_6m_pct?: number | null
          shares_outstanding?: number | null
          sharpe_1y?: number | null
          sma20?: number | null
          sma200?: number | null
          sma50?: number | null
          social_sentiment?: number | null
          sortino_1y?: number | null
          stoch_d?: number | null
          stoch_k?: number | null
          target_price?: number | null
          ticker?: string
          upside_pct?: number | null
          volatility_30d?: number | null
          volatility_90d?: number | null
          volume_vs_3m_avg_pct?: number | null
        }
        Relationships: []
      }
      monthly_analysis: {
        Row: {
          avg_monthly_return_12m: number | null
          best_month_return_12m: number | null
          company_name: string | null
          created_at: string | null
          id: number
          month: string
          monthly_close: number | null
          monthly_high: number | null
          monthly_low: number | null
          monthly_open: number | null
          monthly_return_pct: number | null
          monthly_sma12: number | null
          monthly_sma3: number | null
          monthly_sma6: number | null
          monthly_trend: string | null
          monthly_volume: number | null
          positive_months_12m: number | null
          return_12m: number | null
          return_3m: number | null
          return_6m: number | null
          ticker: string
          worst_month_return_12m: number | null
          ytd_return_pct: number | null
        }
        Insert: {
          avg_monthly_return_12m?: number | null
          best_month_return_12m?: number | null
          company_name?: string | null
          created_at?: string | null
          id?: number
          month: string
          monthly_close?: number | null
          monthly_high?: number | null
          monthly_low?: number | null
          monthly_open?: number | null
          monthly_return_pct?: number | null
          monthly_sma12?: number | null
          monthly_sma3?: number | null
          monthly_sma6?: number | null
          monthly_trend?: string | null
          monthly_volume?: number | null
          positive_months_12m?: number | null
          return_12m?: number | null
          return_3m?: number | null
          return_6m?: number | null
          ticker: string
          worst_month_return_12m?: number | null
          ytd_return_pct?: number | null
        }
        Update: {
          avg_monthly_return_12m?: number | null
          best_month_return_12m?: number | null
          company_name?: string | null
          created_at?: string | null
          id?: number
          month?: string
          monthly_close?: number | null
          monthly_high?: number | null
          monthly_low?: number | null
          monthly_open?: number | null
          monthly_return_pct?: number | null
          monthly_sma12?: number | null
          monthly_sma3?: number | null
          monthly_sma6?: number | null
          monthly_trend?: string | null
          monthly_volume?: number | null
          positive_months_12m?: number | null
          return_12m?: number | null
          return_3m?: number | null
          return_6m?: number | null
          ticker?: string
          worst_month_return_12m?: number | null
          ytd_return_pct?: number | null
        }
        Relationships: []
      }
      seasonality: {
        Row: {
          apr_avg: number | null
          aug_avg: number | null
          best_month: string | null
          company_name: string | null
          dec_avg: number | null
          feb_avg: number | null
          id: number
          jan_avg: number | null
          jul_avg: number | null
          jun_avg: number | null
          mar_avg: number | null
          may_avg: number | null
          nov_avg: number | null
          oct_avg: number | null
          sep_avg: number | null
          ticker: string
          updated_at: string | null
          worst_month: string | null
        }
        Insert: {
          apr_avg?: number | null
          aug_avg?: number | null
          best_month?: string | null
          company_name?: string | null
          dec_avg?: number | null
          feb_avg?: number | null
          id?: number
          jan_avg?: number | null
          jul_avg?: number | null
          jun_avg?: number | null
          mar_avg?: number | null
          may_avg?: number | null
          nov_avg?: number | null
          oct_avg?: number | null
          sep_avg?: number | null
          ticker: string
          updated_at?: string | null
          worst_month?: string | null
        }
        Update: {
          apr_avg?: number | null
          aug_avg?: number | null
          best_month?: string | null
          company_name?: string | null
          dec_avg?: number | null
          feb_avg?: number | null
          id?: number
          jan_avg?: number | null
          jul_avg?: number | null
          jun_avg?: number | null
          mar_avg?: number | null
          may_avg?: number | null
          nov_avg?: number | null
          oct_avg?: number | null
          sep_avg?: number | null
          ticker?: string
          updated_at?: string | null
          worst_month?: string | null
        }
        Relationships: []
      }
      weekly_analysis: {
        Row: {
          company_name: string | null
          created_at: string | null
          distance_52w_high: number | null
          distance_52w_low: number | null
          id: number
          return_13w: number | null
          return_4w: number | null
          ticker: string
          week_ending: string
          weekly_close: number | null
          weekly_high: number | null
          weekly_low: number | null
          weekly_open: number | null
          weekly_return_pct: number | null
          weekly_rsi14: number | null
          weekly_sma10: number | null
          weekly_sma20: number | null
          weekly_trend: string | null
          weekly_volume: number | null
          weekly_volume_ratio: number | null
        }
        Insert: {
          company_name?: string | null
          created_at?: string | null
          distance_52w_high?: number | null
          distance_52w_low?: number | null
          id?: number
          return_13w?: number | null
          return_4w?: number | null
          ticker: string
          week_ending: string
          weekly_close?: number | null
          weekly_high?: number | null
          weekly_low?: number | null
          weekly_open?: number | null
          weekly_return_pct?: number | null
          weekly_rsi14?: number | null
          weekly_sma10?: number | null
          weekly_sma20?: number | null
          weekly_trend?: string | null
          weekly_volume?: number | null
          weekly_volume_ratio?: number | null
        }
        Update: {
          company_name?: string | null
          created_at?: string | null
          distance_52w_high?: number | null
          distance_52w_low?: number | null
          id?: number
          return_13w?: number | null
          return_4w?: number | null
          ticker?: string
          week_ending?: string
          weekly_close?: number | null
          weekly_high?: number | null
          weekly_low?: number | null
          weekly_open?: number | null
          weekly_return_pct?: number | null
          weekly_rsi14?: number | null
          weekly_sma10?: number | null
          weekly_sma20?: number | null
          weekly_trend?: string | null
          weekly_volume?: number | null
          weekly_volume_ratio?: number | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      cleanup_old_daily_stocks: { Args: never; Returns: undefined }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

// Helper types for easier usage
export type DailyStock = Database['public']['Tables']['daily_stocks']['Row']
export type WeeklyAnalysis = Database['public']['Tables']['weekly_analysis']['Row']
export type MonthlyAnalysis = Database['public']['Tables']['monthly_analysis']['Row']
export type Seasonality = Database['public']['Tables']['seasonality']['Row']

export type Tables<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Row']
export type TablesInsert<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Insert']
export type TablesUpdate<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Update']
