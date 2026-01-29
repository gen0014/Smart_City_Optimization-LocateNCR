"""
Visualization Utilities
Chart generation for the explainer page.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_density_histogram(df):
    """Create a histogram of POI density distribution."""
    fig = px.histogram(
        df,
        x="poi_density",
        nbins=40,
        title="POI Density Distribution Across Grid Cells",
        labels={"poi_density": "POI Density (per sq km)", "count": "Number of Grids"},
        color_discrete_sequence=["#4361ee"]
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff")
    )
    return fig


def create_score_comparison_chart(atm_df, hospital_df, mall_df, top_n=10):
    """Create a grouped bar chart comparing scores across POI types."""
    
    data = []
    
    for df, poi_type, color in [
        (atm_df, "ATM", "#4361ee"),
        (hospital_df, "Hospital", "#ef476f"),
        (mall_df, "Mall", "#4cc9f0")
    ]:
        top = df.head(top_n)
        for _, row in top.iterrows():
            data.append({
                "Grid ID": f"Grid {int(row['grid_id'])}",
                "POI Type": poi_type,
                "Score": row["score"]
            })
    
    df_plot = pd.DataFrame(data)
    
    fig = px.bar(
        df_plot,
        x="Grid ID",
        y="Score",
        color="POI Type",
        barmode="group",
        title="Top Recommendation Scores by POI Type",
        color_discrete_map={
            "ATM": "#4361ee",
            "Hospital": "#ef476f",
            "Mall": "#4cc9f0"
        }
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
        xaxis_tickangle=-45
    )
    return fig


def create_density_vs_neighbor_scatter(df):
    """Create a scatter plot of density vs neighbor density."""
    fig = px.scatter(
        df,
        x="poi_density",
        y="neighbor_poi_density",
        size="poi_count",
        color="score",
        color_continuous_scale="Viridis",
        title="POI Density vs Neighbor Density",
        labels={
            "poi_density": "POI Density",
            "neighbor_poi_density": "Neighbor Avg Density",
            "poi_count": "POI Count"
        },
        hover_data=["grid_id"]
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff")
    )
    return fig


def create_stats_cards(stats):
    """Generate HTML for statistics cards."""
    cards = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin: 1rem 0;">
        <div style="background: linear-gradient(135deg, #4361ee 0%, #7209b7 100%); padding: 1.5rem; border-radius: 12px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold;">{stats.get('total_grids', 0):,}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Total Grid Cells</div>
        </div>
        <div style="background: linear-gradient(135deg, #ef476f 0%, #f72585 100%); padding: 1.5rem; border-radius: 12px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold;">{stats.get('total_pois', 0):,}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Total POIs</div>
        </div>
        <div style="background: linear-gradient(135deg, #4cc9f0 0%, #00f5d4 100%); padding: 1.5rem; border-radius: 12px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold;">{stats.get('atm_count', 0):,}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">ATMs</div>
        </div>
        <div style="background: linear-gradient(135deg, #7209b7 0%, #560bad 100%); padding: 1.5rem; border-radius: 12px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold;">{stats.get('hospital_count', 0):,}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Hospitals</div>
        </div>
        <div style="background: linear-gradient(135deg, #f72585 0%, #b5179e 100%); padding: 1.5rem; border-radius: 12px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold;">{stats.get('mall_count', 0):,}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Malls</div>
        </div>
    </div>
    """
    return cards


def create_architecture_diagram():
    """Return Mermaid diagram code for architecture."""
    return """
```mermaid
graph LR
    subgraph Data Sources
        A[🗺️ OpenStreetMap] --> B[📦 osm2pgsql]
    end
    
    subgraph PostGIS Database
        B --> C[(🐘 PostgreSQL)]
        C --> D[📍 POIs]
        C --> E[🔲 Grid Features]
        C --> F[🗺️ Boundaries]
    end
    
    subgraph Analytics
        D --> G[⚡ Apache Spark]
        E --> G
        G --> H[🤖 KMeans Clustering]
        G --> I[📊 Feature Engineering]
    end
    
    subgraph Frontend
        D --> J[🎯 Streamlit]
        E --> J
        H --> J
        J --> K[🗺️ Interactive Map]
        J --> L[📈 Recommendations]
    end
```
    """
