import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from core.parser import load_schwab_csv
from core.portfolio import load_portfolio
from database.database import load_snapshots
# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(page_title="NorthStar Analytics", layout="wide")
st.title("📊 NorthStar Analytics")

# =========================================================
# DEBUG (OPTIONAL - REMOVE LATER)
# =========================================================

with st.expander("Debug Path Info"):
    st.write(debug_path("data/schwab.csv"))

# =========================================================
# LOAD HOLDINGS (SINGLE SOURCE OF TRUTH)
# =========================================================

try:
    holdings = load_schwab_csv("data/schwab.csv")
except Exception as e:
    st.error(f"Failed to load holdings: {e}")
    st.stop()

if not holdings:
    st.warning("No holdings found.")
    st.stop()

df = pd.DataFrame(holdings)

# =========================================================
# BASIC METRICS
# =========================================================

total_value = df["value"].sum()
total_income = df["annual_income"].sum()
yield_pct = (total_income / total_value) * 100 if total_value else 0

col1, col2, col3 = st.columns(3)

col1.metric("Total Portfolio Value", f"${total_value:,.2f}")
col2.metric("Annual Income", f"${total_income:,.2f}")
col3.metric("Yield", f"{yield_pct:.2f}%")

st.divider()

# =========================================================
# TOP HOLDINGS
# =========================================================

st.subheader("Top Holdings by Value")

top_holdings = df.sort_values("value", ascending=False)

st.dataframe(
    top_holdings[["ticker", "shares", "price", "value", "annual_income"]],
    use_container_width=True
)

# =========================================================
# ALLOCATION BY ASSET TYPE
# =========================================================

st.subheader("Asset Allocation")

alloc = df.groupby("asset_type")["value"].sum().reset_index()
alloc["percent"] = alloc["value"] / alloc["value"].sum() * 100

st.bar_chart(alloc.set_index("asset_type")["value"])

st.dataframe(alloc, use_container_width=True)

# =========================================================
# INCOME BREAKDOWN
# =========================================================

st.subheader("Income Breakdown")

income_df = df.sort_values("annual_income", ascending=False)

st.bar_chart(income_df.set_index("ticker")["annual_income"])

st.dataframe(
    income_df[["ticker", "annual_income", "value"]],
    use_container_width=True
)

# =========================================================
# SNAPSHOT HISTORY (SQLite)
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
    st.info("History will appear after multiple app refreshes.")
