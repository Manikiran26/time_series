import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from analysis.household_preprocessing import load_household_daily_series, load_household_hourly_series

df_daily, meta = load_household_daily_series("MH01")
df_hourly = load_household_hourly_series("MH01")

val_col = 'hourly_kwh' if 'hourly_kwh' in df_hourly.columns else 'consumption_kwh'
if 'timestamp' in df_hourly.columns:
    df_hourly['Hour'] = pd.to_datetime(df_hourly['timestamp']).dt.hour
else:
    df_hourly['Hour'] = df_hourly.index.hour

hourly_avg = df_hourly.groupby('Hour')[val_col].mean().reindex(range(24), fill_value=0.05)
x_ticks = [f"{h:02d}" for h in range(24)]
y_vals = hourly_avg.values

tariff_rate = 6.50
y_cost = y_vals * tariff_rate

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x_ticks,
    y=y_cost,
    mode='lines',
    name='Hourly Cost',
    line=dict(color='#10b981', width=2.5, shape='spline'),
    fill='tozeroy',
    fillcolor='rgba(16, 185, 129, 0.16)',
    hovertemplate='<b>%{x}:00</b><br><span style="color:#10b981">●</span> ₹%{y:.2f}<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=x_ticks,
    y=[tariff_rate] * 24,
    mode='lines',
    name='Tariff Rate',
    line=dict(color='#1e293b', width=2.0, shape='spline'),
    yaxis='y2',
    hovertemplate='<b>Rate:</b> ₹%{y:.2f}/kWh (UPPCL)<extra></extra>'
))

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', color='#0f172a', size=11),
    margin=dict(l=35, r=35, t=15, b=25),
    height=260,
    showlegend=False,
    hovermode="x unified",
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=False,
        tickmode='array',
        tickvals=['00', '06', '12', '18', '24'],
        tickfont=dict(color='#64748b', size=11)
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#f1f5f9',
        zeroline=False,
        showline=False,
        tickfont=dict(color='#64748b', size=10),
        nticks=4
    ),
    yaxis2=dict(
        showgrid=False,
        zeroline=False,
        showline=False,
        overlaying='y',
        side='right',
        tickfont=dict(color='#64748b', size=10),
        nticks=4
    )
)

print("Plotly Figure created successfully with", len(fig.data), "traces!")
