"""
Database connection and utilities for Water Leakage Detection System.
Uses SQLite (built into Python - no separate SQLite installation required).
"""

import sqlite3
import os

# Database file path - created in backend folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")


def get_connection():
    """Get a new SQLite database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    return conn


def init_database():
    """
    Create tables if they don't exist.
    Called by init_db.py and on first app run if needed.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Table: leak_events - stores each prediction (single sensor, leak vs no leak only)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leak_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id INTEGER NOT NULL,
            leak_status TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Table: sensors - single sensor; health status and last_seen only (no pipe sections)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            sensor_id INTEGER PRIMARY KEY,
            sensor_name TEXT NOT NULL,
            health_status TEXT NOT NULL,
            last_seen TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
