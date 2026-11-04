from pyspark.sql import functions as F
from spark_utils import get_spark

spark = get_spark("silver_taxi")

df = spark.read.parquet("./bronze/yellow_tripdata_2026-09.parquet")

df = df.filter(~((F.col("tpep_pickup_datetime") < "2026-09-01") | (F.col("tpep_pickup_datetime") >= "2026-10-01")))

df = df.withColumn("duration_min", F.timestamp_diff("SECOND", F.column("tpep_pickup_datetime"), F.column("tpep_dropoff_datetime")) / 60)

df = df.filter((F.col("total_amount") > 0) & (F.col("duration_min") > 0))

q = df.approxQuantile(["total_amount", "duration_min"], [0.999], 0.0001)
amount_cap = q[0][0]
duration_cap = q[1][0]

df = df.filter((F.col("duration_min") <= duration_cap) & (F.col("total_amount") <= amount_cap ))

df = df.withColumn("is_zero_distance", F.when(F.col("trip_distance") <= 0, True).otherwise(False))

df = df.withColumns({"pickup_date": F.to_date(F.col("tpep_pickup_datetime")), "pickup_hour": F.hour(F.col("tpep_pickup_datetime"))})

silver_cols = [
    "tpep_pickup_datetime", "tpep_dropoff_datetime", "pickup_date", "pickup_hour",
    "PULocationID", "DOLocationID",
    "trip_distance", "duration_min", "is_zero_distance",
    "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount",
    "improvement_surcharge", "total_amount", "congestion_surcharge",
    "Airport_fee", "cbd_congestion_fee",
    "request_source",
]

df = df.select(*silver_cols)

df.write.format("delta").mode("overwrite").save("silver/taxi")
print(spark.read.format("delta").load("silver/taxi").count())