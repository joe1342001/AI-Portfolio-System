import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Settings", layout="wide")

st.title("⚙ Settings")


# -----------------------------
# CONFIG FILE
# -----------------------------
CONFIG_PATH = Path("data/settings.json")


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    return {
        "expected_return": 0.065,
        "inflation": 0.03,
        "retirement_age": 65,
        "target_monthly_income": 5000
    }


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


config = load_config()


# -----------------------------
# UI CONTROLS
# -----------------------------
st.subheader("Portfolio Assumptions")

expected_return = st.slider(
    "Expected Annual Return",
    0.02, 0.12,
    config["expected_return"]
)

inflation = st.slider(
    "Inflation Rate",
    0.00, 0.08,
    config["inflation"]
)


st.subheader("Retirement Goals")

retirement_age = st.selectbox(
    "Default Retirement Age",
    [60, 62, 65, 70],
    index=[60, 62, 65, 70].index(config["retirement_age"])
)

target_income = st.number_input(
    "Target Monthly Income",
    value=config["target_monthly_income"]
)


# -----------------------------
# SAVE BUTTON
# -----------------------------
if st.button("Save Settings"):

    config["expected_return"] = expected_return
    config["inflation"] = inflation
    config["retirement_age"] = retirement_age
    config["target_monthly_income"] = target_income

    save_config(config)

    st.success("Settings saved successfully.")
