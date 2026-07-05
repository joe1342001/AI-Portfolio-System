import json
from pathlib import Path
import re

# =========================================================
# SCHWAB PARSER (ROBUST + YOUR FORMAT)
# =========================================================

def load_schwab(file_path="schwab.csv"):
    path = Path(file_path)

    if not path.exists():
        print("❌ File not found:", file_path)
        return []

    lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    holdings = []

    # find CSV header row (your Schwab format)
    header_index = None
    for i, line in enumerate(lines):
        if line.startswith('"Symbol"') and '"Qty' in line:
            header_index = i
            break

    if header_index is None:
        print("❌ Could not locate Schwab CSV header row")
        return []

    headers = [h.strip().strip('"') for h in lines[header_index].split('","')]

    def col(name):
        for i, h in enumerate(headers):
            if name.lower() in h.lower():
                return i
        return None

    i_symbol = col("Symbol")
    i_qty = col("Qty")
    i_value = col("Mkt Val")
    i_asset = col("Asset Type")

    for line in lines[header_index + 1:]:
        if not line.startswith('"'):
            continue

        parts = [p.strip().strip('"') for p in line.split('","')]

        try:
            ticker = parts[i_symbol].strip().upper()

            qty = float(parts[i_qty].replace(",", ""))

            if qty <= 0:
                continue

            value = 0.0
            if i_value is not None and i_value < len(parts):
                value = parts[i_value].replace("$", "").replace(",", "")
                value = float(value) if value else 0.0

            asset_type = parts[i_asset] if i_asset and i_asset < len(parts) else "Equity"

            holdings.append({
                "ticker": ticker,
                "shares": qty,
                "value": value,
                "asset_type": asset_type
            })

        except Exception:
            continue

    return holdings


# =========================================================
# INCOME ENGINE (SCHWAB REALISTIC MODEL)
# =========================================================

YIELD_MAP = {
    "Equity": 0.02,
    "ETFs & Closed End Funds": 0.08,
    "Cash and Money Market": 0.045,
    "REIT": 0.10
}

TICKER_YIELD = {
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
    "SWVXX": 0.045,
    "HDV": 0.03,
    "VGK": 0.03,
    "VWO": 0.03
}


def calculate_income(holdings):
    total_income = 0
    total_value = 0

    for h in holdings:
        ticker = h["ticker"]
        value = float(h.get("value", 0))
        asset_type = h.get("asset_type", "Equity")

        total_value += value

        if ticker in TICKER_YIELD:
            y = TICKER_YIELD[ticker]
        else:
            y = YIELD_MAP.get(asset_type, 0.02)

        total_income += value * y

    return total_value, total_income


# =========================================================
# REPORT
# =========================================================

def report(holdings, total_value, income):
    monthly = income / 12

    print("\nNORTHSTAR v1.1 — SCHWAB INCOME ENGINE")
    print("-" * 55)

    print(f"Portfolio Value: ${total_value:,.2f}")
    print(f"Annual Income:   ${income:,.2f}")
    print(f"Monthly Income:  ${monthly:,.2f}")

    print("\nTop Income Contributors:")

    ranked = []

    for h in holdings:
        ticker = h["ticker"]
        value = h["value"]

        y = TICKER_YIELD.get(ticker, YIELD_MAP.get(h["asset_type"], 0.02))
        ranked.append((ticker, value * y, y))

    ranked.sort(key=lambda x: x[1], reverse=True)

    for t, inc, y in ranked[:8]:
        print(f"{t:6}  ${inc:10,.2f}   ({y*100:.1f}%)")

    print("-" * 55)


# =========================================================
# MAIN
# =========================================================

def main():
    holdings = load_schwab("schwab.csv")

    if not holdings:
        print("❌ No holdings loaded")
        return

    total_value, income = calculate_income(holdings)

    report(holdings, total_value, income)


if __name__ == "__main__":
    main()
