# PowerTrack Data Dictionary & Dataset Documentation

## 1. Dataset Provenance & Attribution

- **Dataset Title**: High frequency smart meter data from two districts in India (Mathura and Bareilly)
- **Primary Source**: Council on Energy, Environment and Water (CEEW), hosted on Harvard Dataverse
- **Persistent DOI**: [doi:10.7910/DVN/GOCHJH](https://doi.org/10.7910/DVN/GOCHJH)
- **Authors**: Shalu Agrawal, Sunil Mani, Abhishek Jain, Karthik Ganesan (CEEW, 2021)
- **License**: **Creative Commons Zero (CC0 1.0) Public Domain Dedication** — Free for research, modification, and production applications without restriction.
- **Coverage**: Urban residential smart meters installed across Mathura and Bareilly districts in Uttar Pradesh, India.
- **Collection Window**: May 2019 through October 2021 (over 2.5 years of continuous smart-meter monitoring).

---

## 2. Dataset Audit & Comparative Analysis

| Attribute | Legacy File (`electricity_bill_dataset.csv`) | New Smart-Meter Dataset (`ceew_smart_meter/`) |
| :--- | :--- | :--- |
| **Target Unit** | Aggregated appliance counts per city/company | **Individual Household Smart-Meter (`household_id`)** |
| **Temporal Granularity** | Integer Month (1-12) without dates | **Continuous Timestamps (3-minute, hourly, daily)** |
| **Observation Count** | 45,345 synthetic/tabular rows | **56,277 daily records + 550,560 3-minute records** |
| **Unique Meters** | 0 (No meter/household identifier) | **84 Unique Indian Households (38 Mathura, 46 Bareilly)** |
| **Bill Calculation** | Direct product: `MonthlyHours × TariffRate` | **True metered kWh with applicable UPPCL Tariff Slabs** |
| **Suitability for Time Series** | **Unsuitable** (no time index or meter identity) | **Production-Ready for Classical Time Series & Forecasting** |

---

## 3. Data Schema & Field Definitions

### A. Daily Household Series (`households_daily.parquet`)
| Column Name | Data Type | Physical Unit | Description |
| :--- | :--- | :--- | :--- |
| `household_id` | String | Identifier | Anonymized unique household smart meter ID (e.g. `MH01` to `MH38`, `BR02` to `BR46`). |
| `city` | String | Categorical | Geographic location (`Mathura` or `Bareilly`, Uttar Pradesh, India). |
| `date` | Date (`YYYY-MM-DD`) | Temporal | Exact calendar date of measurement. |
| `consumption_kwh` | Float64 | kWh (Kilowatt-hours) | Measured daily interval energy consumption. |
| `is_imputed` | Boolean | Flag | Indicates whether the day was interpolated (`True`) or original metered record (`False`). |

### B. High-Frequency Hourly Series (`households_hourly.parquet`)
| Column Name | Data Type | Physical Unit | Description |
| :--- | :--- | :--- | :--- |
| `timestamp` | Datetime64 (`UTC/IST`) | Temporal | 1-hour interval start timestamp (`YYYY-MM-DD HH:00:00`). |
| `household_id` | String | Identifier | Anonymized household smart meter ID. |
| `city` | String | Categorical | District name (`Mathura`). |
| `hourly_kwh` | Float64 | kWh | Aggregated active electrical energy consumed over the 60-minute window. |
| `power_kw` | Float64 | kW | Average active load demand across the hour ($1\text{ kWh} / 1\text{ h} = 1\text{ kW}$). |
| `voltage_v` | Float64 | Volts (V) | Mean grid line voltage recorded by the smart meter (Nominal: 230V, range 180V–270V). |
| `current_a` | Float64 | Amperes (A) | Mean current draw across the hour. |
| `frequency_hz` | Float64 | Hertz (Hz) | Mean grid frequency (Nominal: 50.0 Hz). |

### C. Household Metadata & Quality Index (`households_meta.parquet`)
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `household_id` | String | Household smart meter identifier. |
| `city` | String | District of installation (`Mathura` or `Bareilly`). |
| `start_date` | Date | First recorded smart meter reading. |
| `end_date` | Date | Last recorded smart meter reading. |
| `total_calendar_days` | Integer | Total span of the calendar period in days. |
| `recorded_days` | Integer | Number of valid raw meter readings collected. |
| `missing_days` | Integer | Count of missing days requiring time-weighted interpolation. |
| `completeness_pct` | Float64 | Percentage of calendar days with original recorded data. |
| `mean_daily_kwh` | Float64 | Household historical average daily electricity usage. |
| `std_daily_kwh` | Float64 | Household daily consumption volatility. |
| `data_quality_grade` | String | Data quality rating: Grade A ($\ge 90\%$), Grade B ($\ge 75\%$), Grade C ($< 75\%$). |

---

## 4. Preprocessing, Cleaning, and Aggregation Methodology

1. **Meter Anonymization & Standardization**: Meter codes stripped of formatting artifacts and standardized to alphanumeric tokens (`MHxx` for Mathura, `BRxx` for Bareilly).
2. **Chronological Sorting & Integrity**: Every household series is validated for chronological monotonicity. Duplicate timestamps on identical meters are identified and deduplicated.
3. **Regular Resampling**: Daily records are reindexed to a continuous daily calendar (`freq='D'`).
4. **Time-Weighted Interpolation**: Minor transmission and telemetry dropouts are imputed using monotonic time-weighted linear interpolation bounded by forward/backward fills.
5. **Physical Plausibility Bounds**: Energy readings are verified non-negative (`consumption_kwh >= 0.0`). Extreme values are audited against physical smart meter capabilities.
6. **Separation of Raw and Processed**: Raw files remain untouched in `data/ceew_smart_meter/`; processed fast Parquet files reside in `data/processed/`.

