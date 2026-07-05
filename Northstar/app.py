import streamlit as st
import pandas as pd
from pathlib import Path
import sqlite3

from database.database import (
    initialize_database,
    save_snapshot,
    save_holding,
    load_snapshots
)

# =========================================================
# INIT
# =========================================================

st.set_page_config(page_title="NorthStar", layout="wide")
st.title("⭐ NorthStar v4.1 — Stable Edition")

initialize_database()

import os

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "schwab.csv"

# =========================================================
# SCHWAB PARSER (EMBEDDED - NO DEPENDENCIES)
# =========================================================

def parse_schwab_csv(file_path):
    path = Path(file_path)

    if not path.exists():
        st.error(f"File not found: {file_path}")
        return []

    lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    header_index = None
    for i, line in enumerate(lines):
        if line.startswith('"Symbol"') and '"Qty' in line:
            header_index = i
            break

    if header_index is None:
        st.error("Could not locate Schwab header row")
        return []

    headers = [h.strip().strip('"') for h in lines[header_index].split('","')]

    def col(name):
        for i, h in enumerate(headers):
            if name.lower() in h.lower():
                return i
        return None

    i_symbol = col("Symbol")
    i_qty = col("Qty")
    i_price = col("Price")
    i_value = col("Mkt Val")
    i_asset = col("Asset Type")

    holdings = []

    for line in lines[header_index + 1:]:

        if not line.startswith('"'):
            continue

        parts = [p.strip().strip('"') for p in line.split('","')]

        try:
            ticker = parts[i_symbol]

            # skip junk rows
            if "Total" in ticker or ticker.strip() == "":
                continue

            shares = float(parts[i_qty].replace(",", ""))

            value = parts[i_value].replace("$", "").replace(",", "")
            value = float(value) if value else 0.0

            price = parts[i_price].replace("$", "").replace(",", "")
            price = float(price) if price else 0.0

            asset_type = parts[i_asset] if i_asset else "Equity"

            # fallback income model (Schwab does NOT provide yield)
            annual_income = value * 0.05

            holdings.append({
                "ticker": ticker,
                "shares": shares,
                "price": price,
                "value": value,
                "annual_income": annual_income,
                "asset_type": asset_type
            })

        except Exception:
            continue

    return holdings


# =========================================================
# LOAD DATA
# =========================================================

holdings = parse_schwab_csv(DATA_FILE)

if not holdings:
    st.stop()

# =========================================================
# CALCULATIONS
# =========================================================

total_value = sum(h["value"] for h in holdings)
annual_income = sum(h["annual_income"] for h in holdings)
monthly_income = annual_income / 12
portfolio_yield = annual_income / total_value if total_value else 0

# =========================================================
# SAVE TO DATABASE
# =========================================================

snapshot_id = save_snapshot(
    portfolio_value=total_value,
    annual_income=annual_income,
    monthly_income=monthly_income,
    portfolio_yield=portfolio_yield
)

for h in holdings:
    save_holding(
        snapshot_id,
        h["ticker"],
        h["shares"],
        h["price"],
        h["value"],
        h["annual_income"],
        h["asset_type"]
    )

# =========================================================
# DASHBOARD
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Portfolio Value", f"${total_value:,.2f}")
col2.metric("Annual Income", f"${annual_income:,.2f}")
col3.metric("Monthly Income", f"${monthly_income:,.2f}")
col4.metric("Yield", f"{portfolio_yield*100:.2f}%")

st.divider()

# =========================================================
# HOLDINGS TABLE
# =========================================================

df = pd.DataFrame(holdings).sort_values("value", ascending=False)

st.subheader("Holdings")
st.dataframe(df, use_container_width=True)

# =========================================================
# HISTORY
# =========================================================

st.subheader("Portfolio History")

history = load_snapshots()

if history and len(history) > 1:
    hist_df = pd.DataFrame(history)
    hist_df["snapshot_time"] = pd.to_datetime(hist_df["snapshot_time"])

    st.line_chart(
        hist_df.set_index("snapshot_time")[["portfolio_value"]]
    )
else:
    st.info("History will build as you refresh the app.")
