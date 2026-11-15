"""
Rolling Statistics module for Electricity Time Series Analysis.
Calculates and plots rolling mean, rolling standard deviation, and volatility envelopes.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, Tuple
from analysis.eda import CHART_THEME


def calculate_rolling_statistics(
    series: pd.Series,
    window: int = 30,
    min_periods: int = 1
) -> pd.DataFrame:
    """
    Calculate rolling mean, standard deviation, upper and lower volatility bands.
    """
    clean_series = series.dropna()

    rolling_mean = clean_series.rolling(window=window, min_periods=min_periods).mean()
    rolling_std = clean_series.rolling(window=window, min_periods=min_periods).std()

    upper_band = rolling_mean + (2 * rolling_std)
    lower_band = np.maximum(0, rolling_mean - (2 * rolling_std))

    # Rolling coefficient of variation (CV = std / mean)
    cv = (rolling_std / rolling_mean).replace([np.inf, -np.inf], np.nan)

    result_df = pd.DataFrame({
        'Observed': clean_series,
        'Rolling_Mean': rolling_mean,
        'Rolling_Std': rolling_std,
        'Upper_Band': upper_band,
        'Lower_Band': lower_band,
        'Rolling_CV': cv
    }, index=clean_series.index)

    return result_df


def plot_rolling_statistics(
    rolling_df: pd.DataFrame,
    window: int,
    unit: str = "points"
) -> go.Figure:
    """
    Create dual-panel visualization:
    Top panel: Observed series + Rolling Mean + Rolling 2-Sigma Confidence Band.
    Bottom panel: Rolling Standard Deviation (Volatility).
    """
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=(
            f"<b>Observed Series & Rolling Mean (Window = {window} {unit})</b>",
            f"<b>Rolling Standard Deviation (Volatility Metric)</b>"
        )
    )

    # 1. Shaded Bollinger Band
    fig.add_trace(go.Scatter(
        x=rolling_df.index,
        y=rolling_df['Upper_Band'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=rolling_df.index,
        y=rolling_df['Lower_Band'],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(245, 158, 11, 0.12)',
        name='±2 Std Dev Band',
        hoverinfo='skip'
    ), row=1, col=1)

    # 2. Observed series (semi-transparent)
    fig.add_trace(go.Scatter(
        x=rolling_df.index,
        y=rolling_df['Observed'],
        mode='lines',
        line=dict(color='rgba(148, 163, 184, 0.45)', width=1.0),
        name='Original Series',
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Observed:</b> %{y:.3f} kW<extra></extra>'
    ), row=1, col=1)

    # 3. Rolling Mean (bold cyan)
    fig.add_trace(go.Scatter(
        x=rolling_df.index,
        y=rolling_df['Rolling_Mean'],
        mode='lines',
        line=dict(color=CHART_THEME['primary_color'], width=2.5),
        name=f'Rolling Mean ({window})',
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Rolling Mean:</b> %{y:.3f} kW<extra></extra>'
    ), row=1, col=1)

    # 4. Rolling Standard Deviation (amber)
    fig.add_trace(go.Scatter(
        x=rolling_df.index,
        y=rolling_df['Rolling_Std'],
        mode='lines',
        line=dict(color=CHART_THEME['secondary_color'], width=2),
        name=f'Rolling Std ({window})',
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Rolling Std:</b> %{y:.3f}<extra></extra>'
    ), row=2, col=1)

    # Layout styling
    fig.update_layout(
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor=CHART_THEME['bg_color'],
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(gridcolor=CHART_THEME['grid_color'], row=1, col=1)
    fig.update_xaxes(gridcolor=CHART_THEME['grid_color'], title="Date", row=2, col=1)
    fig.update_yaxes(gridcolor=CHART_THEME['grid_color'], title="Active Power (kW)", row=1, col=1)
    fig.update_yaxes(gridcolor=CHART_THEME['grid_color'], title="Std Dev", row=2, col=1)

    return fig
