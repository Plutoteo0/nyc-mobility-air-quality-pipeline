MODE = "local"

TAXI_START = "2026-09-01"
TAXI_END = "2026-10-01"

CAL_START = "2015-01-01"
CAL_END = "2030-12-31"

QUANTILE = 0.999
QUANTILE_ERROR = 0.0001

BRONZE = {
    "taxi": "bronze/yellow_tripdata_2026-09.parquet",
    "zones": "bronze/taxi_zone_lookup.csv",
    "fx": "bronze/ecb_usd_eur.csv",
    "gdp": "bronze/world_bank_gdp_usa.json",
}

def table_path(layer, name):
    if MODE == "local":
        return f"{layer}/{name}"
    return f"Tables/{layer}_{name}"