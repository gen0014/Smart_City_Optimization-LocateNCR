"""
Page 1: Location Finder
Interactive map for POI location recommendations
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import json
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw

# Page config
st.set_page_config(
    page_title="Location Finder - LocateNCR",
    page_icon="📍",
    layout="wide"
)

# Import modules
from db.queries import (
    get_grid_with_neighbor_density,
    get_pois_by_type,
    get_all_pois,
    get_ncr_boundary,
    get_grid_in_polygon
)
from utils.scoring import calculate_score, normalize_scores, generate_recommendation_reason
from utils.geo import geometry_to_polygon_layer_data
from utils.advanced_scoring import calculate_advanced_score, calculate_competitor_density, generate_score_explanation
from utils.catchment import create_catchment_circle, get_catchment_layers_data, calculate_catchment_metrics
from utils.scenario_analysis import analyze_location, format_analysis_html
from config import POI_TYPES, MAP_CENTER, COLORS


def get_color_for_score(score, max_score, poi_type):
    """Get RGBA color based on score."""
    if max_score == 0:
        intensity = 0
    else:
        intensity = min(1, max(0, score / max_score))
    
    base_colors = {
        "atm": [67, 97, 238],
        "hospital": [239, 71, 111],
        "mall": [76, 201, 240]
    }
    
    base = base_colors.get(poi_type, base_colors["atm"])
    alpha = int(80 + intensity * 175)
    
    return base + [alpha]


def main():
    # Custom CSS
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
        [data-testid="stSidebar"] { background: #16213e; }
        h1, h2, h3 { 
            background: linear-gradient(90deg, #4361ee, #7209b7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .recommendation-card {
            background: rgba(67, 97, 238, 0.1);
            border: 1px solid rgba(67, 97, 238, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📍 Location Finder")
    st.markdown("*Find optimal locations for ATMs, Hospitals, and Malls across Delhi NCR*")
    
    # Sidebar Controls
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # POI Type Selection
        poi_type = st.selectbox(
            "Select POI Type",
            options=list(POI_TYPES.keys()),
            format_func=lambda x: POI_TYPES[x]["label"]
        )
        
        st.divider()
        
        # Number of recommendations
        top_n = st.slider(
            "Top Recommendations",
            min_value=5,
            max_value=50,
            value=10,
            step=5
        )
        
        st.divider()
        
        # Layer toggles
        st.subheader("🗂️ Map Layers")
        show_grid = st.checkbox("Show Grid Cells", value=False)
        show_existing_pois = st.checkbox("Show Existing POIs", value=True)
        show_recommendations = st.checkbox("Highlight Top Recommendations", value=True)
        show_catchment = st.checkbox("Show Catchment Areas", value=True, help="Display service radius around recommendations")
        
        st.divider()
        
        # Advanced Analytics
        st.subheader("🧠 Analytics Mode")
        scoring_mode = st.radio(
            "Scoring Algorithm",
            ["Basic", "Advanced (Multi-Factor)"],
            index=1,
            help="Advanced mode considers competition, activity, and more factors"
        )
        use_advanced = scoring_mode == "Advanced (Multi-Factor)"
        
        if use_advanced:
            st.caption("📊 Factors: POI Density, Commercial Activity, Competition, Accessibility")
        
        st.divider()
        
        # Area selection mode
        st.subheader("✏️ Area Selection")
        enable_drawing = st.checkbox("Enable Polygon Drawing", value=False)
        
        if st.button("🔄 Reset Selection", use_container_width=True):
            if "selected_polygon" in st.session_state:
                del st.session_state["selected_polygon"]
            st.rerun()
    
    # Load data
    with st.spinner("Loading spatial data..."):
        grid_data = get_grid_with_neighbor_density()
        
        if not grid_data:
            st.error("❌ Could not load grid data. Please check database connection.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(grid_data)
        
        # Load existing POIs (always load for competition analysis)
        existing_pois = get_pois_by_type(poi_type)
        all_pois_data = get_all_pois() if use_advanced else []
        
        # Calculate scores based on mode
        if use_advanced and len(existing_pois) > 0:
            # Calculate competitor density
            competitor_counts = calculate_competitor_density(df, existing_pois, radius_km=1.5)
            df = calculate_advanced_score(df, poi_type, competitor_counts)
        else:
            # Basic scoring - now with POI-specific competitor counting
            df = calculate_score(df, poi_type, existing_pois)
            df = normalize_scores(df)
    
    # Check for polygon selection
    selected_polygon = st.session_state.get("selected_polygon")
    
    if selected_polygon:
        # Filter grid to polygon
        filtered_grid = get_grid_in_polygon(json.dumps(selected_polygon))
        if filtered_grid:
            df = pd.DataFrame(filtered_grid)
            if use_advanced and len(existing_pois) > 0:
                competitor_counts = calculate_competitor_density(df, existing_pois, radius_km=1.5)
                df = calculate_advanced_score(df, poi_type, competitor_counts)
            else:
                df = calculate_score(df, poi_type, existing_pois)
                df = normalize_scores(df)
            st.info(f"🔍 Filtered to {len(df)} grid cells in selected area")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ Interactive Map")
        
        if enable_drawing:
            # Folium map with drawing tools
            m = folium.Map(
                location=MAP_CENTER,
                zoom_start=10,
                tiles="CartoDB dark_matter"
            )
            
            # Add draw control
            draw = Draw(
                export=True,
                draw_options={
                    "polyline": False,
                    "rectangle": True,
                    "polygon": True,
                    "circle": False,
                    "marker": False,
                    "circlemarker": False
                }
            )
            draw.add_to(m)
            
            # Add existing POIs as markers
            if show_existing_pois and existing_pois:
                for poi in existing_pois[:100]:  # Limit for performance
                    folium.CircleMarker(
                        location=[poi["lat"], poi["lng"]],
                        radius=4,
                        color=f"rgb{tuple(POI_TYPES[poi_type]['color'])}",
                        fill=True,
                        popup=poi.get("name", "Unnamed")
                    ).add_to(m)
            
            # Render map
            output = st_folium(m, width=None, height=500, key="draw_map")
            
            # Capture drawn polygon
            if output and output.get("last_active_drawing"):
                geometry = output["last_active_drawing"].get("geometry")
                if geometry:
                    st.session_state["selected_polygon"] = geometry
                    st.success("✅ Area selected! Click 'Reset Selection' to clear.")
        
        else:
            # PyDeck map for better performance - ENHANCED VERSION
            max_score = df["score"].max() if len(df) > 0 else 1
            min_score = df["score"].min() if len(df) > 0 else 0
            
            # Color legend
            st.markdown(f"""
            <div style="display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 20px; height: 20px; background: linear-gradient(135deg, #ff4757, #ff6b81); border-radius: 4px;"></div>
                    <span style="color: #fff; font-size: 0.85rem;">🔥 Hot Zone (High Score)</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 20px; height: 20px; background: linear-gradient(135deg, #ffa502, #ff7f50); border-radius: 4px;"></div>
                    <span style="color: #fff; font-size: 0.85rem;">⚡ Medium Score</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 20px; height: 20px; background: linear-gradient(135deg, #3742fa, #5352ed); border-radius: 4px;"></div>
                    <span style="color: #fff; font-size: 0.85rem;">❄️ Low Score</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 20px; height: 20px; background: #00f5d4; border-radius: 50%;"></div>
                    <span style="color: #fff; font-size: 0.85rem;">⭐ Top Recommendations</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced color function with gradient
            def get_vibrant_color(score, max_s, min_s):
                if max_s == min_s:
                    normalized = 0.5
                else:
                    normalized = (score - min_s) / (max_s - min_s)
                
                # Vibrant gradient: Blue -> Orange -> Red
                if normalized < 0.33:
                    # Blue to cyan
                    r = int(55 + normalized * 3 * 100)
                    g = int(66 + normalized * 3 * 150)
                    b = int(250 - normalized * 3 * 50)
                elif normalized < 0.66:
                    # Cyan to orange
                    t = (normalized - 0.33) * 3
                    r = int(155 + t * 100)
                    g = int(216 - t * 80)
                    b = int(200 - t * 150)
                else:
                    # Orange to red
                    t = (normalized - 0.66) * 3
                    r = int(255)
                    g = int(136 - t * 80)
                    b = int(50 + t * 30)
                
                alpha = int(160 + normalized * 95)  # 160-255 alpha
                return [r, g, b, alpha]
            
            # Prepare grid layer data with enhanced properties
            grid_layer_data = []
            for _, row in df.iterrows():
                if row.get("geometry"):
                    coords = row["geometry"].get("coordinates", [[]])[0]
                    if coords:
                        color = get_vibrant_color(row["score"], max_score, min_score)
                        # Height based on score for 3D effect
                        height = max(50, (row["normalized_score"] / 100) * 500)
                        grid_layer_data.append({
                            "polygon": coords,
                            "score": round(row["score"], 1),
                            "poi_density": round(row["poi_density"], 1),
                            "neighbor_density": round(row["neighbor_poi_density"], 1),
                            "poi_count": int(row.get("poi_count", 0)),
                            "grid_id": int(row["grid_id"]),
                            "fill_color": color,
                            "elevation": height
                        })
            
            layers = []
            
            # Grid layer with 3D extrusion
            if show_grid and grid_layer_data:
                grid_layer = pdk.Layer(
                    "PolygonLayer",
                    data=grid_layer_data,
                    get_polygon="polygon",
                    get_fill_color="fill_color",
                    get_line_color=[255, 255, 255, 100],
                    line_width_min_pixels=1,
                    extruded=True,  # 3D effect
                    get_elevation="elevation",
                    elevation_scale=1,
                    pickable=True,
                    auto_highlight=True,
                    highlight_color=[255, 255, 0, 150]
                )
                layers.append(grid_layer)
            
            # Existing POIs layer with glow effect
            if show_existing_pois and existing_pois:
                poi_color = POI_TYPES[poi_type]["color"]
                poi_data = [
                    {
                        "position": [p["lng"], p["lat"]], 
                        "name": p.get("name", "Unnamed"),
                        "type": poi_type.upper()
                    }
                    for p in existing_pois if p.get("lat") and p.get("lng")
                ]
                
                # Outer glow
                poi_glow = pdk.Layer(
                    "ScatterplotLayer",
                    data=poi_data,
                    get_position="position",
                    get_radius=200,
                    get_fill_color=poi_color + [60],
                    pickable=False
                )
                layers.append(poi_glow)
                
                # Inner point
                poi_layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=poi_data,
                    get_position="position",
                    get_radius=80,
                    get_fill_color=poi_color + [255],
                    pickable=True
                )
                layers.append(poi_layer)
            
            # Catchment areas (service radius circles)
            if show_catchment and show_recommendations:
                top_recs_for_catchment = df.head(top_n).to_dict('records')
                catchment_data = get_catchment_layers_data(top_recs_for_catchment, radii=[0.5, 1.0])
                
                if catchment_data:
                    catchment_layer = pdk.Layer(
                        "PolygonLayer",
                        data=catchment_data,
                        get_polygon="polygon",
                        get_fill_color="fill_color",
                        get_line_color=[0, 245, 212, 100],
                        line_width_min_pixels=1,
                        pickable=False,
                        stroked=True
                    )
                    layers.append(catchment_layer)
            
            # Top recommendations with pulsing effect (larger, more visible)
            if show_recommendations:
                top_recs = df.head(top_n)
                rec_data = [
                    {
                        "position": [row["centroid_lng"], row["centroid_lat"]],
                        "grid_id": int(row["grid_id"]),
                        "score": round(row["score"], 1),
                        "poi_density": round(row["poi_density"], 1),
                        "neighbor_density": round(row["neighbor_poi_density"], 1),
                        "poi_count": int(row.get("poi_count", 0)),
                        "rank": i + 1
                    }
                    for i, (_, row) in enumerate(top_recs.iterrows())
                    if row.get("centroid_lat") and row.get("centroid_lng")
                ]
                
                # Outer glow for recommendations
                rec_glow = pdk.Layer(
                    "ScatterplotLayer",
                    data=rec_data,
                    get_position="position",
                    get_radius=600,
                    get_fill_color=[0, 245, 212, 40],
                    pickable=False
                )
                layers.append(rec_glow)
                
                # Inner marker for recommendations
                rec_layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=rec_data,
                    get_position="position",
                    get_radius=250,
                    get_fill_color=[0, 245, 212, 220],
                    pickable=True,
                    stroked=True,
                    get_line_color=[255, 255, 255, 255],
                    line_width_min_pixels=3
                )
                layers.append(rec_layer)
            
            # Render map with tilt for 3D view
            view_state = pdk.ViewState(
                latitude=MAP_CENTER[0],
                longitude=MAP_CENTER[1],
                zoom=9.5,
                pitch=45,  # Tilted for 3D effect
                bearing=0
            )
            
            deck = pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                map_style="mapbox://styles/mapbox/dark-v11",
                tooltip={
                    "html": """
                        <div style="font-family: Arial; padding: 8px;">
                            <div style="font-size: 16px; font-weight: bold; color: #00f5d4; margin-bottom: 8px;">
                                📍 Grid #{grid_id}
                            </div>
                            <div style="display: grid; grid-template-columns: auto auto; gap: 4px 12px;">
                                <span style="color: #888;">🎯 Score:</span>
                                <span style="color: #fff; font-weight: bold;">{score}</span>
                                <span style="color: #888;">📊 POI Density:</span>
                                <span style="color: #fff;">{poi_density}</span>
                                <span style="color: #888;">🏘️ Neighbor Avg:</span>
                                <span style="color: #fff;">{neighbor_density}</span>
                                <span style="color: #888;">📍 POI Count:</span>
                                <span style="color: #fff;">{poi_count}</span>
                            </div>
                        </div>
                    """,
                    "style": {
                        "backgroundColor": "rgba(26, 26, 46, 0.95)",
                        "color": "white",
                        "borderRadius": "8px",
                        "border": "1px solid rgba(0, 245, 212, 0.3)"
                    }
                }
            )
            
            st.pydeck_chart(deck, use_container_width=True)
    
    with col2:
        st.subheader(f"🏆 Top {top_n} Recommendations")
        
        # Show scoring mode indicator
        if use_advanced:
            st.caption("🧠 Advanced Multi-Factor Scoring Active")
        
        top_recommendations = df.head(top_n)
        
        for i, (_, row) in enumerate(top_recommendations.iterrows(), 1):
            score_pct = row["normalized_score"]
            
            # Get score explanation for advanced mode
            if use_advanced:
                explanation = generate_score_explanation(row, poi_type)
                demand_text = explanation.get("demand", "")
                competition_text = explanation.get("competition", "")
                
                st.markdown(f"""
                <div class="recommendation-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.2rem; font-weight: bold;">#{i} Grid {int(row['grid_id'])}</span>
                        <span style="background: linear-gradient(90deg, #4361ee, #7209b7); padding: 4px 12px; border-radius: 20px; font-size: 0.9rem;">
                            Score: {row['score']:.1f}
                        </span>
                    </div>
                    <div style="margin-top: 0.5rem; color: #aaa; font-size: 0.85rem;">
                        {demand_text}<br/>
                        {competition_text}
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem;">
                        <div style="font-size: 0.8rem; color: #888;">📊 Density: {row['poi_density']:.1f}</div>
                        <div style="font-size: 0.8rem; color: #888;">🏢 Competition: {row.get('competitor_penalty', 0):.0f}%</div>
                    </div>
                    <div style="margin-top: 0.5rem; height: 6px; background: #2a2a4e; border-radius: 3px; overflow: hidden;">
                        <div style="width: {score_pct}%; height: 100%; background: linear-gradient(90deg, #4361ee, #00f5d4);"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="recommendation-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.2rem; font-weight: bold;">#{i} Grid {int(row['grid_id'])}</span>
                        <span style="background: linear-gradient(90deg, #4361ee, #7209b7); padding: 4px 12px; border-radius: 20px; font-size: 0.9rem;">
                            Score: {row['score']:.1f}
                        </span>
                    </div>
                    <div style="margin-top: 0.5rem; color: #aaa; font-size: 0.9rem;">
                        📊 POI Density: {row['poi_density']:.1f}<br/>
                        🏘️ Neighbor Density: {row['neighbor_poi_density']:.1f}
                    </div>
                    <div style="margin-top: 0.5rem; height: 6px; background: #2a2a4e; border-radius: 3px; overflow: hidden;">
                        <div style="width: {score_pct}%; height: 100%; background: linear-gradient(90deg, #4361ee, #00f5d4);"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Export options
        st.subheader("📥 Export Results")
        
        export_df = top_recommendations[["grid_id", "poi_density", "neighbor_poi_density", "score", "centroid_lat", "centroid_lng"]].copy()
        export_df.columns = ["Grid ID", "POI Density", "Neighbor Density", "Score", "Latitude", "Longitude"]
        
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"locatencr_{poi_type}_recommendations.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Summary statistics
    st.divider()
    st.subheader("📊 Analysis Summary")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Grid Cells", len(df))
    c2.metric("Avg POI Density", f"{df['poi_density'].mean():.1f}")
    c3.metric("Top Score", f"{df['score'].max():.1f}")
    c4.metric(f"Existing {POI_TYPES[poi_type]['label'].split()[1]}s", len(existing_pois))


if __name__ == "__main__":
    main()
