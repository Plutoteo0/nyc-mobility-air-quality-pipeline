MODE = "local"

TAXI_START = "2026-09-01"
TAXI_END = "2026-10-01"

CAL_START = "2015-01-01"
CAL_END = "2030-12-31"

QUANTILE = 0.999
QUANTILE_ERROR = 0.0001
LOW_COVERAGE_PCT = 75
MAX_STATION_KM = 10

BRONZE = {
    "taxi": "bronze/yellow_tripdata_2026-09.parquet",
    "zones": "bronze/taxi_zone_lookup.csv",
    "fx": "bronze/ecb_usd_eur.csv",
    "gdp": "bronze/world_bank_gdp_usa.json",
    "openaq_days": "bronze/openaq_days_*.json",
}

TAXI_PATH = "bronze/taxi/yellow_tripdata_{ym}.parquet"
TAXI_MONTHS = ["2024-01", "2024-07", "2025-01", "2026-09"]

REFERENCE = {
    "sensors": "reference/openaq_sensors.csv",
    "zone_station_map": "reference/zone_station_map.csv",
}

def table_path(layer, name):
    if MODE == "local":
        return f"{layer}/{name}"
    return f"Tables/{layer}_{name}"