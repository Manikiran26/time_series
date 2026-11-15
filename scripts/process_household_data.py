"""
PowerTrack Household Data Preprocessing & Validation Pipeline
Processes CEEW Mathura and Bareilly Indian Smart-Meter Dataset.
Generates clean daily and hourly time series per household,
caches fast Parquet tables, and calculates data quality metrics.
"""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RAW_CEEW_DIR = os.path.join(DATA_DIR, "ceew_smart_meter")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def process_daily_smart_meter_data():
    print("[1/3] Processing Daily Smart-Meter Records for Mathura & Bareilly...")
    
    # 1. Mathura Aggregated
    m_path = os.path.join(RAW_CEEW_DIR, "Mathura_Aggregated.tab")
    df_m = pd.read_csv(m_path, sep='\t')
    df_m['household_id'] = df_m['meter'].astype(str).str.replace('"', '').str.strip()
    df_m['city'] = 'Mathura'
    df_m['date'] = pd.to_datetime(df_m['Date'])
    df_m['consumption_kwh'] = pd.to_numeric(df_m['t_kWh'], errors='coerce')
    df_m = df_m[['household_id', 'city', 'date', 'consumption_kwh']]

    # 2. Bareilly Aggregated
    b_path = os.path.join(RAW_CEEW_DIR, "Bareilly_Aggregated.tab")
    df_b = pd.read_csv(b_path, sep='\t')
    df_b['household_id'] = df_b['meter'].astype(str).str.replace('"', '').str.strip()
    df_b['city'] = 'Bareilly'
    df_b['date'] = pd.to_datetime(df_b['Date'])
    df_b['consumption_kwh'] = pd.to_numeric(df_b['t_kWh'], errors='coerce')
    df_b = df_b[['household_id', 'city', 'date', 'consumption_kwh']]

    # Combine both cities
    df_combined = pd.concat([df_m, df_b], ignore_index=True)
    df_combined.sort_values(by=['household_id', 'date'], inplace=True)
    
    # Check duplicates
    dups = df_combined.duplicated(subset=['household_id', 'date']).sum()
    if dups > 0:
        print(f"  Warning: Found {dups} duplicate entries. Dropping duplicates keeping first...")
        df_combined.drop_duplicates(subset=['household_id', 'date'], keep='first', inplace=True)

    # Process each household to ensure regular daily time series
    household_records = []
    meta_records = []

    all_households = df_combined['household_id'].unique()
    print(f"  Found {len(all_households)} unique households across Mathura & Bareilly.")

    for hid in all_households:
        sub = df_combined[df_combined['household_id'] == hid].copy()
        city = sub['city'].iloc[0]
        sub.set_index('date', inplace=True)
        sub = sub.sort_index()

        # Check date range
        start_date = sub.index.min()
        end_date = sub.index.max()
        raw_count = len(sub)
        
        # Expected days in continuous calendar
        full_idx = pd.date_range(start=start_date, end=end_date, freq='D')
        expected_days = len(full_idx)
        
        # Reindex to regular daily frequency
        sub_regular = sub.reindex(full_idx)
        sub_regular['household_id'] = hid
        sub_regular['city'] = city
        sub_regular.index.name = 'date'

        missing_days = sub_regular['consumption_kwh'].isnull().sum()
        completeness_pct = (raw_count / expected_days) * 100.0 if expected_days > 0 else 0.0

        # Impute missing days via linear interpolation with ffill/bfill bounds
        imputed_series = sub_regular['consumption_kwh'].interpolate(method='time').ffill().bfill()
        
        # Handle negative or extreme values if any
        imputed_series = imputed_series.clip(lower=0.0)
        
        sub_regular['consumption_kwh'] = imputed_series
        sub_regular['is_imputed'] = sub['consumption_kwh'].reindex(full_idx).isnull()
        
        sub_regular.reset_index(inplace=True)
        household_records.append(sub_regular)

        # Compute household metadata
        meta_records.append({
            'household_id': hid,
            'city': city,
            'start_date': start_date,
            'end_date': end_date,
            'total_calendar_days': expected_days,
            'recorded_days': raw_count,
            'missing_days': int(missing_days),
            'completeness_pct': round(completeness_pct, 1),
            'mean_daily_kwh': round(float(imputed_series.mean()), 2),
            'std_daily_kwh': round(float(imputed_series.std()), 2),
            'min_daily_kwh': round(float(imputed_series.min()), 2),
            'median_daily_kwh': round(float(imputed_series.median()), 2),
            'max_daily_kwh': round(float(imputed_series.max()), 2),
            'data_quality_grade': 'A' if completeness_pct >= 90 else ('B' if completeness_pct >= 75 else 'C')
        })

    df_clean_daily = pd.concat(household_records, ignore_index=True)
    df_meta = pd.DataFrame(meta_records)

    # Save daily processed datasets
    daily_parquet = os.path.join(PROCESSED_DIR, "households_daily.parquet")
    meta_parquet = os.path.join(PROCESSED_DIR, "households_meta.parquet")
    df_clean_daily.to_parquet(daily_parquet, index=False)
    df_meta.to_parquet(meta_parquet, index=False)
    print(f"  Saved clean daily series: {len(df_clean_daily):,} rows to {daily_parquet}")
    print(f"  Saved metadata for {len(df_meta)} households to {meta_parquet}")

    return df_clean_daily, df_meta


def process_hourly_smart_meter_data():
    print("\n[2/3] Processing High-Frequency Hourly Readings from Mathura 2021...")
    hf_path = os.path.join(RAW_CEEW_DIR, "Mathura_2021.tab")
    if not os.path.exists(hf_path):
        print("  Mathura_2021.tab not found. Skipping hourly processing.")
        return None

    # Load high-frequency readings (3-minute interval)
    print("  Reading 3-minute smart-meter records...")
    df_hf = pd.read_csv(
        hf_path,
        sep='\t',
        usecols=['x_Timestamp', 't_kWh', 'z_Avg Voltage (Volt)', 'z_Avg Current (Amp)', 'y_Freq (Hz)', 'meter']
    )
    df_hf['household_id'] = df_hf['meter'].astype(str).str.replace('"', '').str.strip()
    df_hf['timestamp'] = pd.to_datetime(df_hf['x_Timestamp'])
    df_hf['city'] = 'Mathura'
    
    # Rename columns to standard schema
    df_hf.rename(columns={
        't_kWh': 'interval_kwh',
        'z_Avg Voltage (Volt)': 'voltage_v',
        'z_Avg Current (Amp)': 'current_a',
        'y_Freq (Hz)': 'frequency_hz'
    }, inplace=True)

    print(f"  Loaded {len(df_hf):,} 3-minute interval records across {df_hf['household_id'].nunique()} households.")

    # Aggregate to hourly resolution (1h) per household
    hourly_dfs = []
    for hid, group in df_hf.groupby('household_id'):
        group = group.sort_values(by='timestamp').set_index('timestamp')
        
        # Resample to 1h
        resampled = group.resample('1h').agg({
            'interval_kwh': 'sum',
            'voltage_v': 'mean',
            'current_a': 'mean',
            'frequency_hz': 'mean'
        })
        
        resampled['household_id'] = hid
        resampled['city'] = 'Mathura'
        # Interval energy in 1h in kWh is numerically equal to average power in kW
        resampled['power_kw'] = resampled['interval_kwh']
        resampled.rename(columns={'interval_kwh': 'hourly_kwh'}, inplace=True)
        
        # Linear interpolate any missing hours within the range
        resampled['hourly_kwh'] = resampled['hourly_kwh'].interpolate(method='time').ffill().bfill().clip(lower=0.0)
        resampled['voltage_v'] = resampled['voltage_v'].interpolate(method='time').ffill().bfill()
        resampled['current_a'] = resampled['current_a'].interpolate(method='time').ffill().bfill()
        resampled['frequency_hz'] = resampled['frequency_hz'].interpolate(method='time').ffill().bfill()
        resampled['power_kw'] = resampled['hourly_kwh']
        
        resampled.reset_index(inplace=True)
        hourly_dfs.append(resampled)

    df_hourly = pd.concat(hourly_dfs, ignore_index=True)
    hourly_parquet = os.path.join(PROCESSED_DIR, "households_hourly.parquet")
    df_hourly.to_parquet(hourly_parquet, index=False)
    print(f"  Saved clean hourly series: {len(df_hourly):,} rows to {hourly_parquet}")

    # Build 24-hour diurnal profile lookup for all households
    print("\n[3/3] Generating 24-hour diurnal load profiles...")
    df_hourly['hour'] = df_hourly['timestamp'].dt.hour
    diurnal_profile = df_hourly.groupby(['household_id', 'hour'])[['hourly_kwh', 'power_kw', 'voltage_v']].mean().reset_index()
    diurnal_parquet = os.path.join(PROCESSED_DIR, "households_diurnal_profiles.parquet")
    diurnal_profile.to_parquet(diurnal_parquet, index=False)
    print(f"  Saved 24-hour diurnal profiles to {diurnal_parquet}")

    return df_hourly


if __name__ == "__main__":
    print("=" * 70)
    print("POWERTRACK HOUSEHOLD PREPROCESSING PIPELINE")
    print("=" * 70)
    df_daily, df_meta = process_daily_smart_meter_data()
    df_hourly = process_hourly_smart_meter_data()
    print("\nPreprocessing complete! All Parquet files saved in data/processed/")
    print("=" * 70)

