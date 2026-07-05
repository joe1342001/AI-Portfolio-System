from pathlib import Path
import re

# =========================================================
# CLEAN
# =========================================================

def clean_text(x):
    return re.sub(r'\s+', '', str(x)).upper()


# =========================================================
# SCHWAB PARSER
# =========================================================

def load_schwab(file_path="schwab.csv"):
    path = Path(file_path)

    if not path.exists():
        print("❌ Missing file")
        return []

    lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    header_index = None
    for i, line in enumerate(lines):
        if '"Symbol"' in line and '"Qty' in line:
            header_index = i
            break

    if header_index is None:
        print("❌ Header not found")
        return []

    headers = [h.strip().strip('"') for h in lines[header_index].split('","')]

    def col(name):
        for i, h in enumerate(headers):
            if name.lower() in h.lower():
                return i
        return None

    i_symbol = col("Symbol")
    i_qty = col("Qty")
    i_asset = col("Asset Type")

    def extract_value(line):
        vals = re.findall(r"\$?[\d,]+\.\d{2}", line)
        nums = [float(v.replace("$", "").replace(",", "")) for v in vals]
        return max(nums) if nums else 0.0

    holdings = []

    for line in lines[header_index + 1:]:
        if not line.startswith('"'):
            continue

        parts = [p.strip().strip('"') for p in line.split('","')]

        try:
            ticker = clean_text(parts[i_symbol])
            qty = float(parts[i_qty].replace(",", ""))

            if qty <= 0:
                continue

            value = extract_value(line)
            asset = parts[i_asset] if i_asset else "Equity"

            holdings.append({
                "ticker": ticker,
                "value": value,
                "asset": clean_text(asset)
            })

        except:
            continue

    return holdings


# =========================================================
# INCOME MODEL (FAILSAFE)
# =========================================================

ASSET_YIELD = {
    "EQUITY": 0.02,
    "ETF": 0.04,
    "CASH": 0.045,
    "REIT": 0.10
}

TICKER_YIELD = {
    "JEPI": 0.07,
    "JEPQ": 0.09,
    "QYLD": 0.11,
    "QQQI": 0.10,
    "SPYI": 0.10,
    "FEPI": 0.12,
    "YYY": 0.12,
    "AGNC": 0.13,
    "NLY": 0.11,
    "ARCC": 0.10,
    "MPLX": 0.08,
    "EPD": 0.07,
    "SWVXX": 0.045,
    "HDV": 0.03,
    "SCHD": 0.03,
    "VGK": 0.03,
    "VWO": 0.03,
    "QQQ": 0.015
}


def calculate_income(holdings):
    total_value = 0
    total_income = 0

    for h in holdings:
        ticker = h["ticker"]
        value = float(h["value"])
        asset = h["asset"]

        total_value += value

        # HARD PRIORITY: ticker yield
        if ticker in TICKER_YIELD:
            y = TICKER_YIELD[ticker]
        else:
            y = ASSET_YIELD.get(asset, 0.02)

        total_income += value * y

    return total_value, total_income


# =========================================================
# REPORT
# =========================================================

def report(holdings, total_value, income):
    print("\nNORTHSTAR v1.5 — FAILSAFE INCOME ENGINE")
    print("-" * 55)

    print(f"Portfolio Value: ${total_value:,.2f}")
    print(f"Annual Income:   ${income:,.2f}")
    print(f"Monthly Income:  ${income/12:,.2f}")

    print("\nTop Contributors:")

    ranked = []

    for h in holdings:
        ticker = h["ticker"]
        value = h["value"]

        if ticker in TICKER_YIELD:
            y = TICKER_YIELD[ticker]
        else:
            y = 0.02

        ranked.append((ticker, value * y))

    ranked.sort(key=lambda x: x[1], reverse=True)

    for t, inc in ranked[:10]:
        print(f"{t:6}  ${inc:10,.2f}")

    print("-" * 55)


# =========================================================
# MAIN
# =========================================================

def main():
    holdings = load_schwab("schwab.csv")

    print("\nDEBUG: holdings loaded =", len(holdings))

    total_value, income = calculate_income(holdings)

    report(holdings, total_value, income)


if __name__ == "__main__":
    main()
