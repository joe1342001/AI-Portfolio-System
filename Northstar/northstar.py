import json
import datetime
from pathlib import Path
import yfinance as yf

# -----------------------------
# CONFIG
# -----------------------------
HISTORY_FILE = "northstar_history.json"

# -----------------------------
# PORTFOLIO
# -----------------------------
SAMPLE_PORTFOLIO = {
    "portfolio": [
        {"ticker": "AAPL", "shares": 10},
        {"ticker": "MSFT", "shares": 8},
        {"ticker": "SCHD", "shares": 25}
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
# PRICE ENGINE (stable)
# -----------------------------
def get_price(ticker):
    try:
        stock = yf.Ticker(ticker)

        # primary
        price = None
        if hasattr(stock, "fast_info"):
            price = stock.fast_info.get("lastPrice")

        # fallback
        if price is None:
            hist = stock.history(period="1d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]

        return float(price) if price is not None else 0.0

    except Exception:
        return 0.0

# -----------------------------
# DIVIDEND YIELD ENGINE (NEW)
# -----------------------------
def get_dividend_yield(ticker):
    try:
        stock = yf.Ticker(ticker)
        div = None

        if hasattr(stock, "info"):
            div = stock.info.get("dividendYield")

        if div is None:
            return 0.0

        return float(div)

    except Exception:
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

        enriched.append({
            "ticker": h["ticker"],
            "shares": h["shares"],
            "price": price,
            "value": value,
            "dividend_yield": get_dividend_yield(h["ticker"])
        })

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
# INTELLIGENCE LAYER
# -----------------------------
def intelligence(data):
    largest = max(data["allocation"].values()) if data["allocation"] else 0

    return {
        "largest_pct": largest,
        "holdings": len(data["holdings"]),
        "monthly_income": data["income"] / 12,
        "annual_income": data["income"]
    }

# -----------------------------
# HISTORY
# -----------------------------
def load_history():
    path = Path(HISTORY_FILE)
    if not path.exists():
        return []
    return json.load(open(path))

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
# PERFORMANCE
# -----------------------------
def performance(hist):
    if len(hist) < 2:
        return None

    hist = sorted(hist, key=lambda x: x["timestamp"])

    start = hist[0]["value"]
    end = hist[-1]["value"]

    if start == 0:
        return None

    pct = ((end - start) / start) * 100

    trend = "up" if pct > 1 else "down" if pct < -1 else "flat"

    return {
        "start": start,
        "end": end,
        "pct": pct,
        "trend": trend
    }

# -----------------------------
# CHAT ENGINE
# -----------------------------
def ask(question, data, intel, perf):
    q = question.lower()

    if "value" in q or "worth" in q:
        return f"Portfolio value: ${data['total']:.2f}"

    if "income" in q or "dividend" in q:
        return f"Estimated monthly income: ${intel['monthly_income']:.2f}"

    if "risk" in q or "divers" in q:
        if intel["largest_pct"] > 40:
            return "High concentration risk detected."
        return "Diversification looks reasonable."

    if "holdings" in q:
        return "Holdings: " + ", ".join([h["ticker"] for h in data["holdings"]])

    if "performance" in q or "return" in q:
        if perf:
            return f"Return: {perf['pct']:.2f}% ({perf['trend']})"
        return "Not enough history yet."

    return "Try asking about value, income, risk, holdings, or performance."

# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    holdings = load_portfolio("data.json")
    data = analyze(holdings)
    intel = intelligence(data)

    hist = load_history()
    perf = performance(hist)

    save_history(snapshot(data))

    print("\nNORTHSTAR v0.8 (CLEAN BUILD)")
    print("Type 'exit' to quit\n")

    while True:
        q = input("You: ")
        if q.lower() in ["exit", "quit"]:
            break

        print("NorthStar:", ask(q, data, intel, perf))

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()
