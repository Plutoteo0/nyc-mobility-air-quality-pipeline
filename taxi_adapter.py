from pyspark.sql import functions as F
from config import TAXI_PATH

REQUIRED = {
    "PULocationID": "int",
    "DOLocationID": "int",
    "payment_type": "long",
    "trip_distance": "double",
    "fare_amount": "double",
    "extra": "double",
    "mta_tax": "double",
    "tip_amount": "double",
    "tolls_amount": "double",
    "improvement_surcharge": "double",
    "total_amount": "double",
    "congestion_surcharge": "double",
    "Airport_fee": "double",
    "cbd_congestion_fee": "double",
    "request_source": "string",
}

def read_taxi_month(spark, ym):
    df = spark.read.parquet(TAXI_PATH.format(ym=ym))
    actual = { c.lower() : c for c in df.columns}
    exprs = []
    for name, dtype in REQUIRED.items():
        if name.lower() in actual:
            exprs.append(F.col(actual[name.lower()]).cast(dtype).alias(name))
        else:
            exprs.append(F.lit(None).cast(dtype).alias(name))
    adapted = df.select("tpep_pickup_datetime", "tpep_dropoff_datetime", *exprs)
    return adapted