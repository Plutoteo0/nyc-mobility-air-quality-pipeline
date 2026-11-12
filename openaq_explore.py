import requests
import pandas as pd
from dotenv import load_dotenv
import os
import json

load_dotenv()

OPENAQ_KEY = os.getenv("OPENAQ_API_KEY")

response = requests.get(
    "https://api.openaq.org/v3/locations",
    headers={"X-API-Key": OPENAQ_KEY},
    params={"bbox": "-74.197540,40.517975,-73.575439,40.965382","limit": 1000})

data = response.json()
df = pd.DataFrame(data["results"])
print(df.columns)
datetimeFirst = [time["utc"] for time in df['datetimeFirst'].values]
datetimeLast = [time["utc"] for time in df['datetimeLast'].values]
df["datetimeLast"] = pd.to_datetime(datetimeLast, utc=True)
df["datetimeFirst"] = pd.to_datetime(datetimeFirst, utc=True)

mask = (df["datetimeFirst"] <= "2016-07-01") & (df["datetimeLast"] >= "2026-10-01")
stations = df[mask].copy()
sensors = stations[["id", "sensors"]].explode("sensors")

sensors_list = [{"station_id": i, "sensor_id": s['id'], "parameter": s["parameter"]["name"]} for i, s in zip(sensors["id"], sensors['sensors'])]
sensors_df = pd.DataFrame(sensors_list)

stations["latitude"] = stations["coordinates"].apply(lambda coord: coord['latitude'])
stations["longitude"] = stations["coordinates"].apply(lambda coord: coord['longitude'])

stations = stations[["id", "name", "latitude", "longitude", "timezone"]]

sensors_df.to_csv("./reference/openaq_sensors.csv", index=False)
stations.to_csv("./reference/openaq_stations.csv", index=False)

with open("bronze/openaq_locations_nyc.json", "w" ,encoding="utf-8") as f:
    json.dump(data, fp=f, ensure_ascii=False)

mask_sensors = sensors_df['parameter'].isin(["pm25","no2"])
sensors_id = sensors_df[mask_sensors]['sensor_id']

sensor_data_response = []
for sensor_id in sensors_id:
    response_sensors = requests.get(
        f"https://api.openaq.org/v3/sensors/{sensor_id}",
        headers={"X-API-Key": OPENAQ_KEY}
    )
    sensors_data = response_sensors.json()["results"][0]
    sensor_data_response.append({"sensor_id": sensors_data['id'], 
                                 "name": sensors_data["parameter"]["name"], 
                                 "datetimeLast": sensors_data['datetimeLast']["utc"],
                                 "datetimeFirst": sensors_data['datetimeFirst']['utc'],
                                 "observedCount": sensors_data['coverage']['observedCount']})

print(sensor_data_response)