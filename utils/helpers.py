"""
Helper utility functions for UI formatting, CSS badges, and statistical metric displays.
Designed specifically for the PowerTrack consumer electricity monitoring interface.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List


def render_powertrack_header(user_name: str = "Manikiran"):
    """Render the official PowerTrack application header with live smart meter status."""
    header_html = f"""
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 26px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.85) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 18px;
        margin-bottom: 24px;
        box-shadow: 0 12px 36px -10px rgba(0, 0, 0, 0.6);
    ">
        <div>
            <div style="
                font-size: 2.1rem;
                font-weight: 800;
                letter-spacing: -0.03em;
                background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                ⚡ PowerTrack
            </div>
            <div style="font-size: 0.92rem; color: #94a3b8; font-weight: 500; margin-top: 3px;">
                Household Smart-Meter Analytics, Forecasting & Cost Management
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 1.15rem; font-weight: 600; color: #f8fafc;">
                {user_name}
            </div>
            <div style="font-size: 0.82rem; color: #10b981; display: flex; align-items: center; justify-content: flex-end; gap: 6px; margin-top: 4px;">
                <span style="height: 8px; width: 8px; background-color: #10b981; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #10b981;"></span>
                Smart Meter Online
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_summary_card(title: str, value: str, subtext: Optional[str] = None, icon: str = "⚡", delta: Optional[str] = None):
    """Render consumer-grade KPI summary card."""
    subtext_html = f"<div style='font-size: 0.82rem; color: #94a3b8; margin-top: 6px;'>{subtext}</div>" if subtext else ""
    delta_html = f"<span style='font-size: 0.78rem; font-weight: 600; padding: 2px 8px; border-radius: 12px; background: rgba(56, 189, 248, 0.15); color: #38bdf8;'>{delta}</span>" if delta else ""
    
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 4px 24px -3px rgba(0, 0, 0, 0.4);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 0.85rem; font-weight: 600; color: #94a3b8; letter-spacing: 0.02em;">{title}</div>
            <div style="display: flex; align-items: center; gap: 8px;">
                {delta_html}
                <span style="font-size: 1.2rem; opacity: 0.85;">{icon}</span>
            </div>
        </div>
        <div style="font-size: 2.1rem; font-weight: 800; color: #f8fafc; margin-top: 8px; letter-spacing: -0.02em;">
            {value}
        </div>
        {subtext_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_forecast_kpi_card(title: str, value: str, subtext: str, delta: Optional[str] = None, delta_type: str = "good", icon: str = "🔮"):
    """Sleek KPI card specially tailored for future forecasting."""
    delta_bg = "rgba(16, 185, 129, 0.15)" if delta_type == "good" else ("rgba(239, 68, 68, 0.15)" if delta_type == "bad" else "rgba(56, 189, 248, 0.15)")
    delta_color = "#10b981" if delta_type == "good" else ("#ef4444" if delta_type == "bad" else "#38bdf8")
    delta_badge = f"<span style='font-size: 0.76rem; font-weight: 700; padding: 3px 8px; border-radius: 20px; background: {delta_bg}; color: {delta_color};'>{delta}</span>" if delta else ""

    card_html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.65) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.12);
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 6px 25px -4px rgba(0, 0, 0, 0.4);
        height: 100%;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.84rem; font-weight: 600; color: #94a3b8;">{title}</span>
            <div style="display: flex; align-items: center; gap: 8px;">
                {delta_badge}
                <span style="font-size: 1.15rem;">{icon}</span>
            </div>
        </div>
        <div style="font-size: 2.05rem; font-weight: 800; color: #f8fafc; margin-top: 8px; letter-spacing: -0.02em;">
            {value}
        </div>
        <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 6px;">
            {subtext}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_daily_forecast_timeline(df_future: pd.DataFrame):
    """Render modern horizontal day-by-day forecast cards."""
    st.markdown("""
    <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin: 24px 0 14px 0; display: flex; align-items: center; gap: 8px;">
        📅 Day-by-Day Forecast Breakdown
    </div>
    """, unsafe_allow_html=True)

    # Show up to 7 days in clean responsive grid
    display_rows = df_future.head(7)
    cols = st.columns(len(display_rows))

    max_val = float(df_future['forecast_kwh'].max())
    min_val = float(df_future['forecast_kwh'].min())

    for idx, (dt, row) in enumerate(display_rows.iterrows()):
        is_peak = (row['forecast_kwh'] == max_val)
        is_low = (row['forecast_kwh'] == min_val)
        
        tag_bg = "rgba(245, 158, 11, 0.2)" if is_peak else ("rgba(16, 185, 129, 0.2)" if is_low else "rgba(56, 189, 248, 0.1)")
        tag_color = "#f59e0b" if is_peak else ("#10b981" if is_low else "#94a3b8")
        tag_text = "Peak Day" if is_peak else ("Lowest Load" if is_low else "Normal")

        with cols[idx]:
            card_html = f"""
            <div style="
                background: rgba(15, 23, 42, 0.7);
                border: 1px solid {'rgba(245, 158, 11, 0.4)' if is_peak else 'rgba(255, 255, 255, 0.08)'};
                border-radius: 12px;
                padding: 14px 12px;
                text-align: center;
                box-shadow: 0 4px 15px -2px rgba(0, 0, 0, 0.3);
            ">
                <div style="font-size: 0.78rem; font-weight: 600; color: #94a3b8;">
                    {dt.strftime('%a')}
                </div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #f8fafc; margin-top: 2px;">
                    {dt.strftime('%d %b')}
                </div>
                <div style="font-size: 1.45rem; font-weight: 800; color: #38bdf8; margin: 8px 0 4px 0;">
                    {row['forecast_kwh']:.1f}
                </div>
                <div style="font-size: 0.72rem; color: #94a3b8;">kWh</div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #cbd5e1; margin-top: 6px;">
                    ₹{row['est_cost_inr']:.0f}
                </div>
                <div style="margin-top: 8px;">
                    <span style="font-size: 0.7rem; font-weight: 700; padding: 2px 6px; border-radius: 8px; background: {tag_bg}; color: {tag_color};">
                        {tag_text}
                    </span>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)


def render_consumption_pattern_box(
    peak_hours: str,
    lowest_hours: str,
    highest_day: str,
    trend_status: str
):
    """Render clean summary box for Consumption Pattern."""
    trend_color = "#10b981" if trend_status == "Decreasing" else ("#f59e0b" if trend_status == "Stable" else "#38bdf8")
    box_html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.7) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px 24px;
        margin: 20px 0;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
    ">
        <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
            📊 Consumption Pattern Summary
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
            <div style="background: rgba(15, 23, 42, 0.6); padding: 14px 16px; border-radius: 12px; border-left: 3px solid #f59e0b;">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">Diurnal Peak Hours</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-top: 3px;">{peak_hours}</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 14px 16px; border-radius: 12px; border-left: 3px solid #38bdf8;">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">Lowest Standby Hours</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-top: 3px;">{lowest_hours}</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 14px 16px; border-radius: 12px; border-left: 3px solid #818cf8;">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">Highest Load Day</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-top: 3px;">{highest_day}</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 14px 16px; border-radius: 12px; border-left: 3px solid {trend_color};">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">Overall Trajectory</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: {trend_color}; margin-top: 3px;">{trend_status}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(box_html, unsafe_allow_html=True)


def render_insights_cards(insights: list):
    """Render clean, natural-language insights cards."""
    st.markdown("""
    <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin: 24px 0 14px 0; display: flex; align-items: center; gap: 8px;">
        💡 Actionable Consumption Insights
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(insights) if len(insights) <= 3 else 3)
    for i, ins in enumerate(insights[:3]):
        with cols[i]:
            card_html = f"""
            <div style="
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.65) 100%);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 14px;
                padding: 18px 20px;
                height: 100%;
                box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.25);
            ">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 600; color: #38bdf8; font-size: 0.95rem;">
                    <span>{ins.get('icon', '💡')}</span>
                    <span>{ins.get('title', 'Insight')}</span>
                </div>
                <div style="font-size: 0.88rem; color: #cbd5e1; margin-top: 8px; line-height: 1.5;">
                    {ins.get('text', '')}
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    if len(insights) > 3:
        for ins in insights[3:]:
            card_html = f"""
            <div style="
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.55) 100%);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                padding: 14px 18px;
                margin-top: 10px;
                display: flex;
                align-items: flex-start;
                gap: 12px;
            ">
                <span style="font-size: 1.2rem;">{ins.get('icon', '💡')}</span>
                <div>
                    <div style="font-weight: 600; color: #f8fafc; font-size: 0.9rem;">{ins.get('title', 'Insight')}</div>
                    <div style="font-size: 0.86rem; color: #94a3b8; margin-top: 3px; line-height: 1.45;">{ins.get('text', '')}</div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)


def get_powertrack_css() -> str:
    """Return polished, modern SaaS dark-mode CSS."""
    return """
    <style>
    /* Obsidian dark background */
    .stApp {
        background-color: #090d16;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Hide standard chrome */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Modern button styling */
    .stButton button {
        border-radius: 12px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #f8fafc;
        border: 1px solid rgba(56, 189, 248, 0.25);
        font-weight: 600;
        padding: 8px 20px;
        transition: all 0.25s ease;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff;
        border-color: #38bdf8;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.35);
        transform: translateY(-1px);
    }

    /* Primary buttons */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
        border: 1px solid rgba(56, 189, 248, 0.5);
    }
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%);
        box-shadow: 0 6px 22px rgba(37, 99, 235, 0.4);
    }

    /* Segmented controls / pill selectors */
    div[data-baseweb="segmented-control"] {
        background-color: #111827 !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    div[data-baseweb="segmented-control"] button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
    }

    div[data-baseweb="segmented-control"] button[aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4) !important;
    }

    /* Plotly chart container */
    .js-plotly-plot {
        border-radius: 14px;
        overflow: hidden;
    }

    /* Expander styling for internal diagnostics */
    .streamlit-expanderHeader {
        background-color: #0f172a !important;
        border-radius: 12px !important;
        color: #94a3b8 !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 12px 18px !important;
    }

    /* Sidebar polish */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Clean progress bar */
    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, #38bdf8 0%, #10b981 100%) !important;
        border-radius: 10px;
    }
    </style>
    """
