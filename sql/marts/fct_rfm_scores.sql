-- RFM scoring: assign each customer a 1–4 score on Recency, Frequency,
-- and Monetary value using quartiles.
-- Lower recency_days = more recent = better, so recency is scored inversely.

CREATE OR REPLACE TABLE fct_rfm_scores AS
WITH quartiles AS (
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary,
        -- Recency: lower days = better, so rank ASC then invert
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC)     AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC)      AS m_score
    FROM int_customers
)
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    -- Composite RFM score string for readable labelling
    CONCAT(r_score::VARCHAR, f_score::VARCHAR, m_score::VARCHAR) AS rfm_cell,
    -- Single aggregate score (weighted: recency matters most)
    ROUND((r_score * 0.4 + f_score * 0.3 + m_score * 0.3), 2)   AS rfm_score
FROM quartiles;
