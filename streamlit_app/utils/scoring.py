"""
Scoring Module
Recommendation scoring algorithms matching the Spark notebook logic.
"""

import pandas as pd
from config import SCORING_WEIGHTS


def calculate_score(df, poi_type, existing_pois=None):
    """
    Calculate recommendation scores for grid cells.
    
    Args:
        df: DataFrame with poi_density and neighbor_poi_density columns
        poi_type: 'atm', 'hospital', or 'mall'
        existing_pois: List of existing POIs of this type with lat/lng
    
    Returns:
        DataFrame with added 'score' and 'rank' columns
    """
    weights = SCORING_WEIGHTS.get(poi_type, SCORING_WEIGHTS["atm"])
    
    df = df.copy()
    
    # Count competitors of THIS POI type per grid cell
    if existing_pois:
        df["competitor_count"] = _count_pois_in_grid(df, existing_pois)
    else:
        df["competitor_count"] = 0
    
    # Score formula:
    # + High general POI density = good (indicates demand/footfall)
    # - High competitor count = bad (market saturation)
    df["score"] = (
        df["poi_density"] * weights["poi_density_weight"]
    ) - (
        df["competitor_count"] * weights["neighbor_penalty"] * 5  # Scale penalty
    )
    
    # Rank by score (higher is better)
    df["rank"] = df["score"].rank(ascending=False, method="min").astype(int)
    
    return df.sort_values("score", ascending=False)


def _count_pois_in_grid(df, pois, radius_km=2.0):
    """
    Count how many POIs fall within radius_km of each grid cell centroid.
    
    Args:
        df: DataFrame with centroid_lat, centroid_lng columns
        pois: List of dicts with lat, lng keys
        radius_km: Search radius in kilometers (default 2km)
    
    Returns:
        List with count per grid cell
    """
    from math import radians, cos, sin, asin, sqrt
    import pandas as pd
    
    def haversine(lon1, lat1, lon2, lat2):
        """Calculate distance between two points in km."""
        try:
            lon1, lat1, lon2, lat2 = map(lambda x: radians(float(x)), [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            return 6371 * c  # Earth radius in km
        except (TypeError, ValueError):
            return float('inf')  # Return infinite distance if conversion fails
    
    def safe_float(val):
        """Safely convert value to float, handling None, NaN, etc."""
        if val is None:
            return None
        if pd.isna(val):
            return None
        try:
            return float(val)
        except (TypeError, ValueError):
            return None
    
    counts = []
    for idx, row in df.iterrows():
        # Use bracket access for pandas Series (not .get())
        grid_lat = safe_float(row['centroid_lat'] if 'centroid_lat' in row.index else None)
        grid_lng = safe_float(row['centroid_lng'] if 'centroid_lng' in row.index else None)
        
        count = 0
        if grid_lat is not None and grid_lng is not None:
            for poi in pois:
                poi_lat = safe_float(poi.get('lat'))
                poi_lng = safe_float(poi.get('lng'))
                if poi_lat is not None and poi_lng is not None:
                    distance = haversine(grid_lng, grid_lat, poi_lng, poi_lat)
                    if distance <= radius_km:
                        count += 1
        counts.append(count)
    
    return counts


def get_top_recommendations(df, poi_type, top_n=10):
    """
    Get top N recommended locations for a POI type.
    
    Args:
        df: DataFrame with grid features
        poi_type: 'atm', 'hospital', or 'mall'
        top_n: Number of recommendations to return
    
    Returns:
        DataFrame with top recommendations
    """
    scored_df = calculate_score(df, poi_type)
    return scored_df.head(top_n)


def generate_recommendation_reason(row, poi_type):
    """
    Generate a human-readable reason for the recommendation.
    """
    density = row["poi_density"]
    neighbor_density = row["neighbor_poi_density"]
    score = row["score"]
    
    if density > neighbor_density:
        demand_level = "high demand"
    else:
        demand_level = "moderate demand"
    
    if neighbor_density < 50:
        competition = "low competition"
    elif neighbor_density < 150:
        competition = "moderate competition"
    else:
        competition = "high competition area"
    
    poi_labels = {
        "atm": "ATM",
        "hospital": "Healthcare Facility",
        "mall": "Shopping Mall"
    }
    
    return f"Recommended for {poi_labels.get(poi_type, 'POI')}: {demand_level} area with {competition}. Score: {score:.1f}"


def normalize_scores(df):
    """
    Normalize scores to 0-100 range for visualization.
    """
    df = df.copy()
    min_score = df["score"].min()
    max_score = df["score"].max()
    
    if max_score > min_score:
        df["normalized_score"] = (
            (df["score"] - min_score) / (max_score - min_score) * 100
        )
    else:
        df["normalized_score"] = 50
    
    return df
