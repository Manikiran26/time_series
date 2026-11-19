"""
End-Use Energy Attribution for individual households.

Smart meters record a single aggregate load per interval, so end-use shares are
recovered by attributing each hour's measured energy to appliance categories
using the shape of the household's own diurnal profile. This is a documented
profile-based attribution, not submetering.

Categories follow typical Indian urban residential usage:
  Cooling (AC), Lighting, Refrigeration, Water Heating, Entertainment & Electronics,
  Cooking & Kitchen, Laundry & Other.

The attribution weights below encode the hours during which each category is
typically active; the weights are normalised per hour so no energy is invented.
"""

from typing import Any, Dict

import numpy as np
import pandas as pd

CATEGORY_META: Dict[str, Dict[str, str]] = {
    "Cooling (AC)": {"icon": "❄️", "color": "#38bdf8"},
    "Lighting": {"icon": "💡", "color": "#facc15"},
    "Refrigeration": {"icon": "🧊", "color": "#818cf8"},
    "Water Heating": {"icon": "♨️", "color": "#fb7185"},
    "Entertainment": {"icon": "📺", "color": "#a78bfa"},
    "Cooking & Kitchen": {"icon": "🍳", "color": "#fb923c"},
    "Laundry & Other": {"icon": "🧺", "color": "#34d399"},
}

# Activity weight per hour of day (0-23) for each category.
_ACTIVITY = {
    "Cooling (AC)":      [0.5, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.5, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 0.9, 0.9, 0.9, 0.9, 1.0, 1.0, 1.0, 0.8],
    "Lighting":          [0.2, 0.15, 0.1, 0.1, 0.15, 0.5, 0.9, 0.9, 0.6, 0.3, 0.25, 0.25, 0.25, 0.25, 0.3, 0.4, 0.7, 0.9, 1.0, 1.0, 0.95, 0.8, 0.6, 0.35],
    "Refrigeration":     [1.0] * 24,
    "Water Heating":     [0.1, 0.1, 0.1, 0.1, 0.3, 1.0, 1.0, 0.8, 0.3, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.2, 0.4, 0.5, 0.4, 0.2, 0.1, 0.1],
    "Entertainment":     [0.1, 0.05, 0.05, 0.05, 0.05, 0.1, 0.3, 0.5, 0.5, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.5, 0.6, 0.8, 1.0, 1.0, 0.95, 0.8, 0.5, 0.25],
    "Cooking & Kitchen": [0.05, 0.05, 0.05, 0.05, 0.1, 0.6, 0.9, 0.8, 0.3, 0.2, 0.2, 0.5, 0.8, 0.6, 0.2, 0.2, 0.4, 0.7, 0.9, 0.9, 0.6, 0.3, 0.1, 0.05],
    "Laundry & Other":   [0.1, 0.05, 0.05, 0.05, 0.05, 0.2, 0.4, 0.6, 0.7, 0.7, 0.7, 0.6, 0.5, 0.5, 0.5, 0.5, 0.4, 0.4, 0.4, 0.4, 0.3, 0.2, 0.15, 0.1],
}

# Seasonal cooling multiplier by month (Indian summer drives AC use).
_COOLING_MONTH_FACTOR = {
    1: 0.15, 2: 0.20, 3: 0.45, 4: 0.80, 5: 1.00, 6: 1.00,
    7: 0.90, 8: 0.85, 9: 0.75, 10: 0.55, 11: 0.25, 12: 0.15,
}

# India grid emission factor (CEA baseline, kg CO2 per kWh).
CO2_KG_PER_KWH = 0.71


def estimate_end_use_breakdown(
    df_daily: pd.DataFrame,
    df_hourly: Optional[pd.DataFrame] = None,
    total_kwh: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Attribute measured energy to appliance categories.

    Returns a list ordered by energy descending:
        [{category, icon, color, kwh, pct, share_note}, ...]
    Total kWh across categories equals the measured total for the period.
    """
    if df_daily is None or df_daily.empty:
        return []

    total = float(total_kwh) if total_kwh is not None else float(df_daily["consumption_kwh"].sum())
    if total <= 0:
        return []

    profile = _hourly_profile(df_hourly)
    if profile is None:
        # No hourly telemetry: use a typical urban residential diurnal shape.
        profile = pd.Series(
            [0.025, 0.022, 0.020, 0.020, 0.022, 0.028, 0.038, 0.045, 0.048, 0.046,
             0.044, 0.042, 0.042, 0.040, 0.038, 0.036, 0.038, 0.042, 0.052, 0.085,
             0.085, 0.075, 0.052, 0.038],
            index=range(24),
        )

    hourly_share = (profile / profile.sum()).values
    cooling_factor = _monthly_share(df_daily)

    # Weight each category per hour, then marginalise over the measured profile.
    raw: Dict[str, float] = {}
    for cat, weights in _ACTIVITY.items():
        w = np.array(weights, dtype=float)
        if cat == "Cooling (AC)":
            w = w * cooling_factor
        raw[cat] = float(np.dot(hourly_share, w))

    # Base load floor: refrigeration is a small but always-present share.
    if raw.get("Refrigeration", 0.0) < 0.06:
        raw["Refrigeration"] = 0.06

    total_weight = sum(raw.values())
    if total_weight <= 0:
        return []

    results = []
    for cat, weight in raw.items():
        pct = weight / total_weight
        results.append({
            "category": cat,
            "icon": CATEGORY_META[cat]["icon"],
            "color": CATEGORY_META[cat]["color"],
            "kwh": round(total * pct, 1),
            "pct": round(pct * 100, 1),
        })

    results.sort(key=lambda r: r["kwh"], reverse=True)
    return results


def estimate_carbon(category_kwh: float) -> float:
    """Estimated CO2 (kg) for a given energy amount."""
    return round(float(category_kwh) * CO2_KG_PER_KWH, 1)
""", target=open("D:\\time-series-project\\analysis\\end_use.py", "w"))