from pathlib import Path
import re
import tkinter as tk
from tkinter import ttk, messagebox

import yfinance as yf


# =========================================================
# CLEAN UTIL
# =========================================================

def clean_text(x):
    x = str(x)
    x = re.sub(r"\s+", "", x)
    x = re.sub(r"[^\x21-\x7E]", "", x)
    return x.upper()


# =========================================================
# SCHWAB PARSER (STATIC BASE HOLDINGS)
# =========================================================

def load_schwab(file_path="schwab.csv"):
    path = Path(file_path)

    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    header_index = None
    for i, line in enumerate(lines):
        if '"Symbol"' in line and '"Qty' in line:
            header_index = i
            break

    if header_index is None:
        return []

    headers = [h.strip().strip('"') for h in lines[header_index].split('","')]

    def col(name):
        for i, h in enumerate(headers):
            if name.lower() in h.lower():
                return i
        return None

    i_symbol = col("Symbol")
    i_qty = col("Qty")
    i_asset = col("Asset Type")

    holdings = []

    for line in lines[header_index + 1:]:
        if not line.startswith('"'):
            continue

        parts = [p.strip().strip('"') for p in line.split('","')]

        try:
            ticker = clean_text(parts[i_symbol])
            qty = float(parts[i_qty].replace(",", ""))

            if qty <= 0:
                continue

            asset = clean_text(parts[i_asset]) if i_asset else "EQUITY"

            holdings.append({
                "ticker": ticker,
                "shares": qty,
                "asset": asset
            })

        except:
            continue

    return holdings


# =========================================================
# LIVE PRICE ENGINE
# =========================================================

def get_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if data.empty:
            return 0.0
        return float(data["Close"].iloc[-1])
    except:
        return 0.0


# =========================================================
# YIELD MODEL
# =========================================================

YIELD = {
    "JEPI": 0.07,
    "JEPQ": 0.09,
    "QYLD": 0.11,
    "QQQI": 0.10,
    "SPYI": 0.10,
    "FEPI": 0.12,
    "YYY": 0.12,
    "AGNC": 0.13,
    "NLY": 0.11,
    "ARCC": 0.10,
    "MPLX": 0.08,
    "EPD": 0.07,
    "SWVXX": 0.045,
    "HDV": 0.03,
    "SCHD": 0.03,
    "VGK": 0.03,
    "VWO": 0.03,
    "QQQ": 0.015
}

DEFAULT_YIELD = 0.02


# =========================================================
# ANALYTICS ENGINE
# =========================================================

def calculate(holdings):
    total_value = 0
    total_income = 0

    enriched = []

    for h in holdings:
        ticker = h["ticker"]
        shares = h["shares"]

        price = get_price(ticker)
        value = shares * price

        y = YIELD.get(ticker, DEFAULT_YIELD)

        income = value * y

        total_value += value
        total_income += income

        enriched.append((ticker, shares, price, value, income))

    return total_value, total_income, enriched


# =========================================================
# GUI APP
# =========================================================

class NorthStarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NorthStar v2.1 — Live Portfolio Engine")
        self.root.geometry("1000x650")

        self.holdings = load_schwab("schwab.csv")

        self.total_value = 0
        self.total_income = 0
        self.enriched = []

        # TOP METRICS
        self.lbl = tk.Label(root, text="", font=("Arial", 14))
        self.lbl.pack(pady=10)

        # BUTTONS
        frame = tk.Frame(root)
        frame.pack()

        tk.Button(frame, text="Refresh Prices", command=self.refresh).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Top Income", command=self.top_income).pack(side=tk.LEFT, padx=5)

        # TABLE
        self.tree = ttk.Treeview(
            root,
            columns=("ticker", "shares", "price", "value", "income"),
            show="headings"
        )

        for col in ("ticker", "shares", "price", "value", "income"):
            self.tree.heading(col, text=col.upper())

        self.tree.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self):
        try:
            self.total_value, self.total_income, self.enriched = calculate(self.holdings)

            self.lbl.config(
                text=f"Value: ${self.total_value:,.2f}   |   Income: ${self.total_income:,.2f}   |   Monthly: ${self.total_income/12:,.2f}"
            )

            self.tree.delete(*self.tree.get_children())

            for t, s, p, v, i in self.enriched:
                self.tree.insert("", "end", values=(
                    t,
                    s,
                    f"${p:,.2f}",
                    f"${v:,.2f}",
                    f"${i:,.2f}"
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def top_income(self):
        top = sorted(self.enriched, key=lambda x: x[4], reverse=True)[:10]

        popup = tk.Toplevel(self.root)
        popup.title("Top Income Contributors")

        text = tk.Text(popup, width=70, height=25)
        text.pack()

        for t, s, p, v, i in top:
            text.insert("end", f"{t}: value ${v:,.2f} → income ${i:,.2f}\n")


# =========================================================
# MAIN
# =========================================================

def main():
    root = tk.Tk()
    app = NorthStarApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
