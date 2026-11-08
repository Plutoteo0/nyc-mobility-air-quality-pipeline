from pyspark.sql import functions as F
from spark_utils import get_spark
from config import table_path ,BRONZE

spark = get_spark("silver_fx")

df = spark.read.csv(BRONZE["fx"], header=True, inferSchema=True)

df = df.select([F.col("TIME_PERIOD"), F.col("OBS_VALUE")])
df = df.withColumnsRenamed({
    "TIME_PERIOD": "date",
    "OBS_VALUE": "usd_per_eur",
})
df.write.format("delta").mode("overwrite").save(table_path("silver", "fx_usd_eur"))
print(spark.read.format("delta").load(table_path("silver", "fx_usd_eur")).count())