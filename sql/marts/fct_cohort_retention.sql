-- Cohort retention matrix: for each (cohort_month, period_number) pair,
-- what % of the original cohort is still active?
-- period_number 0 = acquisition month (always 100%).

CREATE OR REPLACE TABLE fct_cohort_retention AS
WITH cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM int_customers
    GROUP BY cohort_month
),
active_by_period AS (
    SELECT
        cohort_month,
        period_number,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM int_cohort_orders
    GROUP BY cohort_month, period_number
)
SELECT
    a.cohort_month,
    -- Pre-formatted label avoids Tableau generating TIMESTAMPADD (unsupported in DuckDB JDBC)
    STRFTIME(a.cohort_month, '%b %Y')      AS cohort_label,
    a.period_number,
    cs.cohort_size,
    a.active_customers,
    ROUND(100.0 * a.active_customers / cs.cohort_size, 2) AS retention_rate
FROM active_by_period a
JOIN cohort_sizes cs ON a.cohort_month = cs.cohort_month
ORDER BY a.cohort_month, a.period_number;
