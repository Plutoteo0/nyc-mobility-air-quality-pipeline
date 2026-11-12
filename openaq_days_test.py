import os
import json
import requests
from dotenv import load_dotenv
import time

load_dotenv()
OPENAQ_KEY = os.getenv("OPENAQ_API_KEY")

all_results = []
page = 1
while True:
    response = requests.get(
        "https://api.openaq.org/v3/sensors/673/days",
        headers={"X-API-Key": OPENAQ_KEY},
        params={"date_from": "2016-07-01", "date_to": "2026-11-01", "limit": 1000, "page": page},
    )
    results = response.json()['results']
    all_results.extend(results)

    if len(results) < 1000:
        break
    page += 1
    time.sleep(1)

print("страниц:", page, "записей:", len(all_results))
print("первая дата:", all_results[0]["period"]["datetimeFrom"]["local"])
print("последняя дата:", all_results[-1]["period"]["datetimeFrom"]["local"])
print("низкое покрытие (<75%):", sum(1 for r in all_results if r["coverage"]["percentCoverage"] < 75))
none_records = [r for r in all_results if r["value"] is None]
print("value is None:", len(none_records))
if none_records:
    print(json.dumps(none_records[0], indent=2))
print("минимальное value (без None):", min(r["value"] for r in all_results if r["value"] is not None))