# PowerTrack: Empirical Smart-Meter Time-Series Forecasting and Energy Intelligence for Residential Households Using Classical and Advanced Machine Learning Models

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
Residential electricity demand forecasting is critical for energy efficiency, preventing unexpected utility bill shocks, and enabling demand-side management. This project presents **PowerTrack**, an end-to-end empirical time-series forecasting and energy intelligence platform built on authentic smart-meter data from the Council on Energy, Environment and Water (CEEW) study, hosted on Harvard Dataverse (56,277 daily records across 84 households in Mathura and Bareilly, Uttar Pradesh). We investigate statistical properties using Augmented Dickey-Fuller (ADF), KPSS tests, and LOESS-based STL decomposition, identifying pronounced 7-day cyclical rhythms ($s=7$). A competitive benchmark is conducted comparing classical statistical models (Seasonal Naive, 7-Day Moving Average, Holt-Winters Exponential Smoothing, ARIMA(1,1,1), and SARIMA$(1,0,1)\times(1,1,1)_7$) against advanced machine-learning and deep-learning architectures (Feature-Engineered Ridge Autoregression, XGBoost Regressor, and LSTM Neural Networks) under strict chronological Train-Validation-Test splitting (75%/15%/10%) to prevent lookahead leakage. Empirical evaluations show that SARIMA$(1,0,1)\times(1,1,1)_7$ achieves the lowest validation RMSE (1.805 kWh) and held-out test RMSE of 0.97 kWh (76.0% accuracy), while XGBoost matches closely (test RMSE: 1.02 kWh). Forecasts are coupled with Uttar Pradesh Power Corporation Limited (UPPCL) telescopic tariff slabs (Schedule LMV-1) to deliver proactive budget alerts and simulate appliance energy savings.

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
   $$\text{Completeness (\%)} = \frac{\text{Recorded Days}}{\text{Total Calendar Days}} \times 100$$
   * **Grade A**: Completeness $\ge 90\%$ (Highest reliability).
   * **Grade B**: Completeness between $75\%$ and $89.9\%$.
   * **Grade C**: Completeness $< 75\%$ (Meters subject to prolonged disconnects).
5. **High-Performance Parquet Storage**: Raw files were transformed and serialized into Apache Parquet columnar binary storage (`households_daily.parquet`), reducing query and cache load times from 3.8 seconds to under 80 milliseconds.

---

## 5. Statistical Diagnostics & Methodology

### 5.1 Stationarity Testing & Differencing
Classical models (ARIMA/SARIMA) require stationarity—constant mean, constant variance, and autocovariance dependent only on temporal lag.

#### 1. Augmented Dickey-Fuller (ADF) Test:
* **Null Hypothesis ($H_0$)**: Series possesses a unit root (Non-Stationary).
* **Alternative Hypothesis ($H_1$)**: Series has no unit root (Stationary).
* Test regression: $\Delta y_t = \alpha + \beta t + \gamma y_{t-1} + \sum_{i=1}^p \delta_i \Delta y_{t-i} + \epsilon_t$. Reject $H_0$ if $p < 0.05$.

#### 2. KPSS Test:
* **Null Hypothesis ($H_0$)**: Series is trend-stationary.
* **Alternative Hypothesis ($H_1$)**: Series is non-stationary (Unit root exists).
* Fail to reject $H_0$ if $p \ge 0.05$.

#### Stationarity Experimental Results (Sample Household MH01 & BR04):
* **Raw Consumption (MH01)**: ADF Stat = $-2.477$, $p = 0.1211$ (Non-stationary; fails to reject $H_0$).
* **After Differencing ($d=1, s=7$)**: ADF Stat = **$-10.470$**, $p = 0.0000$ (Strongly stationary; rejects $H_0$ at 1% significance, critical value $-3.438$).
* **Post-Diff KPSS**: Stat = $0.009$, $p = 0.1000$ (Confirms stationarity).

### 5.2 LOESS Seasonal-Trend Decomposition (STL)
Decomposes daily electricity usage into three distinct additive components:
$$Y_t = T_t + S_t + R_t$$
* **Trend ($T_t$)**: Captures seasonal climatic variations (summer AC cooling vs. winter baselines). STL Trend Strength $F_{\text{trend}} = 0.831$.
* **Seasonality ($S_t$)**: Captures the recurring 7-day diurnal rhythm. STL Seasonal Strength $F_{\text{season}} = 0.078$.
* **Residuals ($R_t$)**: Random daily variance and temporary behavioral deviations.

### 5.3 Autocorrelation (ACF) & Partial Autocorrelation (PACF)
* ACF indicates significant serial correlation extending across 30 lags, with marked harmonic peaks at Lags 7, 14, 21, and 28.
* PACF displays a prominent cutoff spike at Lag 1 and a secondary spike at Lag 7, proving that household consumption is heavily governed by immediate yesterday's usage ($t-1$) and the same day of the prior week ($t-7$).

---

## 6. Model Formulation & Implementation

### 6.1 Chronological Data Splitting (Zero Lookahead Leakage)
To ensure mathematical integrity, random splitting (e.g. k-fold or random train_test_split) was strictly rejected. Data was divided chronologically:
$$\underbrace{\text{Training Set (75\%)}}_{\text{Model parameter estimation}} \longrightarrow \underbrace{\text{Validation Set (15\%)}}_{\text{Hyperparameter tuning & tournament selection}} \longrightarrow \underbrace{\text{Held-Out Test Set (10\%)}}_{\text{Final independent evaluation}}$$

### 6.2 Candidate Models Formulated

#### Classical Models (Phase 2):
1. **Seasonal Naive Baseline (Lag-7)**:
   $$\hat{y}_{t+h} = y_{t+h-7}$$
2. **7-Day Moving Average**:
   $$\hat{y}_{t+h} = \frac{1}{7} \sum_{i=1}^7 y_{t-i+1}$$
3. **Holt-Winters Triple Exponential Smoothing**:
   Additive trend and additive seasonal smoothing with seasonal period $m=7$:
   $$\ell_t = \alpha(y_t - s_{t-m}) + (1-\alpha)(\ell_{t-1} + b_{t-1}), \quad b_t = \beta(\ell_t - \ell_{t-1}) + (1-\beta)b_{t-1}, \quad s_t = \gamma(y_t - \ell_t) + (1-\gamma)s_{t-m}$$
4. **Classical ARIMA$(1, 1, 1)$**:
   $$(1 - \phi_1 B)(1 - B) y_t = (1 + \theta_1 B)\epsilon_t$$
5. **Seasonal ARIMA — SARIMA$(1, 0, 1) \times (1, 1, 1, 7)$**:
   $$(1 - \Phi_1 B^7)(1 - \phi_1 B)(1 - B^7) y_t = (1 + \Theta_1 B^7)(1 + \theta_1 B)\epsilon_t$$
   Enforces non-seasonal AR(1), seasonal differencing $D=1$ at period $s=7$, seasonal AR(1), and seasonal MA(1).

#### Advanced Models (Phase 3):
6. **Feature-Engineered Ridge Autoregressive ML**:
   Constructs feature matrix $X = [y_{t-1}, y_{t-2}, y_{t-7}, \text{roll\_mean}_7, \sin(2\pi \cdot \text{DoW}/7), \cos(2\pi \cdot \text{DoW}/7)]$.
   Solves $L_2$-regularized objective: $\min_w \|y - Xw\|_2^2 + \alpha \|w\|_2^2$ with $\alpha=1.0$.
7. **XGBoost Regressor (Gradient Boosted Decision Trees)**:
   Builds an ensemble of regression trees minimizing regularized gradient loss:
   $$\mathcal{L}^{(t)} = \sum_{i=1}^n \left[ g_i f_t(x_i) + \frac{1}{2} h_i f_t^2(x_i) \right] + \Omega(f_t)$$
   Tuned hyperparameters: `n_estimators=100`, `max_depth=4`, `learning_rate=0.05`, `subsample=0.85`.
8. **LSTM Neural Network (Deep Recurrent Sequence Model)**:
   Uses input, forget, and output gating mechanisms:
   $$f_t = \sigma(W_f [h_{t-1}, x_t] + b_f), \quad i_t = \sigma(W_i [h_{t-1}, x_t] + b_i), \quad h_t = o_t \odot \tanh(C_t)$$
   Tuned structure: 14-day lookback sequence, 32 hidden recurrent units, Adam optimizer, learning rate $0.001$, batch size 16, 50 epochs.

### 6.3 Evaluation Metrics
1. **Mean Absolute Error (MAE)**:
   $$\text{MAE} = \frac{1}{n} \sum_{t=1}^n |y_t - \hat{y}_t|$$
2. **Root Mean Squared Error (RMSE)** (Tournament Selection Metric):
   $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{t=1}^n (y_t - \hat{y}_t)^2}$$
3. **Bounded Mean Absolute Percentage Error (MAPE)**:
   $$\text{MAPE} = \frac{1}{n} \sum_{t=1}^n \frac{|y_t - \hat{y}_t|}{\max(y_t, 0.5)} \times 100\%$$
   *(The minimum denominator threshold of 0.5 kWh prevents division-by-zero during low standby night loads).*

### 6.4 Prediction Interval Calculation (95% Confidence)
To convey forecast uncertainty over multi-day horizons ($h=1, \dots, 30$), residual standard deviation $\sigma$ was scaled by horizon factor $\sqrt{h}$:
$$\hat{y}_{t+h} \pm 1.96 \cdot \sigma_{\text{residuals}} \cdot (1 + 0.04\sqrt{h})$$

---

## 7. Results & Comparative Analysis

### 7.1 Multi-Model Performance Benchmark Table

| Model Classification | Candidate Model | Hyperparameters / Setup | Validation MAE (kWh) | Validation RMSE (kWh) | Validation MAPE (%) | Test RMSE (kWh) | Tournament Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | Seasonal Naive | $y_t = y_{t-7}$ (Lag-7 repeat) | 2.134 | 2.435 | 68.9% | — | Evaluated |
| **Baseline** | Moving Average | 7-Day Rolling Historical Mean | 2.104 | 2.371 | 68.2% | — | Evaluated |
| **Classical (Phase 2)** | Holt-Winters | Additive Trend + Seasonality ($s=7$) | 1.924 | 2.175 | 61.8% | — | Evaluated |
| **Classical (Phase 2)** | ARIMA | Order $(1, 1, 1)$ | 2.038 | 2.301 | 66.0% | — | Evaluated |
| **Classical (Phase 2)** | **SARIMA** | **$(1, 0, 1) \times (1, 1, 1, 7)$** | **1.554** | **1.805** | **48.7%** | **0.97** | 🏆 **Selected Winner** |
| **Advanced (Phase 3)** | **Ridge Autoregressive ML** | Lags (1,2,7), Rolling Stats, $\sin/\cos$ DoW | **1.609** | **1.841** | **51.0%** | **0.99** | Evaluated |
| **Advanced (Phase 3)** | **XGBoost Regressor** | 100 Trees, Depth=4, $\eta=0.05$, Lags 1–14 | **1.621** | **1.855** | **51.8%** | **1.02** | Evaluated |
| **Advanced (Phase 3)** | **LSTM Recurrent Net** | 32 Units, Sequence=14d, Adam | **1.710** | **1.940** | **54.2%** | **1.08** | Evaluated |

### 7.2 Independent Held-Out Test Evaluation of Winning Model
* **Selected Winning Model**: $\text{SARIMA}(1, 0, 1) \times (1, 1, 1, 7)$
* **Held-Out Test MAE**: **0.80 kWh**
* **Held-Out Test RMSE**: **0.97 kWh**
* **Held-Out Test Set Accuracy**: **76.0%**

### 7.3 Detailed Discussion: Why Model Performance Differs
1. **Superiority of SARIMA over Classical ARIMA**: Classical ARIMA$(1,1,1)$ produced a validation RMSE of $2.301\text{ kWh}$, whereas SARIMA$(1,0,1)\times(1,1,1)_7$ achieved $1.805\text{ kWh}$ (a $21.5\%$ error reduction). Standard ARIMA only models adjacent sequential relationships ($t-1$) and treats weekly household rhythms as uncorrelated noise. SARIMA's seasonal differencing ($D=1, s=7$) completely stabilizes weekly variance.
2. **Competitive Performance of Advanced Models (Ridge & XGBoost)**: Ridge ML ($1.841\text{ RMSE}$) and XGBoost ($1.855\text{ RMSE}$) performed within $2.5\%$ of SARIMA. This proves that linear and tree-based machine learning models can closely match classical statistical models when provided with explicit cyclical encodings (sine and cosine day-of-week transforms) and multi-step lag features.
3. **Why LSTM Underperformed Relative to SARIMA on Single Household Data**: The LSTM network achieved an RMSE of $1.940\text{ kWh}$. While LSTM excels on large-scale time series (millions of data points), individual household meters have moderate observation spans (300 to 772 days). The high parameter count of LSTM causes it to learn spurious sensor noise and blackout artifacts, whereas the parsimonious parameter structure of SARIMA (only 4 parameters: $\phi_1, \theta_1, \Phi_1, \Theta_1$) provides superior generalization.

---

## 8. Real-World Domain Application: Tariff Engine & Energy Intelligence

### 8.1 Uttar Pradesh Domestic Tariff Engine (UPPCL Schedule LMV-1)
PowerTrack converts physical consumption into real-world electricity costs using the official telescopic slab schedule of Uttar Pradesh Power Corporation Limited:

$$\text{Total Bill (₹)} = \text{Energy Charges} + \text{Fixed Capacity Charge} + \text{State Electricity Duty (5\%)}$$

| Consumption Tier | Slab Range | Rate (₹ / kWh) |
| :--- | :---: | :---: |
| **Slab 1** | 0 – 100 kWh | **₹ 5.50** |
| **Slab 2** | 101 – 150 kWh | **₹ 6.00** |
| **Slab 3** | 151 – 300 kWh | **₹ 6.50** |
| **Slab 4** | Above 300 kWh | **₹ 7.00** |

* **Fixed Capacity Charges**: ₹ 110.00 per kW of sanctioned load per month (Default domestic: $2.0\text{ kW} = ₹ 220.00/\text{month}$).
* **State Electricity Duty**: 5% government tax levied on total energy charges.

### 8.2 Budget Guardian & Proactive Burn Rate Alerting
Calculates the household's current spending velocity:
$$\text{Projected Month-End Units} = \text{MTD Units} + \left( 0.70 \cdot \text{Burn Rate}_{\text{current}} + 0.30 \cdot \text{Mean}_{\text{history}} \right) \times \text{Days Remaining}$$
If the projected cost exceeds the user's monthly budget or triggers a transition into Slab 4 (>300 kWh @ ₹7.00/kWh), proactive conservation warnings are issued.

### 8.3 What-If Energy Simulator
Provides physical simulation of appliance interventions:
* **Air Conditioner Setpoint**: Raising AC setpoint by $+1^\circ\text{C}$ saves approximately $6\%$ cooling power.
* **Lighting Modernization**: Converting incandescent bulbs to LED saves $15\%$ lighting load.
* **Rooftop Solar PV Offset**: Net-metering offset calculation based on projected generation.

### 8.4 Statistical Anomaly Detection
Applies dual Z-score ($|Z| > 2.5$) and Interquartile Range (IQR) bounds on hourly telemetry:
$$\text{Upper Fence} = Q_3 + 1.5 \times \text{IQR}, \quad \text{Lower Fence} = \max(0, Q_1 - 1.5 \times \text{IQR})$$
Flags appliance insulation breakdowns, wiring short-circuits, and abnormal standby baseloads.

---

## 9. Conclusion, Limitations & Future Work

### 9.1 Summary of Findings
1. An empirical, robust time-series pipeline was successfully constructed using 56,277 real smart-meter records from Uttar Pradesh.
2. Rigorous chronological validation proved that SARIMA$(1,0,1)\times(1,1,1)_7$ is the optimal predictive model (0.97 kWh test RMSE, 76.0% accuracy), while feature-engineered XGBoost and Ridge ML serve as strong, non-linear alternatives.
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
