"""
Debug script to understand why competitor_count is always 0.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.queries import get_grid_with_neighbor_density, get_pois_by_type
import pandas as pd

# Load data
print("Loading grid data...")
grid_data = get_grid_with_neighbor_density()
df = pd.DataFrame(grid_data)

print(f"\nGrid DataFrame columns: {df.columns.tolist()}")
print(f"\nSample grid cell:")
sample = df.iloc[0]
print(f"  grid_id: {sample.get('grid_id')}")
print(f"  centroid_lat: {sample.get('centroid_lat')}")
print(f"  centroid_lng: {sample.get('centroid_lng')}")
print(f"  poi_density: {sample.get('poi_density')}")

# Check if centroids exist
has_lat = 'centroid_lat' in df.columns and df['centroid_lat'].notna().any()
has_lng = 'centroid_lng' in df.columns and df['centroid_lng'].notna().any()
print(f"\nHas centroid_lat: {has_lat}")
print(f"Has centroid_lng: {has_lng}")

if has_lat and has_lng:
    print(f"\nCentroid lat range: {df['centroid_lat'].min():.4f} to {df['centroid_lat'].max():.4f}")
    print(f"Centroid lng range: {df['centroid_lng'].min():.4f} to {df['centroid_lng'].max():.4f}")

# Load POIs
print("\n--- POI Data ---")
atms = get_pois_by_type("atm")
print(f"ATM count: {len(atms)}")
if atms:
    sample_poi = atms[0]
    print(f"Sample ATM:")
    print(f"  Keys: {sample_poi.keys()}")
    print(f"  lat: {sample_poi.get('lat')}")
    print(f"  lng: {sample_poi.get('lng')}")
    print(f"  name: {sample_poi.get('name')}")

# Try a manual distance check
if has_lat and has_lng and atms:
    from math import radians, cos, sin, asin, sqrt
    
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return 6371 * c
    
    # Distance from first grid cell to first ATM
    grid_lat = df.iloc[0]['centroid_lat']
    grid_lng = df.iloc[0]['centroid_lng']
    poi_lat = atms[0].get('lat', 0)
    poi_lng = atms[0].get('lng', 0)
    
    print(f"\n--- Distance Check ---")
    print(f"Grid[0]: ({grid_lat}, {grid_lng})")
    print(f"ATM[0]: ({poi_lat}, {poi_lng})")
    
    if grid_lat and grid_lng and poi_lat and poi_lng:
        dist = haversine(grid_lng, grid_lat, poi_lng, poi_lat)
        print(f"Distance: {dist:.2f} km")
    else:
        print("Missing coordinate values!")
        
    # Find closest ATM to first grid cell
    print(f"\nFinding closest ATM to Grid[0]...")
    min_dist = float('inf')
    closest_atm = None
    for atm in atms:
        a_lat = atm.get('lat')
        a_lng = atm.get('lng')
        if a_lat and a_lng and grid_lat and grid_lng:
            d = haversine(grid_lng, grid_lat, a_lng, a_lat)
            if d < min_dist:
                min_dist = d
                closest_atm = atm
    
    if closest_atm:
        print(f"Closest ATM: {closest_atm.get('name')} at {min_dist:.2f} km")
    else:
        print("No ATMs with valid coordinates found!")
