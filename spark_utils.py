from pyspark.sql import SparkSession
from config import MODE

def get_spark(app_name="taxi"):
    if MODE == "fabric":
        return SparkSession.builder.getOrCreate()
    import os, sys
    from delta import configure_spark_with_delta_pip
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    builder = SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    return configure_spark_with_delta_pip(builder).getOrCreate()