from pyspark.sql import functions as F
from spark_utils import get_spark
from config import QUANTILE, QUANTILE_ERROR, table_path, TAXI_MONTHS
from taxi_adapter import read_taxi_month
from functools import reduce
from pyspark.sql import DataFrame

spark = get_spark("silver_taxi")

silver_cols = [
    "tpep_pickup_datetime", "tpep_dropoff_datetime", "pickup_date", "pickup_hour",
    "PULocationID", "DOLocationID",
    "trip_distance", "duration_min", "is_zero_distance", "is_non_positive_amount",
    "is_invalid_duration","is_outlier_amount","is_outlier_duration",
    "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount",
    "improvement_surcharge", "total_amount", "congestion_surcharge",
    "Airport_fee", "cbd_congestion_fee",
    "request_source", "payment_type"
]

def process_month(spark, ym):
    raw = read_taxi_month(spark, ym)
    start = F.to_date(F.lit(ym + "-01"))
    end = F.add_months(start, 1)
    in_range = (F.col("tpep_pickup_datetime") >= start) & (F.col("tpep_pickup_datetime") < end)

    df = raw.filter(in_range)
    rejected = raw.filter(~in_range).withColumn("reject_reason", F.lit("pickup_out_of_range"))

    df = df.withColumn("duration_min", F.timestamp_diff("SECOND", F.col("tpep_pickup_datetime"), F.col("tpep_dropoff_datetime")) / 60)
    df = df.withColumn("is_invalid_duration", F.col("duration_min") <= 0)
    df = df.withColumn("duration_min", F.when(~F.col("is_invalid_duration"), F.col("duration_min")))

    q = df.approxQuantile(["total_amount", "duration_min"], [QUANTILE], QUANTILE_ERROR)
    amount_cap = q[0][0]
    duration_cap = q[1][0]
    df = df.withColumn("is_outlier_amount", F.col("total_amount") > amount_cap)
    df = df.withColumn("is_outlier_duration", F.coalesce(F.col("duration_min") > duration_cap, F.lit(False)))


    df = df.withColumn("is_zero_distance", F.when(F.col("trip_distance") <= 0, True).otherwise(False))
    df = df.withColumn("is_non_positive_amount", F.when(F.col("total_amount") <= 0, True).otherwise(False))
    df = df.withColumns({"pickup_date": F.to_date(F.col("tpep_pickup_datetime")), "pickup_hour": F.hour(F.col("tpep_pickup_datetime"))})

    df = df.select(*silver_cols)

    return df, rejected

silver_parts = []
rejected_parts = []

for ym in TAXI_MONTHS:
    df_m, rej_m = process_month(spark, ym)
    silver_parts.append(df_m)
    rejected_parts.append(rej_m)

silver = reduce(DataFrame.unionByName, silver_parts)
rejected = reduce(DataFrame.unionByName, rejected_parts)

silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(table_path("silver","taxi"))
rejected.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(table_path("silver","taxi_rejected"))

s = spark.read.format("delta").load(table_path("silver", "taxi"))
r = spark.read.format("delta").load(table_path("silver", "taxi_rejected"))

bronze_total = sum(read_taxi_month(spark, ym).count() for ym in TAXI_MONTHS)

print("bronze:", bronze_total)
print("silver:", s.count(), "rejected:", r.count())
print("silver + rejected:", s.count() + r.count())

s.groupBy(F.date_format("pickup_date", "yyyy-MM").alias("month")).count().orderBy("month").show()
r.groupBy(F.date_format("tpep_pickup_datetime", "yyyy-MM").alias("month")).count().orderBy("month").show()