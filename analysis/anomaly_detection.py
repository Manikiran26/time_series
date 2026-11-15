"""
Unusual Consumption & Anomaly Detection Engine for PowerTrack.
Detects statistical consumption anomalies using household-specific baselines
(rolling window + day-of-week seasonal profile + IQR/Z-score thresholds).
Generates explainable severity tags, expected values, and actionable contextual insights.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


def detect_household_anomalies(
    series: pd.Series,
    window: int = 14,
    z_thresh: float = 2.2,
    iqr_factor: float = 1.75
) -> pd.DataFrame:
    """
    Detect unusual consumption days for a given household series.
    Uses a hybrid baseline:
    - 14-day rolling median as trend baseline
    - Day-of-week adjustment factor
    - Dynamic IQR and Z-score thresholding
    """
    df = pd.DataFrame({'actual_kwh': series.copy()})
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    # Day of week and rolling stats
    df['day_of_week'] = df.index.day_name()
    
    # Baseline: Rolling 14-day median (robust to prior outliers)
    rolling_median = df['actual_kwh'].rolling(window=window, min_periods=3, center=True).median()
    df['rolling_median'] = rolling_median.fillna(df['actual_kwh'].median())

    # Day-of-week multiplier
    dow_means = df.groupby('day_of_week')['actual_kwh'].mean()
    overall_mean = df['actual_kwh'].mean()
    dow_factors = (dow_means / overall_mean).to_dict()
    df['dow_factor'] = df['day_of_week'].map(dow_factors)

    # Expected baseline
    df['expected_kwh'] = np.round(df['rolling_median'] * df['dow_factor'], 2)
    df['deviation_kwh'] = np.round(df['actual_kwh'] - df['expected_kwh'], 2)
    df['deviation_pct'] = np.round((df['deviation_kwh'] / np.maximum(df['expected_kwh'], 0.5)) * 100.0, 1)

    # Rolling IQR bounds
    rolling_q25 = df['actual_kwh'].rolling(window=window*2, min_periods=7, center=True).quantile(0.25).fillna(df['actual_kwh'].quantile(0.25))
    rolling_q75 = df['actual_kwh'].rolling(window=window*2, min_periods=7, center=True).quantile(0.75).fillna(df['actual_kwh'].quantile(0.75))
    rolling_iqr = rolling_q75 - rolling_q25
    
    df['upper_bound'] = np.round(rolling_q75 + iqr_factor * rolling_iqr, 2)
    df['lower_bound'] = np.round(np.maximum(0.0, rolling_q25 - iqr_factor * rolling_iqr), 2)

    # Rolling std for z-score
    rolling_std = df['actual_kwh'].rolling(window=window, min_periods=3, center=True).std().fillna(df['actual_kwh'].std())
    df['z_score'] = np.round((df['actual_kwh'] - df['expected_kwh']) / np.maximum(rolling_std, 0.2), 2)

    # Anomaly classification
    conditions = [
        (df['actual_kwh'] > df['upper_bound']) & (df['z_score'] >= z_thresh * 1.5),
        (df['actual_kwh'] > df['upper_bound']),
        (df['actual_kwh'] < df['lower_bound']) & (df['actual_kwh'] < 0.5) & (df['expected_kwh'] > 3.0),
        (df['actual_kwh'] < df['lower_bound'])
    ]
    choices = [
        'Severe Surge',
        'Moderate Spike',
        'Vacant / Zero Consumption',
        'Unusually Low'
    ]
    df['anomaly_type'] = np.select(conditions, choices, default='Normal')
    df['is_anomaly'] = df['anomaly_type'] != 'Normal'

    # Severity rating
    sev_conditions = [
        df['anomaly_type'].isin(['Severe Surge']),
        df['anomaly_type'].isin(['Moderate Spike', 'Vacant / Zero Consumption']),
        df['anomaly_type'].isin(['Unusually Low'])
    ]
    sev_choices = ['High', 'Medium', 'Low']
    df['severity'] = np.select(sev_conditions, sev_choices, default='None')

    # Plain English explainable reason
    def explain_row(r):
        if r['anomaly_type'] == 'Severe Surge':
            return f"Extreme surge ({r['actual_kwh']:.1f} kWh vs baseline {r['expected_kwh']:.1f} kWh, +{r['deviation_pct']:.0f}%). Possible causes: prolonged AC/heating operation, water pump left on, or household gathering."
        elif r['anomaly_type'] == 'Moderate Spike':
            return f"Noticeable spike (+{r['deviation_kwh']:.1f} kWh above typical {r['day_of_week']} baseline). Indicates higher appliance utilization."
        elif r['anomaly_type'] == 'Vacant / Zero Consumption':
            return f"Near-zero load ({r['actual_kwh']:.2f} kWh). Indicates the residence was likely unoccupied or an extended grid outage occurred."
        elif r['anomaly_type'] == 'Unusually Low':
            return f"Consumption was lower than customary for this day (-{abs(r['deviation_pct']):.0f}% below baseline)."
        return "Normal household usage pattern within expected statistical variance."

    df['explanation'] = df.apply(explain_row, axis=1)

    return df


def get_recent_anomalies_summary(df_anomalies: pd.DataFrame, limit: int = 10) -> List[Dict[str, Any]]:
    """Return top recent anomalies formatted for UI display."""
    anom_rows = df_anomalies[df_anomalies['is_anomaly']].copy()
    if anom_rows.empty:
        return []

    anom_rows = anom_rows.sort_index(ascending=False).head(limit)
    summary = []
    for dt, row in anom_rows.iterrows():
        summary.append({
            'date': dt.strftime('%d %b %Y'),
            'day': row['day_of_week'],
            'actual_kwh': row['actual_kwh'],
            'expected_kwh': row['expected_kwh'],
            'deviation_kwh': row['deviation_kwh'],
            'deviation_pct': row['deviation_pct'],
            'type': row['anomaly_type'],
            'severity': row['severity'],
            'explanation': row['explanation']
        })
    return summary

