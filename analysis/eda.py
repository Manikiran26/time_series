"""
Exploratory Data Analysis (EDA) module for Electricity Consumption Time Series.
Generates statistical metrics, hourly/weekly/monthly cyclical profiles,
and publication-quality Plotly interactive visualizations.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, Tuple, Optional


# Consistent modern dark/clean theme styling
CHART_THEME = {
    'bg_color': 'rgba(15, 23, 42, 0.6)',
    'paper_color': 'rgba(0,0,0,0)',
    'grid_color': 'rgba(148, 163, 184, 0.15)',
    'primary_color': '#38bdf8',      # Cyan blue
    'secondary_color': '#f59e0b',    # Amber
    'accent_color': '#ec4899',       # Rose
    'success_color': '#10b981',      # Emerald
    'purple_color': '#a855f7',       # Purple
    'font_family': 'Inter, system-ui, -apple-system, sans-serif',
    'font_color': '#f8fafc'
}


def get_consumption_summary_stats(series: pd.Series) -> Dict[str, float]:
    """Calculate summary statistics for consumption series."""
    s = series.dropna()
    return {
        'count': int(len(s)),
        'mean': float(s.mean()),
        'std': float(s.std()),
        'min': float(s.min()),
        'q25': float(s.quantile(0.25)),
        'median': float(s.median()),
        'q75': float(s.quantile(0.75)),
        'max': float(s.max()),
        'skewness': float(s.skew()),
        'kurtosis': float(s.kurtosis()),
        'iqr': float(s.quantile(0.75) - s.quantile(0.25))
    }


def plot_main_consumption_chart(
    df_slice: pd.DataFrame,
    range_label: str = "Last 30 Days",
    theme: str = "light"
) -> go.Figure:
    """
    Main interactive electricity consumption line chart for PowerTrack.
    Supports hover tooltip, zoom, pan, reset, and smooth responsive styling.
    """
    fig = go.Figure()

    # Determine consumption column (consumption_kwh, Daily_kWh or Global_active_power * 24)
    if 'consumption_kwh' in df_slice.columns:
        y_vals = df_slice['consumption_kwh']
    elif 'Daily_kWh' in df_slice.columns:
        y_vals = df_slice['Daily_kWh']
    else:
        y_vals = df_slice['Global_active_power'] * 24.0

    mean_val = float(y_vals.mean())
    is_light = (theme == 'light')

    line_col = '#0284c7' if is_light else '#38bdf8'
    fill_col = 'rgba(2, 132, 199, 0.08)' if is_light else 'rgba(56, 189, 248, 0.08)'
    font_col = '#0f172a' if is_light else '#f8fafc'
    grid_col = '#f1f5f9' if is_light else 'rgba(148, 163, 184, 0.15)'
    plot_bg = '#ffffff' if is_light else 'rgba(15, 23, 42, 0.5)'
    paper_bg = '#ffffff' if is_light else 'rgba(0,0,0,0)'

    # Filled area under the curve
    fig.add_trace(go.Scatter(
        x=df_slice.index,
        y=y_vals,
        mode='lines',
        name='Daily Consumption',
        line=dict(color=line_col, width=2.5, shape='spline'),
        fill='tozeroy',
        fillcolor=fill_col,
        hovertemplate='<b>Date:</b> %{x|%d %b %Y}<br><b>Consumption:</b> %{y:.1f} kWh<extra></extra>'
    ))

    # Average reference line
    fig.add_hline(
        y=mean_val,
        line_dash="dash",
        line_color="#d97706" if is_light else "#f59e0b",
        annotation_text=f"Average: {mean_val:.1f} kWh",
        annotation_position="top left",
        annotation_font_color="#d97706" if is_light else "#f59e0b",
        annotation_font_size=11
    )

    fig.update_layout(
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(family=CHART_THEME['font_family'], color=font_col),
        hovermode="x unified",
        margin=dict(l=40, r=25, t=25, b=40),
        xaxis=dict(
            gridcolor=grid_col,
            showgrid=True,
            type="date"
        ),
        yaxis=dict(
            title="Consumption (kWh)",
            gridcolor=grid_col,
            zeroline=False,
            showgrid=True
        ),
        height=380,
        showlegend=False
    )

    return fig


def plot_overall_consumption(
    df: pd.DataFrame,
    variable: str = 'Global_active_power',
    title: str = "Electricity Consumption Over Time"
) -> go.Figure:
    """
    Plot interactive time-series with range slider and quick filter buttons
    (Full, 1 Year, 1 Month, 1 Week).
    """
    fig = go.Figure()

    mean_val = df[variable].mean()

    # Main consumption trace
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[variable],
        mode='lines',
        name='Consumption (kW)',
        line=dict(color=CHART_THEME['primary_color'], width=1.8),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d %H:%M}<br><b>Active Power:</b> %{y:.3f} kW<extra></extra>'
    ))

    # Mean line
    fig.add_hline(
        y=mean_val,
        line_dash="dash",
        line_color=CHART_THEME['secondary_color'],
        annotation_text=f"Mean: {mean_val:.2f} kW",
        annotation_position="top left",
        annotation_font_color=CHART_THEME['secondary_color']
    )

    # Date range buttons
    last_date = df.index.max()
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1W", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all", label="Full")
            ]),
            bgcolor="#1e293b",
            activecolor="#0284c7",
            font=dict(color="#f8fafc")
        ),
        rangeslider=dict(visible=True, bgcolor="#1e293b"),
        type="date",
        gridcolor=CHART_THEME['grid_color']
    )

    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=18, color="#f8fafc")),
        yaxis=dict(title="Active Power (kW)", gridcolor=CHART_THEME['grid_color'], zeroline=False),
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor=CHART_THEME['bg_color'],
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def analyze_hourly_pattern(df_hourly: pd.DataFrame, variable: str = 'Global_active_power') -> Tuple[pd.DataFrame, go.Figure]:
    """
    Calculate and visualize average electricity consumption by hour (00:00 to 23:00).
    Identifies peak hours and base load.
    """
    df = df_hourly.copy()
    df['Hour'] = df.index.hour

    grouped = df.groupby('Hour')[variable].agg(['mean', 'std', 'min', 'max', 'median']).reset_index()
    grouped['Hour_Label'] = grouped['Hour'].apply(lambda h: f"{h:02d}:00")

    peak_hour = grouped.loc[grouped['mean'].idxmax(), 'Hour']
    min_hour = grouped.loc[grouped['mean'].idxmin(), 'Hour']

    fig = go.Figure()

    # Confidence interval / standard deviation band
    fig.add_trace(go.Scatter(
        x=grouped['Hour_Label'],
        y=grouped['mean'] + grouped['std'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=grouped['Hour_Label'],
        y=np.maximum(0, grouped['mean'] - grouped['std']),
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(56, 189, 248, 0.15)',
        name='±1 Std Dev Band',
        hoverinfo='skip'
    ))

    # Mean profile line
    fig.add_trace(go.Scatter(
        x=grouped['Hour_Label'],
        y=grouped['mean'],
        mode='lines+markers',
        name='Hourly Mean',
        line=dict(color=CHART_THEME['primary_color'], width=3),
        marker=dict(size=7, color=CHART_THEME['primary_color']),
        hovertemplate='<b>Hour:</b> %{x}<br><b>Avg Consumption:</b> %{y:.3f} kW<extra></extra>'
    ))

    # Highlight peak hour
    peak_val = grouped.loc[grouped['Hour'] == peak_hour, 'mean'].values[0]
    fig.add_trace(go.Scatter(
        x=[f"{peak_hour:02d}:00"],
        y=[peak_val],
        mode='markers+text',
        name=f'Peak Hour ({peak_hour:02d}:00)',
        marker=dict(size=14, color=CHART_THEME['accent_color'], symbol='star'),
        text=[f"Peak: {peak_val:.2f} kW"],
        textposition="top center",
        textfont=dict(color=CHART_THEME['accent_color'], size=12)
    ))

    fig.update_layout(
        title=dict(text="<b>Diurnal (24-Hour) Electricity Consumption Profile</b>", font=dict(size=16, color="#f8fafc")),
        xaxis=dict(title="Hour of Day", gridcolor=CHART_THEME['grid_color'], tickangle=-45),
        yaxis=dict(title="Average Active Power (kW)", gridcolor=CHART_THEME['grid_color']),
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor=CHART_THEME['bg_color'],
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return grouped, fig


def analyze_weekly_pattern(df_daily: pd.DataFrame, variable: str = 'Global_active_power') -> Tuple[pd.DataFrame, go.Figure]:
    """
    Calculate and visualize weekly consumption (Monday -> Sunday).
    Distinguishes weekday vs weekend load.
    """
    df = df_daily.copy()
    df['DayOfWeek'] = df.index.dayofweek
    df['DayName'] = df.index.day_name()

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    grouped = df.groupby(['DayOfWeek', 'DayName'])[variable].agg(['mean', 'std', 'median']).reset_index()
    grouped.sort_values('DayOfWeek', inplace=True)

    weekday_avg = df[df['DayOfWeek'] < 5][variable].mean()
    weekend_avg = df[df['DayOfWeek'] >= 5][variable].mean()

    # Color code: weekdays vs weekend
    colors = [CHART_THEME['primary_color'] if d < 5 else CHART_THEME['secondary_color'] for d in grouped['DayOfWeek']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['DayName'],
        y=grouped['mean'],
        error_y=dict(type='data', array=grouped['std'], visible=True, color='rgba(255,255,255,0.4)'),
        marker_color=colors,
        text=[f"{v:.2f} kW" for v in grouped['mean']],
        textposition='outside',
        hovertemplate='<b>%{x}:</b> %{y:.3f} kW (±%{error_y.array:.2f})<extra></extra>',
        name='Daily Mean'
    ))

    # Benchmark lines
    fig.add_hline(
        y=weekday_avg,
        line_dash="dot",
        line_color=CHART_THEME['primary_color'],
        annotation_text=f"Weekday Avg: {weekday_avg:.2f} kW",
        annotation_position="bottom left"
    )
    fig.add_hline(
        y=weekend_avg,
        line_dash="dot",
        line_color=CHART_THEME['secondary_color'],
        annotation_text=f"Weekend Avg: {weekend_avg:.2f} kW",
        annotation_position="top right"
    )

    fig.update_layout(
        title=dict(text="<b>Weekly Consumption Pattern (Monday – Sunday)</b>", font=dict(size=16, color="#f8fafc")),
        xaxis=dict(title="Day of Week", categoryorder='array', categoryarray=day_order, gridcolor=CHART_THEME['grid_color']),
        yaxis=dict(title="Average Active Power (kW)", gridcolor=CHART_THEME['grid_color']),
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor=CHART_THEME['bg_color'],
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        margin=dict(l=40, r=40, t=50, b=40),
        showlegend=False
    )

    grouped['IsWeekend'] = grouped['DayOfWeek'] >= 5
    return grouped, fig


def analyze_monthly_pattern(df_daily: pd.DataFrame, variable: str = 'Global_active_power') -> Tuple[pd.DataFrame, go.Figure]:
    """
    Calculate and visualize monthly consumption pattern (January to December)
    to diagnose seasonal peaks (winter heating vs summer AC vs spring/autumn lull).
    """
    df = df_daily.copy()
    df['Month'] = df.index.month
    df['MonthName'] = df.index.strftime('%B')

    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    grouped = df.groupby(['Month', 'MonthName'])[variable].agg(['mean', 'std', 'min', 'max', 'median']).reset_index()
    grouped.sort_values('Month', inplace=True)

    fig = go.Figure()

    # Bar chart for monthly mean
    fig.add_trace(go.Bar(
        x=grouped['MonthName'],
        y=grouped['mean'],
        marker=dict(
            color=grouped['mean'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="kW", thickness=15, len=0.7)
        ),
        text=[f"{v:.2f}" for v in grouped['mean']],
        textposition='outside',
        hovertemplate='<b>%{x}:</b> %{y:.3f} kW<br>Min: %{customdata[0]:.2f}<br>Max: %{customdata[1]:.2f}<extra></extra>',
        customdata=grouped[['min', 'max']].values,
        name='Monthly Mean'
    ))

    # Trend line over bars
    fig.add_trace(go.Scatter(
        x=grouped['MonthName'],
        y=grouped['mean'],
        mode='lines+markers',
        line=dict(color='#f43f5e', width=2.5),
        marker=dict(size=8, color='#f43f5e'),
        name='Seasonal Trajectory'
    ))

    fig.update_layout(
        title=dict(text="<b>Monthly Seasonal Electricity Profile (Jan – Dec)</b>", font=dict(size=16, color="#f8fafc")),
        xaxis=dict(title="Month", categoryorder='array', categoryarray=month_order, gridcolor=CHART_THEME['grid_color']),
        yaxis=dict(title="Average Active Power (kW)", gridcolor=CHART_THEME['grid_color']),
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor=CHART_THEME['bg_color'],
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return grouped, fig


def plot_submetering_composition(df: pd.DataFrame) -> Tuple[Dict[str, float], go.Figure]:
    """
    Analyze end-use breakdown across the 3 submeterings and remaining household loads:
    - Sub 1: Kitchen (dishwasher, oven, microwave)
    - Sub 2: Laundry (washing machine, drier, fridge)
    - Sub 3: Climate (electric water heater, AC)
    - Remainder: Other active consumption (lighting, computing, TV)
    """
    total_sub1 = df['Sub_metering_1'].sum() if 'Sub_metering_1' in df.columns else 0
    total_sub2 = df['Sub_metering_2'].sum() if 'Sub_metering_2' in df.columns else 0
    total_sub3 = df['Sub_metering_3'].sum() if 'Sub_metering_3' in df.columns else 0
    total_rem = df['Sub_metering_remainder'].sum() if 'Sub_metering_remainder' in df.columns else 0

    totals = {
        'Kitchen (Sub 1)': float(total_sub1),
        'Laundry & Utility (Sub 2)': float(total_sub2),
        'Water Heater & AC (Sub 3)': float(total_sub3),
        'Other Plug & Lighting Loads': float(total_rem)
    }

    labels = list(totals.keys())
    values = list(totals.values())
    colors = ['#f59e0b', '#10b981', '#38bdf8', '#a855f7']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker=dict(colors=colors, line=dict(color='#0f172a', width=2)),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        hovertemplate='<b>%{label}</b><br>Total Energy: %{value:,.0f} Wh<br>Share: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(text="<b>Household End-Use Energy Breakdown</b>", font=dict(size=16, color="#f8fafc")),
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor=CHART_THEME['bg_color'],
        font=dict(family=CHART_THEME['font_family'], color=CHART_THEME['font_color']),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
    )

    return totals, fig
