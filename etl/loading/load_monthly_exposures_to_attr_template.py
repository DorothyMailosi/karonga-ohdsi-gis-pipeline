import os
import pandas as pd
import psycopg2

# ============================================================
# DATABASE CONNECTION
# ============================================================

DB_CONFIG = {
    "dbname": "gaiacore",
    "user": "postgres",
    "password": "SuperSecret",
    "host": "localhost",
    "port": "5440"
}

DATASET_ID = "karonga_era5_climate_2015_2021"
GEOM_SOURCE_VALUE = "karonga_hdss_bbox"

# ============================================================
# FILE PATH
# ============================================================

BASE_DIR = r"C:\Users\HP\Desktop\karonga-ohdsi-gis-pipeline"

MONTHLY_FILE = os.path.join(
    BASE_DIR,
    "processed",
    "climate",
    "karonga_era5_monthly_exposures.csv"
)

# ============================================================
# VARIABLES TO LOAD INTO attr_template
# ============================================================

EXPOSURE_COLUMNS = [
    "monthly_precipitation_mm",
    "flood_event_count",
    "flood_intensity_mm",
    "mean_temperature_c",
    "mean_relative_humidity",
    "mean_wind_speed_ms",
    "flood_duration_days",
    "flood_event_count_lag1",
    "flood_event_count_lag2",
    "flood_intensity_mm_lag1",
    "flood_intensity_mm_lag2",
    "flood_duration_days_lag1",
    "flood_duration_days_lag2",
    "monthly_precipitation_mm_lag1",
    "monthly_precipitation_mm_lag2",
    "mean_temperature_c_lag1",
    "mean_temperature_c_lag2"
]

# ============================================================
# HELPERS
# ============================================================

def get_ids(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT geom_record_id
            FROM backbone.geom_template
            WHERE geom_source_value = %s;
        """, (GEOM_SOURCE_VALUE,))

        geom = cur.fetchone()

        if geom is None:
            raise ValueError(f"Geometry not found: {GEOM_SOURCE_VALUE}")

        geom_record_id = geom[0]

        cur.execute("""
            SELECT
                vs.variable_source_id,
                vs.variable_name,
                vs.unit_text
            FROM backbone.variable_source vs
            JOIN backbone.data_source ds
            ON vs.data_source_uuid = ds.data_source_uuid
            WHERE ds.dataset_id = %s;
        """, (DATASET_ID,))

        rows = cur.fetchall()

        variable_map = {
            row[1]: {
                "variable_source_id": row[0],
                "unit_text": row[2]
            }
            for row in rows
        }

    return geom_record_id, variable_map


def clean_value(value):
    if pd.isna(value):
        return None
    return float(value)


# ============================================================
# LOAD TO attr_template
# ============================================================

def load_attr_template():
    print("[INFO] Reading monthly exposure file:")
    print(MONTHLY_FILE)

    df = pd.read_csv(MONTHLY_FILE)

    if "month" not in df.columns:
        raise ValueError("Monthly file must contain a 'month' column.")

    df["attr_start_date"] = pd.to_datetime(df["month"] + "-01").dt.date
    df["attr_end_date"] = (
        pd.to_datetime(df["month"] + "-01") + pd.offsets.MonthEnd(0)
    ).dt.date

    conn = psycopg2.connect(**DB_CONFIG)

    geom_record_id, variable_map = get_ids(conn)

    print("[INFO] geom_record_id:", geom_record_id)
    print("[INFO] Variables available in backbone:", list(variable_map.keys()))

    inserted = 0
    skipped = 0

    insert_sql = """
        INSERT INTO backbone.attr_template (
            geom_record_id,
            variable_source_id,
            attr_start_date,
            attr_end_date,
            value_as_number,
            unit_source_value,
            attr_source_value,
            value_source_value
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """

    with conn.cursor() as cur:
        for _, row in df.iterrows():
            for col in EXPOSURE_COLUMNS:

                if col not in df.columns:
                    print(f"[WARNING] Column missing from CSV: {col}")
                    skipped += 1
                    continue

                if col not in variable_map:
                    print(f"[WARNING] Variable not registered in backbone.variable_source: {col}")
                    skipped += 1
                    continue

                value = clean_value(row[col])

                if value is None:
                    skipped += 1
                    continue

                variable_source_id = variable_map[col]["variable_source_id"]
                unit_source_value = variable_map[col]["unit_text"]

                cur.execute(
                    insert_sql,
                    (
                        geom_record_id,
                        variable_source_id,
                        row["attr_start_date"],
                        row["attr_end_date"],
                        value,
                        unit_source_value,
                        col,
                        str(value)
                    )
                )

                inserted += 1

        conn.commit()

    conn.close()

    print("[DONE] Loaded monthly exposures into backbone.attr_template")
    print("[INFO] Inserted rows:", inserted)
    print("[INFO] Skipped rows:", skipped)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    load_attr_template()