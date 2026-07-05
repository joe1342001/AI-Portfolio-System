from pathlib import Path

def get_base_path():
    return Path(__file__).resolve().parent.parent


def load_schwab_csv(file_path="data/schwab.csv"):
    base = get_base_path()
    path = base / file_path

    if not path.exists():
        raise FileNotFoundError(path)

    lines = path.read_text(encoding="utf-8-sig").splitlines()

    header_index = None
    for i, line in enumerate(lines):
        if '"Symbol"' in line and '"Qty' in line:
            header_index = i
            break

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

    holdings = []

    for line in lines[header_index + 1:]:
        if not line.startswith('"'):
            continue

        parts = [p.strip().strip('"') for p in line.split('","')]

        try:
            ticker = parts[i_symbol]

            if not ticker or "Total" in ticker:
                continue

            holdings.append({
                "ticker": ticker,
                "shares": float(parts[i_qty].replace(",", "")),
                "price": float(parts[i_price].replace("$", "") or 0),
                "value": float(parts[i_value].replace("$", "") or 0),
                "asset_type": parts[i_asset] if i_asset else "Equity"
            })

        except:
            continue

    return holdings
