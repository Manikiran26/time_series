"""
Helper utility functions for UI formatting, CSS badges, and statistical metric displays.
Designed specifically for the PowerTrack consumer electricity monitoring interface.
Guarantees clean HTML rendering without Markdown whitespace/codeblock distortion.
"""

import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from typing import Dict, Any, Optional, List, Tuple
from contextlib import contextmanager


# Responsive column helper
def responsive_columns(ratios_or_count, mobile_stack=True, tablet_2col=True):
    """
    Create responsive columns that adapt to screen size.
    On mobile: stacks vertically
    On tablet (768-1024px): 2-column grid for 3+ columns
    On desktop: uses specified ratios
    """
    if isinstance(ratios_or_count, int):
        count = ratios_or_count
        ratios = [1] * count
    else:
        ratios = list(ratios_or_count)
        count = len(ratios)

    cols = st.columns(ratios)
    return cols


@contextmanager
def toast_container():
    """Context manager for toast notifications."""
    container = st.empty()
    yield container


def render_skeleton(height: int = 100, width: str = "100%", border_radius: int = 8) -> None:
    """Render a loading skeleton placeholder."""
    html = f"""
    <div class="powertrack-skeleton" style="height: {height}px; width: {width}; border-radius: {border_radius}px;"></div>
    """
    render_html(html)


def render_skeleton_card() -> None:
    """Render a skeleton card matching KPI card dimensions."""
    html = """
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 16px 18px; min-height: 110px; display: flex; flex-direction: column; justify-content: space-between;">
        <div class="powertrack-skeleton" style="height: 16px; width: 60%; border-radius: 4px; margin-bottom: 12px;"></div>
        <div class="powertrack-skeleton" style="height: 32px; width: 40%; border-radius: 4px; margin-bottom: 12px;"></div>
        <div class="powertrack-skeleton" style="height: 14px; width: 80%; border-radius: 4px;"></div>
    </div>
    """
    render_html(html)


def render_skeleton_chart(height: int = 380) -> None:
    """Render a skeleton for chart placeholders."""
    html = f"""
    <div style="background: rgba(15, 23, 42, 0.5); border-radius: 12px; height: {height}px; border: 1px solid rgba(255, 255, 255, 0.06);">
        <div class="powertrack-skeleton" style="height: 20px; width: 30%; border-radius: 4px; margin: 16px auto 0 auto;"></div>
    </div>
    """
    render_html(html)


def render_skeleton_table(rows: int = 5) -> None:
    """Render a skeleton for table placeholders."""
    skeleton_rows = ""
    for _ in range(rows):
        skeleton_rows += '<div class="powertrack-skeleton" style="height: 12px; width: 100%; border-radius: 4px; margin: 8px 0;"></div>'

    html = f"""
    <div style="background: rgba(15, 23, 42, 0.5); border-radius: 12px; padding: 16px; border: 1px solid rgba(255, 255, 255, 0.06);">
        <div class="powertrack-skeleton" style="height: 16px; width: 40%; border-radius: 4px; margin-bottom: 16px;"></div>
        {skeleton_rows}
    </div>
    """
    render_html(html)


def show_toast(message: str, type: str = "info", duration: int = 4000) -> None:
    """Show a toast notification. Types: success, warning, error, info"""
    icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    icon = icons.get(type, "ℹ️")

    html = f"""
    <div class="powertrack-toast-container" id="toast-container">
        <div class="powertrack-toast {type}" role="alert" aria-live="polite">
            <span style="font-size: 1.2rem;">{icon}</span>
            <span style="flex: 1; color: var(--text-primary);">{message}</span>
            <button onclick="this.parentElement.remove()" style="background: none; border: none; color: var(--text-muted); font-size: 1.2rem; cursor: pointer; padding: 0; line-height: 1;">×</button>
        </div>
    </div>
    <script>
        setTimeout(() => {{
            const toast = document.querySelector('.powertrack-toast');
            if (toast) {{
                toast.style.animation = 'slideIn 0.3s ease-out reverse';
                setTimeout(() => toast.remove(), 300);
            }}
        }}, {duration});
    </script>
    """
    render_html(html)


def show_progress(label: str, progress: float, key: str = None) -> None:
    """Show a progress indicator with label."""
    html = f"""
    <div style="margin: 8px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="font-size: 0.85rem; font-weight: 500; color: var(--text-secondary);">{label}</span>
            <span style="font-size: 0.8rem; color: var(--text-muted);">{int(progress * 100)}%</span>
        </div>
        <div style="height: 6px; background: var(--bg-tertiary); border-radius: 3px; overflow: hidden;">
            <div style="height: 100%; width: {progress * 100}%; background: var(--accent-primary); border-radius: 3px; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """
    render_html(html)


def render_tooltip(text: str, icon: str = "ⓘ") -> None:
    """Render a tooltip with hover text."""
    html = f'<span class="powertrack-tooltip" data-tooltip="{text}" tabindex="0" aria-label="{text}">{icon}</span>'
    render_html(html)


def render_help_text(text: str) -> None:
    """Render help text with consistent styling."""
    html = f'<div class="powertrack-help-text">{text}</div>'
    render_html(html)


def render_info_banner(message: str, icon: str = "ℹ️", type: str = "info") -> None:
    """Render an informational banner. Types: info, warning, success, error"""
    colors = {
        "info": "var(--accent-primary)",
        "warning": "var(--accent-warning)",
        "success": "var(--accent-success)",
        "error": "var(--accent-danger)"
    }
    border_color = colors.get(type, colors["info"])

    html = f"""
    <div class="powertrack-info-banner" style="border-left-color: {border_color};">
        <span class="icon">{icon}</span>
        <div class="content">{message}</div>
    </div>
    """
    render_html(html)


def render_kbd(keys: list) -> str:
    """Render keyboard shortcut keys. Returns HTML string."""
    kbd_html = ''.join(f'<kbd class="powertrack-kbd">{k}</kbd>' for k in keys)
    return f'<span class="powertrack-kbd-sequence">{kbd_html}</span>'


def render_shortcut_help(shortcuts: list) -> None:
    """Render a list of keyboard shortcuts. shortcuts = [('Keys', 'Description'), ...]"""
    rows = ""
    for keys, desc in shortcuts:
        if isinstance(keys, str):
            keys = [keys]
        kbd = render_kbd(keys)
        rows += f'<div style="display: flex; align-items: center; gap: 12px; padding: 6px 0; border-bottom: 1px solid var(--border-subtle);"><div style="min-width: 120px;">{kbd}</div><div style="font-size: 0.8rem; color: var(--text-secondary);">{desc}</div></div>'

    html = f"""
    <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 16px; font-size: 0.85rem;">
        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">Keyboard Shortcuts</div>
        {rows}
    </div>
    """
    render_html(html)


def render_keyboard_shortcuts_modal() -> None:
    """Render the keyboard shortcuts modal with full shortcuts list."""
    shortcuts_by_category = {
        "Navigation": [
            (["1"], "Dashboard"),
            (["2"], "Electricity Usage"),
            (["3"], "Consumption Patterns"),
            (["4"], "Forecasting"),
            (["5"], "Budget Guardian"),
            (["6"], "Bill Analysis"),
            (["7"], "What-If Simulator"),
            (["8"], "Data Quality"),
            (["9"], "Reports & Export"),
        ],
        "Actions": [
            (["T"], "Toggle Theme (Dark/Light)"),
            (["R"], "Refresh / Retrain Models"),
            (["E"], "Export Report"),
            (["C"], "Copy Chart Data"),
        ],
        "Global": [
            (["?"], "Show/Hide This Help"),
            (["Esc"], "Close Modals / Dismiss Toasts"),
            (["Ctrl/Cmd + K"], "Command Palette (Future)"),
        ],
    }

    category_html = ""
    for category, shortcuts in shortcuts_by_category.items():
        category_html += f'<div class="powertrack-shortcut-category">{category}</div>'
        for keys, desc in shortcuts:
            if isinstance(keys, str):
                keys = [keys]
            kbd_html = ''.join(f'<kbd class="powertrack-kbd">{k}</kbd>' for k in keys)
            category_html += f'''
            <div class="powertrack-shortcut-item">
                <div class="powertrack-shortcut-keys">{kbd_html}</div>
                <div class="powertrack-shortcut-desc">{desc}</div>
            </div>
            '''

    html = f"""
    <div class="powertrack-shortcuts-overlay" id="shortcuts-overlay" onclick="document.getElementById('shortcuts-overlay').classList.remove('visible')">
        <div class="powertrack-shortcuts-modal" onclick="event.stopPropagation()">
            <div class="powertrack-shortcuts-header">
                <h3>⌨️ Keyboard Shortcuts</h3>
                <button class="powertrack-shortcuts-close" onclick="document.getElementById('shortcuts-overlay').classList.remove('visible')" aria-label="Close shortcuts help">×</button>
            </div>
            <div class="powertrack-shortcuts-list">
                {category_html}
            </div>
        </div>
    </div>
    <script>
        // Toggle shortcuts modal with ? key
        document.addEventListener('keydown', function(e) {{
            if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {{
                const overlay = document.getElementById('shortcuts-overlay');
                if (overlay) {{
                    overlay.classList.toggle('visible');
                }}
            }}
            // Close with Escape
            if (e.key === 'Escape') {{
                const overlay = document.getElementById('shortcuts-overlay');
                if (overlay && overlay.classList.contains('visible')) {{
                    overlay.classList.remove('visible');
                }}
            }}
        }});

        // Navigation shortcuts (1-9)
        document.addEventListener('keydown', function(e) {{
            if (e.key >= '1' && e.key <= '9' && !e.ctrlKey && !e.metaKey && !e.altKey) {{
                const navItems = document.querySelectorAll('div[role="radiogroup"] label');
                const index = parseInt(e.key) - 1;
                if (navItems[index]) {{
                    navItems[index].click();
                }}
            }}
        }});

        // Theme toggle with T
        document.addEventListener('keydown', function(e) {{
            if (e.key.toLowerCase() === 't' && !e.ctrlKey && !e.metaKey && !e.altKey) {{
                const themeBtn = document.querySelector('button[key="theme_toggle"]');
                if (themeBtn) {{
                    themeBtn.click();
                }}
            }}
        }});
    </script>
    """
    render_html(html)


def render_html(html_str: str):
    """
    Renders HTML safely to Streamlit.
    Collapses newlines and indentation to avoid Markdown treating indented lines as code blocks.
    """
    clean = re.sub(r'\s+', ' ', html_str).strip()
    st.markdown(clean, unsafe_allow_html=True)


def render_powertrack_header(user_name: str = "Manikiran", theme: str = "light"):
    """Render the official PowerTrack application header with live smart meter status."""
    is_light = (theme == 'light')
    header_bg = "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)" if is_light else "linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.85) 100%)"
    border_color = "rgba(2, 132, 199, 0.15)" if is_light else "rgba(56, 189, 248, 0.2)"
    shadow_val = "0 10px 25px -5px rgba(0, 0, 0, 0.04)" if is_light else "0 10px 30px -10px rgba(0, 0, 0, 0.6)"
    text_color = "#0f172a" if is_light else "#f8fafc"
    sub_color = "#64748b" if is_light else "#94a3b8"

    html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 26px; background: {header_bg}; border: 1px solid {border_color}; border-radius: 20px; margin-bottom: 22px; box-shadow: {shadow_val};">
        <div>
            <div style="font-size: 2.0rem; font-weight: 800; letter-spacing: -0.03em; background: linear-gradient(90deg, #0284c7 0%, #6366f1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: flex; align-items: center; gap: 8px;">
                ⚡ PowerTrack
            </div>
            <div style="font-size: 0.88rem; color: {sub_color}; font-weight: 500; margin-top: 2px;">
                Household Smart-Meter Analytics, Forecasting & Cost Management
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 1.1rem; font-weight: 700; color: {text_color};">
                {user_name}
            </div>
            <div style="font-size: 0.8rem; color: #10b981; display: flex; align-items: center; justify-content: flex-end; gap: 6px; margin-top: 4px; font-weight: 600;">
                <span style="height: 7px; width: 7px; background-color: #10b981; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #10b981;"></span>
                Smart Meter Active
            </div>
        </div>
    </div>
    """
    render_html(html)


def render_summary_card(title: str, value: str, subtext: Optional[str] = None, icon: str = "⚡", delta: Optional[str] = None):
    """Render consumer-grade KPI summary card with clean modern styling."""
    subtext_html = f'<div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{subtext}</div>' if subtext else ""
    delta_html = f'<span style="font-size: 0.72rem; font-weight: 700; padding: 2px 7px; border-radius: 10px; background: rgba(14, 165, 233, 0.12); color: var(--accent-primary); margin-right: 6px;">{delta}</span>' if delta else ""
    
    html = f"""
    <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 20px; padding: 18px 20px; box-shadow: 0 4px 20px -3px var(--shadow-card); min-height: 110px; display: flex; flex-direction: column; justify-content: space-between;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted);">{title}</span>
            <div>{delta_html}<span style="font-size: 1.15rem; opacity: 0.85;">{icon}</span></div>
        </div>
        <div style="font-size: 1.85rem; font-weight: 800; color: var(--text-primary); margin-top: 4px; letter-spacing: -0.02em;">
            {value}
        </div>
        {subtext_html}
    </div>
    """
    render_html(html)


def render_forecast_kpi_card(title: str, value: str, subtext: str, delta: Optional[str] = None, delta_type: str = "good", icon: str = "🔮"):
    """Sleek KPI card specially tailored for future forecasting."""
    delta_bg = "rgba(16, 185, 129, 0.12)" if delta_type == "good" else ("rgba(239, 68, 68, 0.12)" if delta_type == "bad" else "rgba(14, 165, 233, 0.12)")
    delta_color = "#10b981" if delta_type == "good" else ("#ef4444" if delta_type == "bad" else "#0284c7")
    delta_badge = f'<span style="font-size: 0.72rem; font-weight: 700; padding: 2px 7px; border-radius: 12px; background: {delta_bg}; color: {delta_color}; margin-right: 6px;">{delta}</span>' if delta else ""

    html = f"""
    <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 20px; padding: 18px 20px; box-shadow: 0 4px 20px -3px var(--shadow-card); min-height: 110px; display: flex; flex-direction: column; justify-content: space-between;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted);">{title}</span>
            <div>{delta_badge}<span style="font-size: 1.15rem;">{icon}</span></div>
        </div>
        <div style="font-size: 1.85rem; font-weight: 800; color: var(--text-primary); margin-top: 4px; letter-spacing: -0.02em;">
            {value}
        </div>
        <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            {subtext}
        </div>
    </div>
    """
    render_html(html)


def render_daily_forecast_timeline(df_future: pd.DataFrame):
    """Render modern horizontal day-by-day forecast cards."""
    st.markdown("""
    <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin: 20px 0 12px 0; display: flex; align-items: center; gap: 8px;">
        📅 Day-by-Day Forecast Breakdown
    </div>
    """, unsafe_allow_html=True)

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
        border_style = "rgba(245, 158, 11, 0.45)" if is_peak else "rgba(255, 255, 255, 0.08)"

        with cols[idx]:
            html = f"""
            <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid {border_style}; border-radius: 12px; padding: 12px 10px; text-align: center; box-shadow: 0 4px 15px -2px rgba(0, 0, 0, 0.3);">
                <div style="font-size: 0.76rem; font-weight: 600; color: #94a3b8;">{dt.strftime('%a')}</div>
                <div style="font-size: 0.82rem; font-weight: 700; color: #f8fafc; margin-top: 2px;">{dt.strftime('%d %b')}</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #38bdf8; margin: 6px 0 2px 0;">{row['forecast_kwh']:.1f}</div>
                <div style="font-size: 0.7rem; color: #94a3b8;">kWh</div>
                <div style="font-size: 0.8rem; font-weight: 600; color: #cbd5e1; margin-top: 4px;">₹{row['est_cost_inr']:.0f}</div>
                <div style="margin-top: 6px;"><span style="font-size: 0.68rem; font-weight: 700; padding: 2px 6px; border-radius: 8px; background: {tag_bg}; color: {tag_color};">{tag_text}</span></div>
            </div>
            """
            render_html(html)


def render_consumption_pattern_box(
    peak_hours: str,
    lowest_hours: str,
    highest_day: str,
    trend_status: str
):
    """Render clean summary box for Consumption Pattern."""
    trend_color = "#10b981" if trend_status == "Decreasing" else ("#f59e0b" if trend_status == "Stable" else "#0ea5e9")
    html = f"""
    <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 20px; padding: 22px 24px; margin: 20px 0; box-shadow: 0 4px 20px -2px var(--shadow-card);">
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin-bottom: 16px;">📊 Consumption Pattern Summary</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px;">
            <div style="background: var(--bg-tertiary); padding: 14px 16px; border-radius: 14px; border-left: 4px solid #f59e0b;">
                <div style="font-size: 0.78rem; color: var(--text-muted); font-weight: 500;">Diurnal Peak Hours</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-top: 4px;">{peak_hours}</div>
            </div>
            <div style="background: var(--bg-tertiary); padding: 14px 16px; border-radius: 14px; border-left: 4px solid #0ea5e9;">
                <div style="font-size: 0.78rem; color: var(--text-muted); font-weight: 500;">Lowest Standby Hours</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-top: 4px;">{lowest_hours}</div>
            </div>
            <div style="background: var(--bg-tertiary); padding: 14px 16px; border-radius: 14px; border-left: 4px solid #8b5cf6;">
                <div style="font-size: 0.78rem; color: var(--text-muted); font-weight: 500;">Highest Load Day</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-top: 4px;">{highest_day}</div>
            </div>
            <div style="background: var(--bg-tertiary); padding: 14px 16px; border-radius: 14px; border-left: 4px solid {trend_color};">
                <div style="font-size: 0.78rem; color: var(--text-muted); font-weight: 500;">Overall Trajectory</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: {trend_color}; margin-top: 4px;">{trend_status}</div>
            </div>
        </div>
    </div>
    """
    render_html(html)


def render_insights_cards(insights: list):
    """Render clean, natural-language insights cards."""
    st.markdown("""
    <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin: 24px 0 14px 0;">
        💡 Actionable Consumption Insights
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(insights) if len(insights) <= 3 else 3)
    for i, ins in enumerate(insights[:3]):
        with cols[i]:
            html = f"""
            <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 16px 18px; height: 100%; box-shadow: 0 4px 16px -2px var(--shadow-card);">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 600; color: var(--accent-primary); font-size: 0.92rem;">
                    <span>{ins.get('icon', '💡')}</span>
                    <span>{ins.get('title', 'Insight')}</span>
                </div>
                <div style="font-size: 0.86rem; color: var(--text-secondary); margin-top: 8px; line-height: 1.5;">
                    {ins.get('text', '')}
                </div>
            </div>
            """
            render_html(html)

    if len(insights) > 3:
        for ins in insights[3:]:
            html = f"""
            <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 14px; padding: 14px 18px; margin-top: 10px; display: flex; align-items: flex-start; gap: 12px; box-shadow: 0 2px 10px -2px var(--shadow-card);">
                <span style="font-size: 1.2rem;">{ins.get('icon', '💡')}</span>
                <div>
                    <div style="font-weight: 600; color: var(--text-primary); font-size: 0.9rem;">{ins.get('title', 'Insight')}</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 3px; line-height: 1.45;">{ins.get('text', '')}</div>
                </div>
            </div>
            """
            render_html(html)


def plot_card1_mini_area_chart(
    df_hourly: Optional[pd.DataFrame] = None,
    df_slice: Optional[pd.DataFrame] = None,
    unit_mode: str = "INR",
    theme: str = "light",
    tariff_rate: float = 6.50
) -> go.Figure:
    """
    Renders the modern mini area curve for Card 1 matching the reference image:
    - Mint-green spline filled area curve
    - Charcoal line overlay
    - Clean dual-axis layout or clean x-axis (00, 06, 12, 18, 24)
    - Hover tooltip popover
    """
    fig = go.Figure()

    if df_hourly is not None and not df_hourly.empty:
        df_h = df_hourly.copy()
        val_col = 'hourly_kwh' if 'hourly_kwh' in df_h.columns else ('power_kw' if 'power_kw' in df_h.columns else 'consumption_kwh')
        if 'Hour' not in df_h.columns:
            if 'timestamp' in df_h.columns and pd.api.types.is_datetime64_any_dtype(df_h['timestamp']):
                df_h['Hour'] = pd.to_datetime(df_h['timestamp']).dt.hour
            elif hasattr(df_h.index, 'hour'):
                df_h['Hour'] = df_h.index.hour
            else:
                df_h['Hour'] = np.arange(len(df_h)) % 24
        
        hourly_grp = df_h.groupby('Hour')[val_col].mean().reindex(range(24), fill_value=0.05)
        x_ticks = [f"{h:02d}" for h in range(24)]
        y_energy = hourly_grp.values
    elif df_slice is not None and not df_slice.empty:
        x_ticks = [d.strftime('%d %b') for d in df_slice.index[-14:]]
        y_energy = df_slice['consumption_kwh'].iloc[-14:].values
    else:
        x_ticks = [f"{h:02d}" for h in range(24)]
        y_energy = np.array([0.02, 0.02, 0.02, 0.03, 0.04, 0.32, 0.25, 0.21, 0.19, 0.20, 0.12, 0.05, 0.05, 0.06, 0.08, 0.07, 0.06, 0.06, 0.05, 0.05, 0.06, 0.07, 0.03, 0.02])

    if unit_mode == "INR":
        y_main = y_energy * tariff_rate
        main_unit = "₹"
        main_name = "Hourly Cost"
        hover_main = "₹%{y:.2f}"
        rate_overlay = np.full_like(y_main, tariff_rate)
    else:
        y_main = y_energy
        main_unit = "kWh"
        main_name = "Hourly Energy"
        hover_main = "%{y:.3f} kWh"
        rate_overlay = np.full_like(y_main, float(np.mean(y_energy)))

    # Main Area Trace (Mint / Teal gradient)
    fig.add_trace(go.Scatter(
        x=x_ticks,
        y=y_main,
        mode='lines',
        name=main_name,
        line=dict(color='#10b981', width=2.5, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.16)',
        hovertemplate='<b>%{x}:00</b><br><span style="color:#10b981">●</span> ' + hover_main + '<extra></extra>'
    ))

    # Secondary Charcoal / Slate Overlay Line (Matching the reference screenshot!)
    is_light = (theme == 'light')
    line_overlay_color = '#1e293b' if is_light else '#cbd5e1'
    fig.add_trace(go.Scatter(
        x=x_ticks,
        y=rate_overlay if unit_mode == "INR" else y_main * 1.15,
        mode='lines',
        name='Tariff Rate (₹/kWh)' if unit_mode == "INR" else 'Baseline Pace',
        line=dict(color=line_overlay_color, width=2.2, shape='spline'),
        yaxis='y2' if unit_mode == "INR" else 'y',
        hovertemplate='<b>Rate:</b> ₹%{y:.2f}/kWh (UPPCL)<extra></extra>' if unit_mode == "INR" else '<b>Baseline:</b> %{y:.2f} kWh<extra></extra>'
    ))

    font_color = '#0f172a' if is_light else '#f8fafc'
    grid_color = '#f1f5f9' if is_light else 'rgba(148, 163, 184, 0.12)'

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, -apple-system, sans-serif', color=font_color, size=11),
        margin=dict(l=30, r=30, t=10, b=25),
        height=260,
        showlegend=False,
        hovermode="x unified",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            tickmode='array',
            tickvals=['00', '06', '12', '18', '24'] if len(x_ticks) == 24 else x_ticks[::max(1, len(x_ticks)//4)],
            tickfont=dict(color='#64748b', size=11)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
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
        ) if unit_mode == "INR" else None
    )

    return fig


def render_card2_appliance_breakdown(
    total_kwh: float,
    theme: str = "light"
):
    """
    Card 2 from reference design: 'What consumed the most?'
    Displays 5 categories with circular outline badges, percentages, and mint-green rounded progress bars.
    """
    total_ref = max(total_kwh, 25.0)
    appliances = [
        {"name": "Heating / AC", "icon": "🌡️", "pct": 31, "kwh": total_ref * 0.31},
        {"name": "Cooking", "icon": "🍳", "pct": 28, "kwh": total_ref * 0.28},
        {"name": "Lights & Fans", "icon": "💡", "pct": 16, "kwh": total_ref * 0.16},
        {"name": "Hot water & Pump", "icon": "🚿", "pct": 10, "kwh": total_ref * 0.10},
        {"name": "Laundry & Fridge", "icon": "🧺", "pct": 6, "kwh": total_ref * 0.06},
    ]

    items_html = ""
    for app in appliances:
        items_html += f"""
        <div style="margin-bottom: 16px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 38px; height: 38px; border-radius: 50%; border: 1.5px solid var(--border-subtle); background: var(--bg-tertiary); display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0;">
                        {app['icon']}
                    </div>
                    <span style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary);">{app['name']}: {int(app['kwh'])} kWh</span>
                </div>
                <span style="font-size: 0.92rem; font-weight: 600; color: var(--text-secondary);">{app['pct']}%</span>
            </div>
            <div style="height: 7px; width: calc(100% - 50px); margin-left: 50px; background: var(--bg-tertiary); border-radius: 9999px; overflow: hidden;">
                <div style="height: 100%; width: {app['pct']}%; background: #10b981; border-radius: 9999px;"></div>
            </div>
        </div>
        """

    html = f"""
    <div>
        <div style="text-align: center; font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin-bottom: 22px;">
            What consumed the most?
        </div>
        {items_html}
    </div>
    """
    render_html(html)


def render_card3_household_performance(
    current_kwh: float,
    baseline_kwh: float,
    household_id: str,
    city: str,
    sanctioned_load_kw: float = 1.8,
    theme: str = "light"
):
    """
    Card 3 from reference design: Individual Household Baseline Comparison
    (Strictly for individual house insights - NOT similar homes!)
    Features the dual rounded pillar bars (blue & pink) with floating house badge.
    """
    diff_pct = ((current_kwh - baseline_kwh) / max(baseline_kwh, 1.0)) * 100.0
    if diff_pct <= 0:
        headline = f"Good job! You've consumed <span style='color: #10b981; font-weight: 700;'>{abs(diff_pct):.0f}% less</span> energy than your historical baseline."
    else:
        headline = f"Notice: You've consumed <span style='color: #f59e0b; font-weight: 700;'>{diff_pct:.0f}% more</span> energy than your historical baseline."

    # Compute bar heights (max height 135px, min 38px)
    max_val = max(current_kwh, baseline_kwh, 1.0)
    h_current = int(max(38, (current_kwh / max_val) * 135))
    h_baseline = int(max(38, (baseline_kwh / max_val) * 135))

    html = f"""
    <div>
        <div style="text-align: center; font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">
            Comparison with your baseline
        </div>
        <div style="text-align: center; font-size: 0.90rem; color: var(--text-secondary); margin-bottom: 22px; line-height: 1.4; padding: 0 8px;">
            {headline}
        </div>

        <div style="display: flex; justify-content: center; align-items: flex-end; gap: 32px; height: 160px; margin-bottom: 20px; position: relative;">
            <!-- Floating house badge on top of baseline bar -->
            <div style="position: absolute; right: calc(50% - 74px); bottom: {h_baseline + 8}px; width: 34px; height: 34px; border-radius: 50%; background: var(--bg-secondary); border: 2px solid #ec4899; box-shadow: 0 4px 12px rgba(236,72,153,0.3); display: flex; align-items: center; justify-content: center; font-size: 1.05rem; z-index: 2;">
                🏠
            </div>

            <!-- Left Bar: Your home (Blue) -->
            <div style="display: flex; flex-direction: column; align-items: center; width: 84px;">
                <div style="width: 76px; height: {h_current}px; background: #38bdf8; border-radius: 20px; box-shadow: 0 8px 20px rgba(56,189,248,0.3);"></div>
                <div style="font-size: 1.15rem; font-weight: 800; color: var(--text-primary); margin-top: 10px;">{int(current_kwh)} kWh</div>
                <div style="font-size: 0.82rem; color: var(--text-muted); font-weight: 500;">Your home</div>
            </div>

            <!-- Right Bar: Your baseline (Pink) -->
            <div style="display: flex; flex-direction: column; align-items: center; width: 84px;">
                <div style="width: 76px; height: {h_baseline}px; background: #ec4899; border-radius: 20px; box-shadow: 0 8px 20px rgba(236,72,153,0.3);"></div>
                <div style="font-size: 1.15rem; font-weight: 800; color: var(--text-primary); margin-top: 10px;">{int(baseline_kwh)} kWh</div>
                <div style="font-size: 0.82rem; color: var(--text-muted); font-weight: 500;">Your baseline</div>
            </div>
        </div>

        <!-- Home Profile Footer -->
        <div style="border-top: 1px solid var(--border-subtle); padding-top: 14px; margin-top: 8px;">
            <div style="font-size: 0.80rem; color: var(--text-muted); font-weight: 500;">Home profile used for comparison:</div>
            <div style="font-size: 0.86rem; font-weight: 600; color: var(--text-primary); margin-top: 2px;">
                Household {household_id}, {city} UP • {sanctioned_load_kw:.1f} kW Sanctioned Load
            </div>
            <div style="margin-top: 8px;">
                <span style="font-size: 0.86rem; font-weight: 600; color: #0284c7; cursor: pointer;">Update home profile</span>
            </div>
        </div>
    </div>
    """
    render_html(html)


def get_powertrack_css(theme: str = 'dark') -> str:
    """Return polished, modern CSS with theme support (dark/light)."""

    if theme == 'dark':
        # Dark theme colors
        colors = {
            'bg_primary': '#090d16',
            'bg_secondary': '#0f172a',
            'bg_tertiary': '#1e293b',
            'bg_card': 'rgba(30, 41, 59, 0.75)',
            'bg_card_hover': 'rgba(30, 41, 59, 0.85)',
            'bg_sidebar': '#0b0f19',
            'border_subtle': 'rgba(255, 255, 255, 0.08)',
            'border_accent': 'rgba(56, 189, 248, 0.2)',
            'text_primary': '#f8fafc',
            'text_secondary': '#cbd5e1',
            'text_muted': '#94a3b8',
            'text_disabled': '#64748b',
            'accent_primary': '#38bdf8',
            'accent_secondary': '#818cf8',
            'accent_warning': '#f59e0b',
            'accent_danger': '#ef4444',
            'accent_success': '#10b981',
            'btn_bg': 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            'btn_hover': 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
            'btn_border': 'rgba(56, 189, 248, 0.25)',
            'input_bg': 'rgba(15, 23, 42, 0.6)',
            'input_border': 'rgba(56, 189, 248, 0.15)',
            'segmented_bg': '#111827',
            'segmented_selected': '#0284c7',
            'expander_bg': '#0f172a',
            'chart_bg': 'rgba(15, 23, 42, 0.5)',
            'chart_paper': 'rgba(0,0,0,0)',
            'grid_color': 'rgba(148, 163, 184, 0.15)',
            'scrollbar_track': '#0f172a',
            'scrollbar_thumb': '#334155',
            'shadow': 'rgba(0, 0, 0, 0.4)',
            'shadow_card': 'rgba(0, 0, 0, 0.3)',
        }
    else:
        # Light theme colors - Modern Card Design System
        colors = {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#f1f5f9',
            'bg_card': '#ffffff',
            'bg_card_hover': '#ffffff',
            'bg_sidebar': '#ffffff',
            'border_subtle': '#f1f5f9',
            'border_accent': 'rgba(2, 132, 199, 0.2)',
            'text_primary': '#0f172a',
            'text_secondary': '#334155',
            'text_muted': '#64748b',
            'text_disabled': '#94a3b8',
            'accent_primary': '#0284c7',
            'accent_secondary': '#6366f1',
            'accent_warning': '#d97706',
            'accent_danger': '#dc2626',
            'accent_success': '#10b981',
            'btn_bg': '#ffffff',
            'btn_hover': '#f8fafc',
            'btn_border': '#e2e8f0',
            'input_bg': '#ffffff',
            'input_border': '#e2e8f0',
            'segmented_bg': '#f1f5f9',
            'segmented_selected': '#0284c7',
            'expander_bg': '#ffffff',
            'chart_bg': '#ffffff',
            'chart_paper': '#ffffff',
            'grid_color': '#f1f5f9',
            'scrollbar_track': '#f8fafc',
            'scrollbar_thumb': '#cbd5e1',
            'shadow': 'rgba(0, 0, 0, 0.08)',
            'shadow_card': 'rgba(0, 0, 0, 0.04)',
        }

    return f"""
    <style>
    /* Theme: {theme} */
    :root {{
        --bg-primary: {colors['bg_primary']};
        --bg-secondary: {colors['bg_secondary']};
        --bg-tertiary: {colors['bg_tertiary']};
        --bg-card: {colors['bg_card']};
        --bg-card-hover: {colors['bg_card_hover']};
        --bg-sidebar: {colors['bg_sidebar']};
        --border-subtle: {colors['border_subtle']};
        --border-accent: {colors['border_accent']};
        --text-primary: {colors['text_primary']};
        --text-secondary: {colors['text_secondary']};
        --text-muted: {colors['text_muted']};
        --text-disabled: {colors['text_disabled']};
        --accent-primary: {colors['accent_primary']};
        --accent-secondary: {colors['accent_secondary']};
        --accent-warning: {colors['accent_warning']};
        --accent-danger: {colors['accent_danger']};
        --accent-success: {colors['accent_success']};
        --btn-bg: {colors['btn_bg']};
        --btn-hover: {colors['btn_hover']};
        --btn-border: {colors['btn_border']};
        --input-bg: {colors['input_bg']};
        --input-border: {colors['input_border']};
        --segmented-bg: {colors['segmented_bg']};
        --segmented-selected: {colors['segmented_selected']};
        --expander-bg: {colors['expander_bg']};
        --chart-bg: {colors['chart_bg']};
        --chart-paper: {colors['chart_paper']};
        --grid-color: {colors['grid_color']};
        --scrollbar-track: {colors['scrollbar_track']};
        --scrollbar-thumb: {colors['scrollbar_thumb']};
        --shadow: {colors['shadow']};
        --shadow-card: {colors['shadow_card']};
    }}

    /* Base App Styling */
    .stApp {{
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        transition: background-color 0.3s ease, color 0.3s ease;
    }}

    /* Hide standard header */
    header {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Modern button styling */
    .stButton button {{
        border-radius: 10px;
        background: var(--btn-bg);
        color: var(--text-primary);
        border: 1px solid var(--btn-border);
        font-weight: 600;
        padding: 6px 18px;
        transition: all 0.2s ease;
    }}

    .stButton button:hover {{
        background: var(--btn-hover);
        color: #ffffff;
        border-color: var(--accent-primary);
    }}

    .stButton button:focus {{
        outline: 2px solid var(--accent-primary);
        outline-offset: 2px;
    }}

    /* Streamlit Bordered Container / Modern Card Styling */
    [data-testid="stVerticalBlockBorderWrapper"] > div {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 24px !important;
        padding: 22px 24px !important;
        box-shadow: 0 10px 25px -5px var(--shadow-card), 0 0 1px 1px var(--border-subtle) !important;
        transition: all 0.2s ease !important;
    }}

    /* Segmented controls / pill selectors */
    div[data-baseweb="segmented-control"] {{
        background-color: var(--segmented-bg) !important;
        border-radius: 9999px !important;
        padding: 4px !important;
        border: 1px solid var(--border-subtle) !important;
    }}

    div[data-baseweb="segmented-control"] button {{
        border-radius: 9999px !important;
        font-weight: 700 !important;
        color: var(--text-secondary) !important;
        padding: 5px 16px !important;
        font-size: 0.85rem !important;
        background: transparent !important;
        background-color: transparent !important;
    }}

    div[data-baseweb="segmented-control"] button div,
    div[data-baseweb="segmented-control"] button p {{
        color: var(--text-secondary) !important;
        font-weight: 700 !important;
    }}

    div[data-baseweb="segmented-control"] button[aria-selected="true"] {{
        background-color: var(--segmented-selected) !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3) !important;
    }}

    div[data-baseweb="segmented-control"] button[aria-selected="true"] div,
    div[data-baseweb="segmented-control"] button[aria-selected="true"] p {{
        color: #ffffff !important;
    }}

    div[data-baseweb="segmented-control"] button[aria-selected="false"] {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    div[data-baseweb="segmented-control"] button:focus {{
        outline: 2px solid var(--accent-primary);
        outline-offset: 2px;
    }}

    /* Selectbox styling */
    div[data-baseweb="select"] > div {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }}

    div[data-baseweb="select"] * {{
        color: var(--text-primary) !important;
    }}

    div[data-baseweb="select"] > div:focus-within {{
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px var(--border-accent) !important;
    }}

    /* Number input styling */
    .stNumberInput input {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }}

    .stNumberInput input:focus {{
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px var(--border-accent) !important;
    }}

    /* Slider styling */
    .stSlider > div > div > div > div {{
        background-color: var(--accent-primary) !important;
    }}

    .stSlider > div > div > div {{
        background-color: var(--border-subtle) !important;
    }}

    /* Plotly chart container */
    .js-plotly-plot {{
        border-radius: 16px;
        overflow: hidden;
        background-color: var(--chart-bg) !important;
    }}

    /* Expander styling for internal diagnostics */
    .streamlit-expanderHeader {{
        background-color: var(--expander-bg) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-size: 0.9rem !important;
        border: 1px solid var(--border-subtle) !important;
        font-weight: 600 !important;
    }}

    .streamlit-expanderHeader:focus {{
        outline: 2px solid var(--accent-primary);
        outline-offset: 2px;
    }}

    /* Sidebar text & label visibility */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: var(--text-primary);
    }}

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] label span,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }}

    /* Radio navigation list in sidebar */
    div[role="radiogroup"] label,
    div[role="radiogroup"] label p,
    div[role="radiogroup"] label div,
    div[role="radiogroup"] label span,
    div[role="radiogroup"] [data-testid="stMarkdownContainer"] p {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }}

    div[role="radiogroup"] label:hover {{
        background: var(--bg-tertiary) !important;
        border-radius: 10px !important;
    }}

    div[role="radiogroup"] label:has(input:checked) p {{
        color: var(--accent-primary) !important;
        font-weight: 700 !important;
    }}

    /* Dataframe styling */
    .stDataFrame {{
        background-color: var(--bg-card) !important;
        border-radius: 14px;
        border: 1px solid var(--border-subtle);
    }}

    /* Progress bar */
    .stProgress > div > div > div {{
        background-color: var(--accent-primary) !important;
    }}

    /* Metrics */
    [data-testid="stMetric"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 18px !important;
        padding: 16px !important;
    }}
        padding: 16px !important;
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--text-muted) !important;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--text-primary) !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: var(--bg-tertiary);
        border-radius: 10px;
        padding: 4px;
        border: 1px solid var(--border-subtle);
    }}

    .stTabs [data-baseweb="tab"] {{
        color: var(--text-muted) !important;
        border-radius: 7px !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: var(--accent-primary) !important;
        color: #ffffff !important;
    }}

    /* Alert/Info boxes */
    .stAlert {{
        border-radius: 10px !important;
        border: none !important;
    }}

    /* Scrollbar styling */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: var(--scrollbar-track);
    }}

    ::-webkit-scrollbar-thumb {{
        background: var(--scrollbar-thumb);
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: var(--text-muted);
    }}

    /* Selection styling */
    ::selection {{
        background-color: var(--accent-primary);
        color: #ffffff;
    }}

    /* Focus visible for accessibility */
    *:focus-visible {{
        outline: 2px solid var(--accent-primary) !important;
        outline-offset: 2px !important;
    }}

    /* Toast notification container */
    .powertrack-toast-container {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 8px;
        pointer-events: none;
    }}

    .powertrack-toast {{
        pointer-events: auto;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 10px 30px -5px var(--shadow);
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 280px;
        max-width: 420px;
        animation: slideIn 0.3s ease-out;
    }}

    @keyframes slideIn {{
        from {{
            opacity: 0;
            transform: translateX(100%);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}

    .powertrack-toast.success {{ border-left: 4px solid var(--accent-success); }}
    .powertrack-toast.warning {{ border-left: 4px solid var(--accent-warning); }}
    .powertrack-toast.error {{ border-left: 4px solid var(--accent-danger); }}
    .powertrack-toast.info {{ border-left: 4px solid var(--accent-primary); }}

    /* Loading skeleton */
    .powertrack-skeleton {{
        background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-secondary) 50%, var(--bg-tertiary) 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 8px;
    }}

    @keyframes shimmer {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}

    /* Page transition */
    .stApp > div:first-child {{
        animation: fadeIn 0.3s ease-out;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Responsive adjustments */
    @media (max-width: 768px) {{
        .stApp {{
            padding: 0 !important;
        }}

        section[data-testid="stSidebar"] {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        .block-container {{
            padding: 1rem !important;
            max-width: 100% !important;
        }}

        /* Stack columns on mobile */
        div[data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }}

        /* Make 4-column grids stack as 2x2 on tablet, 1x4 on mobile */
        @media (max-width: 1024px) and (min-width: 769px) {{
            div[data-testid="column"] {{
                width: 50% !important;
                flex: 1 1 50% !important;
                min-width: 50% !important;
            }}
        }}

        /* Reduce font sizes on mobile */
        html {{
            font-size: 14px;
        }}

        /* Compact KPI cards */
        [data-testid="stMetric"] {{
            padding: 12px !important;
        }}

        /* Stack sidebar elements */
        section[data-testid="stSidebar"] .stSelectbox,
        section[data-testid="stSidebar"] .stRadio {{
            width: 100% !important;
        }}
    }}

    /* Tablet adjustments */
    @media (max-width: 1024px) and (min-width: 769px) {{
        .block-container {{
            padding: 1.5rem !important;
        }}
    }}

    /* High contrast mode support */
    @media (prefers-contrast: high) {{
        :root {{
            --border-subtle: var(--text-primary);
            --border-accent: var(--accent-primary);
        }}
    }}

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }}
    }}

    /* Data density: compact mode */
    .powertrack-compact [data-testid="stMetric"] {{
        padding: 8px 12px !important;
    }}

    .powertrack-compact .stButton button {{
        padding: 4px 12px !important;
        font-size: 0.85rem !important;
    }}

    .powertrack-compact .streamlit-expanderHeader {{
        padding: 8px 12px !important;
        font-size: 0.85rem !important;
    }}

    /* Data density: comfortable mode (default) */
    .powertrack-comfortable [data-testid="stMetric"] {{
        padding: 20px 24px !important;
    }}

    .powertrack-comfortable .stButton button {{
        padding: 8px 24px !important;
        font-size: 0.95rem !important;
    }}

    /* Tooltip styling */
    .powertrack-tooltip {{
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        color: var(--text-muted);
        font-size: 0.75rem;
        cursor: help;
        flex-shrink: 0;
        transition: all 0.2s ease;
    }}

    .powertrack-tooltip:hover {{
        background: var(--accent-primary);
        border-color: var(--accent-primary);
        color: #ffffff;
    }}

    .powertrack-tooltip::after {{
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 0.75rem;
        color: var(--text-primary);
        white-space: nowrap;
        max-width: 280px;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 100;
        box-shadow: 0 4px 12px var(--shadow);
        pointer-events: none;
    }}

    .powertrack-tooltip::before {{
        content: '';
        position: absolute;
        bottom: 110%;
        left: 50%;
        transform: translateX(-50%);
        border: 5px solid transparent;
        border-top-color: var(--bg-card);
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 100;
    }}

    .powertrack-tooltip:hover::after,
    .powertrack-tooltip:hover::before {{
        opacity: 1;
        visibility: visible;
    }}

    .powertrack-tooltip:focus-visible {{
        outline: 2px solid var(--accent-primary);
        outline-offset: 2px;
    }}

    /* Help text styling */
    .powertrack-help-text {{
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 4px;
        line-height: 1.5;
    }}

    .powertrack-help-text strong {{
        color: var(--text-secondary);
    }}

    /* Info banner */
    .powertrack-info-banner {{
        background: var(--bg-card);
        border: 1px solid var(--border-accent);
        border-left: 4px solid var(--accent-primary);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 16px 0;
        display: flex;
        gap: 12px;
        align-items: flex-start;
    }}

    .powertrack-info-banner .icon {{
        font-size: 1.2rem;
        flex-shrink: 0;
        margin-top: 2px;
    }}

    .powertrack-info-banner .content {{
        flex: 1;
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }}

    /* Keyboard shortcut hint */
    .powertrack-kbd {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 24px;
        height: 22px;
        padding: 0 6px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: 4px;
        font-size: 0.7rem;
        font-family: ui-monospace, SFMono-Regular, monospace;
        color: var(--text-muted);
        box-shadow: 0 1px 2px var(--shadow);
    }}

    .powertrack-kbd-sequence {{
        display: inline-flex;
        gap: 4px;
    }}

    /* Keyboard shortcut overlay */
    .powertrack-shortcuts-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
    }}

    .powertrack-shortcuts-overlay.visible {{
        opacity: 1;
        visibility: visible;
    }}

    .powertrack-shortcuts-modal {{
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 24px;
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 20px 50px var(--shadow);
        transform: scale(0.95);
        transition: transform 0.2s ease;
    }}

    .powertrack-shortcuts-overlay.visible .powertrack-shortcuts-modal {{
        transform: scale(1);
    }}

    .powertrack-shortcuts-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--border-subtle);
    }}

    .powertrack-shortcuts-header h3 {{
        margin: 0;
        font-size: 1.1rem;
        color: var(--text-primary);
    }}

    .powertrack-shortcuts-close {{
        background: none;
        border: none;
        font-size: 1.5rem;
        color: var(--text-muted);
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;
        transition: all 0.2s ease;
    }}

    .powertrack-shortcuts-close:hover {{
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }}

    .powertrack-shortcuts-list {{
        display: flex;
        flex-direction: column;
        gap: 8px;
    }}

    .powertrack-shortcut-item {{
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 10px 12px;
        background: var(--bg-tertiary);
        border-radius: 8px;
        transition: all 0.2s ease;
    }}

    .powertrack-shortcut-item:hover {{
        background: var(--bg-secondary);
    }}

    .powertrack-shortcut-keys {{
        display: flex;
        gap: 4px;
        min-width: 100px;
    }}

    .powertrack-shortcut-desc {{
        flex: 1;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }}

    .powertrack-shortcut-category {{
        font-weight: 600;
        color: var(--text-primary);
        margin: 16px 0 8px 0;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    </style>
    """
