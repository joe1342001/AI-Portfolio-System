import streamlit as st
import pandas as pd

from core.history import load_history

st.set_page_config(page_title="History", layout="wide")

st.title("📅 Portfolio History")

history = load_history()

if not history:
    st.info("No history recorded yet.")
    st.stop()

summary = []

for day in history:
    summary.append({
        "Date": day["date"],
        "Portfolio Value": day["portfolio_value"],
        "Annual Income": day["annual_income"],
        "Monthly Income": day["monthly_income"]
    })

df = pd.DataFrame(summary)

st.dataframe(df, use_container_width=True)
