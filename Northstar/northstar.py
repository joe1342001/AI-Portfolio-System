import json
import datetime
from pathlib import Path
import matplotlib.pyplot as plt

# -----------------------------
# CONFIG
# -----------------------------
HISTORY_FILE = "northstar_history.json"
CHART_FILE = "northstar_chart.png"

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
# LOAD
# -----------------------------
def load_portfolio(file_path="data.json"):
    path = Path(file_path)

    if not path.exists():
        print("⚠️ Using sample portfolio.\n")
        return SAMPLE_PORTFOLIO["portfolio"]

    with open(path, "r") as f:
        return json.load(f)["portfolio"]

# -----------------------------
# ANALYSIS
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
    dividend_income = 0

    for h in holdings:
        value = h["shares"] * h["price"]
        weight = value / total_value

        weighted_yield += weight * h["dividend_yield"]
        dividend_income += value * h["dividend_yield"]

    return {
        "total_value": total_value,
        "allocation_pct": allocation_pct,
        "portfolio_yield": weighted_yield,
        "annual_dividend_income": dividend_income
    }

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
# PERFORMANCE
# -----------------------------
def compute_performance(history):
    if not history:
        return None

    history = sorted(history, key=lambda x: x["timestamp"])

    start = history[0]["total_value"]
    current = history[-1]["total_value"]

    if start == 0:
        return None

    pct = ((current - start) / start) * 100

    trend = "up" if pct > 1 else "down" if pct < -1 else "flat"

    return {
        "start": start,
        "current": current,
        "pct": pct,
        "trend": trend
    }

# -----------------------------
# INTELLIGENCE LAYER
# -----------------------------
def portfolio_intelligence(analysis, holdings):
    largest = max(analysis["allocation_pct"].values())
    num = len(holdings)

    return {
        "num_holdings": num,
        "largest_position_pct": largest,
        "annual_income": analysis["annual_dividend_income"],
        "monthly_income": analysis["annual_dividend_income"] / 12
    }

# -----------------------------
# 🧠 AI ANALYST ENGINE (NEW)
# -----------------------------
def ai_insight(analysis, performance, intel):
    insights = []

    # concentration risk
    if intel["largest_position_pct"] > 40:
        insights.append("High concentration risk: one position dominates your portfolio.")
    elif intel["largest_position_pct"] > 25:
        insights.append("Moderate concentration risk in top holding.")

    # diversification
    if intel["num_holdings"] < 5:
        insights.append("Low diversification: consider expanding holdings.")

    # income interpretation
    if intel["annual_income"] > 0:
        insights.append(f"Your portfolio generates about ${intel['monthly_income']:.2f}/month in dividend income.")

    # performance context
    if performance:
        if performance["pct"] > 10:
            insights.append("Strong positive performance trend over time.")
        elif performance["pct"] < -5:
            insights.append("Portfolio is under negative pressure over the observed period.")

        if performance["trend"] == "up":
            insights.append("Momentum is currently positive.")
        elif performance["trend"] == "down":
            insights.append("Momentum is currently negative.")

    return insights

# -----------------------------
# REPORT
# -----------------------------
def generate_report(analysis, performance=None, intel=None, insights=None):
    print("\nNORTHSTAR REPORT (v0.6)")
    print("-" * 55)

    print(f"Total Value: ${analysis['total_value']:.2f}")
    print(f"Dividend Yield: {analysis['portfolio_yield'] * 100:.2f}%")

    print("\nHoldings:")
    for k, v in analysis["allocation_pct"].items():
        print(f"  {k}: {v:.2f}%")

    print("\nIncome:")
    print(f"  Annual: ${analysis['annual_dividend_income']:.2f}")
    print(f"  Monthly: ${analysis['annual_dividend_income']/12:.2f}")

    if intel:
        print("\nPortfolio Intelligence:")
        print(f"  Holdings: {intel['num_holdings']}")
        print(f"  Largest Position: {intel['largest_position_pct']:.2f}%")

    if performance:
        print("\nPerformance:")
        print(f"  Return: {performance['pct']:.2f}%")
        print(f"  Trend: {performance['trend']}")

    if insights:
        print("\n🧠 AI Insights:")
        for i in insights:
            print(f"  - {i}")

    print("-" * 55)

# -----------------------------
# MAIN
# -----------------------------
def main():
    holdings = load_portfolio("data.json")
    analysis = analyze_portfolio(holdings)

    snapshot = create_snapshot(analysis)
    save_history(snapshot)

    history = load_history()
    performance = compute_performance(history)
    intel = portfolio_intelligence(analysis, holdings)
    insights = ai_insight(analysis, performance, intel)

    generate_report(analysis, performance, intel, insights)

    print("\nSnapshot saved ✔")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()
