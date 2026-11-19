import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.forecasting import get_household_forecast_pipeline

for hid in ['MH01', 'BR02']:
    res = get_household_forecast_pipeline(hid, horizon_days=7)
    tot = res['metadata']['total_observations']
    print(f"\n=======================================================")
    print(f"HOUSEHOLD {hid} ({tot} OBSERVED DAYS)")
    print(f"=======================================================")
    print(f"Train Period: {res['metadata']['train_period']}")
    print(f"Val Period:   {res['metadata']['val_period']}")
    print(f"Test Period:  {res['metadata']['test_period']}")
    print(f"Winning Model: {res['best_model']}")
    print(f"Held-Out Test Set: MAE = {res['test_metrics']['mae']} kWh | RMSE = {res['test_metrics']['rmse']} kWh | MAPE = {res['test_metrics']['mape']}%")
    print("\nCandidate Model Validation Leaderboard:")
    for m, vals in res['model_comparison'].items():
        winner_tag = "⭐ Selected Winner" if m == res['best_model'] else "Evaluated"
        print(f"  - {m:35} | MAE: {vals['mae']:.3f} kWh | RMSE: {vals['rmse']:.3f} kWh | MAPE: {vals['mape']:.1f}% | {winner_tag}")

