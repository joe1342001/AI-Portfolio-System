import sys
from pathlib import Path

# =========================================================
# STREAMLIT IMPORT FIX
# =========================================================
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from core.portfolio import load_portfolio
from core.dividends import enrich_with_dividends

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(page_title="NorthStar Income", layout="wide")
st.title("💰 NorthStar Income Dashboard")

# =========================================================
# LOAD DATA
# =========================================================

holdings = load_portfolio()

if not holdings:
    st.warning("No holdings found.")
    st.stop()

# IMPORTANT: ensure income is applied here (safe re-run)
holdings = enrich_with_dividends(holdings)

df = pd.DataFrame(holdings)

# =========================================================
# CORE METRICS
# =========================================================

total_value = df["value"].sum()
total_income = df["annual_income"].sum()
monthly_income = total_income / 12
yield_pct = (total_income / total_value) * 100 if total_value else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Portfolio Value", f"${total_value:,.2f}")
col2.metric("Annual Income", f"${total_income:,.2f}")
col3.metric("Monthly Income", f"${monthly_income:,.2f}")
col4.metric("Yield", f"{yield_pct:.2f}%")

st.divider()

# =========================================================
# INCOME BY HOLDING
# =========================================================

st.subheader("Top Income Generators")

income_df = df.sort_values("annual_income", ascending=False)

st.bar_chart(income_df.set_index("ticker")["annual_income"])

st.dataframe(
    income_df[["ticker", "value", "yield", "annual_income"]],
    use_container_width=True
)

st.divider()

# =========================================================
# INCOME BY ASSET TYPE
# =========================================================

st.subheader("Income by Asset Type")

grouped = df.groupby("asset_type")[["annual_income", "value"]].sum()
grouped["yield"] = grouped["annual_income"] / grouped["value"]

st.bar_chart(grouped["annual_income"])

st.dataframe(grouped, use_container_width=True)

st.divider()

# =========================================================
# YIELD DISTRIBUTION
# =========================================================

st.subheader("Yield Distribution")

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.hist(df["yield"], bins=10)

ax.set_title("Yield Distribution")
ax.set_xlabel("Yield")
ax.set_ylabel("Holdings")

st.pyplot(fig)

st.divider()

# =========================================================
# DEBUG VIEW
# =========================================================

with st.expander("Raw Data"):
    st.dataframe(df, use_container_width=True)
