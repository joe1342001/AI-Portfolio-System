import sys
from pathlib import Path

# =========================================================
# STREAMLIT IMPORT FIX
# =========================================================
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from core.portfolio import load_portfolio

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(page_title="NorthStar Portfolio", layout="wide")
st.title("📊 Portfolio Overview")

# =========================================================
# LOAD DATA (NO DIRECT DIVIDEND CALLS HERE)
# =========================================================

holdings = load_portfolio()

if not holdings:
    st.warning("No holdings found.")
    st.stop()

df = pd.DataFrame(holdings)

# =========================================================
# METRICS
# =========================================================

total_value = df["value"].sum()
total_income = df["annual_income"].sum()
yield_pct = (total_income / total_value) * 100 if total_value else 0

col1, col2, col3 = st.columns(3)

col1.metric("Portfolio Value", f"${total_value:,.2f}")
col2.metric("Annual Income", f"${total_income:,.2f}")
col3.metric("Yield", f"{yield_pct:.2f}%")

st.divider()

# =========================================================
# HOLDINGS TABLE
# =========================================================

st.subheader("Holdings")

st.dataframe(
    df.sort_values("value", ascending=False),
    use_container_width=True
)

st.divider()

# =========================================================
# ALLOCATION
# =========================================================

st.subheader("Asset Allocation")

alloc = df.groupby("asset_type")["value"].sum().reset_index()
alloc["percent"] = alloc["value"] / alloc["value"].sum() * 100

st.bar_chart(alloc.set_index("asset_type")["value"])

st.dataframe(alloc, use_container_width=True)
