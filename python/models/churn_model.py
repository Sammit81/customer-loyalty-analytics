"""
Churn prediction: logistic regression on RFM + behavioural features.

Outputs:
  - Classification report and ROC-AUC to stdout
  - Feature importance table to stdout
  - Predictions written back to DuckDB: churn_predictions table
  - Model saved to python/models/churn_model.pkl

Run from project root:
    uv run python/models/churn_model.py
"""
import pickle
from pathlib import Path

import duckdb
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from churn_features import load_features

DB_PATH  = Path(__file__).parent.parent.parent / "data" / "duckdb" / "retail.duckdb"
MODEL_PATH = Path(__file__).parent / "churn_model.pkl"

# recency_days and r_score are excluded: the churn label is defined as
# recency_days > 90, so including them causes perfect data leakage (AUC=1.0).
# The model must learn from purchase behaviour, not from the label definition.
FEATURES = [
    "frequency",
    "monetary",
    "avg_order_value",
    "unique_products",
    "customer_age_days",
    "f_score",
    "m_score",
]


def train() -> None:
    df = load_features()
    print(f"Loaded {len(df):,} customers. Churn rate: {df['label'].mean():.1%}")

    X = df[FEATURES].fillna(0)
    y = df["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_sc, y_train)

    y_pred  = model.predict(X_test_sc)
    y_proba = model.predict_proba(X_test_sc)[:, 1]

    print("\n── Classification Report ──────────────────────────")
    print(classification_report(y_test, y_pred, target_names=["Active", "Churned"]))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")

    print("\n── Feature Importance (log-odds coefficients) ────")
    coef_df = pd.DataFrame({
        "feature": FEATURES,
        "coefficient": model.coef_[0],
    }).sort_values("coefficient", ascending=False)
    print(coef_df.to_string(index=False))

    # Save model + scaler for later scoring
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "scaler": scaler, "features": FEATURES}, f)
    print(f"\nModel saved to {MODEL_PATH}")

    # Score all customers and write predictions back to DuckDB
    all_df = load_features()
    X_all = all_df[FEATURES].fillna(0)
    X_all_sc = scaler.transform(X_all)
    all_df["churn_probability"] = model.predict_proba(X_all_sc)[:, 1]
    all_df["churn_predicted"]   = model.predict(X_all_sc)

    predictions = all_df[["customer_id", "churn_probability", "churn_predicted", "label"]]
    predictions = predictions.rename(columns={"label": "churn_actual"})

    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE OR REPLACE TABLE churn_predictions AS SELECT * FROM predictions")
    (n,) = con.execute("SELECT COUNT(*) FROM churn_predictions").fetchone()
    con.close()

    print(f"Predictions written to DuckDB: {n:,} rows → churn_predictions")


if __name__ == "__main__":
    train()
