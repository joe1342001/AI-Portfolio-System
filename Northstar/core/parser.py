from pathlib import Path


# =========================================================
# PATH RESOLUTION (STREAMLIT SAFE)
# =========================================================

def get_base_path():
    return Path(__file__).resolve().parent.parent


# =========================================================
# MAIN CSV LOADER (RAW HOLDINGS ONLY)
# =========================================================

def load_schwab_csv(file_path="data/schwab.csv"):
    """
    Loads Schwab CSV and returns RAW holdings data.
    NO income logic here.
    """

    base_path = get_base_path()
    full_path = base_path / file_path

    # -------------------------
    # FILE CHECK
    # -------------------------
    if not full_path.exists():
        raise FileNotFoundError(f"CSV not found at: {full_path}")

    # -------------------------
    # READ FILE
    # -------------------------
    lines = full_path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    if not lines:
        raise ValueError("CSV file is empty")

    # -------------------------
    # FIND HEADER ROW
    # -------------------------
    header_index = None

    for i, line in enumerate(lines):
        # more resilient than strict quotes match
        if "Symbol" in line and "Qty" in line:
            header_index = i
            break

    if header_index is None:
        raise ValueError(
            "Could not locate header row in Schwab CSV (Symbol / Qty not found)"
        )

    # -------------------------
    # PARSE HEADERS
    # -------------------------
    headers = [h.strip().strip('"') for h in lines[header_index].split('","')]

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
        raise ValueError("Required columns missing: Symbol or Qty")

    # -------------------------
    # PARSE ROWS
    # -------------------------
    holdings = []

    for line in lines[header_index + 1:]:

        if not line.startswith('"'):
            continue

        parts = [p.strip().strip('"') for p in line.split('","')]

        try:
            ticker = parts[i_symbol].strip()

            if not ticker or "Total" in ticker:
                continue

            shares = float(parts[i_qty].replace(",", "") or 0)

            price = 0.0
            if i_price is not None and i_price < len(parts):
                price = float(parts[i_price].replace("$", "").replace(",", "") or 0)

            value = 0.0
            if i_value is not None and i_value < len(parts):
                value = float(parts[i_value].replace("$", "").replace(",", "") or 0)

            asset_type = (
                parts[i_asset] if i_asset is not None and i_asset < len(parts)
                else "Equity"
            )

            holdings.append({
                "ticker": ticker,
                "shares": shares,
                "price": price,
                "value": value,
                "asset_type": asset_type
            })

        except Exception:
            # DO NOT crash pipeline for one bad row
            continue

    return holdings


# =========================================================
# DEBUG HELPERS (OPTIONAL)
# =========================================================

def debug_path(file_path="data/schwab.csv"):
    base_path = get_base_path()
    full_path = base_path / file_path

    return {
        "base_path": str(base_path),
        "full_path": str(full_path),
        "exists": full_path.exists()
    }
