"""
Peer comparison for a single household against the wider smart-meter cohort.

Compares the selected household's recent average daily consumption with the
distribution of all other meters in the same district (and the full cohort),
so a household can see where it sits relative to similar homes.
"""

from typing import Any, Dict

import numpy as np
import pandas as pd

COHORT_CACHE: Dict[str, pd.Series] = {}


def _cohort_daily_means(meta: pd.DataFrame, households_daily: pd.DataFrame) -> pd.Series:
    """Average daily kWh per household id."""
    if "household_id" in COHORT_CACHE and len(COHORT_CACHE["household_id"]) == len(households_daily):
        return COHORT_CACHE["household_id"]
    means = households_daily.groupby("household_id")["consumption_kwh"].mean()
    COHORT_CACHE["household_id"] = means
    return means


def compare_with_peers(
    household_id: str,
    meta_row: Dict[str, Any],
    df_daily: pd.DataFrame,
    households_daily: pd.DataFrame,
    households_meta: pd.DataFrame,
    window_days: int = 90,
) -> Dict[str, Any]:
    """
    Peer comparison payload for the UI.

    Returns:
        {
          "your_avg_kwh", "peer_group_label", "peer_count",
          "peer_avg_kwh", "peer_median_kwh", "peer_p25_kwh", "peer_p75_kwh",
          "pct_diff", "percentile", "verdict", "verdict_tone",
          "city_avg_kwh", "cohort_avg_kwh",
        }
    """
    window = df_daily.iloc[-window_days:] if len(df_daily) > window_days else df_daily
    yours = float(window["consumption_kwh"].mean()) if not window.empty else 0.0

    city = meta_row.get("city")
    meta = households_meta.copy()
    means = _cohort_daily_means(meta, households_daily)

    city_ids = set(meta.loc[meta["city"] == city, "household_id"])
    city_ids.discard(household_id)
    city_vals = means[means.index.isin(city_ids)].dropna()

    all_ids = set(meta["household_id"])
    all_ids.discard(household_id)
    all_vals = means[means.index.isin(all_ids)].dropna()

    peers = city_vals if len(city_vals) >= 5 else all_vals
    peer_label = f"{city} households" if len(city_vals) >= 5 else "All monitored households"

    if len(peers) == 0:
        return {
            "your_avg_kwh": round(yours, 1),
            "peer_group_label": peer_label,
            "peer_count": 0,
            "peer_avg_kwh": 0.0,
            "peer_median_kwh": 0.0,
            "peer_p25_kwh": 0.0,
            "peer_p75_kwh": 0.0,
            "pct_diff": 0.0,
            "percentile": 50,
            "verdict": "Peer comparison unavailable",
            "verdict_tone": "neutral",
            "city_avg_kwh": round(float(means[means.index.isin(city_ids)].mean()), 1) if len(city_ids) else 0.0,
            "cohort_avg_kwh": round(float(all_vals.mean()), 1) if len(all_vals) else 0.0,
        }

    peer_avg = float(peers.mean())
    pct_diff = ((yours - peer_avg) / peer_avg) * 100 if peer_avg > 0 else 0.0
    percentile = float((peers < yours).mean() * 100)

    if pct_diff <= -8:
        verdict, tone = "Well below similar homes", "good"
    elif pct_diff < 3:
        verdict, tone = "About the same as similar homes", "neutral"
    elif pct_diff < 15:
        verdict, tone = "Slightly above similar homes", "warn"
    else:
        verdict, tone = "Above similar homes", "bad"

    return {
        "your_avg_kwh": round(yours, 1),
        "peer_group_label": peer_label,
        "peer_count": int(len(peers)),
        "peer_avg_kwh": round(peer_avg, 1),
        "peer_median_kwh": round(float(peers.median()), 1),
        "peer_p25_kwh": round(float(peers.quantile(0.25)), 1),
        "peer_p75_kwh": round(float(peers.quantile(0.75)), 1),
        "pct_diff": round(pct_diff, 1),
        "percentile": round(percentile, 0),
        "verdict": verdict,
        "verdict_tone": tone,
        "city_avg_kwh": round(float(means[means.index.isin(city_ids)].mean()), 1) if len(city_ids) else 0.0,
        "cohort_avg_kwh": round(float(all_vals.mean()), 1) if len(all_vals) else 0.0,
    }
