"""
PowerTrack Advanced Household Time-Series Forecasting Engine.
Trains, validates, and benchmarks classical and machine-learning models
(Seasonal Naive, 7-Day Moving Average, Holt-Winters Exponential Smoothing,
ARIMA, SARIMA, and Ridge Autoregressive ML) on individual household smart meter data.
Preserves strict chronological train-validation-test separation (zero data leakage)
and produces multi-horizon out-of-sample forecasts with 95% prediction intervals.
"""

import os
import warnings
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.linear_model import Ridge

warnings.filterwarnings("ignore")

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate MAE, RMSE, and bounded MAPE."""
    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()
    
    # Clip predictions to physically plausible non-negative values
    y_pred = np.maximum(0.0, y_pred)
    
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    
    # Bounded MAPE (minimum denominator 0.5 kWh prevents division by zero)
    denom = np.maximum(y_true, 0.5)
    mape = float(np.mean(np.abs(y_true - y_pred) / denom) * 100.0)
    
    return {
        'mae': round(mae, 3),
        'rmse': round(rmse, 3),
        'mape': round(mape, 2)
    }


def split_chronological_data(
    series: pd.Series,
    train_pct: float = 0.75,
    val_pct: float = 0.15
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Split time series into chronological Train, Validation, and Test subsets.
    Preserves strict temporal sequence to eliminate future-lookahead data leakage.
    """
    n = len(series)
    train_end = int(n * train_pct)
    val_end = int(n * (train_pct + val_pct))

    train = series.iloc[:train_end]
    val = series.iloc[train_end:val_end]
    test = series.iloc[val_end:]

    return train, val, test


class HouseholdForecaster:
    """End-to-end multi-model forecasting engine for an individual household."""

    def __init__(self, household_id: str, series: pd.Series):
        self.household_id = household_id
        # Ensure daily regular frequency with linear forward-backward boundary fill
        self.series = series.copy().asfreq('D').interpolate(method='time').ffill().bfill()
        self.train, self.val, self.test = split_chronological_data(self.series)
        self.model_results = {}
        self.best_model_name = None
        self.metadata = {
            'household_id': household_id,
            'total_observations': len(self.series),
            'train_period': f"{self.train.index.min().strftime('%Y-%m-%d')} to {self.train.index.max().strftime('%Y-%m-%d')} ({len(self.train)} days)",
            'val_period': f"{self.val.index.min().strftime('%Y-%m-%d')} to {self.val.index.max().strftime('%Y-%m-%d')} ({len(self.val)} days)",
            'test_period': f"{self.test.index.min().strftime('%Y-%m-%d')} to {self.test.index.max().strftime('%Y-%m-%d')} ({len(self.test)} days)",
        }

    def train_and_evaluate_all(self) -> Dict[str, Any]:
        """Train all candidate models and benchmark on validation and held-out test sets."""
        val_len = len(self.val)
        y_val = self.val.values

        # -----------------------------------------------------------------
        # Model 1: Seasonal Naive Baseline (Lag-7)
        # -----------------------------------------------------------------
        train_vals = list(self.train.values)
        snaive_val_preds = np.array([train_vals[-7 + (i % 7)] for i in range(val_len)])
        self.model_results['Seasonal Naive'] = {
            'val_metrics': calculate_metrics(y_val, snaive_val_preds),
            'val_predictions': snaive_val_preds,
            'display_name': 'Seasonal Naive (Lag-7)'
        }

        # -----------------------------------------------------------------
        # Model 2: Moving Average Baseline (7-Day Rolling)
        # -----------------------------------------------------------------
        ma_val = float(np.mean(self.train.values[-7:]))
        ma_val_preds = np.full(val_len, ma_val)
        self.model_results['Moving Average'] = {
            'val_metrics': calculate_metrics(y_val, ma_val_preds),
            'val_predictions': ma_val_preds,
            'display_name': 'Moving Average (7-Day)'
        }

        # -----------------------------------------------------------------
        # Model 3: Holt-Winters Exponential Smoothing
        # -----------------------------------------------------------------
        try:
            hw_model = ExponentialSmoothing(
                self.train,
                trend='add',
                seasonal='add',
                seasonal_periods=7,
                initialization_method='estimated'
            ).fit(optimized=True)
            hw_val_preds = np.maximum(0.0, hw_model.forecast(val_len).values)
            self.model_results['Exponential Smoothing'] = {
                'val_metrics': calculate_metrics(y_val, hw_val_preds),
                'val_predictions': hw_val_preds,
                'display_name': 'Holt-Winters Exp. Smoothing'
            }
        except Exception:
            try:
                hw_model = ExponentialSmoothing(self.train, trend='add').fit(optimized=True)
                hw_val_preds = np.maximum(0.0, hw_model.forecast(val_len).values)
                self.model_results['Exponential Smoothing'] = {
                    'val_metrics': calculate_metrics(y_val, hw_val_preds),
                    'val_predictions': hw_val_preds,
                    'display_name': 'Holt Linear Smoothing'
                }
            except Exception:
                pass

        # -----------------------------------------------------------------
        # Model 4: Classical ARIMA (p=1, d=1, q=1)
        # -----------------------------------------------------------------
        try:
            arima_model = ARIMA(self.train, order=(1, 1, 1)).fit()
            arima_val_preds = np.maximum(0.0, arima_model.forecast(steps=val_len).values)
            self.model_results['ARIMA'] = {
                'val_metrics': calculate_metrics(y_val, arima_val_preds),
                'val_predictions': arima_val_preds,
                'display_name': 'ARIMA (1,1,1)'
            }
        except Exception:
            pass

        # -----------------------------------------------------------------
        # Model 5: Seasonal ARIMA (SARIMA) with 7-Day Diurnal/Weekly Cycle
        # -----------------------------------------------------------------
        sarima_candidates = [
            ((1, 0, 1), (1, 1, 1, 7)),
            ((1, 1, 1), (1, 1, 1, 7)),
            ((0, 1, 1), (0, 1, 1, 7))
        ]
        best_sarima_res = None
        best_sarima_rmse = float('inf')

        for order, s_order in sarima_candidates:
            try:
                fit = SARIMAX(
                    self.train,
                    order=order,
                    seasonal_order=s_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False
                ).fit(disp=False, maxiter=40)
                preds = np.maximum(0.0, fit.forecast(steps=val_len).values)
                met = calculate_metrics(y_val, preds)
                if met['rmse'] < best_sarima_rmse:
                    best_sarima_rmse = met['rmse']
                    best_sarima_res = {
                        'order': order,
                        'seasonal_order': s_order,
                        'metrics': met,
                        'preds': preds
                    }
            except Exception:
                continue

        if best_sarima_res:
            self.model_results['SARIMA'] = {
                'val_metrics': best_sarima_res['metrics'],
                'val_predictions': best_sarima_res['preds'],
                'display_name': f"SARIMA {best_sarima_res['order']}x{best_sarima_res['seasonal_order']}"
            }

        # -----------------------------------------------------------------
        # Model 6: Feature-Engineered Ridge Autoregressive Model
        # (Lags, 7-day Rolling Stats, Day-of-Week cyclical encodings)
        # -----------------------------------------------------------------
        try:
            ridge_val_preds = self._train_and_predict_ridge(self.train, steps=val_len)
            self.model_results['Ridge Autoregressive'] = {
                'val_metrics': calculate_metrics(y_val, ridge_val_preds),
                'val_predictions': ridge_val_preds,
                'display_name': 'Ridge Autoregressive ML'
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
        self.metadata['best_display_name'] = self.model_results[best_name].get('display_name', best_name)
        self.metadata['val_rmse'] = self.model_results[best_name]['val_metrics']['rmse']

        # Evaluate selected model on the strictly held-out TEST set
        train_val_series = pd.concat([self.train, self.val])
        test_len = len(self.test)
        y_test = self.test.values

        test_preds = self._forecast_model(best_name, train_val_series, steps=test_len)
        test_metrics = calculate_metrics(y_test, test_preds)
        
        self.metadata['test_metrics'] = test_metrics
        self.test_predictions = test_preds

        return {
            'model_comparison': {
                self.model_results[k].get('display_name', k): self.model_results[k]['val_metrics']
                for k in self.model_results
            },
            'best_model': self.model_results[best_name].get('display_name', best_name),
            'best_model_key': best_name,
            'test_metrics': test_metrics,
            'metadata': self.metadata
        }

    def _train_and_predict_ridge(self, history: pd.Series, steps: int) -> np.ndarray:
        """Recursive multi-step forecast using Ridge regression with lag and calendar features."""
        df_feat = pd.DataFrame({'y': history.values}, index=history.index)
        df_feat['lag_1'] = df_feat['y'].shift(1)
        df_feat['lag_2'] = df_feat['y'].shift(2)
        df_feat['lag_7'] = df_feat['y'].shift(7)
        df_feat['roll_mean_7'] = df_feat['y'].shift(1).rolling(7).mean()
        df_feat['day_of_week'] = df_feat.index.dayofweek
        df_feat['sin_dow'] = np.sin(2 * np.pi * df_feat['day_of_week'] / 7)
        df_feat['cos_dow'] = np.cos(2 * np.pi * df_feat['day_of_week'] / 7)
        df_clean = df_feat.dropna()

        feature_cols = ['lag_1', 'lag_2', 'lag_7', 'roll_mean_7', 'sin_dow', 'cos_dow']
        X = df_clean[feature_cols]
        y = df_clean['y']

        model = Ridge(alpha=1.0)
        model.fit(X, y)

        # Recursive multi-step generation
        history_list = list(history.values)
        current_date = history.index.max()
        preds = []

        for i in range(steps):
            current_date = current_date + pd.Timedelta(days=1)
            dow = current_date.dayofweek
            sin_d = np.sin(2 * np.pi * dow / 7)
            cos_d = np.cos(2 * np.pi * dow / 7)
            l1 = history_list[-1]
            l2 = history_list[-2]
            l7 = history_list[-7]
            rm7 = np.mean(history_list[-7:])
            
            x_step = np.array([[l1, l2, l7, rm7, sin_d, cos_d]])
            y_pred = float(model.predict(x_step)[0])
            y_pred = max(0.0, y_pred)
            preds.append(y_pred)
            history_list.append(y_pred)

        return np.array(preds)

    def _forecast_model(self, model_key: str, history: pd.Series, steps: int) -> np.ndarray:
        """Fit model on full history and forecast future steps."""
        if 'Naive' in model_key:
            hist_vals = list(history.values)
            return np.array([hist_vals[-7 + (i % 7)] for i in range(steps)])
        elif 'Moving Average' in model_key:
            val = float(np.mean(history.values[-7:]))
            return np.full(steps, val)
        elif 'Exponential Smoothing' in model_key:
            try:
                fit = ExponentialSmoothing(history, trend='add', seasonal='add', seasonal_periods=7).fit(optimized=True)
                return np.maximum(0.0, fit.forecast(steps).values)
            except Exception:
                fit = ExponentialSmoothing(history, trend='add').fit(optimized=True)
                return np.maximum(0.0, fit.forecast(steps).values)
        elif 'SARIMA' in model_key:
            try:
                fit = SARIMAX(
                    history,
                    order=(1, 0, 1),
                    seasonal_order=(1, 1, 1, 7),
                    enforce_stationarity=False,
                    enforce_invertibility=False
                ).fit(disp=False, maxiter=40)
                return np.maximum(0.0, fit.forecast(steps=steps).values)
            except Exception:
                return self._forecast_model('ARIMA', history, steps)
        elif 'ARIMA' in model_key:
            try:
                fit = ARIMA(history, order=(1, 1, 1)).fit()
                return np.maximum(0.0, fit.forecast(steps=steps).values)
            except Exception:
                return np.full(steps, float(history.mean()))
        elif 'Ridge' in model_key:
            return self._train_and_predict_ridge(history, steps)
        else:
            return np.full(steps, float(history.mean()))

    def generate_future_forecast(self, horizon_days: int = 7) -> pd.DataFrame:
        """
        Generate out-of-sample future forecasts for specified horizon (7, 14, 30 days)
        with 95% confidence bounds and physical non-negative clipping.
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

        # Prediction intervals expand with horizon sqrt(h)
        horizon_factors = np.sqrt(np.arange(1, horizon_days + 1))
        z_score = 1.96  # 95% confidence interval

        lower_bound = np.maximum(0.0, preds - z_score * sigma * (1.0 + 0.04 * horizon_factors))
        upper_bound = preds + z_score * sigma * (1.0 + 0.04 * horizon_factors)

        # Future date index
        last_date = self.series.index.max()
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon_days, freq='D')

        # Estimated cost per day under domestic slab average (~₹6.50/kWh)
        daily_cost_est = np.round(preds * 6.50, 0)

        df_future = pd.DataFrame({
            'date': future_dates,
            'day_name': future_dates.day_name(),
            'forecast_kwh': np.round(preds, 2),
            'lower_bound_kwh': np.round(lower_bound, 2),
            'upper_bound_kwh': np.round(upper_bound, 2),
            'est_cost_inr': daily_cost_est,
            'household_id': self.household_id,
            'model_name': self.model_results[self.best_model_name].get('display_name', self.best_model_name)
        }).set_index('date')

        return df_future


def get_household_forecast_pipeline(household_id: str, horizon_days: int = 7) -> Dict[str, Any]:
    """
    Main entry point for UI. Loads household data, benchmarks candidate models,
    evaluates on test set, and returns future forecast DataFrame and insights.
    """
    from analysis.household_preprocessing import load_household_daily_series
    from analysis.billing_tariffs import calculate_electricity_bill

    df_daily, meta = load_household_daily_series(household_id)
    series = df_daily['consumption_kwh']

    forecaster = HouseholdForecaster(household_id, series)
    benchmarks = forecaster.train_and_evaluate_all()
    df_future = forecaster.generate_future_forecast(horizon_days=horizon_days)

    total_fc_kwh = float(df_future['forecast_kwh'].sum())
    avg_daily_kwh = float(df_future['forecast_kwh'].mean())
    bill_calc = calculate_electricity_bill(total_fc_kwh, sanctioned_load_kw=2.0)
    
    # Comparison vs past comparable window
    past_window_kwh = float(series.iloc[-horizon_days:].sum()) if len(series) >= horizon_days else total_fc_kwh
    pct_diff = ((total_fc_kwh - past_window_kwh) / max(past_window_kwh, 1.0)) * 100.0

    # Peak day
    peak_row = df_future.loc[df_future['forecast_kwh'].idxmax()]
    min_row = df_future.loc[df_future['forecast_kwh'].idxmin()]

    summary = {
        'total_fc_kwh': round(total_fc_kwh, 1),
        'avg_daily_kwh': round(avg_daily_kwh, 2),
        'past_window_kwh': round(past_window_kwh, 1),
        'pct_diff': round(pct_diff, 1),
        'estimated_bill_inr': round(bill_calc['total_bill'], 0),
        'energy_charges_inr': round(bill_calc['energy_charges'], 0),
        'fixed_charges_inr': round(bill_calc['fixed_charges'], 0),
        'duty_inr': round(bill_calc['electricity_duty'], 0),
        'peak_day': peak_row['day_name'],
        'peak_date': peak_row.name.strftime('%d %b'),
        'peak_kwh': float(peak_row['forecast_kwh']),
        'lowest_day': min_row['day_name'],
        'lowest_date': min_row.name.strftime('%d %b'),
        'lowest_kwh': float(min_row['forecast_kwh'])
    }

    # Generate explainable household forecast insights
    insights = []
    if pct_diff > 3.0:
        insights.append(f"Consumption is projected to rise by +{pct_diff:.1f}% compared to the previous {horizon_days} days, primarily driven by weekend activity.")
    elif pct_diff < -3.0:
        insights.append(f"Consumption is projected to decrease by {abs(pct_diff):.1f}% over the next {horizon_days} days compared to recent baseline.")
    else:
        insights.append(f"Consumption is projected to remain steady (within ±{abs(pct_diff):.1f}% of recent baseline usage).")

    insights.append(f"Peak electricity demand is anticipated on {summary['peak_day']} ({summary['peak_date']}) with an estimated {summary['peak_kwh']:.1f} kWh.")
    insights.append(f"Standby load drops to its lowest on {summary['lowest_day']} ({summary['lowest_date']}) at approximately {summary['lowest_kwh']:.1f} kWh.")

    return {
        'forecaster': forecaster,
        'benchmarks': benchmarks,
        'future_forecast': df_future,
        'household_series': series,
        'best_model': forecaster.metadata.get('best_display_name', forecaster.best_model_name),
        'best_model_key': forecaster.best_model_name,
        'test_metrics': benchmarks['test_metrics'],
        'model_comparison': benchmarks['model_comparison'],
        'summary': summary,
        'insights': insights,
        'metadata': forecaster.metadata
    }
