"""
Database Connection Module
Handles PostgreSQL/PostGIS connections for the LocateNCR app.
"""

import psycopg2
import streamlit as st
from contextlib import contextmanager
from config import DB_CONFIG


def get_db_connection():
    """
    Create a new database connection.
    Each connection is used once and then closed.
    """
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None


@contextmanager
def get_connection():
    """
    Context manager for database connections.
    Ensures connections are always closed after use.
    """
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    finally:
        if conn:
            conn.close()


def execute_query(query, params=None):
    """
    Execute a query and return results as a list of dicts.
    Connection is automatically closed after query.
    """
    with get_connection() as conn:
        if not conn:
            return []
        
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                results = [dict(zip(columns, row)) for row in cur.fetchall()]
                return results
        except Exception as e:
            st.error(f"Query error: {e}")
            return []


def test_connection():
    """Test database connectivity."""
    with get_connection() as conn:
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT PostGIS_Version();")
                    version = cur.fetchone()[0]
                    return True, f"PostGIS {version}"
            except Exception as e:
                return False, str(e)
        return False, "Could not connect to database"

