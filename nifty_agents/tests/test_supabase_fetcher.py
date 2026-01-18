"""
Test suite for Supabase data fetcher.

TDD Approach: Tests written BEFORE implementation.
Run with: pytest nifty_agents/tests/test_supabase_fetcher.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date


class TestGetDailyStockData:
    """Tests for get_daily_stock_data function."""
    
    @pytest.fixture
    def mock_supabase_response(self):
        """Mock Supabase daily_stocks response."""
        return {
            "data": [
                {
                    "ticker": "RELIANCE.NS",
                    "company_name": "Reliance Industries Limited",
                    "date": "2026-01-17",
                    "price_last": 2450.0,
                    "return_1d": 1.05,
                    "return_1w": 2.5,
                    "return_1m": 5.2,
                    "pe_ttm": 25.5,
                    "pb": 2.1,
                    "roe_ttm": 12.5,
                    "debt_equity": 45.2,
                    "rsi14": 55.0,
                    "sma20": 2400.0,
                    "sma50": 2350.0,
                    "sma200": 2200.0,
                    "overall_score": 72.5,
                    "score_fundamental": 75.0,
                    "score_technical": 68.0,
                    "score_risk": 70.0,
                    "sector": "Energy",
                    "industry": "Oil & Gas",
                }
            ],
            "error": None
        }
    
    @patch('nifty_agents.tools.supabase_fetcher.get_supabase_client')
    def test_get_daily_data_valid_ticker(self, mock_client, mock_supabase_response):
        """Test fetching daily stock data for valid ticker."""
        from nifty_agents.tools.supabase_fetcher import get_daily_stock_data
        
        # Setup mock chain
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_eq = MagicMock()
        mock_order = MagicMock()
        mock_limit = MagicMock()
        
        mock_client.return_value = mock_supabase
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.order.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.execute.return_value = MagicMock(data=mock_supabase_response["data"])
        
        result = get_daily_stock_data("RELIANCE.NS")
        
        assert result is not None
        assert result["ticker"] == "RELIANCE.NS"
        assert result["price_last"] == 2450.0
        assert result["overall_score"] == 72.5
        assert "error" not in result
    
    @patch('nifty_agents.tools.supabase_fetcher.get_supabase_client')
    def test_get_daily_data_with_scores(self, mock_client, mock_supabase_response):
        """Test that scores are included in response."""
        from nifty_agents.tools.supabase_fetcher import get_daily_stock_data
        
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=mock_supabase_response["data"])
        mock_client.return_value = mock_supabase
        
        result = get_daily_stock_data("RELIANCE.NS")
        
        assert "score_fundamental" in result
        assert "score_technical" in result
        assert "score_risk" in result
        assert "overall_score" in result
    
    @patch('nifty_agents.tools.supabase_fetcher.get_supabase_client')
    def test_get_daily_data_not_found(self, mock_client):
        """Test handling when ticker not found."""
        from nifty_agents.tools.supabase_fetcher import get_daily_stock_data
        
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
        mock_client.return_value = mock_supabase
        
        result = get_daily_stock_data("INVALIDTICKER")
        
        assert result is None or "error" in result


class TestGetWeeklyAnalysis:
    """Tests for get_weekly_analysis function."""
    
    @pytest.fixture
    def mock_weekly_response(self):
        """Mock weekly_analysis response."""
        return [
            {
                "ticker": "RELIANCE.NS",
                "week_ending": "2026-01-17",
                "weekly_close": 2450.0,
                "weekly_return_pct": 1.5,
                "weekly_rsi14": 58.0,
                "weekly_sma10": 2420.0,
                "weekly_sma20": 2380.0,
                "return_4w": 3.2,
                "return_13w": 8.5,
                "weekly_trend": "UP",
            },
            {
                "ticker": "RELIANCE.NS",
                "week_ending": "2026-01-10",
                "weekly_close": 2415.0,
                "weekly_return_pct": 0.8,
                "weekly_rsi14": 55.0,
                "weekly_trend": "UP",
            },
        ]
    
    @patch('nifty_agents.tools.supabase_fetcher.get_supabase_client')
    def test_get_weekly_analysis_history(self, mock_client, mock_weekly_response):
        """Test fetching weekly analysis history."""
        from nifty_agents.tools.supabase_fetcher import get_weekly_analysis
        
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=mock_weekly_response)
        mock_client.return_value = mock_supabase
        
        result = get_weekly_analysis("RELIANCE.NS", weeks=10)
        
        assert result is not None
        assert len(result) >= 1
        assert result[0]["weekly_trend"] == "UP"
        assert "return_4w" in result[0]


class TestGetMonthlyAnalysis:
    """Tests for get_monthly_analysis function."""
    
    @pytest.fixture
    def mock_monthly_response(self):
        """Mock monthly_analysis response."""
        return [
            {
                "ticker": "RELIANCE.NS",
                "month": "2026-01",
                "monthly_close": 2450.0,
                "monthly_return_pct": 4.5,
                "return_3m": 8.2,
                "return_6m": 15.5,
                "return_12m": 22.0,
                "ytd_return_pct": 4.5,
                "monthly_trend": "UP",
            },
        ]
    
    @patch('nifty_agents.tools.supabase_fetcher.get_supabase_client')
    def test_get_monthly_analysis_history(self, mock_client, mock_monthly_response):
        """Test fetching monthly analysis history."""
        from nifty_agents.tools.supabase_fetcher import get_monthly_analysis
        
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=mock_monthly_response)
        mock_client.return_value = mock_supabase
        
        result = get_monthly_analysis("RELIANCE.NS", months=12)
        
        assert result is not None
        assert len(result) >= 1
        assert "return_12m" in result[0]


class TestGetSeasonalityData:
    """Tests for get_seasonality_data function."""
    
    @pytest.fixture
    def mock_seasonality_response(self):
        """Mock seasonality response."""
        return [
            {
                "ticker": "RELIANCE.NS",
                "company_name": "Reliance Industries Limited",
                "jan_avg": 2.5,
                "feb_avg": 1.8,
                "mar_avg": -0.5,
                "apr_avg": 3.2,
                "may_avg": 1.2,
                "jun_avg": -1.0,
                "jul_avg": 2.8,
                "aug_avg": 0.5,
                "sep_avg": -2.1,
                "oct_avg": 3.5,
                "nov_avg": 2.2,
                "dec_avg": 1.5,
                "best_month": "October",
                "worst_month": "September",
            }
        ]
    
    @patch('nifty_agents.tools.supabase_fetcher.get_supabase_client')
    def test_get_seasonality_data(self, mock_client, mock_seasonality_response):
        """Test fetching seasonality data."""
        from nifty_agents.tools.supabase_fetcher import get_seasonality_data
        
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_seasonality_response)
        mock_client.return_value = mock_supabase
        
        result = get_seasonality_data("RELIANCE.NS")
        
        assert result is not None
        assert result["best_month"] == "October"
        assert result["worst_month"] == "September"
        assert "jan_avg" in result
        assert "dec_avg" in result
    
    @patch('nifty_agents.tools.supabase_fetcher.get_supabase_client')
    def test_seasonality_identifies_patterns(self, mock_client, mock_seasonality_response):
        """Test that seasonality patterns are identified."""
        from nifty_agents.tools.supabase_fetcher import get_seasonality_data
        
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=mock_seasonality_response)
        mock_client.return_value = mock_supabase
        
        result = get_seasonality_data("RELIANCE.NS")
        
        # Check pattern identification
        assert result["best_month"] is not None
        assert result["worst_month"] is not None


class TestSupabaseConnection:
    """Tests for Supabase connection handling."""
    
    @patch.dict('os.environ', {'SUPABASE_URL': '', 'SUPABASE_KEY': ''})
    def test_handles_missing_credentials(self):
        """Test handling when Supabase credentials missing."""
        from nifty_agents.tools.supabase_fetcher import get_supabase_client
        
        # Should raise or return None gracefully
        with pytest.raises(Exception):
            get_supabase_client()
    
    @patch('nifty_agents.tools.supabase_fetcher.create_client')
    @patch.dict('os.environ', {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_KEY': 'test-key'})
    def test_creates_client_with_credentials(self, mock_create_client):
        """Test that client is created with proper credentials."""
        from nifty_agents.tools.supabase_fetcher import get_supabase_client
        
        mock_create_client.return_value = MagicMock()
        
        client = get_supabase_client()
        
        mock_create_client.assert_called_once()
        assert client is not None
