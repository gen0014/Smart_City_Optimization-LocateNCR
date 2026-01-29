"""
Geometry Utilities
Helper functions for working with spatial data.
"""

import json


def parse_geometry_to_coordinates(geometry):
    """
    Parse PostGIS geometry (GeoJSON) to coordinate list for PyDeck.
    
    Args:
        geometry: GeoJSON dict or string
    
    Returns:
        List of coordinate rings for polygons
    """
    if isinstance(geometry, str):
        geometry = json.loads(geometry)
    
    geom_type = geometry.get("type", "")
    coordinates = geometry.get("coordinates", [])
    
    if geom_type == "Polygon":
        return coordinates
    elif geom_type == "MultiPolygon":
        # Flatten to list of polygons
        return [ring for polygon in coordinates for ring in polygon]
    else:
        return coordinates


def geometry_to_polygon_layer_data(rows):
    """
    Convert database rows with geometry to PyDeck polygon format.
    
    Args:
        rows: List of dicts with 'geometry' key containing GeoJSON
    
    Returns:
        List of dicts formatted for PyDeck PolygonLayer
    """
    result = []
    for row in rows:
        geometry = row.get("geometry")
        if not geometry:
            continue
        
        coords = parse_geometry_to_coordinates(geometry)
        
        # PyDeck expects flat list of [lng, lat] pairs
        if coords and len(coords) > 0:
            # For Polygon, take the outer ring
            outer_ring = coords[0] if isinstance(coords[0][0], list) else coords
            
            result.append({
                "polygon": outer_ring,
                "grid_id": row.get("grid_id"),
                "poi_density": row.get("poi_density", 0),
                "poi_count": row.get("poi_count", 0),
                "score": row.get("score", 0),
                "normalized_score": row.get("normalized_score", 50),
                "centroid_lat": row.get("centroid_lat"),
                "centroid_lng": row.get("centroid_lng")
            })
    
    return result


def get_color_from_score(normalized_score, poi_type="atm"):
    """
    Get RGBA color based on normalized score.
    
    Higher scores = more intense color
    """
    # Base colors for each POI type
    colors = {
        "atm": [67, 97, 238],      # Blue
        "hospital": [239, 71, 111], # Red/Pink
        "mall": [76, 201, 240]      # Cyan
    }
    
    base = colors.get(poi_type, colors["atm"])
    
    # Intensity based on score (0-100)
    alpha = int(50 + (normalized_score / 100) * 180)  # 50-230 range
    
    return base + [alpha]


def create_boundary_geojson(boundary_data):
    """
    Create GeoJSON FeatureCollection from boundary query result.
    """
    if not boundary_data:
        return None
    
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"name": boundary_data.get("name", "NCR")},
            "geometry": boundary_data.get("geometry")
        }]
    }
