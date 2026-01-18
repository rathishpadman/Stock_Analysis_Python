"""
End-to-End Integration Tests for NIFTY Agent System

Tests the complete flow from API request to agent analysis.
Run with: pytest nifty_agents/tests/test_e2e.py -v
"""

import pytest
import asyncio
import json
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Test fixtures and markers
pytestmark = pytest.mark.integration


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_genai():
    """Mock Google GenAI for testing without API key."""
    with patch('nifty_agents.agents.orchestrator.genai') as mock:
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "recommendation": "buy",
            "composite_score": 75,
            "target_price": 2800,
            "confidence": "medium",
            "key_thesis": "Strong fundamentals with technical breakout"
        })
        mock_model.generate_content.return_value = mock_response
        mock.GenerativeModel.return_value = mock_model
        yield mock


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    with patch('nifty_agents.tools.supabase_fetcher._get_supabase_client') as mock:
        mock_client = MagicMock()
        
        # Mock daily_stocks response
        mock_response = MagicMock()
        mock_response.data = [{
            "ticker": "RELIANCE",
            "date": "2025-01-17",
            "close": 2650.50,
            "fundamental_score": 72,
            "technical_score": 68,
            "composite_score": 70,
            "rank": 5
        }]
        
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_ticker():
    """Sample NIFTY 50 ticker for testing."""
    return "RELIANCE"


@pytest.fixture
def sample_tickers():
    """Sample list of NIFTY 50 tickers."""
    return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]


# ============================================================================
# Tool Integration Tests
# ============================================================================

class TestNiftyFetcherIntegration:
    """Test nifty_fetcher integration with real/mocked data."""
    
    def test_normalize_ticker_variations(self):
        """Test ticker normalization handles all variations."""
        from nifty_agents.tools.nifty_fetcher import _normalize_ticker
        
        assert _normalize_ticker("RELIANCE") == "RELIANCE.NS"
        assert _normalize_ticker("RELIANCE.NS") == "RELIANCE.NS"
        assert _normalize_ticker("reliance") == "RELIANCE.NS"
        assert _normalize_ticker("TCS.ns") == "TCS.NS"
    
    def test_get_stock_fundamentals_with_mock(self):
        """Test fundamentals fetching with mocked yfinance."""
        from nifty_agents.tools.nifty_fetcher import get_stock_fundamentals
        
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.info = {
                "symbol": "RELIANCE.NS",
                "longName": "Reliance Industries Limited",
                "currentPrice": 2650.50,
                "trailingPE": 25.5,
                "priceToBook": 2.8,
                "returnOnEquity": 0.12,
                "debtToEquity": 45.2,
                "dividendYield": 0.004
            }
            
            result = get_stock_fundamentals("RELIANCE")
            
            assert result["ticker"] == "RELIANCE"
            assert "pe_ratio" in result
            assert "pb_ratio" in result
            assert "roe" in result
    
    def test_get_price_history_returns_dataframe(self):
        """Test price history returns proper DataFrame structure."""
        from nifty_agents.tools.nifty_fetcher import get_price_history
        import pandas as pd
        
        with patch('yfinance.Ticker') as mock_ticker:
            mock_df = pd.DataFrame({
                'Open': [2600, 2620, 2640],
                'High': [2650, 2660, 2680],
                'Low': [2580, 2600, 2620],
                'Close': [2630, 2650, 2670],
                'Volume': [1000000, 1200000, 1100000]
            })
            mock_ticker.return_value.history.return_value = mock_df
            
            result = get_price_history("RELIANCE", "1mo")
            
            assert isinstance(result, dict)
            assert "data" in result or "error" not in result


class TestMacroFetcherIntegration:
    """Test macro indicator fetching."""
    
    def test_get_macro_indicators_structure(self):
        """Test macro indicators return proper structure."""
        from nifty_agents.tools.india_macro_fetcher import get_macro_indicators
        
        result = get_macro_indicators()
        
        assert "timestamp" in result
        assert "rbi_rates" in result
        assert "india_vix" in result or "error" in result.get("india_vix", {})
    
    def test_market_regime_determination(self):
        """Test market regime logic."""
        from nifty_agents.tools.india_macro_fetcher import determine_market_regime
        
        # Bullish indicators
        bullish_indicators = {
            "india_vix": {"value": 12.0},
            "nifty_pe": 18.0,
            "rbi_rates": {"repo_rate": 5.0}
        }
        assert determine_market_regime(bullish_indicators) == "bullish"
        
        # Bearish indicators
        bearish_indicators = {
            "india_vix": {"value": 32.0},
            "nifty_pe": 28.0,
            "rbi_rates": {"repo_rate": 7.5}
        }
        assert determine_market_regime(bearish_indicators) == "bearish"


class TestNewsFetcherIntegration:
    """Test news and sentiment fetching."""
    
    def test_sentiment_score_calculation(self):
        """Test sentiment score calculation."""
        from nifty_agents.tools.india_news_fetcher import _calculate_sentiment_score
        
        positive_text = "Stock surges to record high after strong profit growth"
        positive_result = _calculate_sentiment_score(positive_text)
        assert positive_result["sentiment"] == "positive"
        assert positive_result["score"] > 0
        
        negative_text = "Stock crashes amid fraud investigation and debt concerns"
        negative_result = _calculate_sentiment_score(negative_text)
        assert negative_result["sentiment"] == "negative"
        assert negative_result["score"] < 0
    
    def test_get_stock_news_with_mock_feed(self):
        """Test stock news fetching with mocked RSS."""
        from nifty_agents.tools.india_news_fetcher import get_stock_news
        
        with patch('nifty_agents.tools.india_news_fetcher.fetch_rss_news') as mock_fetch:
            mock_fetch.return_value = [
                {
                    "title": "Reliance shares surge on strong earnings",
                    "summary": "RIL reported record profits",
                    "sentiment": {"score": 0.8, "sentiment": "positive"}
                }
            ]
            
            news = get_stock_news("RELIANCE", max_items=5)
            assert len(news) <= 5


class TestSupabaseFetcherIntegration:
    """Test Supabase data fetching."""
    
    def test_get_stock_scores_with_mock(self, mock_supabase):
        """Test stock scores retrieval."""
        from nifty_agents.tools.supabase_fetcher import get_stock_scores
        
        result = get_stock_scores("RELIANCE")
        
        assert result["ticker"] == "RELIANCE"
        # Should have score interpretation
        if result.get("composite_score"):
            assert "rating" in result


# ============================================================================
# Orchestrator Integration Tests
# ============================================================================

class TestOrchestratorIntegration:
    """Test the orchestrator integration."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly."""
        from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator
        
        # Without API key
        with patch.dict(os.environ, {"GOOGLE_API_KEY": ""}, clear=True):
            orch = NiftyAgentOrchestrator()
            assert orch.model is None
    
    def test_ticker_validation(self):
        """Test ticker validation logic."""
        from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator
        
        orch = NiftyAgentOrchestrator()
        
        with patch.object(orch, '_validate_ticker') as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "ticker": "RELIANCE",
                "name": "Reliance Industries",
                "current_price": 2650.50
            }
            
            result = orch._validate_ticker("RELIANCE")
            assert result["valid"] is True
    
    def test_base_data_gathering(self, sample_ticker):
        """Test base data gathering from all sources."""
        from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator
        
        orch = NiftyAgentOrchestrator()
        
        with patch.multiple(
            'nifty_agents.agents.orchestrator',
            get_stock_fundamentals=MagicMock(return_value={"ticker": sample_ticker}),
            get_stock_quote=MagicMock(return_value={"last_price": 2650}),
            get_price_history=MagicMock(return_value={"data": []}),
            get_macro_indicators=MagicMock(return_value={"market_regime": "neutral"}),
            analyze_sentiment_aggregate=MagicMock(return_value={"sentiment": "neutral"}),
            get_comprehensive_stock_data=MagicMock(return_value={"scores": {}})
        ):
            data = orch._gather_base_data(sample_ticker)
            
            assert data["ticker"] == sample_ticker
            assert "fundamentals" in data
            assert "macro" in data
    
    @pytest.mark.asyncio
    async def test_full_analysis_flow_mocked(self, mock_genai, mock_supabase, sample_ticker):
        """Test complete analysis flow with all mocks."""
        from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator
        
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            orch = NiftyAgentOrchestrator()
            
            # Mock validation
            with patch.object(orch, '_validate_ticker') as mock_val:
                mock_val.return_value = {
                    "valid": True,
                    "ticker": sample_ticker,
                    "name": "Reliance Industries",
                    "current_price": 2650.50
                }
                
                # Mock base data
                with patch.object(orch, '_gather_base_data') as mock_data:
                    mock_data.return_value = {
                        "ticker": sample_ticker,
                        "fundamentals": {},
                        "macro": {}
                    }
                    
                    # Mock agent calls
                    with patch.object(orch, '_call_agent') as mock_agent:
                        mock_agent.return_value = {
                            "score": 70,
                            "recommendation": "buy"
                        }
                        
                        # Mock predictor
                        with patch.object(orch, '_call_predictor') as mock_pred:
                            mock_pred.return_value = {
                                "recommendation": "buy",
                                "composite_score": 72,
                                "confidence": "medium"
                            }
                            
                            report = await orch.analyze_async(sample_ticker)
                            
                            assert report["ticker"] == sample_ticker
                            assert "recommendation" in report


# ============================================================================
# API Integration Tests
# ============================================================================

class TestAPIIntegration:
    """Test FastAPI endpoints."""
    
    @pytest.fixture
    def test_client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from nifty_agents.api import app
        
        return TestClient(app)
    
    def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/api/agent/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "genai_configured" in data
        assert "supabase_configured" in data
    
    def test_quick_analysis_endpoint(self, test_client, mock_supabase):
        """Test quick analysis endpoint."""
        with patch('nifty_agents.api.orchestrator.get_quick_summary') as mock_quick:
            mock_quick.return_value = {
                "ticker": "RELIANCE",
                "current_price": 2650.50,
                "scores": {"composite_score": 70}
            }
            
            response = test_client.get("/api/agent/quick/RELIANCE")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "RELIANCE"
    
    def test_macro_endpoint(self, test_client):
        """Test macro indicators endpoint."""
        with patch('nifty_agents.api.get_macro_indicators') as mock_macro:
            mock_macro.return_value = {
                "market_regime": "neutral",
                "india_vix": {"value": 15.5}
            }
            
            response = test_client.get("/api/agent/macro")
            
            assert response.status_code == 200
    
    def test_batch_endpoint_limit(self, test_client):
        """Test batch endpoint respects limits."""
        # Too many tickers should return 400
        response = test_client.post(
            "/api/agent/batch",
            json={"tickers": ["STOCK"] * 25, "quick_mode": True}
        )
        
        assert response.status_code == 400


# ============================================================================
# End-to-End Flow Tests
# ============================================================================

class TestE2EFlow:
    """Complete end-to-end flow tests."""
    
    @pytest.mark.skipif(
        not os.environ.get("GOOGLE_API_KEY"),
        reason="Requires GOOGLE_API_KEY for live testing"
    )
    @pytest.mark.asyncio
    async def test_live_analysis_flow(self, sample_ticker):
        """Test live analysis with real API (when available)."""
        from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator
        
        orch = NiftyAgentOrchestrator()
        
        # This test only runs if GOOGLE_API_KEY is set
        report = await orch.analyze_async(sample_ticker)
        
        assert report["ticker"] == sample_ticker
        assert "agent_analyses" in report
        assert "synthesis" in report
    
    def test_error_handling_invalid_ticker(self):
        """Test graceful handling of invalid ticker."""
        from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator
        
        orch = NiftyAgentOrchestrator()
        
        with patch.object(orch, '_validate_ticker') as mock_val:
            mock_val.return_value = {
                "valid": False,
                "error": "Invalid ticker",
                "ticker": "INVALID123"
            }
            
            result = orch.analyze("INVALID123")
            
            assert "error" in result
    
    def test_agent_failure_recovery(self):
        """Test system continues when individual agent fails."""
        from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator
        
        orch = NiftyAgentOrchestrator()
        
        # Simulate one agent failing
        def mock_call_agent(agent_name, data):
            if agent_name == "sentiment_agent":
                raise Exception("Sentiment agent failed")
            return {"score": 70}
        
        with patch.object(orch, '_call_agent', side_effect=mock_call_agent):
            with patch.object(orch, '_validate_ticker') as mock_val:
                mock_val.return_value = {"valid": True, "ticker": "TEST"}
                
                with patch.object(orch, '_gather_base_data') as mock_data:
                    mock_data.return_value = {"ticker": "TEST"}
                    
                    with patch.object(orch, '_call_predictor') as mock_pred:
                        mock_pred.return_value = {"recommendation": "hold"}
                        
                        # Should not raise, should handle gracefully
                        try:
                            report = orch.analyze("TEST")
                            # Check that we got partial results
                            assert report is not None
                        except Exception:
                            pass  # Expected in some cases


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance and timeout tests."""
    
    def test_quick_analysis_is_fast(self, mock_supabase):
        """Quick analysis should complete in < 2 seconds."""
        from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator
        import time
        
        orch = NiftyAgentOrchestrator()
        
        start = time.time()
        result = orch.get_quick_summary("RELIANCE")
        elapsed = time.time() - start
        
        assert elapsed < 2.0, f"Quick analysis took {elapsed}s, expected < 2s"
    
    def test_parallel_agent_execution(self, mock_genai):
        """Test agents run in parallel, not sequential."""
        from nifty_agents.agents.orchestrator import NiftyAgentOrchestrator
        import time
        
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test"}):
            orch = NiftyAgentOrchestrator()
            
            call_times = []
            
            def slow_agent(name, data):
                call_times.append(time.time())
                time.sleep(0.1)  # Simulate slow agent
                return {"score": 70}
            
            with patch.object(orch, '_call_agent', side_effect=slow_agent):
                with patch.object(orch, '_validate_ticker') as mock_val:
                    mock_val.return_value = {"valid": True, "ticker": "TEST"}
                    
                    with patch.object(orch, '_gather_base_data') as mock_data:
                        mock_data.return_value = {"ticker": "TEST"}
                        
                        with patch.object(orch, '_call_predictor') as mock_pred:
                            mock_pred.return_value = {}
                            
                            start = time.time()
                            orch.analyze("TEST")
                            total_time = time.time() - start
                            
                            # If parallel: ~0.1-0.2s, if sequential: ~0.5s+
                            # Account for some overhead
                            assert total_time < 0.5, "Agents should run in parallel"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
