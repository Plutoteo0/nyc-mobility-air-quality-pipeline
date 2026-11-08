from pyspark.sql import functions as F
from spark_utils import get_spark

spark = get_spark("gold_gdp")
dates = spark.read.format("delta").load("gold/dim_date")
years = dates.select(F.col("year")).distinct()

gdp = spark.read.format("delta").load("silver/gdp")

gdp_per_year = years.join(other=gdp, on="year", how="left").orderBy("year")
gdp_per_year.write.format("delta").mode("overwrite").save("gold/dim_gdp")
