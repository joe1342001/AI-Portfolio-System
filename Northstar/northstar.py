import json
import datetime
from pathlib import Path
import yfinance as yf

# -----------------------------
# CONFIG
# -----------------------------
HISTORY_FILE = "northstar_history.json"
PRICE_CACHE_FILE = "northstar_price_cache.json"

# -----------------------------
# PORTFOLIO DATA
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
# PRICE ENGINE (simplified v0.8)
# -----------------------------
def get_price(ticker):
    try:
        return float(yf.Ticker(ticker).fast_info["lastPrice"])
    except:
        return 0.0

# -----------------------------
# ANALYSIS
# -----------------------------
def analyze(holdings):
    total = 0
    enriched = []
    allocation = {}

    for h in holdings:
        price = get_price(h["ticker"])
        value = price * h["shares"]

        enriched.append({**h, "price": price, "value": value})

        total += value
        allocation[h["ticker"]] = value

    allocation_pct = {
        k: (v / total) * 100 if total > 0 else 0
        for k, v in allocation.items()
    }

    income = sum(h["value"] * h["dividend_yield"] for h in enriched)

    return {
        "total": total,
        "holdings": enriched,
        "allocation": allocation_pct,
        "income": income
    }

# -----------------------------
# INTELLIGENCE
# -----------------------------
def intelligence(data):
    largest = max(data["allocation"].values()) if data["allocation"] else 0

    return {
        "largest_pct": largest,
        "holdings": len(data["holdings"]),
        "monthly_income": data["income"] / 12
    }

# -----------------------------
# HISTORY
# -----------------------------
def load_history():
    p = Path(HISTORY_FILE)
    if not p.exists():
        return []
    return json.load(open(p))

def save_history(entry):
    hist = load_history()
    hist.append(entry)
    json.dump(hist, open(HISTORY_FILE, "w"), indent=2)

def snapshot(data):
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "value": data["total"]
    }

# -----------------------------
# SIMPLE PERFORMANCE
# -----------------------------
def performance(hist):
    if len(hist) < 2:
        return None

    hist = sorted(hist, key=lambda x: x["timestamp"])

    start = hist[0]["value"]
    end = hist[-1]["value"]

    pct = ((end - start) / start) * 100 if start else 0

    trend = "up" if pct > 1 else "down" if pct < -1 else "flat"

    return {"start": start, "end": end, "pct": pct, "trend": trend}

# -----------------------------
# 🧠 CHAT ENGINE (NEW CORE FEATURE)
# -----------------------------
def ask_northstar(question, data, intel, perf):
    q = question.lower()

    # portfolio value
    if "value" in q or "worth" in q:
        return f"Your portfolio is worth about ${data['total']:.2f}"

    # income
    if "income" in q or "dividend" in q:
        return f"Estimated monthly income: ${intel['monthly_income']:.2f}"

    # concentration risk
    if "risk" in q or "divers" in q:
        if intel["largest_pct"] > 40:
            return "High concentration risk: one holding dominates your portfolio."
        return "Your portfolio is reasonably diversified."

    # performance
    if "performance" in q or "return" in q:
        if perf:
            return f"Return: {perf['pct']:.2f}% ({perf['trend']})"
        return "Not enough history yet."

    # holdings
    if "holdings" in q or "stocks" in q:
        names = ", ".join([h["ticker"] for h in data["holdings"]])
        return f"You hold: {names}"

    # default
    return "I can help with value, income, risk, performance, or holdings."

# -----------------------------
# MAIN LOOP (CHAT MODE)
# -----------------------------
def main():
    holdings = load_portfolio("data.json")
    data = analyze(holdings)
    intel = intelligence(data)

    hist = load_history()
    perf = performance(hist)

    save_history(snapshot(data))

    print("\nNORTHSTAR v0.8 — AI PORTFOLIO ASSISTANT")
    print("Type a question (or 'exit')\n")

    while True:
        q = input("You: ")

        if q.lower() in ["exit", "quit"]:
            break

        response = ask_northstar(q, data, intel, perf)
        print("NorthStar:", response)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()
