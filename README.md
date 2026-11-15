# PowerTrack — Household Smart-Energy Analytics Platform

**PowerTrack** is a production-style, consumer-facing household electricity monitoring, time-series analysis, forecasting, budget management, and bill audit platform. 

Powered by genuine smart-meter readings collected across urban households in **Mathura and Bareilly** (Uttar Pradesh, India) from the **Council on Energy, Environment and Water (CEEW)**, hosted on **Harvard Dataverse** (DOI: `10.7910/DVN/GOCHJH`, CC0 1.0 Public Domain).

---

## ⚡ Key Highlights & Core Capabilities

1. **Authentic Smart-Meter Dataset Replacement**:
   - Replaced synthetic/static data with **84 unique Indian residential smart meters** monitored across 2.5 years (May 2019 – Oct 2021).
   - Preserves 56,277 clean daily series and 550,560 3-minute high-frequency interval readings.
   - Clean separation of raw telemetry and fast cached Parquet tables.

2. **Full-Featured 9-View Application Interface**:
   - **⚡ Dashboard**: Real-time KPI summaries, interactive consumption trends, 24-hour diurnal patterns, weekly rhythms, and natural language insights.
   - **📊 Electricity Usage**: Multi-resolution resampling (Daily, Weekly, Monthly), cumulative energy consumption, statistical distribution diagnostics, and raw readings explorer.
   - **🔄 Consumption Patterns**: STL LOESS decomposition, dual stationarity testing (**ADF** & **KPSS**), differencing verification ($d=1, D=1$), ACF/PACF autocorrelation structure, and seasonal profiles.
   - **🔮 Forecasting Engine**: Chronologically split benchmark (70% Train, 15% Validation, 15% Test) comparing **Seasonal Naive**, **Moving Average (7-Day)**, **Holt-Winters Exponential Smoothing**, **ARIMA(1,1,1)**, and **SARIMA(1,0,1)(1,1,1)₇**. Generates out-of-sample forecasts with 95% confidence bounds.
   - **🛡️ Budget Guardian**: Live month-to-date spending tracking, daily burn rate calculation, projected end-of-month bill estimation, and daily allowance targets.
   - **🧾 Bill Analysis (Discrepancy Checker)**: Audits utility paper bills against smart-meter measured kWh and official **UPPCL LMV-1 Domestic Telescopic Tariff Slabs** (accounting for slab rates, fixed charges, and 5% electricity duty).
   - **💡 What-If Simulator**: Simulates energy-saving scenarios (AC runtime reduction, 5-Star BLDC fan upgrades, phantom load reduction) with physical wattage models and financial savings projections.
   - **📈 Data Quality Monitor**: Telemetry tracking, observation continuity, missing value audit, and data quality grading (Grade A/B/C) across all 84 meters.
   - **📑 Reports & Export**: Single-click export of complete academic/executive markdown reports and filtered CSV time series.

---

## 📁 System Architecture

```text
d:\time-series-project/
│
├── app.py                             # PowerTrack Streamlit Multi-Page Web Platform
├── requirements.txt                   # Production Python dependencies
├── DATA_DICTIONARY.md                 # Complete Data Dictionary & Schema Documentation
├── README.md                          # Project Documentation & Architecture
├── .gitignore                         # Git exclusion rules
│
├── data/
│   ├── ceew_smart_meter/              # Raw CEEW Indian Smart-Meter Data (Harvard Dataverse)
│   │   ├── CEEW_ReadMe.txt            # Dataset metadata & documentation
│   │   ├── Mathura_Aggregated.tab     # Mathura daily meter records
│   │   └── Bareilly_Aggregated.tab    # Bareilly daily meter records
│   └── processed/                     # High-performance Parquet caching layer
│       ├── households_daily.parquet   # 56,277 clean daily records across 84 households
│       ├── households_hourly.parquet  # Clean hourly aggregated series with power/voltage
│       ├── households_meta.parquet    # Household metadata, quality index, and metrics
│       └── households_diurnal_profiles.parquet # Empirical 24-hour diurnal load profiles
│
├── analysis/                          # Mathematical & Machine Learning Engines
│   ├── household_preprocessing.py     # Household access layer & chronological filtering
│   ├── forecasting.py                 # Time-series forecasting (Naive, MA, HW, ARIMA, SARIMA)
│   ├── anomaly_detection.py           # Statistical anomaly detection & baseline deviation
│   ├── billing_tariffs.py             # UPPCL tariff engine, Budget Guardian & What-If simulator
│   ├── eda.py                         # Summary stats & Plotly interactive chart themes
│   ├── trend.py                       # Rolling statistics & trend slope detection
│   ├── seasonality.py                 # Diurnal, weekly, and monthly seasonal engines
│   ├── decomposition.py               # STL LOESS decomposition & component strengths
│   ├── stationarity.py                # Dual ADF & KPSS hypothesis testing & differencing
│   ├── autocorrelation.py             # ACF & PACF stem plots & lag orders
│   └── insights.py                    # Natural language insight generation engine
│
├── utils/
│   ├── helpers.py                     # PowerTrack dark UI cards, badges, and styling
│   └── report_generator.py            # Academic & Executive report synthesis (.MD)
│
└── scripts/
    ├── audit_dataset.py               # Dataset validation and comparison script
    ├── process_household_data.py      # Reproducible ETL and preprocessing pipeline
    └── test_pipeline.py               # Comprehensive end-to-end integration test suite
```

---

## 🚀 Getting Started

### 1. Installation
Clone this repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Verify Pipeline & Run Tests
Run the comprehensive integration test suite verifying data loaders, forecasting models, anomaly detection, and billing slabs:
```bash
python scripts/test_pipeline.py
```

### 3. Launch the PowerTrack Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Forecasting Benchmark Results (Sample: Household MH01)

| Model Name | Validation MAE (kWh) | Validation RMSE (kWh) | Validation MAPE (%) | Test RMSE (kWh) | Test MAE (kWh) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **SARIMA (1,0,1)(1,1,1)₇** | **1.382** | **1.672** | **35.9%** | **1.108** | **0.879** |
| Moving Average (7-Day) | 2.191 | 2.762 | 60.4% | - | - |
| Seasonal Naive | 2.474 | 3.090 | 63.9% | - | - |
| ARIMA (1,1,1) | 2.583 | 3.162 | 70.0% | - | - |
| Holt-Winters Exp. Smoothing | 4.006 | 4.586 | 102.6% | - | - |

---

## 📜 License & Citation

- **Codebase License**: MIT License
- **Smart-Meter Data**: Council on Energy, Environment and Water (CEEW), hosted on Harvard Dataverse (`doi:10.7910/DVN/GOCHJH`), Creative Commons CC0 1.0 Public Domain Dedication.
