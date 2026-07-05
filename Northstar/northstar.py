from pathlib import Path
import re
import tkinter as tk
from tkinter import ttk

# =========================================================
# CLEAN UTIL
# =========================================================

def clean_text(x):
    x = str(x)
    x = re.sub(r'\s+', '', x)
    x = re.sub(r'[^\x21-\x7E]', '', x)
    return x.upper()


# =========================================================
# SCHWAB PARSER
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

    def extract_value(line):
        vals = re.findall(r"\$?[\d,]+\.\d{2}", line)
        nums = [float(v.replace("$", "").replace(",", "")) for v in vals]
        return max(nums) if nums else 0.0

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

            value = extract_value(line)
            asset = clean_text(parts[i_asset]) if i_asset else "EQUITY"

            holdings.append({
                "ticker": ticker,
                "shares": qty,
                "value": value,
                "asset": asset
            })

        except:
            continue

    return holdings


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
# CALC ENGINE
# =========================================================

def calculate(holdings):
    total_value = 0
    total_income = 0

    for h in holdings:
        t = h["ticker"]
        v = float(h["value"])

        total_value += v
        y = YIELD.get(t, DEFAULT_YIELD)

        total_income += v * y

    return total_value, total_income


# =========================================================
# GUI APP
# =========================================================

class NorthStarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NorthStar Portfolio Engine v2.0")
        self.root.geometry("900x600")

        self.holdings = load_schwab("schwab.csv")
        self.total_value, self.income = calculate(self.holdings)

        # ================= TOP METRICS =================
        self.frame_top = tk.Frame(root)
        self.frame_top.pack(pady=10)

        self.lbl_value = tk.Label(self.frame_top, text="", font=("Arial", 14))
        self.lbl_value.pack()

        self.lbl_income = tk.Label(self.frame_top, text="", font=("Arial", 14))
        self.lbl_income.pack()

        # ================= BUTTONS =================
        self.frame_btn = tk.Frame(root)
        self.frame_btn.pack(pady=10)

        tk.Button(self.frame_btn, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=5)
        tk.Button(self.frame_btn, text="Show Top Income", command=self.show_top).pack(side=tk.LEFT, padx=5)

        # ================= TABLE =================
        self.tree = ttk.Treeview(root, columns=("ticker", "shares", "value"), show="headings")
        self.tree.heading("ticker", text="Ticker")
        self.tree.heading("shares", text="Shares")
        self.tree.heading("value", text="Value")
        self.tree.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self):
        self.holdings = load_schwab("schwab.csv")
        self.total_value, self.income = calculate(self.holdings)

        self.lbl_value.config(text=f"Portfolio Value: ${self.total_value:,.2f}")
        self.lbl_income.config(text=f"Annual Income: ${self.income:,.2f}  |  Monthly: ${self.income/12:,.2f}")

        for row in self.tree.get_children():
            self.tree.delete(row)

        for h in self.holdings:
            self.tree.insert("", "end", values=(h["ticker"], h["shares"], f"${h['value']:,.2f}"))

    def show_top(self):
        top = sorted(self.holdings, key=lambda x: x["value"], reverse=True)[:10]

        popup = tk.Toplevel(self.root)
        popup.title("Top Holdings")

        text = tk.Text(popup, width=60, height=20)
        text.pack()

        for h in top:
            t = h["ticker"]
            v = h["value"]
            y = YIELD.get(t, DEFAULT_YIELD)
            text.insert("end", f"{t}: ${v:,.2f} → Income ${v*y:,.2f}\n")


# =========================================================
# MAIN
# =========================================================

def main():
    root = tk.Tk()
    app = NorthStarApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
