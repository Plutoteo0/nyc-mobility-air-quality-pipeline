DROP TABLE IF EXISTS dbo.fact_taxi_daily;
CREATE TABLE dbo.fact_taxi_daily AS
SELECT
    pickup_date,
    PULocationID,
    COUNT(PULocationID) AS trip_count,
    SUM(fare_amount) AS sum_fare_amount,
    SUM(tip_amount) AS sum_tip_amount,
    SUM(total_amount) AS sum_total_amount,
    SUM(CAST(is_invalid_duration AS INT)) AS invalid_duration_trips,
    SUM(CAST(is_non_positive_amount AS INT)) AS non_positive_amount_trips,
    SUM(CAST(is_outlier_amount AS INT)) AS outlier_amount_trips,
    SUM(CAST(is_outlier_duration AS INT)) AS outlier_duration_trips,
    SUM(trip_distance) AS sum_trip_distance,
    AVG(CASE is_zero_distance WHEN 0 THEN trip_distance END) AS avg_trip_distance,
    AVG(CASE is_outlier_duration WHEN 0 THEN duration_min END) AS avg_duration_min,
    AVG(CASE WHEN is_non_positive_amount = 0 AND is_outlier_amount = 0 THEN fare_amount END) AS avg_fare_amount,
    SUM(CASE payment_type WHEN 4 THEN total_amount END) AS dispute_amount,
    SUM(CASE WHEN payment_type = 4 THEN 1 ELSE 0 END) AS dispute_trips,
    COUNT(CASE is_zero_distance WHEN 1 THEN is_zero_distance END) AS zero_distance_trips
FROM lh_silver.dbo.taxi
GROUP BY pickup_date, PULocationID;