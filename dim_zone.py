from pyspark.sql import functions as F
from spark_utils import get_spark
from config import BRONZE, table_path

spark = get_spark("dim_zone")

df = spark.read.csv(BRONZE["zones"], header=True, inferSchema=True)

dim_zone = (
    df.withColumnRenamed("LocationID", "zone_id")
      .withColumnRenamed("Borough", "borough")
      .withColumnRenamed("Zone", "zone_name")
)

dim_zone.write.format("delta").mode("overwrite").save(table_path("gold", "dim_zone"))
print(spark.read.format("delta").load(table_path("gold", "dim_zone")).count())