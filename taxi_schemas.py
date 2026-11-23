import glob
import pyarrow.parquet as pq

files = sorted((glob.glob("bronze/taxi/*.parquet") + glob.glob("bronze/taxi_samples/*.parquet")))

schemas = {}
for f in files:
    pf = pq.ParquetFile(f)
    name = f.split("yellow_tripdata_")[1].replace(".parquet", "")
    schemas[name] = {field.name: str(field.type) for field in pf.schema_arrow}
    print(name, "rows:", pf.metadata.num_rows, "cols:", len(schemas[name]))

all_cols = sorted(set().union(*[set(s) for s in schemas.values()]))
print()
for c in all_cols:
    row = [schemas[n].get(c, "-") for n in schemas]
    print(f"{c:28}", *[f"{x:12}" for x in row])
print()
print("order:", list(schemas))