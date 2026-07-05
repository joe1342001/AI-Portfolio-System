import json
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("data/history.json")


def load_history():
    """Load portfolio history from disk."""
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_snapshot(holdings, total_value, annual_income):
    """Append a new snapshot if today's snapshot doesn't already exist."""
    history = load_history()

    today = datetime.now().strftime("%Y-%m-%d")

    # Only one snapshot per day
    if history and history[-1]["date"] == today:
        history[-1] = build_snapshot(holdings, total_value, annual_income)
    else:
        history.append(build_snapshot(holdings, total_value, annual_income))

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def build_snapshot(holdings, total_value, annual_income):
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "portfolio_value": round(total_value, 2),
        "annual_income": round(annual_income, 2),
        "monthly_income": round(annual_income / 12, 2),
        "holdings": [
            {
                "ticker": h["ticker"],
                "shares": h["shares"],
                "value": round(h["live_value"], 2),
                "income": round(h["annual_income"], 2)
            }
            for h in holdings
        ]
    }
