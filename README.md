# Customer Loyalty & Cohort Analytics

An end-to-end customer analytics pipeline on the UCI Online Retail dataset (~541k transactions). Covers cohort retention analysis, RFM segmentation, logistic regression churn prediction, campaign uplift analysis, and a Tableau customer health dashboard.

---

## Architecture

```
Online Retail.xlsx (UCI dataset)
    │
    ▼
[Staging]  stg_transactions
    │       Column normalisation, type casting, revenue calculation
    ▼
[Intermediate]
    │   int_customers          — per-customer RFM inputs, cohort month, churn label
    │   int_cohort_orders      — monthly activity tagged with cohort, period number
    ▼
[Marts]
    │   fct_rfm_scores         — R/F/M quartile scores (1–4) + composite score
    │   fct_cohort_retention   — cohort × period retention matrix (% retained)
    │   fct_campaign_uplift    — pre/post holiday campaign behaviour comparison
    ▼
[Scoring]  rfm_segments
    │       Segment labels: High Value · Loyal · At-Risk · Lapsed · Promising · New
    ▼
[Python ML]  churn_model.py
    │         Logistic regression on 9 RFM + behavioural features
    │         Predictions written back to DuckDB: churn_predictions
    ▼
[Tableau]  Customer health dashboard
           Segment trends · Retention heatmap · Churn risk · Campaign uplift
```

---

## Key Findings

*(To be filled after running the pipeline — update with actual numbers)*

**Dataset**: ~541k transactions, ~4,300 customers (after removing null CustomerIDs), Dec 2010–Dec 2011. UK-based online retailer.

**RFM Segments**: Six segments — High Value, Loyal, At-Risk, Lapsed, Promising, New — defined by quartile combinations on recency, frequency, and monetary spend.

**Churn label**: No purchase in the 90 days before dataset end (2011-12-09). ~XX% churn rate.

**Cohort retention**: Typical e-commerce pattern — sharp drop after month 0, with a loyal core persisting 6–12 months.

**Campaign uplift**: Holiday window (Nov–Dec 2011) compared against the equivalent 60-day pre-period (Sep–Oct 2011).

---

## Tech Stack

| Tool | Role | Why |
|------|------|-----|
| **DuckDB** | Analytics database | In-process, no server, handles 500k rows trivially. File-based for portability. |
| **SQL (medallion layers)** | Transformation | Same staging → intermediate → marts → scoring pattern as the fraud project — each layer independently queryable. |
| **pandas** | Data loading | Reading the `.xlsx` source; DuckDB takes over once data is in-memory. |
| **scikit-learn** | Churn model | Logistic regression: interpretable coefficients, directly answers "which features drive churn?" |
| **Tableau Desktop** | Dashboard | Retention heatmap, segment KPI tiles, churn risk scatter, campaign uplift bars. |

---

## Setup

**Prerequisites**: Python 3.9+, `uv`. Download the dataset first:

1. Go to https://archive.ics.uci.edu/dataset/352/online+retail
2. Download `Online Retail.xlsx`
3. Place it in `data/raw/Online Retail.xlsx`

```bash
# Install dependencies
uv sync

# Load raw data into DuckDB
uv run python/load_data.py

# Build all SQL layers
uv run python/run_sql.py

# Train churn model and write predictions to DuckDB
uv run python/models/churn_model.py
```

---

## Dashboard

Built in Tableau Desktop, connecting to `data/duckdb/retail.duckdb`.

| Page | What it shows |
|------|--------------|
| Customer Overview | Segment distribution, total customers, revenue by segment |
| Cohort Retention | Heatmap: cohort month × period, colour = retention % |
| Churn Risk | Scatter of customers by churn probability vs. monetary value |
| Campaign Uplift | Pre/post revenue and order frequency by campaign response group |

*Screenshots — add after dashboard is built.*

---

## What I'd Do Next

- **Survival analysis**: Kaplan-Meier curves per segment would give a more rigorous lifetime estimate than the 90-day binary churn label.
- **Random forest comparison**: benchmark against logistic regression on AUC and feature importance consistency.
- **CLV model**: combine churn probability with average order value to produce a customer lifetime value score for each segment.
- **Proper campaign groups**: the current uplift analysis uses a date-based proxy for campaign exposure; a real A/B test flag in the data would allow true causal uplift measurement.
