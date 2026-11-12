import geopandas as gpd

zones = gpd.read_file("reference/taxi_zones/taxi_zones.shp")
print(zones.crs)
zones_4326 = zones.to_crs(epsg=4326)
print(zones_4326.total_bounds)
print(zones["LocationID"].nunique(), len(zones))
print(zones[zones["LocationID"].duplicated(keep=False)][["LocationID", "zone"]])