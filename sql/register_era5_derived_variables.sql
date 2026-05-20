-- =====================================================
-- Register derived ERA5 exposure variables in GaiaCore
-- =====================================================

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
        'monthly_precipitation_mm',
        'Monthly total precipitation derived from hourly ERA5 total precipitation and converted from metres to millimetres.',
        'monthly_precipitation',
        'numeric',
        'mm',
        'millimetres'
    ),

    (
        'flood_event_count',
        'Number of daily precipitation exceedance days per month using the 95th percentile rainfall threshold.',
        'flood_event_count',
        'integer',
        'days',
        'days'
    ),

    (
        'flood_intensity_mm',
        'Mean rainfall intensity on flood exceedance days within each month.',
        'flood_intensity',
        'numeric',
        'mm',
        'millimetres'
    ),

    (
        'flood_duration_days',
        'Longest consecutive run of flood exceedance days within each month.',
        'flood_duration',
        'integer',
        'days',
        'days'
    ),

    (
        'mean_temperature_c',
        'Monthly mean air temperature derived from ERA5 2m temperature and converted from Kelvin to Celsius.',
        'mean_temperature',
        'numeric',
        'degC',
        'degrees Celsius'
    ),

    (
        'mean_relative_humidity',
        'Monthly mean relative humidity derived from ERA5 temperature and dewpoint temperature.',
        'relative_humidity',
        'numeric',
        '%',
        'percent'
    ),

    (
        'mean_wind_speed_ms',
        'Monthly mean wind speed derived from ERA5 10m u and v wind components.',
        'wind_speed',
        'numeric',
        'm/s',
        'metres per second'
    ),

    (
        'flood_event_count_lag1',
        'One-month lag of monthly flood event count.',
        'flood_event_count_lag1',
        'integer',
        'days',
        'days'
    ),

    (
        'flood_event_count_lag2',
        'Two-month lag of monthly flood event count.',
        'flood_event_count_lag2',
        'integer',
        'days',
        'days'
    ),

    (
        'flood_intensity_mm_lag1',
        'One-month lag of flood intensity.',
        'flood_intensity_lag1',
        'numeric',
        'mm',
        'millimetres'
    ),

    (
        'flood_intensity_mm_lag2',
        'Two-month lag of flood intensity.',
        'flood_intensity_lag2',
        'numeric',
        'mm',
        'millimetres'
    ),

    (
        'flood_duration_days_lag1',
        'One-month lag of flood duration.',
        'flood_duration_lag1',
        'integer',
        'days',
        'days'
    ),

    (
        'flood_duration_days_lag2',
        'Two-month lag of flood duration.',
        'flood_duration_lag2',
        'integer',
        'days',
        'days'
    ),

    (
        'monthly_precipitation_mm_lag1',
        'One-month lag of monthly precipitation.',
        'monthly_precipitation_lag1',
        'numeric',
        'mm',
        'millimetres'
    ),

    (
        'monthly_precipitation_mm_lag2',
        'Two-month lag of monthly precipitation.',
        'monthly_precipitation_lag2',
        'numeric',
        'mm',
        'millimetres'
    ),

    (
        'mean_temperature_c_lag1',
        'One-month lag of monthly mean temperature.',
        'mean_temperature_lag1',
        'numeric',
        'degC',
        'degrees Celsius'
    ),

    (
        'mean_temperature_c_lag2',
        'Two-month lag of monthly mean temperature.',
        'mean_temperature_lag2',
        'numeric',
        'degC',
        'degrees Celsius'
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