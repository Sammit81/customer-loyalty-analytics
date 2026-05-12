"""Pull churn feature matrix from DuckDB."""
import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "duckdb" / "retail.duckdb"


def load_features() -> pd.DataFrame:
    """Return a DataFrame with one row per customer, ready for modelling."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("""
        SELECT
            customer_id,
            recency_days,
            frequency,
            monetary,
            avg_order_value,
            unique_products,
            customer_age_days,
            r_score,
            f_score,
            m_score,
            rfm_score,
            is_churned AS label
        FROM rfm_segments
        WHERE customer_age_days > 0
    """).df()
    con.close()
    return df
