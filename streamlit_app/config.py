"""
LocateNCR Configuration
"""

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "smartcity_delhi",
    "user": "postgres",
    "password": "toor"
}

# Map Configuration
MAP_CENTER = [28.6139, 77.2090]  # Delhi center
MAP_ZOOM = 10

# Scoring Weights
SCORING_WEIGHTS = {
    "atm": {
        "poi_density_weight": 0.8,
        "neighbor_penalty": 1.2
    },
    "hospital": {
        "poi_density_weight": 0.5,
        "neighbor_penalty": 0.6
    },
    "mall": {
        "poi_density_weight": 0.7,
        "neighbor_penalty": 1.8
    },
    "pharmacy": {
        "poi_density_weight": 0.7,
        "neighbor_penalty": 1.0
    },
    "school": {
        "poi_density_weight": 0.6,
        "neighbor_penalty": 0.8
    },
    "bank": {
        "poi_density_weight": 0.8,
        "neighbor_penalty": 1.4
    },
    "police": {
        "poi_density_weight": 0.4,
        "neighbor_penalty": 0.5
    },
    "bus_station": {
        "poi_density_weight": 0.6,
        "neighbor_penalty": 0.7
    },
    "fuel": {
        "poi_density_weight": 0.7,
        "neighbor_penalty": 1.2
    },
    "supermarket": {
        "poi_density_weight": 0.75,
        "neighbor_penalty": 1.5
    }
}

# Color Palette
COLORS = {
    "primary": "#4361ee",
    "secondary": "#7209b7",
    "background": "#1a1a2e",
    "surface": "#16213e",
    "text": "#ffffff",
    "accent": "#00f5d4"
}

# POI Type Configurations
POI_TYPES = {
    "atm": {
        "label": "🏧 ATM",
        "color": [67, 97, 238],  # Blue
        "filter_amenity": "atm",
        "filter_shop": None
    },
    "hospital": {
        "label": "🏥 Hospital",
        "color": [239, 71, 111],  # Red
        "filter_amenity": ["hospital", "clinic"],
        "filter_shop": None
    },
    "mall": {
        "label": "🛒 Mall",
        "color": [76, 201, 240],  # Cyan
        "filter_amenity": "mall",
        "filter_shop": "mall"
    },
    "pharmacy": {
        "label": "💊 Pharmacy",
        "color": [0, 200, 83],  # Green
        "filter_amenity": "pharmacy",
        "filter_shop": None
    },
    "school": {
        "label": "🏫 School",
        "color": [255, 193, 7],  # Yellow
        "filter_amenity": ["school", "college", "university"],
        "filter_shop": None
    },
    "bank": {
        "label": "🏦 Bank",
        "color": [156, 39, 176],  # Purple
        "filter_amenity": "bank",
        "filter_shop": None
    },
    "police": {
        "label": "🚔 Police Station",
        "color": [33, 150, 243],  # Light Blue
        "filter_amenity": "police",
        "filter_shop": None
    },
    "bus_station": {
        "label": "🚌 Bus Station",
        "color": [255, 152, 0],  # Orange
        "filter_amenity": "bus_station",
        "filter_shop": None
    },
    "fuel": {
        "label": "⛽ Fuel Station",
        "color": [121, 85, 72],  # Brown
        "filter_amenity": "fuel",
        "filter_shop": None
    },
    "supermarket": {
        "label": "🛍️ Supermarket",
        "color": [0, 150, 136],  # Teal
        "filter_amenity": None,
        "filter_shop": "supermarket"
    }
}
