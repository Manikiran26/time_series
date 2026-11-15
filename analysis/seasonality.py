"""
Seasonality Analysis Module for PowerTrack.
Analyzes Diurnal (Hourly), Weekly (Day of Week), and Monthly seasonal consumption.
Produces user-friendly metrics and interactive Plotly charts.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, Tuple
from analysis.eda import CHART_THEME


def calculate_daily_hourly_pattern(df_hourly: pd.DataFrame) -> Tuple[Dict[str, Any], go.Figure]:
    """
    Compute 24-hour diurnal profile and identify peak and lowest windows.
    """
    df = df_hourly.copy()
    df['Hour'] = df.index.hour

    # Power in kW or energy per hour in kWh (1 kW avg over 1 hr = 1 kWh)
    val_col = 'hourly_kwh' if 'hourly_kwh' in df.columns else ('power_kw' if 'power_kw' in df.columns else 'Global_active_power')
    hourly_avg = df.groupby('Hour')[val_col].mean().reset_index()
    hourly_avg.rename(columns={val_col: 'Global_active_power'}, inplace=True)
    hourly_avg['Hour_Str'] = hourly_avg['Hour'].apply(
        lambda h: f"{12 if h % 12 == 0 else h % 12} {'AM' if h < 12 else 'PM'}"
    )

    peak_row = hourly_avg.loc[hourly_avg['Global_active_power'].idxmax()]
    min_row = hourly_avg.loc[hourly_avg['Global_active_power'].idxmin()]

    peak_hour = int(peak_row['Hour'])
    min_hour = int(min_row['Hour'])

    # Format window strings e.g. "7 PM – 10 PM"
    def format_hour_window(h_center: int) -> str:
        h_start = (h_center - 1) % 24
        h_end = (h_center + 1) % 24
        s_ampm = "AM" if h_start < 12 else "PM"
        e_ampm = "AM" if h_end < 12 else "PM"
        s_12 = 12 if h_start % 12 == 0 else h_start % 12
        e_12 = 12 if h_end % 12 == 0 else h_end % 12
        return f"{s_12} {s_ampm} - {e_12} {e_ampm}"

    peak_window = format_hour_window(peak_hour)
    lowest_window = format_hour_window(min_hour)

    # Interactive area/spline chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hourly_avg['Hour_Str'],
        y=hourly_avg['Global_active_power'],
        mode='lines',
        line=dict(color='#38bdf8', width=3, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(56, 189, 248, 0.12)',
        name='Avg Hourly Consumption',
        hovertemplate='<b>%{x}</b><br>Average: %{y:.2f} kWh/hr<extra></extra>'
    ))

    # Highlight peak point
    fig.add_trace(go.Scatter(
        x=[hourly_avg.loc[hourly_avg['Hour'] == peak_hour, 'Hour_Str'].values[0]],
        y=[peak_row['Global_active_power']],
        mode='markers+text',
        marker=dict(color='#f59e0b', size=10, symbol='diamond'),
        text=[f"Peak: {peak_row['Global_active_power']:.2f} kW"],
        textposition="top center",
        textfont=dict(color='#f59e0b', size=11),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        margin=dict(l=35, r=25, t=30, b=35),
        xaxis=dict(gridcolor=CHART_THEME['grid_color'], tickangle=-45),
        yaxis=dict(title="Avg Power (kW)", gridcolor=CHART_THEME['grid_color'], zeroline=False),
        height=330,
        showlegend=False
    )

    metrics = {
        'peak_hour': peak_hour,
        'peak_window': peak_window,
        'peak_val': float(peak_row['Global_active_power']),
        'lowest_hour': min_hour,
        'lowest_window': lowest_window,
        'lowest_val': float(min_row['Global_active_power']),
        'hourly_data': hourly_avg
    }

    return metrics, fig


def calculate_weekly_pattern(daily_series: pd.Series) -> Tuple[Dict[str, Any], go.Figure]:
    """
    Compute Day-of-Week consumption (Monday through Sunday in kWh/day).
    """
    df = pd.DataFrame({'Daily_kWh': daily_series.values}, index=daily_series.index)
    df['DayOfWeek'] = df.index.dayofweek
    df['DayName'] = df.index.day_name()

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    grouped = df.groupby(['DayOfWeek', 'DayName'])['Daily_kWh'].mean().reset_index()
    grouped.sort_values('DayOfWeek', inplace=True)

    highest_day = grouped.loc[grouped['Daily_kWh'].idxmax(), 'DayName']
    highest_val = float(grouped['Daily_kWh'].max())
    lowest_day = grouped.loc[grouped['Daily_kWh'].idxmin(), 'DayName']
    lowest_val = float(grouped['Daily_kWh'].min())

    weekday_avg = float(df[df['DayOfWeek'] < 5]['Daily_kWh'].mean())
    weekend_avg = float(df[df['DayOfWeek'] >= 5]['Daily_kWh'].mean())
    weekend_diff_pct = ((weekend_avg / weekday_avg) - 1) * 100 if weekday_avg > 0 else 0

    # Colors: subtle cyan for weekdays, vibrant amber/purple for weekend
    colors = ['#38bdf8' if d < 5 else '#818cf8' for d in grouped['DayOfWeek']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['DayName'].apply(lambda x: x[:3]),
        y=grouped['Daily_kWh'],
        marker_color=colors,
        text=[f"{v:.1f}" for v in grouped['Daily_kWh']],
        textposition='outside',
        textfont=dict(color='#cbd5e1', size=11),
        hovertemplate='<b>%{x}</b><br>Average: %{y:.1f} kWh<extra></extra>'
    ))

    # Benchmark line for overall average
    overall_mean = float(df['Daily_kWh'].mean())
    fig.add_hline(
        y=overall_mean,
        line_dash="dash",
        line_color="rgba(245, 158, 11, 0.7)",
        annotation_text=f"Avg: {overall_mean:.1f} kWh",
        annotation_position="top right",
        annotation_font_color="#f59e0b"
    )

    fig.update_layout(
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        margin=dict(l=35, r=25, t=30, b=35),
        xaxis=dict(gridcolor=CHART_THEME['grid_color']),
        yaxis=dict(title="Energy (kWh/day)", gridcolor=CHART_THEME['grid_color'], zeroline=False),
        height=330,
        showlegend=False
    )

    metrics = {
        'highest_day': highest_day,
        'highest_val': highest_val,
        'lowest_day': lowest_day,
        'lowest_val': lowest_val,
        'weekday_avg': weekday_avg,
        'weekend_avg': weekend_avg,
        'weekend_diff_pct': weekend_diff_pct
    }

    return metrics, fig


def calculate_monthly_pattern(daily_series: pd.Series) -> Tuple[Dict[str, Any], go.Figure]:
    """
    Compute monthly seasonal average consumption (kWh/day by month of year).
    """
    df = pd.DataFrame({'Daily_kWh': daily_series.values}, index=daily_series.index)
    df['Month'] = df.index.month
    df['MonthName'] = df.index.strftime('%b')

    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    grouped = df.groupby(['Month', 'MonthName'])['Daily_kWh'].mean().reset_index()
    grouped.sort_values('Month', inplace=True)

    peak_month = grouped.loc[grouped['Daily_kWh'].idxmax(), 'MonthName']
    peak_val = float(grouped['Daily_kWh'].max())
    lowest_month = grouped.loc[grouped['Daily_kWh'].idxmin(), 'MonthName']
    lowest_val = float(grouped['Daily_kWh'].min())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['MonthName'],
        y=grouped['Daily_kWh'],
        marker=dict(
            color=grouped['Daily_kWh'],
            colorscale='Teal',
            showscale=False
        ),
        text=[f"{v:.1f}" for v in grouped['Daily_kWh']],
        textposition='outside',
        textfont=dict(color='#cbd5e1', size=11),
        hovertemplate='<b>%{x}</b><br>Daily Avg: %{y:.1f} kWh<extra></extra>'
    ))

    fig.update_layout(
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        margin=dict(l=35, r=25, t=30, b=35),
        xaxis=dict(categoryorder='array', categoryarray=month_order, gridcolor=CHART_THEME['grid_color']),
        yaxis=dict(title="Daily Avg (kWh)", gridcolor=CHART_THEME['grid_color'], zeroline=False),
        height=330,
        showlegend=False
    )

    metrics = {
        'peak_month': peak_month,
        'peak_val': peak_val,
        'lowest_month': lowest_month,
        'lowest_val': lowest_val
    }

    return metrics, fig
