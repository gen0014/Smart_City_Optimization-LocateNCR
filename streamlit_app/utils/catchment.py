"""
Catchment Area Analysis
Calculate service radius and population coverage
"""

import math
from typing import List, Dict, Tuple


def create_catchment_circle(center_lat: float, center_lng: float, radius_km: float, num_points: int = 64) -> List[List[float]]:
    """
    Create a circle polygon for catchment area visualization.
    
    Args:
        center_lat: Latitude of center point
        center_lng: Longitude of center point
        radius_km: Radius in kilometers
        num_points: Number of points in the circle (more = smoother)
    
    Returns:
        List of [lng, lat] coordinates forming the circle
    """
    coords = []
    
    for i in range(num_points + 1):
        angle = (2 * math.pi * i) / num_points
        
        # Convert radius from km to degrees (approximate)
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude ≈ 111 * cos(lat) km
        lat_offset = (radius_km / 111) * math.sin(angle)
        lng_offset = (radius_km / (111 * math.cos(math.radians(center_lat)))) * math.cos(angle)
        
        coords.append([center_lng + lng_offset, center_lat + lat_offset])
    
    return coords


def calculate_catchment_metrics(
    center_lat: float, 
    center_lng: float, 
    radius_km: float,
    all_pois: List[Dict],
    grid_data: List[Dict]
) -> Dict:
    """
    Calculate metrics for a catchment area.
    
    Args:
        center_lat: Center latitude
        center_lng: Center longitude
        radius_km: Radius in km
        all_pois: List of all POIs with lat/lng
        grid_data: Grid cell data with poi_density
    
    Returns:
        Dict with catchment metrics
    """
    from math import radians, cos, sin, asin, sqrt
    
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return 6371 * c
    
    # Count POIs in catchment
    pois_in_catchment = 0
    poi_types = {}
    
    for poi in all_pois:
        poi_lat = poi.get("lat", 0)
        poi_lng = poi.get("lng", 0)
        
        if poi_lat and poi_lng:
            distance = haversine(center_lng, center_lat, poi_lng, poi_lat)
            if distance <= radius_km:
                pois_in_catchment += 1
                poi_type = poi.get("poi_type", poi.get("amenity", "other"))
                poi_types[poi_type] = poi_types.get(poi_type, 0) + 1
    
    # Count grid cells in catchment
    grids_in_catchment = 0
    total_density = 0
    
    for grid in grid_data:
        grid_lat = grid.get("centroid_lat", 0)
        grid_lng = grid.get("centroid_lng", 0)
        
        if grid_lat and grid_lng:
            distance = haversine(center_lng, center_lat, grid_lng, grid_lat)
            if distance <= radius_km:
                grids_in_catchment += 1
                total_density += grid.get("poi_density", 0)
    
    avg_density = total_density / grids_in_catchment if grids_in_catchment > 0 else 0
    
    # Estimate population (rough estimate based on density and area)
    area_sq_km = math.pi * radius_km ** 2
    # Assuming avg 5000 people per sq km in urban NCR
    estimated_population = int(area_sq_km * 5000 * (avg_density / 100 + 0.5))
    
    return {
        "radius_km": radius_km,
        "area_sq_km": round(area_sq_km, 2),
        "pois_in_catchment": pois_in_catchment,
        "poi_breakdown": poi_types,
        "grids_covered": grids_in_catchment,
        "avg_density": round(avg_density, 1),
        "estimated_population": estimated_population
    }


def find_competitor_overlap(
    center_lat: float,
    center_lng: float,
    radius_km: float,
    competitor_pois: List[Dict]
) -> Dict:
    """
    Find competitors within catchment and calculate overlap.
    
    Returns:
        Dict with overlap analysis
    """
    from math import radians, cos, sin, asin, sqrt
    
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return 6371 * c
    
    competitors_in_radius = []
    nearest_competitor = None
    min_distance = float('inf')
    
    for poi in competitor_pois:
        poi_lat = poi.get("lat", 0)
        poi_lng = poi.get("lng", 0)
        
        if poi_lat and poi_lng:
            distance = haversine(center_lng, center_lat, poi_lng, poi_lat)
            
            if distance <= radius_km:
                competitors_in_radius.append({
                    "name": poi.get("name", "Unnamed"),
                    "distance_km": round(distance, 2),
                    "lat": poi_lat,
                    "lng": poi_lng
                })
            
            if distance < min_distance:
                min_distance = distance
                nearest_competitor = {
                    "name": poi.get("name", "Unnamed"),
                    "distance_km": round(distance, 2)
                }
    
    # Sort by distance
    competitors_in_radius.sort(key=lambda x: x["distance_km"])
    
    return {
        "competitors_in_catchment": len(competitors_in_radius),
        "competitor_list": competitors_in_radius[:10],  # Top 10 nearest
        "nearest_competitor": nearest_competitor,
        "competition_level": "High" if len(competitors_in_radius) > 5 else "Medium" if len(competitors_in_radius) > 2 else "Low"
    }


def get_catchment_layers_data(recommendations, radii=[0.5, 1.0, 2.0]):
    """
    Generate catchment circle data for multiple recommendations.
    
    Args:
        recommendations: List of dicts with centroid_lat, centroid_lng
        radii: List of radius values to show (in km)
    
    Returns:
        List of circle polygon data for PyDeck
    """
    circles = []
    
    # Colors for different radii (with transparency)
    radius_colors = {
        0.5: [0, 245, 212, 40],   # Cyan, very transparent
        1.0: [0, 245, 212, 25],   # Cyan, more transparent
        2.0: [0, 245, 212, 15],   # Cyan, very faint
    }
    
    for rec in recommendations:
        lat = rec.get("centroid_lat", 0)
        lng = rec.get("centroid_lng", 0)
        grid_id = rec.get("grid_id", 0)
        
        if lat and lng:
            for radius in sorted(radii, reverse=True):  # Draw larger first
                coords = create_catchment_circle(lat, lng, radius)
                circles.append({
                    "polygon": coords,
                    "grid_id": grid_id,
                    "radius": radius,
                    "fill_color": radius_colors.get(radius, [0, 245, 212, 30])
                })
    
    return circles
