from pyspark.sql import functions as F, Window
from spark_utils import get_spark
from config import table_path

spark = get_spark("dim_fx")

dates = spark.read.format("delta").load(table_path("gold", "dim_date"))
fx_usd_eur = spark.read.format("delta").load(table_path("silver","fx_usd_eur"))

dim_fx = dates.join(fx_usd_eur, on="date", how="left")

first_last_date = fx_usd_eur.agg(F.min(F.col("date")), F.max(F.col("date"))).first()
first_date = first_last_date[0]
last_date = first_last_date[1]

dim_fx = dim_fx.filter(F.col("date").between(first_date, last_date))

window = Window.orderBy("date").rowsBetween(Window.unboundedPreceding, Window.currentRow)
dim_fx = dim_fx.withColumn("usd_per_eur", F.last(F.col("usd_per_eur"), ignorenulls=True).over(window))

dim_fx.write.format("delta").mode("overwrite").save(table_path("gold", "dim_fx"))
print(spark.read.format("delta").load(table_path("gold", "dim_fx")).count())