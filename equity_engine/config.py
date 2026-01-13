import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

DEFAULT_INDEXES = ["NIFTY 200"]
DEFAULT_WEIGHTS = {"fundamental": 0.40, "technical": 0.25, "sentiment": 0.15, "macro": 0.10, "risk": 0.10}

@dataclass(frozen=True)
class Settings:
    indexes: List[str]
    yahoo_suffix: str
    weights: Dict[str, float]
    history_years: int
    use_finbert: bool
    use_llm: bool
    rf_annual_pct: float
    return_windows: List[int]
    sma_windows: List[int]
    rsi_window: int
    macd: Tuple[int, int, int]
    max_workers: int
    # Weekly/Monthly analysis settings
    weekly_history_weeks: int = 52
    monthly_history_months: int = 24
    seasonality_years: int = 5

def _parse_int_list(s: str, default: List[int]) -> List[int]:
    if not s: return default
    return [int(x.strip()) for x in s.split(",") if x.strip()]

def _parse_int_tuple(s: str, default: Tuple[int, ...]) -> Tuple[int, ...]:
    if not s: return default
    return tuple(int(x.strip()) for x in s.split(",") if x.strip())

def _parse_indexes(s: str) -> List[str]:
    if not s: return DEFAULT_INDEXES
    return [x.strip() for x in s.split(",") if x.strip()]

def _parse_weights(s: str) -> Dict[str, float]:
    if not s: return DEFAULT_WEIGHTS
    try:
        w = json.loads(s)
        return w
    except Exception:
        parts = [p.strip() for p in s.split(";") if p.strip()]
        out = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                out[k.strip()] = float(v)
        return out or DEFAULT_WEIGHTS

def load_settings() -> Settings:
    indexes = _parse_indexes(os.getenv("STOCK_INDEXES", ",".join(DEFAULT_INDEXES)))
    yahoo_suffix = os.getenv("YAHOO_SUFFIX", ".NS")
    weights = _parse_weights(os.getenv("WEIGHTS_JSON", ""))
    total = sum(weights.values()) or 1.0
    weights = {k: v / total for k, v in weights.items()}
    years = int(os.getenv("HISTORY_YEARS", "5"))
    use_finbert = os.getenv("USE_FINBERT", "0") in ("1", "true", "True")
    use_llm = os.getenv("USE_LLM", "0") in ("1", "true", "True")

    # Processing parameters
    rf_annual_pct = float(os.getenv("RF_ANNUAL_PCT", "7.0"))
    return_windows = _parse_int_list(os.getenv("RETURN_WINDOWS", "1,5,21,63,126,252"), [1, 5, 21, 63, 126, 252])
    sma_windows = _parse_int_list(os.getenv("SMA_WINDOWS", "20,50,200"), [20, 50, 200])
    rsi_window = int(os.getenv("RSI_WINDOW", "14"))
    macd = _parse_int_tuple(os.getenv("MACD_PARAMS", "12,26,9"), (12, 26, 9))
    max_workers = int(os.getenv("MAX_WORKERS", "10"))
    
    # Weekly/Monthly analysis parameters
    weekly_history_weeks = int(os.getenv("WEEKLY_HISTORY_WEEKS", "52"))
    monthly_history_months = int(os.getenv("MONTHLY_HISTORY_MONTHS", "24"))
    seasonality_years = int(os.getenv("SEASONALITY_YEARS", "5"))

    return Settings(
        indexes=indexes, yahoo_suffix=yahoo_suffix, weights=weights, history_years=years,
        use_finbert=use_finbert, use_llm=use_llm, rf_annual_pct=rf_annual_pct,
        return_windows=return_windows, sma_windows=sma_windows, rsi_window=rsi_window,
        macd=macd, max_workers=max_workers,
        weekly_history_weeks=weekly_history_weeks, monthly_history_months=monthly_history_months,
        seasonality_years=seasonality_years
    )