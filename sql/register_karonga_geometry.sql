INSERT INTO backbone.geom_template (
    data_source_uuid,
    geom_name,
    geom_source_value,
    geom_wgs84,
    geom_local_epsg,
    geom_local_value,
    properties
)
SELECT
    ds.data_source_uuid,

    'Karonga HDSS bounding box',

    'karonga_hdss_bbox',

    ST_SetSRID(
        ST_MakeEnvelope(
            33.4,
            -10.4,
            34.3,
            -9.2
        ),
        4326
    ),

    4326,

    ST_SetSRID(
        ST_MakeEnvelope(
            33.4,
            -10.4,
            34.3,
            -9.2
        ),
        4326
    ),

    '{
        "site": "Karonga HDSS",
        "country": "Malawi",
        "geometry_type": "bounding_box",
        "north": -9.2,
        "west": 33.4,
        "south": -10.4,
        "east": 34.3,
        "purpose": "ERA5 climate exposure linkage"
    }'::jsonb

FROM backbone.data_source ds
WHERE ds.dataset_id = 'karonga_era5_climate_2015_2021';