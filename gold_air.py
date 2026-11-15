from pyspark.sql import functions as F
from spark_utils import get_spark
from config import table_path

spark = get_spark("gold_air")

air_quality = spark.read.format("delta").load(table_path("silver","air_quality"))
zone_map = spark.read.format("delta").load(table_path("silver", "zone_station_map"))

joined = air_quality.join(zone_map, on=["station_id", "parameter"], how="inner")

cols = ["value", "station_id", "dist_km", "is_far_station",
        "is_low_coverage", "is_missing_value", "is_negative_value"]

aggs = [
    F.max(F.when(F.col("parameter") == p, F.col(c))).alias(f"{p}_{c}")
    for p in ("pm25", "no2")
    for c in cols
]

fact = joined.groupBy("zone_id", "date_local").agg(*aggs)
fact.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(table_path("gold", "fact_air_quality_daily"))

g = spark.read.format("delta").load(table_path("gold", "fact_air_quality_daily"))
print(joined.filter(F.col("parameter") == "pm25").count(),
      g.filter(F.col("pm25_station_id").isNotNull()).count())
print(joined.filter(F.col("parameter") == "no2").count(),
      g.filter(F.col("no2_station_id").isNotNull()).count())

taxi = spark.read.format("delta").load(table_path("gold", "fact_taxi_daily"))
air = spark.read.format("delta").load(table_path("gold", "fact_air_quality_daily"))
j = taxi.join(air, (taxi["PULocationID"] == air["zone_id"]) & (taxi["pickup_date"] == air["date_local"]), "left")
print(taxi.count(), j.count(), j.filter(F.col("pm25_value").isNotNull()).count())