import pytest
import pandas as pd
from datetime import date
from unittest.mock import MagicMock, patch
from pipeline.weekly_to_supabase import prepare_weekly_payload

def test_prepare_weekly_payload():
    df = pd.DataFrame([{
        "Ticker": "RELIANCE",
        "Company Name": "Reliance Industries",
        "Week Ending": "2026-01-09",
        "Weekly Close": 1475.3,
        "Weekly Return %": -7.35,
        "Weekly Trend": "SIDEWAYS"
    }])
    
    payload = prepare_weekly_payload(df)
    
    assert len(payload) == 1
    item = payload[0]
    assert item["ticker"] == "RELIANCE"
    assert item["week_ending"] == "2026-01-09"
    assert item["weekly_close"] == 1475.3
    assert item["weekly_trend"] == "SIDEWAYS"

def test_prepare_weekly_payload_converts_dates():
    df = pd.DataFrame([{
        "Ticker": "TCS",
        "Week Ending": date(2026, 1, 9),
        "Weekly Close": 3800.0
    }])
    
    payload = prepare_weekly_payload(df)
    assert payload[0]["week_ending"] == "2026-01-09"
