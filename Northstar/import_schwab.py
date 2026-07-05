import re
from pathlib import Path

def parse_schwab(csv_file):
    path = Path(csv_file)

    if not path.exists():
        print("❌ File not found:", csv_file)
        return []

    lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    # -----------------------------
    # STEP 1: FIND HEADER LINE
    # -----------------------------
    header_line = None

    for line in lines:
        if line.startswith('"Symbol"') and '"Qty' in line:
            header_line = line
            break

    if not header_line:
        print("❌ Could not find Schwab header row")
        return []

    headers = [h.strip().strip('"') for h in header_line.split('","')]

    # column indexes (fixed mapping)
    def find_index(name_contains):
        for i, h in enumerate(headers):
            if name_contains.lower() in h.lower():
                return i
        return None

    i_symbol = find_index("Symbol")
    i_qty = find_index("Qty")
    i_value = find_index("Mkt Val")
    i_asset = find_index("Asset Type")

    if i_symbol is None or i_qty is None:
        print("❌ Required columns missing in header")
        print(headers)
        return []

    holdings = []

    # -----------------------------
    # STEP 2: PARSE ROWS MANUALLY
    # -----------------------------
    data_started = False

    for line in lines:
        if line == header_line:
            data_started = True
            continue

        if not data_started:
            continue

        # skip junk lines
        if not line.startswith('"'):
            continue

        # split safely on "," but keep structure
        parts = [p.strip().strip('"') for p in line.split('","')]

        try:
            ticker = parts[i_symbol].strip().upper()

            qty_raw = parts[i_qty].replace(",", "")
            qty = float(qty_raw) if qty_raw else 0

            if qty <= 0:
                continue

            value = 0.0
            if i_value is not None and i_value < len(parts):
                val_raw = parts[i_value].replace("$", "").replace(",", "")
                value = float(val_raw) if val_raw else 0.0

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
