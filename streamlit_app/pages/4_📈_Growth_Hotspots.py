"""
Page 4: Growth Hotspots
Predict emerging high-potential areas
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Growth Hotspots - LocateNCR",
    page_icon="📈",
    layout="wide"
)

# Import modules
from db.queries import get_grid_with_neighbor_density, get_database_stats
from utils.advanced_scoring import calculate_advanced_score, ADVANCED_WEIGHTS
from config import POI_TYPES, MAP_CENTER


def identify_growth_hotspots(df, threshold_percentile=75):
    """
    Identify emerging high-potential areas based on:
    1. High POI density (activity)
    2. Low neighbor density (room to grow)
    3. Balanced accessibility
    """
    df = df.copy()
    
    # Calculate growth potential score
    # High density but low neighbor density = emerging area
    poi_max = df["poi_density"].max()
    neighbor_max = df["neighbor_poi_density"].max()
    
    if poi_max > 0 and neighbor_max > 0:
        df["density_normalized"] = df["poi_density"] / poi_max * 100
        df["neighbor_normalized"] = df["neighbor_poi_density"] / neighbor_max * 100
        
        # Growth potential = high own density + low neighbor density (room to expand)
        df["growth_potential"] = (
            df["density_normalized"] * 0.6 +
            (100 - df["neighbor_normalized"]) * 0.4
        )
    else:
        df["growth_potential"] = 50
    
    # Classify areas
    threshold = df["growth_potential"].quantile(threshold_percentile / 100)
    df["is_hotspot"] = df["growth_potential"] >= threshold
    
    # Assign growth tiers
    df["growth_tier"] = pd.cut(
        df["growth_potential"],
        bins=[0, 40, 60, 80, 100],
        labels=["Stable", "Growing", "High Growth", "Emerging Hotspot"]
    )
    
    return df.sort_values("growth_potential", ascending=False)


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
        .hotspot-card {
            background: rgba(255, 107, 107, 0.1);
            border: 1px solid rgba(255, 107, 107, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .tier-emerging { border-left: 4px solid #ff4757; }
        .tier-high { border-left: 4px solid #ffa502; }
        .tier-growing { border-left: 4px solid #2ed573; }
        .tier-stable { border-left: 4px solid #3742fa; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📈 Growth Hotspots")
    st.markdown("*Identify emerging high-potential areas for future investment*")
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Configuration")
        
        # Threshold slider
        threshold = st.slider(
            "Hotspot Threshold (percentile)",
            min_value=50,
            max_value=95,
            value=75,
            step=5,
            help="Areas above this percentile are marked as hotspots"
        )
        
        st.divider()
        
        # Map style
        show_all_grids = st.checkbox("Show All Grid Cells", value=False)
        show_hotspots_only = st.checkbox("Highlight Hotspots Only", value=True)
        
        st.divider()
        
        st.subheader("📊 About Growth Analysis")
        st.markdown("""
        Growth potential is calculated by:
        - **High POI density** = Active area
        - **Low neighbor density** = Room to expand
        - **Balanced mix** = Emerging opportunity
        """)
    
    # Load data
    with st.spinner("Analyzing growth patterns..."):
        grid_data = get_grid_with_neighbor_density()
        
        if not grid_data:
            st.error("❌ Could not load grid data.")
            return
        
        df = pd.DataFrame(grid_data)
        df = identify_growth_hotspots(df, threshold)
        
        hotspots = df[df["is_hotspot"]]
        stats = get_database_stats()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Grid Cells", len(df))
    col2.metric("🔥 Hotspots Identified", len(hotspots))
    col3.metric("Avg Growth Potential", f"{df['growth_potential'].mean():.1f}")
    col4.metric("Max Growth Potential", f"{df['growth_potential'].max():.1f}")
    
    st.divider()
    
    # Main content
    col_map, col_list = st.columns([2, 1])
    
    with col_map:
        st.subheader("🗺️ Growth Hotspots Map")
        
        # Prepare map data
        map_data = []
        
        if show_all_grids:
            for _, row in df.iterrows():
                if row.get("geometry"):
                    coords = row["geometry"].get("coordinates", [[]])[0]
                    if coords:
                        # Color based on growth tier
                        if row["growth_tier"] == "Emerging Hotspot":
                            color = [255, 71, 87, 200]
                        elif row["growth_tier"] == "High Growth":
                            color = [255, 165, 2, 180]
                        elif row["growth_tier"] == "Growing":
                            color = [46, 213, 115, 150]
                        else:
                            color = [55, 66, 250, 100]
                        
                        map_data.append({
                            "polygon": coords,
                            "grid_id": int(row["grid_id"]),
                            "growth_potential": round(row["growth_potential"], 1),
                            "tier": str(row["growth_tier"]),
                            "fill_color": color
                        })
        
        # Hotspot markers
        hotspot_data = [
            {
                "position": [row["centroid_lng"], row["centroid_lat"]],
                "grid_id": int(row["grid_id"]),
                "growth_potential": round(row["growth_potential"], 1),
                "poi_density": round(row["poi_density"], 1)
            }
            for _, row in hotspots.iterrows()
            if row.get("centroid_lat") and row.get("centroid_lng")
        ]
        
        layers = []
        
        # Grid layer
        if show_all_grids and map_data:
            grid_layer = pdk.Layer(
                "PolygonLayer",
                data=map_data,
                get_polygon="polygon",
                get_fill_color="fill_color",
                get_line_color=[255, 255, 255, 50],
                line_width_min_pixels=1,
                pickable=True,
                auto_highlight=True
            )
            layers.append(grid_layer)
        
        # Hotspot markers
        if show_hotspots_only and hotspot_data:
            # Outer glow
            glow_layer = pdk.Layer(
                "ScatterplotLayer",
                data=hotspot_data,
                get_position="position",
                get_radius=800,
                get_fill_color=[255, 71, 87, 50],
                pickable=False
            )
            layers.append(glow_layer)
            
            # Inner marker
            marker_layer = pdk.Layer(
                "ScatterplotLayer",
                data=hotspot_data,
                get_position="position",
                get_radius=300,
                get_fill_color=[255, 71, 87, 220],
                pickable=True,
                stroked=True,
                get_line_color=[255, 255, 255, 255],
                line_width_min_pixels=2
            )
            layers.append(marker_layer)
        
        view_state = pdk.ViewState(
            latitude=MAP_CENTER[0],
            longitude=MAP_CENTER[1],
            zoom=10,
            pitch=40
        )
        
        deck = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/dark-v11",
            tooltip={
                "html": """
                    <div style="font-family: Arial; padding: 8px;">
                        <div style="font-size: 14px; font-weight: bold; color: #ff4757;">
                            🔥 Grid #{grid_id}
                        </div>
                        <div style="margin-top: 8px;">
                            <span style="color: #888;">Growth Potential:</span>
                            <span style="color: #fff; font-weight: bold;"> {growth_potential}%</span>
                        </div>
                    </div>
                """,
                "style": {"backgroundColor": "rgba(26, 26, 46, 0.95)", "color": "white", "borderRadius": "8px"}
            }
        )
        
        st.pydeck_chart(deck, use_container_width=True)
        
        # Legend
        st.markdown("""
        <div style="display: flex; gap: 1.5rem; margin-top: 1rem; justify-content: center;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 16px; height: 16px; background: #ff4757; border-radius: 50%;"></div>
                <span style="color: #aaa; font-size: 0.85rem;">Emerging Hotspot</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 16px; height: 16px; background: #ffa502; border-radius: 50%;"></div>
                <span style="color: #aaa; font-size: 0.85rem;">High Growth</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 16px; height: 16px; background: #2ed573; border-radius: 50%;"></div>
                <span style="color: #aaa; font-size: 0.85rem;">Growing</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 16px; height: 16px; background: #3742fa; border-radius: 50%;"></div>
                <span style="color: #aaa; font-size: 0.85rem;">Stable</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_list:
        st.subheader("🔥 Top Growth Areas")
        
        for i, (_, row) in enumerate(hotspots.head(10).iterrows(), 1):
            tier_class = {
                "Emerging Hotspot": "tier-emerging",
                "High Growth": "tier-high",
                "Growing": "tier-growing",
                "Stable": "tier-stable"
            }.get(str(row["growth_tier"]), "")
            
            st.markdown(f"""
            <div class="hotspot-card {tier_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.1rem; font-weight: bold;">#{i} Grid {int(row['grid_id'])}</span>
                    <span style="background: linear-gradient(90deg, #ff4757, #ff6b81); padding: 4px 10px; border-radius: 12px; font-size: 0.85rem;">
                        {row['growth_potential']:.0f}%
                    </span>
                </div>
                <div style="margin-top: 0.5rem; color: #aaa; font-size: 0.85rem;">
                    📊 POI Density: {row['poi_density']:.1f} | 
                    🏘️ Neighbor: {row['neighbor_poi_density']:.1f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Export
        st.subheader("📥 Export Hotspots")
        export_df = hotspots[["grid_id", "poi_density", "neighbor_poi_density", "growth_potential", "centroid_lat", "centroid_lng"]].copy()
        export_df.columns = ["Grid ID", "POI Density", "Neighbor Density", "Growth %", "Latitude", "Longitude"]
        
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Hotspots CSV",
            data=csv,
            file_name="locatencr_growth_hotspots.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Distribution chart
    st.divider()
    st.subheader("📊 Growth Potential Distribution")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Histogram
        fig = px.histogram(
            df,
            x="growth_potential",
            nbins=30,
            color_discrete_sequence=["#4361ee"],
            title="Distribution of Growth Potential Scores"
        )
        fig.add_vline(x=df["growth_potential"].quantile(threshold/100), 
                      line_dash="dash", line_color="#ff4757",
                      annotation_text=f"Hotspot Threshold ({threshold}th percentile)")
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        # Tier breakdown
        tier_counts = df["growth_tier"].value_counts().reset_index()
        tier_counts.columns = ["Tier", "Count"]
        
        fig = px.pie(
            tier_counts,
            values="Count",
            names="Tier",
            title="Grid Cells by Growth Tier",
            color="Tier",
            color_discrete_map={
                "Emerging Hotspot": "#ff4757",
                "High Growth": "#ffa502",
                "Growing": "#2ed573",
                "Stable": "#3742fa"
            }
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
