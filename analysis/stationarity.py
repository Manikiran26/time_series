"""
Stationarity Analysis & Differencing Module for Electricity Time Series.
Performs real Augmented Dickey-Fuller (ADF) and Kwiatkowski-Phillips-Schmidt-Shin (KPSS) tests.
Includes first-order and seasonal differencing with pre/post statistical validation.
"""

import pandas as pd
import numpy as np
import warnings
from statsmodels.tsa.stattools import adfuller, kpss
import plotly.graph_objects as go
from typing import Dict, Any, Tuple, Optional
from analysis.eda import CHART_THEME


def perform_adf_test(series: pd.Series, maxlag: Optional[int] = None) -> Dict[str, Any]:
    """
    Augmented Dickey-Fuller (ADF) Test:
    H0 (Null Hypothesis): The series has a unit root (NON-STATIONARY).
    H1 (Alternative Hypothesis): The series has no unit root (STATIONARY).
    """
    clean_series = series.dropna()
    res = adfuller(clean_series, maxlag=maxlag, autolag='AIC')

    test_stat = float(res[0])
    p_value = float(res[1])
    used_lag = int(res[2])
    nobs = int(res[3])
    crit_vals = {k: float(v) for k, v in res[4].items()}

    # Check 5% alpha threshold
    is_stationary = p_value < 0.05

    interpretation = (
        "Reject H₀: The time series is STATIONARY (p < 0.05). No unit root detected."
        if is_stationary
        else "Fail to reject H₀: The time series is NON-STATIONARY (p ≥ 0.05). Unit root present."
    )

    return {
        'test_name': 'Augmented Dickey-Fuller (ADF)',
        'null_hypothesis': 'Series possesses a unit root (Non-Stationary)',
        'alt_hypothesis': 'Series has no unit root (Stationary)',
        'test_statistic': test_stat,
        'p_value': p_value,
        'used_lag': used_lag,
        'nobs': nobs,
        'critical_values': crit_vals,
        'is_stationary': is_stationary,
        'conclusion': 'Stationary' if is_stationary else 'Non-Stationary',
        'interpretation': interpretation
    }


def perform_kpss_test(series: pd.Series, regression: str = 'c') -> Dict[str, Any]:
    """
    Kwiatkowski-Phillips-Schmidt-Shin (KPSS) Test:
    H0 (Null Hypothesis): The series is level/trend STATIONARY.
    H1 (Alternative Hypothesis): The series has a unit root (NON-STATIONARY).
    Note inverse hypothesis compared to ADF!
    """
    clean_series = series.dropna()

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        try:
            res = kpss(clean_series, regression=regression, nlags="auto")
            test_stat = float(res[0])
            p_value = float(res[1])
            lags = int(res[2])
            crit_vals = {k: float(v) for k, v in res[3].items()}
        except Exception:
            # Fallback if nlags fails
            res = kpss(clean_series, regression=regression, nlags=10)
            test_stat = float(res[0])
            p_value = float(res[1])
            lags = 10
            crit_vals = {k: float(v) for k, v in res[3].items()}

    # For KPSS, p < 0.05 rejects H0 (meaning Non-Stationary)
    is_stationary = p_value >= 0.05

    interpretation = (
        "Fail to reject H₀: The time series is STATIONARY around level/trend (p ≥ 0.05)."
        if is_stationary
        else "Reject H₀: The time series is NON-STATIONARY (p < 0.05). Unit root present."
    )

    return {
        'test_name': 'Kwiatkowski-Phillips-Schmidt-Shin (KPSS)',
        'null_hypothesis': 'Series is level/trend stationary',
        'alt_hypothesis': 'Series possesses a unit root (Non-Stationary)',
        'test_statistic': test_stat,
        'p_value': p_value,
        'lags_used': lags,
        'critical_values': crit_vals,
        'is_stationary': is_stationary,
        'conclusion': 'Stationary' if is_stationary else 'Non-Stationary',
        'interpretation': interpretation
    }


def evaluate_joint_stationarity(adf_res: Dict[str, Any], kpss_res: Dict[str, Any]) -> Dict[str, str]:
    """
    Evaluate combined diagnostic matrix of ADF and KPSS:
    - Case 1: Both indicate stationary -> Strictly Stationary.
    - Case 2: Both indicate non-stationary -> Strictly Non-Stationary (Differencing required).
    - Case 3: ADF stationary, KPSS non-stationary -> Difference Stationary (weak seasonality or structural shift).
    - Case 4: ADF non-stationary, KPSS stationary -> Trend Stationary (detrending needed).
    """
    adf_stat = adf_res['is_stationary']
    kpss_stat = kpss_res['is_stationary']

    if adf_stat and kpss_stat:
        status = "Stationary"
        action = "No differencing required (d = 0)."
        badge_color = "#10b981"  # Emerald
        explanation = "Both ADF and KPSS tests agree that the electricity consumption series is stationary."
    elif (not adf_stat) and (not kpss_stat):
        status = "Non-Stationary"
        action = "Differencing recommended (d = 1 or D = 1)."
        badge_color = "#ef4444"  # Red
        explanation = "Both ADF and KPSS tests agree that the electricity consumption series contains a unit root."
    elif adf_stat and (not kpss_stat):
        status = "Difference Stationary"
        action = "First differencing or seasonal differencing recommended."
        badge_color = "#f59e0b"  # Amber
        explanation = "ADF indicates stationarity, but KPSS detects a unit root. Differencing is advisable to stabilize variance/mean."
    else:
        status = "Trend Stationary"
        action = "Detrending or differencing recommended."
        badge_color = "#38bdf8"  # Cyan
        explanation = "KPSS indicates stationarity around a deterministic trend, while ADF detects unit root. Removing the trend will yield a stationary series."

    return {
        'status': status,
        'action': action,
        'badge_color': badge_color,
        'explanation': explanation
    }


def apply_differencing(
    series: pd.Series,
    order: int = 1,
    seasonal_lag: Optional[int] = None
) -> Tuple[pd.Series, str]:
    """
    Apply regular and/or seasonal differencing to series:
    - order: 1 (first difference: y_t - y_{t-1}), 2 (second difference)
    - seasonal_lag: e.g. 7 for daily weekly season, 24 for hourly daily season.
    """
    clean_series = series.dropna()

    if seasonal_lag is not None and seasonal_lag > 1:
        # Seasonal difference
        diff_series = clean_series.diff(seasonal_lag)
        desc = f"Seasonal Differencing (Lag = {seasonal_lag})"
        if order >= 1:
            diff_series = diff_series.diff(order)
            desc = f"First Differencing (d={order}) + Seasonal Differencing (Lag={seasonal_lag})"
    else:
        diff_series = clean_series
        for _ in range(order):
            diff_series = diff_series.diff()
        desc = f"First-Order Differencing (d={order})"

    diff_series = diff_series.dropna()
    return diff_series, desc


def plot_differencing_comparison(
    original_series: pd.Series,
    differenced_series: pd.Series,
    diff_desc: str
) -> go.Figure:
    """
    Plot side-by-side or stacked view of Original vs Differenced Series.
    """
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            "<b>Original Electricity Consumption Series</b>",
            f"<b>Differenced Series [{diff_desc}]</b>"
        )
    )

    fig.add_trace(go.Scatter(
        x=original_series.index,
        y=original_series,
        mode='lines',
        name='Original',
        line=dict(color=CHART_THEME['primary_color'], width=1.5),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Value:</b> %{y:.3f} kW<extra></extra>'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=differenced_series.index,
        y=differenced_series,
        mode='lines',
        name='Differenced',
        line=dict(color=CHART_THEME['accent_color'], width=1.3),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Diff:</b> %{y:.3f}<extra></extra>'
    ), row=2, col=1)

    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)", row=2, col=1)

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
    fig.update_xaxes(gridcolor=CHART_THEME['grid_color'], title="Date", row=2, col=1)
    fig.update_yaxes(gridcolor=CHART_THEME['grid_color'], title="kW", row=1, col=1)
    fig.update_yaxes(gridcolor=CHART_THEME['grid_color'], title="Δ kW", row=2, col=1)

    return fig
