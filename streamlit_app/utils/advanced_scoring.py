"""
Advanced Multi-Factor Scoring Engine
Enhanced scoring with multiple real-world factors
"""

import pandas as pd
import numpy as np
from config import SCORING_WEIGHTS


# Enhanced factor weights configuration
ADVANCED_WEIGHTS = {
    "atm": {
        "poi_density": 0.25,          # General activity indicator
        "commercial_density": 0.30,   # Commercial areas need ATMs
        "competitor_penalty": 0.35,   # Nearby ATMs reduce score
        "residential_bonus": 0.10,    # Residential areas also need ATMs
    },
    "hospital": {
        "poi_density": 0.20,
        "residential_density": 0.35,  # Hospitals serve residents
        "competitor_penalty": 0.25,
        "accessibility_bonus": 0.20,  # Near main roads
    },
    "mall": {
        "poi_density": 0.25,
        "commercial_density": 0.25,
        "competitor_penalty": 0.40,   # High penalty - malls need exclusivity
        "population_bonus": 0.10,
    },
    "pharmacy": {
        "poi_density": 0.20,
        "residential_density": 0.40,
        "competitor_penalty": 0.25,
        "hospital_proximity": 0.15,   # Bonus near hospitals
    },
    "school": {
        "residential_density": 0.45,
        "competitor_penalty": 0.30,
        "safety_factor": 0.15,
        "accessibility_bonus": 0.10,
    },
    "bank": {
        "commercial_density": 0.35,
        "poi_density": 0.20,
        "competitor_penalty": 0.35,
        "population_bonus": 0.10,
    },
    "default": {
        "poi_density": 0.30,
        "commercial_density": 0.25,
        "competitor_penalty": 0.30,
        "residential_bonus": 0.15,
    }
}


def calculate_advanced_score(df, poi_type, competitor_count=None, custom_weights=None):
    """
    Calculate multi-factor recommendation score.
    
    Factors:
    1. POI Density - General activity/footfall indicator
    2. Commercial Density - Shops, offices, restaurants
    3. Competitor Penalty - Existing facilities of same type
    4. Residential Bonus - Population density proxy
    5. Neighbor Factor - Surrounding area characteristics
    
    Args:
        df: DataFrame with grid features
        poi_type: Type of POI (atm, hospital, mall, etc.)
        competitor_count: Optional series with competitor counts per grid
        custom_weights: Optional dict to override default weights
    
    Returns:
        DataFrame with score and factor breakdown
    """
    df = df.copy()
    
    # Get weights for this POI type
    weights = custom_weights or ADVANCED_WEIGHTS.get(poi_type, ADVANCED_WEIGHTS["default"])
    
    # Factor 1: POI Density Score (normalized 0-100)
    poi_max = df["poi_density"].max()
    if poi_max > 0:
        df["poi_density_score"] = (df["poi_density"] / poi_max) * 100
    else:
        df["poi_density_score"] = 0
    
    # Factor 2: Commercial Activity Score
    # Using POI density as proxy (higher density = more commercial)
    df["commercial_score"] = df["poi_density_score"] * 0.9
    
    # Factor 3: Residential Score
    # REVISED: Residential isn't just "not commercial". It peaks at MODERATE density.
    # Gaussian-like curve peaking at 30-40% density (typical residential density)
    # This prevents the most dense areas (markets) from getting high residential scores
    df["residential_score"] = 100 - (abs(df["poi_density_score"] - 30) * 1.5)
    df["residential_score"] = df["residential_score"].clip(0, 100)
    
    # Special Handling: Schools and Hospitals prefer QUIETER areas
    # If type is school/hospital, heavily penalize extremely high density
    if poi_type in ["school", "hospital", "clinic"]:
        # Inverse commercial score for these types
        df["commercial_score"] = 100 - df["commercial_score"] 
    
    # Factor 4: Competitor Penalty
    # REVISED: Absolute penalty instead of relative. 
    # If relative, a dataset with 1 max competitor makes that 1 count as 100% penalty
    # If absolute, we say "5 competitors is saturated" (100% penalty)
    if competitor_count is not None:
        # Saturation point: 5 competitors nearby = 100% penalty
        df["competitor_penalty"] = (competitor_count * 20).clip(0, 100)
    else:
        # Fallback to neighbor density if no specific competitor count
        neighbor_max = df["neighbor_poi_density"].max()
        if neighbor_max > 0:
            df["competitor_penalty"] = (df["neighbor_poi_density"] / neighbor_max) * 100
        else:
            df["competitor_penalty"] = 0
    
    # Factor 5: Accessibility Score
    # Use logarithmic scale to favor "some access" vs "no access" without 
    # letting super-dense hubs dominate linearly
    poi_count_max = df["poi_count"].max() if "poi_count" in df.columns else 1
    if poi_count_max > 0:
        # Log-based score: diminishing returns for huge hubs
        # +1 to handle 0s
        df["accessibility_score"] = (np.log1p(df.get("poi_count", 0)) / np.log1p(poi_count_max)) * 100
    else:
        df["accessibility_score"] = 50
    
    # Calculate weighted score
    df["score"] = (
        df["poi_density_score"] * weights.get("poi_density", 0.25)
        + df["commercial_score"] * weights.get("commercial_density", 0.25)
        + df["residential_score"] * weights.get("residential_bonus", weights.get("residential_density", 0.15))
        + df["accessibility_score"] * weights.get("accessibility_bonus", 0.10)
        - df["competitor_penalty"] * weights.get("competitor_penalty", 0.30)
    )
    
    # Normalize result to useful range (0-100) but keep distribution
    # Don't just min-max normalize, as it can hide that ALL locations are bad
    # Instead, clip and scale reasonable expectations
    df["score"] = df["score"].clip(0, 100)
    
    # Re-normalize only if the distribution is too compressed
    score_min = df["score"].min()
    score_max = df["score"].max()
    if score_max > score_min + 10: # Only if there's variance
        df["normalized_score"] = ((df["score"] - score_min) / (score_max - score_min)) * 100
    else:
        df["normalized_score"] = df["score"]
    
    # Rank by score
    df["rank"] = df["score"].rank(ascending=False, method="min").astype(int)
    
    return df.sort_values("score", ascending=False)


def get_factor_breakdown(row):
    """
    Get a breakdown of factors for a single grid cell.
    Useful for tooltips and detailed analysis.
    """
    return {
        "poi_density_score": round(row.get("poi_density_score", 0), 1),
        "commercial_score": round(row.get("commercial_score", 0), 1),
        "residential_score": round(row.get("residential_score", 0), 1),
        "competitor_penalty": round(row.get("competitor_penalty", 0), 1),
        "accessibility_score": round(row.get("accessibility_score", 0), 1),
        "final_score": round(row.get("score", 0), 1)
    }


def calculate_competitor_density(df, existing_pois, radius_km=1.5):
    """
    Calculate number of existing competitors near each grid cell.
    
    Args:
        df: DataFrame with grid centroids (centroid_lat, centroid_lng)
        existing_pois: List of existing POI dicts with lat/lng
        radius_km: Search radius in kilometers (default 1.5km for advanced mode)
    
    Returns:
        Series with competitor count per grid
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
            return float('inf')
    
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
    
    competitor_counts = []
    
    for idx, row in df.iterrows():
        # Use bracket access for pandas Series (not .get())
        grid_lat = safe_float(row['centroid_lat'] if 'centroid_lat' in row.index else None)
        grid_lng = safe_float(row['centroid_lng'] if 'centroid_lng' in row.index else None)
        
        count = 0
        if grid_lat is not None and grid_lng is not None:
            for poi in existing_pois:
                poi_lat = safe_float(poi.get('lat'))
                poi_lng = safe_float(poi.get('lng'))
                if poi_lat is not None and poi_lng is not None:
                    distance = haversine(grid_lng, grid_lat, poi_lng, poi_lat)
                    if distance <= radius_km:
                        count += 1
        competitor_counts.append(count)
    
    return pd.Series(competitor_counts, index=df.index)


def generate_score_explanation(row, poi_type):
    """
    Generate human-readable explanation for a location's score.
    """
    score = row.get("score", 0)
    poi_score = row.get("poi_density_score", 0)
    competitor = row.get("competitor_penalty", 0)
    
    # Determine demand level
    if poi_score > 70:
        demand = "🔥 High demand zone"
    elif poi_score > 40:
        demand = "⚡ Moderate demand"
    else:
        demand = "❄️ Low activity area"
    
    # Determine competition level
    if competitor > 70:
        competition = "⚠️ High competition"
    elif competitor > 40:
        competition = "📊 Moderate competition"
    else:
        competition = "✅ Low competition (opportunity!)"
    
    # Overall recommendation
    if score > 60:
        recommendation = "🎯 Excellent location - highly recommended"
    elif score > 40:
        recommendation = "👍 Good location - worth considering"
    elif score > 20:
        recommendation = "🤔 Average location - proceed with caution"
    else:
        recommendation = "❌ Poor location - not recommended"
    
    return {
        "demand": demand,
        "competition": competition,
        "recommendation": recommendation
    }
