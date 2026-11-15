"""
Comprehensive integration test suite for PowerTrack:
1. Available households & data querying
2. Household daily and hourly series loading
3. Time series forecasting pipeline (Naive, MA, Holt-Winters, ARIMA, SARIMA)
4. Anomaly and unusual consumption detection
5. Tariff calculation and UPPCL slab accuracy
6. Budget Guardian state and projection
7. Bill Discrepancy Checker
8. What-If Energy Simulator
"""
import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from analysis.forecasting import get_household_forecast_pipeline
from analysis.household_preprocessing import get_available_households, load_household_daily_series, load_household_hourly_series
from analysis.anomaly_detection import detect_household_anomalies, get_recent_anomalies_summary
from analysis.billing_tariffs import (
    calculate_electricity_bill,
    compute_budget_guardian_status,
    audit_bill_discrepancy,
    run_what_if_simulation
)

def run_all_tests():
    print("=" * 70)
    print("RUNNING COMPREHENSIVE POWERTRACK INTEGRATION TESTS")
    print("=" * 70)

    # 1. Household Discovery
    print("\n[Test 1] Testing Household Discovery & Metadata...")
    households = get_available_households()
    assert len(households) >= 80, f"Expected >= 80 households, found {len(households)}"
    print(f"  Passed! Found {len(households)} households across Mathura & Bareilly.")

    # 2. Loading Daily & Hourly Series
    print("\n[Test 2] Testing Series Loading for MH01 and BR02...")
    df_m, meta_m = load_household_daily_series('MH01')
    assert len(df_m) > 400, "MH01 should have >400 records"
    assert meta_m['city'] == 'Mathura', f"Expected Mathura, got {meta_m['city']}"

    df_b, meta_b = load_household_daily_series('BR02')
    assert len(df_b) > 400, "BR02 should have >400 records"
    assert meta_b['city'] == 'Bareilly', f"Expected Bareilly, got {meta_b['city']}"
    print(f"  Passed! MH01: {len(df_m)} days, BR02: {len(df_b)} days.")

    df_hourly = load_household_hourly_series('MH01')
    assert df_hourly is not None and len(df_hourly) > 24, "Hourly series should be populated"
    print(f"  Passed! MH01 Hourly Series: {len(df_hourly)} hours.")

    # 3. Forecasting Pipeline
    print("\n[Test 3] Testing Forecasting Pipeline on MH01...")
    fc = get_household_forecast_pipeline('MH01', horizon_days=7)
    assert fc['best_model'] is not None, "Best model not selected"
    assert 'rmse' in fc['test_metrics'], "Test metrics missing RMSE"
    assert len(fc['future_forecast']) == 7, f"Expected 7 forecast days, got {len(fc['future_forecast'])}"
    print(f"  Passed! Best model: {fc['best_model']}, Test RMSE: {fc['test_metrics']['rmse']}")

    # 4. Anomaly Detection
    print("\n[Test 4] Testing Anomaly Detection on MH01...")
    anomalies = detect_household_anomalies(df_m['consumption_kwh'])
    assert 'anomaly_type' in anomalies.columns, "Missing anomaly_type column"
    anom_count = int(anomalies['is_anomaly'].sum())
    recent_anom = get_recent_anomalies_summary(anomalies, limit=5)
    print(f"  Passed! Found {anom_count} anomalous days. Sample anomaly: {recent_anom[0] if recent_anom else 'None'}")

    # 5. Billing Engine & UPPCL Telescopic Slabs
    print("\n[Test 5] Testing UPPCL Tariff Slabs...")
    bill_100 = calculate_electricity_bill(100, sanctioned_load_kw=2.0)
    # Energy: 100 * 5.50 = 550. Fixed: 2 * 110 = 220. Duty: 550 * 0.05 = 27.50. Total = 797.50
    assert abs(bill_100['energy_charges'] - 550.0) < 0.01, f"Expected 550, got {bill_100['energy_charges']}"
    assert abs(bill_100['total_bill'] - 797.50) < 0.01, f"Expected 797.50, got {bill_100['total_bill']}"

    bill_250 = calculate_electricity_bill(250, sanctioned_load_kw=2.0)
    # S1: 100*5.5=550; S2: 50*6.0=300; S3: 100*6.5=650 -> Energy: 1500. Fixed: 220. Duty: 75 -> 1795.0
    assert abs(bill_250['energy_charges'] - 1500.0) < 0.01, f"Expected 1500, got {bill_250['energy_charges']}"
    print(f"  Passed! 100 kWh Bill: ₹{bill_100['total_bill']}, 250 kWh Bill: ₹{bill_250['total_bill']}")

    # 6. Budget Guardian
    print("\n[Test 6] Testing Budget Guardian...")
    bg = compute_budget_guardian_status(
        month_to_date_kwh=120.0,
        current_day_of_month=15,
        days_in_month=30,
        monthly_budget_inr=2000.0,
        daily_history_avg_kwh=8.0
    )
    assert 'projected_total_cost_inr' in bg, "Missing projected_total_cost_inr"
    assert 'status' in bg, "Missing status"
    print(f"  Passed! Budget: ₹2,000, Projected Bill: ₹{bg['projected_total_cost_inr']}, Status: {bg['status']}")

    # 7. Bill Discrepancy Checker
    print("\n[Test 7] Testing Bill Discrepancy Checker...")
    disc = audit_bill_discrepancy(
        meter_kwh=200.0,
        billed_units_kwh=260.0,
        billed_amount_inr=2300.0
    )
    assert disc['is_significant_discrepancy'], "Should detect discrepancy"
    assert len(disc['findings']) > 0, "Should generate findings"
    print(f"  Passed! Discrepancy: ₹{disc['cost_discrepancy_inr']}, Findings: {disc['findings'][0]}")

    # 8. What-If Simulator
    print("\n[Test 8] Testing What-If Simulator...")
    sim = run_what_if_simulation(
        baseline_monthly_kwh=350.0,
        ac_hours_reduction_per_day=2.0,
        general_reduction_pct=10.0,
        bldc_fan_switch_count=3
    )
    assert sim['monthly_kwh_saved'] > 0, "Should save kWh"
    assert sim['monthly_inr_saved'] > 0, "Should save INR"
    print(f"  Passed! Monthly Saved: {sim['monthly_kwh_saved']} kWh (₹{sim['monthly_inr_saved']}), Annual: ₹{sim['annual_inr_saved']}")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
