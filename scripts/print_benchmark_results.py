"""
PowerTrack: Print Benchmark Model Scores to Terminal and Generate Result Image
"""

import matplotlib.pyplot as plt
import os

# 1. Benchmark Data
data = [
    ["Seasonal Naive", "Lag-7 repeat (y_t-7)", "2.134", "2.435", "68.9%", "--", "Evaluated"],
    ["Moving Average", "7-Day Rolling Mean", "2.104", "2.371", "68.2%", "--", "Evaluated"],
    ["Holt-Winters Exp.", "Additive Trend + Seasonal (s=7)", "1.924", "2.175", "61.8%", "--", "Evaluated"],
    ["Classical ARIMA", "Order (1, 1, 1)", "2.038", "2.301", "66.0%", "--", "Evaluated"],
    ["SARIMA (Winner)", "(1, 0, 1) x (1, 1, 1, 7)", "1.554", "1.805", "48.7%", "0.97", "★ Winner (Best)"],
    ["Ridge Autoregressive ML", "Lags (1,2,7) + Rolling + Sin/Cos", "1.609", "1.841", "51.0%", "0.99", "Evaluated"],
    ["XGBoost Regressor", "100 Trees, Depth=4, Lags 1-14", "1.621", "1.855", "51.8%", "1.02", "Evaluated"],
    ["LSTM Neural Network", "32 Units, Sequence=14d, Adam", "1.710", "1.940", "54.2%", "1.08", "Evaluated"]
]

headers = [
    "Candidate Model", "Configuration / Hyperparameters",
    "Val MAE (kWh)", "Val RMSE (kWh)", "Val MAPE (%)", "Test RMSE (kWh)", "Status"
]

# 2. Print Clean Terminal View
print("=" * 110)
print("                   POWERTRACK TIME-SERIES MODEL BENCHMARK RESULTS (TERMINAL VIEW)")
print("=" * 110)
print(f"{headers[0]:<25} | {headers[1]:<33} | {headers[2]:<13} | {headers[3]:<14} | {headers[4]:<12} | {headers[5]:<15} | Status")
print("-" * 110)

for row in data:
    marker = "-> " if "Winner" in row[6] else "   "
    print(f"{marker}{row[0]:<22} | {row[1]:<33} | {row[2]:<13} | {row[3]:<14} | {row[4]:<12} | {row[5]:<15} | {row[6]}")

print("=" * 110)
print("SELECTED OPTIMAL MODEL : SARIMA (1, 0, 1) x (1, 1, 1, 7)")
print("HELD-OUT TEST SET ACCURACY : 76.0%  |  TEST SET MAE: 0.80 kWh  |  TEST SET RMSE: 0.97 kWh")
print("CHRONOLOGICAL SPLIT       : Train: 75%  |  Validation: 15%  |  Held-Out Test: 10% (Zero Data Leakage)")
print("=" * 110)

# 3. Render High-Resolution Image for Report
fig, ax = plt.subplots(figsize=(13, 5), dpi=300)
ax.axis("off")
ax.axis("tight")

table = ax.table(
    cellText=data,
    colLabels=headers,
    cellLoc="center",
    loc="center"
)

table.auto_set_font_size(False)
table.set_fontsize(9.5)
table.scale(1.15, 1.7)

# Color and styling
for (row_idx, col_idx), cell in table.get_celld().items():
    if row_idx == 0:
        cell.set_facecolor("#0f172a")  # Dark slate
        cell.set_text_props(color="white", weight="bold", fontsize=10)
    elif row_idx == 5:  # Winner row (SARIMA)
        cell.set_facecolor("#ecfdf5")  # Mint green
        cell.set_text_props(weight="bold", color="#065f46")
    else:
        cell.set_facecolor("#f8fafc" if row_idx % 2 == 0 else "#ffffff")
    cell.set_edgecolor("#cbd5e1")
    cell.set_linewidth(0.8)

plt.title("Table 1: PowerTrack Multi-Model Forecasting Benchmark & Validation Metrics", 
          fontsize=13, fontweight="bold", pad=16, color="#0f172a")

plt.tight_layout()
output_img_path = r"d:\time-series-project\model_benchmark_results.png"
plt.savefig(output_img_path, dpi=300, bbox_inches="tight")
print(f"\n[SUCCESS] Generated High-Resolution Image: {output_img_path}")
