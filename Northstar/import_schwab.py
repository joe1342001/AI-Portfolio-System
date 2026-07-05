import csv
from pathlib import Path
from io import StringIO

def load_schwab(csv_file):
    path = Path(csv_file)

    if not path.exists():
        print("❌ File not found:", csv_file)
        return []

    raw = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    # -----------------------------
    # FIND REAL HEADER ROW
    # -----------------------------
    header_index = None

    for i, line in enumerate(raw):
        line_lower = line.lower()

        if "symbol" in line_lower and "qty" in line_lower:
            header_index = i
            break

        if "symbol" in line_lower and "quantity" in line_lower:
            header_index = i
            break

    if header_index is None:
        print("❌ Could not locate Schwab data table in file.")
        print("First line preview:", raw[0])
        return []

    clean_data = "\n".join(raw[header_index:])

    reader = csv.DictReader(StringIO(clean_data))

    holdings = []

    for row in reader:
        try:
            ticker = None
            shares = None
            value = None
            asset_type = None

            for k, v in row.items():
                lk = k.lower()

                if "symbol" in lk:
                    ticker = v

                if "qty" in lk or "quantity" in lk:
                    shares = v

                if "market val" in lk:
                    value = v

                if "asset type" in lk:
                    asset_type = v

            if not ticker or not shares:
                continue

            ticker = ticker.strip().upper()
            shares = float(shares)

            # clean value (remove $)
            if value:
                value = float(value.replace("$", "").replace(",", ""))
            else:
                value = 0.0

            holdings.append({
                "ticker": ticker,
                "shares": shares,
                "value": value,
                "asset_type": asset_type or "Equity"
            })

        except Exception:
            continue

    return holdings
