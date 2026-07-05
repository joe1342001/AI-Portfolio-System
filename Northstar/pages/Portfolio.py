import streamlit as st

from core.parser import load_schwab_csv
from core.pricing import update_market_values, portfolio_value
from core.dividends import enrich_income

st.set_page_config(page_title="Portfolio", layout="wide")

st.title("📈 Portfolio Overview")


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

total_value = portfolio_value(holdings)
monthly_income = total_income / 12


# -----------------------------
# SUMMARY CARDS
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Portfolio Value", f"${total_value:,.2f}")

with col2:
    st.metric("Annual Income", f"${total_income:,.2f}")

with col3:
    st.metric("Monthly Income", f"${monthly_income:,.2f}")


st.divider()


# -----------------------------
# HOLDINGS TABLE
# -----------------------------
st.subheader("Holdings")

display_data = []

for h in holdings:
    display_data.append({
        "Ticker": h["ticker"],
        "Shares": h["shares"],
        "Price": h["live_price"],
        "Value": h["live_value"],
        "Yield": f"{h['yield']*100:.2f}%",
        "Annual Income": h["annual_income"],
    })

st.dataframe(display_data, use_container_width=True)


st.divider()


# -----------------------------
# TOP HOLDINGS
# -----------------------------
st.subheader("Top Income Holdings")

top = sorted(holdings, key=lambda x: x["annual_income"], reverse=True)[:10]

for h in top:
    st.write(
        f"**{h['ticker']}** — "
        f"${h['annual_income']:,.2f} annual income "
        f"({h['yield']*100:.2f}%)"
    )
