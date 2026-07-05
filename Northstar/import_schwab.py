import re
from pathlib import Path

def parse_schwab(csv_file):
    path = Path(csv_file)

    if not path.exists():
        print("❌ File not found:", csv_file)
        return []

    lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    holdings = []

    # -----------------------------
    # PATTERN STRATEGY
    # -----------------------------
    # We identify real rows by:
    # "SYMBOL","DESCRIPTION","NUMBER"... pattern
    row_pattern = re.compile(r'^"([A-Z0-9\.]+)","')

    for line in lines:

        # skip header/meta
        if not line.startswith('"'):
            continue

        # must look like a real ticker row
        match = row_pattern.match(line)
        if not match:
            continue

        try:
            parts = [p.strip().strip('"') for p in line.split('","')]

            if len(parts) < 5:
                continue

            ticker = parts[0].strip().upper()

            # Qty (your exact column position from sample)
            qty_raw = parts[2].replace(",", "")
            qty = float(qty_raw) if qty_raw else 0

            if qty <= 0:
                continue

            # Market value (optional safety)
            value = 0.0
            for p in parts:
                if "$" in p:
                    val = p.replace("$", "").replace(",", "")
                    if re.match(r'^\d+(\.\d+)?$', val):
                        value = float(val)
                        break

            # asset type (last column usually)
            asset_type = parts[-1] if parts[-1] else "Equity"

            holdings.append({
                "ticker": ticker,
                "shares": qty,
                "value": value,
                "asset_type": asset_type
            })

        except Exception:
            continue

    return holdings
