from pyspark.sql import functions as F
from spark_utils import get_spark
from config import table_path

spark = get_spark("gold_gdp")
dates = spark.read.format("delta").load(table_path("gold", "dim_date"))
years = dates.select(F.col("year")).distinct()

gdp = spark.read.format("delta").load(table_path("silver", "gdp"))

gdp_per_year = years.join(other=gdp, on="year", how="left").orderBy("year")
gdp_per_year.write.format("delta").mode("overwrite").save(table_path("gold", "dim_gdp"))
loaded = spark.read.format("delta").load(table_path("gold", "dim_gdp"))
print(loaded.count(), loaded.select("year").distinct().count(), loaded.filter(F.col("gdp_usd").isNull()).count())
