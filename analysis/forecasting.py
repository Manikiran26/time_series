"""
Household-Level Electricity Consumption Forecasting Engine.
Implements classical time-series models (Naive, Moving Average, Exponential Smoothing, ARIMA, SARIMA)
with strict chronological Train-Validation-Test splitting, preventing data leakage.
Computes MAE, RMSE, and MAPE, selects the best model on validation, evaluates on held-out test set,
and generates multi-horizon out-of-sample forecasts with 95% prediction intervals.
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate MAE, RMSE, and bounded MAPE."""
    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()
    
    # Clip predictions to non-negative
    y_pred = np.maximum(0.0, y_pred)
    
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    
    # Bounded MAPE: clip denominator to min 0.5 kWh to prevent infinite percentage errors on near-zero days
    denom = np.maximum(y_true, 0.5)
    mape = float(np.mean(np.abs(y_true - y_pred) / denom) * 100.0)
    
    return {
        'mae': round(mae, 3),
        'rmse': round(rmse, 3),
        'mape': round(mape, 2)
    }


def split_chronological_data(
    series: pd.Series,
    train_pct: float = 0.70,
    val_pct: float = 0.15
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Split time series into chronological Train, Validation, and Test sets.
    Preserves strict temporal sequence to prevent lookahead data leakage.
    """
    n = len(series)
    train_end = int(n * train_pct)
    val_end = int(n * (train_pct + val_pct))

    train = series.iloc[:train_end]
    val = series.iloc[train_end:val_end]
    test = series.iloc[val_end:]

    return train, val, test


class HouseholdForecaster:
    """End-to-end forecasting pipeline for a single household's electricity series."""

    def __init__(self, household_id: str, series: pd.Series):
        self.household_id = household_id
        # Ensure regular daily frequency
        self.series = series.copy().asfreq('D').fillna(method='ffill').fillna(method='bfill')
        self.train, self.val, self.test = split_chronological_data(self.series)
        self.model_results = {}
        self.best_model_name = None
        self.best_model_obj = None
        self.metadata = {
            'household_id': household_id,
            'total_observations': len(self.series),
            'train_period': f"{self.train.index.min().strftime('%Y-%m-%d')} to {self.train.index.max().strftime('%Y-%m-%d')} ({len(self.train)} days)",
            'val_period': f"{self.val.index.min().strftime('%Y-%m-%d')} to {self.val.index.max().strftime('%Y-%m-%d')} ({len(self.val)} days)",
            'test_period': f"{self.test.index.min().strftime('%Y-%m-%d')} to {self.test.index.max().strftime('%Y-%m-%d')} ({len(self.test)} days)",
        }

    def train_and_evaluate_all(self) -> Dict[str, Any]:
        """Train all candidate models and benchmark on validation and test sets."""
        val_len = len(self.val)
        y_val = self.val.values

        # 1. Model: Seasonal Naive Baseline (Lag-7)
        # y(t) = y(t-7)
        train_vals = list(self.train.values)
        snaive_val_preds = []
        for i in range(val_len):
            snaive_val_preds.append(train_vals[-7 + (i % 7)])
        snaive_val_preds = np.array(snaive_val_preds)
        self.model_results['Seasonal Naive'] = {
            'val_metrics': calculate_metrics(y_val, snaive_val_preds),
            'val_predictions': snaive_val_preds
        }

        # 2. Model: Moving Average (MA-7) Baseline
        ma_val = float(np.mean(self.train.values[-7:]))
        ma_val_preds = np.full(val_len, ma_val)
        self.model_results['Moving Average (7-Day)'] = {
            'val_metrics': calculate_metrics(y_val, ma_val_preds),
            'val_predictions': ma_val_preds
        }

        # 3. Model: Holt-Winters Exponential Smoothing (Additive Trend & 7-Day Seasonality)
        try:
            hw_model = ExponentialSmoothing(
                self.train,
                trend='add',
                seasonal='add',
                seasonal_periods=7,
                initialization_method='estimated'
            ).fit(optimized=True)
            hw_val_preds = hw_model.forecast(val_len).values
            self.model_results['Exponential Smoothing'] = {
                'val_metrics': calculate_metrics(y_val, hw_val_preds),
                'val_predictions': hw_val_preds,
                'fitted_model': hw_model
            }
        except Exception as e:
            # Fallback to simple Holt linear
            try:
                hw_model = ExponentialSmoothing(self.train, trend='add').fit(optimized=True)
                hw_val_preds = hw_model.forecast(val_len).values
                self.model_results['Exponential Smoothing'] = {
                    'val_metrics': calculate_metrics(y_val, hw_val_preds),
                    'val_predictions': hw_val_preds,
                    'fitted_model': hw_model
                }
            except Exception:
                pass

        # 4. Model: ARIMA(1, 1, 1)
        try:
            arima_model = ARIMA(self.train, order=(1, 1, 1)).fit()
            arima_val_preds = arima_model.forecast(steps=val_len).values
            self.model_results['ARIMA (1,1,1)'] = {
                'val_metrics': calculate_metrics(y_val, arima_val_preds),
                'val_predictions': arima_val_preds,
                'fitted_model': arima_model
            }
        except Exception:
            pass

        # 5. Model: SARIMA(1, 0, 1)x(1, 1, 1, 7)
        try:
            sarima_model = SARIMAX(
                self.train,
                order=(1, 0, 1),
                seasonal_order=(1, 1, 1, 7),
                enforce_stationarity=False,
                enforce_invertibility=False
            ).fit(disp=False, maxiter=50)
            sarima_val_preds = sarima_model.forecast(steps=val_len).values
            self.model_results['SARIMA (1,0,1)(1,1,1)7'] = {
                'val_metrics': calculate_metrics(y_val, sarima_val_preds),
                'val_predictions': sarima_val_preds,
                'fitted_model': sarima_model
            }
        except Exception:
            pass

        # Select Best Model based on lowest Validation RMSE
        best_name = min(
            self.model_results.keys(),
            key=lambda m: self.model_results[m]['val_metrics']['rmse']
        )
        self.best_model_name = best_name
        self.metadata['best_model_name'] = best_name
        self.metadata['val_rmse'] = self.model_results[best_name]['val_metrics']['rmse']

        # Now evaluate the selected model on the held-out TEST set
        # Fit on combined Train + Val and forecast Test
        train_val_series = pd.concat([self.train, self.val])
        test_len = len(self.test)
        y_test = self.test.values

        test_preds = self._forecast_model(best_name, train_val_series, steps=test_len)
        test_metrics = calculate_metrics(y_test, test_preds)
        
        self.metadata['test_metrics'] = test_metrics
        self.test_predictions = test_preds

        return {
            'model_comparison': {
                name: res['val_metrics'] for name, res in self.model_results.items()
            },
            'best_model': best_name,
            'test_metrics': test_metrics,
            'metadata': self.metadata
        }

    def _forecast_model(self, model_name: str, history: pd.Series, steps: int) -> np.ndarray:
        """Helper to fit and forecast for a specific model name."""
        if 'Naive' in model_name:
            hist_vals = list(history.values)
            preds = [hist_vals[-7 + (i % 7)] for i in range(steps)]
            return np.array(preds)
        elif 'Moving Average' in model_name:
            val = float(np.mean(history.values[-7:]))
            return np.full(steps, val)
        elif 'Exponential Smoothing' in model_name:
            try:
                fit = ExponentialSmoothing(history, trend='add', seasonal='add', seasonal_periods=7).fit(optimized=True)
                return fit.forecast(steps).values
            except Exception:
                fit = ExponentialSmoothing(history, trend='add').fit(optimized=True)
                return fit.forecast(steps).values
        elif 'SARIMA' in model_name:
            try:
                fit = SARIMAX(history, order=(1, 0, 1), seasonal_order=(1, 1, 1, 7), enforce_stationarity=False, enforce_invertibility=False).fit(disp=False, maxiter=50)
                return fit.forecast(steps=steps).values
            except Exception:
                return self._forecast_model('ARIMA', history, steps)
        elif 'ARIMA' in model_name:
            try:
                fit = ARIMA(history, order=(1, 1, 1)).fit()
                return fit.forecast(steps=steps).values
            except Exception:
                return np.full(steps, float(history.mean()))
        else:
            return np.full(steps, float(history.mean()))

    def generate_future_forecast(self, horizon_days: int = 7) -> pd.DataFrame:
        """
        Generate out-of-sample future forecasts for the specified horizon (7, 14, 30 days)
        using the selected best model trained on full historical observations.
        Includes 95% confidence intervals and non-negative clipping.
        """
        if not self.best_model_name:
            self.train_and_evaluate_all()

        # Fit best model on full series
        preds = self._forecast_model(self.best_model_name, self.series, steps=horizon_days)
        preds = np.maximum(0.0, preds)

        # Estimate residual standard deviation for prediction intervals
        train_val = pd.concat([self.train, self.val])
        back_preds = self._forecast_model(self.best_model_name, self.train, steps=len(self.val))
        residuals = self.val.values - back_preds
        sigma = float(np.std(residuals)) if len(residuals) > 0 else float(np.std(self.series))

        # Prediction intervals widen slightly with horizon
        horizon_factors = np.sqrt(np.arange(1, horizon_days + 1))
        z_score = 1.96  # 95% confidence interval

        lower_bound = np.maximum(0.0, preds - z_score * sigma * (1.0 + 0.05 * horizon_factors))
        upper_bound = preds + z_score * sigma * (1.0 + 0.05 * horizon_factors)

        # Future date index
        last_date = self.series.index.max()
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon_days, freq='D')

        df_future = pd.DataFrame({
            'date': future_dates,
            'forecast_kwh': np.round(preds, 2),
            'lower_bound_kwh': np.round(lower_bound, 2),
            'upper_bound_kwh': np.round(upper_bound, 2),
            'household_id': self.household_id,
            'model_name': self.best_model_name
        }).set_index('date')

        return df_future


def get_household_forecast_pipeline(household_id: str, horizon_days: int = 7) -> Dict[str, Any]:
    """
    Main entry point for UI. Loads household data, benchmarks models,
    evaluates on test set, and returns future forecast DataFrame.
    """
    from analysis.household_preprocessing import load_household_daily_series
    df_daily, meta = load_household_daily_series(household_id)
    series = df_daily['consumption_kwh']

    forecaster = HouseholdForecaster(household_id, series)
    benchmarks = forecaster.train_and_evaluate_all()
    df_future = forecaster.generate_future_forecast(horizon_days=horizon_days)

    return {
        'forecaster': forecaster,
        'benchmarks': benchmarks,
        'future_forecast': df_future,
        'household_series': series,
        'best_model': forecaster.best_model_name,
        'test_metrics': benchmarks['test_metrics'],
        'model_comparison': benchmarks['model_comparison'],
        'metadata': forecaster.metadata
    }

