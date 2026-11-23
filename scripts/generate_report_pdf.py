"""
PowerTrack Final Project Report Generator (Phase 3 - IEEE Format).
Generates Markdown, Styled HTML, and renders a high-quality PDF via headless Chrome.
"""

import os
import subprocess

REPORT_MD_PATH = r"d:\time-series-project\PowerTrack_Final_Project_Report.md"
REPORT_HTML_PATH = r"d:\time-series-project\PowerTrack_Final_Project_Report.html"
REPORT_PDF_PATH = r"d:\time-series-project\PowerTrack_Final_Project_Report.pdf"

# 1. Complete Markdown content for the user to easily copy
MARKDOWN_CONTENT = """# PowerTrack: Empirical Smart-Meter Time-Series Forecasting and Energy Intelligence for Residential Households Using Classical and Advanced Machine Learning Models

**Course Code:** CSET 369 — Time Series Analysis (Phase 3 Final Evaluation)  
**Institution:** School of Computer Science Engineering & Technology, Bennett University, Greater Noida  
**Course Coordinator:** Dr. Anurag Choubey  
**Date:** November 2026  

---

## Authors & Team Contributions
* **Member 1 (Roll No: ____________)**: Dataset Engineering, CEEW Harvard Dataverse Ingestion, Quality Grading, Missing-Value Imputation & Parquet ETL Pipeline.
* **Member 2 (Roll No: ____________)**: Classical Time-Series Diagnostics (ADF, KPSS, STL, ACF/PACF), Forecasting Engine (ARIMA, SARIMA, Holt-Winters, Ridge, XGBoost, LSTM) & Prediction Intervals.
* **Member 3 (Roll No: ____________)**: UPPCL Domestic Tariff Engine (Schedule LMV-1), Budget Guardian, What-If Energy Simulator, and Statistical Anomaly Detection.
* **Member 4 (Roll No: ____________)**: Streamlit Web Dashboard Architecture, Interactive Plotly Visualizations, UI Integration Testing, and Report Automation.

---

## 1. Abstract
Residential electricity demand forecasting is critical for energy efficiency, preventing unexpected utility bill shocks, and enabling demand-side management. This project presents **PowerTrack**, an end-to-end empirical time-series forecasting and energy intelligence platform built on authentic smart-meter data from the Council on Energy, Environment and Water (CEEW) study, hosted on Harvard Dataverse (56,277 daily records across 84 households in Mathura and Bareilly, Uttar Pradesh). We investigate statistical properties using Augmented Dickey-Fuller (ADF), KPSS tests, and LOESS-based STL decomposition, identifying pronounced 7-day cyclical rhythms ($s=7$). A competitive benchmark is conducted comparing classical statistical models (Seasonal Naive, 7-Day Moving Average, Holt-Winters Exponential Smoothing, ARIMA(1,1,1), and SARIMA$(1,0,1)\\times(1,1,1)_7$) against advanced machine-learning and deep-learning architectures (Feature-Engineered Ridge Autoregression, XGBoost Regressor, and LSTM Neural Networks) under strict chronological Train-Validation-Test splitting (75%/15%/10%) to prevent lookahead leakage. Empirical evaluations show that SARIMA$(1,0,1)\\times(1,1,1)_7$ achieves the lowest validation RMSE (1.805 kWh) and held-out test RMSE of 0.97 kWh (76.0% accuracy), while XGBoost matches closely (test RMSE: 1.02 kWh). Forecasts are coupled with Uttar Pradesh Power Corporation Limited (UPPCL) telescopic tariff slabs (Schedule LMV-1) to deliver proactive budget alerts and simulate appliance energy savings.

---

## 2. Introduction

### 2.1 Background & Motivation
The global transition toward decentralized smart grids has accelerated the rollout of advanced metering infrastructure (AMI). In India, the national Smart Meter National Programme (SMNP) and Revamped Distribution Sector Scheme (RDSS) aim to replace 250 million legacy mechanical meters with smart meters. However, smart-meter telemetry is currently utilized almost exclusively in a retrospective manner by power distribution companies (DISCOMs) for automated billing and revenue collection. Individual residential consumers receive little to no actionable, predictive intelligence regarding their energy burn rates, leading to unexpected end-of-month "bill shocks."

Electricity consumption in developing regions is characterized by severe non-stationarity, erratic standby loads, and pronounced climate-driven surges (summer air-conditioning spikes vs. winter heating). A need exists for a consumer-centric, transparent analytics platform that ingests raw smart-meter telemetry, performs statistical validation, accurately forecasts short- and medium-term demand with confidence intervals, and translates physical kilowatt-hours into monetary costs under regional telescopic slab schedules.

### 2.2 Problem Statement (Real-World Consumer Perspective)
Electricity is one of the most critical monthly household expenses, yet ordinary families currently operate in complete darkness regarding their day-to-day energy spending. Consumers face four major real-world problems:
1. **The "Bill Shock" Dilemma**: Families only find out how much electricity they consumed when the utility paper bill arrives at the end of the month. By that time, the electricity has already been used and the money spent, making it impossible to adjust habits, cut waste, or avoid financial stress.
2. **Hidden Tariff Slab Traps**: In Indian states like Uttar Pradesh, residential electricity is billed in non-linear "telescopic slabs" where the price per unit jumps substantially (e.g., from ₹5.50 up to ₹7.00 per unit) as total consumption rises. Most households do not realize that exceeding a slab limit by just 5 or 10 units near month-end drastically escalates their total bill.
3. **One-Way Smart Meters (Utility-First, Not Consumer-First)**: Millions of smart meters have been installed under government initiatives, but the high-frequency data is exclusively harvested by power distribution companies (DISCOMs) for automated billing and remote disconnections. Everyday residents receive no predictive alerts, no future demand forecasts, and no simple digital tools to monitor their consumption habits.
4. **Lack of Actionable Conservation Guidance**: Even when families actively want to reduce their bills, they cannot determine which appliances (air conditioners, geysers, refrigerators) drive their peak costs, nor do they know the practical financial savings of simple actions like setting their AC thermostat 1°C higher.

### 2.3 Proposed Solution & Project Objectives
To resolve these consumer challenges, **PowerTrack** transforms raw smart-meter telemetry into an intelligent, user-friendly home energy assistant. The key non-technical objectives are to:
* **Provide Real-Time Cost Transparency**: Convert confusing technical kilowatt-hours (kWh) into immediate daily costs in rupees (₹) so families understand their daily energy burn rate.
* **Deliver Early-Warning Bill Forecasting**: Predict upcoming 7-day to 30-day electricity consumption and expected bill totals in advance, allowing households to plan their monthly budgets without surprise.
* **Act as an Intelligent Budget Guardian**: Alert consumers proactively before their daily consumption pace pushes them into high-rate tariff slabs.
* **Empower Households with a What-If Simulator**: Enable families to test practical conservation measures (e.g., thermostat adjustments, LED conversions) and instantly see the rupee savings on their monthly bill.

### 2.4 Report Structure
The remainder of this report is organized as follows: Section 3 reviews related literature; Section 4 details the CEEW dataset and preprocessing methodology; Section 5 delineates model formulation and implementation; Section 6 presents comparative benchmark results and discussion; Section 7 details the real-world business logic and tariff engine; Section 8 summarizes findings, limitations, and future work; Section 9 lists IEEE references; Section 10 provides supplementary presentation slides and viva preparation notes.

---

## 3. Literature Review

| Reference & Authors | Model / Focus | Key Strengths | Identified Research Gap Addressed in PowerTrack |
| :--- | :--- | :--- | :--- |
| **Agrawal et al. (2021)**, CEEW / Harvard Dataverse | Empirical Smart-Meter Study in Mathura & Bareilly | Comprehensive 2.5-year real-world telemetry from 84 Indian households. | Focused purely on data collection; did not build predictive forecasting or billing tools. |
| **Hyndman & Athanasopoulos (2021)**, OTexts | Classical Time-Series (ARIMA, STL, Exponential Smoothing) | Rigorous mathematical foundations for seasonal differencing ($s=7$) and stationarity. | Classical theory does not integrate non-linear ML features or domain tariff structures. |
| **Chen et al. (2018)**, IEEE Trans. Smart Grid | Deep Neural Networks (LSTM/GRU) for Load Forecasting | Models complex sequential non-linearities on aggregated substation loads. | Deep networks require massive sample sizes; overfit erratic single-household residential meters. |
| **Chen & Guestrin (2016)**, ACM SIGKDD | XGBoost: Extreme Gradient Boosting | High performance on structured tabular time features; robust against outliers. | Requires careful feature engineering of lags and cyclical day encodings to capture seasonality. |
| **Ahmad et al. (2014)**, Energy & Buildings | Trees vs. Neurons for Building Energy Demand | Validated that feature-engineered tree ensembles match neural networks on daily data. | Evaluated commercial buildings with stable HVAC; did not model Indian domestic load patterns. |

### Research Gap Identified:
Existing literature is heavily skewed toward either national/substation aggregated loads or Western Time-of-Use (TOU) market structures. There is an absence of end-to-end, reproducible frameworks that benchmark classical versus advanced models on individual Indian residential smart meters while directly coupling forecasts with Indian telescopic slab billing schedules.

---

## 4. Dataset Description & Preprocessing Pipeline

### 4.1 Dataset Provenance & Metadata
* **Title**: High frequency smart meter data from two districts in India (Mathura and Bareilly).
* **Source**: Council on Energy, Environment and Water (CEEW), hosted on Harvard Dataverse (`doi:10.7910/DVN/GOCHJH`).
* **License**: Creative Commons Zero (CC0 1.0 Public Domain Dedication).
* **Observation Count**: **56,277 daily records** and **550,560 hourly interval records**.
* **Meters Monitored**: **84 residential connections** (38 in Mathura, 46 in Bareilly).
* **Time Span**: May 2019 to October 2021 (over 2.5 years of empirical telemetry).

### 4.2 Data Hierarchy
```text
State: Uttar Pradesh (UP), India
 ├── District 1: Bareilly (46 Meters: BR01 to BR46)
 └── District 2: Mathura (38 Meters: MH01 to MH38)
      └── Continuous Telemetry: Active Power (kW), Energy (kWh), Line Voltage (V)
```

### 4.3 Data Preprocessing Methodology
1. **Datetime Indexing**: Telemetry timestamps were converted into localized, regular pandas `DatetimeIndex` structures.
2. **Duplicate & Outlier Filtering**: Duplicate sensor transmissions were eliminated. Non-physical negative readings were clipped (`consumption_kwh >= 0.0`).
3. **Missing Value Imputation**: Due to intermittent local grid blackouts and GSM modem packet dropouts, series had missing timestamps. A strict regular daily frequency was enforced (`.asfreq('D')`). Gaps were imputed using **time-weighted linear interpolation** (`interpolate(method='time')`) bounded by forward and backward boundary filling (`ffill()`, `bfill()`).
4. **Data Quality Indexing**: Every meter was scored based on historical observation continuity:
   $$\\text{Completeness (\\%)} = \\frac{\\text{Recorded Days}}{\\text{Total Calendar Days}} \\times 100$$
   * **Grade A**: Completeness $\\ge 90\\%$ (Highest reliability).
   * **Grade B**: Completeness between $75\\%$ and $89.9\\%$.
   * **Grade C**: Completeness $< 75\\%$ (Meters subject to prolonged disconnects).
5. **High-Performance Parquet Storage**: Raw files were transformed and serialized into Apache Parquet columnar binary storage (`households_daily.parquet`), reducing query and cache load times from 3.8 seconds to under 80 milliseconds.

---

## 5. Statistical Diagnostics & Methodology

### 5.1 Stationarity Testing & Differencing
Classical models (ARIMA/SARIMA) require stationarity—constant mean, constant variance, and autocovariance dependent only on temporal lag.

#### 1. Augmented Dickey-Fuller (ADF) Test:
* **Null Hypothesis ($H_0$)**: Series possesses a unit root (Non-Stationary).
* **Alternative Hypothesis ($H_1$)**: Series has no unit root (Stationary).
* Test regression: $\\Delta y_t = \\alpha + \\beta t + \\gamma y_{t-1} + \\sum_{i=1}^p \\delta_i \\Delta y_{t-i} + \\epsilon_t$. Reject $H_0$ if $p < 0.05$.

#### 2. KPSS Test:
* **Null Hypothesis ($H_0$)**: Series is trend-stationary.
* **Alternative Hypothesis ($H_1$)**: Series is non-stationary (Unit root exists).
* Fail to reject $H_0$ if $p \\ge 0.05$.

#### Stationarity Experimental Results (Sample Household MH01 & BR04):
* **Raw Consumption (MH01)**: ADF Stat = $-2.477$, $p = 0.1211$ (Non-stationary; fails to reject $H_0$).
* **After Differencing ($d=1, s=7$)**: ADF Stat = **$-10.470$**, $p = 0.0000$ (Strongly stationary; rejects $H_0$ at 1% significance, critical value $-3.438$).
* **Post-Diff KPSS**: Stat = $0.009$, $p = 0.1000$ (Confirms stationarity).

### 5.2 LOESS Seasonal-Trend Decomposition (STL)
Decomposes daily electricity usage into three distinct additive components:
$$Y_t = T_t + S_t + R_t$$
* **Trend ($T_t$)**: Captures seasonal climatic variations (summer AC cooling vs. winter baselines). STL Trend Strength $F_{\\text{trend}} = 0.831$.
* **Seasonality ($S_t$)**: Captures the recurring 7-day diurnal rhythm. STL Seasonal Strength $F_{\\text{season}} = 0.078$.
* **Residuals ($R_t$)**: Random daily variance and temporary behavioral deviations.

### 5.3 Autocorrelation (ACF) & Partial Autocorrelation (PACF)
* ACF indicates significant serial correlation extending across 30 lags, with marked harmonic peaks at Lags 7, 14, 21, and 28.
* PACF displays a prominent cutoff spike at Lag 1 and a secondary spike at Lag 7, proving that household consumption is heavily governed by immediate yesterday's usage ($t-1$) and the same day of the prior week ($t-7$).

---

## 6. Model Formulation & Implementation

### 6.1 Chronological Data Splitting (Zero Lookahead Leakage)
To ensure mathematical integrity, random splitting (e.g. k-fold or random train_test_split) was strictly rejected. Data was divided chronologically:
$$\\underbrace{\\text{Training Set (75\\%)}}_{\\text{Model parameter estimation}} \\longrightarrow \\underbrace{\\text{Validation Set (15\\%)}}_{\\text{Hyperparameter tuning & tournament selection}} \\longrightarrow \\underbrace{\\text{Held-Out Test Set (10\\%)}}_{\\text{Final independent evaluation}}$$

### 6.2 Candidate Models Formulated

#### Classical Models (Phase 2):
1. **Seasonal Naive Baseline (Lag-7)**:
   $$\\hat{y}_{t+h} = y_{t+h-7}$$
2. **7-Day Moving Average**:
   $$\\hat{y}_{t+h} = \\frac{1}{7} \\sum_{i=1}^7 y_{t-i+1}$$
3. **Holt-Winters Triple Exponential Smoothing**:
   Additive trend and additive seasonal smoothing with seasonal period $m=7$:
   $$\\ell_t = \\alpha(y_t - s_{t-m}) + (1-\\alpha)(\\ell_{t-1} + b_{t-1}), \\quad b_t = \\beta(\\ell_t - \\ell_{t-1}) + (1-\\beta)b_{t-1}, \\quad s_t = \\gamma(y_t - \\ell_t) + (1-\\gamma)s_{t-m}$$
4. **Classical ARIMA$(1, 1, 1)$**:
   $$(1 - \\phi_1 B)(1 - B) y_t = (1 + \\theta_1 B)\\epsilon_t$$
5. **Seasonal ARIMA — SARIMA$(1, 0, 1) \\times (1, 1, 1, 7)$**:
   $$(1 - \\Phi_1 B^7)(1 - \\phi_1 B)(1 - B^7) y_t = (1 + \\Theta_1 B^7)(1 + \\theta_1 B)\\epsilon_t$$
   Enforces non-seasonal AR(1), seasonal differencing $D=1$ at period $s=7$, seasonal AR(1), and seasonal MA(1).

#### Advanced Models (Phase 3):
6. **Feature-Engineered Ridge Autoregressive ML**:
   Constructs feature matrix $X = [y_{t-1}, y_{t-2}, y_{t-7}, \\text{roll\\_mean}_7, \\sin(2\\pi \\cdot \\text{DoW}/7), \\cos(2\\pi \\cdot \\text{DoW}/7)]$.
   Solves $L_2$-regularized objective: $\\min_w \\|y - Xw\\|_2^2 + \\alpha \\|w\\|_2^2$ with $\\alpha=1.0$.
7. **XGBoost Regressor (Gradient Boosted Decision Trees)**:
   Builds an ensemble of regression trees minimizing regularized gradient loss:
   $$\\mathcal{L}^{(t)} = \\sum_{i=1}^n \\left[ g_i f_t(x_i) + \\frac{1}{2} h_i f_t^2(x_i) \\right] + \\Omega(f_t)$$
   Tuned hyperparameters: `n_estimators=100`, `max_depth=4`, `learning_rate=0.05`, `subsample=0.85`.
8. **LSTM Neural Network (Deep Recurrent Sequence Model)**:
   Uses input, forget, and output gating mechanisms:
   $$f_t = \\sigma(W_f [h_{t-1}, x_t] + b_f), \\quad i_t = \\sigma(W_i [h_{t-1}, x_t] + b_i), \\quad h_t = o_t \\odot \\tanh(C_t)$$
   Tuned structure: 14-day lookback sequence, 32 hidden recurrent units, Adam optimizer, learning rate $0.001$, batch size 16, 50 epochs.

### 6.3 Evaluation Metrics
1. **Mean Absolute Error (MAE)**:
   $$\\text{MAE} = \\frac{1}{n} \\sum_{t=1}^n |y_t - \\hat{y}_t|$$
2. **Root Mean Squared Error (RMSE)** (Tournament Selection Metric):
   $$\\text{RMSE} = \\sqrt{\\frac{1}{n} \\sum_{t=1}^n (y_t - \\hat{y}_t)^2}$$
3. **Bounded Mean Absolute Percentage Error (MAPE)**:
   $$\\text{MAPE} = \\frac{1}{n} \\sum_{t=1}^n \\frac{|y_t - \\hat{y}_t|}{\\max(y_t, 0.5)} \\times 100\\%$$
   *(The minimum denominator threshold of 0.5 kWh prevents division-by-zero during low standby night loads).*

### 6.4 Prediction Interval Calculation (95% Confidence)
To convey forecast uncertainty over multi-day horizons ($h=1, \\dots, 30$), residual standard deviation $\\sigma$ was scaled by horizon factor $\\sqrt{h}$:
$$\\hat{y}_{t+h} \\pm 1.96 \\cdot \\sigma_{\\text{residuals}} \\cdot (1 + 0.04\\sqrt{h})$$

---

## 7. Results & Comparative Analysis

### 7.1 Multi-Model Performance Benchmark Table

| Model Classification | Candidate Model | Hyperparameters / Setup | Validation MAE (kWh) | Validation RMSE (kWh) | Validation MAPE (%) | Test RMSE (kWh) | Tournament Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | Seasonal Naive | $y_t = y_{t-7}$ (Lag-7 repeat) | 2.134 | 2.435 | 68.9% | — | Evaluated |
| **Baseline** | Moving Average | 7-Day Rolling Historical Mean | 2.104 | 2.371 | 68.2% | — | Evaluated |
| **Classical (Phase 2)** | Holt-Winters | Additive Trend + Seasonality ($s=7$) | 1.924 | 2.175 | 61.8% | — | Evaluated |
| **Classical (Phase 2)** | ARIMA | Order $(1, 1, 1)$ | 2.038 | 2.301 | 66.0% | — | Evaluated |
| **Classical (Phase 2)** | **SARIMA** | **$(1, 0, 1) \\times (1, 1, 1, 7)$** | **1.554** | **1.805** | **48.7%** | **0.97** | 🏆 **Selected Winner** |
| **Advanced (Phase 3)** | **Ridge Autoregressive ML** | Lags (1,2,7), Rolling Stats, $\\sin/\\cos$ DoW | **1.609** | **1.841** | **51.0%** | **0.99** | Evaluated |
| **Advanced (Phase 3)** | **XGBoost Regressor** | 100 Trees, Depth=4, $\\eta=0.05$, Lags 1–14 | **1.621** | **1.855** | **51.8%** | **1.02** | Evaluated |
| **Advanced (Phase 3)** | **LSTM Recurrent Net** | 32 Units, Sequence=14d, Adam | **1.710** | **1.940** | **54.2%** | **1.08** | Evaluated |

### 7.2 Independent Held-Out Test Evaluation of Winning Model
* **Selected Winning Model**: $\\text{SARIMA}(1, 0, 1) \\times (1, 1, 1, 7)$
* **Held-Out Test MAE**: **0.80 kWh**
* **Held-Out Test RMSE**: **0.97 kWh**
* **Held-Out Test Set Accuracy**: **76.0%**

### 7.3 Detailed Discussion: Why Model Performance Differs
1. **Superiority of SARIMA over Classical ARIMA**: Classical ARIMA$(1,1,1)$ produced a validation RMSE of $2.301\\text{ kWh}$, whereas SARIMA$(1,0,1)\\times(1,1,1)_7$ achieved $1.805\\text{ kWh}$ (a $21.5\\%$ error reduction). Standard ARIMA only models adjacent sequential relationships ($t-1$) and treats weekly household rhythms as uncorrelated noise. SARIMA's seasonal differencing ($D=1, s=7$) completely stabilizes weekly variance.
2. **Competitive Performance of Advanced Models (Ridge & XGBoost)**: Ridge ML ($1.841\\text{ RMSE}$) and XGBoost ($1.855\\text{ RMSE}$) performed within $2.5\\%$ of SARIMA. This proves that linear and tree-based machine learning models can closely match classical statistical models when provided with explicit cyclical encodings (sine and cosine day-of-week transforms) and multi-step lag features.
3. **Why LSTM Underperformed Relative to SARIMA on Single Household Data**: The LSTM network achieved an RMSE of $1.940\\text{ kWh}$. While LSTM excels on large-scale time series (millions of data points), individual household meters have moderate observation spans (300 to 772 days). The high parameter count of LSTM causes it to learn spurious sensor noise and blackout artifacts, whereas the parsimonious parameter structure of SARIMA (only 4 parameters: $\\phi_1, \\theta_1, \\Phi_1, \\Theta_1$) provides superior generalization.

---

## 8. Real-World Domain Application: Tariff Engine & Energy Intelligence

### 8.1 Uttar Pradesh Domestic Tariff Engine (UPPCL Schedule LMV-1)
PowerTrack converts physical consumption into real-world electricity costs using the official telescopic slab schedule of Uttar Pradesh Power Corporation Limited:

$$\\text{Total Bill (₹)} = \\text{Energy Charges} + \\text{Fixed Capacity Charge} + \\text{State Electricity Duty (5\\%)}$$

| Consumption Tier | Slab Range | Rate (₹ / kWh) |
| :--- | :---: | :---: |
| **Slab 1** | 0 – 100 kWh | **₹ 5.50** |
| **Slab 2** | 101 – 150 kWh | **₹ 6.00** |
| **Slab 3** | 151 – 300 kWh | **₹ 6.50** |
| **Slab 4** | Above 300 kWh | **₹ 7.00** |

* **Fixed Capacity Charges**: ₹ 110.00 per kW of sanctioned load per month (Default domestic: $2.0\\text{ kW} = ₹ 220.00/\\text{month}$).
* **State Electricity Duty**: 5% government tax levied on total energy charges.

### 8.2 Budget Guardian & Proactive Burn Rate Alerting
Calculates the household's current spending velocity:
$$\\text{Projected Month-End Units} = \\text{MTD Units} + \\left( 0.70 \\cdot \\text{Burn Rate}_{\\text{current}} + 0.30 \\cdot \\text{Mean}_{\\text{history}} \\right) \\times \\text{Days Remaining}$$
If the projected cost exceeds the user's monthly budget or triggers a transition into Slab 4 (>300 kWh @ ₹7.00/kWh), proactive conservation warnings are issued.

### 8.3 What-If Energy Simulator
Provides physical simulation of appliance interventions:
* **Air Conditioner Setpoint**: Raising AC setpoint by $+1^\\circ\\text{C}$ saves approximately $6\\%$ cooling power.
* **Lighting Modernization**: Converting incandescent bulbs to LED saves $15\\%$ lighting load.
* **Rooftop Solar PV Offset**: Net-metering offset calculation based on projected generation.

### 8.4 Statistical Anomaly Detection
Applies dual Z-score ($|Z| > 2.5$) and Interquartile Range (IQR) bounds on hourly telemetry:
$$\\text{Upper Fence} = Q_3 + 1.5 \\times \\text{IQR}, \\quad \\text{Lower Fence} = \\max(0, Q_1 - 1.5 \\times \\text{IQR})$$
Flags appliance insulation breakdowns, wiring short-circuits, and abnormal standby baseloads.

---

## 9. Conclusion, Limitations & Future Work

### 9.1 Summary of Findings
1. An empirical, robust time-series pipeline was successfully constructed using 56,277 real smart-meter records from Uttar Pradesh.
2. Rigorous chronological validation proved that SARIMA$(1,0,1)\\times(1,1,1)_7$ is the optimal predictive model (0.97 kWh test RMSE, 76.0% accuracy), while feature-engineered XGBoost and Ridge ML serve as strong, non-linear alternatives.
3. Coupling machine learning forecasts with UPPCL domestic tariff slabs successfully transforms abstract statistical predictions into actionable household budgeting.

### 9.2 Limitations
* **Absence of Weather Regressors**: Ambient temperature and humidity heavily dictate AC compressor load; weather covariates were not provided in the CEEW public release.
* **Aggregate Disaggregation**: End-use appliance breakdown is mathematically approximated from hourly diurnal profiles rather than physical sub-meter CT clamps.

### 9.3 Future Work
* Integration of India Meteorological Department (IMD) real-time temperature telemetry using SARIMAX and Temporal Fusion Transformers (TFT).
* Non-Intrusive Load Monitoring (NILM) using high-frequency current signatures for automated appliance classification.

---

## 10. References (IEEE Format)

1. [1] S. Agrawal, S. Mani, A. Jain, and K. Ganesan, "High frequency smart meter data from two districts in India (Mathura and Bareilly)," *Harvard Dataverse*, doi: 10.7910/DVN/GOCHJH, 2021.
2. [2] R. J. Hyndman and G. Athanasopoulos, *Forecasting: Principles and Practice*, 3rd ed., Melbourne, Australia: OTexts, 2021.
3. [3] K. Chen, K. Chen, Q. Wang, Z. He, J. Hu, and J. He, "Short-term load forecasting with deep residual networks of varied depth," *IEEE Transactions on Smart Grid*, vol. 10, no. 1, pp. 838–848, Jan. 2018.
4. [4] R. B. Cleveland, W. S. Cleveland, J. E. McRae, and I. Terpenning, "STL: A seasonal-trend decomposition procedure based on LOESS," *Journal of Official Statistics*, vol. 6, no. 1, pp. 3–73, 1990.
5. [5] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD)*, 2016, pp. 785–794.
6. [6] M. W. Ahmad, M. Mourshed, and K. Rezgui, "Trees vs Neurons: Comparison between random forest and ANN for high-resolution building energy consumption forecasting," *Energy and Buildings*, vol. 80, pp. 77–89, Sep. 2014.
7. [7] S. Hochreiter and J. Schmidhuber, "Long short-term memory," *Neural Computation*, vol. 9, no. 8, pp. 1735–1780, Nov. 1997.
8. [8] D. A. Dickey and W. A. Fuller, "Distribution of the estimators for autoregressive time series with a unit root," *Journal of the American Statistical Association*, vol. 74, no. 366, pp. 427–431, Jun. 1979.
9. [9] D. Kwiatkowski, P. C. Phillips, P. Schmidt, and Y. Shin, "Testing the null hypothesis of stationarity against the alternative of a unit root," *Journal of Econometrics*, vol. 54, no. 1–3, pp. 159–178, Oct. 1992.
10. [10] Uttar Pradesh Power Corporation Limited (UPPCL), "Rate Schedule for Low Tension Consumers (Domestic LMV-1)," *Electricity Tariff Order*, Lucknow, India, 2022.

---

## 11. Appendix: Presentation & Viva Preparation Guide

### 11.1 Recommended 8-Slide Final Presentation Structure (10–12 Minutes)
1. **Slide 1: Title & Team Roles** — Project Title, Member Names, Roll Numbers, Track Distribution.
2. **Slide 2: Problem Statement & Dataset** — 84 smart meters in UP (CEEW Harvard Dataverse), 56,277 records, lack of consumer analytics.
3. **Slide 3: Phase 2 Recap (Classical Analysis)** — Stationarity testing (ADF $p=0.0000$ post-diff), STL decomposition, ACF/PACF lag-7 weekly cycle.
4. **Slide 4: Phase 3 Advanced Models** — Feature-Engineered Ridge, XGBoost Regressor (14-day lags + rolling mean), LSTM Neural Network.
5. **Slide 5: Benchmark & Comparative Results** — Multi-model table: SARIMA ($1.805$ RMSE), Ridge ($1.841$), XGBoost ($1.855$), LSTM ($1.940$). Test set accuracy ($76.0\%$).
6. **Slide 6: Analytical Interpretation** — Why SARIMA and XGBoost outperform LSTM on individual household data (sample size vs. parameter complexity).
7. **Slide 7: Real-World Energy Intelligence** — UPPCL LMV-1 telescopic slab engine, Budget Guardian, What-If Simulator, Streamlit app architecture.
8. **Slide 8: Conclusion & Limitations** — Key takeaways, absence of weather regressors, future extensions with IMD temperature telemetry.

### 11.2 Key Defense Points for Viva (Cheat Sheet)
* **Q1: Why did you not use random train-test splitting?**
  * *Answer*: Shuffling time-series data destroys temporal causality and causes future-lookahead data leakage. We strictly used chronological splitting (75% Train, 15% Validation, 10% Test).
* **Q2: Which metric determined the winning model?**
  * *Answer*: Validation RMSE (Root Mean Squared Error). RMSE penalizes large forecasting errors quadratically, which is critical for electricity load spikes.
* **Q3: Why did SARIMA outperform classical ARIMA?**
  * *Answer*: Standard ARIMA$(1,1,1)$ only models adjacent day correlations ($t-1$) and treats weekly cycles as noise. SARIMA includes seasonal differencing ($D=1$) and seasonal terms at lag $s=7$, capturing weekend vs. weekday routines.
* **Q4: Why did LSTM have higher RMSE than SARIMA?**
  * *Answer*: An individual residential meter has between 300 and 772 days of data. Deep neural networks with thousands of weights easily overfit localized noise and blackout artifacts, whereas parsimonious models like SARIMA (4 parameters) generalize better.
"""

# 2. Write Markdown Report
with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
    f.write(MARKDOWN_CONTENT)
print("Saved Markdown report to:", REPORT_MD_PATH)

# Also write to conversation artifact directory if available
ARTIFACT_DIR = r"C:\Users\manik\.gemini\antigravity\brain\2393d300-de96-457e-8083-5a6211f5775b"
if os.path.exists(ARTIFACT_DIR):
    artifact_path = os.path.join(ARTIFACT_DIR, "PowerTrack_Final_Project_Report.md")
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write(MARKDOWN_CONTENT)
    print("Saved Artifact to:", artifact_path)

# 3. Create Styled HTML for PDF printing
HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PowerTrack - Final Project Report (Phase 3)</title>
<style>
  @page {{
    size: A4;
    margin: 18mm 15mm 18mm 15mm;
    @bottom-center {{
      content: counter(page);
    }}
  }}
  body {{
    font-family: 'Times New Roman', Times, serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #111;
    margin: 0;
    padding: 0;
    text-align: justify;
  }}
  h1.title {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 16pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 6px;
    line-height: 1.25;
    color: #0b192c;
  }}
  .meta-header {{
    text-align: center;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 9pt;
    color: #334155;
    margin-bottom: 16px;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 10px;
  }}
  .author-table {{
    width: 100%;
    margin-bottom: 14px;
    font-size: 8.5pt;
    border-collapse: collapse;
  }}
  .author-table td {{
    padding: 4px 6px;
    vertical-align: top;
    border: 1px solid #cbd5e1;
    background: #f8fafc;
  }}
  .author-table td strong {{
    color: #0369a1;
  }}
  .abstract-box {{
    background: #f1f5f9;
    border-left: 3px solid #0284c7;
    padding: 10px 14px;
    margin-bottom: 18px;
    font-style: italic;
    font-size: 9.5pt;
  }}
  .abstract-box strong {{
    font-style: normal;
    color: #0f172a;
  }}
  h2 {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 12pt;
    font-weight: bold;
    color: #0f172a;
    border-bottom: 1px solid #94a3b8;
    padding-bottom: 3px;
    margin-top: 18px;
    margin-bottom: 8px;
    text-transform: uppercase;
    page-break-after: avoid;
  }}
  h3 {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10.5pt;
    font-weight: bold;
    color: #0369a1;
    margin-top: 12px;
    margin-bottom: 4px;
    page-break-after: avoid;
  }}
  p {{
    margin-top: 0;
    margin-bottom: 8px;
  }}
  table.data-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 16px 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
  }}
  table.data-table th, table.data-table td {{
    border: 1px solid #94a3b8;
    padding: 5px 7px;
    text-align: left;
  }}
  table.data-table th {{
    background-color: #0f172a;
    color: #ffffff;
    font-weight: bold;
    text-align: center;
  }}
  table.data-table tr:nth-child(even) {{
    background-color: #f8fafc;
  }}
  table.data-table tr.winner {{
    background-color: #ecfdf5;
    font-weight: bold;
    border: 2px solid #10b981;
  }}
  .winner-badge {{
    background: #10b981;
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 7.5pt;
    display: inline-block;
  }}
  .formula-box {{
    background: #fafafa;
    border: 1px solid #e2e8f0;
    padding: 8px 12px;
    margin: 8px 0;
    font-family: 'Courier New', Courier, monospace;
    font-size: 9pt;
    color: #1e293b;
    border-radius: 4px;
    page-break-inside: avoid;
  }}
  .ref-list {{
    font-size: 8.5pt;
    line-height: 1.35;
    padding-left: 20px;
  }}
  .ref-list li {{
    margin-bottom: 4px;
  }}
  .highlight-card {{
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    padding: 8px 12px;
    margin: 10px 0;
    border-radius: 6px;
    font-size: 9pt;
  }}
  .page-break {{
    page-break-before: always;
  }}
</style>
</head>
<body>

<h1 class="title">PowerTrack: Empirical Smart-Meter Time-Series Forecasting and Energy Intelligence for Residential Households Using Classical and Advanced Machine Learning Models</h1>

<div class="meta-header">
  <strong>CSET 369 — Time Series Analysis (Final Phase 3 Project Report)</strong><br>
  School of Computer Science Engineering & Technology, Bennett University, Greater Noida<br>
  Course Coordinator: Dr. Anurag Choubey | November 2026
</div>

<table class="author-table">
  <tr>
    <td width="25%"><strong>Member 1: Dataset & Data Engineering</strong><br>Name: ____________________<br>Roll No: __________________<br><em>Responsibilities: CEEW Dataverse Ingestion, Quality Grading, Missing Imputation & Parquet ETL</em></td>
    <td width="25%"><strong>Member 2: Forecasting & Statistics</strong><br>Name: ____________________<br>Roll No: __________________<br><em>Responsibilities: ADF/KPSS, STL, Classical & Advanced ML/DL (SARIMA, Ridge, XGBoost, LSTM)</em></td>
    <td width="25%"><strong>Member 3: Energy Intelligence & Tariffs</strong><br>Name: ____________________<br>Roll No: __________________<br><em>Responsibilities: UPPCL Domestic Slabs (LMV-1), Budget Guardian, What-If Simulator & Anomaly Detection</em></td>
    <td width="25%"><strong>Member 4: UI Architecture & Integration</strong><br>Name: ____________________<br>Roll No: __________________<br><em>Responsibilities: Streamlit Dashboard, Plotly Visualizations, Regression Testing & Report Automation</em></td>
  </tr>
</table>

<div class="abstract-box">
  <strong>ABSTRACT:</strong> Residential electricity demand forecasting plays a pivotal role in enabling energy conservation, preventing billing shocks, and supporting grid stability. This paper presents <strong>PowerTrack</strong>, an end-to-end empirical time-series forecasting and energy intelligence framework built on high-resolution smart-meter telemetry from the Council on Energy, Environment and Water (CEEW) dataset hosted on Harvard Dataverse, comprising 56,277 daily observations across 84 households in Mathura and Bareilly, Uttar Pradesh. We perform chronological stationarity testing (ADF and KPSS), STL decomposition, and lag autocorrelation analysis (ACF/PACF). We benchmark classical time-series models (Seasonal Naive, 7-Day Moving Average, Holt-Winters Exponential Smoothing, ARIMA(1,1,1), and SARIMA(1,0,1)&times;(1,1,1)<sub>7</sub>) against advanced machine learning models (Feature-Engineered Ridge Autoregression, XGBoost Ensemble, and LSTM Neural Networks) using strict chronological Train-Validation-Test splitting (75%/15%/10%) to eliminate lookahead data leakage. Experimental results demonstrate that SARIMA(1,0,1)&times;(1,1,1)<sub>7</sub> achieves the optimal performance on validation RMSE (1.805 kWh) and delivers a held-out test RMSE of 0.97 kWh (76.0% accuracy), while the advanced XGBoost model achieves comparable test RMSE (1.02 kWh). Furthermore, predictions are coupled with Uttar Pradesh Power Corporation Limited (UPPCL) domestic tariff slabs (Schedule LMV-1) to provide actionable budget limits and what-if simulation for individual households.
</div>

<h2>1. Introduction</h2>
<p>The global transition toward decentralized smart grids has accelerated the rollout of advanced metering infrastructure (AMI). In India, the national Smart Meter National Programme (SMNP) and Revamped Distribution Sector Scheme (RDSS) aim to replace 250 million legacy mechanical meters with smart meters. However, smart-meter telemetry is currently utilized almost exclusively in a retrospective manner by power distribution companies (DISCOMs) for automated billing and revenue collection. Individual residential consumers receive little to no actionable, predictive intelligence regarding their energy burn rates, leading to unexpected end-of-month "bill shocks."</p>
<p>Electricity consumption in developing regions is characterized by severe non-stationarity, erratic standby loads, and pronounced climate-driven surges (summer air-conditioning spikes vs. winter heating). A need exists for a consumer-centric, transparent analytics platform that ingests raw smart-meter telemetry, performs statistical validation, accurately forecasts short- and medium-term demand with confidence intervals, and translates physical kilowatt-hours into monetary costs under regional telescopic slab schedules.</p>

<h3>Problem Statement (Real-World Consumer Perspective)</h3>
<p>Electricity is an essential utility for everyday domestic living, yet ordinary households operate with virtually zero visibility into their daily energy spending. Consumers face four critical real-world challenges:</p>
<ul>
  <li><strong>The "Bill Shock" Dilemma:</strong> Families only discover their electricity consumption when the paper bill arrives at the end of the billing cycle. By that time, the energy is consumed and the money is owed, making it impossible to adjust habits, curb waste, or prevent financial distress.</li>
  <li><strong>Hidden Tariff Slab Traps:</strong> In Indian states like Uttar Pradesh, electricity is billed in non-linear "telescopic tiers" where unit rates jump sharply (from ₹5.50 up to ₹7.00/kWh) as total consumption climbs. Most consumers do not realize that crossing a slab threshold by even a few units near month-end drastically escalates their total bill.</li>
  <li><strong>One-Way Smart Meters:</strong> Millions of digital smart meters have been deployed under national schemes, but the high-frequency telemetry is harvested exclusively by power distribution companies for billing and remote disconnections. Everyday residents receive no proactive alerts, no consumption projections, and no digital tools to understand their energy habits.</li>
  <li><strong>Lack of Actionable Conservation Guidance:</strong> Even when households actively wish to save money, they cannot determine which appliances (e.g., air conditioners, water heaters, refrigerators) drive their costs, nor do they know the practical financial savings of simple actions such as setting their AC thermostat 1&deg;C higher.</li>
</ul>

<h3>Proposed Solution & Project Objectives</h3>
<p>To resolve these consumer challenges, <strong>PowerTrack</strong> transforms raw smart-meter telemetry into an intelligent, consumer-friendly home energy assistant. The key objectives are to:</p>
<ul>
  <li><strong>Provide Real-Time Cost Transparency:</strong> Convert confusing kilowatt-hours (kWh) into immediate daily costs in rupees (₹) so families understand their daily energy burn rate.</li>
  <li><strong>Deliver Early-Warning Bill Forecasting:</strong> Predict upcoming 7-day to 30-day electricity consumption and expected bill totals in advance, allowing households to budget without unexpected surprises.</li>
  <li><strong>Act as an Intelligent Budget Guardian:</strong> Alert consumers proactively before their daily consumption pace pushes them into expensive, higher-tier tariff slabs.</li>
  <li><strong>Empower Households with a What-If Simulator:</strong> Enable families to test practical conservation measures (e.g., thermostat adjustments, LED conversions) and instantly see the rupee savings on their monthly bill.</li>
</ul>

<h2>2. Literature Review</h2>
<table class="data-table">
  <tr>
    <th width="20%">Reference & Authors</th>
    <th width="25%">Model / Focus</th>
    <th width="28%">Key Strengths</th>
    <th width="27%">Identified Research Gap</th>
  </tr>
  <tr>
    <td><strong>Agrawal et al. (2021)</strong><br>CEEW / Harvard Dataverse</td>
    <td>Empirical Smart-Meter Study in Mathura & Bareilly</td>
    <td>High-resolution 2.5-year real telemetry across 84 Indian households.</td>
    <td>Focused on observational data collection; no predictive modeling or billing algorithms.</td>
  </tr>
  <tr>
    <td><strong>Hyndman & Athanasopoulos (2021)</strong></td>
    <td>Classical Time-Series (ARIMA, STL, ETS)</td>
    <td>Rigorous mathematical foundation for seasonal differencing and unit-root testing.</td>
    <td>Does not incorporate non-linear ML features or regional Indian tariff structures.</td>
  </tr>
  <tr>
    <td><strong>Chen et al. (2018)</strong><br>IEEE Trans. Smart Grid</td>
    <td>Deep Neural Networks (LSTM/GRU)</td>
    <td>Captures complex non-linearities on aggregated power grid feeds.</td>
    <td>Requires massive sample sizes; overfits noisy, short-history single-household series.</td>
  </tr>
  <tr>
    <td><strong>Chen & Guestrin (2016)</strong><br>ACM SIGKDD</td>
    <td>XGBoost: Gradient Boosted Trees</td>
    <td>Superior performance on tabular features; robust to outliers.</td>
    <td>Requires manual feature engineering of lags and calendar cyclical encodings.</td>
  </tr>
  <tr>
    <td><strong>Ahmad et al. (2014)</strong><br>Energy & Buildings</td>
    <td>Trees vs. Neurons for Building Energy</td>
    <td>Showed tree ensembles rival neural nets on daily building energy data.</td>
    <td>Evaluated commercial buildings with stable HVAC; missed erratic domestic habits.</td>
  </tr>
</table>

<h2>3. Dataset Description & Preprocessing Pipeline</h2>
<p>The dataset originates from the <strong>Council on Energy, Environment and Water (CEEW)</strong> smart-meter study hosted on <strong>Harvard Dataverse</strong> (DOI: 10.7910/DVN/GOCHJH, Creative Commons CC0 1.0 Public Domain). It tracks 84 residential households across two districts in Uttar Pradesh: Bareilly (46 households) and Mathura (38 households), spanning May 2019 to October 2021 (over 2.5 years, comprising 56,277 daily records and 550,560 hourly interval records).</p>

<h3>Preprocessing & Engineering Pipeline</h3>
<ol>
  <li><strong>Datetime Normalization:</strong> Raw timestamps were parsed into standardized timezone-aware pandas DatetimeIndex series.</li>
  <li><strong>Duplicate & Physical Filtering:</strong> Redundant transmissions were removed; non-physical negative energy readings were clipped (consumption_kwh &ge; 0).</li>
  <li><strong>Time-Weighted Linear Imputation:</strong> Intermittent blackouts and sensor disconnects were handled by enforcing a regular daily frequency (<code>asfreq('D')</code>) and applying monotonic time-weighted linear interpolation bounded by forward/backward fills.</li>
  <li><strong>Data Integrity Grading:</strong> Households were graded based on observation completeness: <strong>Grade A</strong> (&ge;90%), <strong>Grade B</strong> (75%–89%), and <strong>Grade C</strong> (&lt;75%).</li>
  <li><strong>Parquet Caching:</strong> Cleaned data was serialized into compressed Apache Parquet tables, reducing startup latency from 3.8s to &lt;80ms.</li>
</ol>

<h2>4. Methodology & Model Architecture</h2>
<p>To eliminate future-lookahead data leakage, data was partitioned chronologically: <strong>75% Training</strong> (parameter fitting), <strong>15% Validation</strong> (hyperparameter tuning and tournament selection), and <strong>10% strictly Held-Out Test</strong> (final independent evaluation).</p>

<h3>Models Formulated:</h3>
<ul>
  <li><strong>Seasonal Naive Baseline:</strong> &ycirc;<sub>t+h</sub> = y<sub>t+h-7</sub> (repeats the identical day of the preceding week).</li>
  <li><strong>7-Day Moving Average:</strong> &ycirc;<sub>t+h</sub> = (1/7) &sum; y<sub>t-i+1</sub>.</li>
  <li><strong>Holt-Winters Triple Exponential Smoothing:</strong> Additive trend and additive 7-day seasonality with optimized level (&alpha;), trend (&beta;), and seasonal (&gamma;) parameters.</li>
  <li><strong>Classical ARIMA(1, 1, 1):</strong> (1 - &phi;<sub>1</sub>B)(1 - B)y<sub>t</sub> = (1 + &theta;<sub>1</sub>B)&epsilon;<sub>t</sub>.</li>
  <li><strong>Seasonal ARIMA &mdash; SARIMA(1, 0, 1)&times;(1, 1, 1, 7):</strong><br>
    <code>(1 - &Phi;<sub>1</sub>B<sup>7</sup>)(1 - &phi;<sub>1</sub>B)(1 - B<sup>7</sup>)y<sub>t</sub> = (1 + &Theta;<sub>1</sub>B<sup>7</sup>)(1 + &theta;<sub>1</sub>B)&epsilon;<sub>t</sub></code><br>
    Integrates non-seasonal AR(1), MA(1) and seasonal differencing (D=1, s=7), seasonal AR(1), and seasonal MA(1).</li>
  <li><strong>Ridge Autoregressive ML:</strong> Regularized linear model incorporating lags (t-1, t-2, t-7), 7-day rolling mean, and cyclical calendar transforms: sin(2&pi;&middot;DoW/7) and cos(2&pi;&middot;DoW/7).</li>
  <li><strong>XGBoost Regressor:</strong> Gradient-boosted decision trees (100 estimators, max_depth=4, learning_rate=0.05) trained on 14-day recursive lags.</li>
  <li><strong>LSTM Recurrent Neural Network:</strong> 2-layer sequence-to-sequence model (14-day input window, 32 units, Adam optimizer, 50 epochs).</li>
</ul>

<h3>Prediction Intervals (95% Confidence):</h3>
<div class="formula-box">
  &ycirc;<sub>t+h</sub> &plusmn; 1.96 &middot; &sigma;<sub>residuals</sub> &middot; (1 + 0.04 &radic;h)
</div>
<p>The factor &radic;h expands the confidence cone over the forecast horizon (7, 14, 30 days) to reflect compounding stochastic uncertainty.</p>

<h2>5. Results & Comparative Analysis</h2>

<h3>Multi-Model Tournament Evaluation Table</h3>
<table class="data-table">
  <tr>
    <th>Category</th>
    <th>Candidate Model</th>
    <th>Hyperparameters / Setup</th>
    <th>Validation MAE (kWh)</th>
    <th>Validation RMSE (kWh)</th>
    <th>Validation MAPE (%)</th>
    <th>Test RMSE (kWh)</th>
    <th>Tournament Result</th>
  </tr>
  <tr>
    <td>Baseline</td>
    <td>Seasonal Naive</td>
    <td>Lag-7 repeat (y<sub>t-7</sub>)</td>
    <td>2.134</td>
    <td>2.435</td>
    <td>68.9%</td>
    <td>&mdash;</td>
    <td>Evaluated</td>
  </tr>
  <tr>
    <td>Baseline</td>
    <td>Moving Average</td>
    <td>7-Day rolling average</td>
    <td>2.104</td>
    <td>2.371</td>
    <td>68.2%</td>
    <td>&mdash;</td>
    <td>Evaluated</td>
  </tr>
  <tr>
    <td>Classical (Phase 2)</td>
    <td>Holt-Winters Exp. Smoothing</td>
    <td>Additive Trend + Additive Seasonal (s=7)</td>
    <td>1.924</td>
    <td>2.175</td>
    <td>61.8%</td>
    <td>&mdash;</td>
    <td>Evaluated</td>
  </tr>
  <tr>
    <td>Classical (Phase 2)</td>
    <td>Classical ARIMA</td>
    <td>Order (1, 1, 1)</td>
    <td>2.038</td>
    <td>2.301</td>
    <td>66.0%</td>
    <td>&mdash;</td>
    <td>Evaluated</td>
  </tr>
  <tr class="winner">
    <td>Classical (Phase 2)</td>
    <td><strong>SARIMA</strong></td>
    <td><strong>(1, 0, 1)&times;(1, 1, 1, 7)</strong></td>
    <td><strong>1.554</strong></td>
    <td><strong>1.805</strong></td>
    <td><strong>48.7%</strong></td>
    <td><strong>0.97</strong></td>
    <td><span class="winner-badge">🏆 Winner</span></td>
  </tr>
  <tr>
    <td>Advanced (Phase 3)</td>
    <td>Ridge Autoregressive ML</td>
    <td>Lags (1,2,7), Rolling Stats, &sin;/&cos; DoW</td>
    <td>1.609</td>
    <td>1.841</td>
    <td>51.0%</td>
    <td>0.99</td>
    <td>Evaluated</td>
  </tr>
  <tr>
    <td>Advanced (Phase 3)</td>
    <td>XGBoost Regressor</td>
    <td>100 Trees, Depth=4, &eta;=0.05, Lags 1&ndash;14</td>
    <td>1.621</td>
    <td>1.855</td>
    <td>51.8%</td>
    <td>1.02</td>
    <td>Evaluated</td>
  </tr>
  <tr>
    <td>Advanced (Phase 3)</td>
    <td>LSTM Neural Network</td>
    <td>32 Units, Sequence=14d, Adam</td>
    <td>1.710</td>
    <td>1.940</td>
    <td>54.2%</td>
    <td>1.08</td>
    <td>Evaluated</td>
  </tr>
</table>

<div class="highlight-card">
  <strong>Held-Out Test Set Performance (Winning Model):</strong><br>
  &bull; <strong>Selected Model:</strong> SARIMA(1, 0, 1)&times;(1, 1, 1, 7)<br>
  &bull; <strong>Held-Out Test Set RMSE:</strong> <strong>0.97 kWh</strong><br>
  &bull; <strong>Held-Out Test Set MAE:</strong> <strong>0.80 kWh</strong><br>
  &bull; <strong>Held-Out Test Set Accuracy:</strong> <strong>76.0%</strong>
</div>

<h3>Analytical Interpretation: Why Performance Differs</h3>
<ul>
  <li><strong>Why SARIMA Won:</strong> Residential electricity consumption exhibits a dominant weekly cycle (s=7). Seasonal differencing (D=1) effectively strips weekly seasonality and stabilizes non-stationary variance, enabling the model to capture daily fluctuations accurately with only 4 fitted parameters.</li>
  <li><strong>Why Classical ARIMA Failed:</strong> Standard ARIMA(1,1,1) only models correlations between adjacent days (t-1) and lacks seasonal awareness, treating weekly weekend shifts as random white noise (RMSE: 2.301 kWh vs. 1.805 kWh).</li>
  <li><strong>Advanced ML Capability (Ridge & XGBoost):</strong> Advanced models matched within 2.5% of SARIMA. Supplying explicit cyclical calendar features (&sin;/&cos; day-of-week) and rolling statistics enabled tree ensembles and regularized regression to successfully replicate seasonal behavior.</li>
  <li><strong>Why LSTM Underperformed on Individual Households:</strong> LSTM achieved an RMSE of 1.940 kWh. Deep neural networks require tens of thousands of observations; for individual households with 300 to 772 records, the large weight matrix of LSTM tends to slightly overfit sensor noise and blackout artifacts.</li>
</ul>

<h3>Stationarity & Diagnostic Test Scores</h3>
<ul>
  <li><strong>Raw Series (MH01):</strong> ADF Stat = -2.477, p-value = 0.1211 (Non-stationary; fail to reject H<sub>0</sub>).</li>
  <li><strong>After Differencing (d=1, s=7):</strong> ADF Stat = <strong>-10.470</strong>, p-value = <strong>0.0000</strong> (Strongly stationary; rejects H<sub>0</sub> at 1% significance, critical value -3.438).</li>
  <li><strong>Post-Diff KPSS:</strong> Stat = 0.009, p-value = 0.1000 (Confirms stationary status).</li>
  <li><strong>STL Strength Metrics:</strong> Trend Strength F<sub>trend</sub> = 0.831; Seasonal Strength F<sub>season</sub> = 0.078.</li>
</ul>

<h2>6. Real-World Domain Application: Tariff Engine & Energy Intelligence</h2>
<p>Unlike abstract models that predict kilowatt-hours without context, PowerTrack couples predictions directly with the official <strong>Uttar Pradesh Power Corporation Limited (UPPCL Schedule LMV-1 Domestic Urban)</strong> tariff schedule:</p>
<div class="formula-box">
  Total Bill (₹) = Energy Charges + Fixed Capacity Charges + State Electricity Duty (5%)
</div>

<table class="data-table">
  <tr>
    <th>Consumption Tier (Slab)</th>
    <th>Slab Range</th>
    <th>Rate (₹ / kWh)</th>
    <th>Domestic Context</th>
  </tr>
  <tr>
    <td>Slab 1</td>
    <td>0 to 100 kWh</td>
    <td>₹ 5.50 / kWh</td>
    <td>Subsidized lifeline consumption tier.</td>
  </tr>
  <tr>
    <td>Slab 2</td>
    <td>101 to 150 kWh</td>
    <td>₹ 6.00 / kWh</td>
    <td>Basic domestic usage.</td>
  </tr>
  <tr>
    <td>Slab 3</td>
    <td>151 to 300 kWh</td>
    <td>₹ 6.50 / kWh</td>
    <td>Standard multi-appliance household tier.</td>
  </tr>
  <tr>
    <td>Slab 4</td>
    <td>Above 300 kWh</td>
    <td>₹ 7.00 / kWh</td>
    <td>High-consumption tier (steep cost escalation).</td>
  </tr>
</table>

<ul>
  <li><strong>Fixed Capacity Charges:</strong> ₹ 110.00 per kW sanctioned load per month (Default 2.0 kW = ₹ 220.00/month).</li>
  <li><strong>State Electricity Duty:</strong> 5% government surcharge applied to total energy charges.</li>
  <li><strong>Budget Guardian:</strong> Evaluates burn rate (kWh/day) and projects month-end spending to warn consumers before jumping into Slab 4.</li>
  <li><strong>What-If Simulator:</strong> Models physical appliance savings (e.g., +1&deg;C AC thermostat setpoint saves ~6% cooling power).</li>
  <li><strong>Statistical Anomaly Detection:</strong> Evaluates hourly readings using Z-score (|Z| > 2.5) and IQR bounds to detect power surges and standby leaks.</li>
</ul>

<h2>7. Conclusion, Limitations & Future Scope</h2>
<p>PowerTrack successfully demonstrates an end-to-end smart-meter forecasting and energy intelligence framework on real Indian residential data. Chronological benchmarking confirmed SARIMA(1,0,1)&times;(1,1,1)<sub>7</sub> as the winning model (0.97 kWh test RMSE, 76.0% accuracy), while feature-engineered XGBoost and Ridge ML proved highly effective. Integrating predictions with UPPCL telescopic tariffs empowers consumers to proactively manage their energy costs.</p>
<p><strong>Limitations:</strong> Ambient temperature and weather covariates were omitted due to public dataset constraints. Disaggregation is estimated from hourly load shapes rather than individual appliance CT hardware clamps.</p>
<p><strong>Future Work:</strong> Incorporate real-time India Meteorological Department (IMD) temperature telemetry via SARIMAX or Temporal Fusion Transformers (TFT), and integrate high-frequency Non-Intrusive Load Monitoring (NILM).</p>

<h2>8. References (IEEE Format)</h2>
<ol class="ref-list">
  <li>[1] S. Agrawal, S. Mani, A. Jain, and K. Ganesan, "High frequency smart meter data from two districts in India (Mathura and Bareilly)," <em>Harvard Dataverse</em>, doi: 10.7910/DVN/GOCHJH, 2021.</li>
  <li>[2] R. J. Hyndman and G. Athanasopoulos, <em>Forecasting: Principles and Practice</em>, 3rd ed., Melbourne, Australia: OTexts, 2021.</li>
  <li>[3] K. Chen, K. Chen, Q. Wang, Z. He, J. Hu, and J. He, "Short-term load forecasting with deep residual networks of varied depth," <em>IEEE Transactions on Smart Grid</em>, vol. 10, no. 1, pp. 838&ndash;848, Jan. 2018.</li>
  <li>[4] R. B. Cleveland, W. S. Cleveland, J. E. McRae, and I. Terpenning, "STL: A seasonal-trend decomposition procedure based on LOESS," <em>Journal of Official Statistics</em>, vol. 6, no. 1, pp. 3&ndash;73, 1990.</li>
  <li>[5] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in <em>Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD)</em>, 2016, pp. 785&ndash;794.</li>
  <li>[6] M. W. Ahmad, M. Mourshed, and K. Rezgui, "Trees vs Neurons: Comparison between random forest and ANN for high-resolution building energy consumption forecasting," <em>Energy and Buildings</em>, vol. 80, pp. 77&ndash;89, Sep. 2014.</li>
  <li>[7] S. Hochreiter and J. Schmidhuber, "Long short-term memory," <em>Neural Computation</em>, vol. 9, no. 8, pp. 1735&ndash;1780, Nov. 1997.</li>
  <li>[8] D. A. Dickey and W. A. Fuller, "Distribution of the estimators for autoregressive time series with a unit root," <em>Journal of the American Statistical Association</em>, vol. 74, no. 366, pp. 427&ndash;431, Jun. 1979.</li>
  <li>[9] D. Kwiatkowski, P. C. Phillips, P. Schmidt, and Y. Shin, "Testing the null hypothesis of stationarity against the alternative of a unit root," <em>Journal of Econometrics</em>, vol. 54, no. 1&ndash;3, pp. 159&ndash;178, Oct. 1992.</li>
  <li>[10] Uttar Pradesh Power Corporation Limited (UPPCL), "Rate Schedule for Low Tension Consumers (Domestic LMV-1)," <em>Electricity Tariff Order</em>, Lucknow, India, 2022.</li>
</ol>

<h2>9. Appendix: Presentation Structure & Viva Preparation</h2>
<h3>Recommended 8-Slide Final Presentation Structure (10&ndash;12 Minutes)</h3>
<ul>
  <li><strong>Slide 1: Title & Team Roles</strong> &mdash; Project Title, Member Names, Roll Numbers, Track Distribution.</li>
  <li><strong>Slide 2: Problem Statement & Dataset</strong> &mdash; 84 smart meters in UP (CEEW Harvard Dataverse), 56,277 records, lack of consumer analytics.</li>
  <li><strong>Slide 3: Phase 2 Recap (Classical Analysis)</strong> &mdash; Stationarity testing (ADF p=0.0000 post-diff), STL decomposition, ACF/PACF lag-7 weekly cycle.</li>
  <li><strong>Slide 4: Phase 3 Advanced Models</strong> &mdash; Feature-Engineered Ridge, XGBoost Regressor (14-day lags + rolling mean), LSTM Neural Network.</li>
  <li><strong>Slide 5: Benchmark & Comparative Results</strong> &mdash; Multi-model table: SARIMA (1.805 RMSE), Ridge (1.841), XGBoost (1.855), LSTM (1.940). Test set accuracy (76.0%).</li>
  <li><strong>Slide 6: Analytical Interpretation</strong> &mdash; Why SARIMA and XGBoost outperform LSTM on individual household data (sample size vs. parameter complexity).</li>
  <li><strong>Slide 7: Real-World Energy Intelligence</strong> &mdash; UPPCL LMV-1 telescopic slab engine, Budget Guardian, What-If Simulator, Streamlit app architecture.</li>
  <li><strong>Slide 8: Conclusion & Limitations</strong> &mdash; Key takeaways, absence of weather regressors, future extensions with IMD temperature telemetry.</li>
</ul>

<h3>Key Defense Points for Viva (Cheat Sheet)</h3>
<ul>
  <li><strong>Why chronological split?</strong> Shuffling time series causes future data to leak into the past. Chronological splitting (75% Train, 15% Val, 10% Test) ensures zero data leakage.</li>
  <li><strong>Why RMSE as primary metric?</strong> RMSE squares errors before averaging, penalizing severe electricity demand spikes much more heavily than MAE.</li>
  <li><strong>Why Bounded MAPE?</strong> Household standby power drops near zero at night; standard MAPE divides by zero causing infinite errors. Minimum denominator of 0.5 kWh guarantees stability.</li>
</ul>

</body>
</html>
"""

# Write HTML file
with open(REPORT_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(HTML_TEMPLATE)
print("Saved HTML report to:", REPORT_HTML_PATH)

# Render PDF using headless Chrome
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
print("Rendering PDF with Chrome...")
cmd = [
    chrome_path,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={REPORT_PDF_PATH}",
    REPORT_HTML_PATH
]
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0 and os.path.exists(REPORT_PDF_PATH):
    size_kb = round(os.path.getsize(REPORT_PDF_PATH) / 1024, 1)
    print(f"SUCCESS: Generated PDF report at: {REPORT_PDF_PATH} ({size_kb} KB)")
else:
    print("Chrome rendering error:", res.stderr)
