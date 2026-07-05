import sys
from pathlib import Path

# =========================================================
# STREAMLIT IMPORT FIX
# =========================================================
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from core.portfolio import load_portfolio

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(page_title="NorthStar Income v6", layout="wide")
st.title("💰 Income Dashboard v6")

# =========================================================
# LOAD DATA
# =========================================================

holdings = load_portfolio()

if not holdings:
    st.warning("No holdings found.")
    st.stop()

df = pd.DataFrame(holdings)

# =========================================================
# CORE METRICS
# =========================================================

portfolio_value = df["value"].sum()
annual_income = df["annual_income"].sum()
monthly_income = annual_income / 12
yield_pct = (annual_income / portfolio_value) * 100 if portfolio_value else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Portfolio Value", f"${portfolio_value:,.2f}")
col2.metric("Annual Income", f"${annual_income:,.2f}")
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

asset_income = df.groupby("asset_type")[["value", "annual_income"]].sum()
asset_income["yield"] = asset_income["annual_income"] / asset_income["value"]

st.bar_chart(asset_income["annual_income"])

st.dataframe(asset_income, use_container_width=True)

st.divider()

# =========================================================
# YIELD DISTRIBUTION (FIXED PROPERLY)
# =========================================================

st.subheader("Yield Distribution")

fig, ax = plt.subplots()
ax.hist(df["yield"], bins=12, edgecolor="black")
ax.set_xlabel("Yield")
ax.set_ylabel("Number of Holdings")
ax.set_title("Portfolio Yield Distribution")

st.pyplot(fig)

st.divider()

# =========================================================
# INCOME CONCENTRATION RISK
# =========================================================

st.subheader("Income Concentration Risk")

top_income = income_df.head(5)
top_income_share = top_income["annual_income"].sum() / annual_income * 100

st.metric("Top 5 Income Share", f"{top_income_share:.2f}%")

if top_income_share > 60:
    st.error("High income concentration risk")
elif top_income_share > 40:
    st.warning("Moderate income concentration")
else:
    st.success("Healthy income diversification")

st.divider()

# =========================================================
# FORWARD INCOME PROJECTION (12 MONTHS)
# =========================================================

st.subheader("Forward Income Projection (12 Months)")

growth_rate = 0.03  # dividend growth assumption

future_income = annual_income * (1 + growth_rate)
future_monthly = future_income / 12

col1, col2 = st.columns(2)

col1.metric("Projected Annual Income", f"${future_income:,.2f}")
col2.metric("Projected Monthly Income", f"${future_monthly:,.2f}")

st.info("Assumes 3% annual dividend growth across portfolio.")

st.divider()

# =========================================================
# INCOME STABILITY SCORE (SIMPLE MODEL)
# =========================================================

st.subheader("Income Stability Score")

high_yield = df[df["yield"] > 0.08]
high_yield_risk = len(high_yield) / len(df)

score = 100 - (high_yield_risk * 60)

score = max(0, min(100, score))

st.metric("Stability Score", f"{score:.0f}/100")

if score > 80:
    st.success("Stable income profile")
elif score > 60:
    st.warning("Moderate income risk")
else:
    st.error("High-risk income profile")

st.divider()

# =========================================================
# RAW DATA
# =========================================================

with st.expander("Raw Portfolio Data"):
    st.dataframe(df, use_container_width=True)
