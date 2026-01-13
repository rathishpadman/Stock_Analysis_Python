import base64
import io
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
from dash import Dash, Input, Output, State, dash_table, dcc, html
from plotly import express as px
from plotly import graph_objects as go
from plotly.subplots import make_subplots


QUALITY_METRICS: Dict[str, Tuple[float, bool]] = {
    "ROE TTM %": (0.20, True),
    "Debt/Equity": (0.20, False),
    "Piotroski F-Score": (0.30, True),
    "Interest Coverage": (0.15, True),
    "Net Profit Margin %": (0.15, True),
}

VALUE_METRICS: Dict[str, Tuple[float, bool]] = {
    "P/E vs Sector": (0.25, False),
    "P/S Ratio": (0.25, False),
    "FCF Yield %": (0.30, True),
    "PEG Ratio": (0.20, False),
}

GROWTH_METRICS: Dict[str, Tuple[float, bool]] = {
    "Revenue Growth YoY %": (0.35, True),
    "EPS Growth YoY %": (0.35, True),
    "Upside %": (0.30, True),
}

MOMENTUM_METRICS: Dict[str, Tuple[float, bool]] = {
    "Return 6M %": (0.25, True),
    "Return 1Y %": (0.25, True),
    "Price vs SMA200 %": (0.25, True),
    "Sector Relative Strength 6M %": (0.25, True),
}

REQUIRED_COLUMNS: Dict[str, Iterable[str]] = {
    "Ticker": ["Ticker", "symbol"],
    "Company Name": ["Company Name", "longName"],
    "Sector": ["Sector"],
    "Industry": ["Industry"],
    "Market Cap (INR Cr)": ["Market Cap (INR Cr)", "marketCap"],
    "ROE TTM %": ["ROE TTM %"],
    "Debt/Equity": ["Debt/Equity"],
    "Piotroski F-Score": ["Piotroski F-Score"],
    "Interest Coverage": ["Interest Coverage"],
    "Net Profit Margin %": ["Net Profit Margin %"],
    "P/E (TTM)": ["P/E (TTM)"],
    "Sector P/E (Median)": ["Sector P/E (Median)"],
    "P/S Ratio": ["P/S Ratio"],
    "FCF Yield %": ["FCF Yield %"],
    "PEG Ratio": ["PEG Ratio"],
    "Revenue Growth YoY %": ["Revenue Growth YoY %"],
    "EPS Growth YoY %": ["EPS Growth YoY %"],
    "Upside %": ["Upside %"],
    "Return 6M %": ["Return 6M %"],
    "Return 1Y %": ["Return 1Y %"],
    "Price (Last)": ["Price (Last)"],
    "SMA200": ["SMA200"],
    "Sector Relative Strength 6M %": ["Sector Relative Strength 6M %"],
    "P/E vs Sector": [],
    "Price vs SMA200 %": [],
}

APP_THEME = {
    "background": "#0b1a30",
    "card": "#132640",
    "accent": "#1f77b4",
    "text": "#f2f5fa",
    "muted": "#8aa3c1",
}

TAB_STYLE = {
    "padding": "0.75rem 1.25rem",
    "fontWeight": "500",
    "backgroundColor": "#112035",
    "color": APP_THEME["muted"],
    "border": "none",
}

TAB_SELECTED_STYLE = {
    "padding": "0.75rem 1.25rem",
    "fontWeight": "600",
    "backgroundColor": APP_THEME["card"],
    "color": APP_THEME["text"],
    "borderBottom": f"3px solid {APP_THEME['accent']}",
}


def percentile_rank(series: pd.Series, higher_is_better: bool) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    mask = values.notna()
    if mask.sum() <= 1:
        return pd.Series(np.nan, index=series.index)
    ranks = values.rank(pct=True, method="average")
    if not higher_is_better:
        ranks = 1.0 - ranks
    return (ranks * 100.0).astype(float)


def weighted_score(df: pd.DataFrame, metric_spec: Dict[str, Tuple[float, bool]]) -> pd.Series:
    parts: List[pd.Series] = []
    weights: List[float] = []
    for metric, (weight, higher) in metric_spec.items():
        if metric not in df.columns:
            continue
        ranked = percentile_rank(df[metric], higher)
        if ranked.notna().any():
            parts.append(ranked)
            weights.append(weight)
    if not parts:
        return pd.Series(np.nan, index=df.index)
    stacked = pd.concat(parts, axis=1)
    weight_array = np.array(weights)
    weight_array = weight_array / weight_array.sum()
    score = np.average(stacked.fillna(stacked.mean()), axis=1, weights=weight_array)
    return pd.Series(score, index=df.index)


def _first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> Optional[str]:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.copy()
    renamed.columns = [c.strip() for c in renamed.columns]
    for canonical, options in REQUIRED_COLUMNS.items():
        if canonical in renamed.columns:
            continue
        alt = _first_existing_column(renamed, options)
        if alt is not None:
            renamed = renamed.rename(columns={alt: canonical})
    return renamed


def compute_quantcore_scores(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    working = standardise_columns(df)
    missing = [col for col in QUALITY_METRICS.keys() if col not in working.columns]
    for col in ["P/E (TTM)", "Sector P/E (Median)"]:
        if col not in working.columns:
            missing.append(col)
    if "Market Cap (INR Cr)" not in working.columns:
        missing.append("Market Cap (INR Cr)")
    for col in VALUE_METRICS.keys():
        if col not in working.columns and col not in ("P/E vs Sector", "Price vs SMA200 %"):
            missing.append(col)
    for col in GROWTH_METRICS.keys():
        if col not in working.columns:
            missing.append(col)
    for col in MOMENTUM_METRICS.keys():
        if col not in working.columns:
            missing.append(col)
    missing = sorted(set(missing))

    numeric_cols = set(
        list(QUALITY_METRICS.keys())
        + ["P/E (TTM)", "Sector P/E (Median)"]
        + list(VALUE_METRICS.keys())
        + list(GROWTH_METRICS.keys())
        + list(MOMENTUM_METRICS.keys())
        + ["Market Cap (INR Cr)", "Price (Last)", "SMA200"]
    )
    for col in numeric_cols:
        if col in working.columns:
            series = working[col]
            if series.dtype == object:
                cleaned = (
                    series.astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("%", "", regex=False)
                    .str.replace("₹", "", regex=False)
                    .str.replace("INR", "", regex=False)
                )
                working[col] = pd.to_numeric(cleaned, errors="coerce")
            else:
                working[col] = pd.to_numeric(series, errors="coerce")

    if "P/E vs Sector" not in working.columns:
        if {"P/E (TTM)", "Sector P/E (Median)"}.issubset(working.columns):
            sector_pe = working["Sector P/E (Median)"]
            with np.errstate(divide="ignore", invalid="ignore"):
                working["P/E vs Sector"] = np.where(
                    sector_pe > 0,
                    working["P/E (TTM)"] / sector_pe,
                    np.nan,
                )
        else:
            working["P/E vs Sector"] = np.nan

    if "Price vs SMA200 %" not in working.columns:
        if {"Price (Last)", "SMA200"}.issubset(working.columns):
            with np.errstate(divide="ignore", invalid="ignore"):
                working["Price vs SMA200 %"] = np.where(
                    working["SMA200"].abs() > 1e-6,
                    (working["Price (Last)"] - working["SMA200"]) / working["SMA200"] * 100.0,
                    np.nan,
                )
        else:
            working["Price vs SMA200 %"] = np.nan

    working["Quality Score"] = weighted_score(working, QUALITY_METRICS)
    working["Value Score"] = weighted_score(working, VALUE_METRICS)
    working["Growth Score"] = weighted_score(working, GROWTH_METRICS)
    working["Momentum Score"] = weighted_score(working, MOMENTUM_METRICS)

    pillar_cols = ["Quality Score", "Value Score", "Growth Score", "Momentum Score"]
    working["QuantCore N50 Score"] = working[pillar_cols].mean(axis=1, skipna=True)
    working["QuantCore Rank"] = working["QuantCore N50 Score"].rank(ascending=False, method="dense")

    working.sort_values("QuantCore N50 Score", ascending=False, inplace=True)
    working.reset_index(drop=True, inplace=True)
    return working, missing


def load_json_frame(payload: str) -> pd.DataFrame:
    """Safely load a DataFrame that was JSON-serialised via df.to_json(orient="split")."""
    return pd.read_json(io.StringIO(payload), orient="split")


def parse_upload(contents: str, filename: str) -> pd.DataFrame:
    content_type, content_string = contents.split(",", 1)
    decoded = base64.b64decode(content_string)
    if filename.lower().endswith(".csv"):
        return pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    return pd.read_excel(io.BytesIO(decoded))


def format_missing_list(missing: Optional[List[str]]) -> html.Div:
    if not missing:
        return html.Div(
            "All required fields detected.",
            style={"color": APP_THEME["muted"], "padding": "0.5rem 0"},
        )
    items = [html.Li(col) for col in missing]
    return html.Div(
        [
            html.Strong("Missing or empty fields:"),
            html.Ul(items, style={"margin": "0.5rem 0 0 1.5rem"}),
        ],
        style={"color": "#ffb347", "padding": "0.5rem 0"},
    )


def make_top_table(df: pd.DataFrame) -> dash_table.DataTable:
    display_cols = [
        "QuantCore Rank",
        "Ticker",
        "Company Name",
        "Sector",
        "QuantCore N50 Score",
        "Quality Score",
        "Value Score",
        "Growth Score",
        "Momentum Score",
    ]
    available = [col for col in display_cols if col in df.columns]
    if df.empty or not available:
        preview = pd.DataFrame(columns=available)
    else:
        preview = df[available].head(10).copy()
    numeric_cols = [
        "QuantCore N50 Score",
        "Quality Score",
        "Value Score",
        "Growth Score",
        "Momentum Score",
    ]
    for col in numeric_cols:
        if col in preview.columns:
            preview[col] = preview[col].round(1)
    table = dash_table.DataTable(
        data=preview.to_dict("records"),
        columns=[{"name": col, "id": col} for col in preview.columns],
        style_as_list_view=True,
        style_header={"backgroundColor": APP_THEME["card"], "color": APP_THEME["text"], "fontWeight": "bold"},
        style_cell={
            "padding": "6px 8px",
            "backgroundColor": APP_THEME["background"],
            "color": APP_THEME["text"],
            "border": "1px solid #1f2f47",
        },
        style_table={"overflowX": "auto"},
    )
    return table


def apply_filters(
    df: pd.DataFrame,
    sectors: Optional[List[str]],
    tickers: Optional[List[str]],
    pe_range: Optional[List[float]],
) -> pd.DataFrame:
    filtered = df.copy()
    if sectors:
        filtered = filtered[filtered["Sector"].isin(sectors)]
    if tickers:
        filtered = filtered[filtered["Ticker"].isin(tickers)]
    if pe_range is not None and len(pe_range) == 2 and "P/E (TTM)" in filtered.columns:
        lo, hi = pe_range
        filtered = filtered[(filtered["P/E (TTM)"] >= lo) & (filtered["P/E (TTM)"] <= hi)]
    return filtered


def make_valuation_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    figure = px.scatter(
        df,
        x="P/E (TTM)",
        y="ROE TTM %",
        color="QuantCore N50 Score",
        size="Market Cap (INR Cr)" if "Market Cap (INR Cr)" in df.columns else None,
        hover_data=["Ticker", "Company Name", "Sector", "Value Score"],
        labels={"P/E (TTM)": "P/E (TTM)", "ROE TTM %": "ROE TTM %"},
        color_continuous_scale="Viridis",
    )
    figure.update_layout(template="plotly_dark", margin=dict(t=40, r=10, b=40, l=55))
    return figure


def make_fcf_boxplot(df: pd.DataFrame) -> go.Figure:
    if df.empty or "Sector" not in df.columns or "FCF Yield %" not in df.columns:
        return go.Figure()
    figure = px.box(
        df,
        x="Sector",
        y="FCF Yield %",
        color="Sector",
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    figure.update_layout(showlegend=False, template="plotly_dark", margin=dict(t=40, r=10, b=80, l=40))
    return figure


def make_ranking_bar(df: pd.DataFrame, metric: str) -> go.Figure:
    if df.empty or metric not in df.columns:
        return go.Figure()
    ranked = df.sort_values(metric, ascending=False).head(20)
    figure = px.bar(
        ranked,
        x=metric,
        y="Ticker",
        orientation="h",
        color="Sector" if "Sector" in ranked.columns else None,
        hover_data=["Company Name", "QuantCore N50 Score"],
    )
    figure.update_layout(template="plotly_dark", margin=dict(t=40, r=10, b=40, l=120))
    return figure


def make_momentum_gauge(df: pd.DataFrame, focus_ticker: Optional[str]) -> go.Figure:
    if df.empty:
        return go.Figure()
    row = None
    if focus_ticker and focus_ticker in df["Ticker"].values:
        row = df[df["Ticker"] == focus_ticker].iloc[0]
    else:
        row = df.iloc[0]
    fields = [
        ("Return 1D %", "1D Return", 10),
        ("Return 1W %", "1W Return", 15),
        ("Return 6M %", "6M Return", 50),
    ]
    figure = make_subplots(
        rows=1,
        cols=len(fields),
        specs=[[{"type": "indicator"} for _ in fields]],
        subplot_titles=[label for _, label, _ in fields],
    )
    for idx, (column, label, default_span) in enumerate(fields, start=1):
        value = float(row.get(column, np.nan)) if column in row.index else np.nan
        if not np.isfinite(value):
            value = np.nan
        span = max(default_span, abs(value) * 1.5 if np.isfinite(value) else default_span)
        figure.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=value if np.isfinite(value) else 0,
                title={"text": label},
                gauge={
                    "axis": {"range": [-span, span]},
                    "bar": {"color": APP_THEME["accent"]},
                    "bgcolor": "#1b2c44",
                    "steps": [
                        {"range": [-span, -span / 3], "color": "#aa3f3f"},
                        {"range": [-span / 3, span / 3], "color": "#866f32"},
                        {"range": [span / 3, span], "color": "#2d7f4f"},
                    ],
                },
                number={"suffix": "%"},
            ),
            row=1,
            col=idx,
        )
    figure.update_layout(height=320, template="plotly_dark", margin=dict(l=20, r=20, t=40, b=0))
    return figure


def make_ma_gap_chart(df: pd.DataFrame) -> go.Figure:
    required = {"Ticker", "Price vs SMA200 %", "Price (Last)", "SMA20", "SMA50", "SMA200"}
    if df.empty or not required.issubset(df.columns):
        return go.Figure()
    sample = df.head(15).copy()
    for col in ["SMA20", "SMA50", "SMA200"]:
        sample[f"Gap vs {col}"] = np.where(
            sample[col].abs() > 1e-6,
            (sample["Price (Last)"] - sample[col]) / sample[col] * 100.0,
            np.nan,
        )
    melted = sample.melt(
        id_vars=["Ticker"],
        value_vars=["Gap vs SMA20", "Gap vs SMA50", "Gap vs SMA200"],
        var_name="Moving Average",
        value_name="Gap %",
    ).dropna()
    figure = px.bar(
        melted,
        x="Ticker",
        y="Gap %",
        color="Moving Average",
        barmode="group",
    )
    figure.update_layout(template="plotly_dark", margin=dict(t=40, r=10, b=80, l=40))
    return figure


def make_technical_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty or "RSI14" not in df.columns or "MACD Hist" not in df.columns:
        return go.Figure()
    figure = px.scatter(
        df,
        x="RSI14",
        y="MACD Hist",
        size="Volatility 30D %" if "Volatility 30D %" in df.columns else None,
        color="QuantCore N50 Score",
        hover_data=["Ticker", "Momentum Score"],
        color_continuous_scale="Turbo",
    )
    figure.update_layout(template="plotly_dark", margin=dict(t=40, r=10, b=40, l=60))
    return figure


def make_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    numeric_df = df.select_dtypes(include=[np.number]).dropna(axis=1, how="all")
    if numeric_df.shape[1] <= 1:
        return go.Figure()
    corr = numeric_df.corr().round(2)
    corr = corr.iloc[:40, :40]
    figure = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale="RdYlGn",
            zmin=-1,
            zmax=1,
            colorbar={"title": "Corr"},
        )
    )
    figure.update_layout(template="plotly_dark", height=600, margin=dict(t=40, r=40, b=40, l=120))
    return figure


def make_risk_return(df: pd.DataFrame) -> go.Figure:
    required = {"Max Drawdown 1Y %", "Sharpe 1Y"}
    if df.empty or not required.issubset(df.columns):
        return go.Figure()
    figure = px.scatter(
        df,
        x="Max Drawdown 1Y %",
        y="Sharpe 1Y",
        color="Sortino 1Y" if "Sortino 1Y" in df.columns else None,
        size="Volatility 90D %" if "Volatility 90D %" in df.columns else None,
        hover_data=["Ticker", "Sector", "Score Risk (0-100)"] if "Score Risk (0-100)" in df.columns else ["Ticker", "Sector"],
        color_continuous_scale="IceFire",
    )
    figure.update_layout(template="plotly_dark", margin=dict(t=40, r=10, b=40, l=60))
    return figure


def make_sentiment_box(df: pd.DataFrame) -> go.Figure:
    if df.empty or "Sector" not in df.columns or "News Sentiment Score" not in df.columns:
        return go.Figure()
    figure = px.box(
        df,
        x="Sector",
        y="News Sentiment Score",
        color="Sector",
        points="all",
        hover_data=["Ticker", "Return 1W %"] if "Return 1W %" in df.columns else ["Ticker"],
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    figure.update_layout(showlegend=False, template="plotly_dark", margin=dict(t=40, r=10, b=80, l=40))
    return figure


app = Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.H2("QuantCore N50 Interactive Dashboard", style={"color": APP_THEME["text"], "marginTop": "1rem"}),
        html.Div(
            [
                dcc.Upload(
                    id="file-upload",
                    children=html.Div(["Drag and drop or click to upload Excel (.xlsx) or CSV"]),
                    style={
                        "width": "100%",
                        "height": "80px",
                        "lineHeight": "80px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "6px",
                        "textAlign": "center",
                        "marginBottom": "1rem",
                        "color": APP_THEME["muted"],
                    },
                    multiple=False,
                ),
                html.Div(id="upload-status", style={"color": APP_THEME["muted"], "marginBottom": "0.5rem"}),
                html.Div(id="missing-columns"),
            ],
            style={"backgroundColor": APP_THEME["card"], "padding": "1rem", "borderRadius": "8px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Sector Filter", style={"color": APP_THEME["text"]}),
                        dcc.Dropdown(id="sector-filter", multi=True, placeholder="All sectors"),
                    ],
                    style={"flex": "1", "paddingRight": "0.5rem"},
                ),
                html.Div(
                    [
                        html.Label("Ticker Filter", style={"color": APP_THEME["text"]}),
                        dcc.Dropdown(id="ticker-filter", multi=True, placeholder="All tickers"),
                    ],
                    style={"flex": "1", "paddingRight": "0.5rem"},
                ),
                html.Div(
                    [
                        html.Label("P/E (TTM) Range", style={"color": APP_THEME["text"]}),
                        dcc.RangeSlider(id="pe-filter", tooltip={"placement": "bottom", "always_visible": False}),
                    ],
                    style={"flex": "1", "paddingRight": "0.5rem"},
                ),
                html.Div(
                    [
                        html.Label("Ranking Metric", style={"color": APP_THEME["text"]}),
                        dcc.Dropdown(id="ranking-metric"),
                    ],
                    style={"flex": "1", "paddingRight": "0.5rem"},
                ),
                html.Div(
                    [
                        html.Label("Focus Ticker", style={"color": APP_THEME["text"]}),
                        dcc.Dropdown(id="focus-stock", placeholder="Auto"),
                    ],
                    style={"flex": "1"},
                ),
            ],
            style={"display": "flex", "flexWrap": "wrap", "gap": "0.5rem", "margin": "1rem 0"},
        ),
        html.Div(id="top-table-container", style={"marginBottom": "1rem"}),
        dcc.Tabs(
            id="dashboard-tabs",
            value="valuation-tab",
            colors={"border": APP_THEME["card"], "primary": APP_THEME["accent"], "background": APP_THEME["background"]},
            children=[
                dcc.Tab(
                    label="Valuation & Cross-Section",
                    value="valuation-tab",
                    children=[
                        dcc.Graph(id="valuation-scatter"),
                        dcc.Graph(id="fcf-boxplot"),
                        dcc.Graph(id="ranking-bar"),
                    ],
                    style=TAB_STYLE,
                    selected_style=TAB_SELECTED_STYLE,
                ),
                dcc.Tab(
                    label="Momentum & Technicals",
                    value="momentum-tab",
                    children=[
                        dcc.Graph(id="momentum-gauges"),
                        dcc.Graph(id="ma-distance"),
                        dcc.Graph(id="technical-scatter"),
                    ],
                    style=TAB_STYLE,
                    selected_style=TAB_SELECTED_STYLE,
                ),
                dcc.Tab(
                    label="Correlation & Risk",
                    value="correlation-tab",
                    children=[
                        dcc.Graph(id="corr-heatmap"),
                        dcc.Graph(id="risk-return"),
                        dcc.Graph(id="sentiment-box"),
                    ],
                    style=TAB_STYLE,
                    selected_style=TAB_SELECTED_STYLE,
                ),
            ],
        ),
        dcc.Store(id="raw-data"),
        dcc.Store(id="processed-data"),
        dcc.Store(id="missing-store"),
    ],
    style={
        "backgroundColor": APP_THEME["background"],
        "minHeight": "100vh",
        "padding": "1rem 2rem",
        "fontFamily": "Segoe UI, sans-serif",
    },
)


@app.callback(
    Output("upload-status", "children"),
    Output("raw-data", "data"),
    Output("processed-data", "data"),
    Output("missing-store", "data"),
    Input("file-upload", "contents"),
    State("file-upload", "filename"),
)
def handle_file_upload(contents: Optional[str], filename: Optional[str]):
    if contents is None or not filename:
        return "Awaiting upload...", None, None, None
    try:
        df = parse_upload(contents, filename)
    except Exception as exc:  # pragma: no cover - user input path
        return f"Could not read file: {exc}", None, None, None

    processed, missing = compute_quantcore_scores(df)
    status = f"Loaded {filename} with {len(processed)} rows."
    return (
        status,
        df.to_json(orient="split"),
        processed.to_json(orient="split"),
        missing,
    )


@app.callback(Output("missing-columns", "children"), Input("missing-store", "data"))
def update_missing_columns(missing):
    return format_missing_list(missing)


@app.callback(
    Output("sector-filter", "options"),
    Output("sector-filter", "value"),
    Output("ticker-filter", "options"),
    Output("ticker-filter", "value"),
    Output("pe-filter", "min"),
    Output("pe-filter", "max"),
    Output("pe-filter", "value"),
    Output("pe-filter", "marks"),
    Output("ranking-metric", "options"),
    Output("ranking-metric", "value"),
    Output("focus-stock", "options"),
    Output("focus-stock", "value"),
    Input("processed-data", "data"),
)
def populate_filters(processed_json):
    if not processed_json:
        empty: List = []
        return empty, empty, empty, empty, 0, 1, [0, 1], {}, [], None, empty, None
    df = load_json_frame(processed_json)
    sectors = sorted(df["Sector"].dropna().unique()) if "Sector" in df.columns else []
    sector_options = [{"label": s, "value": s} for s in sectors]
    tickers = df["Ticker"].dropna().unique().tolist() if "Ticker" in df.columns else []
    ticker_options = [{"label": t, "value": t} for t in tickers]
    pe_min, pe_max = 0.0, 1.0
    marks: Dict[int, str] = {}
    if "P/E (TTM)" in df.columns and df["P/E (TTM)"].notna().any():
        sample_pe = df["P/E (TTM)"].dropna().astype(float)
        if not sample_pe.empty:
            pe_min = float(np.nanpercentile(sample_pe, 5))
            pe_max = float(np.nanpercentile(sample_pe, 95))
            if pe_min == pe_max:
                pe_max = pe_min + 1.0
            mid = (pe_min + pe_max) / 2.0
            marks = {
                int(pe_min): str(int(pe_min)),
                int(mid): str(int(mid)),
                int(pe_max): str(int(pe_max)),
            }
    ranking_candidates = [
        "QuantCore N50 Score",
        "Quality Score",
        "Value Score",
        "Growth Score",
        "Momentum Score",
        "ROE TTM %",
        "FCF Yield %",
        "Return 1Y %",
    ]
    ranking_options = [
        {"label": metric, "value": metric}
        for metric in ranking_candidates
        if metric in df.columns
    ]
    ranking_value = ranking_options[0]["value"] if ranking_options else None
    focus_options = [{"label": t, "value": t} for t in tickers]
    return (
        sector_options,
        [],
        ticker_options,
        [],
        pe_min,
        pe_max,
        [pe_min, pe_max],
        marks,
        ranking_options,
        ranking_value,
        focus_options,
        None,
    )


@app.callback(
    Output("top-table-container", "children"),
    Output("valuation-scatter", "figure"),
    Output("fcf-boxplot", "figure"),
    Output("ranking-bar", "figure"),
    Output("momentum-gauges", "figure"),
    Output("ma-distance", "figure"),
    Output("technical-scatter", "figure"),
    Output("corr-heatmap", "figure"),
    Output("risk-return", "figure"),
    Output("sentiment-box", "figure"),
    Input("processed-data", "data"),
    Input("sector-filter", "value"),
    Input("ticker-filter", "value"),
    Input("pe-filter", "value"),
    Input("ranking-metric", "value"),
    Input("focus-stock", "value"),
)
def update_visuals(processed_json, sectors, tickers, pe_range, ranking_metric, focus_ticker):
    if not processed_json:
        empty_table = html.Div("Upload data to begin.", style={"color": APP_THEME["muted"]})
        empty_fig = go.Figure()
        return (
            empty_table,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
            empty_fig,
        )
    df = load_json_frame(processed_json)
    filtered = apply_filters(df, sectors, tickers, pe_range)

    table_source = filtered if not filtered.empty else df
    table = make_top_table(table_source)
    valuation_fig = make_valuation_scatter(filtered)
    fcf_fig = make_fcf_boxplot(filtered)
    default_metric = "QuantCore N50 Score" if "QuantCore N50 Score" in filtered.columns else None
    active_metric = ranking_metric or default_metric
    ranking_fig = make_ranking_bar(filtered, active_metric) if active_metric else go.Figure()
    momentum_fig = make_momentum_gauge(filtered, focus_ticker)
    ma_fig = make_ma_gap_chart(filtered)
    tech_fig = make_technical_scatter(filtered)
    corr_fig = make_correlation_heatmap(filtered)
    risk_fig = make_risk_return(filtered)
    sentiment_fig = make_sentiment_box(filtered)

    return (
        html.Div(table),
        valuation_fig,
        fcf_fig,
        ranking_fig,
        momentum_fig,
        ma_fig,
        tech_fig,
        corr_fig,
        risk_fig,
        sentiment_fig,
    )


if __name__ == "__main__":
    app.run(debug=False)
