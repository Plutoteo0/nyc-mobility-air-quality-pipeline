import pandas as pd

file = "./yellow_tripdata_2026-09.parquet"
data = pd.read_parquet(file)

print(data.dtypes)

mask_isna = data["request_source"].isna()
mask_notna = data["request_source"].notna()

mask_date = (data["tpep_pickup_datetime"] < '2026-09-01') | (data["tpep_pickup_datetime"] >= '2026-10-01')
print(mask_date.sum())

mask_total_amount = data["total_amount"] <= 0;
print(mask_total_amount.sum())

mask_trip_distance = data["trip_distance"] <= 0;
print(mask_trip_distance.sum())

data["duration_min"] = data["tpep_dropoff_datetime"] - data["tpep_pickup_datetime"]
data["duration_min"] = (data["duration_min"].dt.total_seconds() / 60)
mask_trip_duration = data['duration_min'] <= 0;
print(mask_trip_duration.sum())

bad = mask_date | mask_total_amount | mask_trip_distance | mask_trip_duration
print(bad.sum())

print(data[mask_trip_distance][["total_amount","duration_min"]].describe())
print(data[["total_amount","duration_min"]].quantile([0.99, 0.999, 1.0]))