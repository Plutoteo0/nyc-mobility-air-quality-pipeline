from spark_utils import get_spark
from config import TAXI_MONTHS, TAXI_PATH
from taxi_adapter import read_taxi_month

spark = get_spark("taxi_adapter")

raw = {ym: spark.read.parquet(TAXI_PATH.format(ym=ym)).schema for ym in TAXI_MONTHS}

adapted = {ym: read_taxi_month(spark, ym).schema for ym in TAXI_MONTHS}

for ym in TAXI_MONTHS:
    print(ym, len(raw[ym].fields), len(adapted[ym].fields))

ref = adapted[TAXI_MONTHS[0]]

fields = [adapted[ym] == ref for ym in TAXI_MONTHS]
print(fields)