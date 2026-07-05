import csv
from pathlib import Path
from io import StringIO

def parse_schwab(csv_file):
    path = Path(csv_file)

    if not path.exists():
        print("❌ File not found:", csv_file)
        return []

    raw_lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    # -----------------------------
    # STEP 1: FIND EXACT HEADER LINE
    # -----------------------------
    header_index = None

    for i, line in enumerate(raw_lines):
        if line.startswith('"Symbol"') and '"Qty' in line:
            header_index = i
            break

    if header_index is None:
        print("❌ Schwab header not found")
        print("First line:", raw_lines[0])
        return []

    csv_data = "\n".join(raw_lines[header_index:])

    reader = csv.DictReader(StringIO(csv_data))

    holdings = []

    # -----------------------------
    # STEP 2: FIELD MAPPING (FIXED FOR YOUR FORMAT)
    # -----------------------------
    for row in reader:
        try:
            ticker = row.get("Symbol", "").strip().upper()

            qty_raw = row.get("Qty (Quantity)", "0")
            qty = float(qty_raw.replace(",", ""))

            asset_type = row.get("Asset Type", "Equity").strip()

            market_val_raw = row.get("Mkt Val (Market Value)", "0")
            market_val = float(
                market_val_raw.replace("$", "").replace(",", "")
            )

            if not ticker or qty <= 0:
                continue

            holdings.append({
                "ticker": ticker,
                "shares": qty,
                "value": market_val,
                "asset_type": asset_type
            })

        except Exception:
            continue

    return holdings
