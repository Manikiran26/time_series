"""
Autocorrelation (ACF) and Partial Autocorrelation (PACF) Module.
Calculates autocorrelation, confidence bounds, lag significance, and generates
publication-quality interactive stem plots with parameter recommendations for Part 2 ARIMA/SARIMA.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.stattools import acf, pacf
from typing import Dict, Any, Tuple, Optional, List
from analysis.eda import CHART_THEME


def calculate_acf_pacf(
    series: pd.Series,
    nlags: int = 40,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Calculate ACF and PACF values along with 95% confidence intervals.
    """
    clean_series = series.dropna()
    n = len(clean_series)

    # Ensure nlags doesn't exceed 50% of series length
    effective_lags = min(nlags, int(n / 2) - 1)

    acf_vals, acf_confint = acf(clean_series, nlags=effective_lags, alpha=alpha)
    pacf_vals, pacf_confint = pacf(clean_series, nlags=effective_lags, alpha=alpha, method='ywm')

    # Bartlett 95% confidence threshold: +- 1.96 / sqrt(N)
    crit_bound = 1.96 / np.sqrt(n)

    lags = list(range(effective_lags + 1))

    # Identify significant lags (excluding lag 0)
    sig_acf_lags = [i for i in range(1, len(acf_vals)) if abs(acf_vals[i]) > crit_bound]
    sig_pacf_lags = [i for i in range(1, len(pacf_vals)) if abs(pacf_vals[i]) > crit_bound]

    # Suggest potential p and q for Part 2 ARIMA
    # Cutoff in PACF indicates p; Cutoff in ACF indicates q
    suggested_p = sig_pacf_lags[0] if len(sig_pacf_lags) > 0 and sig_pacf_lags[0] <= 5 else 1
    suggested_q = sig_acf_lags[0] if len(sig_acf_lags) > 0 and sig_acf_lags[0] <= 5 else 1

    return {
        'lags': lags,
        'acf': acf_vals,
        'pacf': pacf_vals,
        'acf_confint': acf_confint,
        'pacf_confint': pacf_confint,
        'crit_bound': float(crit_bound),
        'nobs': n,
        'effective_lags': effective_lags,
        'sig_acf_lags': sig_acf_lags,
        'sig_pacf_lags': sig_pacf_lags,
        'suggested_p': suggested_p,
        'suggested_q': suggested_q
    }


def plot_acf_pacf(acf_pacf_data: Dict[str, Any], title_prefix: str = "") -> go.Figure:
    """
    Generate clean, interactive dual stem-plot for ACF and PACF with 95% confidence bounds.
    """
    lags = acf_pacf_data['lags']
    acf_vals = acf_pacf_data['acf']
    pacf_vals = acf_pacf_data['pacf']
    bound = acf_pacf_data['crit_bound']

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(
            f"<b>{title_prefix} Autocorrelation Function (ACF) — Guides MA(q) Selection</b>",
            f"<b>{title_prefix} Partial Autocorrelation Function (PACF) — Guides AR(p) Selection</b>"
        )
    )

    # 1. Shaded 95% Confidence Bounds (ACF)
    fig.add_trace(go.Scatter(
        x=[lags[0], lags[-1]], y=[bound, bound],
        mode='lines', line=dict(color='rgba(245, 158, 11, 0.5)', dash='dash', width=1.2),
        name='+95% Confidence Band', showlegend=False, hoverinfo='skip'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[lags[0], lags[-1]], y=[-bound, -bound],
        mode='lines', line=dict(color='rgba(245, 158, 11, 0.5)', dash='dash', width=1.2),
        fill='tonexty', fillcolor='rgba(245, 158, 11, 0.08)',
        name='-95% Confidence Band', showlegend=False, hoverinfo='skip'
    ), row=1, col=1)

    # 2. Shaded 95% Confidence Bounds (PACF)
    fig.add_trace(go.Scatter(
        x=[lags[0], lags[-1]], y=[bound, bound],
        mode='lines', line=dict(color='rgba(245, 158, 11, 0.5)', dash='dash', width=1.2),
        showlegend=False, hoverinfo='skip'
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=[lags[0], lags[-1]], y=[-bound, -bound],
        mode='lines', line=dict(color='rgba(245, 158, 11, 0.5)', dash='dash', width=1.2),
        fill='tonexty', fillcolor='rgba(245, 158, 11, 0.08)',
        showlegend=False, hoverinfo='skip'
    ), row=2, col=1)

    # 3. ACF Stems (vertical lines)
    for lag, val in zip(lags, acf_vals):
        fig.add_shape(
            type="line",
            x0=lag, y0=0, x1=lag, y1=val,
            line=dict(color=CHART_THEME['primary_color'], width=1.8),
            row=1, col=1
        )

    # ACF Markers
    fig.add_trace(go.Scatter(
        x=lags, y=acf_vals,
        mode='markers',
        marker=dict(size=6, color=CHART_THEME['primary_color']),
        name='ACF',
        hovertemplate='<b>Lag:</b> %{x}<br><b>ACF:</b> %{y:.3f}<extra></extra>'
    ), row=1, col=1)

    # 4. PACF Stems (vertical lines)
    for lag, val in zip(lags, pacf_vals):
        fig.add_shape(
            type="line",
            x0=lag, y0=0, x1=lag, y1=val,
            line=dict(color=CHART_THEME['accent_color'], width=1.8),
            row=2, col=1
        )

    # PACF Markers
    fig.add_trace(go.Scatter(
        x=lags, y=pacf_vals,
        mode='markers',
        marker=dict(size=6, color=CHART_THEME['accent_color']),
        name='PACF',
        hovertemplate='<b>Lag:</b> %{x}<br><b>PACF:</b> %{y:.3f}<extra></extra>'
    ), row=2, col=1)

    # Zero lines
    fig.add_hline(y=0, line_color="rgba(255,255,255,0.4)", row=1, col=1)
    fig.add_hline(y=0, line_color="rgba(255,255,255,0.4)", row=2, col=1)

    fig.update_layout(
        height=580,
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor=CHART_THEME['bg_color'],
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        showlegend=False
    )

    fig.update_xaxes(gridcolor=CHART_THEME['grid_color'], row=1, col=1)
    fig.update_xaxes(gridcolor=CHART_THEME['grid_color'], title="Lag", row=2, col=1)
    fig.update_yaxes(gridcolor=CHART_THEME['grid_color'], title="Autocorrelation", range=[-1.05, 1.05], row=1, col=1)
    fig.update_yaxes(gridcolor=CHART_THEME['grid_color'], title="Partial Autocorr.", range=[-1.05, 1.05], row=2, col=1)

    return fig
