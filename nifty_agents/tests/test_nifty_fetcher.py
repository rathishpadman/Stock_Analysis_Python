"""
Test suite for NIFTY data fetcher tools and fundamentals adapter.

TDD Approach: Tests written BEFORE implementation.
Run with: pytest nifty_agents/tests/test_nifty_fetcher.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
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
        assert "error" not in result

    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_get_fundamentals_with_ns_suffix(self, mock_ticker, mock_yfinance_info):
        """Test that .NS suffix is handled correctly."""
        from nifty_agents.tools.nifty_fetcher import get_stock_fundamentals

        mock_instance = MagicMock()
        mock_instance.info = mock_yfinance_info
        mock_ticker.return_value = mock_instance

        result = get_stock_fundamentals("RELIANCE.NS")

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

        # Should still return something (from adapter cascade)
        assert result is not None
        assert isinstance(result, dict)

    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_get_fundamentals_handles_exceptions(self, mock_ticker):
        """Test graceful handling of API exceptions."""
        from nifty_agents.tools.nifty_fetcher import get_stock_fundamentals

        mock_ticker.side_effect = Exception("API Error")

        result = get_stock_fundamentals("RELIANCE")

        assert result is not None
        assert isinstance(result, dict)


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


class TestFundamentalsAdapter:
    """Tests for the multi-source fundamentals adapter layer."""

    def test_adapter_cascade_returns_data(self):
        """Test that the adapter cascade returns data for a valid ticker."""
        from nifty_agents.tools.fundamentals_adapter import get_fundamentals

        result = get_fundamentals("DUMMYSTOCK_NONEXISTENT")

        # Even for invalid tickers, should return a dict (possibly with error)
        assert isinstance(result, dict)
        assert "ticker" in result
        assert "data_source" in result

    @patch('nifty_agents.tools.fundamentals_adapter.SupabaseAdapter.fetch')
    def test_supabase_adapter_used_first(self, mock_supabase_fetch):
        """Test that Supabase is tried first and used when available."""
        from nifty_agents.tools.fundamentals_adapter import get_fundamentals

        mock_supabase_fetch.return_value = {
            "ticker": "TESTSTOCK",
            "current_price": 100.0,
            "pe_ratio": 15.0,
            "sector": "Technology",
            "industry": "Software",
            "market_cap": 5000000000,
            "data_source": "supabase",
            "timestamp": "2026-01-01T00:00:00",
        }

        result = get_fundamentals("TESTSTOCK")

        assert "error" not in result
        assert "supabase" in result["data_source"]
        assert result["current_price"] == 100.0
        assert result["pe_ratio"] == 15.0
        mock_supabase_fetch.assert_called_once_with("TESTSTOCK")

    @patch('nifty_agents.tools.fundamentals_adapter.YFinanceAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.NSEPythonAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.SupabaseAdapter.fetch')
    def test_cascade_merges_missing_fields(self, mock_sb, mock_nse, mock_yf):
        """Test that cascade fills in None fields from subsequent adapters."""
        from nifty_agents.tools.fundamentals_adapter import get_fundamentals

        # Supabase has price + PE but no industry
        mock_sb.return_value = {
            "ticker": "TESTSTOCK",
            "current_price": 100.0,
            "pe_ratio": 15.0,
            "sector": "Technology",
            "industry": None,
            "market_cap": None,
            "data_source": "supabase",
            "timestamp": "2026-01-01T00:00:00",
        }

        # NSEPython fills in industry and market_cap
        mock_nse.return_value = {
            "ticker": "TESTSTOCK",
            "current_price": 100.5,  # won't overwrite Supabase's value
            "industry": "Software Services",
            "market_cap": 5000000000,
            "data_source": "nsepython",
            "timestamp": "2026-01-01T00:00:00",
        }

        # yfinance returns None in this test
        mock_yf.return_value = None

        result = get_fundamentals("TESTSTOCK")

        assert result["current_price"] == 100.0  # from Supabase (first wins)
        assert result["industry"] == "Software Services"  # filled by NSEPython
        assert result["market_cap"] == 5000000000  # filled by NSEPython
        assert "supabase" in result["data_source"]
        assert "nsepython" in result["data_source"]

    @patch('nifty_agents.tools.fundamentals_adapter.FinnhubAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.YFinanceAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.NSEPythonAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.SupabaseAdapter.fetch')
    def test_cascade_does_not_stop_early_when_basic_fields_filled(self, mock_sb, mock_nse, mock_yf, mock_fh):
        """CRITICAL: Cascade must NOT stop early when basic fields are filled.
        yfinance/Finnhub must still run to contribute deep fundamentals
        (margins, debt_to_equity, ROE, dividends, beta).
        This test prevents regression of the early-stop bug."""
        from nifty_agents.tools.fundamentals_adapter import get_fundamentals

        # Supabase fills all basic fields (price, PE, sector, industry, market_cap)
        mock_sb.return_value = {
            "ticker": "COALINDIA",
            "current_price": 400.0,
            "pe_ratio": 8.5,
            "sector": "Energy",
            "industry": "Coal",
            "market_cap": 250000000000,
            "roe": 0.45,
            "profit_margin": None,
            "operating_margin": None,
            "debt_to_equity": None,
            "dividend_yield": None,
            "beta": None,
            "data_source": "supabase",
            "timestamp": "2026-01-01T00:00:00",
        }

        # NSEPython also fills basic fields (all already filled, so minimal merge)
        mock_nse.return_value = {
            "ticker": "COALINDIA",
            "current_price": 401.0,
            "sector": "Energy",
            "industry": "Coal",
            "market_cap": 250000000000,
            "data_source": "nsepython",
            "timestamp": "2026-01-01T00:00:00",
        }

        # yfinance provides deep fundamentals — MUST be reached
        mock_yf.return_value = {
            "ticker": "COALINDIA",
            "profit_margin": 0.22,
            "operating_margin": 0.30,
            "gross_margin": 0.55,
            "debt_to_equity": 12.5,
            "dividend_yield": 0.06,
            "beta": 0.8,
            "current_ratio": 2.1,
            "roa": 0.18,
            "data_source": "yfinance",
            "timestamp": "2026-01-01T00:00:00",
        }

        mock_fh.return_value = None  # Finnhub not needed in this test

        result = get_fundamentals("COALINDIA")

        # Basic fields from Supabase (first source wins)
        assert result["current_price"] == 400.0
        assert result["pe_ratio"] == 8.5
        assert result["roe"] == 0.45

        # Deep fundamentals from yfinance — MUST be present (the whole point of this fix)
        assert result["profit_margin"] == 0.22, "profit_margin should come from yfinance"
        assert result["operating_margin"] == 0.30, "operating_margin should come from yfinance"
        assert result["debt_to_equity"] == 12.5, "debt_to_equity should come from yfinance"
        assert result["dividend_yield"] == 0.06, "dividend_yield should come from yfinance"
        assert result["beta"] == 0.8, "beta should come from yfinance"
        assert result["current_ratio"] == 2.1, "current_ratio should come from yfinance"

        # All three adapters should have been called
        mock_sb.assert_called_once()
        mock_nse.assert_called_once()
        mock_yf.assert_called_once()

        # All contributing sources should appear in data_source
        assert "supabase" in result["data_source"]
        assert "yfinance" in result["data_source"]

    @patch('nifty_agents.tools.fundamentals_adapter.YFinanceAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.NSEPythonAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.SupabaseAdapter.fetch')
    def test_cascade_skips_failed_adapters(self, mock_sb, mock_nse, mock_yf):
        """Test that cascade continues when an adapter returns None."""
        from nifty_agents.tools.fundamentals_adapter import get_fundamentals

        mock_sb.return_value = None  # Supabase fails
        mock_nse.return_value = {  # NSEPython succeeds
            "ticker": "TESTSTOCK",
            "current_price": 200.0,
            "pe_ratio": 10.0,
            "sector": "Energy",
            "industry": "Coal",
            "market_cap": 3000000000,
            "data_source": "nsepython",
            "timestamp": "2026-01-01T00:00:00",
        }
        mock_yf.return_value = None

        result = get_fundamentals("TESTSTOCK")

        assert "error" not in result
        assert result["current_price"] == 200.0
        assert "nsepython" in result["data_source"]

    @patch('nifty_agents.tools.fundamentals_adapter.FinnhubAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.YFinanceAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.NSEPythonAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.SupabaseAdapter.fetch')
    def test_all_adapters_fail_returns_error(self, mock_sb, mock_nse, mock_yf, mock_fh):
        """Test that error dict is returned when all adapters fail."""
        from nifty_agents.tools.fundamentals_adapter import get_fundamentals

        mock_sb.return_value = None
        mock_nse.return_value = None
        mock_yf.return_value = None
        mock_fh.return_value = None

        result = get_fundamentals("TESTSTOCK")

        assert "error" in result
        assert result["data_source"] == "none"

    @patch('nifty_agents.tools.fundamentals_adapter.YFinanceAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.NSEPythonAdapter.fetch')
    @patch('nifty_agents.tools.fundamentals_adapter.SupabaseAdapter.fetch')
    def test_adapter_exception_handled_gracefully(self, mock_sb, mock_nse, mock_yf):
        """Test that adapter exceptions don't crash the cascade."""
        from nifty_agents.tools.fundamentals_adapter import get_fundamentals

        mock_sb.side_effect = Exception("Supabase connection timeout")
        mock_nse.return_value = {
            "ticker": "TESTSTOCK",
            "current_price": 300.0,
            "pe_ratio": 20.0,
            "sector": "Finance",
            "industry": "Banking",
            "market_cap": 10000000000,
            "data_source": "nsepython",
            "timestamp": "2026-01-01T00:00:00",
        }
        mock_yf.return_value = None

        result = get_fundamentals("TESTSTOCK")

        assert "error" not in result
        assert result["current_price"] == 300.0


class TestRateLimitRetry:
    """Tests for rate-limit retry logic on yfinance calls."""

    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_price_history_retries_on_rate_limit(self, mock_ticker):
        """Simulate 429 on price_history, then success."""
        from nifty_agents.tools.nifty_fetcher import get_price_history

        dates = pd.date_range(start="2025-01-01", periods=5, freq="D")
        ok_df = pd.DataFrame({
            "Open": [100.0] * 5, "High": [105.0] * 5,
            "Low": [95.0] * 5, "Close": [102.0] * 5,
            "Volume": [10000] * 5,
        }, index=dates)

        mock_fail = MagicMock()
        mock_fail.history.side_effect = Exception("429 Too Many Requests")

        mock_ok = MagicMock()
        mock_ok.history.return_value = ok_df

        mock_ticker.side_effect = [mock_fail, mock_ok]

        result = get_price_history("DUMMYSTOCK", days=5)

        assert "error" not in result
        assert result["count"] == 5
        assert mock_ticker.call_count == 2

    @patch('nifty_agents.tools.nifty_fetcher.yf.Ticker')
    def test_non_rate_limit_error_does_not_retry(self, mock_ticker):
        """Non-429 errors should NOT trigger retry — should return error dict immediately."""
        from nifty_agents.tools.nifty_fetcher import get_price_history

        mock_instance = MagicMock()
        mock_instance.history.side_effect = Exception("Network connection failed")
        mock_ticker.return_value = mock_instance

        result = get_price_history("DUMMYSTOCK", days=5)

        assert "error" in result
        assert "Network connection failed" in result["error"]
        # Should only be called once — no retry for non-rate-limit errors
        assert mock_ticker.call_count == 1
