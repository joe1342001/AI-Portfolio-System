import json
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import yfinance as yf

# -----------------------------
# CONFIG
# -----------------------------
HISTORY_FILE = "northstar_history.json"
CHART_FILE = "northstar_chart.png"

# -----------------------------
# SAMPLE PORTFOLIO (no prices needed anymore)
# -----------------------------
SAMPLE_PORTFOLIO = {
    "portfolio": [
        {"ticker": "AAPL", "shares": 10, "dividend_yield": 0.0052},
        {"ticker": "MSFT", "shares": 8, "dividend_yield": 0.0070},
        {"ticker": "SCHD", "shares": 25, "dividend_yield": 0.0340}
    ]
}

# -----------------------------
# LOAD PORTFOLIO
# -----------------------------
def load_portfolio(file_path="data.json"):
    path = Path(file_path)

    if not path.exists():
        print("⚠️ Using sample portfolio.\n")
        return SAMPLE_PORTFOLIO["portfolio"]

    with open(path, "r") as f:
        return json.load(f)["portfolio"]

# -----------------------------
# LIVE PRICE ENGINE (NEW)
# -----------------------------
def get_live_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.fast_info["lastPrice"]
        return float(price)
    except Exception:
        print(f"⚠️ Price fetch failed for {ticker}, using fallback 0")
        return 0.0

# -----------------------------
# ANALYSIS ENGINE (UPDATED)
# -----------------------------
def analyze_portfolio(holdings):
    total_value = 0
    allocation = {}

    enriched_holdings = []

    for h in holdings:
        price = get_live_price(h["ticker"])
        value = h["shares"] * price

        total_value += value
        allocation[h["ticker"]] = value

        enriched_holdings.append({
            **h,
            "price": price,
            "value": value
        })

    allocation_pct = {
        k: (v / total_value) * 100 if total_value > 0 else 0
        for k, v in allocation.items()
    }

    weighted_yield = 0
    dividend_income = 0

    for h in enriched_holdings:
        weight = h["value"] / total_value if total_value > 0 else 0

        weighted_yield += weight * h["dividend_yield"]
        dividend_income += h["value"] * h["dividend_yield"]

    return {
        "total_value": total_value,
        "allocation_pct": allocation_pct,
        "portfolio_yield": weighted_yield,
        "annual_dividend_income": dividend_income,
        "holdings": enriched_holdings
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
# PERFORMANCE ENGINE
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
def portfolio_intelligence(analysis):
    holdings = analysis["holdings"]

    largest = max(analysis["allocation_pct"].values()) if holdings else 0

    return {
        "num_holdings": len(holdings),
        "largest_position_pct": largest,
        "annual_income": analysis["annual_dividend_income"],
        "monthly_income": analysis["annual_dividend_income"] / 12
    }

# -----------------------------
# AI INSIGHTS
# -----------------------------
def ai_insight(analysis, performance, intel):
    insights = []

    if intel["largest_position_pct"] > 40:
        insights.append("High concentration risk in a single asset.")

    if intel["num_holdings"] < 5:
        insights.append("Portfolio is lightly diversified.")

    insights.append(
        f"Estimated income: ${intel['monthly_income']:.2f}/month from dividends."
    )

    if performance:
        if performance["pct"] > 5:
            insights.append("Strong positive trend over time.")
        elif performance["pct"] < -5:
            insights.append("Portfolio under negative pressure.")

    return insights

# -----------------------------
# REPORT
# -----------------------------
def generate_report(analysis, performance=None, intel=None, insights=None):
    print("\nNORTHSTAR REPORT (v0.7)")
    print("-" * 60)

    print(f"Total Value: ${analysis['total_value']:.2f}")
    print(f"Dividend Yield: {analysis['portfolio_yield'] * 100:.2f}%")

    print("\nHoldings (Live Prices):")
    for h in analysis["holdings"]:
        print(f"  {h['ticker']}: {h['shares']} shares @ ${h['price']:.2f} → ${h['value']:.2f}")

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
        print("\nAI Insights:")
        for i in insights:
            print(f"  - {i}")

    print("-" * 60)

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
    intel = portfolio_intelligence(analysis)
    insights = ai_insight(analysis, performance, intel)

    generate_report(analysis, performance, intel, insights)

    print("\nSnapshot saved ✔")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()
