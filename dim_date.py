from pyspark.sql import functions as F
from spark_utils import get_spark
from config import CAL_START, CAL_END, table_path

spark = get_spark("dim_date")

dates = spark.range(1).select(
    F.explode(
        F.sequence(
            F.to_date(F.lit(CAL_START)),
            F.to_date(F.lit(CAL_END)),
            F.expr("interval 1 day")
        )
    ).alias("date")
)

dim_date = dates.withColumns({
    "year": F.year(F.col("date")),
    "month": F.month(F.col("date")),
    "day": F.dayofmonth(F.col("date")),
    "day_of_week": (F.dayofweek("date") + 5) % 7 + 1,
    "day_name": F.date_format(F.col("date"), "E")
    })

dim_date = dim_date.withColumn("is_weekend", F.col("day_of_week").isin([6, 7]))
dim_date.write.format("delta").mode("overwrite").save(table_path("gold", "dim_date"))
print(spark.read.format("delta").load(table_path("gold", "dim_date")).count())