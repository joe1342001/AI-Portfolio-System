import sqlite3
from pathlib import Path

DB_FILE = Path("database/northstar.db")


def get_connection():
    return sqlite3.connect(DB_FILE)


def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_time TEXT,
        portfolio_value REAL,
        annual_income REAL,
        monthly_income REAL,
        portfolio_yield REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS holdings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_id INTEGER,
        ticker TEXT,
        shares REAL,
        price REAL,
        value REAL,
        annual_income REAL,
        asset_type TEXT
    )
    """)

    conn.commit()
    conn.close()
