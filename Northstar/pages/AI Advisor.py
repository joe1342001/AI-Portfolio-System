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

st.set_page_config(page_title="NorthStar AI Advisor", layout="wide")
st.title("🤖 NorthStar AI Advisor")

# =========================================================
# LOAD PORTFOLIO
# =========================================================

holdings = load_portfolio()

if not holdings:
    st.warning("No portfolio data found.")
    st.stop()

df = pd.DataFrame(holdings)

# =========================================================
# CORE METRICS
# =========================================================

total_value = df["value"].sum()
total_income = df["annual_income"].sum()
yield_pct = (total_income / total_value) * 100 if total_value else 0

# =========================================================
# AI SUMMARY HEADER
# =========================================================

st.subheader("📊 Portfolio Summary")

st.metric("Portfolio Value", f"${total_value:,.2f}")
st.metric("Annual Income", f"${total_income:,.2f}")
st.metric("Yield", f"{yield_pct:.2f}%")

st.divider()

# =========================================================
# CONCENTRATION ANALYSIS
# =========================================================

st.subheader("⚠️ Concentration Analysis")

df["weight"] = df["value"] / total_value * 100

top_holdings = df.sort_values("weight", ascending=False).head(5)

top_weight = top_holdings["weight"].sum()

st.write(f"Top 5 holdings represent **{top_weight:.2f}%** of portfolio")

if top_weight > 60:
    st.error("High concentration risk detected (>60% in top 5 holdings)")
elif top_weight > 40:
    st.warning("Moderate concentration risk")
else:
    st.success("Well diversified concentration profile")

st.dataframe(
    top_holdings[["ticker", "value", "weight", "annual_income"]],
    use_container_width=True
)

st.divider()

# =========================================================
# INCOME QUALITY ANALYSIS
# =========================================================

st.subheader("💰 Income Quality")

income_df = df.sort_values("annual_income", ascending=False)

yield_by_asset = df.groupby("asset_type")["annual_income"].sum()

st.bar_chart(yield_by_asset)

reit_exposure = df[df["asset_type"].str.contains("reit", case=False, na=False)]["value"].sum()
reit_pct = (reit_exposure / total_value) * 100 if total_value else 0

st.write(f"REIT exposure: **{reit_pct:.2f}%**")

if reit_pct > 40:
    st.warning("High REIT concentration risk")
elif reit_pct > 20:
    st.info("Moderate REIT exposure")
else:
    st.success("Balanced REIT exposure")

st.divider()

# =========================================================
# DIVIDEND DEPENDENCY RISK
# =========================================================

st.subheader("📉 Dividend Dependency Risk")

high_yield = df[df["yield"] > 0.08] if "yield" in df.columns else pd.DataFrame()

high_yield_pct = (high_yield["value"].sum() / total_value) * 100 if not high_yield.empty else 0

st.write(f"High-yield exposure (>8%): **{high_yield_pct:.2f}%**")

if high_yield_pct > 50:
    st.error("Portfolio heavily dependent on high-yield assets (risk of dividend cuts)")
elif high_yield_pct > 25:
    st.warning("Moderate income risk exposure")
else:
    st.success("Low dependency on high-yield risk assets")

st.divider()

# =========================================================
# SIMPLE AI INSIGHT ENGINE (RULE BASED)
# =========================================================

st.subheader("🧠 AI Insights")

insights = []

# Yield check
if yield_pct < 3:
    insights.append("Portfolio yield is low — income strategy is underweighted.")
elif yield_pct > 8:
    insights.append("Yield is high — monitor for sustainability risk.")

# Diversification check
if top_weight > 60:
    insights.append("Portfolio is highly concentrated in a few positions.")

# REIT exposure
if reit_pct > 40:
    insights.append("Overexposure to REITs increases interest rate sensitivity.")

# Income stability
if high_yield_pct > 50:
    insights.append("Income may be unstable due to high-yield dependency.")

if not insights:
    insights.append("Portfolio structure appears balanced with no major risks detected.")

for i, ins in enumerate(insights, 1):
    st.write(f"{i}. {ins}")

st.divider()

# =========================================================
# RAW DATA VIEW (DEBUG / POWER USERS)
# =========================================================

with st.expander("View Full Portfolio Data"):
    st.dataframe(df, use_container_width=True)
