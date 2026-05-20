"""
Export DuckDB tables to CSV for Tableau Public.

Tableau Public cannot connect to local files via JDBC, so we export
the four dashboard tables as CSVs. Connect Tableau Public to these files.

Run from project root:
    uv run python/export_for_tableau.py
"""
import duckdb
from pathlib import Path

DB_PATH     = Path(__file__).parent.parent / "data" / "duckdb" / "retail.duckdb"
EXPORT_DIR  = Path(__file__).parent.parent / "data" / "tableau_exports"

TABLES = {
    "rfm_segments":        "rfm_segments.csv",
    "fct_cohort_retention": "fct_cohort_retention.csv",
    "churn_predictions":   "churn_predictions.csv",
    "fct_campaign_uplift": "fct_campaign_uplift.csv",
}


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)

    for table, filename in TABLES.items():
        out_path = EXPORT_DIR / filename
        con.execute(f"COPY {table} TO '{out_path}' (HEADER, DELIMITER ',')")
        rows = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<30} {rows:>6,} rows → {filename}")

    con.close()
    print(f"\nExported to {EXPORT_DIR.relative_to(Path.cwd())}/")
    print("Connect Tableau Public to these CSV files to build the dashboard.")


if __name__ == "__main__":
    main()
