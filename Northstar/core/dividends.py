"""
NorthStar Dividend Engine
Clean version — no artificial 2% global fallback
"""

# =========================================================
# CORE YIELD MAP (KNOWN TICKERS)
# =========================================================

TICKER_YIELD = {
    # High-yield ETFs / income products
    "AGNC": 0.13,
    "ARCC": 0.10,
    "NLY": 0.11,
    "JEPI": 0.07,
    "JEPQ": 0.09,
    "QYLD": 0.11,
    "QQQI": 0.10,
    "SPYI": 0.10,
    "FEPI": 0.12,

    # Core ETFs
    "SCHD": 0.03,
    "VYM": 0.03,
    "HDV": 0.03,
    "VIG": 0.02,

    # International / broad equity (low yield)
    "VTI": 0.015,
    "VOO": 0.015,
    "SPY": 0.015,
    "QQQ": 0.008,

    # Cash / money market
    "SWVXX": 0.045,
    "BIL": 0.045,
}


# =========================================================
# SAFE YIELD RESOLUTION
# =========================================================

def get_dividend_yield(ticker: str, asset_type: str = None) -> float:
    """
    Returns estimated dividend yield.
    NO GLOBAL 2% DEFAULT.
    """

    if not ticker:
        return 0.0

    t = ticker.upper()

    # 1. Known ticker map (highest confidence)
    if t in TICKER_YIELD:
        return TICKER_YIELD[t]

    # 2. Asset-type heuristics (secondary logic)
    asset = (asset_type or "").lower()

    if "reit" in asset:
        return 0.09

    if "etf" in asset:
        return 0.025

    if "cash" in asset or "money" in asset:
        return 0.045

    if "equity" in asset or "stock" in asset:
        return 0.015

    # 3. Conservative unknown fallback (NOT 2%)
    # This is intentionally LOW and explicit
    return 0.01


# =========================================================
# ENRICH PORTFOLIO WITH INCOME DATA
# =========================================================

def enrich_with_dividends(holdings: list) -> list:
    """
    Adds:
    - yield
    - annual_income
    """

    for h in holdings:
        y = get_dividend_yield(
            h.get("ticker"),
            h.get("asset_type")
        )

        h["yield"] = y
        h["annual_income"] = h.get("value", 0) * y

    return holdings
