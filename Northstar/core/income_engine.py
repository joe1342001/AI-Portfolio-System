TICKER_YIELD = {
    "AGNC": 0.13,
    "ARCC": 0.10,
    "NLY": 0.11,
    "JEPI": 0.07,
    "JEPQ": 0.09,
    "QYLD": 0.11,
    "QQQI": 0.10,
    "SPYI": 0.10,
    "FEPI": 0.12,
    "SCHD": 0.03,
    "HDV": 0.03,
    "VWO": 0.03,
    "VGK": 0.03,
    "SWVXX": 0.045
}


def get_yield(ticker, asset_type):
    t = ticker.upper()

    if t in TICKER_YIELD:
        return TICKER_YIELD[t]

    at = (asset_type or "").lower()

    if "cash" in at:
        return 0.045

    if "reit" in at:
        return 0.10

    if "etf" in at:
        return 0.04

    return 0.015


def enrich_with_income(holdings):
    for h in holdings:
        y = get_yield(h["ticker"], h.get("asset_type"))
        h["yield"] = y
        h["annual_income"] = h["value"] * y

    return holdings
