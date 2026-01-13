import pytest
import pandas as pd
import numpy as np
from datetime import date
from unittest.mock import MagicMock, patch
from pipeline.daily_to_supabase import prepare_daily_payload, upload_to_supabase

def test_prepare_daily_payload():
    # Mock a dataframe with required columns
    df = pd.DataFrame([{
        "symbol": "RELIANCE",
        "Company Name": "Reliance Industries",
        "Price": 1500.0,
        "52W High": 1600.0,
        "52W Low": 1400.0,
        "Score Fundamental (0-100)": 75.5,
        "Overall Score": 82.0,
        "RSI": 65.0,
        "Sector": "Energy"
    }])
    
    payload = prepare_daily_payload(df, date(2026, 1, 11))
    
    assert len(payload) == 1
    item = payload[0]
    assert item["ticker"] == "RELIANCE"
    assert item["date"] == "2026-01-11"
    assert item["price_last"] == 1500.0
    assert item["overall_score"] == 82.0
    assert item["sector"] == "Energy"

def test_prepare_daily_payload_handles_nan():
    df = pd.DataFrame([{
        "symbol": "TCS",
        "Price": np.nan,
        "Overall Score": 80.0
    }])
    
    payload = prepare_daily_payload(df, date(2026, 1, 11))
    assert payload[0]["price_last"] is None
    assert payload[0]["overall_score"] == 80.0

@patch("pipeline.daily_to_supabase.get_supabase_client")
def test_upload_to_supabase(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    payload = [{"ticker": "RELIANCE", "date": "2026-01-11", "price_last": 1500.0}]
    
    upload_to_supabase(payload)
    
    mock_client.table.assert_called_with("daily_stocks")
    mock_client.table().upsert.assert_called_with(payload)
