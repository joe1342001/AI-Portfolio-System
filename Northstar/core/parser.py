"""
NorthStar Parser Module
Version: 3.0

Loads Schwab CSV exports and converts them into
a standardized holdings list.
"""

from pathlib import Path
import csv


def clean_number(value):
    """Convert strings like '$1,234.56' into float."""
    if value is None:
        return 0.0

    value = str(value).strip()

    if value in ("", "--", "N/A"):
        return 0.0

    value = (
        value.replace("$", "")
             .replace(",", "")
             .replace("%", "")
             .strip()
    )

    try:
        return float(value)
    except ValueError:
        return 0.0


def load_schwab_csv(filename="data/schwab.csv"):
    """
    Reads a Schwab positions export.

    Returns:
        list[dict]
    """

    path = Path(filename)

    if not path.exists():
        raise FileNotFoundError(f"Cannot find {filename}")

    holdings = []

    with path.open("r", encoding="utf-8-sig", newline="") as f:

        # Skip anything before the real header row.
        while True:
            position = f.tell()
            line = f.readline()

            if not line:
                raise ValueError("Could not locate Schwab header row.")

            if line.startswith('"Symbol"') or line.startswith("Symbol"):
                f.seek(position)
                break

        reader = csv.DictReader(f)

        for row in reader:

            symbol = (row.get("Symbol") or "").strip()

            if symbol in (
                "",
                "Positions Total",
                "Cash & Cash Investments",
            ):
                continue

            qty = clean_number(row.get("Qty (Quantity)"))
            market_value = clean_number(row.get("Mkt Val (Market Value)"))
            price = clean_number(row.get("Price"))
            cost_basis = clean_number(row.get("Cost Basis"))

            holdings.append(
                {
                    "ticker": symbol,
                    "shares": qty,
                    "price": price,
                    "market_value": market_value,
                    "cost_basis": cost_basis,
                    "asset_type": row.get("Asset Type", "").strip(),
                    "description": row.get("Description", "").strip(),
                }
            )

    return holdings


if __name__ == "__main__":
    portfolio = load_schwab_csv()

    print(f"\nLoaded {len(portfolio)} holdings\n")

    for h in portfolio:
        print(
            f"{h['ticker']:6}"
            f"{h['shares']:10.4f}"
            f"   ${h['market_value']:12,.2f}"
        )
