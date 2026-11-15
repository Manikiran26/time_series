"""
Audit script for CEEW Mathura and Bareilly Indian Smart-Meter Dataset
as well as the previous electricity_bill_dataset.csv.
"""
import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ceew_smart_meter")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def audit_datasets():
    print("=" * 70)
    print("STAGE 1 & 2: DATASET AUDIT AND VALIDATION REPORT")
    print("=" * 70)

    # 1. Inspect existing electricity_bill_dataset.csv
    old_csv_path = os.path.join(ROOT_DIR, "electricity_bill_dataset.csv")
    if os.path.exists(old_csv_path):
        df_old = pd.read_csv(old_csv_path)
        print(f"\n[1] Existing File: electricity_bill_dataset.csv")
        print(f"  - Rows: {len(df_old):,}, Columns: {len(df_old.columns)}")
        print(f"  - Columns: {list(df_old.columns)}")
        print(f"  - Cities: {df_old['City'].unique()[:5]}... ({df_old['City'].nunique()} unique)")
        print(f"  - Null values: {df_old.isnull().sum().to_dict()}")
        
        # Check formula: MonthlyHours * TariffRate vs ElectricityBill
        calculated_bill = df_old['MonthlyHours'] * df_old['TariffRate']
        diff = (df_old['ElectricityBill'] - calculated_bill).abs()
        max_diff = diff.max()
        print(f"  - Bill Verification: Max |ElectricityBill - (MonthlyHours * TariffRate)| = {max_diff:.4f}")
        print(f"  - Household identifier: None present (only categorical appliances, city, company, month integer).")
        print(f"  - Timestamp: No timestamp, only month integer (1-12).")
        print(f"  - Assessment: Unsuitable for personalized time series forecasting, but valuable for appliance baseline profiling.")

    # 2. Inspect Mathura Aggregated
    mathura_agg_path = os.path.join(DATA_DIR, "Mathura_Aggregated.tab")
    if os.path.exists(mathura_agg_path):
        df_m = pd.read_csv(mathura_agg_path, sep='\t')
        df_m['meter'] = df_m['meter'].astype(str).str.replace('"', '').str.strip()
        df_m['Date'] = pd.to_datetime(df_m['Date'])
        print(f"\n[2] Mathura Aggregated Daily Dataset (CEEW Dataverse)")
        print(f"  - Rows: {len(df_m):,}, Columns: {list(df_m.columns)}")
        print(f"  - Unique Households / Meters: {df_m['meter'].nunique()} ({sorted(df_m['meter'].unique())[:5]}...)")
        print(f"  - Date Range: {df_m['Date'].min().strftime('%Y-%m-%d')} to {df_m['Date'].max().strftime('%Y-%m-%d')}")
        print(f"  - Duration: {(df_m['Date'].max() - df_m['Date'].min()).days} days (~2.5 years)")
        print(f"  - Nulls: {df_m.isnull().sum().to_dict()}")
        print(f"  - Consumption (t_kWh) stats: min={df_m['t_kWh'].min():.3f}, mean={df_m['t_kWh'].mean():.3f}, median={df_m['t_kWh'].median():.3f}, max={df_m['t_kWh'].max():.3f}")
        
        # Meter observation counts
        obs_per_meter = df_m.groupby('meter')['Date'].count()
        print(f"  - Observations per meter: min={obs_per_meter.min()}, median={obs_per_meter.median():.0f}, max={obs_per_meter.max()}")

    # 3. Inspect Bareilly Aggregated
    bareilly_agg_path = os.path.join(DATA_DIR, "Bareilly_Aggregated.tab")
    if os.path.exists(bareilly_agg_path):
        df_b = pd.read_csv(bareilly_agg_path, sep='\t')
        df_b['meter'] = df_b['meter'].astype(str).str.replace('"', '').str.strip()
        df_b['Date'] = pd.to_datetime(df_b['Date'])
        print(f"\n[3] Bareilly Aggregated Daily Dataset (CEEW Dataverse)")
        print(f"  - Rows: {len(df_b):,}, Columns: {list(df_b.columns)}")
        print(f"  - Unique Households / Meters: {df_b['meter'].nunique()} ({sorted(df_b['meter'].unique())[:5]}...)")
        print(f"  - Date Range: {df_b['Date'].min().strftime('%Y-%m-%d')} to {df_b['Date'].max().strftime('%Y-%m-%d')}")
        print(f"  - Duration: {(df_b['Date'].max() - df_b['Date'].min()).days} days (~2.3 years)")
        print(f"  - Nulls: {df_b.isnull().sum().to_dict()}")
        print(f"  - Consumption (t_kWh) stats: min={df_b['t_kWh'].min():.3f}, mean={df_b['t_kWh'].mean():.3f}, median={df_b['t_kWh'].median():.3f}, max={df_b['t_kWh'].max():.3f}")
        
        obs_per_meter_b = df_b.groupby('meter')['Date'].count()
        print(f"  - Observations per meter: min={obs_per_meter_b.min()}, median={obs_per_meter_b.median():.0f}, max={obs_per_meter_b.max()}")

    # 4. Inspect High-Frequency Mathura 2021
    mathura_hf_path = os.path.join(DATA_DIR, "Mathura_2021.tab")
    if os.path.exists(mathura_hf_path):
        df_hf = pd.read_csv(mathura_hf_path, sep='\t', nrows=200000)
        df_hf['meter'] = df_hf['meter'].astype(str).str.replace('"', '').str.strip()
        df_hf['x_Timestamp'] = pd.to_datetime(df_hf['x_Timestamp'])
        print(f"\n[4] Mathura 2021 High-Frequency Smart Meter Dataset (CEEW Dataverse)")
        print(f"  - Sample Rows: {len(df_hf):,}")
        print(f"  - Columns: {list(df_hf.columns)}")
        print(f"  - Sampling interval: 3 minutes")
        print(f"  - Meters in sample: {df_hf['meter'].nunique()} ({df_hf['meter'].unique()})")
        print(f"  - Date Range in sample: {df_hf['x_Timestamp'].min()} to {df_hf['x_Timestamp'].max()}")
        print(f"  - Metrics: Interval Energy (t_kWh), Voltage (Volt), Current (Amp), Frequency (Hz)")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    audit_datasets()

