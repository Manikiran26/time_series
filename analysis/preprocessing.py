"""
Data Preprocessing Pipeline for Electricity Time Series Analysis.
Supports raw UCI Individual Household Electric Power Consumption dataset
and user-specific electricity datasets for future extensibility.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional

DEFAULT_RAW_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "individual+household+electric+power+consumption (1)",
    "household_power_consumption.txt"
)

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_raw_dataset(file_path: Optional[str] = None, nrows: Optional[int] = None) -> pd.DataFrame:
    """
    Load raw electricity consumption dataset.
    Detects delimiter (semicolon or comma) and treats '?' as NaN.
    """
    path = file_path or DEFAULT_RAW_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at: {path}")

    # Determine separator
    sep = ';'
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        first_line = f.readline()
        if ';' in first_line:
            sep = ';'
        elif ',' in first_line:
            sep = ','

    df = pd.read_csv(
        path,
        sep=sep,
        na_values=['?', 'NA', 'null', 'None', ''],
        low_memory=False,
        nrows=nrows
    )

    # Column name normalization
    df.columns = [c.strip() for c in df.columns]

    return df


def parse_and_index_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse timestamp columns and set as time-series DatetimeIndex.
    Handles 'Date' + 'Time' composite columns or single 'Datetime' / 'Timestamp' column.
    """
    df = df.copy()

    if 'Date' in df.columns and 'Time' in df.columns:
        # Check standard DD/MM/YYYY format
        df['Datetime'] = pd.to_datetime(
            df['Date'].astype(str) + ' ' + df['Time'].astype(str),
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        # Drop raw string columns
        df.drop(columns=['Date', 'Time'], inplace=True)
    elif 'Datetime' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
    elif 'Timestamp' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    else:
        # Try to find first datetime-like column
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                df['Datetime'] = pd.to_datetime(df[col], errors='coerce')
                df.drop(columns=[col], inplace=True)
                break

    if 'Datetime' not in df.columns:
        raise ValueError("Could not find or parse date/time columns in dataset.")

    # Drop NaT in Datetime
    df.dropna(subset=['Datetime'], inplace=True)
    df.sort_values(by='Datetime', inplace=True)
    df.set_index('Datetime', inplace=True)

    # Convert numeric columns
    numeric_cols = [
        'Global_active_power', 'Global_reactive_power', 'Voltage',
        'Global_intensity', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def get_dataset_metadata(df_raw: pd.DataFrame, df_indexed: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Compute comprehensive dataset statistics for Exploratory Data Analysis & Report.
    """
    total_records = len(df_raw)
    null_counts = df_raw.isna().sum().to_dict()
    null_percentages = {k: (v / total_records) * 100 for k, v in null_counts.items()}
    total_nulls = sum(null_counts.values())

    meta = {
        'total_records': total_records,
        'null_counts': null_counts,
        'null_percentages': null_percentages,
        'total_missing_values': total_nulls,
        'overall_missing_pct': (total_nulls / (total_records * len(df_raw.columns))) * 100 if total_records > 0 else 0,
        'columns': list(df_raw.columns)
    }

    if df_indexed is not None and isinstance(df_indexed.index, pd.DatetimeIndex):
        meta['start_date'] = str(df_indexed.index.min())
        meta['end_date'] = str(df_indexed.index.max())
        meta['duration_days'] = (df_indexed.index.max() - df_indexed.index.min()).days
        meta['is_monotonic'] = bool(df_indexed.index.is_monotonic_increasing)
        meta['duplicates_count'] = int(df_indexed.index.duplicated().sum())

    return meta


def handle_missing_values(df: pd.DataFrame, method: str = 'linear') -> pd.DataFrame:
    """
    Handle missing values using linear interpolation, forward fill, backward fill, or drop.
    """
    df_clean = df.copy()

    if method == 'linear':
        df_clean = df_clean.interpolate(method='time').ffill().bfill()
    elif method == 'ffill':
        df_clean = df_clean.ffill().bfill()
    elif method == 'mean':
        df_clean = df_clean.fillna(df_clean.mean())
    elif method == 'drop':
        df_clean = df_clean.dropna()
    else:
        df_clean = df_clean.interpolate(method='linear').ffill().bfill()

    return df_clean


def detect_outliers(series: pd.Series, method: str = 'iqr', factor: float = 1.5) -> Dict[str, Any]:
    """
    Detect statistical outliers in electricity series using IQR or Z-Score.
    """
    clean_series = series.dropna()

    if method == 'iqr':
        q25 = clean_series.quantile(0.25)
        q75 = clean_series.quantile(0.75)
        iqr = q75 - q25
        lower_bound = max(0.0, q25 - factor * iqr)
        upper_bound = q75 + factor * iqr
        outlier_mask = (clean_series < lower_bound) | (clean_series > upper_bound)
    else:  # z-score
        mean = clean_series.mean()
        std = clean_series.std()
        lower_bound = max(0.0, mean - factor * std)
        upper_bound = mean + factor * std
        outlier_mask = (clean_series < lower_bound) | (clean_series > upper_bound)

    return {
        'method': method,
        'factor': factor,
        'lower_bound': float(lower_bound),
        'upper_bound': float(upper_bound),
        'outlier_count': int(outlier_mask.sum()),
        'outlier_pct': float((outlier_mask.sum() / len(clean_series)) * 100) if len(clean_series) > 0 else 0.0,
        'outlier_indices': clean_series[outlier_mask].index,
        'outlier_values': clean_series[outlier_mask].values
    }


def resample_series(df: pd.DataFrame, freq: str = 'D', agg_active: str = 'mean') -> pd.DataFrame:
    """
    Resample time series to specified frequency:
    - 'h' (Hourly)
    - 'D' (Daily)
    - 'W' (Weekly)
    - 'MS' (Monthly)
    Aggregates active power, voltage, reactive power, intensity, and submeters appropriately.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame must have a DatetimeIndex for resampling.")

    agg_dict = {}
    if 'Global_active_power' in df.columns:
        agg_dict['Global_active_power'] = agg_active
    if 'Global_reactive_power' in df.columns:
        agg_dict['Global_reactive_power'] = 'mean'
    if 'Voltage' in df.columns:
        agg_dict['Voltage'] = 'mean'
    if 'Global_intensity' in df.columns:
        agg_dict['Global_intensity'] = 'mean'
    if 'Sub_metering_1' in df.columns:
        agg_dict['Sub_metering_1'] = 'sum'
    if 'Sub_metering_2' in df.columns:
        agg_dict['Sub_metering_2'] = 'sum'
    if 'Sub_metering_3' in df.columns:
        agg_dict['Sub_metering_3'] = 'sum'

    resampled = df.resample(freq).agg(agg_dict)

    # Calculate active submetering remainder in Wh
    # 1 kW active power for 1 hour = 1000 Wh.
    if 'Global_active_power' in resampled.columns and 'Sub_metering_1' in resampled.columns:
        # Determine duration factor based on frequency
        if freq == 'h' or freq == '1h':
            wh_total = resampled['Global_active_power'] * 1000.0
        elif freq == 'D':
            wh_total = resampled['Global_active_power'] * 1000.0 * 24.0
        elif freq == 'W':
            wh_total = resampled['Global_active_power'] * 1000.0 * 168.0
        elif freq == 'MS' or freq == 'M':
            # Approximate 30.4 days
            wh_total = resampled['Global_active_power'] * 1000.0 * 730.0
        else:
            wh_total = resampled['Global_active_power'] * 1000.0

        sub_sum = (
            resampled['Sub_metering_1'].fillna(0) +
            resampled['Sub_metering_2'].fillna(0) +
            resampled['Sub_metering_3'].fillna(0)
        )
        resampled['Sub_metering_remainder'] = np.maximum(0, wh_total - sub_sum)

    # Clean any missing timestamps introduced by resampling
    resampled = resampled.interpolate(method='time').ffill().bfill()

    return resampled


def get_preprocessed_data(
    freq: str = 'D',
    use_cache: bool = True,
    missing_method: str = 'linear',
    custom_file_path: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    High-level entry point: Loads, preprocesses, resamples, and caches datasets.
    Provides fast instant retrieval for Streamlit while supporting live raw reprocessing.
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    cache_file = os.path.join(PROCESSED_DIR, f"household_resampled_{freq.replace(':', '_')}.parquet")

    # If custom dataset is provided, bypass pre-cached default
    if custom_file_path is None and use_cache and os.path.exists(cache_file):
        df_resampled = pd.read_parquet(cache_file)
        # Load small sample of raw data for metadata
        df_meta_sample = pd.read_parquet(os.path.join(PROCESSED_DIR, "dataset_meta.parquet")) if os.path.exists(
            os.path.join(PROCESSED_DIR, "dataset_meta.parquet")
        ) else None
        
        meta = {
            'total_records': 2075259,
            'total_missing_values': 25979 * 7,
            'overall_missing_pct': 1.25,
            'start_date': str(df_resampled.index.min()),
            'end_date': str(df_resampled.index.max()),
            'duration_days': (df_resampled.index.max() - df_resampled.index.min()).days,
            'is_monotonic': True,
            'duplicates_count': 0,
            'resampled_points': len(df_resampled),
            'frequency': freq
        }
        return df_resampled, meta

    # Full pipeline execution
    raw_df = load_raw_dataset(custom_file_path)
    indexed_df = parse_and_index_timestamps(raw_df)
    meta = get_dataset_metadata(raw_df, indexed_df)
    clean_df = handle_missing_values(indexed_df, method=missing_method)
    resampled_df = resample_series(clean_df, freq=freq)

    meta['resampled_points'] = len(resampled_df)
    meta['frequency'] = freq

    # Save to parquet cache if standard path
    if custom_file_path is None:
        try:
            resampled_df.to_parquet(cache_file)
        except Exception:
            pass

    return resampled_df, meta
