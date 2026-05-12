"""
Load the UCI Online Retail dataset into DuckDB staging.

Source: data/raw/Online Retail.xlsx  (or .csv if pre-converted)
Target: stg_transactions in data/duckdb/retail.duckdb

Run from project root:
    uv run python/load_data.py
"""

import duckdb
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "duckdb" / "retail.duckdb"

XLSX_FILE = RAW_DIR / "Online Retail.xlsx"
CSV_FILE  = RAW_DIR / "online_retail.csv"


def load_source() -> pd.DataFrame:
    """Read whichever source file is present."""
    if CSV_FILE.exists():
        print(f"Reading {CSV_FILE.name} ...")
        df = pd.read_csv(CSV_FILE, encoding="latin-1", dtype=str)
    elif XLSX_FILE.exists():
        print(f"Reading {XLSX_FILE.name} (this takes ~30 seconds for the xlsx) ...")
        df = pd.read_excel(XLSX_FILE, dtype=str)
    else:
        raise FileNotFoundError(
            f"No source file found. Place 'Online Retail.xlsx' or 'online_retail.csv' in {RAW_DIR}"
        )
    return df


def normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to snake_case and cast types."""
    df = df.rename(columns={
        "InvoiceNo":    "invoice_no",
        "StockCode":    "stock_code",
        "Description":  "description",
        "Quantity":     "quantity",
        "InvoiceDate":  "invoice_date",
        "UnitPrice":    "unit_price",
        "CustomerID":   "customer_id",
        "Country":      "country",
    })

    df["quantity"]     = pd.to_numeric(df["quantity"],   errors="coerce")
    df["unit_price"]   = pd.to_numeric(df["unit_price"], errors="coerce")
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["customer_id"]  = df["customer_id"].str.strip()

    return df


def print_summary(con: duckdb.DuckDBPyConnection) -> None:
    total = con.execute("SELECT COUNT(*) FROM stg_transactions").fetchone()[0]
    print(f"\n── stg_transactions: {total:,} rows total ──────────────────")

    print("\nRow counts by data quality status:")
    rows = con.execute("""
        SELECT
            CASE
                WHEN customer_id IS NULL          THEN 'null_customer_id'
                WHEN invoice_no LIKE 'C%'         THEN 'cancellation'
                WHEN quantity   <= 0              THEN 'non_positive_qty'
                WHEN unit_price <= 0              THEN 'non_positive_price'
                ELSE                                   'clean'
            END AS status,
            COUNT(*) AS n,
            ROUND(100.0 * COUNT(*) / ? , 1) AS pct
        FROM stg_transactions
        GROUP BY 1
        ORDER BY n DESC
    """, [total]).fetchall()
    for status, n, pct in rows:
        print(f"  {status:<25} {n:>8,}  ({pct}%)")

    print("\nDate range:")
    row = con.execute("""
        SELECT MIN(invoice_date), MAX(invoice_date)
        FROM stg_transactions
        WHERE customer_id IS NOT NULL
    """).fetchone()
    print(f"  {row[0]}  →  {row[1]}")

    print("\nTop 5 countries by transaction count:")
    rows = con.execute("""
        SELECT country, COUNT(*) AS n
        FROM stg_transactions
        WHERE customer_id IS NOT NULL
        GROUP BY country ORDER BY n DESC LIMIT 5
    """).fetchall()
    for country, n in rows:
        print(f"  {country:<30} {n:>8,}")


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = load_source()
    df = normalise(df)
    print(f"Loaded {len(df):,} rows from source.")

    con = duckdb.connect(str(DB_PATH))

    print("Writing stg_transactions ...")
    con.execute("CREATE OR REPLACE TABLE stg_transactions AS SELECT * FROM df")

    print_summary(con)
    con.close()
    print(f"\nDone. Database written to {DB_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
