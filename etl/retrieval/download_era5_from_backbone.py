import os
import json
import calendar
import cdsapi
import pandas as pd
import psycopg2

# ============================================================
# 1. DATABASE CONNECTION TO GAIACORE / GAIADB
# ============================================================

DB_CONFIG = {
    "dbname": "gaiacore",
    "user": "postgres",
    "password": "SuperSecret",
    "host": "localhost",
    "port": "5440"
}

DATASET_ID = "karonga_era5_climate_2015_2021"

# ============================================================
# 2. OUTPUT SETTINGS
# ============================================================

OUTPUT_DIR = r"C:\Users\HP\Desktop\karonga-ohdsi-gis-pipeline\raw\era5"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Hourly ERA5 data
TIMES = [f"{h:02d}:00" for h in range(24)]

# ============================================================
# 3. READ METADATA FROM GAIACORE BACKBONE
# ============================================================

def read_backbone_metadata():
    conn = psycopg2.connect(**DB_CONFIG)

    dataset_sql = """
        SELECT
            dataset_id,
            dataset_name,
            additional_properties,
            etl_metadata
        FROM backbone.data_source
        WHERE dataset_id = %s;
    """

    dataset = pd.read_sql(dataset_sql, conn, params=(DATASET_ID,))

    if dataset.empty:
        conn.close()
        raise ValueError(f"Dataset not found in backbone.data_source: {DATASET_ID}")

    row = dataset.iloc[0]

    additional_properties = row["additional_properties"]
    etl_metadata = row["etl_metadata"]

    if isinstance(additional_properties, str):
        additional_properties = json.loads(additional_properties)

    if isinstance(etl_metadata, str):
        etl_metadata = json.loads(etl_metadata)

    bbox = [
        float(additional_properties["north"]),
        float(additional_properties["west"]),
        float(additional_properties["south"]),
        float(additional_properties["east"])
    ]

    start_year = int(additional_properties["start_year"])
    end_year = int(additional_properties["end_year"])

    cds_dataset = etl_metadata["dataset"]
    data_format = etl_metadata.get("data_format", "netcdf")
    download_format = etl_metadata.get("download_format", "unarchived")

    variables_sql = """
        SELECT
            variable_name,
            property_id,
            unit_code,
            unit_text
        FROM backbone.variable_source vs
        JOIN backbone.data_source ds
        ON vs.data_source_uuid = ds.data_source_uuid
        WHERE ds.dataset_id = %s
        ORDER BY variable_name;
    """

    variables_df = pd.read_sql(variables_sql, conn, params=(DATASET_ID,))
    conn.close()

    if variables_df.empty:
        raise ValueError(f"No variables found in backbone.variable_source for {DATASET_ID}")

    variables = variables_df["variable_name"].drop_duplicates().tolist()

    return {
        "cds_dataset": cds_dataset,
        "bbox": bbox,
        "start_year": start_year,
        "end_year": end_year,
        "data_format": data_format,
        "download_format": download_format,
        "variables": variables
    }

# ============================================================
# 4. DOWNLOAD ERA5 DATA
# ============================================================

def download_era5():
    metadata = read_backbone_metadata()

    print("[INFO] Metadata-driven ERA5 download")
    print("[INFO] Dataset ID:", DATASET_ID)
    print("[INFO] CDS dataset:", metadata["cds_dataset"])
    print("[INFO] Variables:", metadata["variables"])
    print("[INFO] Years:", metadata["start_year"], "-", metadata["end_year"])
    print("[INFO] Bounding box:", metadata["bbox"])
    print("[INFO] Output folder:", OUTPUT_DIR)

    # Uses C:\Users\HP\.cdsapirc automatically
    client = cdsapi.Client()

    for var in metadata["variables"]:
        for year in range(metadata["start_year"], metadata["end_year"] + 1):
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
                    "data_format": metadata["data_format"],
                    "download_format": metadata["download_format"],
                    "area": metadata["bbox"]
                }

                client.retrieve(metadata["cds_dataset"], request).download(out_file)

                print(f"[DONE] {out_file}")

    print("[DONE] ERA5 metadata-driven download completed.")

# ============================================================
# 5. RUN
# ============================================================

if __name__ == "__main__":
    download_era5()