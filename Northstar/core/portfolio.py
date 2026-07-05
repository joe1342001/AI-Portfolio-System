from pathlib import Path


def get_base_path():
    return Path(__file__).resolve().parent.parent


def load_portfolio():
    """
    SAFE loader that avoids import-time circular issues
    """

    # Import INSIDE function (breaks circular imports)
    from core.parser import load_schwab_csv
    from core.income_engine import enrich_with_income

    holdings = load_schwab_csv()
    holdings = enrich_with_income(holdings)

    return holdings
