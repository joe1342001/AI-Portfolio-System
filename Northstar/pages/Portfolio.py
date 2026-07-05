import streamlit as st

st.set_page_config(
    page_title="NorthStar",
    page_icon="⭐",
    layout="wide"
)

st.title("⭐ NorthStar")

st.subheader("Personal AI Portfolio System")

st.write(
    """
Welcome to NorthStar.

Use the navigation panel on the left to explore:

- 📈 Portfolio
- 💰 Income
- 🧮 Retirement
- 📊 Analytics
- ⚙ Settings
"""
)

st.info("NorthStar v3.0 is under active development.")
