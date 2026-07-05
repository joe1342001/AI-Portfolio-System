import json

def build_portfolio():
    print("\nNorthStar Portfolio Builder")
    print("Enter your holdings. Type 'done' when finished.\n")

    portfolio = []

    while True:
        ticker = input("Ticker (or 'done'): ").strip().upper()

        if ticker.lower() == "done":
            break

        shares_input = input("Shares: ").strip()

        # validation
        if not shares_input.replace(".", "").isdigit():
            print("Invalid shares. Try again.\n")
            continue

        shares = float(shares_input)

        portfolio.append({
            "ticker": ticker,
            "shares": shares
        })

        print(f"Added: {ticker} ({shares} shares)\n")

    data = {"portfolio": portfolio}

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    print("\n✅ data.json created successfully!")
    print("Holdings saved:", len(portfolio))


if __name__ == "__main__":
    build_portfolio()
