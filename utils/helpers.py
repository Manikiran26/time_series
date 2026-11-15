"""
Helper utility functions for UI formatting, CSS badges, and statistical metric displays.
Designed specifically for the PowerTrack consumer electricity monitoring interface.
"""

import streamlit as st
from typing import Dict, Any, Optional


def render_powertrack_header(user_name: str = "Manikiran"):
    """Render the official PowerTrack application header."""
    header_html = f"""
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 24px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    ">
        <div>
            <div style="
                font-size: 2.0rem;
                font-weight: 800;
                letter-spacing: -0.03em;
                background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                ⚡ PowerTrack
            </div>
            <div style="font-size: 0.95rem; color: #94a3b8; font-weight: 500; margin-top: 2px;">
                Electricity Consumption Dashboard
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 1.15rem; font-weight: 600; color: #f8fafc;">
                Hello, {user_name}
            </div>
            <div style="font-size: 0.8rem; color: #10b981; display: flex; align-items: center; justify-content: flex-end; gap: 5px; margin-top: 3px;">
                <span style="height: 7px; width: 7px; background-color: #10b981; border-radius: 50%; display: inline-block;"></span>
                Smart Meter Active
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_summary_card(title: str, value: str, subtext: Optional[str] = None, icon: str = "⚡"):
    """Render consumer-grade KPI summary card."""
    subtext_html = f"<div style='font-size: 0.82rem; color: #94a3b8; margin-top: 5px;'>{subtext}</div>" if subtext else ""
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.75) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 4px 20px -3px rgba(0, 0, 0, 0.35);
        height: 100%;
        transition: transform 0.2s ease;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 0.88rem; font-weight: 500; color: #94a3b8; letter-spacing: 0.02em;">{title}</div>
            <span style="font-size: 1.1rem; opacity: 0.85;">{icon}</span>
        </div>
        <div style="font-size: 2.0rem; font-weight: 700; color: #f8fafc; margin-top: 6px; letter-spacing: -0.02em;">
            {value}
        </div>
        {subtext_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_consumption_pattern_box(
    peak_hours: str,
    lowest_hours: str,
    highest_day: str,
    trend_status: str
):
    """
    Render clean summary box for Consumption Pattern:
    Peak: 7 PM – 10 PM
    Lowest: 3 AM – 5 AM
    Highest Day: Sunday
    Trend: Increasing
    """
    trend_color = "#10b981" if trend_status == "Decreasing" else ("#f59e0b" if trend_status == "Stable" else "#38bdf8")
    box_html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.7) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 22px 24px;
        margin: 20px 0;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
    ">
        <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
            📊 Consumption Pattern
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px 16px; border-radius: 10px; border-left: 3px solid #f59e0b;">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">Peak Hours</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-top: 2px;">{peak_hours}</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px 16px; border-radius: 10px; border-left: 3px solid #38bdf8;">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">Lowest Hours</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-top: 2px;">{lowest_hours}</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px 16px; border-radius: 10px; border-left: 3px solid #818cf8;">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">Highest Day</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-top: 2px;">{highest_day}</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px 16px; border-radius: 10px; border-left: 3px solid {trend_color};">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">Overall Trend</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: {trend_color}; margin-top: 2px;">{trend_status}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(box_html, unsafe_allow_html=True)


def render_insights_cards(insights: list):
    """Render clean, natural-language insights cards."""
    st.markdown("""
    <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin: 24px 0 14px 0; display: flex; align-items: center; gap: 8px;">
        💡 Usage Insights
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(insights) if len(insights) <= 3 else 3)
    for i, ins in enumerate(insights[:3]):
        with cols[i]:
            card_html = f"""
            <div style="
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.65) 100%);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 12px;
                padding: 16px 18px;
                height: 100%;
                box-shadow: 0 4px 15px -2px rgba(0, 0, 0, 0.25);
            ">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 600; color: #38bdf8; font-size: 0.95rem;">
                    <span>{ins.get('icon', '💡')}</span>
                    <span>{ins.get('title', 'Insight')}</span>
                </div>
                <div style="font-size: 0.88rem; color: #cbd5e1; margin-top: 8px; line-height: 1.45;">
                    {ins.get('text', '')}
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    # Remaining insights in full-width rows if any
    if len(insights) > 3:
        for ins in insights[3:]:
            card_html = f"""
            <div style="
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.55) 100%);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 10px;
                padding: 14px 18px;
                margin-top: 10px;
                display: flex;
                align-items: flex-start;
                gap: 12px;
            ">
                <span style="font-size: 1.2rem;">{ins.get('icon', '💡')}</span>
                <div>
                    <div style="font-weight: 600; color: #f8fafc; font-size: 0.9rem;">{ins.get('title', 'Insight')}</div>
                    <div style="font-size: 0.86rem; color: #94a3b8; margin-top: 3px; line-height: 1.4;">{ins.get('text', '')}</div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)


def get_powertrack_css() -> str:
    """Return sleek dark-mode CSS for the consumer PowerTrack interface."""
    return """
    <style>
    /* App background */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Hide default header decor */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Modern button styling */
    .stButton button {
        border-radius: 10px;
        background-color: #1e293b;
        color: #f8fafc;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-weight: 500;
        padding: 6px 16px;
        transition: all 0.2s ease;
    }

    .stButton button:hover {
        background-color: #0284c7;
        color: #ffffff;
        border-color: #38bdf8;
    }

    /* Plotly chart container */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Expander styling for internal diagnostics */
    .streamlit-expanderHeader {
        background-color: #111827 !important;
        border-radius: 10px !important;
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    </style>
    """
