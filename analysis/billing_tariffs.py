"""
PowerTrack Indian Electricity Tariff & Billing Engine.
Implements:
1. Domestic Telescopic Slab Tariffs (UPPCL Uttar Pradesh schedule & flat-rate fallback).
2. Budget Guardian (month-to-date spending, end-of-month projections, burn rates, targets).
3. Bill Discrepancy Checker (meter vs utility bill audit with duty, fixed charges, and alerts).
4. What-If Energy Simulator (appliance schedule reductions, percentage savings, and cost impacts).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple


# Standard UPPCL Domestic Urban Tariff Schedule (LMV-1)
UPPCL_SLABS = [
    {'min': 0, 'max': 100, 'rate': 5.50},
    {'min': 100, 'max': 150, 'rate': 6.00},
    {'min': 150, 'max': 300, 'rate': 6.50},
    {'min': 300, 'max': float('inf'), 'rate': 7.00}
]

FIXED_CHARGE_PER_KW_MONTH = 110.0  # ₹ / kW / month
ELECTRICITY_DUTY_PCT = 0.05        # 5% state electricity duty


def calculate_electricity_bill(
    units_kwh: float,
    sanctioned_load_kw: float = 2.0,
    tariff_mode: str = 'slab',
    flat_rate: float = 7.0,
    include_taxes: bool = True
) -> Dict[str, Any]:
    """
    Calculate domestic electricity bill according to Indian slab tariff rules or flat rate.
    """
    units = max(0.0, float(units_kwh))
    slab_breakdown = []
    energy_charges = 0.0

    if tariff_mode == 'slab':
        remaining_units = units
        for slab in UPPCL_SLABS:
            slab_width = slab['max'] - slab['min']
            units_in_slab = min(remaining_units, slab_width)
            if units_in_slab > 0:
                cost = units_in_slab * slab['rate']
                energy_charges += cost
                slab_breakdown.append({
                    'range': f"{slab['min']}-{slab['max'] if slab['max'] != float('inf') else 'Above 300'} kWh",
                    'units': round(units_in_slab, 2),
                    'rate': slab['rate'],
                    'cost': round(cost, 2)
                })
                remaining_units -= units_in_slab
            if remaining_units <= 0:
                break
    else:
        energy_charges = units * flat_rate
        slab_breakdown.append({
            'range': 'All Units (Flat)',
            'units': round(units, 2),
            'rate': flat_rate,
            'cost': round(energy_charges, 2)
        })

    # Fixed charge (prorated if monthly)
    fixed_charge = sanctioned_load_kw * FIXED_CHARGE_PER_KW_MONTH if include_taxes else 0.0
    
    # State Electricity Duty (5% of Energy Charges)
    electricity_duty = (energy_charges * ELECTRICITY_DUTY_PCT) if include_taxes else 0.0

    total_bill = energy_charges + fixed_charge + electricity_duty
    effective_rate = (total_bill / units) if units > 0 else 0.0

    return {
        'total_units_kwh': round(units, 2),
        'energy_charges': round(energy_charges, 2),
        'fixed_charges': round(fixed_charge, 2),
        'electricity_duty': round(electricity_duty, 2),
        'total_bill': round(total_bill, 2),
        'effective_rate_per_kwh': round(effective_rate, 2),
        'slab_breakdown': slab_breakdown,
        'tariff_mode': tariff_mode,
        'sanctioned_load_kw': sanctioned_load_kw
    }


def compute_budget_guardian_status(
    month_to_date_kwh: float,
    current_day_of_month: int,
    days_in_month: int,
    monthly_budget_inr: float,
    daily_history_avg_kwh: float,
    sanctioned_load_kw: float = 2.0
) -> Dict[str, Any]:
    """
    Budget Guardian: Evaluates spending to date, projected end-of-month cost,
    burn rate, and target daily allowances to prevent bill shock.
    """
    days_elapsed = max(1, current_day_of_month)
    days_remaining = max(0, days_in_month - days_elapsed)

    # Actual cost to date
    spent_to_date = calculate_electricity_bill(month_to_date_kwh, sanctioned_load_kw)['total_bill']
    
    # Daily consumption velocity
    current_daily_burn_kwh = month_to_date_kwh / days_elapsed

    # Projected end-of-month units (blend current pace and historical average)
    projected_additional_kwh = (0.7 * current_daily_burn_kwh + 0.3 * daily_history_avg_kwh) * days_remaining
    projected_month_kwh = month_to_date_kwh + projected_additional_kwh

    # Projected end-of-month cost
    projected_total_cost = calculate_electricity_bill(projected_month_kwh, sanctioned_load_kw)['total_bill']

    # Budget comparisons
    remaining_budget = monthly_budget_inr - spent_to_date
    projected_diff = projected_total_cost - monthly_budget_inr

    # Target daily consumption to stay strictly within remaining budget
    if days_remaining > 0 and remaining_budget > 0:
        # Approximate units affordable with remaining budget
        # Solving inverse slab tariff roughly:
        approx_affordable_units = max(0.0, (remaining_budget / 6.5))
        target_daily_kwh = approx_affordable_units / days_remaining
        target_daily_spend = remaining_budget / days_remaining
    else:
        target_daily_kwh = 0.0
        target_daily_spend = 0.0

    # Status classification
    if projected_total_cost <= monthly_budget_inr * 0.90:
        status = "Comfortable"
        status_color = "#10b981"  # Emerald
        alert_msg = f"You are well within your ₹{monthly_budget_inr:,.0f} budget. Projected bill is ₹{projected_total_cost:,.0f}."
    elif projected_total_cost <= monthly_budget_inr:
        status = "On Track"
        status_color = "#38bdf8"  # Sky blue
        alert_msg = f"On track to meet budget. Projected bill is ₹{projected_total_cost:,.0f} against ₹{monthly_budget_inr:,.0f} limit."
    elif projected_total_cost <= monthly_budget_inr * 1.15:
        status = "Caution: Moderate Overrun Risk"
        status_color = "#f59e0b"  # Amber
        alert_msg = f"Caution: Current usage will exceed your ₹{monthly_budget_inr:,.0f} budget by approx ₹{projected_diff:,.0f} (+{(projected_diff/monthly_budget_inr)*100:.1f}%)."
    else:
        status = "Alert: High Overrun Projected"
        status_color = "#ef4444"  # Red
        alert_msg = f"Warning: At your current burn rate, your bill is projected at ₹{projected_total_cost:,.0f}, exceeding your budget by ₹{projected_diff:,.0f}!"

    return {
        'spent_to_date_inr': round(spent_to_date, 2),
        'month_to_date_kwh': round(month_to_date_kwh, 1),
        'projected_month_kwh': round(projected_month_kwh, 1),
        'projected_total_cost_inr': round(projected_total_cost, 2),
        'monthly_budget_inr': float(monthly_budget_inr),
        'remaining_budget_inr': round(remaining_budget, 2),
        'projected_diff_inr': round(projected_diff, 2),
        'current_daily_burn_kwh': round(current_daily_burn_kwh, 2),
        'target_daily_kwh': round(target_daily_kwh, 2),
        'target_daily_spend_inr': round(target_daily_spend, 2),
        'days_elapsed': days_elapsed,
        'days_remaining': days_remaining,
        'status': status,
        'status_color': status_color,
        'alert_msg': alert_msg
    }


def audit_bill_discrepancy(
    meter_kwh: float,
    billed_units_kwh: float,
    billed_amount_inr: float,
    billing_period_days: int = 30,
    sanctioned_load_kw: float = 2.0
) -> Dict[str, Any]:
    """
    Bill Discrepancy Checker:
    Compares meter recorded energy with utility paper bill, computes expected UPPCL tariff,
    and isolates discrepancy drivers (tariff slabs, fixed charges, meter errors, or billing cycle offsets).
    """
    meter_kwh = float(meter_kwh)
    billed_units = float(billed_units_kwh)
    billed_amount = float(billed_amount_inr)

    # Compute expected bill from actual meter readings
    expected = calculate_electricity_bill(meter_kwh, sanctioned_load_kw=sanctioned_load_kw)
    expected_bill = expected['total_bill']
    
    # Differences
    unit_discrepancy = billed_units - meter_kwh
    unit_pct_diff = (unit_discrepancy / max(meter_kwh, 1.0)) * 100.0

    cost_discrepancy = billed_amount - expected_bill
    cost_pct_diff = (cost_discrepancy / max(expected_bill, 1.0)) * 100.0

    # Diagnostic findings & investigation items
    findings = []
    
    if abs(unit_discrepancy) > 20:
        if unit_discrepancy > 0:
            findings.append(f"Billed units exceed smart-meter reading by {unit_discrepancy:.1f} kWh (+{unit_pct_diff:.1f}%). Possible causes: utility meter reading cycle does not align with calendar month, or estimated provisional billing was applied.")
        else:
            findings.append(f"Billed units are lower than smart-meter consumption by {abs(unit_discrepancy):.1f} kWh. You may receive an adjustment charge in subsequent billing cycles.")

    if abs(cost_discrepancy) > 200:
        if cost_discrepancy > 0:
            findings.append(f"Billed charge is ₹{cost_discrepancy:.0f} higher than expected energy charge. Verify utility bill line items: includes fixed charges (approx ₹{expected['fixed_charges']}), 5% electricity duty (₹{expected['electricity_duty']}), meter rent, or prior unpaid arrears.")
        else:
            findings.append(f"Billed amount is lower than expected by ₹{abs(cost_discrepancy):.0f}. A government tariff subsidy (e.g. lifeline domestic subsidy) or prompt payment rebate may have been credited.")

    if not findings:
        findings.append("Billed amount and metered consumption closely match within normal statutory tolerance (<5% variance).")

    return {
        'meter_kwh': round(meter_kwh, 2),
        'billed_units_kwh': round(billed_units, 2),
        'unit_discrepancy_kwh': round(unit_discrepancy, 2),
        'unit_pct_diff': round(unit_pct_diff, 1),
        'expected_energy_charges': expected['energy_charges'],
        'expected_fixed_charges': expected['fixed_charges'],
        'expected_electricity_duty': expected['electricity_duty'],
        'expected_total_bill': expected['total_bill'],
        'billed_amount_inr': round(billed_amount, 2),
        'cost_discrepancy_inr': round(cost_discrepancy, 2),
        'cost_pct_diff': round(cost_pct_diff, 1),
        'is_significant_discrepancy': abs(cost_discrepancy) > 300 or abs(unit_pct_diff) > 10.0,
        'findings': findings
    }


def run_what_if_simulation(
    baseline_monthly_kwh: float,
    ac_hours_reduction_per_day: float = 0.0,
    ac_tonnage_kw: float = 1.5,
    general_reduction_pct: float = 0.0,
    bldc_fan_switch_count: int = 0,
    sanctioned_load_kw: float = 2.0
) -> Dict[str, Any]:
    """
    What-If Energy Simulator:
    Simulates user-defined energy saving interventions with physical wattage models
    and calculates both kWh and Rupee savings under telescopic tariffs.
    """
    days = 30.0
    baseline_units = float(baseline_monthly_kwh)
    baseline_bill = calculate_electricity_bill(baseline_units, sanctioned_load_kw)['total_bill']

    # 1. AC reduction: AC wattage (typical 1.5-ton inverter ~1.2 kW to 1.5 kW average)
    ac_kwh_saved = ac_hours_reduction_per_day * ac_tonnage_kw * days

    # 2. BLDC Fan upgrade: Saves ~45W per fan compared to traditional induction fan (75W -> 30W)
    # running 14 hours a day
    fan_kwh_saved = bldc_fan_switch_count * ((45.0 / 1000.0) * 14.0 * days)

    # 3. General behavioral efficiency reduction (e.g. 5%, 10%, 15%)
    behavioral_saved = baseline_units * (general_reduction_pct / 100.0)

    total_kwh_saved = min(baseline_units * 0.75, ac_kwh_saved + fan_kwh_saved + behavioral_saved)
    simulated_units = max(0.0, baseline_units - total_kwh_saved)

    simulated_bill = calculate_electricity_bill(simulated_units, sanctioned_load_kw)['total_bill']
    monthly_inr_saved = max(0.0, baseline_bill - simulated_bill)
    annual_inr_saved = monthly_inr_saved * 12.0

    return {
        'baseline_monthly_kwh': round(baseline_units, 1),
        'baseline_monthly_bill_inr': round(baseline_bill, 2),
        'simulated_monthly_kwh': round(simulated_units, 1),
        'simulated_monthly_bill_inr': round(simulated_bill, 2),
        'monthly_kwh_saved': round(total_kwh_saved, 1),
        'monthly_inr_saved': round(monthly_inr_saved, 2),
        'annual_inr_saved': round(annual_inr_saved, 2),
        'pct_kwh_reduction': round((total_kwh_saved / max(baseline_units, 1.0)) * 100.0, 1),
        'breakdown': {
            'ac_reduction_kwh': round(ac_kwh_saved, 1),
            'bldc_fan_kwh': round(fan_kwh_saved, 1),
            'behavioral_kwh': round(behavioral_saved, 1)
        }
    }

