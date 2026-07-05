import json
import datetime
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
HISTORY_FILE = "northstar_history.json"

# -----------------------------
# SAMPLE DATA
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
        print("⚠️ No data.json found — using sample portfolio.\n")
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

    for h in holdings:
        value = h["shares"] * h["price"]
        total_value += value
        allocation[h["ticker"]] = value

    allocation_pct = {
        k: (v / total_value) * 100
        for k, v in allocation.items()
    }

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
# REPORT
# -----------------------------
def generate_report(analysis, performance=None):
    print("\nNORTHSTAR REPORT (v0.3)")
    print("-" * 45)

    print(f"Total Portfolio Value: ${analysis['total_value']:.2f}")
    print(f"Estimated Dividend Yield: {analysis['portfolio_yield'] * 100:.2f}%")

    print("\nAllocation Breakdown:")
    for ticker, pct in analysis["allocation_pct"].items():
        print(f"  {ticker}: {pct:.2f}%")

    # PERFORMANCE BLOCK (NEW)
    if performance:
        print("\nPERFORMANCE METRICS:")
        print(f"Start Value: ${performance['start']:.2f}")
        print(f"Current Value: ${performance['current']:.2f}")
        print(f"Total Return: {performance['return_pct']:.2f}%")
        print(f"Trend: {performance['trend']}")

    print("-" * 45)

# -----------------------------
# HISTORY
# -----------------------------
def load_history():
    path = Path(HISTORY_FILE)

    if not path.exists():
        return []

    with open(path, "r") as f:
        return json.load(f)

def save_history(entry):
    history = load_history()
    history.append(entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def create_snapshot(analysis):
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_value": analysis["total_value"],
        "yield": analysis["portfolio_yield"]
    }

# -----------------------------
# PERFORMANCE ENGINE (NEW)
# -----------------------------
def compute_performance(history):
    if not history:
        return None

    # sort by time
    history = sorted(history, key=lambda x: x["timestamp"])

    start = history[0]["total_value"]
    current = history[-1]["total_value"]

    if start == 0:
        return None

    return_pct = ((current - start) / start) * 100

    if return_pct > 1:
        trend = "📈 Uptrend"
    elif return_pct < -1:
        trend = "📉 Downtrend"
    else:
        trend = "➖ Flat"

    return {
        "start": start,
        "current": current,
        "return_pct": return_pct,
        "trend": trend
    }

# -----------------------------
# MAIN
# -----------------------------
def main():
    holdings = load_portfolio("data.json")
    analysis = analyze_portfolio(holdings)

    generate_report(analysis)

    snapshot = create_snapshot(analysis)
    save_history(snapshot)

    history = load_history()
    performance = compute_performance(history)

    print("\nSnapshot saved to history ✔")

    # reprint with performance (clean UX)
    generate_report(analysis, performance)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()
