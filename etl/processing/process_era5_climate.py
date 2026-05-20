import os
import glob
import numpy as np
import pandas as pd
import xarray as xr

# ============================================================
# PATHS
# ============================================================

BASE_DIR = r"C:\Users\HP\Desktop\karonga-ohdsi-gis-pipeline"

RAW_DIR = os.path.join(BASE_DIR, "raw", "era5")
OUT_DIR = os.path.join(BASE_DIR, "processed", "climate")

os.makedirs(OUT_DIR, exist_ok=True)

DAILY_FILE = os.path.join(OUT_DIR, "karonga_era5_daily_climate.csv")
MONTHLY_FILE = os.path.join(OUT_DIR, "karonga_era5_monthly_exposures.csv")

# ============================================================
# FUNCTIONS
# ============================================================

def get_time_column(df):
    for col in ["time", "valid_time", "date"]:
        if col in df.columns:
            return col
    raise ValueError("No time column found.")


def process_variable(pattern, variable_name):
    files = glob.glob(os.path.join(RAW_DIR, pattern))

    if not files:
        print(f"[WARNING] No files found for {variable_name}")
        return None

    daily_list = []

    for f in files:
        print(f"[PROCESSING] {f}")

        ds = xr.open_dataset(f)

        data_var = list(ds.data_vars)[0]

        df = ds[data_var].to_dataframe().reset_index()

        time_col = get_time_column(df)

        df["date"] = pd.to_datetime(df[time_col]).dt.date

        # area mean across all grid cells
        daily = (
            df.groupby("date")[data_var]
            .mean()
            .reset_index()
        )

        daily.columns = ["date", variable_name]

        daily_list.append(daily)

    final = pd.concat(daily_list, ignore_index=True)

    final["date"] = pd.to_datetime(final["date"])

    final = final.sort_values("date")

    return final


# ============================================================
# 1. READ DAILY VARIABLES
# ============================================================

print("[STEP 1] Processing ERA5 variables...")

temp = process_variable("*2m_temperature*.nc", "temperature_k")
dew = process_variable("*2m_dewpoint_temperature*.nc", "dewpoint_k")
precip = process_variable("*total_precipitation*.nc", "precipitation_m")
u10 = process_variable("*10m_u_component_of_wind*.nc", "u10")
v10 = process_variable("*10m_v_component_of_wind*.nc", "v10")

# ============================================================
# 2. MERGE DAILY DATA
# ============================================================

print("[STEP 2] Merging daily climate variables...")

dfs = [df for df in [temp, dew, precip, u10, v10] if df is not None]

daily = dfs[0]

for df in dfs[1:]:
    daily = daily.merge(df, on="date", how="outer")

daily = daily.sort_values("date")

# ============================================================
# 3. DERIVE DAILY INDICATORS
# ============================================================

print("[STEP 3] Deriving daily indicators...")

if "temperature_k" in daily.columns:
    daily["temperature_c"] = daily["temperature_k"] - 273.15

if "dewpoint_k" in daily.columns:
    daily["dewpoint_c"] = daily["dewpoint_k"] - 273.15

if "precipitation_m" in daily.columns:
    daily["precipitation_mm"] = daily["precipitation_m"] * 1000

if "u10" in daily.columns and "v10" in daily.columns:
    daily["wind_speed_ms"] = np.sqrt(daily["u10"]**2 + daily["v10"]**2)

# Relative humidity approximation
if "temperature_c" in daily.columns and "dewpoint_c" in daily.columns:
    daily["relative_humidity"] = 100 * (
        np.exp((17.625 * daily["dewpoint_c"]) / (243.04 + daily["dewpoint_c"]))
        /
        np.exp((17.625 * daily["temperature_c"]) / (243.04 + daily["temperature_c"]))
    )

# ============================================================
# 4. DEFINE FLOOD EXCEEDANCE
# ============================================================

print("[STEP 4] Defining 95th percentile flood threshold...")

threshold = daily["precipitation_mm"].quantile(0.95)

daily["flood_exceedance_day"] = (
    daily["precipitation_mm"] > threshold
).astype(int)

daily["flood_threshold_mm"] = threshold

# ============================================================
# 5. MONTHLY FLOOD INDICATORS
# ============================================================

print("[STEP 5] Creating monthly flood indicators...")

daily["month"] = daily["date"].dt.to_period("M").astype(str)

monthly = (
    daily.groupby("month")
    .agg(
        monthly_precipitation_mm=("precipitation_mm", "sum"),
        flood_event_count=("flood_exceedance_day", "sum"),
        flood_intensity_mm=("precipitation_mm", lambda x: x[x > threshold].mean()),
        mean_temperature_c=("temperature_c", "mean"),
        mean_relative_humidity=("relative_humidity", "mean"),
        mean_wind_speed_ms=("wind_speed_ms", "mean")
    )
    .reset_index()
)

monthly["flood_intensity_mm"] = monthly["flood_intensity_mm"].fillna(0)

# ============================================================
# 6. FLOOD DURATION
# ============================================================

print("[STEP 6] Calculating monthly flood duration...")

def longest_run(values):
    max_run = 0
    current = 0

    for v in values:
        if v == 1:
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0

    return max_run


duration = (
    daily.groupby("month")["flood_exceedance_day"]
    .apply(longest_run)
    .reset_index(name="flood_duration_days")
)

monthly = monthly.merge(duration, on="month", how="left")

# ============================================================
# 7. CREATE LAG VARIABLES
# ============================================================

print("[STEP 7] Creating lag variables...")

monthly = monthly.sort_values("month")

for col in [
    "flood_event_count",
    "flood_intensity_mm",
    "flood_duration_days",
    "monthly_precipitation_mm",
    "mean_temperature_c"
]:
    monthly[f"{col}_lag1"] = monthly[col].shift(1)
    monthly[f"{col}_lag2"] = monthly[col].shift(2)

# ============================================================
# 8. SAVE OUTPUTS
# ============================================================

daily.to_csv(DAILY_FILE, index=False)
monthly.to_csv(MONTHLY_FILE, index=False)

print("[DONE] Daily climate file:")
print(DAILY_FILE)

print("[DONE] Monthly exposure file:")
print(MONTHLY_FILE)

print("[INFO] Flood threshold mm:")
print(threshold)