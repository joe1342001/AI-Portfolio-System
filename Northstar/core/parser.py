from pathlib import Path
import streamlit as st


def get_base_path():
    return Path(__file__).resolve().parent.parent


def load_schwab_csv_debug(file_path="data/schwab.csv"):

    st.write("🔍 STEP 1: Starting parser debug")

    base_path = get_base_path()
    full_path = base_path / file_path

    # =========================================================
    # STEP 2: PATH CHECK
    # =========================================================

    st.write("📁 Base Path:", base_path)
    st.write("📁 Full Path:", full_path)
    st.write("📁 File Exists:", full_path.exists())

    if not full_path.exists():
        st.error("❌ FILE NOT FOUND — STOPPING HERE")
        return []

    # =========================================================
    # STEP 3: READ FILE
    # =========================================================

    lines = full_path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()

    st.write("📄 Total Lines:", len(lines))

    # =========================================================
    # STEP 4: FIND HEADER
    # =========================================================

    header_index = None

    for i, line in enumerate(lines):
        if "Symbol" in line and "Qty" in line:
            header_index = i
            break

    st.write("📌 Header Index Found:", header_index)

    if header_index is None:
        st.error("❌ HEADER NOT FOUND — CSV FORMAT ISSUE")
        st.write("First 5 lines for inspection:")
        for l in lines[:5]:
            st.write(l)
        return []

    headers = [h.strip().strip('"') for h in lines[header_index].split('","')]

    st.write("📊 Headers Detected:", headers)

    # =========================================================
    # STEP 5: COLUMN MAPPING
    # =========================================================

    def col(name):
        for i, h in enumerate(headers):
            if name.lower() in h.lower():
                return i
        return None

    i_symbol = col("Symbol")
    i_qty = col("Qty")
    i_price = col("Price")
    i_value = col("Mkt Val")
    i_asset = col("Asset Type")

    st.write("🔎 Column Mapping:")
    st.write("Symbol:", i_symbol)
    st.write("Qty:", i_qty)
    st.write("Price:", i_price)
    st.write("Value:", i_value)
    st.write("Asset:", i_asset)

    # =========================================================
    # STEP 6: PARSE ROWS
    # =========================================================

    holdings = []
    parse_errors = 0

    for idx, line in enumerate(lines[header_index + 1:]):

        if not line.startswith('"'):
            continue

        parts = [p.strip().strip('"') for p in line.split('","')]

        try:
            ticker = parts[i_symbol]

            if not ticker or "Total" in ticker:
                continue

            shares = float(parts[i_qty].replace(",", ""))

            price = float(parts[i_price].replace("$", "").replace(",", "") or 0)
            value = float(parts[i_value].replace("$", "").replace(",", "") or 0)

            asset_type = parts[i_asset] if i_asset else "Equity"

            holdings.append({
                "ticker": ticker,
                "shares": shares,
                "price": price,
                "value": value,
                "asset_type": asset_type
            })

        except Exception as e:
            parse_errors += 1
            st.write(f"⚠️ Row {idx} parse error:", e)

    # =========================================================
    # STEP 7: FINAL RESULTS
    # =========================================================

    st.write("📦 HOLDINGS PARSED:", len(holdings))
    st.write("⚠️ PARSE ERRORS:", parse_errors)

    if holdings:
        st.write("📊 SAMPLE HOLDING:", holdings[0])

    return holdings
