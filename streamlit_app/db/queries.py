"""
Database Queries Module
SQL queries for fetching spatial data from PostGIS.
"""

import pandas as pd
import streamlit as st
from db.connection import execute_query


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_grid_features():
    """
    Fetch all grid cells with their features.
    Returns geometry as GeoJSON for map rendering.
    """
    query = """
    SELECT 
        grid_id,
        poi_count,
        area_sq_km,
        poi_density,
        ST_AsGeoJSON(geom)::json as geometry,
        ST_X(ST_Centroid(geom)) as centroid_lng,
        ST_Y(ST_Centroid(geom)) as centroid_lat
    FROM ncr_grid_features
    WHERE poi_density IS NOT NULL
    ORDER BY grid_id;
    """
    return execute_query(query)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_grid_with_neighbor_density():
    """
    Fetch grid cells with precomputed neighbor POI density.
    Uses a simplified window-based approach for better performance.
    """
    # First, get basic grid features
    query = """
    SELECT 
        grid_id,
        poi_count,
        area_sq_km,
        poi_density,
        ST_AsGeoJSON(geom)::json as geometry,
        ST_X(ST_Centroid(geom)) as centroid_lng,
        ST_Y(ST_Centroid(geom)) as centroid_lat
    FROM ncr_grid_features
    WHERE poi_density IS NOT NULL
    ORDER BY grid_id;
    """
    results = execute_query(query)
    
    # Calculate neighbor density using a simple rolling average approach
    # Based on nearby grid_ids (faster than spatial join)
    if results:
        import pandas as pd
        df = pd.DataFrame(results)
        # Use rolling window of 5 cells as proxy for neighbor density
        df['neighbor_poi_density'] = df['poi_density'].rolling(window=5, center=True, min_periods=1).mean()
        return df.to_dict('records')
    
    return results


@st.cache_data(ttl=300)
def get_pois_by_type(poi_type):
    """
    Fetch POIs of a specific type.
    Supports the new config structure with filter_amenity and filter_shop.
    Coordinates are transformed to WGS84 (EPSG:4326) for compatibility.
    """
    from config import POI_TYPES
    
    poi_config = POI_TYPES.get(poi_type, {})
    filter_amenity = poi_config.get("filter_amenity")
    filter_shop = poi_config.get("filter_shop")
    
    conditions = []
    
    # Handle amenity filter (can be string or list)
    if filter_amenity:
        if isinstance(filter_amenity, list):
            amenity_list = ", ".join([f"'{a}'" for a in filter_amenity])
            conditions.append(f"amenity IN ({amenity_list})")
        else:
            conditions.append(f"amenity = '{filter_amenity}'")
    
    # Handle shop filter
    if filter_shop:
        conditions.append(f"shop = '{filter_shop}'")
    
    if not conditions:
        filter_clause = "1=0"  # No results if no filters
    else:
        filter_clause = " OR ".join(conditions)
    
    # Transform coordinates from Web Mercator (3857) to WGS84 (4326)
    query = f"""
    SELECT 
        osm_id,
        name,
        amenity,
        shop,
        ST_X(ST_Transform(geom, 4326)) as lng,
        ST_Y(ST_Transform(geom, 4326)) as lat
    FROM osm_pois_ncr
    WHERE ({filter_clause})
    AND geom IS NOT NULL;
    """
    return execute_query(query)


@st.cache_data(ttl=300)
def get_all_pois():
    """Fetch all POIs with their types. Coordinates transformed to WGS84."""
    query = """
    SELECT 
        osm_id,
        name,
        amenity,
        shop,
        ST_X(ST_Transform(geom, 4326)) as lng,
        ST_Y(ST_Transform(geom, 4326)) as lat,
        CASE 
            WHEN amenity = 'atm' THEN 'atm'
            WHEN amenity IN ('hospital', 'clinic') THEN 'hospital'
            WHEN shop = 'mall' OR amenity = 'mall' THEN 'mall'
            ELSE 'other'
        END as poi_type
    FROM osm_pois_ncr
    WHERE geom IS NOT NULL
    AND (
        amenity IN ('atm', 'hospital', 'clinic', 'mall')
        OR shop = 'mall'
    );
    """
    return execute_query(query)


@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_ncr_boundary():
    """Fetch NCR boundary as GeoJSON."""
    query = """
    SELECT 
        name,
        ST_AsGeoJSON(geom)::json as geometry
    FROM ncr_boundary
    LIMIT 1;
    """
    results = execute_query(query)
    return results[0] if results else None


@st.cache_data(ttl=300)
def get_database_stats():
    """Get summary statistics for the explainer page."""
    query = """
    SELECT 
        (SELECT COUNT(*) FROM ncr_grid_features) as total_grids,
        (SELECT COUNT(*) FROM osm_pois_ncr) as total_pois,
        (SELECT COUNT(*) FROM osm_pois_ncr WHERE amenity = 'atm') as atm_count,
        (SELECT COUNT(*) FROM osm_pois_ncr WHERE amenity IN ('hospital', 'clinic')) as hospital_count,
        (SELECT COUNT(*) FROM osm_pois_ncr WHERE shop = 'mall' OR amenity = 'mall') as mall_count,
        (SELECT ROUND(AVG(poi_density)::numeric, 2) FROM ncr_grid_features) as avg_density,
        (SELECT ROUND(MAX(poi_density)::numeric, 2) FROM ncr_grid_features) as max_density,
        (SELECT ROUND(MIN(poi_density)::numeric, 2) FROM ncr_grid_features WHERE poi_density > 0) as min_density;
    """
    results = execute_query(query)
    return results[0] if results else {}


@st.cache_data(ttl=300)
def get_poi_breakdown():
    """Get breakdown of POIs by amenity type - for data verification."""
    query = """
    SELECT 
        COALESCE(amenity, 'no_amenity') as amenity_type,
        COALESCE(shop, 'no_shop') as shop_type,
        COUNT(*) as count
    FROM osm_pois_ncr
    GROUP BY amenity, shop
    ORDER BY count DESC
    LIMIT 20;
    """
    return execute_query(query)


@st.cache_data(ttl=300) 
def get_poi_sample(poi_type, limit=10):
    """Get sample POIs of a specific type - for data verification."""
    from config import POI_TYPES
    
    poi_config = POI_TYPES.get(poi_type, {})
    filter_amenity = poi_config.get("filter_amenity")
    filter_shop = poi_config.get("filter_shop")
    
    conditions = []
    if filter_amenity:
        if isinstance(filter_amenity, list):
            amenity_list = ", ".join([f"'{a}'" for a in filter_amenity])
            conditions.append(f"amenity IN ({amenity_list})")
        else:
            conditions.append(f"amenity = '{filter_amenity}'")
    if filter_shop:
        conditions.append(f"shop = '{filter_shop}'")
    
    if not conditions:
        return []
    
    filter_clause = " OR ".join(conditions)
    
    query = f"""
    SELECT osm_id, name, amenity, shop, ST_X(geom) as lng, ST_Y(geom) as lat
    FROM osm_pois_ncr
    WHERE ({filter_clause}) AND geom IS NOT NULL
    LIMIT {limit};
    """
    return execute_query(query)


def get_grid_in_polygon(polygon_geojson):
    """
    Fetch grid cells that intersect with a drawn polygon.
    polygon_geojson: GeoJSON string of the polygon
    """
    query = """
    SELECT 
        grid_id,
        poi_count,
        area_sq_km,
        poi_density,
        ST_AsGeoJSON(geom)::json as geometry,
        ST_X(ST_Centroid(geom)) as centroid_lng,
        ST_Y(ST_Centroid(geom)) as centroid_lat
    FROM ncr_grid_features
    WHERE ST_Intersects(
        geom,
        ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
    )
    AND poi_density IS NOT NULL
    ORDER BY grid_id;
    """
    return execute_query(query, (polygon_geojson,))


# ============ Data Exploration Queries ============

@st.cache_data(ttl=300)
def get_table_list():
    """Get list of all tables in the database."""
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
    """
    return execute_query(query)


@st.cache_data(ttl=300)
def get_raw_pois_sample(limit=10):
    """Get sample rows from raw POI table."""
    query = f"""
    SELECT 
        osm_id,
        name,
        amenity,
        shop,
        ST_AsText(geom) as geometry_wkt,
        ST_X(geom) as longitude,
        ST_Y(geom) as latitude
    FROM osm_pois_ncr
    WHERE geom IS NOT NULL
    LIMIT {limit};
    """
    return execute_query(query)


@st.cache_data(ttl=300)
def get_grid_sample(limit=10):
    """Get sample rows from grid features table."""
    query = f"""
    SELECT 
        grid_id,
        poi_count,
        area_sq_km,
        poi_density,
        ST_AsText(ST_Centroid(geom)) as centroid_wkt,
        ST_X(ST_Centroid(geom)) as centroid_lng,
        ST_Y(ST_Centroid(geom)) as centroid_lat
    FROM ncr_grid_features
    WHERE poi_density IS NOT NULL
    ORDER BY grid_id
    LIMIT {limit};
    """
    return execute_query(query)


@st.cache_data(ttl=300)
def get_boundary_sample():
    """Get NCR boundary info."""
    query = """
    SELECT 
        name,
        ST_NPoints(geom) as num_points,
        ST_Area(geom::geography) / 1000000 as area_sq_km,
        ST_AsText(ST_Centroid(geom)) as centroid
    FROM ncr_boundary
    LIMIT 1;
    """
    return execute_query(query)


@st.cache_data(ttl=300)
def get_table_row_counts():
    """Get row counts for all relevant tables."""
    query = """
    SELECT 
        'osm_pois_ncr' as table_name,
        COUNT(*) as row_count
    FROM osm_pois_ncr
    UNION ALL
    SELECT 
        'ncr_grid_features' as table_name,
        COUNT(*) as row_count
    FROM ncr_grid_features
    UNION ALL
    SELECT 
        'ncr_boundary' as table_name,
        COUNT(*) as row_count
    FROM ncr_boundary;
    """
    return execute_query(query)


@st.cache_data(ttl=300)
def get_column_info(table_name):
    """Get column information for a table."""
    query = f"""
    SELECT 
        column_name,
        data_type,
        is_nullable
    FROM information_schema.columns
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position;
    """
    return execute_query(query)
