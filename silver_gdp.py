from pyspark.sql import functions as F
from spark_utils import get_spark
import json
from config import BRONZE, table_path

PATH = BRONZE["gdp"]
spark = get_spark("silver_gdp")

with open(PATH, "r") as f:
    data = json.load(f)[1]

records = [(int(d["date"]), d["value"]) for d in data]

df = spark.createDataFrame(records, ["year", "gdp_usd"])
df = df.withColumn("year", F.col("year").cast("int"))

df.write.format("delta").mode("overwrite").save(table_path("silver","gdp"))