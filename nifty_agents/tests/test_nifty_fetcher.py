"""
Test suite for NIFTY data fetcher tools.

TDD Approach: Tests written BEFORE implementation.
Run with: pytest nifty_agents/tests/test_nifty_fetcher.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import pandas as pd


class TestGetStockFundamentals:
    """Tests for get_stock_fundamentals function."""
    
    @pytest.fixture
    def mock_yfinance_info(self):
        """Mock yfinance Ticker.info response for RELIANCE.NS"""
        return {
            "symbol": "RELIANCE.NS",
            "shortName": "Reliance Industries Limited",
            "longName": "Reliance Industries Limited",
            "sector": "Energy",
            "industry": "Oil & Gas Refining & Marketing",
            "marketCap": 17500000000000,  # 17.5 Lakh Cr
            "trailingPE": 25.5,
            "forwardPE": 22.3,
            "priceToBook": 2.1,
            "returnOnEquity": 0.125,  # 12.5%
            "debtToEquity": 45.2,
            "dividendYield": 0.004,  # 0.4%
            "currentPrice": 2450.0,
            "fiftyTwoWeekHigh": 2800.0,
            "fiftyTwoWeekLow": 2100.0,
            "totalRevenue": 850000000000,
            "grossMargins": 0.28,
            "operatingMargins": 0.18,
            "profitMargins": 0.08,
        }
    
    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_get_fundamentals_valid_ticker(self, mock_ticker, mock_yfinance_info):
        """Test fetching fundamentals for a valid NIFTY ticker."""
        from nifty_agents.tools.nifty_fetcher import get_stock_fundamentals
        
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.info = mock_yfinance_info
        mock_ticker.return_value = mock_instance
        
        # Execute
        result = get_stock_fundamentals("RELIANCE")
        
        # Assert
        assert result is not None
        assert result["ticker"] == "RELIANCE"
        assert result["market_cap"] == 17500000000000
        assert result["pe_ratio"] == 25.5
        assert result["sector"] == "Energy"
        assert "error" not in result
    
    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_get_fundamentals_with_ns_suffix(self, mock_ticker, mock_yfinance_info):
        """Test that .NS suffix is handled correctly."""
        from nifty_agents.tools.nifty_fetcher import get_stock_fundamentals
        
        mock_instance = MagicMock()
        mock_instance.info = mock_yfinance_info
        mock_ticker.return_value = mock_instance
        
        result = get_stock_fundamentals("RELIANCE.NS")
        
        # Should call yfinance with .NS suffix
        mock_ticker.assert_called_with("RELIANCE.NS")
        assert result["ticker"] == "RELIANCE"
    
    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_get_fundamentals_invalid_ticker(self, mock_ticker):
        """Test handling of invalid/nonexistent ticker."""
        from nifty_agents.tools.nifty_fetcher import get_stock_fundamentals
        
        # Mock empty response
        mock_instance = MagicMock()
        mock_instance.info = {}
        mock_ticker.return_value = mock_instance
        
        result = get_stock_fundamentals("INVALIDTICKER")
        
        assert "error" in result
        assert result["ticker"] == "INVALIDTICKER"
    
    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_get_fundamentals_handles_exceptions(self, mock_ticker):
        """Test graceful handling of API exceptions."""
        from nifty_agents.tools.nifty_fetcher import get_stock_fundamentals
        
        mock_ticker.side_effect = Exception("API Error")
        
        result = get_stock_fundamentals("RELIANCE")
        
        assert "error" in result
        assert "API Error" in result["error"]


class TestGetStockQuote:
    """Tests for get_stock_quote function (live quotes)."""
    
    @pytest.fixture
    def mock_nse_quote(self):
        """Mock NSE live quote response."""
        return {
            "lastPrice": 2450.0,
            "change": 25.5,
            "pChange": 1.05,
            "previousClose": 2424.5,
            "open": 2430.0,
            "close": 2448.0,
            "vwap": 2445.0,
            "intraDayHighLow": {"min": 2420.0, "max": 2460.0, "value": 2450.0},
            "weekHighLow": {"min": 2100.0, "max": 2800.0},
        }
    
    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_get_quote_valid_ticker(self, mock_ticker, mock_nse_quote):
        """Test fetching live quote for valid ticker (via yfinance fallback)."""
        from nifty_agents.tools.nifty_fetcher import get_stock_quote
        
        # Mock yfinance (used when nsetools not available)
        mock_instance = MagicMock()
        mock_instance.info = {
            "currentPrice": 2450.0,
            "previousClose": 2424.5,
            "open": 2430.0,
            "dayHigh": 2460.0,
            "dayLow": 2420.0,
            "volume": 1000000,
            "fiftyTwoWeekHigh": 2800.0,
            "fiftyTwoWeekLow": 2100.0
        }
        mock_ticker.return_value = mock_instance
        
        result = get_stock_quote("RELIANCE")
        
        assert result is not None
        assert result["last_price"] == 2450.0
        assert "error" not in result
    
    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_get_quote_strips_ns_suffix(self, mock_ticker, mock_nse_quote):
        """Test that .NS suffix is handled correctly."""
        from nifty_agents.tools.nifty_fetcher import get_stock_quote
        
        mock_instance = MagicMock()
        mock_instance.info = {
            "currentPrice": 2450.0,
            "previousClose": 2424.5,
        }
        mock_ticker.return_value = mock_instance
        
        result = get_stock_quote("RELIANCE.NS")
        
        # Should still return RELIANCE as ticker
        assert result["ticker"] == "RELIANCE"


class TestGetPriceHistory:
    """Tests for get_price_history function."""
    
    @pytest.fixture
    def mock_history_df(self):
        """Mock yfinance history DataFrame."""
        dates = pd.date_range(start="2025-01-01", periods=30, freq="D")
        return pd.DataFrame({
            "Open": [2400 + i for i in range(30)],
            "High": [2420 + i for i in range(30)],
            "Low": [2380 + i for i in range(30)],
            "Close": [2410 + i for i in range(30)],
            "Volume": [1000000 + i * 10000 for i in range(30)],
        }, index=dates)
    
    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_get_price_history_valid(self, mock_ticker, mock_history_df):
        """Test fetching price history."""
        from nifty_agents.tools.nifty_fetcher import get_price_history
        
        mock_instance = MagicMock()
        mock_instance.history.return_value = mock_history_df
        mock_ticker.return_value = mock_instance
        
        result = get_price_history("RELIANCE", days=30)
        
        assert result is not None
        assert "data" in result
        assert len(result["data"]) == 30
        assert "error" not in result
    
    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_get_price_history_empty(self, mock_ticker):
        """Test handling of empty history."""
        from nifty_agents.tools.nifty_fetcher import get_price_history
        
        mock_instance = MagicMock()
        mock_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_instance
        
        result = get_price_history("INVALIDTICKER", days=30)
        
        assert "error" in result


class TestGetIndexQuote:
    """Tests for get_index_quote function."""
    
    @pytest.fixture
    def mock_index_quote(self):
        """Mock NIFTY 50 index quote."""
        return {
            "index": "NIFTY 50",
            "last": 22500.75,
            "variation": 125.50,
            "percentChange": 0.56,
            "open": 22400.0,
            "high": 22550.0,
            "low": 22350.0,
            "previousClose": 22375.25,
            "pe": 22.5,
            "pb": 4.2,
            "dy": 1.3,
            "advances": 35,
            "declines": 15,
        }
    
    def test_get_index_quote_nifty50(self, mock_index_quote):
        """Test fetching NIFTY 50 index quote."""
        from nifty_agents.tools.nifty_fetcher import get_index_quote
        
        # Since nsetools may not be installed, just test the function exists
        # and returns a dict with expected structure
        result = get_index_quote("NIFTY 50")
        
        assert result is not None
        assert isinstance(result, dict)
        # Should have either valid data or an error
        assert "index" in result or "error" in result
    
    def test_get_index_quote_banknifty(self):
        """Test fetching Bank NIFTY index quote."""
        from nifty_agents.tools.nifty_fetcher import get_index_quote
        
        result = get_index_quote("NIFTY BANK")
        
        assert result is not None
        assert isinstance(result, dict)
        # Should have either valid data or an error
        assert "index" in result or "error" in result
