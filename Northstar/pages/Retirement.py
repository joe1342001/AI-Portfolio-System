import streamlit as st
from core.parser import load_schwab_csv
from core.pricing import update_market_values
from core.dividends import enrich_income

st.set_page_config(page_title="Retirement", layout="wide")

st.title("🧮 Retirement Simulator")


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    holdings = load_schwab_csv("data/schwab.csv")
    holdings = update_market_values(holdings)
    holdings, total_income = enrich_income(holdings)
    return holdings, total_income


holdings, base_income = load_data()

portfolio_value = sum(h["live_value"] for h in holdings)


# -----------------------------
# USER INPUTS
# -----------------------------
st.subheader("Inputs")

col1, col2, col3 = st.columns(3)

with col1:
    current_age = st.number_input("Current Age", value=55)

with col2:
    retirement_age = st.selectbox("Retirement Age", [60, 62, 65, 70])

with col3:
    years = retirement_age - current_age


col4, col5 = st.columns(2)

with col4:
    weekly_contribution = st.number_input("Weekly Contribution ($)", value=250)

with col5:
    expected_return = st.slider("Expected Annual Return (%)", 3.0, 10.0, 6.5) / 100


dividend_reinvest = st.checkbox("Reinvest Dividends", value=True)


st.divider()


# -----------------------------
# PROJECTIONS
# -----------------------------

def project_future_value(pv, contribution, years, rate):
    weekly_rate = rate / 52
    value = pv

    for _ in range(int(years * 52)):
        value *= (1 + weekly_rate)
        value += contribution

    return value


future_value = project_future_value(
    portfolio_value,
    weekly_contribution,
    years,
    expected_return
)


# dividend yield (derived from current income)
current_yield = base_income / portfolio_value if portfolio_value else 0

if dividend_reinvest:
    projected_income = future_value * current_yield
else:
    projected_income = future_value * (current_yield * 0.6)


monthly_income = projected_income / 12


# -----------------------------
# RESULTS
# -----------------------------
st.subheader("Projection Results")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Projected Portfolio", f"${future_value:,.2f}")

with col2:
    st.metric("Annual Income", f"${projected_income:,.2f}")

with col3:
    st.metric("Monthly Income", f"${monthly_income:,.2f}")


st.divider()


# -----------------------------
# RETIREMENT READINESS
# -----------------------------
st.subheader("Retirement Readiness")

target_income = st.number_input("Desired Monthly Income", value=5000)

if monthly_income >= target_income:
    st.success("On track to meet your retirement goal.")
else:
    gap = target_income - monthly_income
    st.warning(f"You are short by ${gap:,.2f} per month.")


st.divider()


# -----------------------------
# SIMPLE INSIGHT ENGINE
# -----------------------------
st.subheader("AI Insight")

if years < 10:
    st.info("Short time horizon increases risk sensitivity.")

if expected_return > 8:
    st.warning("Return assumption is aggressive.")

if weekly_contribution > 500:
    st.info("High contribution rate significantly accelerates compounding.")

if current_yield > 0.07:
    st.success("Portfolio is income-efficient for retirement.")
