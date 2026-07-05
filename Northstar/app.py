import streamlit as st
import pandas as pd

from datetime import datetime

# Core modules
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

initialize_database()

st.title("⭐ NorthStar v4.0")

# =========================================================
# LOAD DATA (YOUR EXISTING PIPELINE HOOK)
# =========================================================

def load_schwab_data():
    """
    Replace this with your existing Schwab parser.
    Must return list of holdings in format:

    {
        "ticker": str,
        "shares": float,
        "price": float,
        "value": float,
        "annual_income": float,
        "asset_type": str
    }
    """
    st.warning("Hook your existing Schwab parser into load_schwab_data()")
    return []


holdings = load_schwab_data()

if not holdings:
    st.error("No holdings loaded. Connect your Schwab parser.")
    st.stop()

# =========================================================
# CALCULATIONS
# =========================================================

total_value = sum(h["value"] for h in holdings)

# fallback income model if not provided
for h in holdings:
    if "annual_income" not in h:
        h["annual_income"] = h["value"] * 0.05  # default 5%

annual_income = sum(h["annual_income"] for h in holdings)
monthly_income = annual_income / 12
portfolio_yield = (annual_income / total_value) if total_value > 0 else 0

# =========================================================
# SAVE SNAPSHOT (HISTORY ENGINE)
# =========================================================

snapshot_id = save_snapshot(
    portfolio_value=total_value,
    annual_income=annual_income,
    monthly_income=monthly_income,
    portfolio_yield=portfolio_yield
)

for h in holdings:
    save_holding(
        snapshot_id=snapshot_id,
        ticker=h["ticker"],
        shares=h["shares"],
        price=h["price"],
        value=h["value"],
        annual_income=h["annual_income"],
        asset_type=h.get("asset_type", "Equity")
    )

# =========================================================
# DASHBOARD UI
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

df = pd.DataFrame(holdings)

st.subheader("Holdings")

st.dataframe(
    df.sort_values("value", ascending=False),
    use_container_width=True
)

# =========================================================
# SIMPLE HISTORY VIEW
# =========================================================

st.subheader("History (Snapshots)")

history = load_snapshots()

if history:
    hist_df = pd.DataFrame(history)

    st.line_chart(
        hist_df.set_index("snapshot_time")[["portfolio_value"]]
    )
else:
    st.info("No history yet. Refresh app to generate snapshots.")
