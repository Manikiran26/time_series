"""
Trend Analysis Module for PowerTrack.
Calculates rolling statistics, overall direction (Increasing, Decreasing, Stable),
and returns formatted trend trajectories for dashboard display.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, Tuple
from analysis.eda import CHART_THEME


def calculate_trend_metrics(daily_series: pd.Series, window: int = 7) -> Dict[str, Any]:
    """
    Calculate rolling average and detect trend direction using linear slope
    and recent vs historical moving average.
    """
    clean = daily_series.dropna()
    rolling_avg = clean.rolling(window=window, min_periods=1).mean()
    rolling_std = clean.rolling(window=window, min_periods=1).std().fillna(0)

    # Calculate trend slope over the series
    if len(clean) > 1:
        x = np.arange(len(clean))
        y = clean.values
        slope, _ = np.polyfit(x, y, 1)
        # Check percentage change of rolling average from start to end of period
        start_val = rolling_avg.iloc[:max(1, len(rolling_avg)//4)].mean()
        end_val = rolling_avg.iloc[-max(1, len(rolling_avg)//4):].mean()
        pct_change = ((end_val - start_val) / start_val) * 100 if start_val > 0 else 0

        if pct_change > 5.0:
            direction = "Increasing"
            direction_badge = "trend-up"
            direction_desc = f"Upward trend (+{pct_change:.1f}%)"
        elif pct_change < -5.0:
            direction = "Decreasing"
            direction_badge = "trend-down"
            direction_desc = f"Downward trend ({pct_change:.1f}%)"
        else:
            direction = "Stable"
            direction_badge = "trend-stable"
            direction_desc = f"Stable consumption (±{abs(pct_change):.1f}%)"
    else:
        direction = "Stable"
        direction_badge = "trend-stable"
        direction_desc = "Stable consumption"
        pct_change = 0.0

    return {
        'rolling_avg': rolling_avg,
        'rolling_std': rolling_std,
        'direction': direction,
        'direction_badge': direction_badge,
        'direction_desc': direction_desc,
        'pct_change': pct_change,
        'current_avg': float(rolling_avg.iloc[-1]) if len(rolling_avg) > 0 else 0.0
    }


def plot_trend_chart(
    daily_series: pd.Series,
    rolling_avg: pd.Series,
    window: int = 7
) -> go.Figure:
    """
    Generate an interactive Plotly chart comparing Actual Daily Consumption (kWh)
    with the Rolling Average.
    """
    fig = go.Figure()

    # Actual consumption line (with slight opacity)
    fig.add_trace(go.Scatter(
        x=daily_series.index,
        y=daily_series.values,
        mode='lines',
        name='Actual Daily',
        line=dict(color='rgba(148, 163, 184, 0.45)', width=1.2),
        hovertemplate='<b>%{x|%b %d, %Y}</b><br>Actual: %{y:.1f} kWh<extra></extra>'
    ))

    # Rolling average line (accent cyan)
    fig.add_trace(go.Scatter(
        x=rolling_avg.index,
        y=rolling_avg.values,
        mode='lines',
        name=f'{window}-Day Rolling Avg',
        line=dict(color='#38bdf8', width=2.8),
        hovertemplate='<b>%{x|%b %d, %Y}</b><br>Rolling Avg: %{y:.1f} kWh<extra></extra>'
    ))

    fig.update_layout(
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        hovermode="x unified",
        margin=dict(l=35, r=25, t=30, b=35),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor=CHART_THEME['grid_color'], showgrid=True),
        yaxis=dict(title="Energy (kWh)", gridcolor=CHART_THEME['grid_color'], zeroline=False),
        height=330
    )

    return fig
