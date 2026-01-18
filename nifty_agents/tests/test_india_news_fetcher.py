"""
Test suite for India News fetcher.

TDD Approach: Tests written BEFORE implementation.
Run with: pytest nifty_agents/tests/test_india_news_fetcher.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestGetStockNews:
    """Tests for get_stock_news function."""
    
    @pytest.fixture
    def mock_rss_feed(self):
        """Mock RSS feed response."""
        mock_feed = MagicMock()
        mock_feed.entries = [
            MagicMock(
                title="Reliance Industries Q3 results: Net profit rises 10%",
                summary="Reliance Industries reported strong Q3 earnings...",
                published="Sat, 18 Jan 2026 10:30:00 GMT",
                link="https://economictimes.com/reliance-q3-results"
            ),
            MagicMock(
                title="Reliance Jio adds 5 million subscribers",
                summary="Jio continues to dominate telecom market...",
                published="Fri, 17 Jan 2026 14:00:00 GMT",
                link="https://economictimes.com/jio-subscribers"
            ),
            MagicMock(
                title="TCS announces dividend",
                summary="TCS board declares interim dividend...",
                published="Fri, 17 Jan 2026 16:00:00 GMT",
                link="https://economictimes.com/tcs-dividend"
            ),
        ]
        return mock_feed
    
    @patch('nifty_agents.tools.india_news_fetcher.feedparser.parse')
    def test_get_news_for_ticker(self, mock_parse, mock_rss_feed):
        """Test fetching news filtered by ticker."""
        from nifty_agents.tools.india_news_fetcher import get_stock_news
        
        mock_parse.return_value = mock_rss_feed
        
        result = get_stock_news("RELIANCE", max_articles=10)
        
        assert result is not None
        assert len(result) >= 1
        # Should only return RELIANCE-related news
        for article in result:
            assert "RELIANCE" in article["title"].upper() or "RELIANCE" in article.get("summary", "").upper() or "RELIANCE" in article.get("ticker_mentioned", "").upper()
    
    @patch('nifty_agents.tools.india_news_fetcher.feedparser.parse')
    def test_get_news_returns_structured_data(self, mock_parse, mock_rss_feed):
        """Test that news is returned in structured format."""
        from nifty_agents.tools.india_news_fetcher import get_stock_news
        
        mock_parse.return_value = mock_rss_feed
        
        result = get_stock_news("RELIANCE", max_articles=5)
        
        if result:  # If any articles found
            article = result[0]
            assert "title" in article
            assert "summary" in article
            assert "published" in article
            assert "link" in article
            assert "source" in article
    
    @patch('nifty_agents.tools.india_news_fetcher.feedparser.parse')
    def test_get_news_handles_no_results(self, mock_parse):
        """Test handling when no news found for ticker."""
        from nifty_agents.tools.india_news_fetcher import get_stock_news
        
        mock_feed = MagicMock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed
        
        result = get_stock_news("OBSCURETICKER", max_articles=10)
        
        assert result == []
    
    @patch('nifty_agents.tools.india_news_fetcher.feedparser.parse')
    def test_get_news_handles_rss_error(self, mock_parse):
        """Test graceful handling of RSS feed errors."""
        from nifty_agents.tools.india_news_fetcher import get_stock_news
        
        mock_parse.side_effect = Exception("RSS feed unavailable")
        
        result = get_stock_news("RELIANCE", max_articles=10)
        
        # Should return empty list, not crash
        assert result == [] or "error" in result


class TestAnalyzeSentiment:
    """Tests for analyze_sentiment function."""
    
    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis for positive news."""
        from nifty_agents.tools.india_news_fetcher import analyze_sentiment
        
        articles = [
            {"title": "Company reports record profits", "summary": "Strong growth in revenue"},
            {"title": "Analyst upgrades stock to buy", "summary": "Positive outlook for Q4"},
        ]
        
        result = analyze_sentiment(articles)
        
        assert result is not None
        assert result["overall_sentiment"] in ["positive", "very_positive", "neutral"]
        assert "sentiment_score" in result
        assert result["sentiment_score"] >= 0
    
    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis for negative news."""
        from nifty_agents.tools.india_news_fetcher import analyze_sentiment
        
        articles = [
            {"title": "Company faces regulatory probe", "summary": "SEBI investigation ongoing"},
            {"title": "Profit falls 20% amid weak demand", "summary": "Revenue decline continues"},
        ]
        
        result = analyze_sentiment(articles)
        
        assert result["overall_sentiment"] in ["negative", "very_negative", "neutral"]
        assert result["sentiment_score"] <= 0.5
    
    def test_analyze_sentiment_empty_articles(self):
        """Test sentiment analysis with no articles."""
        from nifty_agents.tools.india_news_fetcher import analyze_sentiment
        
        result = analyze_sentiment([])
        
        assert result["overall_sentiment"] == "neutral"
        assert result["sentiment_score"] == 0.5
        assert result["article_count"] == 0
    
    def test_sentiment_keywords_detection(self):
        """Test that sentiment keywords are properly detected."""
        from nifty_agents.tools.india_news_fetcher import analyze_sentiment
        
        positive_articles = [
            {"title": "Stock hits all-time high", "summary": "Strong buyback announced"},
        ]
        
        negative_articles = [
            {"title": "Stock crashes amid scandal", "summary": "Fraud allegations surface"},
        ]
        
        pos_result = analyze_sentiment(positive_articles)
        neg_result = analyze_sentiment(negative_articles)
        
        assert pos_result["sentiment_score"] > neg_result["sentiment_score"]


class TestGetCorporateAnnouncements:
    """Tests for get_corporate_announcements function."""
    
    @patch('nifty_agents.tools.india_news_fetcher.get_bse_announcements')
    def test_get_announcements_for_ticker(self, mock_bse):
        """Test fetching corporate announcements."""
        from nifty_agents.tools.india_news_fetcher import get_corporate_announcements
        
        mock_bse.return_value = [
            {
                "headline": "Board Meeting Outcome",
                "date": "2026-01-17",
                "category": "Board Meeting",
            },
            {
                "headline": "Dividend Declaration",
                "date": "2026-01-15",
                "category": "Dividend",
            },
        ]
        
        result = get_corporate_announcements("RELIANCE")
        
        assert result is not None
        assert len(result) >= 1
        assert "headline" in result[0]
        assert "category" in result[0]
    
    @patch('nifty_agents.tools.india_news_fetcher.get_bse_announcements')
    def test_categorizes_announcement_types(self, mock_bse):
        """Test that announcements are categorized by type."""
        from nifty_agents.tools.india_news_fetcher import get_corporate_announcements
        
        mock_bse.return_value = [
            {"headline": "Quarterly Results", "category": "Financial Results"},
            {"headline": "Stock Split 1:2", "category": "Corporate Action"},
        ]
        
        result = get_corporate_announcements("TCS")
        
        categories = [a.get("category") for a in result]
        assert any(cat in ["Financial Results", "Corporate Action", "Board Meeting", "Dividend"] 
                   for cat in categories)
