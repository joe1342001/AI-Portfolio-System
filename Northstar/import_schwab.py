def import_schwab(csv_file):
    import csv
    from pathlib import Path

    path = Path(csv_file)

    if not path.exists():
        print("❌ File not found")
        return []

    with open(path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    # Find first real CSV header row
    header_index = None

    for i, line in enumerate(lines):
        if "symbol" in line.lower() or "ticker" in line.lower():
            header_index = i
            break

    if header_index is None:
        print("❌ No valid holdings table found in CSV")
        return []

    from io import StringIO
    clean_csv = StringIO("".join(lines[header_index:]))

    reader = csv.DictReader(clean_csv)

    holdings = []

    def find(col, options):
        for o in options:
            if o in col.lower():
                return True
        return False

    for row in reader:
        try:
            # flexible column detection
            ticker = None
            shares = None

            for k in row:
                if find(k, ["symbol", "ticker"]):
                    ticker = row[k]

                if find(k, ["quantity", "shares", "qty"]):
                    shares = row[k]

            if not ticker or not shares:
                continue

            ticker = ticker.strip().upper()
            shares = float(shares)

            if shares <= 0:
                continue

            holdings.append({
                "ticker": ticker,
                "shares": shares
            })

        except Exception:
            continue

    return holdings
