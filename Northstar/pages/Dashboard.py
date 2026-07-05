import streamlit as st
import pandas as pd

from core.parser import load_schwab_csv
from database.database import load_snapshots

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(page_title="NorthStar Dashboard", layout="wide")
st.title("⭐ NorthStar Dashboard")

# =========================================================
# LOAD DATA (SINGLE SOURCE OF TRUTH)
# =========================================================

try:
    holdings = load_schwab_csv("data/schwab.csv")
except Exception as e:
    st.error(f"Failed to load Schwab data: {e}")
    st.stop()

if not holdings:
    st.warning("No holdings found.")
    st.stop()

df = pd.DataFrame(holdings)

# =========================================================
# HEADER METRICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Portfolio Value", f"${total_value:,.2f}")
col2.metric("Annual Income", f"${annual_income:,.2f}")
col3.metric("Monthly Income", f"${monthly_income:,.2f}")
col4.metric("Yield", f"{yield_pct:.2f}%")

st.divider()

# =========================================================
# CORE METRICS
# =========================================================

total_value = df["value"].sum()
annual_income = df["annual_income"].sum()
monthly_income = annual_income / 12
yield_pct = (annual_income / total_value) * 100 if total_value else 0
# =========================================================
# ALLOCATION OVERVIEW
# =========================================================

st.subheader("Asset Allocation")

alloc = df.groupby("asset_type")["value"].sum().reset_index()
alloc["percent"] = alloc["value"] / alloc["value"].sum() * 100

col1, col2 = st.columns(2)

with col1:
    st.bar_chart(alloc.set_index("asset_type")["value"])

with col2:
    st.dataframe(alloc, use_container_width=True)

st.divider()

# =========================================================
# TOP HOLDINGS
# =========================================================

st.subheader("Top Holdings")

top_holdings = df.sort_values("value", ascending=False).head(10)

st.dataframe(
    top_holdings[["ticker", "shares", "price", "value", "annual_income"]],
    use_container_width=True
)

st.divider()

# =========================================================
# INCOME LEADERS
# =========================================================

st.subheader("Top Income Generators")

income_df = df.sort_values("annual_income", ascending=False).head(10)

st.bar_chart(income_df.set_index("ticker")["annual_income"])

st.dataframe(
    income_df[["ticker", "annual_income", "value"]],
    use_container_width=True
)

st.divider()

# =========================================================
# PORTFOLIO HISTORY (SQLite)
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
    st.info("History will build as you refresh the app over time.")
