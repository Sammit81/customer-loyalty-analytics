# Architecture & Design Decisions

## Churn label definition

Churn is defined as no purchase in the 90 days before the dataset end date (2011-12-09). This is a binary proxy — not a survival model. 90 days was chosen because the dataset spans ~13 months; shorter windows (30/60 days) would over-label seasonal inactivity as churn given the holiday-heavy end of the dataset. A production system would use a rolling window or Kaplan-Meier survival curves.

## RFM scoring: quartiles, not arbitrary thresholds

Each dimension is scored 1–4 using `NTILE(4)`. This is distribution-relative — a "4" means top quartile of this customer base, not an absolute threshold. The tradeoff is that scores aren't comparable across time periods without re-scoring, but for a single-snapshot analysis it's more robust than picking thresholds manually.

Recency is scored inversely (more recent = better): `NTILE(4) OVER (ORDER BY recency_days DESC)`.

## Composite RFM weight

`rfm_score = r_score × 0.4 + f_score × 0.3 + m_score × 0.3`

Recency is weighted higher because it's the strongest predictor of near-term purchase probability — a customer who bought yesterday is more actionable than one who spent more two years ago. This is a common industry weighting; adjust if A/B testing shows frequency is a stronger signal for this specific retailer.

## Campaign uplift window

No explicit campaign flag exists in the UCI dataset. The holiday window (2011-11-01 to 2011-12-31) is used as a proxy for "post-campaign" and compared against an equivalent 60-day pre-window (2011-09-02 to 2011-10-31). This measures correlation, not causal uplift — without a randomised control group, the revenue increase during the holiday period can't be attributed solely to the campaign. Documented as a known limitation in the README.

## Data cleaning decisions

- **Null CustomerID (~25% of rows)**: dropped. These are guest/anonymous transactions and cannot be linked to customer-level behaviour. Including them would inflate transaction counts but add no customer signal.
- **Cancellations (InvoiceNo starts with 'C')**: dropped from all analysis. They represent reversals, not genuine demand. A more complete model would net cancellations against originals.
- **Non-positive quantity/price**: dropped. These appear to be data entry errors and internal adjustments.

## SQL layer design

Same medallion pattern as the fraud project (staging → intermediate → marts → scoring). DuckDB chosen for the same reasons: self-contained file, no server, handles 500k rows well.

## Logistic regression over tree models

Logistic regression is the right first model here because:
1. The coefficients directly answer "which features drive churn?" — interpretable for a business audience
2. With only ~4,300 customers and 9 features, a complex model would overfit
3. The feature relationships (recency → churn, frequency → retention) are expected to be monotonic, which logistic regression captures well

Random forest is noted as a future comparison point.
