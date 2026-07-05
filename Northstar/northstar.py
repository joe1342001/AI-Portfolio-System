import json
import datetime
from pathlib import Path
import yfinance as yf
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
HISTORY_FILE = "northstar_history.json"

# -----------------------------
# SAMPLE PORTFOLIO
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
# PRICE ENGINE (robust)
# -----------------------------
def get_price(ticker):
    try:
        stock = yf.Ticker(ticker)

        price = None

        if hasattr(stock, "fast_info"):
            price = stock.fast_info.get("lastPrice")

        if price is None:
            hist = stock.history(period="5d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]

        return float(price) if price is not None else 0.0

    except Exception:
        return 0.0

# -----------------------------
# DIVIDEND ENGINE (FIXED + SAFE)
# -----------------------------
def get_annual_dividend_per_share(ticker):
    try:
        stock = yf.Ticker(ticker)
        divs = stock.dividends

        if divs is None or divs.empty:
            return 0.0

        # ensure clean datetime index
        divs = divs.copy()
        divs.index = pd.to_datetime(divs.index)

        one_year_ago = divs.index.max() - pd.Timedelta(days=365)

        last_year_divs = divs[divs.index >= one_year_ago]

        total = last_year_divs.sum()

        if pd.isna(total):
            return 0.0

        return float(total)

    except Exception:
        return 0.0

# -----------------------------
# ANALYSIS ENGINE
# -----------------------------
def analyze(holdings):
    total_value = 0
    enriched = []
    allocation = {}

    for h in holdings:
        ticker = h["ticker"]
        shares = h["shares"]

        price = get_price(ticker)
        value = price * shares

        div_per_share = get_annual_dividend_per_share(ticker)

        income = shares * div_per_share

        enriched.append({
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "value": value,
            "div_per_share": div_per_share,
            "income": income
        })

        total_value += value
        allocation[ticker] = value

    allocation_pct = {
        k: (v / total_value) * 100 if total_value > 0 else 0
        for k, v in allocation.items()
    }

    total_income = sum(h["income"] for h in enriched)

    return {
        "total": total_value,
        "holdings": enriched,
        "allocation": allocation_pct,
        "income": total_income
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

    return "Ask: value, income, risk, holdings, performance."

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

    print("\nNORTHSTAR v0.9 (STABLE INCOME ENGINE)")
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
