import json
from pathlib import Path

# -----------------------------
# LOAD SCHWAB DATA (already parsed CSV → JSON-like list)
# -----------------------------
def load_portfolio(file_path="data.json"):
    path = Path(file_path)

    if not path.exists():
        print("❌ data.json not found")
        return []

    return json.load(open(path))["portfolio"]

# -----------------------------
# INCOME MODEL (BROKER-REALISTIC)
# -----------------------------

# conservative yield assumptions (based on typical Schwab holdings)
YIELD_MAP = {
    "REIT": 0.08,
    "ETFs & Closed End Funds": 0.10,
    "Equity": 0.02,
    "Cash and Money Market": 0.045
}

# ticker-specific overrides (important for your portfolio)
TICKER_YIELD_OVERRIDE = {
    "AGNC": 0.13,
    "ARCC": 0.10,
    "NLY": 0.11,
    "MPLX": 0.08,
    "EPD": 0.07,
    "JEPI": 0.07,
    "JEPQ": 0.09,
    "QYLD": 0.11,
    "QQQI": 0.10,
    "SPYI": 0.10,
    "FEPI": 0.12,
    "YYY": 0.12,
    "DIVO": 0.04,
    "HDV": 0.03,
    "VGK": 0.03,
    "VWO": 0.03,
    "SCHD": 0.03,
    "SWVXX": 0.045
}

# -----------------------------
# ANALYZE PORTFOLIO
# -----------------------------
def analyze(holdings):
    total_value = 0
    total_income = 0
    breakdown = []

    for h in holdings:
        ticker = h["ticker"]
        value = float(h.get("value", 0))
        asset_type = h.get("asset_type", "Equity")

        # determine yield
        if ticker in TICKER_YIELD_OVERRIDE:
            yield_rate = TICKER_YIELD_OVERRIDE[ticker]
        else:
            yield_rate = YIELD_MAP.get(asset_type, 0.02)

        income = value * yield_rate

        total_value += value
        total_income += income

        breakdown.append({
            "ticker": ticker,
            "value": value,
            "yield": yield_rate,
            "income": income
        })

    return {
        "total_value": total_value,
        "annual_income": total_income,
        "monthly_income": total_income / 12,
        "breakdown": breakdown
    }

# -----------------------------
# SIMPLE REPORT
# -----------------------------
def report(data):
    print("\nNORTHSTAR v1.0 (SCHWAB REAL INCOME MODEL)")
    print("-" * 50)
    print(f"Portfolio Value: ${data['total_value']:,.2f}")
    print(f"Annual Income:    ${data['annual_income']:,.2f}")
    print(f"Monthly Income:   ${data['monthly_income']:,.2f}")
    print("-" * 50)

    top = sorted(data["breakdown"], key=lambda x: x["income"], reverse=True)[:5]

    print("\nTop Income Contributors:")
    for t in top:
        print(f"{t['ticker']}: ${t['income']:.2f} (yield {t['yield']*100:.1f}%)")

# -----------------------------
# MAIN
# -----------------------------
def main():
    holdings = load_portfolio()
    if not holdings:
        return

    data = analyze(holdings)
    report(data)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    main() if not ticker or not shares:
                continue

            ticker = ticker.strip().upper()
            shares = float(shares)

            if shares <= 0:
                continue

            holdings.append({
                "ticker": ticker,
                "shares": shares
            })

        except Exception:
            continue

    return holdings
