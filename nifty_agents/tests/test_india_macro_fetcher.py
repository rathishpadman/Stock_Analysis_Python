"""
Test suite for India Macro data fetcher.

TDD Approach: Tests written BEFORE implementation.
Run with: pytest nifty_agents/tests/test_india_macro_fetcher.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestGetMacroIndicators:
    """Tests for get_macro_indicators function."""
    
    @pytest.fixture
    def mock_rbi_rates(self):
        """Mock RBI rates response."""
        return {
            "repo_rate": 6.50,
            "reverse_repo_rate": 3.35,
            "bank_rate": 6.75,
            "crr": 4.50,
            "slr": 18.00,
            "msf_rate": 6.75,
        }
    
    @pytest.fixture
    def mock_india_vix(self):
        """Mock India VIX response."""
        return {
            "index": "INDIA VIX",
            "last": 14.25,
            "variation": -0.35,
            "percentChange": -2.4,
        }
    
    @patch('nifty_agents.tools.india_macro_fetcher.get_rbi_rates')
    @patch('nifty_agents.tools.india_macro_fetcher.get_india_vix')
    def test_get_macro_indicators_success(self, mock_vix, mock_rbi, mock_rbi_rates, mock_india_vix):
        """Test fetching all macro indicators."""
        from nifty_agents.tools.india_macro_fetcher import get_macro_indicators
        
        mock_rbi.return_value = mock_rbi_rates
        mock_vix.return_value = mock_india_vix
        
        result = get_macro_indicators()
        
        assert result is not None
        assert "rbi_rates" in result
        assert "india_vix" in result
        assert "market_regime" in result
        assert "timestamp" in result
    
    def test_get_macro_indicators_handles_partial_failure(self):
        """Test graceful handling when some data sources fail."""
        from nifty_agents.tools.india_macro_fetcher import get_macro_indicators
        
        with patch('nifty_agents.tools.india_macro_fetcher.get_rbi_rates') as mock_rbi:
            mock_rbi.side_effect = Exception("RBI API down")
            
            with patch('nifty_agents.tools.india_macro_fetcher.get_india_vix') as mock_vix:
                mock_vix.return_value = {"index": "INDIA VIX", "last": 14.0}
                
                result = get_macro_indicators()
                
                # Should still return partial data with error flag
                assert result is not None
                assert "india_vix" in result


class TestGetIndiaVix:
    """Tests for get_india_vix function."""
    
    @patch('nifty_agents.tools.india_macro_fetcher.Nse')
    def test_get_india_vix_success(self, mock_nse_class):
        """Test fetching India VIX."""
        from nifty_agents.tools.india_macro_fetcher import get_india_vix
        
        mock_nse = MagicMock()
        mock_nse.get_index_quote.return_value = {
            "index": "INDIA VIX",
            "last": 14.25,
            "variation": -0.35,
            "percentChange": -2.4,
        }
        mock_nse_class.return_value = mock_nse
        
        result = get_india_vix()
        
        mock_nse.get_index_quote.assert_called_with("INDIA VIX")
        assert result["value"] == 14.25
        assert result["change_pct"] == -2.4
    
    @patch('nifty_agents.tools.india_macro_fetcher.Nse')
    def test_get_india_vix_determines_fear_level(self, mock_nse_class):
        """Test that VIX value is categorized into fear levels."""
        from nifty_agents.tools.india_macro_fetcher import get_india_vix
        
        mock_nse = MagicMock()
        
        # Low VIX (< 15) = Low Fear
        mock_nse.get_index_quote.return_value = {"index": "INDIA VIX", "last": 12.0, "percentChange": 0}
        mock_nse_class.return_value = mock_nse
        result = get_india_vix()
        assert result["fear_level"] == "low"
        
        # Moderate VIX (15-20) = Moderate Fear
        mock_nse.get_index_quote.return_value = {"index": "INDIA VIX", "last": 17.0, "percentChange": 0}
        result = get_india_vix()
        assert result["fear_level"] == "moderate"
        
        # Elevated VIX (20-25) = Elevated Fear
        mock_nse.get_index_quote.return_value = {"index": "INDIA VIX", "last": 22.0, "percentChange": 0}
        result = get_india_vix()
        assert result["fear_level"] == "elevated"
        
        # High VIX (25-30) = High Fear
        mock_nse.get_index_quote.return_value = {"index": "INDIA VIX", "last": 28.0, "percentChange": 0}
        result = get_india_vix()
        assert result["fear_level"] == "high"
        
        # Extreme VIX (> 30) = Extreme Fear
        mock_nse.get_index_quote.return_value = {"index": "INDIA VIX", "last": 35.0, "percentChange": 0}
        result = get_india_vix()
        assert result["fear_level"] == "extreme"


class TestGetRbiRates:
    """Tests for get_rbi_rates function."""
    
    @patch('nifty_agents.tools.india_macro_fetcher.RBI')
    def test_get_rbi_rates_success(self, mock_rbi_class):
        """Test fetching RBI policy rates."""
        from nifty_agents.tools.india_macro_fetcher import get_rbi_rates
        
        mock_rbi = MagicMock()
        mock_rbi.current_rates.return_value = {
            "repo_rate": 6.50,
            "reverse_repo_rate": 3.35,
            "crr": 4.50,
            "slr": 18.00,
        }
        mock_rbi_class.return_value = mock_rbi
        
        result = get_rbi_rates()
        
        assert result is not None
        assert result["repo_rate"] == 6.50
        assert "policy_stance" in result  # Should interpret the rates
    
    @patch('nifty_agents.tools.india_macro_fetcher.RBI')
    def test_get_rbi_rates_determines_policy_stance(self, mock_rbi_class):
        """Test that RBI rates are interpreted for policy stance."""
        from nifty_agents.tools.india_macro_fetcher import get_rbi_rates
        
        mock_rbi = MagicMock()
        
        # High repo rate (> 6%) = Hawkish
        mock_rbi.current_rates.return_value = {"repo_rate": 7.0}
        mock_rbi_class.return_value = mock_rbi
        result = get_rbi_rates()
        assert result["policy_stance"] in ["hawkish", "neutral"]
        
        # Low repo rate (< 5%) = Dovish
        mock_rbi.current_rates.return_value = {"repo_rate": 4.0}
        result = get_rbi_rates()
        assert result["policy_stance"] in ["dovish", "neutral"]


class TestMarketRegime:
    """Tests for market regime determination."""
    
    def test_determine_market_regime_bullish(self):
        """Test bullish market regime detection."""
        from nifty_agents.tools.india_macro_fetcher import determine_market_regime
        
        indicators = {
            "india_vix": {"value": 12.0},  # Low fear
            "nifty_pe": 20.0,  # Reasonable valuation
            "rbi_rates": {"repo_rate": 5.5},  # Accommodative
        }
        
        result = determine_market_regime(indicators)
        assert result in ["bullish", "neutral"]
    
    def test_determine_market_regime_bearish(self):
        """Test bearish market regime detection."""
        from nifty_agents.tools.india_macro_fetcher import determine_market_regime
        
        indicators = {
            "india_vix": {"value": 35.0},  # High fear
            "nifty_pe": 28.0,  # High valuation
            "rbi_rates": {"repo_rate": 7.5},  # Restrictive
        }
        
        result = determine_market_regime(indicators)
        assert result in ["bearish", "cautious", "neutral"]
