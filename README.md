# 🌆 LocateNCR - Smart City Optimization Platform

**LocateNCR** is an advanced spatial analytics platform designed to optimize urban planning and business expansion in the Delhi National Capital Region (NCR). 

Using geospatial data from OpenStreetMap and power of PostGIS, it identifies the optimal locations for new Points of Interest (POIs) like ATMs, Hospitals, Malls, and more by balancing **demand** (footfall/density) against **competition**.

![Dashboard Screenshot](https://via.placeholder.com/800x400.png?text=LocateNCR+Dashboard+Preview)

---

## 🚀 Key Features

### 📍 Intelligent Location Finder
- **Grid-Based Scoring**: Divides NCR into 1km × 1km grids to evaluate potential.
- **POI-Specific Analysis**: 
  - *ATM Strategy*: High density areas with low existing ATM count.
  - *Hospital Strategy*: Residential areas with gaps in healthcare coverage.
  - *Mall Strategy*: Exclusive zones with high commercial activity but no nearby competitors.
- **Interactive Maps**: 3D visualization of high-potential zones using PyDeck.

### 🧠 Advanced Multi-Factor Scoring Engine
Goes beyond simple density maps by considering 5 key factors:
1. **POI Density** (Activity Level)
2. **Commercial Density** (Business Presence)
3. **Residential Score** (Population Proxy)
4. **Accessibility** (Transit Connectivity)
5. **Competitor Penalty** (Real-time distance checks specific to POI type)

### 📈 Growth Hotspots Prediction
- Identifies **emerging neighborhoods** that are growing fast but underserved.
- Classifies areas into *Emerging*, *High Growth*, *Growing*, and *Stable*.


---

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python)
- **Database**: PostgreSQL 15 + PostGIS (Spatial Queries)
- **Visualization**: PyDeck (3D Maps), Folium (Interactive Layers), Plotly (Charts)
- **Data Processing**: Pandas, GeoPandas, Shapely
- **Data Source**: OpenStreetMap (OSM) PBF Extracts

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL with PostGIS extension enabled
- PostGIS database named `smart_city` (or configure in `db/connection.py`)

### 1. Clone the Repository
```bash
git clone https://github.com/UtkarshShaarma/Smart_City_Optimization-LocateNCR.git
cd Smart_City_Optimization-LocateNCR
```

### 2. Install Dependencies
```bash
cd streamlit_app
pip install -r requirements.txt
```

### 3. Database Setup
Ensure your PostgreSQL database is running and credentials are set in `.env` or `db/connection.py`.
The system expects tables: `ncr_grid_features`, `osm_pois_ncr`, `ncr_boundary`.

### 4. Run the Application
```bash
streamlit run app.py
```
The application will open in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
SmartCity_project/
├── streamlit_app/           # Main Application Code
│   ├── app.py               # Entry point
│   ├── config.py            # Global configuration & weights
│   ├── pages/               # Streamlit Multi-Page App
│   │   ├── 1_📍_Location_Finder.py
│   │   ├── 2_📊_How_It_Works.py
│   │   ├── 3_🔮_Scenario_Analysis.py
│   │   └── 4_📈_Growth_Hotspots.py
│   ├── utils/               # Helper modules
│   │   ├── scoring.py       # Basic scoring logic
│   │   ├── advanced_scoring.py # Multi-factor engine
│   │   ├── visualization.py # Charting & mapping helpers
│   │   └── geo.py           # Geometry transformations
│   └── db/                  # Database connectivity
│       ├── connection.py    # DB connection string
│       └── queries.py       # SQL queries
├── data_set/                # Data storage (ignored in git)
├── notes/                   # Development notes
└── README.md                # Project documentation
```

---

## 🤝 Contribution

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
