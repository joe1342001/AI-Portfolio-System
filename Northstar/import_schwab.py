import csv
import json
from pathlib import Path

def detect_column(row_keys):
    """
    Try to find the correct Schwab column names automatically.
    """
    keys = [k.lower() for k in row_keys]

    def find(possible):
        for p in possible:
            for k in keys:
                if p in k:
                    return row_keys[keys.index(k)]
        return None

    return {
        "ticker": find(["symbol", "ticker"]),
        "shares": find(["quantity", "shares", "qty"])
    }


def import_schwab(csv_file="schwab.csv"):
    path = Path(csv_file)

    if not path.exists():
        print("❌ CSV file not found:", csv_file)
        return

    portfolio = []

    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            print("❌ Could not read CSV headers")
            return

        columns = detect_column(reader.fieldnames)

        if not columns["ticker"] or not columns["shares"]:
            print("❌ Could not detect required columns.")
            print("Found columns:", reader.fieldnames)
            return

        for row in reader:
            try:
                ticker = row[columns["ticker"]].strip().upper()
                shares = float(row[columns["shares"]])

                # skip empty or zero rows
                if not ticker or shares <= 0:
                    continue

                portfolio.append({
                    "ticker": ticker,
                    "shares": shares
                })

            except Exception:
                continue

    data = {"portfolio": portfolio}

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    print("\n✅ Schwab import complete!")
    print(f"Holdings imported: {len(portfolio)}")
    print("Saved to data.json")


if __name__ == "__main__":
    import_schwab("schwab.csv")
