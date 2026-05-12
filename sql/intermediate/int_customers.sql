-- Per-customer aggregates on clean transactions only.
-- Excludes: cancellations (InvoiceNo starts with C), null CustomerID,
--           non-positive quantity or price.
-- Reference date: 2011-12-09 (last date in the dataset).

CREATE OR REPLACE TABLE int_customers AS
WITH clean AS (
    SELECT *,
        quantity * unit_price AS revenue
    FROM stg_transactions
    WHERE customer_id IS NOT NULL
      AND invoice_no NOT LIKE 'C%'
      AND quantity   > 0
      AND unit_price > 0
),
first_purchase AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(invoice_date)) AS cohort_month,
        MIN(invoice_date)                       AS first_purchase_date
    FROM clean
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    fp.cohort_month,
    fp.first_purchase_date,
    MAX(c.invoice_date)                                              AS last_purchase_date,
    DATE_DIFF('day', MAX(c.invoice_date), DATE '2011-12-09')        AS recency_days,
    COUNT(DISTINCT c.invoice_no)                                     AS frequency,
    ROUND(SUM(c.revenue), 2)                                         AS monetary,
    ROUND(AVG(c.revenue), 2)                                         AS avg_order_value,
    COUNT(DISTINCT c.stock_code)                                     AS unique_products,
    COUNT(DISTINCT c.country)                                        AS countries_count,
    DATE_DIFF('day', fp.first_purchase_date, DATE '2011-12-09')     AS customer_age_days,
    -- Churn label: no purchase in the 90 days before dataset end
    CASE
        WHEN DATE_DIFF('day', MAX(c.invoice_date), DATE '2011-12-09') > 90
        THEN TRUE ELSE FALSE
    END AS is_churned
FROM clean c
JOIN first_purchase fp ON c.customer_id = fp.customer_id
GROUP BY c.customer_id, fp.cohort_month, fp.first_purchase_date;
