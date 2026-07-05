import json
import datetime
from pathlib import Path

HISTORY_FILE = "northstar_history.json"

# -----------------------------
# SAMPLE DATA (fallback if no file)
# -----------------------------
SAMPLE_PORTFOLIO = {
    "portfolio": [
        {"ticker": "AAPL", "shares": 10, "price": 190.25, "dividend_yield": 0.0052},
        {"ticker": "MSFT", "shares": 8, "price": 410.10, "dividend_yield": 0.0070},
        {"ticker": "SCHD", "shares": 25, "price": 78.40, "dividend_yield": 0.0340}
    ]
}


# -----------------------------
# LOAD PORTFOLIO
# -----------------------------
def load_portfolio(file_path="data.json"):
    path = Path(file_path)

    if not path.exists():
        print("⚠️ No data.json found — using built-in sample portfolio.\n")
        return SAMPLE_PORTFOLIO["portfolio"]

    with open(path, "r") as f:
        data = json.load(f)

    return data["portfolio"]


# -----------------------------
# ANALYSIS ENGINE
# -----------------------------
def analyze_portfolio(holdings):
    total_value = 0
    allocation = {}

    # compute values
    for h in holdings:
        value = h["shares"] * h["price"]
        total_value += value
        allocation[h["ticker"]] = value

    # allocation %
    allocation_pct = {
        ticker: (value / total_value) * 100
        for ticker, value in allocation.items()
    }

    # weighted dividend yield
    weighted_yield = 0
    for h in holdings:
        weight = (h["shares"] * h["price"]) / total_value
        weighted_yield += weight * h["dividend_yield"]

    return {
        "total_value": total_value,
        "allocation_pct": allocation_pct,
        "portfolio_yield": weighted_yield
    }


# -----------------------------
# REPORT OUTPUT
# -----------------------------
def generate_report(analysis):
    print("\nNORTHSTAR REPORT")
    print("-" * 40)

    print(f"Total Portfolio Value: ${analysis['total_value']:.2f}")
    print(f"Estimated Dividend Yield: {analysis['portfolio_yield'] * 100:.2f}%\n")

    print("Allocation Breakdown:")
    for ticker, pct in analysis["allocation_pct"].items():
        print(f"  {ticker}: {pct:.2f}%")

    print("-" * 40)

def load_history():
    path = Path(HISTORY_FILE)

    if not path.exists():
        return []

    with open(path, "r") as f:
        return json.load(f)

def create_snapshot(analysis):
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_value": analysis["total_value"],
        "yield": analysis["portfolio_yield"]
    }

def main():
    holdings = load_portfolio("data.json")
    analysis = analyze_portfolio(holdings)

    generate_report(analysis)

    # NEW: create and save snapshot
    snapshot = create_snapshot(analysis)
    save_history(snapshot)

    print("\nSnapshot saved to history ✔")

def save_history(entry):
    history = load_history()
    history.append(entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# -----------------------------
# MAIN
# -----------------------------
def main():
    holdings = load_portfolio("data.json")
    analysis = analyze_portfolio(holdings)
    generate_report(analysis)


if __name__ == "__main__":
    main()
