from core.parser import load_schwab_csv
from core.income_engine import enrich_with_income


def load_portfolio():
    holdings = load_schwab_csv()
    holdings = enrich_with_income(holdings)
    return holdings
