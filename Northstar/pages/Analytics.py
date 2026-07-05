import streamlit as st
from collections import defaultdict

from core.parser import load_schwab_csv
from core.pricing import update_market_values
from core.dividends import enrich_income

st.set_page_config(page_title="Analytics", layout="wide")

st.title("📊 Portfolio Analytics")


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    holdings = load_schwab_csv("data/schwab.csv")
    holdings = update_market_values(holdings)
    holdings, total_income = enrich_income(holdings)
    return holdings


holdings = load_data()

total_value = sum(h["live_value"] for h in holdings)


# -----------------------------
# SECTOR BREAKDOWN
# -----------------------------
st.subheader("Asset Type Breakdown")

sector = defaultdict(float)

for h in holdings:
    sector[h.get("asset_type", "Unknown")] += h["live_value"]

sector_data = [
    {"Asset Type": k, "Value": v, "Weight %": (v / total_value) * 100}
    for k, v in sector.items()
]

st.dataframe(sorted(sector_data, key=lambda x: x["Value"], reverse=True), use_container_width=True)


st.divider()


# -----------------------------
# TOP POSITIONS (RISK CONCENTRATION)
# -----------------------------
st.subheader("Top Holdings by Value")

top_positions = sorted(holdings, key=lambda x: x["live_value"], reverse=True)[:10]

for h in top_positions:
    weight = (h["live_value"] / total_value) * 100

    st.write(
        f"**{h['ticker']}** → "
        f"${h['live_value']:,.2f} "
        f"({weight:.2f}% of portfolio)"
    )


st.divider()


# -----------------------------
# RISK METRICS
# -----------------------------
st.subheader("Risk & Diversification Metrics")

# concentration risk
top_weight = top_positions[0]["live_value"] / total_value if total_value else 0

if top_weight > 0.20:
    st.error("High concentration risk: top holding > 20%")

elif top_weight > 0.10:
    st.warning("Moderate concentration risk")

else:
    st.success("Well diversified by position size")


# income vs non-income proxy
income_tickers = {"JEPI","JEPQ","QYLD","QQQI","SPYI","AIPI","FEPI","HDV","DIVO","YYY"}

income_value = sum(
    h["live_value"]
    for h in holdings
    if h["ticker"] in income_tickers
)

income_ratio = income_value / total_value if total_value else 0

st.metric("Income Strategy Exposure", f"{income_ratio*100:.2f}%")


if income_ratio > 0.6:
    st.info("Portfolio is heavily income-focused.")
elif income_ratio > 0.3:
    st.info("Balanced income/growth mix.")
else:
    st.info("Growth-leaning allocation.")
