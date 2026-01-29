"""
LocateNCR - Smart City POI Recommendation System
Main Streamlit Application
"""

import streamlit as st

# Page Configuration - must be first Streamlit command
st.set_page_config(
    page_title="LocateNCR - Smart City POI Finder",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium dark theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(67, 97, 238, 0.3);
    }
    
    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(90deg, #4361ee, #7209b7, #f72585);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Cards */
    .stMetric {
        background: rgba(67, 97, 238, 0.1);
        border: 1px solid rgba(67, 97, 238, 0.3);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #4361ee, #7209b7);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(67, 97, 238, 0.4);
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: rgba(22, 33, 62, 0.8);
        border: 1px solid rgba(67, 97, 238, 0.3);
        border-radius: 8px;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #4361ee, #7209b7);
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(67, 97, 238, 0.1);
        border: 1px solid rgba(67, 97, 238, 0.3);
        border-radius: 12px;
    }
    
    /* Glassmorphism effect for containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    ::-webkit-scrollbar-thumb {
        background: #4361ee;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Import database module
from db.connection import test_connection


def main():
    """Main application entry point."""
    
    # Sidebar Header
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <span style="font-size: 3rem;">📍</span>
            <h1 style="margin: 0.5rem 0;">LocateNCR</h1>
            <p style="color: #888; font-size: 0.9rem;">Smart City POI Finder</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Database Status
        status, message = test_connection()
        if status:
            st.success(f"✅ Database Connected\n\n{message}")
        else:
            st.error(f"❌ Database Error\n\n{message}")
        
        st.divider()
        
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            <p>Built with ❤️ for Delhi NCR</p>
            <p>Data: OpenStreetMap</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content - Landing Page
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">🏙️ Welcome to LocateNCR</h1>
        <p style="font-size: 1.2rem; color: #aaa; max-width: 700px; margin: 0 auto;">
            Find the optimal locations for ATMs, Hospitals, and Malls across the Delhi NCR region 
            using spatial analysis and machine learning.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <h3>📍 Location Finder</h3>
            <p style="color: #aaa;">
                Interactive map with AI-powered recommendations for optimal POI placement.
                Filter by type, draw areas, and export results.
            </p>
            <ul style="color: #888;">
                <li>1km × 1km grid analysis</li>
                <li>Real-time scoring algorithm</li>
                <li>Existing POI visualization</li>
                <li>Polygon selection tool</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗺️ Open Location Finder", key="loc_btn", use_container_width=True):
            st.switch_page("pages/1_📍_Location_Finder.py")
    
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h3>📊 How It Works</h3>
            <p style="color: #aaa;">
                Understand the methodology behind our recommendations with 
                interactive visualizations and explanations.
            </p>
            <ul style="color: #888;">
                <li>Architecture overview</li>
                <li>Scoring algorithm details</li>
                <li>Clustering analysis</li>
                <li>Live database statistics</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📈 Learn How It Works", key="how_btn", use_container_width=True):
            st.switch_page("pages/2_📊_How_It_Works.py")
    
    # Quick Stats
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Quick Overview")
    
    if status:
        from db.queries import get_database_stats
        stats = get_database_stats()
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Grid Cells", f"{stats.get('total_grids', 0):,}")
        c2.metric("Total POIs", f"{stats.get('total_pois', 0):,}")
        c3.metric("ATMs", f"{stats.get('atm_count', 0):,}")
        c4.metric("Hospitals", f"{stats.get('hospital_count', 0):,}")
        c5.metric("Malls", f"{stats.get('mall_count', 0):,}")
    else:
        st.warning("Connect to database to see statistics")


if __name__ == "__main__":
    main()
