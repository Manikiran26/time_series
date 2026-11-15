"""
Time Series Decomposition Module using STL (Seasonal-Trend decomposition using LOESS).
Decomposes electricity consumption into Observed, Trend, Seasonal, and Residual components.
Calculates statistical strength of trend and seasonality for academic reporting.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import STL, seasonal_decompose
from typing import Dict, Any, Tuple, Optional
from analysis.eda import CHART_THEME


def perform_stl_decomposition(
    series: pd.Series,
    period: Optional[int] = None,
    seasonal_window: int = 7,
    robust: bool = True
) -> Dict[str, Any]:
    """
    Perform STL decomposition on time series.
    Auto-detects default period if not provided:
    - Daily: period = 7 (weekly cycle) or 365 (annual cycle)
    - Hourly: period = 24 (daily cycle)
    - Weekly: period = 52
    """
    clean_series = series.dropna()

    if period is None:
        # Infer frequency
        inferred_freq = pd.infer_freq(clean_series.index)
        if inferred_freq:
            if 'h' in inferred_freq.lower():
                period = 24
            elif 'd' in inferred_freq.lower():
                period = 7
            elif 'w' in inferred_freq.lower():
                period = 52
            elif 'm' in inferred_freq.lower():
                period = 12
            else:
                period = 7
        else:
            # Fallback based on typical index difference
            delta = (clean_series.index[1] - clean_series.index[0]).total_seconds()
            if delta <= 3600:
                period = 24
            elif delta <= 86400:
                period = 7
            else:
                period = 12

    # Fit STL
    stl = STL(clean_series, period=period, seasonal=seasonal_window, robust=robust)
    res = stl.fit()

    observed = clean_series
    trend = res.trend
    seasonal = res.seasonal
    resid = res.resid

    # Compute variance and strength of components (Hyndman & Athanasopoulos, Forecasting: Principles and Practice)
    var_resid = np.var(resid)
    var_trend_resid = np.var(trend + resid)
    var_season_resid = np.var(seasonal + resid)
    var_total = np.var(observed)

    trend_strength = max(0.0, 1.0 - (var_resid / var_trend_resid)) if var_trend_resid > 0 else 0.0
    seasonal_strength = max(0.0, 1.0 - (var_resid / var_season_resid)) if var_season_resid > 0 else 0.0

    # Variance contribution proportions
    trend_var_pct = (np.var(trend) / var_total) * 100 if var_total > 0 else 0
    seasonal_var_pct = (np.var(seasonal) / var_total) * 100 if var_total > 0 else 0
    resid_var_pct = (var_resid / var_total) * 100 if var_total > 0 else 0

    components_df = pd.DataFrame({
        'Observed': observed,
        'Trend': trend,
        'Seasonal': seasonal,
        'Residual': resid
    }, index=clean_series.index)

    return {
        'components': components_df,
        'period': period,
        'seasonal_window': seasonal_window,
        'robust': robust,
        'trend_strength': float(trend_strength),
        'seasonal_strength': float(seasonal_strength),
        'trend_var_pct': float(trend_var_pct),
        'seasonal_var_pct': float(seasonal_var_pct),
        'resid_var_pct': float(resid_var_pct),
        'residual_mean': float(resid.mean()),
        'residual_std': float(resid.std())
    }


def plot_stl_decomposition(decomp_result: Dict[str, Any]) -> go.Figure:
    """
    Generate clear 4-panel interactive subplot of STL Decomposition:
    1. Observed
    2. Trend
    3. Seasonal
    4. Residual
    """
    df = decomp_result['components']
    period = decomp_result['period']

    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        subplot_titles=(
            "<b>1. Observed Series (Raw Data)</b>",
            f"<b>2. Trend Component (Long-Term Movement) — Strength: {decomp_result['trend_strength']:.2f}</b>",
            f"<b>3. Seasonal Component (Cycle Period = {period}) — Strength: {decomp_result['seasonal_strength']:.2f}</b>",
            f"<b>4. Residual / Noise (Irregular Variations) — Std: {decomp_result['residual_std']:.3f}</b>"
        )
    )

    # 1. Observed
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Observed'],
        mode='lines',
        name='Observed',
        line=dict(color=CHART_THEME['primary_color'], width=1.5),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Observed:</b> %{y:.3f} kW<extra></extra>'
    ), row=1, col=1)

    # 2. Trend
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Trend'],
        mode='lines',
        name='Trend',
        line=dict(color=CHART_THEME['secondary_color'], width=2.2),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Trend:</b> %{y:.3f} kW<extra></extra>'
    ), row=2, col=1)

    # 3. Seasonal
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Seasonal'],
        mode='lines',
        name='Seasonal',
        line=dict(color=CHART_THEME['success_color'], width=1.4),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Seasonal:</b> %{y:.3f} kW<extra></extra>'
    ), row=3, col=1)

    # 4. Residual
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Residual'],
        mode='markers',
        name='Residual',
        marker=dict(color=CHART_THEME['accent_color'], size=3, opacity=0.7),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Residual:</b> %{y:.3f}<extra></extra>'
    ), row=4, col=1)

    # Zero line for residual
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)", row=4, col=1)

    # Styling
    fig.update_layout(
        height=780,
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor=CHART_THEME['bg_color'],
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        showlegend=False
    )

    for i in range(1, 5):
        fig.update_xaxes(gridcolor=CHART_THEME['grid_color'], row=i, col=1)
        fig.update_yaxes(gridcolor=CHART_THEME['grid_color'], row=i, col=1)

    fig.update_xaxes(title="Date", row=4, col=1)

    return fig
