"""
Initialize SQLite database and tables for Water Leakage Detection System.
Run once: python init_db.py
SQLite is built into Python - no separate SQLite installation needed.
"""

import sys
import os

# Add parent so we can import from backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.db import init_database

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully. database.db created in backend/")
