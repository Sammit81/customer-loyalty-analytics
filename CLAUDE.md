# CLAUDE.md

## Commands

```bash
uv sync                            # install dependencies
uv run python/load_data.py         # load raw Excel/CSV into DuckDB staging
uv run python/run_sql.py           # build intermediate → marts → scoring layers
uv run python/models/churn_model.py  # train and evaluate churn model
```

## Architecture

Customer loyalty analytics pipeline on the UCI Online Retail dataset (~541k transactions, Dec 2010–Dec 2011):

1. Raw Excel → DuckDB staging (`stg_transactions`)
2. Intermediate: cleaned transactions, customer-level aggregates, cohort assignments
3. Marts: RFM scores, cohort retention matrix, campaign uplift
4. Scoring: RFM segment labels (High Value, Loyal, At-Risk, Lapsed, New)
5. Python ML: churn prediction model (features from DuckDB, model trained in scikit-learn)
6. Tableau dashboard: segment trends, retention heatmap, churn risk scores, campaign uplift

### Key files

- `python/load_data.py` — loads `data/raw/Online Retail.xlsx` into `stg_transactions`
- `python/run_sql.py` — executes SQL layers in dependency order
- `sql/intermediate/int_customers.sql` — per-customer aggregates (recency, frequency, monetary, cohort month)
- `sql/marts/fct_rfm_scores.sql` — RFM quintile scoring
- `sql/marts/fct_cohort_retention.sql` — monthly cohort × period retention matrix
- `sql/marts/fct_campaign_uplift.sql` — pre/post promotion behaviour comparison
- `sql/scoring/rfm_segments.sql` — segment labels applied to RFM scores
- `python/models/churn_features.py` — pulls churn feature matrix from DuckDB
- `python/models/churn_model.py` — trains RandomForest, outputs feature importance and predictions

### Data notes

- Remove cancelled orders: `InvoiceNo` starting with `'C'`
- Remove rows with NULL `CustomerID` (~25% of rows)
- Remove negative `UnitPrice` and zero/negative `Quantity`
- Revenue = `Quantity × UnitPrice`
- Churn label: no purchase in the 90 days before the dataset end date (2011-12-09)

### Environment

No API keys required. All computation is local DuckDB + Python.
Dataset: download `Online Retail.xlsx` from https://archive.ics.uci.edu/dataset/352/online+retail
and place in `data/raw/`.
