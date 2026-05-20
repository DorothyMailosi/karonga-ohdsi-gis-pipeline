INSERT INTO backbone.data_source (
    dataset_id,
    dataset_name,
    dataset_version,
    description,
    creator,
    provider,
    license,
    spatial_coverage,
    date_published,
    date_modified,
    keywords,
    url,
    measurement_technique,
    additional_properties,
    geom_type,
    srid,
    etl_metadata
)
VALUES (
    'karonga_era5_climate_2015_2021',
    'Karonga ERA5 Climate Exposure Dataset',
    'v1.0',
    'ERA5 climate variables for Karonga HDSS, Malawi, used for flood and climate-health exposure analyses.',
    ARRAY['Dorothy Mailosi'],
    ARRAY['Copernicus Climate Data Store'],
    'Copernicus CDS terms of use',
    'Karonga HDSS bounding box: north=-9.2, west=33.4, south=-10.4, east=34.3',
    DATE '2026-05-19',
    DATE '2026-05-19',
    ARRAY['ERA5', 'climate', 'Karonga', 'flood', 'OHDSI', 'EXTERNAL_EXPOSURE'],
    'https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels',
    '{"method": "Hourly ERA5 reanalysis retrieved using CDS API and processed into daily and monthly exposure indicators."}'::jsonb,
    '{"north": -9.2, "west": 33.4, "south": -10.4, "east": 34.3, "start_year": 2015, "end_year": 2021}'::jsonb,
    'bbox',
    4326,
    '{"api": "cdsapi", "dataset": "reanalysis-era5-single-levels", "data_format": "netcdf", "download_format": "unarchived"}'::jsonb
)
ON CONFLICT (dataset_id)
DO UPDATE SET
    dataset_name = EXCLUDED.dataset_name,
    description = EXCLUDED.description,
    date_modified = EXCLUDED.date_modified,
    measurement_technique = EXCLUDED.measurement_technique,
    additional_properties = EXCLUDED.additional_properties,
    etl_metadata = EXCLUDED.etl_metadata;


INSERT INTO backbone.variable_source (
    data_source_uuid,
    variable_name,
    variable_description,
    property_id,
    data_type,
    unit_code,
    unit_text,
    min_value,
    max_value,
    start_date,
    end_date
)
SELECT
    ds.data_source_uuid,
    v.variable_name,
    v.variable_description,
    v.property_id,
    v.data_type,
    v.unit_code,
    v.unit_text,
    NULL,
    NULL,
    DATE '2015-01-01',
    DATE '2021-12-31'
FROM backbone.data_source ds
CROSS JOIN (
    VALUES

    (
        '2m_temperature',
        'Air temperature at 2 metres.',
        'temperature_2m',
        'numeric',
        'K',
        'Kelvin'
    ),

    (
        '2m_dewpoint_temperature',
        'Dewpoint temperature at 2 metres.',
        'dewpoint_2m',
        'numeric',
        'K',
        'Kelvin'
    ),

    (
        'total_precipitation',
        'Total precipitation used for flood metrics.',
        'precipitation',
        'numeric',
        'm',
        'metres of water equivalent'
    ),

    (
        '10m_u_component_of_wind',
        'Eastward wind component at 10 metres.',
        'wind_u10',
        'numeric',
        'm/s',
        'metres per second'
    ),

    (
        '10m_v_component_of_wind',
        'Northward wind component at 10 metres.',
        'wind_v10',
        'numeric',
        'm/s',
        'metres per second'
    )

) AS v (
    variable_name,
    variable_description,
    property_id,
    data_type,
    unit_code,
    unit_text
)

WHERE ds.dataset_id = 'karonga_era5_climate_2015_2021';