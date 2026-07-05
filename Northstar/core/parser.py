from pathlib import Path

# =========================================================
# PATH RESOLUTION (STREAMLIT SAFE)
# =========================================================

def get_base_path():
    return Path(__file__).resolve().parent.parent


# =========================================================
# YIELD ENGINE (REALISTIC MODEL)
# =========================================================

TICKER_YIELD = {
    # High yield REITs / BDCs
    "AGNC": 0.13,
    "ARCC": 0.10,
    "NLY": 0.11,
    "O": 0.05,

    # Covered call / income ETFs
    "JEPI": 0.07,
    "JEPQ": 0.09,
    "QYLD": 0.11,
    "XYLD": 0.10,
    "SPYI": 0.10,
    "QQQI": 0.10,
    "FEPI": 0.12,

    # Dividend ETFs
    "SCHD": 0.03,
    "VYM": 0.03,
    "HDV": 0.03,

    # International ETFs
    "VGK": 0.03,
    "VWO": 0.03,

    # Cash / MMF
    "SWVXX": 0.045,
}


def get_yield_rate(ticker, asset_type):
    ticker = ticker.upper().strip()

    # 1. Exact ticker match (highest priority)
    if ticker in TICKER_YIELD:
        return TICKER_YIELD[ticker]

    # 2. Asset-type fallback
    asset_type = (asset_type or "").lower()

    if "cash" in asset_type or "money" in asset_type:
        return 0.045

    if "reit" in asset_type:
        return 0.10

    if "etf" in asset_type or "closed" in asset_type:
        return 0.04

    # 3. Default equity yield (S&P-like)
    return 0.015


# =========================================================
# MAIN CSV LOADER
# =========================================================

def load_schwab_csv(file_path="data/schwab.csv"):

    base_path = get_base_path()
    full_path = base_path / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"Cannot find file: {full_path}")

    lines = full_path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    # =========================================================
    # FIND HEADER ROW
    # =========================================================

    header_index = None

    for i, line in enumerate(lines):
        if '"Symbol"' in line and '"Qty' in line:
            header_index = i
            break

    if header_index is None:
        raise ValueError("Could not locate Schwab CSV header row")

    headers = [h.strip().strip('"') for h in lines[header_index].split('","')]

    # =========================================================
    # COLUMN MAPPING
    # =========================================================

    def col(name):
        for i, h in enumerate(headers):
            if name.lower() in h.lower():
                return i
        return None

    i_symbol = col("Symbol")
    i_qty = col("Qty")
    i_price = col("Price")
    i_value = col("Mkt Val")
    i_asset = col("Asset Type")

    if i_symbol is None or i_qty is None:
        raise ValueError("Missing required Schwab columns")

    # =========================================================
    # PARSE ROWS
    # =========================================================

    holdings = []

    for line in lines[header_index + 1:]:

        if not line.startswith('"'):
            continue

        parts = [p.strip().strip('"') for p in line.split('","')]

        try:
            ticker = parts[i_symbol].strip()

            # skip junk rows
            if not ticker or "Total" in ticker:
                continue

            shares = float(parts[i_qty].replace(",", ""))

            price = 0.0
            if i_price is not None and i_price < len(parts):
                price_raw = parts[i_price].replace("$", "").replace(",", "")
                price = float(price_raw) if price_raw else 0.0

            value = 0.0
            if i_value is not None and i_value < len(parts):
                value_raw = parts[i_value].replace("$", "").replace(",", "")
                value = float(value_raw) if value_raw else 0.0

            asset_type = parts[i_asset] if i_asset and i_asset < len(parts) else "Equity"

            # =====================================================
            # REAL INCOME MODEL
            # =====================================================

            yield_rate = get_yield_rate(ticker, asset_type)
            annual_income = value * yield_rate

            holdings.append({
                "ticker": ticker,
                "shares": shares,
                "price": price,
                "value": value,
                "annual_income": annual_income,
                "asset_type": asset_type,
                "yield": yield_rate
            })

        except Exception:
            continue

    return holdings


# =========================================================
# DEBUG HELPER
# =========================================================

def debug_path(file_path="data/schwab.csv"):
    base_path = get_base_path()
    full_path = base_path / file_path

    return {
        "base_path": str(base_path),
        "full_path": str(full_path),
        "exists": full_path.exists()
    }
