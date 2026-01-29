"""
Page 2: How It Works
Project explainer with visualizations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="How It Works - LocateNCR",
    page_icon="📊",
    layout="wide"
)

# Import modules
from db.queries import get_database_stats, get_grid_with_neighbor_density
from utils.scoring import calculate_score, normalize_scores
from utils.visualization import (
    create_density_histogram,
    create_stats_cards,
    create_density_vs_neighbor_scatter
)
from config import SCORING_WEIGHTS


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
        .section-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(67, 97, 238, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        .formula-box {
            background: rgba(0, 0, 0, 0.3);
            border-left: 4px solid #4361ee;
            padding: 1rem;
            font-family: monospace;
            font-size: 1.1rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 How It Works")
    st.markdown("*Understanding the methodology behind LocateNCR's recommendations*")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("📑 Sections")
        section = st.radio(
            "Jump to:",
            ["Overview", "Architecture", "Spatial Grid", "Data Pipeline", "Scoring Algorithm", "Advanced Analytics", "Data Verification", "Live Statistics"],
            label_visibility="collapsed"
        )
    
    # Load data for visualizations
    stats = get_database_stats()
    
    # Section: Overview
    if section == "Overview":
        st.header("🎯 Project Overview")
        
        st.markdown("""
        <div class="section-card">
            <h3>What is LocateNCR?</h3>
            <p style="color: #ccc; font-size: 1.1rem; line-height: 1.8;">
                LocateNCR is a <b>spatial analytics platform</b> that helps businesses and urban planners 
                identify optimal locations for Points of Interest (POIs) in the Delhi National Capital Region.
            </p>
            <p style="color: #aaa; line-height: 1.8;">
                Using OpenStreetMap data, PostGIS spatial analysis, and machine learning clustering, 
                we analyze the region through a 1km × 1km grid and calculate recommendation scores 
                based on demand (POI density) and competition (existing facilities).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats cards
        if stats:
            st.markdown(create_stats_cards(stats), unsafe_allow_html=True)
        
        # Supported POI types - using config
        from config import POI_TYPES
        
        st.markdown("""
        <div class="section-card">
            <h3>Supported POI Types</h3>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-top: 1rem;">
        """, unsafe_allow_html=True)
        
        # Color mapping for POI cards
        poi_colors = {
            "atm": "#4361ee", "hospital": "#ef476f", "mall": "#4cc9f0",
            "pharmacy": "#00c853", "school": "#ffc107", "bank": "#9c27b0",
            "police": "#2196f3", "bus_station": "#ff9800", "fuel": "#795548",
            "supermarket": "#009688"
        }
        
        poi_html = ""
        for poi_type, config in POI_TYPES.items():
            color = poi_colors.get(poi_type, "#4361ee")
            label_parts = config["label"].split(" ", 1)
            emoji = label_parts[0]
            name = label_parts[1] if len(label_parts) > 1 else poi_type.title()
            poi_html += f'''
                <div style="text-align: center; padding: 1rem; background: {color}22; border-radius: 12px; border: 1px solid {color}44;">
                    <span style="font-size: 2rem;">{emoji}</span>
                    <div style="font-size: 0.9rem; font-weight: bold; margin-top: 0.5rem;">{name}</div>
                </div>
            '''
        
        st.markdown(poi_html + "</div></div>", unsafe_allow_html=True)
    
    # Section: Architecture
    elif section == "Architecture":
        st.header("🏗️ System Architecture")
        
        st.markdown("""
        <div class="section-card">
            <p style="color: #aaa; margin-bottom: 1rem;">
                LocateNCR follows a multi-layer architecture combining geospatial databases, 
                big data processing, and interactive visualization.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Architecture diagram using columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(67, 97, 238, 0.2); border-radius: 12px; height: 200px;">
                <span style="font-size: 2.5rem;">🗺️</span>
                <div style="font-weight: bold; margin: 0.5rem 0;">Data Source</div>
                <div style="color: #888; font-size: 0.85rem;">
                    OpenStreetMap<br/>
                    PBF Extract<br/>
                    Delhi NCR Region
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(114, 9, 183, 0.2); border-radius: 12px; height: 200px;">
                <span style="font-size: 2.5rem;">🐘</span>
                <div style="font-weight: bold; margin: 0.5rem 0;">PostGIS</div>
                <div style="color: #888; font-size: 0.85rem;">
                    Spatial Database<br/>
                    Grid Generation<br/>
                    POI Extraction
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(239, 71, 111, 0.2); border-radius: 12px; height: 200px;">
                <span style="font-size: 2.5rem;">⚡</span>
                <div style="font-weight: bold; margin: 0.5rem 0;">Apache Spark</div>
                <div style="color: #888; font-size: 0.85rem;">
                    Feature Engineering<br/>
                    KMeans Clustering<br/>
                    Scoring Pipeline
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: rgba(0, 245, 212, 0.2); border-radius: 12px; height: 200px;">
                <span style="font-size: 2.5rem;">🎯</span>
                <div style="font-weight: bold; margin: 0.5rem 0;">Streamlit</div>
                <div style="color: #888; font-size: 0.85rem;">
                    Interactive Map<br/>
                    Recommendations<br/>
                    Export Tools
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Technology stack
        st.subheader("🛠️ Technology Stack")
        
        tech_data = [
            {"Layer": "Database", "Technology": "PostgreSQL 15 + PostGIS", "Purpose": "Spatial data storage & queries"},
            {"Layer": "ETL", "Technology": "osm2pgsql", "Purpose": "OpenStreetMap data ingestion"},
            {"Layer": "Analytics", "Technology": "Apache Spark + PySpark", "Purpose": "Distributed processing & ML"},
            {"Layer": "Frontend", "Technology": "Streamlit + PyDeck", "Purpose": "Interactive visualization"},
            {"Layer": "Mapping", "Technology": "Folium + Mapbox", "Purpose": "Map rendering & drawing"}
        ]
        
        st.dataframe(pd.DataFrame(tech_data), use_container_width=True, hide_index=True)
    
    # Section: Data Pipeline
    elif section == "Data Pipeline":
        st.header("🔄 Data Pipeline")
        
        steps = [
            ("1️⃣", "OSM Data Ingestion", "Download Delhi NCR extract from OpenStreetMap as PBF file"),
            ("2️⃣", "PostGIS Loading", "Use osm2pgsql to load data into PostGIS with hstore support"),
            ("3️⃣", "Boundary Creation", "Extract administrative boundaries for Delhi + NCR cities"),
            ("4️⃣", "POI Extraction", "Filter points by amenity/shop tags (ATM, hospital, mall, etc.)"),
            ("5️⃣", "Grid Generation", "Create 1km × 1km square grid using ST_SquareGrid"),
            ("6️⃣", "Feature Engineering", "Calculate POI count, density, area for each grid cell"),
            ("7️⃣", "Neighbor Analysis", "Compute average POI density of neighboring cells"),
            ("8️⃣", "Scoring", "Apply weighted formula to rank cells by recommendation score")
        ]
        
        for emoji, title, desc in steps:
            st.markdown(f"""
            <div style="display: flex; gap: 1rem; margin: 1rem 0; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 12px;">
                <span style="font-size: 2rem;">{emoji}</span>
                <div>
                    <div style="font-weight: bold; font-size: 1.1rem;">{title}</div>
                    <div style="color: #888;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Grid explanation
        st.subheader("🔲 Understanding the Grid")
        
        st.markdown("""
        <div class="section-card">
            <p style="color: #ccc;">
                The NCR region is divided into <b>1km × 1km grid cells</b>. Each cell is analyzed independently 
                with the following metrics.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # NEW Section: Spatial Grid
    elif section == "Spatial Grid":
        st.header("🔲 Understanding the Spatial Grid")
        
        st.markdown("""
        <div class="section-card">
            <p style="color: #ccc; font-size: 1.1rem; line-height: 1.8;">
                The heart of LocateNCR's analysis is a <b>spatial grid system</b> that divides the entire 
                Delhi NCR region into uniform square cells for systematic evaluation.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # What is the Grid?
        st.subheader("📐 What is the Grid?")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="section-card">
                <h4 style="color: #00f5d4;">Grid Specifications</h4>
                <table style="width: 100%; color: #ccc; margin-top: 1rem;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;">📏 <b>Cell Size</b></td>
                        <td style="text-align: right;">1 km × 1 km</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;">📐 <b>Cell Area</b></td>
                        <td style="text-align: right;">~1 sq km each</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;">🗺️ <b>Projection</b></td>
                        <td style="text-align: right;">WGS 84 (EPSG:4326)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;">🔧 <b>Generation</b></td>
                        <td style="text-align: right;">PostGIS ST_SquareGrid</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;">🌐 <b>Coverage</b></td>
                        <td style="text-align: right;">Entire NCR Boundary</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="section-card">
                <h4 style="color: #00f5d4;">Why 1km Grid?</h4>
                <ul style="color: #aaa; line-height: 2; margin-top: 1rem;">
                    <li>🚶 <b>Walking Distance:</b> 1km ≈ 12-15 min walk</li>
                    <li>🎯 <b>Local Context:</b> Captures neighborhood-level demand</li>
                    <li>⚡ <b>Performance:</b> Balances detail vs computation</li>
                    <li>📊 <b>Density Calculation:</b> Easy per-sq-km metrics</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Grid Cell Metrics
        st.subheader("📊 Grid Cell Metrics")
        
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1rem 0;">
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(67, 97, 238, 0.3), rgba(67, 97, 238, 0.1)); border-radius: 16px; border: 1px solid rgba(67, 97, 238, 0.4);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📍</div>
                <div style="font-weight: bold; font-size: 1.1rem;">POI Count</div>
                <div style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">Total POIs inside the cell</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(239, 71, 111, 0.3), rgba(239, 71, 111, 0.1)); border-radius: 16px; border: 1px solid rgba(239, 71, 111, 0.4);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📐</div>
                <div style="font-weight: bold; font-size: 1.1rem;">Area (sq km)</div>
                <div style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">Actual cell area</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(0, 245, 212, 0.3), rgba(0, 245, 212, 0.1)); border-radius: 16px; border: 1px solid rgba(0, 245, 212, 0.4);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📈</div>
                <div style="font-weight: bold; font-size: 1.1rem;">POI Density</div>
                <div style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">POIs per sq km</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(114, 9, 183, 0.3), rgba(114, 9, 183, 0.1)); border-radius: 16px; border: 1px solid rgba(114, 9, 183, 0.4);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏘️</div>
                <div style="font-weight: bold; font-size: 1.1rem;">Neighbor Density</div>
                <div style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">Avg density of nearby cells</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample Calculation
        st.subheader("🧮 Sample Calculation")
        
        st.markdown("""
        <div class="section-card">
            <h4 style="color: #00f5d4;">Example: Grid Cell #1234</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1rem;">
                <div>
                    <p style="color: #ccc;"><b>Step 1: Count POIs</b></p>
                    <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; font-family: monospace; color: #aaa;">
                        POIs found in cell: <span style="color: #00f5d4;">47</span>
                    </div>
                </div>
                <div>
                    <p style="color: #ccc;"><b>Step 2: Calculate Area</b></p>
                    <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; font-family: monospace; color: #aaa;">
                        Area: <span style="color: #00f5d4;">0.98 sq km</span>
                    </div>
                </div>
                <div>
                    <p style="color: #ccc;"><b>Step 3: POI Density</b></p>
                    <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; font-family: monospace; color: #aaa;">
                        47 ÷ 0.98 = <span style="color: #00f5d4;">47.96 POIs/sq km</span>
                    </div>
                </div>
                <div>
                    <p style="color: #ccc;"><b>Step 4: Neighbor Avg</b></p>
                    <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; font-family: monospace; color: #aaa;">
                        Nearby 8 cells avg: <span style="color: #00f5d4;">32.1 POIs/sq km</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Visual Grid Representation
        st.subheader("🖼️ Grid Visualization")
        
        st.markdown("""
        <div class="section-card">
            <p style="color: #ccc; margin-bottom: 1rem;">How the grid overlays Delhi NCR:</p>
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; max-width: 400px;">
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.2); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; color: #888;">Low</div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.3); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(255, 165, 2, 0.4); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(255, 71, 87, 0.7); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; color: #fff;">🔥</div>
                <div style="aspect-ratio: 1; background: rgba(255, 165, 2, 0.5); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.3); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.2); border-radius: 4px;"></div>
                
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.3); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(255, 165, 2, 0.4); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(255, 71, 87, 0.6); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(255, 71, 87, 0.8); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; color: #fff;">⭐</div>
                <div style="aspect-ratio: 1; background: rgba(255, 71, 87, 0.6); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(255, 165, 2, 0.4); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.3); border-radius: 4px;"></div>
                
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.2); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.3); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(255, 165, 2, 0.5); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(255, 71, 87, 0.6); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(255, 165, 2, 0.4); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.3); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.2); border-radius: 4px;"></div>
                
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.1); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.2); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.3); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(255, 165, 2, 0.3); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.3); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.2); border-radius: 4px;"></div>
                <div style="aspect-ratio: 1; background: rgba(67, 97, 238, 0.1); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; color: #888;">Low</div>
            </div>
            <div style="display: flex; gap: 2rem; margin-top: 1rem; color: #888; font-size: 0.85rem;">
                <span>❄️ Blue = Low density</span>
                <span>🟠 Orange = Medium</span>
                <span>🔥 Red = High density</span>
                <span>⭐ = Top recommendation</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Live Grid Stats
        st.subheader("📈 Current Grid Statistics")
        
        if stats:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Grid Cells", f"{stats.get('total_grids', 0):,}")
            col2.metric("Avg POI Density", f"{stats.get('avg_density', 0):.1f} per sq km")
            col3.metric("Max POI Density", f"{stats.get('max_density', 0):.1f} per sq km")
    
    # Section: Scoring Algorithm
    elif section == "Scoring Algorithm":
        st.header("🧮 Scoring Algorithm")
        
        st.markdown("""
        <div class="section-card">
            <p style="color: #ccc; font-size: 1.1rem;">
                The recommendation score balances <b>demand</b> (high POI density = more activity) 
                against <b>POI-specific competition</b> (existing facilities of the SAME type nearby).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key Innovation
        st.subheader("🎯 Key Innovation: POI-Specific Scoring")
        
        st.markdown("""
        <div class="section-card" style="border-left: 4px solid #00f5d4;">
            <h4 style="color: #00f5d4;">Why Different POI Types Have Different Results</h4>
            <p style="color: #aaa; margin-top: 0.5rem;">
                When you select <b>ATM</b>, we count nearby <b>ATMs only</b>.<br/>
                When you select <b>Hospital</b>, we count nearby <b>Hospitals only</b>.<br/>
                This ensures each POI type gets <b>unique recommendations</b> based on its actual competition landscape.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📐 Formula")
        
        st.markdown("""
        <div class="formula-box">
            <b>Score</b> = (POI_Density × <span style="color: #4361ee;">Demand_Weight</span>) 
            − (Competitor_Count × <span style="color: #ef476f;">Penalty_Weight</span> × 5)
        </div>
        
        <div style="margin-top: 1rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div style="background: rgba(67, 97, 238, 0.1); padding: 1rem; border-radius: 8px;">
                <div style="font-weight: bold; color: #4361ee;">📈 POI Density</div>
                <div style="color: #aaa; font-size: 0.9rem;">Total POIs per sq km in the cell<br/>Higher = More demand/footfall</div>
            </div>
            <div style="background: rgba(239, 71, 111, 0.1); padding: 1rem; border-radius: 8px;">
                <div style="font-weight: bold; color: #ef476f;">🏢 Competitor Count</div>
                <div style="color: #aaa; font-size: 0.9rem;">Same-type POIs within 2km radius<br/>Higher = More saturation = Penalty</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Technical Implementation
        st.subheader("⚙️ Technical Implementation")
        
        st.markdown("""
        <div class="section-card">
            <h4 style="color: #00f5d4;">Distance Calculation</h4>
            <p style="color: #aaa;">
                Competition is calculated using the <b>Haversine formula</b> to find 
                great-circle distance between grid cell centroids and existing POIs.
            </p>
            <div class="formula-box" style="margin-top: 1rem;">
                <code>distance = 6371 × 2 × arcsin(√(sin²(Δlat/2) + cos(lat₁)×cos(lat₂)×sin²(Δlon/2)))</code>
            </div>
            <p style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">
                Where 6371 km is Earth's radius. Distance ≤ 2km = competitor counted.
            </p>
        </div>
        
        <div class="section-card">
            <h4 style="color: #00f5d4;">Coordinate Transformation</h4>
            <p style="color: #aaa;">
                POI coordinates are stored in <b>Web Mercator (EPSG:3857)</b> projection.
                They are transformed to <b>WGS84 (EPSG:4326)</b> using PostGIS:
            </p>
            <div class="formula-box" style="margin-top: 0.5rem;">
                <code>ST_Transform(geom, 4326)</code>
            </div>
            <p style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">
                This ensures lat/lon coordinates match between grid cells and POIs.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Weights table
        st.subheader("⚖️ Weight Configuration by POI Type")
        
        weights_data = []
        for poi_type, weights in SCORING_WEIGHTS.items():
            weights_data.append({
                "POI Type": poi_type.upper(),
                "Demand Weight": weights["poi_density_weight"],
                "Competition Penalty": weights["neighbor_penalty"],
                "Strategy": "High traffic" if weights["poi_density_weight"] > 0.6 else "Gap filling"
            })
        
        st.dataframe(pd.DataFrame(weights_data), use_container_width=True, hide_index=True)
        
        st.markdown("""
        <div style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">
            <b>High Penalty</b> (e.g., Mall: 1.8) = Avoid areas with existing competitors<br/>
            <b>Low Penalty</b> (e.g., Hospital: 0.6) = Less sensitive to competition, serve underserved areas
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive calculator
        st.subheader("🔢 Score Calculator")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            test_density = st.number_input("POI Density", value=100.0, min_value=0.0, max_value=500.0)
        with col2:
            test_competitors = st.number_input("Competitors Nearby", value=3, min_value=0, max_value=20)
        with col3:
            test_type = st.selectbox("POI Type", list(SCORING_WEIGHTS.keys()))
        
        weights = SCORING_WEIGHTS[test_type]
        calculated_score = (test_density * weights["poi_density_weight"]) - (test_competitors * weights["neighbor_penalty"] * 5)
        
        st.metric("Calculated Score", f"{calculated_score:.2f}")
        
        if calculated_score > 50:
            st.success("✅ This location has a strong recommendation score!")
        elif calculated_score > 0:
            st.info("ℹ️ This location has moderate potential.")
        else:
            st.warning("⚠️ High competition may make this location challenging.")
    
    # Section: Advanced Analytics
    elif section == "Advanced Analytics":
        st.header("🧠 Advanced Analytics")
        
        st.markdown("""
        <div class="section-card">
            <p style="color: #ccc; font-size: 1.1rem; line-height: 1.8;">
                LocateNCR offers advanced analytics features that go beyond basic scoring to provide 
                <b>industrial-level insights</b> for site selection.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Multi-Factor Scoring
        st.subheader("📊 Multi-Factor Scoring Engine")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="section-card">
                <h4 style="color: #00f5d4;">Basic vs Advanced Scoring</h4>
                <table style="width: 100%; color: #ccc; margin-top: 1rem;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 0;"><b>Basic</b></td>
                        <td>2 factors (POI density, neighbor density)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><b>Advanced</b></td>
                        <td>5+ factors including competition analysis</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="section-card">
                <h4 style="color: #00f5d4;">Advanced Factors</h4>
                <ul style="color: #aaa; line-height: 2; margin-top: 1rem;">
                    <li>📍 <b>POI Density Score</b> - Activity level</li>
                    <li>🏢 <b>Commercial Score</b> - Business activity</li>
                    <li>🏠 <b>Residential Score</b> - Population proxy</li>
                    <li>🚫 <b>Competitor Penalty</b> - Same-type competition</li>
                    <li>🚗 <b>Accessibility Score</b> - Connectivity</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="formula-box">
            <b>Advanced Score</b> = (POI_Density × 0.25) + (Commercial × 0.25) + (Residential × 0.15) 
            + (Accessibility × 0.10) − (<span style="color: #ef476f;">Competitor_Penalty × 0.30</span>)
        </div>
        """, unsafe_allow_html=True)
        
        # Catchment Analysis
        st.subheader("📍 Catchment Area Analysis")
        
        st.markdown("""
        <div class="section-card">
            <p style="color: #ccc;">
                Catchment areas show the <b>service radius</b> of each recommended location, 
                helping you understand population coverage and competitor overlap.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1rem 0;">
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(0, 245, 212, 0.3), rgba(0, 245, 212, 0.1)); border-radius: 16px; border: 1px solid rgba(0, 245, 212, 0.4);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">500m</div>
                <div style="font-weight: bold;">Walking Distance</div>
                <div style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">~6 min walk</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(67, 97, 238, 0.3), rgba(67, 97, 238, 0.1)); border-radius: 16px; border: 1px solid rgba(67, 97, 238, 0.4);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">1km</div>
                <div style="font-weight: bold;">Standard Catchment</div>
                <div style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">~12 min walk</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(114, 9, 183, 0.3), rgba(114, 9, 183, 0.1)); border-radius: 16px; border: 1px solid rgba(114, 9, 183, 0.4);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">2km</div>
                <div style="font-weight: bold;">Extended Reach</div>
                <div style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">~5 min drive</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Competitor Analysis
        st.subheader("🏢 Competitor Density Analysis")
        
        st.markdown("""
        <div class="section-card">
            <p style="color: #ccc; margin-bottom: 1rem;">
                The system calculates <b>competitor density</b> by counting existing POIs of the same type 
                within a 1.5km radius of each grid cell.
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px;">
                    <div style="color: #888; font-size: 0.85rem;">Low Competition</div>
                    <div style="font-size: 1.1rem; color: #00f5d4;">0-2 competitors in 1.5km</div>
                    <div style="color: #00f5d4; font-size: 0.9rem;">✅ Opportunity zone</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        

        
        # Growth Hotspots
        st.subheader("📈 Growth Hotspots Prediction")
        
        st.markdown("""
        <div class="section-card">
            <p style="color: #ccc;">
                The <b>Growth Hotspots</b> feature identifies emerging high-potential areas 
                based on POI density patterns and neighborhood characteristics.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="formula-box">
            <b>Growth Potential</b> = (Own_Density × 0.6) + ((100 - Neighbor_Density) × 0.4)
        </div>
        
        <div style="margin-top: 1rem; color: #aaa;">
            <b>Logic:</b> Areas with high activity but low surrounding development = room to grow
        </div>
        """, unsafe_allow_html=True)
        
        # Growth Tiers
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin: 1rem 0;">
            <div style="text-align: center; padding: 1rem; background: rgba(255, 71, 87, 0.2); border-radius: 8px; border-left: 4px solid #ff4757;">
                <div style="font-weight: bold;">🔥 Emerging</div>
                <div style="color: #888; font-size: 0.8rem;">80-100%</div>
            </div>
            <div style="text-align: center; padding: 1rem; background: rgba(255, 165, 2, 0.2); border-radius: 8px; border-left: 4px solid #ffa502;">
                <div style="font-weight: bold;">📈 High Growth</div>
                <div style="color: #888; font-size: 0.8rem;">60-80%</div>
            </div>
            <div style="text-align: center; padding: 1rem; background: rgba(46, 213, 115, 0.2); border-radius: 8px; border-left: 4px solid #2ed573;">
                <div style="font-weight: bold;">📊 Growing</div>
                <div style="color: #888; font-size: 0.8rem;">40-60%</div>
            </div>
            <div style="text-align: center; padding: 1rem; background: rgba(55, 66, 250, 0.2); border-radius: 8px; border-left: 4px solid #3742fa;">
                <div style="font-weight: bold;">🏠 Stable</div>
                <div style="color: #888; font-size: 0.8rem;">0-40%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Section: Data Verification
    elif section == "Data Verification":
        st.header("🔍 Data Verification & Exploration")
        
        st.markdown("""
        <div class="section-card">
            <p style="color: #ccc; font-size: 1.1rem;">
                Explore the complete data pipeline - from <b>raw OSM files</b> to <b>processed database tables</b>.
                This helps understand how data flows through the system.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Import all needed functions
        from db.queries import (
            get_poi_breakdown, get_poi_sample, get_raw_pois_sample, 
            get_grid_sample, get_boundary_sample, get_table_row_counts, get_column_info
        )
        from config import POI_TYPES
        import os
        
        # Create tabs for different data views
        tab1, tab2, tab3, tab4 = st.tabs(["📁 Raw Files", "🗄️ Database Tables", "📊 POI Breakdown", "⚙️ Schema"])
        
        with tab1:
            st.subheader("📁 Raw Data Files")
            st.markdown("These are the source files used to populate the database:")
            
            # Raw data folder path
            raw_data_path = r"d:\Project_Smart\SmartCity_project\raw_data"
            
            # File descriptions
            file_info = {
                "delhi_boundary.geojson": {"type": "GeoJSON", "desc": "Delhi/NCR boundary polygon", "color": "#4361ee"},
                "delhi_boundary.osm.pbf": {"type": "OSM PBF", "desc": "Raw OSM boundary data", "color": "#7209b7"},
                "delhi_pois.csv": {"type": "CSV", "desc": "Extracted POI data", "color": "#00f5d4"},
                "delhi_pois.geojson": {"type": "GeoJSON", "desc": "POI data with geometry", "color": "#4cc9f0"},
                "delhi_pois.osm.pbf": {"type": "OSM PBF", "desc": "Raw POI from OpenStreetMap", "color": "#ef476f"},
                "delhi_roads.geojson": {"type": "GeoJSON", "desc": "Road network data", "color": "#ffc107"},
                "delhi_roads.osm.pbf": {"type": "OSM PBF", "desc": "Raw road data from OSM", "color": "#ff9800"},
                "NewDelhi.osm.pbf": {"type": "OSM PBF", "desc": "Main OSM extract for Delhi", "color": "#9c27b0"},
            }
            
            # Show file info
            if os.path.exists(raw_data_path):
                files = os.listdir(raw_data_path)
                
                for filename in sorted(files):
                    filepath = os.path.join(raw_data_path, filename)
                    if os.path.isfile(filepath):
                        size_mb = os.path.getsize(filepath) / (1024 * 1024)
                        info = file_info.get(filename, {"type": "Unknown", "desc": "Data file", "color": "#888"})
                        
                        st.markdown(f"""
                        <div style="background: rgba(0,0,0,0.3); padding: 0.75rem 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid {info['color']};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="font-weight: bold; color: {info['color']};">{filename}</span>
                                    <span style="background: {info['color']}22; color: {info['color']}; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin-left: 8px;">{info['type']}</span>
                                </div>
                                <span style="color: #888; font-size: 0.85rem;">{size_mb:.2f} MB</span>
                            </div>
                            <div style="color: #aaa; font-size: 0.85rem; margin-top: 4px;">{info['desc']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning(f"Raw data folder not found at: {raw_data_path}")
            
            st.divider()
            st.markdown("""
            **File Format Explanation:**
            - **OSM PBF**: Binary format from OpenStreetMap - compact and fast
            - **GeoJSON**: JSON with geographic features - human readable
            - **CSV**: Tabular data - easy to view in Excel
            """)
        
        with tab2:
            st.subheader("🗄️ Database Tables")
            
            # Get table row counts
            row_counts = get_table_row_counts()
            if row_counts:
                col1, col2, col3 = st.columns(3)
                for i, rc in enumerate(row_counts):
                    cols = [col1, col2, col3]
                    cols[i].metric(
                        rc['table_name'], 
                        f"{rc['row_count']:,} rows",
                        help=f"Records in {rc['table_name']} table"
                    )
            
            st.divider()
            
            # Sample data tabs
            table_choice = st.selectbox(
                "Select table to view sample data:",
                ["osm_pois_ncr (Raw POIs)", "ncr_grid_features (Processed Grid)", "ncr_boundary (Boundary)"]
            )
            
            if "osm_pois_ncr" in table_choice:
                st.markdown("**Sample from `osm_pois_ncr` table (raw POI data):**")
                raw_pois = get_raw_pois_sample(15)
                if raw_pois:
                    st.dataframe(pd.DataFrame(raw_pois), use_container_width=True, hide_index=True)
                    st.caption("This is the raw POI data extracted from OSM with geometry coordinates")
                    
            elif "ncr_grid_features" in table_choice:
                st.markdown("**Sample from `ncr_grid_features` table (processed grid):**")
                grid_sample = get_grid_sample(15)
                if grid_sample:
                    st.dataframe(pd.DataFrame(grid_sample), use_container_width=True, hide_index=True)
                    st.caption("This is the processed grid with POI counts and density calculations")
                    
            elif "ncr_boundary" in table_choice:
                st.markdown("**Sample from `ncr_boundary` table:**")
                boundary = get_boundary_sample()
                if boundary:
                    st.dataframe(pd.DataFrame(boundary), use_container_width=True, hide_index=True)
                    st.caption("This contains the NCR region boundary polygon")
        
        with tab3:
            st.subheader("📊 POI Breakdown by Amenity Type")
            
            poi_breakdown = get_poi_breakdown()
            if poi_breakdown:
                df_breakdown = pd.DataFrame(poi_breakdown)
                
                # Show as table
                st.dataframe(
                    df_breakdown,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "amenity_type": st.column_config.TextColumn("Amenity Tag"),
                        "shop_type": st.column_config.TextColumn("Shop Tag"),
                        "count": st.column_config.NumberColumn("Count", format="%d")
                    }
                )
                
                total = df_breakdown['count'].sum()
                st.success(f"✅ Total POIs in database: **{total:,}**")
                
                # Filter tester
                st.divider()
                st.subheader("🔎 Test POI Filter")
                
                selected_type = st.selectbox(
                    "Select POI Type to verify:",
                    options=list(POI_TYPES.keys()),
                    format_func=lambda x: POI_TYPES[x]["label"]
                )
                
                sample_pois = get_poi_sample(selected_type, limit=10)
                
                if sample_pois:
                    df_sample = pd.DataFrame(sample_pois)
                    st.dataframe(df_sample, use_container_width=True, hide_index=True)
                    st.info(f"✅ Found {len(sample_pois)} records for **{POI_TYPES[selected_type]['label']}**")
                else:
                    st.warning(f"⚠️ No POIs found for: {POI_TYPES[selected_type]['label']}")
            else:
                st.error("Could not load POI breakdown")
        
        with tab4:
            st.subheader("⚙️ Database Schema")
            
            st.markdown("Column structure of each database table:")
            
            for table in ["osm_pois_ncr", "ncr_grid_features", "ncr_boundary"]:
                with st.expander(f"📋 {table}"):
                    cols = get_column_info(table)
                    if cols:
                        st.dataframe(
                            pd.DataFrame(cols),
                            use_container_width=True,
                            hide_index=True
                        )
            
            st.divider()
            st.subheader("🔧 POI Filter Configuration")
            st.markdown("Current OSM tag mappings in `config.py`:")
            
            for poi_key, poi_config in POI_TYPES.items():
                col1, col2, col3 = st.columns([1, 1, 1])
                col1.markdown(f"**{poi_config['label']}**")
                col2.code(f"amenity: {poi_config.get('filter_amenity', 'None')}")
                col3.code(f"shop: {poi_config.get('filter_shop', 'None')}")
    
    # Section: Live Statistics
    elif section == "Live Statistics":
        st.header("📈 Live Database Statistics")
        
        if stats:
            st.markdown(create_stats_cards(stats), unsafe_allow_html=True)
            
            # Additional metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Density", f"{stats.get('avg_density', 0):.2f}")
            col2.metric("Max Density", f"{stats.get('max_density', 0):.2f}")
            col3.metric("Min Density", f"{stats.get('min_density', 0):.2f}")
        
        # Load grid data for charts
        with st.spinner("Loading grid data..."):
            grid_data = get_grid_with_neighbor_density()
            
            if grid_data:
                df = pd.DataFrame(grid_data)
                
                # Density histogram
                st.subheader("📊 POI Density Distribution")
                fig = create_density_histogram(df)
                st.plotly_chart(fig, use_container_width=True)
                
                # Score comparison
                st.subheader("🎯 Score by POI Type")
                
                scores_by_type = {}
                for poi_type in ["atm", "hospital", "mall"]:
                    scored_df = calculate_score(df.copy(), poi_type)
                    scores_by_type[poi_type] = scored_df
                
                # Top 5 comparison
                comparison_data = []
                for poi_type, scored_df in scores_by_type.items():
                    for _, row in scored_df.head(5).iterrows():
                        comparison_data.append({
                            "Grid": f"Grid {int(row['grid_id'])}",
                            "Type": poi_type.upper(),
                            "Score": row["score"]
                        })
                
                fig = px.bar(
                    pd.DataFrame(comparison_data),
                    x="Grid",
                    y="Score",
                    color="Type",
                    barmode="group",
                    color_discrete_map={"ATM": "#4361ee", "HOSPITAL": "#ef476f", "MALL": "#4cc9f0"}
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Scatter plot
                st.subheader("📍 Density vs Neighbor Density")
                df_scored = calculate_score(df.copy(), "atm")
                fig = create_density_vs_neighbor_scatter(df_scored)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Could not load grid data for visualization")


if __name__ == "__main__":
    main()
