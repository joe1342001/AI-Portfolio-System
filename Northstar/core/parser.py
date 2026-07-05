from pathlib import Path


# =========================================================
# PATH RESOLUTION (FIXES STREAMLIT CLOUD ISSUES)
# =========================================================

def get_base_path():
    """
    Always resolves project root correctly whether:
    - running locally
    - running in Streamlit Cloud
    - running from submodule pages
    """
    return Path(__file__).resolve().parent.parent


# =========================================================
# MAIN LOADER
# =========================================================

def load_schwab_csv(file_path="data/schwab.csv"):
    """
    Loads Schwab export CSV into structured holdings list.
    """

    base_path = get_base_path()
    full_path = base_path / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"Cannot find file at: {full_path}")

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
        raise ValueError("Missing required Schwab columns (Symbol or Qty)")

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

            # skip totals / empty rows
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
            # INCOME MODEL (Schwab does NOT provide yield data)
            # =====================================================
            annual_income = value * 0.05

            holdings.append({
                "ticker": ticker,
                "shares": shares,
                "price": price,
                "value": value,
                "annual_income": annual_income,
                "asset_type": asset_type
            })

        except Exception:
            continue

    return holdings


# =========================================================
# OPTIONAL DEBUG FUNCTION
# =========================================================

def debug_path(file_path="data/schwab.csv"):
    base_path = get_base_path()
    full_path = base_path / file_path

    return {
        "base_path": str(base_path),
        "full_path": str(full_path),
        "exists": full_path.exists()
    }
