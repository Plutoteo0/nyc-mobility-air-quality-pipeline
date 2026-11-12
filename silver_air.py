from pyspark.sql import functions as F
from spark_utils import get_spark
from config import BRONZE, LOW_COVERAGE_PCT, table_path

spark = get_spark("silver_air")

raw = spark.read.option("multiline", True).json(BRONZE["openaq_days"])
raw = raw.withColumn("sensor_id", F.regexp_extract(F.col("_metadata.file_name"), r"openaq_days_(\d+)\.json", 1).cast("int"))

table = raw.select(
    F.col("sensor_id").alias("sensor_id"),
    F.col("parameter.name").alias("parameter"),
    F.col("parameter.units").alias("units"),
    F.to_date(F.substring(F.col("period.datetimeFrom.local"), 1, 10)).alias("date_local"), 
    F.col("value").alias("value"),
    F.col("summary.min").alias("min_value"),
    F.col("summary.max").alias("max_value"),
    F.col("coverage.expectedCount").alias("expected_count"),
    F.col("coverage.observedCount").alias("observed_count"),
    F.col("coverage.percentCoverage").alias("percent_coverage"),
)

table = table.withColumn("is_missing_value", F.col("value").isNull())
table = table.withColumn("is_negative_value", F.coalesce(F.col("value") < 0, F.lit(False)))
table = table.withColumn("is_low_coverage", F.col("percent_coverage") < LOW_COVERAGE_PCT)

table.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(table_path("silver", "air_quality"))

s = spark.read.format("delta").load(table_path("silver", "air_quality"))
print("silver air:", s.count())
print("missing:", s.filter("is_missing_value").count())
print("negative:", s.filter("is_negative_value").count())
print("low_coverage:", s.filter("is_low_coverage").count())