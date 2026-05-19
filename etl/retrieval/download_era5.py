import os
import json
import calendar
import cdsapi

# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

METADATA_FILE = os.path.join(
    BASE_DIR,
    "metadata",
    "etl",
    "karonga_era5_etl.json"
)

# --------------------------------------------------
# LOAD ETL METADATA
# --------------------------------------------------

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    meta = json.load(f)

DATASET = meta["dataset"]
VARIABLES = meta["variables"]

START_YEAR = meta["temporal_coverage"]["start_year"]
END_YEAR = meta["temporal_coverage"]["end_year"]

bbox = meta["spatial_coverage"]

AREA = [
    bbox["north"],
    bbox["west"],
    bbox["south"],
    bbox["east"]
]

OUTPUT_DIR = os.path.join(BASE_DIR, meta["output_directory"])
os.makedirs(OUTPUT_DIR, exist_ok=True)

if meta["times"] == "hourly":
    TIMES = [f"{h:02d}:00" for h in range(24)]
else:
    TIMES = meta["times"]

# --------------------------------------------------
# CDS CLIENT
# --------------------------------------------------
# Uses your .cdsapirc file automatically.
# Do NOT hardcode your API key in GitHub.

client = cdsapi.Client()

# --------------------------------------------------
# DOWNLOAD FUNCTION
# --------------------------------------------------

def download_era5():
    print("[INFO] Metadata-driven ERA5 download started")
    print("[INFO] Dataset:", DATASET)
    print("[INFO] Variables:", VARIABLES)
    print("[INFO] Years:", START_YEAR, "-", END_YEAR)
    print("[INFO] Area:", AREA)
    print("[INFO] Output:", OUTPUT_DIR)

    for var in VARIABLES:
        for year in range(START_YEAR, END_YEAR + 1):
            for month in range(1, 13):

                year_str = str(year)
                month_str = f"{month:02d}"

                _, last_day = calendar.monthrange(year, month)
                days = [f"{d:02d}" for d in range(1, last_day + 1)]

                out_file = os.path.join(
                    OUTPUT_DIR,
                    f"{var}_{year_str}_{month_str}.nc"
                )

                if os.path.exists(out_file):
                    print(f"[SKIP] {out_file}")
                    continue

                print(f"[DOWNLOAD] {var} {year_str}-{month_str}")

                request = {
                    "product_type": ["reanalysis"],
                    "variable": [var],
                    "year": [year_str],
                    "month": [month_str],
                    "day": days,
                    "time": TIMES,
                    "data_format": meta["data_format"],
                    "download_format": meta["download_format"],
                    "area": AREA
                }

                client.retrieve(DATASET, request).download(out_file)

                print(f"[DONE] {out_file}")

# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":
    download_era5()