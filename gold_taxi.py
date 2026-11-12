from pyspark.sql import functions as F
from spark_utils import get_spark
from config import table_path

spark = get_spark("gold_taxi")

df = spark.read.format("delta").load(table_path("silver", "taxi"))

fact_taxi_daily = df.groupBy(F.col("pickup_date"), F.col("PULocationID")).agg(
    F.count(F.col("PULocationID")).alias("trip_count"),
    F.sum(F.col("fare_amount")).alias("sum_fare_amount"),
    F.sum(F.col("tip_amount")).alias("sum_tip_amount"),
    F.sum(F.col("total_amount")).alias("sum_total_amount"),
    F.sum(F.col("is_invalid_duration").cast("int")).alias("invalid_duration_trips"),
    F.sum(F.col("is_non_positive_amount").cast("int")).alias("non_positive_amount_trips"),
    F.sum(F.col("is_outlier_amount").cast("int")).alias("outlier_amount_trips"),
    F.sum(F.col("is_outlier_duration").cast("int")).alias("outlier_duration_trips"),
    F.sum(F.col("trip_distance")).alias("sum_trip_distance"),
    F.avg(F.when(F.col("is_zero_distance") == False, F.col("trip_distance"))).alias("avg_trip_distance"),
    F.avg(F.when(~F.col("is_outlier_duration"), F.col("duration_min"))).alias("avg_duration_min"),
    F.avg(F.when(~F.col("is_non_positive_amount") & ~F.col("is_outlier_amount"), F.col("fare_amount"))).alias("avg_fare_amount"),
    F.sum(F.when(F.col("payment_type") == 4, F.col("total_amount"))).alias("dispute_amount"),
    F.sum((F.col("payment_type") == 4).cast("int")).alias("dispute_trips"),
    F.count(F.when(F.col("is_zero_distance") == True, F.col("is_zero_distance"))).alias("zero_distance_trips"))

fact_taxi_daily.agg(F.sum("trip_count")).show()

fact_taxi_daily.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(table_path("gold", "fact_taxi_daily"))
g = spark.read.format("delta").load(table_path("gold", "fact_taxi_daily"))
print("rows:", g.count())
g.agg(F.sum("trip_count"), F.sum("invalid_duration_trips"), F.sum("non_positive_amount_trips"), F.sum("zero_distance_trips"), F.sum("dispute_trips")).show()