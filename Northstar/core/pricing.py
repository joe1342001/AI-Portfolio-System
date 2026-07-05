"""
NorthStar Pricing Module
Version: 3.0

Retrieves live market prices with automatic fallback
to Schwab CSV prices.
"""

import yfinance as yf

# Simple in-memory cache
_price_cache = {}


def get_live_price(ticker):
    """
    Get the latest market price from Yahoo Finance.

    Returns:
        float or None
    """
    ticker = ticker.upper().strip()

    if ticker in _price_cache:
        return _price_cache[ticker]

    try:
        stock = yf.Ticker(ticker)

        data = stock.history(period="5d")

        if data.empty:
            return None

        price = float(data["Close"].iloc[-1])

        _price_cache[ticker] = price

        return price

    except Exception:
        return None


def get_price(holding):
    """
    Returns the best available price.

    Preference:
        1. Live Yahoo price
        2. Schwab CSV price
    """

    live = get_live_price(holding["ticker"])

    if live is not None:
        return live

    return float(holding.get("price", 0))


def update_market_values(holdings):
    """
    Adds live pricing information to every holding.

    Returns:
        Updated holdings list
    """

    updated = []

    for h in holdings:

        price = get_price(h)

        h = h.copy()

        h["live_price"] = price
        h["live_value"] = price * h["shares"]

        updated.append(h)

    return updated


def portfolio_value(holdings):
    """
    Calculates total portfolio value
    using live prices when available.
    """

    total = 0

    for h in holdings:
        total += h["live_value"]

    return total


# --------------------------------------------------
# Test Mode
# --------------------------------------------------

if __name__ == "__main__":

    from parser import load_schwab_csv

    holdings = load_schwab_csv("../data/schwab.csv")

    holdings = update_market_values(holdings)

    print()

    for h in holdings:

        print(
            f"{h['ticker']:6}"
            f"  Live ${h['live_price']:8.2f}"
            f"   Value ${h['live_value']:12,.2f}"
        )

    print("\nPortfolio Value")
    print(f"${portfolio_value(holdings):,.2f}")
