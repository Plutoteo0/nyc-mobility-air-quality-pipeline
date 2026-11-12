import pandas as pd
import geopandas as gpd
from config import MAX_STATION_KM

zones = gpd.read_file("reference/taxi_zones/taxi_zones.shp")

stations = pd.read_csv("reference/openaq_stations.csv")
sensors = pd.read_csv("reference/openaq_sensors.csv")

sensors = sensors[sensors["parameter"].isin(["pm25","no2"])]
merged = stations.merge(sensors, left_on="id", right_on="station_id")

points = gpd.GeoDataFrame(
    merged,
    geometry=gpd.points_from_xy(merged["longitude"], merged["latitude"]),
    crs="EPSG:4326",
).to_crs(epsg=2263)

zone_pts = zones[["LocationID", "zone", "borough", "geometry"]].copy()
zone_pts["geometry"] = zone_pts.geometry.centroid

def nearest_station(parameter):
    pts = points[points["parameter"] == parameter][["station_id", "name", "geometry"]]
    res = gpd.sjoin_nearest(zone_pts, pts, distance_col="dist_ft")
    res["dist_km"] = res["dist_ft"] / 3280.84
    res["parameter"] = parameter
    return res

mapped_table = pd.concat([nearest_station("pm25"), nearest_station("no2")])
mapped_table = mapped_table.rename(columns={"LocationID": "zone_id", "name": "station_name"})
mapped_table = mapped_table[["zone_id", "parameter", "station_id", "station_name", "dist_km"]]

mapped_table["is_far_station"] = mapped_table["dist_km"] > MAX_STATION_KM
mapped_table.to_csv("reference/zone_station_map.csv", index=False)

print(len(mapped_table))
print(mapped_table.groupby("parameter")["is_far_station"].sum())
print(mapped_table.duplicated(["zone_id", "parameter"]).sum())