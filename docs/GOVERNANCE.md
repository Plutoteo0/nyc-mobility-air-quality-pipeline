# Governance policies

## 1. Secrets and access

- The OpenAQ API key is stored only in Azure Key Vault `kv-itra-fioda` (secret `openaq-api-key`, RBAC access model, soft delete 90 days).
- `nb_bronze_air` reads it at runtime with `notebookutils.credentials.getSecret`. The key is not in notebooks, pipelines, Dataflows or the repository.
- Local scripts read the key from `.env`, which is listed in `.gitignore`.
- Roles: Key Vault Secrets Officer for the owner (create and read); Secrets User is enough for read-only access.
- Pipeline and notebook exports were checked for secrets before publishing (`grep` over `fabric/`; only the secret name remains).
- Dataflow Gen2 is used for open APIs only (ECB, World Bank). OpenAQ needs a key in the request header, which in a Dataflow would be stored in the M query and could leak through Git, so a notebook with Key Vault is used instead.

## 2. Data quality rules

- **Keep and flag, never silently drop.** Suspicious rows stay in Silver and Gold with flags: `is_invalid_duration`, non-positive amount, amount and duration outliers (monthly 0.999 quantile), zero distance, dispute payments (`payment_type = 4`).
- **Only exception:** taxi rows whose pickup date is outside the month of the file go to `taxi_rejected` (802 rows) with a reason.
- **Air quality flags:** `*_is_missing_value`, `*_is_negative_value`, `*_is_low_coverage` (coverage below 75%), `*_is_far_station` (nearest station farther than 10 km). Missing values stay NULL, never 0.
- **NULL safety:** filters are written so that rows with NULL are not lost by `filter(cond)` / `filter(~cond)`.
- **Averages in Gold** exclude flagged rows where it matters (for example average fare excludes non-positive and outlier amounts), while `trip_count` and sums keep all trips.

## 3. Control checks

| Check | Result |
|---|---|
| Bronze taxi = Silver `taxi` + `taxi_rejected` | 123,471,721 = 123,470,919 + 802 |
| Sum of `trip_count` in `fact_taxi_daily` = Silver `taxi` | 123,470,919 |
| Taxi to air join (LEFT JOIN on zone and date) | 239,457 → 239,457 rows, no duplicates |
| Rows without PM2.5 after join | 7,009 (2.9%): zones 264/265 have no station, plus days without a measurement |

## 4. Reliability and operations

- **Idempotency:** file names contain the month, reruns overwrite; Silver and Gold use overwrite; Dataflows use the "Replace" method. A rerun gives the same numbers (except the growing ECB and air data).
- **Orchestration:** `pl_main` runs the four Bronze loads in parallel, waits at the `bronze_done` barrier, then runs Silver and Gold notebooks in a chain (small F2 capacity does not allow parallel Spark sessions).
- **Schedule:** weekly (Sunday 03:00), created inactive, because a scheduled run needs the paid F2 capacity to be running. It is enabled only when needed.
- **Cost control:** capacity `fabricitra` is paused after every working session.

## 5. Known limitations

- Reference files (`openaq_sensors.csv`, `zone_station_map.csv`, `taxi_zone_lookup.csv`) are updated manually.
- The list of taxi months is a manual pipeline parameter.
- Facts are daily, so time-of-day analysis is not covered.
- Taxi data covers 2024-01 → 2026-09; air, FX and GDP are wider.
- `dim_gdp` is NULL for years the World Bank has not published (2026–2030).
- Correlation between taxi trips and air quality does not prove causation.
- NO2 is reported in ppm, PM2.5 in µg/m³; values are not converted.
