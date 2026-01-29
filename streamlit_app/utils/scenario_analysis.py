"""
What-If Scenario Analysis
Click-to-analyze functionality for location assessment
"""

from typing import Dict, List, Optional
import math


def analyze_location(
    lat: float,
    lng: float,
    poi_type: str,
    grid_data: List[Dict],
    existing_pois: List[Dict],
    all_pois: List[Dict]
) -> Dict:
    """
    Analyze a potential location for opening a new POI.
    
    Args:
        lat: Latitude of selected point
        lng: Longitude of selected point
        poi_type: Type of POI to analyze (atm, hospital, etc.)
        grid_data: All grid cell data
        existing_pois: Existing POIs of the same type
        all_pois: All POIs for activity analysis
    
    Returns:
        Dict with comprehensive location analysis
    """
    from math import radians, cos, sin, asin, sqrt
    
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return 6371 * c
    
    # Find the grid cell this location falls into
    nearest_grid = None
    min_distance = float('inf')
    
    for grid in grid_data:
        grid_lat = grid.get("centroid_lat", 0)
        grid_lng = grid.get("centroid_lng", 0)
        
        if grid_lat and grid_lng:
            distance = haversine(lng, lat, grid_lng, grid_lat)
            if distance < min_distance:
                min_distance = distance
                nearest_grid = grid
    
    if not nearest_grid:
        return {"error": "Could not find grid cell for this location"}
    
    # Analyze competitors within 1km, 2km
    competitors_1km = []
    competitors_2km = []
    nearest_competitor = None
    nearest_distance = float('inf')
    
    for poi in existing_pois:
        poi_lat = poi.get("lat", 0)
        poi_lng = poi.get("lng", 0)
        
        if poi_lat and poi_lng:
            distance = haversine(lng, lat, poi_lng, poi_lat)
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_competitor = {
                    "name": poi.get("name", "Unnamed"),
                    "distance_m": int(distance * 1000)
                }
            
            if distance <= 1:
                competitors_1km.append(poi)
            if distance <= 2:
                competitors_2km.append(poi)
    
    # Count all POIs within catchment (activity indicator)
    pois_500m = 0
    pois_1km = 0
    
    for poi in all_pois:
        poi_lat = poi.get("lat", 0)
        poi_lng = poi.get("lng", 0)
        
        if poi_lat and poi_lng:
            distance = haversine(lng, lat, poi_lng, poi_lat)
            if distance <= 0.5:
                pois_500m += 1
            if distance <= 1:
                pois_1km += 1
    
    # Calculate opportunity score
    activity_score = min(100, pois_1km * 2)  # More POIs = more activity
    competition_penalty = min(100, len(competitors_1km) * 20)  # Each competitor = 20 penalty
    
    opportunity_score = activity_score - competition_penalty + 50  # Base of 50
    opportunity_score = max(0, min(100, opportunity_score))  # Clamp to 0-100
    
    # Generate recommendation
    if opportunity_score >= 70:
        verdict = "🎯 Excellent"
        verdict_detail = "High activity, low competition - Recommended!"
        color = "#00f5d4"
    elif opportunity_score >= 50:
        verdict = "👍 Good"
        verdict_detail = "Reasonable opportunity with moderate competition"
        color = "#ffc107"
    elif opportunity_score >= 30:
        verdict = "⚠️ Moderate"
        verdict_detail = "Some potential, but watch competition"
        color = "#ff9800"
    else:
        verdict = "❌ Poor"
        verdict_detail = "High competition or low activity area"
        color = "#ef476f"
    
    # Estimated catchment population (rough)
    # Based on 1km radius and assuming 5000 people/sq km avg in NCR
    catchment_area = math.pi * 1  # 1 km radius
    density_factor = pois_1km / 50 if pois_1km > 0 else 0.5
    estimated_population = int(catchment_area * 5000 * density_factor)
    
    return {
        "location": {
            "lat": lat,
            "lng": lng
        },
        "grid_info": {
            "grid_id": nearest_grid.get("grid_id"),
            "poi_density": round(nearest_grid.get("poi_density", 0), 1),
            "poi_count": nearest_grid.get("poi_count", 0)
        },
        "competition": {
            "within_1km": len(competitors_1km),
            "within_2km": len(competitors_2km),
            "nearest": nearest_competitor
        },
        "activity": {
            "pois_500m": pois_500m,
            "pois_1km": pois_1km,
            "activity_level": "High" if pois_1km > 30 else "Medium" if pois_1km > 15 else "Low"
        },
        "catchment": {
            "radius_km": 1,
            "estimated_population": estimated_population
        },
        "scores": {
            "activity_score": activity_score,
            "competition_penalty": competition_penalty,
            "opportunity_score": opportunity_score
        },
        "recommendation": {
            "verdict": verdict,
            "detail": verdict_detail,
            "color": color
        }
    }


def format_analysis_html(analysis: Dict) -> str:
    """
    Format analysis results as HTML for display.
    """
    if "error" in analysis:
        return f'<div style="color: #ef476f;">{analysis["error"]}</div>'
    
    rec = analysis["recommendation"]
    comp = analysis["competition"]
    act = analysis["activity"]
    score = analysis["scores"]
    
    html = f"""
    <div style="background: rgba(0,0,0,0.3); border-radius: 16px; padding: 1.5rem; border: 1px solid {rec['color']};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem; font-weight: bold; color: {rec['color']};">
                {rec['verdict']}
            </span>
            <span style="font-size: 2rem; font-weight: bold; color: {rec['color']};">
                {score['opportunity_score']}/100
            </span>
        </div>
        
        <p style="color: #aaa; margin-bottom: 1rem;">{rec['detail']}</p>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
                <div style="color: #888; font-size: 0.85rem;">🏪 Activity (1km)</div>
                <div style="font-size: 1.2rem; font-weight: bold;">{act['pois_1km']} POIs</div>
                <div style="color: #888; font-size: 0.85rem;">Level: {act['activity_level']}</div>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
                <div style="color: #888; font-size: 0.85rem;">🏢 Competition (1km)</div>
                <div style="font-size: 1.2rem; font-weight: bold;">{comp['within_1km']} Competitors</div>
                <div style="color: #888; font-size: 0.85rem;">Nearest: {comp['nearest']['distance_m'] if comp['nearest'] else 'N/A'}m</div>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
                <div style="color: #888; font-size: 0.85rem;">👥 Catchment Pop.</div>
                <div style="font-size: 1.2rem; font-weight: bold;">{analysis['catchment']['estimated_population']:,}</div>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
                <div style="color: #888; font-size: 0.85rem;">📍 Grid Cell</div>
                <div style="font-size: 1.2rem; font-weight: bold;">#{analysis['grid_info']['grid_id']}</div>
                <div style="color: #888; font-size: 0.85rem;">Density: {analysis['grid_info']['poi_density']}</div>
            </div>
        </div>
    </div>
    """
    return html
