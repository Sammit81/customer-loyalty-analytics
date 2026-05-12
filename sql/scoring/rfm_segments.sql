-- RFM segment labels applied to fct_rfm_scores.
-- Segments are defined by R/F/M score combinations.
-- Also joins churn prediction output when available.

CREATE OR REPLACE TABLE rfm_segments AS
SELECT
    r.customer_id,
    r.recency_days,
    r.frequency,
    r.monetary,
    r.r_score,
    r.f_score,
    r.m_score,
    r.rfm_score,
    ic.cohort_month,
    ic.first_purchase_date,
    ic.last_purchase_date,
    ic.avg_order_value,
    ic.unique_products,
    ic.customer_age_days,
    ic.is_churned,
    CASE
        -- High Value: recent, frequent, high spend
        WHEN r.r_score >= 3 AND r.f_score >= 3 AND r.m_score >= 3
            THEN 'High Value'
        -- Loyal: frequent buyers, not necessarily big spenders
        WHEN r.r_score >= 3 AND r.f_score >= 3
            THEN 'Loyal'
        -- At-Risk: used to be good, recency dropping
        WHEN r.r_score <= 2 AND r.f_score >= 3
            THEN 'At-Risk'
        -- Lapsed: haven't purchased recently
        WHEN r.r_score = 1
            THEN 'Lapsed'
        -- Promising: recent but low frequency
        WHEN r.r_score >= 3 AND r.f_score <= 2
            THEN 'Promising'
        -- New: only one or two purchases
        WHEN r.frequency <= 2
            THEN 'New'
        ELSE 'Needs Attention'
    END AS segment
FROM fct_rfm_scores r
JOIN int_customers ic ON r.customer_id = ic.customer_id;
