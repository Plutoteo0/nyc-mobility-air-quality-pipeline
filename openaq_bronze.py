import json
import requests
import pandas as pd
from dotenv import load_dotenv
import time
import os

load_dotenv()
OPENAQ_KEY = os.getenv("OPENAQ_API_KEY")

def fetch_sensors_days(sensor_id):
    all_results = []
    page = 1
    while True:
        for attempt in range(3):
            response = requests.get(
                f"https://api.openaq.org/v3/sensors/{sensor_id}/days",
                headers={"X-API-Key": OPENAQ_KEY},
                params={"date_from": "2016-07-01", "date_to": "2026-11-01", "limit": 1000, "page": page},
            )
            if response.status_code == 200:
                break
            time.sleep(2 * (attempt + 1))
        else:
            response.raise_for_status()
        results = response.json()['results']
        all_results.extend(results)

        if len(results) < 1000:
            break
        page += 1
        time.sleep(1)
    return all_results

sensors = pd.read_csv("reference/openaq_sensors.csv")
sensors = sensors[sensors['parameter'].isin(['pm25','no2'])]

for _, row in sensors.iterrows():
    sensor_id = row['sensor_id']
    res = fetch_sensors_days(sensor_id)
    with open(f"bronze/openaq_days_{sensor_id}.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False)

    values = [r["value"] for r in res if r["value"] is not None]
    print(
        sensor_id, row['parameter'], len(res),
        res[0]["period"]["datetimeFrom"]["local"][:10],
        res[-1]["period"]["datetimeFrom"]["local"][:10],
        "low_cov:", sum(1 for r in res if r["coverage"]["percentCoverage"] < 75),
        "none:", sum(1 for r in res if r["value"] is None),
        "neg:", sum(1 for v in values if v < 0),
    )
    time.sleep(1)