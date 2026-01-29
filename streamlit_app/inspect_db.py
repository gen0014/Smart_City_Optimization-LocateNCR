
import psycopg2
from config import DB_CONFIG

def inspect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        print("Tables in database:", [t[0] for t in tables])
        
        # Inspect ncr_grid_features columns
        if ('ncr_grid_features',) in tables:
            print("\nColumns in ncr_grid_features:")
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'ncr_grid_features'
            """)
            columns = cur.fetchall()
            for col in columns:
                print(f"- {col[0]} ({col[1]})")
                
        # Inspect osm_pois_ncr columns
        if ('osm_pois_ncr',) in tables:
            print("\nColumns in osm_pois_ncr:")
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'osm_pois_ncr'
            """)
            columns = cur.fetchall()
            for col in columns:
                print(f"- {col[0]} ({col[1]})")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_db()
