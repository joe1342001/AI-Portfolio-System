import sqlite3
from pathlib import Path

# ============================================================
# NorthStar Database Engine v1.0
# ============================================================

DB_FOLDER = Path("database")
DB_FOLDER.mkdir(exist_ok=True)

DB_FILE = DB_FOLDER / "northstar.db"


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    with get_connection() as conn:

        cur = conn.cursor()

        # ----------------------------------------
        # Portfolio snapshots
        # ----------------------------------------

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

        # ----------------------------------------
        # Holdings
        # ----------------------------------------

        cur.execute("""
        CREATE TABLE IF NOT EXISTS holdings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            snapshot_id INTEGER,

            ticker TEXT,

            shares REAL,

            price REAL,

            value REAL,

            annual_income REAL,

            asset_type TEXT,

            FOREIGN KEY(snapshot_id)
                REFERENCES snapshots(id)

        )
        """)

        conn.commit()


# ============================================================
# SAVE SNAPSHOT
# ============================================================

def save_snapshot(
    portfolio_value,
    annual_income,
    monthly_income,
    portfolio_yield
):

    with get_connection() as conn:

        cur = conn.cursor()

        cur.execute("""
        INSERT INTO snapshots
        (
            snapshot_time,
            portfolio_value,
            annual_income,
            monthly_income,
            portfolio_yield
        )
        VALUES
        (
            datetime('now','localtime'),
            ?,?,?,?
        )
        """,
        (
            portfolio_value,
            annual_income,
            monthly_income,
            portfolio_yield
        ))

        conn.commit()

        return cur.lastrowid


# ============================================================
# SAVE HOLDING
# ============================================================

def save_holding(
    snapshot_id,
    ticker,
    shares,
    price,
    value,
    annual_income,
    asset_type
):

    with get_connection() as conn:

        cur = conn.cursor()

        cur.execute("""
        INSERT INTO holdings
        (
            snapshot_id,
            ticker,
            shares,
            price,
            value,
            annual_income,
            asset_type
        )
        VALUES
        (
            ?,?,?,?,?,?,?
        )
        """,
        (
            snapshot_id,
            ticker,
            shares,
            price,
            value,
            annual_income,
            asset_type
        ))

        conn.commit()


# ============================================================
# LOAD SNAPSHOT HISTORY
# ============================================================

def load_snapshots():

    with get_connection() as conn:

        cur = conn.cursor()

        cur.execute("""
        SELECT *
        FROM snapshots
        ORDER BY snapshot_time DESC
        """)

        return [dict(row) for row in cur.fetchall()]


# ============================================================
# LOAD HOLDINGS FOR SNAPSHOT
# ============================================================

def load_holdings(snapshot_id):

    with get_connection() as conn:

        cur = conn.cursor()

        cur.execute("""
        SELECT *
        FROM holdings
        WHERE snapshot_id=?
        ORDER BY value DESC
        """, (snapshot_id,))

        return [dict(row) for row in cur.fetchall()]


# ============================================================
# LATEST SNAPSHOT
# ============================================================

def latest_snapshot():

    with get_connection() as conn:

        cur = conn.cursor()

        cur.execute("""
        SELECT *
        FROM snapshots
        ORDER BY id DESC
        LIMIT 1
        """)

        row = cur.fetchone()

        if row is None:
            return None

        return dict(row)


# ============================================================
# DELETE DATABASE CONTENTS
# ============================================================

def clear_database():

    with get_connection() as conn:

        cur = conn.cursor()

        cur.execute("DELETE FROM holdings")
        cur.execute("DELETE FROM snapshots")

        conn.commit()


# ============================================================
# DATABASE STATISTICS
# ============================================================

def database_stats():

    with get_connection() as conn:

        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM snapshots")
        snapshots = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM holdings")
        holdings = cur.fetchone()[0]

    return {
        "snapshots": snapshots,
        "holdings": holdings
    }


# ============================================================
# FIRST RUN
# ============================================================

initialize_database()
