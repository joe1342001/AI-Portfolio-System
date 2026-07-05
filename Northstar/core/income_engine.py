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


def get_yield(ticker, asset_type=None):
    t = ticker.upper()

    # HARD FIX: NEVER default to 2%
    if t in TICKER_YIELD:
        return TICKER_YIELD[t]

    asset_type = (asset_type or "").lower()

    if "reit" in asset_type:
        return 0.09

    if "etf" in asset_type:
        return 0.04

    if "cash" in asset_type:
        return 0.045

    # realistic equity fallback (NOT 2%)
    return 0.015


def enrich_with_income(holdings):
    for h in holdings:
        y = get_yield(h["ticker"], h.get("asset_type"))
        h["yield"] = y
        h["annual_income"] = h["value"] * y

    return holdings
