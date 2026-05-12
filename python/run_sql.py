"""Execute the SQL layer pipeline in dependency order."""
import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "duckdb" / "retail.duckdb"

SQL_STEPS = [
    ("int_customers",        "sql/intermediate/int_customers.sql"),
    ("int_cohort_orders",    "sql/intermediate/int_cohort_orders.sql"),
    ("fct_rfm_scores",       "sql/marts/fct_rfm_scores.sql"),
    ("fct_cohort_retention", "sql/marts/fct_cohort_retention.sql"),
    ("fct_campaign_uplift",  "sql/marts/fct_campaign_uplift.sql"),
    ("rfm_segments",         "sql/scoring/rfm_segments.sql"),
]


def main():
    root = Path(__file__).parent.parent
    con = duckdb.connect(str(DB_PATH))

    for table_name, sql_path in SQL_STEPS:
        full_path = root / sql_path
        sql = full_path.read_text()
        print(f"Running {sql_path} ...", end=" ", flush=True)
        con.execute(sql)
        (row_count,) = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        print(f"{row_count:,} rows → {table_name}")

    con.close()
    print("\nSQL pipeline complete.")


if __name__ == "__main__":
    main()
