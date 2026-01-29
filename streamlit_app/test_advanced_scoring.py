"""
Test script to verify Advanced Multi-Factor Scoring works correctly.
Run from streamlit_app directory: python test_advanced_scoring.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.queries import get_grid_with_neighbor_density, get_pois_by_type
from utils.advanced_scoring import calculate_advanced_score, calculate_competitor_density
from config import POI_TYPES
import pandas as pd

def test_advanced_scoring():
    print("Loading grid data...")
    grid_data = get_grid_with_neighbor_density()
    df = pd.DataFrame(grid_data)
    print(f"Loaded {len(df)} grid cells\n")
    
    test_types = ["atm", "hospital", "mall"]
    results = {}
    
    print("=" * 70)
    print("ADVANCED MULTI-FACTOR SCORING TEST")
    print("=" * 70)
    
    for poi_type in test_types:
        print(f"\n--- Testing {POI_TYPES[poi_type]['label']} (Advanced Mode) ---")
        
        # Get existing POIs
        existing_pois = get_pois_by_type(poi_type)
        print(f"Found {len(existing_pois)} existing {poi_type}s")
        
        # Calculate competitor density (the fixed function)
        competitor_counts = calculate_competitor_density(df.copy(), existing_pois, radius_km=1.5)
        
        # Check competitor counts
        non_zero = (competitor_counts > 0).sum()
        max_comp = competitor_counts.max()
        print(f"Competitor density: {non_zero} cells have nearby {poi_type}s (max: {max_comp})")
        
        # Calculate advanced score
        scored_df = calculate_advanced_score(df.copy(), poi_type, competitor_counts)
        
        # Get top 5
        top5 = scored_df.head(5)[["grid_id", "score", "poi_density_score", "commercial_score", 
                                   "residential_score", "competitor_penalty", "accessibility_score"]].to_dict('records')
        
        results[poi_type] = [int(row["grid_id"]) for row in top5]
        
        print(f"Top 5 Grid IDs: {results[poi_type]}")
        print(f"Factor breakdown (Grid #{top5[0]['grid_id']}):")
        print(f"  POI Density Score: {top5[0]['poi_density_score']:.1f}")
        print(f"  Commercial Score:  {top5[0]['commercial_score']:.1f}")
        print(f"  Residential Score: {top5[0]['residential_score']:.1f}")
        print(f"  Accessibility:     {top5[0]['accessibility_score']:.1f}")
        print(f"  Competitor Penalty: {top5[0]['competitor_penalty']:.1f}")
        print(f"  FINAL SCORE:       {top5[0]['score']:.1f}")
    
    # Compare results
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    
    all_same = set(results["atm"]) == set(results["hospital"]) == set(results["mall"])
    
    for i, t1 in enumerate(test_types):
        for t2 in test_types[i+1:]:
            overlap = len(set(results[t1]) & set(results[t2]))
            print(f"  {t1.upper()} ∩ {t2.upper()}: {overlap}/5 overlap")
    
    print()
    if all_same:
        print("❌ FAIL: All POI types have identical recommendations")
    else:
        print("✅ SUCCESS: Advanced scoring produces different recommendations per POI type!")

if __name__ == "__main__":
    test_advanced_scoring()
