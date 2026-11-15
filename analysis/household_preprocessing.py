"""
Household-level Preprocessing and Access Layer.
Loads and caches processed smart-meter series from Mathura and Bareilly (CEEW Dataverse),
providing seamless household filtering, chronological slicing, and metadata queries.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DAILY_FILE = os.path.join(PROCESSED_DIR, "households_daily.parquet")
HOURLY_FILE = os.path.join(PROCESSED_DIR, "households_hourly.parquet")
META_FILE = os.path.join(PROCESSED_DIR, "households_meta.parquet")
DIURNAL_FILE = os.path.join(PROCESSED_DIR, "households_diurnal_profiles.parquet")


def load_all_households_meta() -> pd.DataFrame:
    """Load metadata table for all households across Mathura and Bareilly."""
    if not os.path.exists(META_FILE):
        from scripts.process_household_data import process_daily_smart_meter_data
        _, df_meta = process_daily_smart_meter_data()
        return df_meta
    return pd.read_parquet(META_FILE)


def get_available_households(city_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return list of available households with city and date range."""
    df_meta = load_all_households_meta()
    if city_filter and city_filter != "All Cities":
        df_meta = df_meta[df_meta['city'] == city_filter]
    
    households = []
    for _, row in df_meta.iterrows():
        households.append({
            'household_id': row['household_id'],
            'city': row['city'],
            'label': f"{row['household_id']} ({row['city']}) — {row['recorded_days']} days (Quality: {row['data_quality_grade']})",
            'start_date': str(row['start_date'])[:10],
            'end_date': str(row['end_date'])[:10],
            'recorded_days': row['recorded_days'],
            'mean_kwh': row['mean_daily_kwh'],
            'quality_grade': row['data_quality_grade']
        })
    return households


def load_household_daily_series(
    household_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load clean, continuous daily consumption series for a specific household.
    Returns DataFrame indexed by date and a metadata dictionary.
    """
    if not os.path.exists(DAILY_FILE):
        from scripts.process_household_data import process_daily_smart_meter_data
        df_daily, _ = process_daily_smart_meter_data()
    else:
        df_daily = pd.read_parquet(DAILY_FILE)

    sub = df_daily[df_daily['household_id'] == household_id].copy()
    if sub.empty:
        raise ValueError(f"Household ID '{household_id}' not found in smart-meter database.")

    sub['date'] = pd.to_datetime(sub['date'])
    sub.sort_values(by='date', inplace=True)
    sub.set_index('date', inplace=True)

    # Date range filtering
    if start_date:
        sub = sub[sub.index >= pd.to_datetime(start_date)]
    if end_date:
        sub = sub[sub.index <= pd.to_datetime(end_date)]

    city = sub['city'].iloc[0] if not sub.empty else "Unknown"

    meta = {
        'household_id': household_id,
        'city': city,
        'start_date': str(sub.index.min())[:10] if not sub.empty else None,
        'end_date': str(sub.index.max())[:10] if not sub.empty else None,
        'total_days': len(sub),
        'mean_daily_kwh': float(sub['consumption_kwh'].mean()) if not sub.empty else 0.0,
        'std_daily_kwh': float(sub['consumption_kwh'].std()) if not sub.empty else 0.0,
        'min_daily_kwh': float(sub['consumption_kwh'].min()) if not sub.empty else 0.0,
        'max_daily_kwh': float(sub['consumption_kwh'].max()) if not sub.empty else 0.0,
        'imputed_days': int(sub['is_imputed'].sum()) if 'is_imputed' in sub.columns else 0,
        'data_source': "CEEW Smart Meter Study (Harvard Dataverse DOI:10.7910/DVN/GOCHJH)"
    }

    return sub, meta


def load_household_hourly_series(household_id: str) -> Optional[pd.DataFrame]:
    """
    Load hourly smart-meter readings if available for this household.
    Falls back to synthetic diurnal scaling based on daily values if not in high-frequency set.
    """
    if os.path.exists(HOURLY_FILE):
        df_hourly = pd.read_parquet(HOURLY_FILE)
        sub = df_hourly[df_hourly['household_id'] == household_id].copy()
        if not sub.empty:
            sub['timestamp'] = pd.to_datetime(sub['timestamp'])
            sub.sort_values(by='timestamp', inplace=True)
            sub.set_index('timestamp', inplace=True)
            return sub

    # If this household is not in the Mathura 2021 high-frequency file,
    # generate an empirically calibrated 24-hour hourly series using the diurnal profile template
    df_daily, _ = load_household_daily_series(household_id)
    if df_daily.empty:
        return None

    # Load typical diurnal weights
    if os.path.exists(DIURNAL_FILE):
        df_diurnal = pd.read_parquet(DIURNAL_FILE)
        weights = df_diurnal.groupby('hour')['hourly_kwh'].mean()
        norm_weights = weights / weights.sum()
    else:
        # Standard residential evening-peaking weights
        norm_weights = pd.Series([
            0.025, 0.022, 0.020, 0.020, 0.022, 0.028,
            0.038, 0.045, 0.048, 0.046, 0.044, 0.042,
            0.040, 0.038, 0.036, 0.038, 0.042, 0.052,
            0.075, 0.088, 0.085, 0.075, 0.052, 0.038
        ], index=range(24))

    # Construct hourly series for the last 60 days
    recent_daily = df_daily.iloc[-60:].copy()
    hourly_records = []
    
    for dt, row in recent_daily.iterrows():
        day_kwh = row['consumption_kwh']
        for hr in range(24):
            hr_timestamp = dt + pd.Timedelta(hours=hr)
            hr_kwh = float(day_kwh * norm_weights[hr])
            hourly_records.append({
                'timestamp': hr_timestamp,
                'household_id': household_id,
                'city': row['city'],
                'hourly_kwh': hr_kwh,
                'power_kw': hr_kwh,
                'voltage_v': 230.0 + np.random.normal(0, 4.0),
                'current_a': max(0.1, hr_kwh * 1000.0 / 230.0),
                'frequency_hz': 50.0 + np.random.normal(0, 0.05)
            })

    df_synth_hourly = pd.DataFrame(hourly_records).set_index('timestamp')
    return df_synth_hourly

