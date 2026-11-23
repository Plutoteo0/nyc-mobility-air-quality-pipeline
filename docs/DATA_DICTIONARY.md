# Data dictionary: Gold layer (`wh_gold`, schema `dbo`)

Star schema with two daily fact tables and four dimensions. Grain of both facts: **one row per zone per day**.
Principle: bad values are kept and flagged (`is_*`, `*_trips`), never silently deleted.

| Table                    | Type      | Grain                                             | Source (Silver)                    |
| ------------------------ | --------- | ------------------------------------------------- | ---------------------------------- |
| `fact_taxi_daily`        | fact      | pickup date × pickup zone                         | `lh_silver.dbo.taxi`               |
| `fact_air_quality_daily` | fact      | local date × zone (pm25 and no2 as columns)       | `air_quality` + `zone_station_map` |
| `dim_date`               | dimension | one row per calendar day, 2015-01-01 → 2030-12-31 | generated                          |
| `dim_zone`               | dimension | one row per taxi zone (265)                       | `taxi_zone_lookup`                 |
| `dim_fx`                 | dimension | one row per day with an ECB rate                  | ECB (USD per EUR)                  |
| `dim_gdp`                | dimension | one row per year, 2015–2030                       | World Bank (US GDP)                |

## fact_taxi_daily

| Column                      | Type  | Description                                                                                                                                                        |
| --------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `pickup_date`               | date  | Pickup day. Joins to `dim_date.date`.                                                                                                                              |
| `PULocationID`              | int   | Pickup zone. Joins to `dim_zone.zone_id`.                                                                                                                          |
| `trip_count`                | int   | Number of trips in the zone that day (all trips, flagged ones included).                                                                                           |
| `sum_fare_amount`           | float | Sum of the metered fare.                                                                                                                                           |
| `sum_tip_amount`            | float | Sum of tips.                                                                                                                                                       |
| `sum_total_amount`          | float | Sum of the total charged (USD). Basis of the `Revenue EUR` measure.                                                                                                |
| `invalid_duration_trips`    | int   | Trips flagged `is_invalid_duration`.                                                                                                                               |
| `non_positive_amount_trips` | int   | Trips with a non-positive amount.                                                                                                                                  |
| `outlier_amount_trips`      | int   | Trips with an outlier amount (monthly 0.999 quantile).                                                                                                             |
| `outlier_duration_trips`    | int   | Trips with an outlier duration (monthly 0.999 quantile).                                                                                                           |
| `sum_trip_distance`         | float | Sum of trip distance (all trips).                                                                                                                                  |
| `avg_trip_distance`         | float | Average distance, zero-distance trips excluded.                                                                                                                    |
| `avg_duration_min`          | float | Average duration in minutes, duration outliers excluded.                                                                                                           |
| `avg_fare_amount`           | float | Average fare, non-positive and outlier amounts excluded. For multi-day or multi-zone averages use `sum_fare_amount / trip_count`: an average of averages is wrong. |
| `dispute_amount`            | float | Total amount of trips with `payment_type = 4` (dispute). NULL if none.                                                                                             |
| `dispute_trips`             | int   | Number of `payment_type = 4` trips.                                                                                                                                |
| `zero_distance_trips`       | int   | Trips with zero distance.                                                                                                                                          |

## fact_air_quality_daily

Columns repeat for each parameter (`pm25_*`, `no2_*`). A missing measurement stays **NULL** (never 0) and is flagged.

| Column                                             | Type  | Description                                                                                                              |
| -------------------------------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------ |
| `zone_id`                                          | int   | Taxi zone. Joins to `dim_zone.zone_id`.                                                                                  |
| `date_local`                                       | date  | Local day. Joins to `dim_date.date`.                                                                                     |
| `pm25_value` / `no2_value`                         | float | Daily value from the zone's nearest station for that parameter. Units as reported by OpenAQ: PM2.5 in µg/m³, NO2 in ppm. |
| `pm25_station_id` / `no2_station_id`               | int   | Station (OpenAQ sensor) used for the zone.                                                                               |
| `pm25_dist_km` / `no2_dist_km`                     | float | Distance from the zone to that station, km.                                                                              |
| `pm25_is_far_station` / `no2_is_far_station`       | bit   | The nearest station is farther than 10 km from the zone (`MAX_STATION_KM = 10`).                                         |
| `pm25_is_low_coverage` / `no2_is_low_coverage`     | bit   | The day's measurement coverage is below 75% (`LOW_COVERAGE_PCT = 75`).                                                   |
| `pm25_is_missing_value` / `no2_is_missing_value`   | bit   | No measurement for that zone and day.                                                                                    |
| `pm25_is_negative_value` / `no2_is_negative_value` | bit   | The sensor reported a negative value. Kept, flagged.                                                                     |

## dim_date

| Column                 | Type    | Description                |
| ---------------------- | ------- | -------------------------- |
| `date`                 | date    | Calendar day (key).        |
| `year`, `month`, `day` | int     | Date parts.                |
| `day_of_week`          | int     | Day of week number.        |
| `day_name`             | varchar | Day name.                  |
| `is_weekend`           | bit     | 1 for Saturday and Sunday. |

## dim_zone

| Column         | Type    | Description               |
| -------------- | ------- | ------------------------- |
| `zone_id`      | int     | TLC zone ID, 1–265 (key). |
| `borough`      | varchar | Borough.                  |
| `zone_name`    | varchar | Zone name.                |
| `service_zone` | varchar | TLC service zone.         |

## dim_fx

| Column                                                          | Type                | Description                                  |
| --------------------------------------------------------------- | ------------------- | -------------------------------------------- |
| `date`                                                          | date                | Day (key). Weekends carry the last ECB rate. |
| `usd_per_eur`                                                   | float               | USD for 1 EUR (ECB reference rate).          |
| `year`, `month`, `day`, `day_of_week`, `day_name`, `is_weekend` | int / varchar / bit | Date attributes, as in `dim_date`.           |

## dim_gdp

| Column  | Type   | Description                                                                                                            |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------- |
| `year`  | int    | Year (key).                                                                                                            |
| `date`  | bigint | Original World Bank `date` field (the year as a number). Duplicates `year`; kept as in the source. NULL for 2026–2030. |
| `value` | float  | US GDP, current USD (World Bank `NY.GDP.MKTP.CD`). NULL for years not yet published (2026–2030).                       |

`dim_gdp` is built from the distinct years of `dim_date` with a LEFT JOIN to Silver `gdp` on `year`; `year` in Silver is `date` cast to int.

## Relationships in the semantic model `sm_taxi_air`

- `dim_date.date` 1:\* `fact_taxi_daily.pickup_date`
- `dim_date.date` 1:\* `fact_air_quality_daily.date_local`
- `dim_zone.zone_id` 1:\* `fact_taxi_daily.PULocationID`
- `dim_zone.zone_id` 1:\* `fact_air_quality_daily.zone_id`
- `dim_date.date` 1:\* `dim_fx.date`
- `dim_gdp` is not related (yearly; `dim_date.year` is not unique).
