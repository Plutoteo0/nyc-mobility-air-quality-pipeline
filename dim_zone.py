from pyspark.sql import functions as F
from spark_utils import get_spark

spark = get_spark("gold_taxi")

df = spark.read.csv("./bronze/taxi_zone_lookup.csv", header=True, inferSchema=True)

dim_zone = (
    df.withColumnRenamed("LocationID", "zone_id")
      .withColumnRenamed("Borough", "borough")
      .withColumnRenamed("Zone", "zone_name")
)

dim_zone.write.format("delta").mode("overwrite").save("gold/dim_zone")