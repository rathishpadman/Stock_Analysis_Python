"""
Unit Tests for Temporal Analysis Crews

Tests for:
- WeeklyAnalysisCrew
- MonthlyAnalysisCrew
- SeasonalityAnalysisCrew
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

# Import the crews
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nifty_agents.agents.temporal_crews import (
    BaseTemporalCrew,
    WeeklyAnalysisCrew,
    MonthlyAnalysisCrew,
    SeasonalityAnalysisCrew,
    WEEKLY_AGENT_PROMPTS,
    MONTHLY_AGENT_PROMPTS,
    SEASONALITY_AGENT_PROMPTS,
)


class TestBaseTemporalCrew:
    """Tests for BaseTemporalCrew class."""
    
    def test_initialization_without_api_key(self):
        """Test that crew initializes gracefully without API key."""
        with patch.dict('os.environ', {}, clear=True):
            crew = BaseTemporalCrew()
            # Should not raise, but model may be None
            assert crew.timeout == 60
    
    def test_initialization_with_custom_timeout(self):
        """Test custom timeout setting."""
        crew = BaseTemporalCrew(timeout=120)
        assert crew.timeout == 120


class TestWeeklyAnalysisCrew:
    """Tests for WeeklyAnalysisCrew class."""
    
    def test_prompts_exist(self):
        """Test that all required prompts are defined."""
        required_prompts = [
            "trend_agent",
            "sector_rotation_agent",
            "risk_regime_agent",
            "weekly_synthesizer"
        ]
        for prompt_key in required_prompts:
            assert prompt_key in WEEKLY_AGENT_PROMPTS
            assert len(WEEKLY_AGENT_PROMPTS[prompt_key]) > 100
    
    def test_prompt_contains_json_output(self):
        """Test that prompts request JSON output format."""
        for key, prompt in WEEKLY_AGENT_PROMPTS.items():
            assert "JSON" in prompt or "json" in prompt
    
    @pytest.mark.asyncio
    async def test_analyze_returns_structure(self):
        """Test that analyze returns expected structure."""
        crew = WeeklyAnalysisCrew(api_key="fake_key")
        
        # Mock the model
        crew.model = None  # Force error path
        
        result = await crew.analyze()
        
        # Should have error or analysis structure
        assert "error" in result or "analysis_type" in result
    
    def test_market_breadth_helper(self):
        """Test _get_market_breadth_data helper."""
        crew = WeeklyAnalysisCrew()
        result = crew._get_market_breadth_data()
        
        # Should return dict (even if error)
        assert isinstance(result, dict)
    
    def test_fii_dii_helper(self):
        """Test _get_fii_dii_weekly helper."""
        crew = WeeklyAnalysisCrew()
        result = crew._get_fii_dii_weekly()
        
        assert isinstance(result, dict)


class TestMonthlyAnalysisCrew:
    """Tests for MonthlyAnalysisCrew class."""
    
    def test_prompts_exist(self):
        """Test that all required prompts are defined."""
        required_prompts = [
            "macro_cycle_agent",
            "fund_flow_agent",
            "valuation_regime_agent",
            "monthly_strategist"
        ]
        for prompt_key in required_prompts:
            assert prompt_key in MONTHLY_AGENT_PROMPTS
            assert len(MONTHLY_AGENT_PROMPTS[prompt_key]) > 100
    
    @pytest.mark.asyncio
    async def test_analyze_returns_structure(self):
        """Test that analyze returns expected structure."""
        crew = MonthlyAnalysisCrew(api_key="fake_key")
        crew.model = None  # Force error path
        
        result = await crew.analyze()
        
        assert "error" in result or "analysis_type" in result
    
    def test_monthly_flows_helper(self):
        """Test _get_monthly_flows helper."""
        crew = MonthlyAnalysisCrew()
        result = crew._get_monthly_flows()
        
        assert isinstance(result, dict)
        # Should have FII/DII data
        if "error" not in result:
            assert "fii_mtd" in result or "fii_net" in result or "error" in result
    
    def test_valuation_metrics_helper(self):
        """Test _get_valuation_metrics helper."""
        crew = MonthlyAnalysisCrew()
        result = crew._get_valuation_metrics()
        
        assert isinstance(result, dict)
        if "error" not in result:
            assert "nifty_pe" in result


class TestSeasonalityAnalysisCrew:
    """Tests for SeasonalityAnalysisCrew class."""
    
    def test_prompts_exist(self):
        """Test that all required prompts are defined."""
        required_prompts = [
            "historical_pattern_agent",
            "event_calendar_agent",
            "sector_seasonality_agent",
            "seasonality_synthesizer"
        ]
        for prompt_key in required_prompts:
            assert prompt_key in SEASONALITY_AGENT_PROMPTS
            assert len(SEASONALITY_AGENT_PROMPTS[prompt_key]) > 100
    
    @pytest.mark.asyncio
    async def test_analyze_returns_structure(self):
        """Test that analyze returns expected structure."""
        crew = SeasonalityAnalysisCrew(api_key="fake_key")
        crew.model = None  # Force error path
        
        result = await crew.analyze()
        
        assert "error" in result or "analysis_type" in result
    
    def test_event_calendar_helper(self):
        """Test _get_event_calendar helper."""
        crew = SeasonalityAnalysisCrew()
        result = crew._get_event_calendar()
        
        assert isinstance(result, dict)
        assert "event_calendar" in result
        # Should have 12 months
        assert len(result["event_calendar"]) == 12
    
    def test_sector_seasonality_helper(self):
        """Test _get_sector_seasonality helper."""
        crew = SeasonalityAnalysisCrew()
        result = crew._get_sector_seasonality()
        
        assert isinstance(result, dict)
        assert "sector_patterns" in result
        # Should have multiple sectors
        assert len(result["sector_patterns"]) >= 4
    
    def test_historical_patterns_helper(self):
        """Test _get_historical_patterns helper."""
        crew = SeasonalityAnalysisCrew()
        result = crew._get_historical_patterns()
        
        assert isinstance(result, dict)
        assert "current_month" in result


class TestPromptFormats:
    """Tests for prompt format consistency."""
    
    def test_all_prompts_have_output_section(self):
        """All prompts should have OUTPUT section."""
        all_prompts = {
            **WEEKLY_AGENT_PROMPTS,
            **MONTHLY_AGENT_PROMPTS,
            **SEASONALITY_AGENT_PROMPTS
        }
        
        for key, prompt in all_prompts.items():
            assert "OUTPUT" in prompt, f"Prompt {key} missing OUTPUT section"
    
    def test_all_prompts_have_data_placeholder(self):
        """All agent prompts (not synthesizers) should have {data} placeholder."""
        agent_prompts = {
            k: v for k, v in WEEKLY_AGENT_PROMPTS.items() 
            if "synthesizer" not in k
        }
        agent_prompts.update({
            k: v for k, v in MONTHLY_AGENT_PROMPTS.items() 
            if "strategist" not in k
        })
        agent_prompts.update({
            k: v for k, v in SEASONALITY_AGENT_PROMPTS.items() 
            if "synthesizer" not in k
        })
        
        for key, prompt in agent_prompts.items():
            assert "{data}" in prompt, f"Prompt {key} missing {{data}} placeholder"
    
    def test_synthesizer_prompts_have_input_placeholders(self):
        """Synthesizer prompts should have agent input placeholders."""
        assert "{trend_analysis}" in WEEKLY_AGENT_PROMPTS["weekly_synthesizer"]
        assert "{macro_analysis}" in MONTHLY_AGENT_PROMPTS["monthly_strategist"]
        assert "{pattern_analysis}" in SEASONALITY_AGENT_PROMPTS["seasonality_synthesizer"]


class TestDataFetcherIntegration:
    """Tests for data fetcher integration."""
    
    def test_imports_work(self):
        """Test that all imports work correctly."""
        from nifty_agents.agents.temporal_crews import (
            get_weekly_analysis,
            get_monthly_analysis,
            get_seasonality_data,
            get_sector_performance,
            get_market_breadth,
            get_macro_indicators,
            get_india_vix,
            determine_market_regime
        )
        
        # All should be callable
        assert callable(get_weekly_analysis)
        assert callable(get_monthly_analysis)
        assert callable(get_seasonality_data)
        assert callable(get_sector_performance)
        assert callable(get_market_breadth)
        assert callable(get_macro_indicators)
        assert callable(get_india_vix)
        assert callable(determine_market_regime)


# Async test utilities
@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
