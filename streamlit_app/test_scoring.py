"""
Test script to verify POI-specific scoring produces different results.
Run from streamlit_app directory: python test_scoring.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.queries import get_grid_with_neighbor_density, get_pois_by_type
from utils.scoring import calculate_score, normalize_scores
from config import POI_TYPES
import pandas as pd

def test_poi_scoring():
    print("Loading grid data...")
    grid_data = get_grid_with_neighbor_density()
    df = pd.DataFrame(grid_data)
    print(f"Loaded {len(df)} grid cells\n")
    
    results = {}
    all_poi_types = list(POI_TYPES.keys())
    
    print(f"Testing {len(all_poi_types)} POI types: {all_poi_types}\n")
    print("=" * 70)
    
    for poi_type in all_poi_types:
        print(f"\n--- Testing {POI_TYPES[poi_type]['label']} ---")
        
        # Get existing POIs of this type
        existing_pois = get_pois_by_type(poi_type)
        print(f"Found {len(existing_pois)} existing {poi_type}s")
        
        if len(existing_pois) == 0:
            print(f"⚠️  No POIs found for {poi_type}, skipping...")
            results[poi_type] = []
            continue
        
        # Calculate scores
        scored_df = calculate_score(df.copy(), poi_type, existing_pois)
        scored_df = normalize_scores(scored_df)
        
        # Get top 5
        top5 = scored_df.head(5)[["grid_id", "score", "competitor_count"]].values.tolist()
        results[poi_type] = [int(row[0]) for row in top5]
        
        print(f"Top 5 Grid IDs: {results[poi_type]}")
        print(f"Top 5 Scores: {[round(row[1], 2) for row in top5]}")
        print(f"Competitor counts: {[int(row[2]) for row in top5]}")
    
    # Check if results differ
    print("\n" + "=" * 70)
    print("\n📊 COMPARISON SUMMARY")
    print("=" * 70)
    
    # Compare key POI types
    key_types = ["atm", "hospital", "mall"]
    valid_types = [t for t in key_types if t in results and len(results[t]) > 0]
    
    if len(valid_types) < 2:
        print("❌ Not enough POI types with data to compare")
        return
    
    all_identical = True
    for i, t1 in enumerate(valid_types):
        for t2 in valid_types[i+1:]:
            overlap = len(set(results[t1]) & set(results[t2]))
            if set(results[t1]) != set(results[t2]):
                all_identical = False
            print(f"  {t1.upper()} ∩ {t2.upper()}: {overlap}/5 overlap")
    
    print()
    if all_identical:
        print("❌ FAIL: Key POI types have identical top 5 recommendations")
    else:
        print("✅ SUCCESS: POI types have different top 5 recommendations!")
        
    # Show detailed comparison table
    print("\n📋 Top 5 Grid IDs by POI Type:")
    print("-" * 50)
    header = "Rank | " + " | ".join([f"{t[:8]:^8}" for t in valid_types])
    print(header)
    print("-" * 50)
    for rank in range(5):
        row = f"  {rank+1}  | "
        for t in valid_types:
            if rank < len(results[t]):
                row += f"{results[t][rank]:^8} | "
            else:
                row += f"{'N/A':^8} | "
        print(row)

if __name__ == "__main__":
    test_poi_scoring()
