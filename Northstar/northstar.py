import json
import csv
import datetime
from pathlib import Path
import yfinance as yf

# -----------------------------
# CONFIG
# -----------------------------
HISTORY_FILE = "northstar_history.json"
SCHWAB_FILE = "schwab.csv"

# -----------------------------
# PRICE ENGINE (live, optional)
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

        return float(price) if price else 0.0

    except Exception:
        return 0.0

# -----------------------------
# SCHWAB CSV IMPORT (CORE)
# -----------------------------
def import_schwab(csv_file):
    path = Path(csv_file)

    if not path.exists():
        print(f"❌ Schwab file not found: {csv_file}")
        return []

    holdings = []

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            print("❌ Invalid CSV format")
            return []

        def find(col_options):
            for c in reader.fieldnames:
                for opt in col_options:
                    if opt.lower() in c.lower():
                        return c
            return None

        symbol_col = find(["symbol", "ticker"])
        qty_col = find(["quantity", "shares", "qty"])
        cost_col = find(["cost", "cost basis"])

        if not symbol_col or not qty_col:
            print("❌ Could not detect required Schwab columns")
            print("Found:", reader.fieldnames)
            return []

        for row in reader:
            try:
                ticker = row[symbol_col].strip().upper()
                shares = float(row[qty_col])

                if not ticker or shares <= 0:
                    continue

                cost = None
                if cost_col and row.get(cost_col):
                    try:
                        cost = float(row[cost_col])
                    except:
                        cost = None

                holdings.append({
                    "ticker": ticker,
                    "shares": shares,
                    "cost_basis": cost
                })

            except Exception:
                continue

    return holdings

# -----------------------------
# ANALYSIS ENGINE (BROKER-BASED)
# -----------------------------
def analyze(holdings):
    total_value = 0
    total_cost = 0
    enriched = []
    allocation = {}

    for h in holdings:
        ticker = h["ticker"]
        shares = h["shares"]

        price = get_price(ticker)
        value = price * shares

        cost = h.get("cost_basis")
        if cost:
            total_cost += cost

        total_value += value
        allocation[ticker] = value

        enriched.append({
            **h,
            "price": price,
            "value": value
        })

    allocation_pct = {
        k: (v / total_value) * 100 if total_value > 0 else 0
        for k, v in allocation.items()
    }

    return {
        "total_value": total_value,
        "total_cost": total_cost,
        "holdings": enriched,
        "allocation": allocation_pct
    }

# -----------------------------
# PERFORMANCE (REAL RETURN IF COST AVAILABLE)
# -----------------------------
def performance(data):
    if data["total_cost"] > 0:
        return ((data["total_value"] - data["total_cost"]) / data["total_cost"]) * 100
    return None

# -----------------------------
# SIMPLE INTELLIGENCE
# -----------------------------
def intelligence(data, perf):
    largest = max(data["allocation"].values()) if data["allocation"] else 0

    return {
        "holdings": len(data["holdings"]),
        "largest_pct": largest,
        "return_pct": perf
    }

# -----------------------------
# CHAT ENGINE
# -----------------------------
def ask(q, data, intel):
    q = q.lower()

    if "value" in q or "worth" in q:
        return f"Portfolio value: ${data['total_value']:.2f}"

    if "return" in q or "performance" in q:
        if intel["return_pct"] is not None:
            return f"Total return: {intel['return_pct']:.2f}%"
        return "Return unavailable (missing cost basis)."

    if "holdings" in q:
        return "Holdings: " + ", ".join([h["ticker"] for h in data["holdings"]])

    if "risk" in q:
        if intel["largest_pct"] > 40:
            return "High concentration risk detected."
        return "Diversification looks reasonable."

    return "Ask: value, return, holdings, risk."

# -----------------------------
# MAIN
# -----------------------------
def main():
    holdings = import_schwab(SCHWAB_FILE)

    if not holdings:
        print("No holdings loaded.")
        return

    data = analyze(holdings)
    perf = performance(data)
    intel = intelligence(data, perf)

    print("\nNORTHSTAR v1.0 (BROKER-GRADE MODE)")
    print("Type 'exit' to quit\n")

    while True:
        q = input("You: ")
        if q.lower() in ["exit", "quit"]:
            break

        print("NorthStar:", ask(q, data, intel))

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main()
