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

st.set_page_config(page_title="NorthStar Retirement", layout="wide")
st.title("🏁 Retirement Planner")

# =========================================================
# LOAD PORTFOLIO
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

# =========================================================
# USER INPUTS
# =========================================================

st.subheader("Assumptions")

col1, col2, col3 = st.columns(3)

with col1:
    current_age = st.number_input("Current Age", 18, 100, 55)

with col2:
    retirement_age = st.number_input("Retirement Age", 40, 100, 65)

with col3:
    monthly_expenses = st.number_input("Monthly Expenses ($)", 500, 50000, 5000)

years_to_retire = retirement_age - current_age

# =========================================================
# PROJECTIONS (SIMPLE BUT STABLE MODEL)
# =========================================================

# Conservative assumptions (can upgrade later)
growth_rate = 0.06   # 6% portfolio growth
income_growth = 0.03 # dividend growth

future_value = portfolio_value * ((1 + growth_rate) ** years_to_retire)
future_income = annual_income * ((1 + income_growth) ** years_to_retire)

future_monthly_income = future_income / 12

# =========================================================
# OUTPUT METRICS
# =========================================================

st.subheader("Retirement Projection")

col1, col2, col3 = st.columns(3)

col1.metric("Projected Portfolio Value", f"${future_value:,.2f}")
col2.metric("Projected Annual Income", f"${future_income:,.2f}")
col3.metric("Projected Monthly Income", f"${future_monthly_income:,.2f}")

st.divider()

# =========================================================
# RETIREMENT READINESS
# =========================================================

st.subheader("Retirement Readiness")

if future_monthly_income >= monthly_expenses:
    st.success("✅ You are on track for retirement income coverage")
else:
    gap = monthly_expenses - future_monthly_income
    st.error(f"❌ Income gap of ${gap:,.2f} per month")

st.divider()

# =========================================================
# CURRENT POSITION SUMMARY
# =========================================================

st.subheader("Current Portfolio Snapshot")

col1, col2, col3 = st.columns(3)

col1.metric("Portfolio Value", f"${portfolio_value:,.2f}")
col2.metric("Annual Income", f"${annual_income:,.2f}")
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

# =========================================================
# ASSUMPTIONS NOTE
# =========================================================

st.info(
    "Projection assumes constant contributions are NOT included and uses "
    "simple growth models (6% capital growth, 3% dividend growth)."
)
