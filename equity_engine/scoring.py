from typing import Dict, List
import numpy as np
import pandas as pd

def _rank_0_100(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    s = series.astype(float).replace([np.inf, -np.inf], np.nan)
    if s.dropna().empty:
        return pd.Series(np.nan, index=s.index)
    ranks = s.rank(pct=True, method="average")
    if not higher_is_better:
        ranks = 1.0 - ranks
    return (ranks * 100.0).astype(float)

def compute_subscores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-stock subscores on [0,100] for categories:
    - Fundamental, Technical, Sentiment, Macro, Risk.
    Uses available columns. Missing metrics are ignored for each composite.
    """
    out = pd.DataFrame(index=df.index)

    # Fundamental metrics: higher is better
    pos = {
        "ROE TTM %": True, "ROA %": True, "Net Profit Margin %": True, "Gross Profit Margin %": True,
        "Operating Profit Margin %": True, "EPS Growth YoY %": True, "Revenue Growth YoY %": True,
        "Dividend Yield %": True, "FCF Yield %": True, "Interest Coverage": True
    }
    # lower is better
    neg = {
        "P/E (TTM)": False, "P/B": False, "P/S Ratio": False, "Debt/Equity": False, "PEG Ratio": False
    }
    # Build composite
    parts = []
    for col, hib in {**pos, **neg}.items():
        if col in df.columns:
            parts.append(_rank_0_100(df[col], higher_is_better=hib).rename(col))
    if parts:
        F = pd.concat(parts, axis=1)
        out["Score Fundamental (0-100)"] = F.mean(axis=1, skipna=True)
    else:
        out["Score Fundamental (0-100)"] = np.nan

    # Technical: returns momentum + trend + vol breakouts
    tech_parts = []
    for col in ["Return 21d %","Return 63d %","Return 126d %","Return 252d %"]:
        if col in df.columns: tech_parts.append(_rank_0_100(df[col], True).rename(col))
    # price above moving averages (binary boosts)
    if "Price (Last)" in df.columns:
        if "SMA50" in df.columns:
            tech_parts.append(((df["Price (Last)"]>df["SMA50"]).astype(int)*100).rename("Above SMA50"))
        if "SMA200" in df.columns:
            tech_parts.append(((df["Price (Last)"]>df["SMA200"]).astype(int)*100).rename("Above SMA200"))
    if "ADX14" in df.columns:
        tech_parts.append(_rank_0_100(df["ADX14"], True).rename("ADX14"))
    if tech_parts:
        T = pd.concat(tech_parts, axis=1)
        out["Score Technical (0-100)"] = T.mean(axis=1, skipna=True)
    else:
        out["Score Technical (0-100)"] = np.nan

    # Sentiment: map to 0-100
    sent_parts = []
    if "News Sentiment Score" in df.columns:
        sent_parts.append(((df["News Sentiment Score"]+1.0)/2.0*100.0).clip(0,100).rename("News Sentiment"))
    if "Social Media Sentiment" in df.columns:
        sent_parts.append(((df["Social Media Sentiment"]+1.0)/2.0*100.0).clip(0,100).rename("Social Sentiment"))
    if "Consensus Rating (1-5)" in df.columns:
        # 1=Strong Buy, 5=Strong Sell -> map to 0-100 with 1->100, 5->0
        cr = df["Consensus Rating (1-5)"].astype(float)
        sent_parts.append(((5.0 - cr)/4.0*100.0).clip(0,100).rename("Analyst Consensus"))
    if sent_parts:
        S = pd.concat(sent_parts, axis=1)
        out["Score Sentiment (0-100)"] = S.mean(axis=1, skipna=True)
    else:
        out["Score Sentiment (0-100)"] = np.nan

    # Macro: a single scalar applied to all; expect a column 'Macro Composite (0-100)' merged into df
    if "Macro Composite (0-100)" in df.columns:
        out["Score Macro (0-100)"] = df["Macro Composite (0-100)"].astype(float).clip(0,100)
    else:
        out["Score Macro (0-100)"] = 50.0  # neutral if unknown

    # Risk: lower vol & drawdown & D/E is better; higher Sharpe better
    risk_parts = []
    for col in ["Volatility 90D %","Volatility 30D %","Max Drawdown 1Y %","Debt/Equity"]:
        if col in df.columns:
            risk_parts.append(_rank_0_100(df[col], higher_is_better=False).rename(col))
    if "Sharpe 1Y" in df.columns:
        risk_parts.append(_rank_0_100(df["Sharpe 1Y"], True).rename("Sharpe 1Y"))
    if "Interest Coverage" in df.columns:
        risk_parts.append(_rank_0_100(df["Interest Coverage"], True).rename("Interest Coverage"))
    if risk_parts:
        R = pd.concat(risk_parts, axis=1)
        out["Score Risk (0-100)"] = R.mean(axis=1, skipna=True)
    else:
        out["Score Risk (0-100)"] = np.nan

    return out

def overall_score(subscores: pd.DataFrame, weights: Dict[str, float]) -> pd.Series:
    wF = weights.get("fundamental", 0.4)
    wT = weights.get("technical", 0.25)
    wS = weights.get("sentiment", 0.15)
    wM = weights.get("macro", 0.10)
    wR = weights.get("risk", 0.10)
    components = [
        ("Score Fundamental (0-100)", wF),
        ("Score Technical (0-100)", wT),
        ("Score Sentiment (0-100)", wS),
        ("Score Macro (0-100)", wM),
        ("Score Risk (0-100)", wR),
    ]

    numer = pd.Series(0.0, index=subscores.index)
    denom = pd.Series(0.0, index=subscores.index)

    for col, weight in components:
        if weight <= 0:
            continue
        series = subscores.get(col)
        if series is None:
            continue
        series = series.astype(float)
        valid = series.notna()
        if valid.any():
            numer = numer.add(series.fillna(0.0) * weight, fill_value=0.0)
            denom = denom.add(valid.astype(float) * weight, fill_value=0.0)

    denom = denom.replace(0, np.nan)
    score = numer / denom
    return score
