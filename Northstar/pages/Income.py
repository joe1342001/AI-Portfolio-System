import streamlit as st

from core.parser import load_schwab_csv
from core.pricing import update_market_values
from core.dividends import enrich_income

st.set_page_config(page_title="Income", layout="wide")

st.title("💰 Dividend Income Dashboard")


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    holdings = load_schwab_csv("data/schwab.csv")
    holdings = update_market_values(holdings)
    holdings, total_income = enrich_income(holdings)
    return holdings, total_income


holdings, total_income = load_data()

monthly_income = total_income / 12


# -----------------------------
# SUMMARY METRICS
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Annual Income", f"${total_income:,.2f}")

with col2:
    st.metric("Monthly Income", f"${monthly_income:,.2f}")

with col3:
    yield_on_portfolio = total_income / sum(h["live_value"] for h in holdings)
    st.metric("Yield", f"{yield_on_portfolio*100:.2f}%")


st.divider()


# -----------------------------
# INCOME BY HOLDING
# -----------------------------
st.subheader("Income by Holding")

income_table = []

for h in holdings:
    income_table.append({
        "Ticker": h["ticker"],
        "Value": h["live_value"],
        "Yield": f"{h['yield']*100:.2f}%",
        "Annual Income": h["annual_income"],
        "Monthly Income": h["monthly_income"],
    })

income_table = sorted(income_table, key=lambda x: x["Annual Income"], reverse=True)

st.dataframe(income_table, use_container_width=True)


st.divider()


# -----------------------------
# TOP INCOME CONTRIBUTORS
# -----------------------------
st.subheader("Top Income Contributors")

top = income_table[:10]

for h in top:
    st.write(
        f"**{h['Ticker']}** → "
        f"${h['Annual Income']:,.2f}/yr "
        f"(${h['Monthly Income']:,.2f}/mo)"
    )


st.divider()


# -----------------------------
# INSIGHTS
# -----------------------------
st.subheader("AI Income Insights")

if yield_on_portfolio > 0.08:
    st.success("High-income portfolio (above 8% yield).")

elif yield_on_portfolio > 0.05:
    st.info("Moderate-income portfolio.")

else:
    st.warning("Low-income portfolio — growth-oriented allocation detected.")

# concentration risk
top_weight = income_table[0]["Annual Income"] / total_income if total_income else 0

if top_weight > 0.20:
    st.warning("Income concentration risk: top holding exceeds 20% of income.")
