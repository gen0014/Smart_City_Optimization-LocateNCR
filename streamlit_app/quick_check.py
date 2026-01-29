"""Quick data check"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db.queries import get_grid_with_neighbor_density, get_pois_by_type
import pandas as pd

grid_data = get_grid_with_neighbor_density()
df = pd.DataFrame(grid_data)
atms = get_pois_by_type("atm")

print("Grid sample (first row):")
print(f"  centroid_lat type: {type(df.iloc[0].get('centroid_lat'))}, value: {df.iloc[0].get('centroid_lat')}")
print(f"  centroid_lng type: {type(df.iloc[0].get('centroid_lng'))}, value: {df.iloc[0].get('centroid_lng')}")

print("\nATM sample (first row):")
if atms:
    print(f"  lat type: {type(atms[0].get('lat'))}, value: {atms[0].get('lat')}")
    print(f"  lng type: {type(atms[0].get('lng'))}, value: {atms[0].get('lng')}")

# Test distance
from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

g_lat = float(df.iloc[0]['centroid_lat'])
g_lng = float(df.iloc[0]['centroid_lng'])
a_lat = float(atms[0]['lat'])
a_lng = float(atms[0]['lng'])

print(f"\nDistance from Grid[0] to ATM[0]: {haversine(g_lng, g_lat, a_lng, a_lat):.2f} km")

# Count ALL ATMs within various radii of ALL grids
print("\nCounting ATMs at different radii...")
for radius in [1.0, 2.0, 5.0, 10.0]:
    total_count = 0
    grids_with_pois = 0
    for _, row in df.iterrows():
        count = 0
        gl = float(row['centroid_lat']) if row['centroid_lat'] else 0
        gn = float(row['centroid_lng']) if row['centroid_lng'] else 0
        if gl and gn:
            for atm in atms:
                al = float(atm['lat']) if atm['lat'] else 0
                an = float(atm['lng']) if atm['lng'] else 0
                if al and an:
                    if haversine(gn, gl, an, al) <= radius:
                        count += 1
        total_count += count
        if count > 0:
            grids_with_pois += 1
    print(f"  {radius}km: {grids_with_pois}/{len(df)} grids have ATMs nearby, total count: {total_count}")
