"""
NorthStar Dividend Module
Version 3.0
"""

import json
from pathlib import Path

DEFAULT_YIELD = 0.02


def load_yield_table(filename="data/dividend_yields.json"):
    path = Path(filename)

    if not path.exists():
        return {}

    with path.open("r") as f:
        return json.load(f)


YIELDS = load_yield_table()


def get_yield(ticker):
    return YIELDS.get(ticker.upper(), DEFAULT_YIELD)


def annual_income(holding):
    value = holding["live_value"]
    y = get_yield(holding["ticker"])
    return value * y


def monthly_income(holding):
    return annual_income(holding) / 12


def enrich_income(holdings):
    total = 0

    new = []

    for h in holdings:

        h = h.copy()

        h["yield"] = get_yield(h["ticker"])

        h["annual_income"] = annual_income(h)

        h["monthly_income"] = monthly_income(h)

        total += h["annual_income"]

        new.append(h)

    return new, total


def top_income(holdings, n=10):
    return sorted(
        holdings,
        key=lambda h: h["annual_income"],
        reverse=True
    )[:n]


if __name__ == "__main__":

    from parser import load_schwab_csv
    from pricing import update_market_values

    holdings = load_schwab_csv("../data/schwab.csv")

    holdings = update_market_values(holdings)

    holdings, total = enrich_income(holdings)

    print("\nEstimated Annual Income")
    print(f"${total:,.2f}")

    print("\nTop Income Holdings\n")

    for h in top_income(holdings):

        print(
            f"{h['ticker']:6}"
            f"  Yield {h['yield']*100:5.1f}%"
            f"  Annual ${h['annual_income']:9,.2f}"
        )
