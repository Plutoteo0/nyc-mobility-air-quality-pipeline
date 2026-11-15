from pyspark.sql import functions as F
from spark_utils import get_spark
from config import table_path

spark = get_spark("silver_zone_station_map")

m = spark.read.option("header", True).option("inferSchema", True).csv("reference/zone_station_map.csv")
m.printSchema()

m.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(table_path("silver", "zone_station_map"))

s = spark.read.format("delta").load(table_path("silver", "zone_station_map"))
print(s.count())
s.groupBy("parameter").agg(F.sum(F.col("is_far_station").cast("int"))).show()