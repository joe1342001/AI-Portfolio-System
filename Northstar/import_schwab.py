from pathlib import Path

# =========================================================
# SCHWAB PARSER (YOUR FORMAT, SAFE + SIMPLE)
# =========================================================

def load_schwab(file_path="schwab.csv"):
    path = Path(file_path)

    if not path.exists():
        print("❌ File not found:", file_path)
        return []

    lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    holdings = []

    # find header row
    header_index = None
    for i, line in enumerate(lines):
        if line.startswith('"Symbol"') and '"Qty' in line:
            header_index = i
            break

    if header_index is None:
        print("❌ Schwab header not found")
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
                raw = parts[i_value].replace("$", "").replace(",", "")
                value = float(raw) if raw else 0.0

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
# YIELD MODEL (THIS IS REQUIRED — SCHWAB DOES NOT PROVIDE IT)
# =========================================================

YIELD = {
    # income ETFs / CEFs
    "JEPI": 0.07,
    "JEPQ": 0.09,
    "QYLD": 0.11,
    "QQQI": 0.10,
    "SPYI": 0.10,
    "FEPI": 0.12,
    "YYY": 0.12,

    # REITs
    "AGNC": 0.13,
    "NLY": 0.11,

    # BDC / energy income
    "ARCC": 0.10,
    "MPLX": 0.08,
    "EPD": 0.07,

    # bond/cash proxy
    "SWVXX": 0.045,

    # equity ETFs
    "HDV": 0.03,
    "SCHD": 0.03,
    "VGK": 0.03,
    "VWO": 0.03,

    # fallback handled separately
}


DEFAULT_YIELD = 0.02


# =========================================================
# INCOME ENGINE
# =========================================================

def calculate_income(holdings):
    total_value = 0
    total_income = 0

    for h in holdings:
        ticker = h["ticker"]
        value = float(h.get("value", 0))

        total_value += value

        y = YIELD.get(ticker, DEFAULT_YIELD)

        total_income += value * y

    return total_value, total_income


# =========================================================
# REPORT
# =========================================================

def report(holdings, total_value, income):
    monthly = income / 12

    print("\nNORTHSTAR v1.2 — SCHWAB INCOME MODEL")
    print("-" * 55)

    print(f"Portfolio Value: ${total_value:,.2f}")
    print(f"Annual Income:   ${income:,.2f}")
    print(f"Monthly Income:  ${monthly:,.2f}")

    print("\nTop Income Contributors:")

    ranked = []
    for h in holdings:
        ticker = h["ticker"]
        value = h["value"]
        y = YIELD.get(ticker, DEFAULT_YIELD)
        ranked.append((ticker, value * y, y))

    ranked.sort(key=lambda x: x[1], reverse=True)

    for t, inc, y in ranked[:10]:
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
