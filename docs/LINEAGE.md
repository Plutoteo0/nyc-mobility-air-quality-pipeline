# Data lineage

End-to-end flow of the pipeline `pl_main`: Bronze (raw) → Silver (cleaned, typed, flagged) → Gold (star schema in `wh_gold`).
Each layer reads only the previous one. Nothing is silently deleted; rows are flagged or routed to `taxi_rejected`.

```mermaid
flowchart LR
  subgraph SRC[Sources]
    S1[NYC TLC yellow taxi parquet]
    S2[OpenAQ API v3]
    S3[ECB API]
    S4[World Bank API]
    S5[taxi_zone_lookup.csv]
    S6[openaq_sensors.csv]
    S7[zone_station_map.csv]
  end

  subgraph BR[Bronze: lh_bronze]
    B1[Files/taxi/*.parquet]
    B2[Files/air/openaq_days_*.json]
    B3[dbo.ecb_usd_eur]
    B4[dbo.worldbank_gdp]
    B5[Files/reference/*.csv]
    B6[Files/zone/taxi_zone_lookup.csv]
  end

  subgraph SI[Silver: lh_silver]
    T1[taxi]
    T2[taxi_rejected]
    T3[air_quality]
    T4[zone_station_map]
    T5[fx_usd_eur]
    T6[gdp]
  end

  subgraph GO[Gold: wh_gold]
    G1[fact_taxi_daily]
    G2[fact_air_quality_daily]
    G3[dim_date]
    G4[dim_zone]
    G5[dim_fx]
    G6[dim_gdp]
  end

  S1 -->|pl_taxi_ingest Copy| B1
  S2 -->|nb_bronze_air + Key Vault| B2
  S3 -->|df_ecb Dataflow Gen2| B3
  S4 -->|df_wb Dataflow Gen2| B4
  S5 --> B6
  S6 --> B5
  S7 --> B5

  B1 -->|nb_silver_taxi| T1
  B1 -->|nb_silver_taxi| T2
  B2 -->|nb_silver_air| T3
  B5 -->|nb_silver_zone_map| T4
  B3 -->|nb_silver_fx| T5
  B4 -->|nb_silver_gdp| T6

  T1 -->|SQL: run_sql_fact_taxi_daily| G1
  T3 -->|nb_fact_air_quality_daily| G2
  T4 -->|nb_fact_air_quality_daily| G2
  G3 -->|nb_dim_fx| G5
  T5 -->|nb_dim_fx| G5
  G3 -->|nb_dim_gdp| G6
  T6 -->|nb_dim_gdp| G6
  B6 -->|nb_dim_zone| G4
```

## Notes

- **Order in `pl_main`:** four Bronze loads in parallel → `bronze_done` barrier → Silver notebooks in a chain → Gold in a chain (`dim_date` first, because `dim_fx` and `dim_gdp` read it) → `fact_taxi_daily` (T-SQL).
- **Taxi ↔ air link:** not built in Gold. Both facts share `zone_id` (= `PULocationID`) and the date, joined through `dim_zone` and `dim_date` in the semantic model `sm_taxi_air`.
- **`zone_station_map`:** computed locally (geopandas: nearest station per zone and parameter), loaded as CSV. 263 zones × 2 parameters = 526 rows. Gives `zone_id`, `station_id`, distance and `is_far_station`.
- **Control rule:** Bronze taxi rows = Silver `taxi` + `taxi_rejected` (123,471,721 = 123,470,919 + 802).
- **Secrets:** the OpenAQ key lives in Azure Key Vault `kv-itra-fioda`, read at runtime by `nb_bronze_air`; it is not in code or in the repository.
- **Exception to the layer chain:** `dim_zone` is built directly from the Bronze file `Files/zone/taxi_zone_lookup.csv` (columns renamed to `zone_id`, `borough`, `zone_name`; `service_zone` kept). It is a small reference table that needs no cleaning, so there is no Silver step for it.
