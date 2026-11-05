from pyspark.sql import functions as F
from spark_utils import get_spark

spark = get_spark("gold_taxi")

df = spark.read.format("delta").load("silver/taxi")

fact_taxi_daily = df.groupBy(F.col("pickup_date"), F.col("PULocationID")).agg(
    F.count(F.col("PULocationID")).alias("trip_count"),
    F.sum(F.col("fare_amount")).alias("sum_fare_amount"),
    F.sum(F.col("tip_amount")).alias("sum_tip_amount"),
    F.sum(F.col("total_amount")).alias("sum_total_amount"),
    F.avg(F.col("fare_amount")).alias("avg_fare_amount"),
    F.sum(F.col("trip_distance")).alias("sum_trip_distance"),
    F.avg(F.when(F.col("is_zero_distance") == False, F.col("trip_distance"))).alias("avg_trip_distance"),
    F.avg(F.col("duration_min")).alias("avg_duration_min"),
    F.count(F.when(F.col("is_zero_distance") == True, F.col("is_zero_distance"))).alias("zero_distance_trips"))

fact_taxi_daily.agg(F.sum("trip_count")).show()

fact_taxi_daily.write.format("delta").mode("overwrite").save("gold/fact_taxi_daily")