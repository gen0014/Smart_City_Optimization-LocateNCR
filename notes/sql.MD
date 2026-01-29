# PHASE 2 — POSTGIS & SPATIAL DATABASE


This document fully recreates **Phase 2** of the Smart City NCR project.
It includes Docker setup, PostGIS configuration, OpenStreetMap ingestion,
boundary creation, POI extraction, spatial grid generation, and feature engineering.

This file alone is sufficient to reproduce the database from scratch.

====================================================================
SYSTEM REQUIREMENTS
====================================================================

• Windows 10 / 11  
• Docker Desktop (WSL2 backend enabled)  
• Minimum 8 GB RAM  
• OpenStreetMap PBF file placed at:
  data_set/raw_data/NewDelhi.osm.pbf

====================================================================
PROJECT STRUCTURE
====================================================================

SmartCity_project/
│
├── data_set/
│   └── raw_data/
│       └── NewDelhi.osm.pbf
│
└── PHASE_2_POSTGIS_SMART_CITY_NCR.md

====================================================================
STEP 1 — START POSTGIS DATABASE (DOCKER)
====================================================================

Run in **PowerShell** from project root:

 & "C:\Program Files\PostgreSQL\15\bin\psql.exe" 


## STEP 2 — CREATE DATABASE


CREATE DATABASE smartcity_delhi;

\c smartcity_delhi


## Enable extensions:

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS hstore;
\dx



# Download a basic flex config
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/osm2pgsql-dev/osm2pgsql/master/flex-config/compatible.lua" -OutFile "compatible.lua"

# Run with flex output
osm2pgsql `
  -H localhost `
  -P 5432 `
  -U postgres `
  -W `
  -d smartcity_delhi `
  --create `
  --slim `
  -O flex `
  -S compatible.lua `
  data_set/raw_data/NewDelhi.osm.pbf

   & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d smartcity_delhi
psql (15.15)

====================================================================
STEP 2 — ENABLE POSTGIS & HSTORE EXTENSIONS
====================================================================

docker exec -it smartcity_postgis psql -U postgres smartcity_delhi

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS hstore;
\dx
\q

====================================================================
STEP 3 — INGEST OPENSTREETMAP DATA (osm2pgsql)
====================================================================

This creates:
• planet_osm_point
• planet_osm_polygon
• planet_osm_line
• planet_osm_roads

docker run --rm `
  -e PGPASSWORD=postgres `
  -v ${PWD}/data_set:/data `
  iboates/osm2pgsql `
  osm2pgsql `
  -H host.docker.internal `
  -P 5432 `
  -U postgres `
  -d smartcity_delhi `
  --create `
  --slim `
  --hstore `
  --latlong `
  /data/raw_data/NewDelhi.osm.pbf

====================================================================
STEP 4 — CONNECT TO DATABASE
====================================================================

docker exec -it smartcity_postgis psql -U postgres smartcity_delhi

====================================================================
STEP 5 — CREATE DELHI ADMINISTRATIVE BOUNDARY
====================================================================

DROP TABLE IF EXISTS delhi_boundary;

CREATE TABLE delhi_boundary AS
SELECT
  name,
  ST_Multi(ST_Union(way)) AS geom
FROM planet_osm_polygon
WHERE boundary = 'administrative'
  AND name ILIKE '%Delhi%'
GROUP BY name;

CREATE INDEX idx_delhi_boundary_geom
ON delhi_boundary
USING GIST (geom);

====================================================================
STEP 6 — CREATE NCR BOUNDARY (DELHI + SURROUNDING CITIES)
====================================================================

DROP TABLE IF EXISTS ncr_boundary;

CREATE TABLE ncr_boundary AS
SELECT
  'NCR' AS name,
  ST_Multi(ST_Union(way)) AS geom
FROM planet_osm_polygon
WHERE boundary = 'administrative'
AND name ILIKE ANY (ARRAY[
  '%Delhi%',
  '%Gurgaon%',
  '%Gurugram%',
  '%Noida%',
  '%Ghaziabad%',
  '%Faridabad%',
  '%Gautam Buddha Nagar%'
]);

CREATE INDEX idx_ncr_boundary_geom
ON ncr_boundary
USING GIST (geom);

====================================================================
STEP 7 — CREATE AUTHORITATIVE OSM POI TABLE
====================================================================

DROP TABLE IF EXISTS osm_pois;

CREATE TABLE osm_pois AS
SELECT
  osm_id,
  amenity,
  shop,
  leisure,
  tags->'healthcare' AS healthcare,
  name,
  way AS geom
FROM planet_osm_point
WHERE
  amenity IS NOT NULL
  OR shop IS NOT NULL
  OR leisure IS NOT NULL
  OR tags ? 'healthcare';

CREATE INDEX idx_osm_pois_geom
ON osm_pois
USING GIST (geom);

====================================================================
STEP 8 — FILTER POIS TO NCR ONLY
====================================================================

DROP TABLE IF EXISTS osm_pois_ncr;

CREATE TABLE osm_pois_ncr AS
SELECT p.*
FROM osm_pois p
JOIN ncr_boundary n
ON ST_Within(p.geom, n.geom);

CREATE INDEX idx_osm_pois_ncr_geom
ON osm_pois_ncr
USING GIST (geom);

====================================================================
STEP 9 — CREATE 1 KM × 1 KM NCR GRID (CORRECT CRS HANDLING)
====================================================================

IMPORTANT:
Grid generation must be done in a projected CRS (meters),
then transformed back to EPSG:4326.

DROP TABLE IF EXISTS ncr_grid;

CREATE TABLE ncr_grid AS
SELECT
  row_number() OVER () AS grid_id,
  ST_Transform(geom, 4326) AS geom
FROM ST_SquareGrid(
  1000,
  (
    SELECT ST_Transform(geom, 3857)
    FROM ncr_boundary
  )
);

CREATE INDEX idx_ncr_grid_geom
ON ncr_grid
USING GIST (geom);

VALIDATION:
SELECT COUNT(*) FROM ncr_grid;
-- Expected ≈ 1000+

====================================================================
STEP 10 — GRID-LEVEL FEATURE ENGINEERING (ML READY)
====================================================================

DROP TABLE IF EXISTS ncr_grid_features;

CREATE TABLE ncr_grid_features AS
SELECT
  g.grid_id,
  g.geom,
  COUNT(p.osm_id) AS poi_count
FROM ncr_grid g
LEFT JOIN osm_pois_ncr p
ON ST_Within(p.geom, g.geom)
GROUP BY g.grid_id, g.geom;

ALTER TABLE ncr_grid_features
ADD COLUMN area_sq_km DOUBLE PRECISION,
ADD COLUMN poi_density DOUBLE PRECISION;

UPDATE ncr_grid_features
SET
  area_sq_km = ST_Area(geom::geography) / 1000000,
  poi_density = poi_count / NULLIF(ST_Area(geom::geography) / 1000000, 0);

CREATE INDEX idx_ncr_grid_features_geom
ON ncr_grid_features
USING GIST (geom);

====================================================================
STEP 11 — FINAL VALIDATION
====================================================================

SELECT
  COUNT(*) AS total_grids,
  MIN(poi_count),
  MAX(poi_count),
  ROUND(AVG(poi_count), 2) AS avg_poi
FROM ncr_grid_features;

EXPECTED (APPROX):
• total_grids ≈ 1020
• min = 0
• max ≈ 300+
• avg ≈ 8

====================================================================
FINAL TABLES CREATED
====================================================================

• planet_osm_point
• planet_osm_polygon
• planet_osm_line
• delhi_boundary
• ncr_boundary
• osm_pois
• osm_pois_ncr
• ncr_grid
• ncr_grid_features

====================================================================
PHASE 2 STATUS
====================================================================

✔ Dockerized PostGIS  
✔ OpenStreetMap ingested  
✔ NCR boundary modeled  
✔ Authoritative POIs extracted  
✔ Correct spatial grid created  
✔ ML-ready feature table built  

======================
PHASE 2 COMPLETE
======================




PHASE 3 architecture :
PostGIS (Spatial DB)
      │
      │ JDBC
      ▼
Apache Spark (Docker)
      │
      ├── Feature Engineering
      ├── Aggregations
      ├── Scaling / Normalization
      ├── ML (Clustering / Regression)
      ▼
ML-Ready Dataset (Parquet / CSV)


📁 PHASE 3 PROJECT STRUCTURE
SmartCity_project/
│
├── docker-compose.yml
├── data_set/
│
├── notebooks/
│   └── phase3_spark_ml.ipynb
│
└── phase3/
    ├── spark_jobs/
    └── outputs/

    

🚀 PHASE 3 ROADMAP (STEP-BY-STEP)
STEP 1 — Spark Docker Setup

Run Spark + Jupyter together (no local Spark install)

STEP 2 — Connect Spark to PostGIS

Load ncr_grid_features via JDBC

STEP 3 — Spark Data Validation

Check schema, nulls, distributions

STEP 4 — Feature Engineering

POI density normalization

Grid classification

Log transforms

STEP 5 — ML Pipeline

VectorAssembler

StandardScaler

KMeans (Hotspot clustering)

STEP 6 — Export ML Dataset

Save as Parquet / CSV for visualization



dOCKER (jUYP)
docker logs smartcity_jupyter
