from pathlib import Path
import re

# =========================================================
# CLEAN UTIL
# =========================================================

def clean_text(x):
    x = str(x)
    x = re.sub(r'\s+', '', x)          # remove all whitespace
    x = re.sub(r'[^\x21-\x7E]', '', x)  # remove hidden chars
    return x.upper()


# =========================================================
# SCHWAB PARSER
# =========================================================

def load_schwab(file_path="schwab.csv"):
    path = Path(file_path)

    if not path.exists():
        print("❌ File not found:", file_path)
        return []

    lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    header_index = None
    for i, line in enumerate(lines):
        if '"Symbol"' in line and '"Qty' in line:
            header_index = i
            break

    if header_index is None:
        print("❌ Could not locate Schwab header")
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
            asset = clean_text(parts[i_asset]) if i_asset else "EQUITY"

            holdings.append({
                "ticker": ticker,
                "shares": qty,
                "value": value,
                "asset": asset
            })

        except:
            continue

    return holdings


# =========================================================
# YIELD MODEL
# =========================================================

YIELD = {
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

DEFAULT_YIELD = 0.02


# =========================================================
# INCOME ENGINE
# =========================================================

def calculate_income(holdings):
    total_value = 0
    total_income = 0

    for h in holdings:
        ticker = h["ticker"]
        value = float(h["value"])
        asset = h["asset"]

        total_value += value

        y = YIELD.get(ticker, DEFAULT_YIELD)
        total_income += value * y

    return total_value, total_income


# =========================================================
# REPORT
# =========================================================

def report(holdings, total_value, income):
    print("\nNORTHSTAR v1.7 — PORTFOLIO ENGINE")
    print("-" * 55)

    print(f"Portfolio Value: ${total_value:,.2f}")
    print(f"Annual Income:   ${income:,.2f}")
    print(f"Monthly Income:  ${income/12:,.2f}")

    print("\nTop Income Contributors:")

    ranked = []

    for h in holdings:
        t = h["ticker"]
        v = h["value"]
        y = YIELD.get(t, DEFAULT_YIELD)

        ranked.append((t, v * y))

    ranked.sort(key=lambda x: x[1], reverse=True)

    for t, inc in ranked[:10]:
        print(f"{t:6}  ${inc:10,.2f}")

    print("-" * 55)


# =========================================================
# MENU SYSTEM (THIS IS WHAT YOU WERE MISSING)
# =========================================================

def menu(holdings, total_value, income):
    while True:
        print("\n===== NORTHSTAR MENU =====")
        print("1. Portfolio Value")
        print("2. Income")
        print("3. Full Report")
        print("4. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            print(f"\nPortfolio Value: ${total_value:,.2f}")

        elif choice == "2":
            print(f"\nAnnual Income:  ${income:,.2f}")
            print(f"Monthly Income: ${income/12:,.2f}")

        elif choice == "3":
            report(holdings, total_value, income)

        elif choice == "4":
            break

        else:
            print("Invalid option")


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

    menu(holdings, total_value, income)


if __name__ == "__main__":
    main()
