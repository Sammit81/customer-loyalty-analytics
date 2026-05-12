-- Monthly activity per customer, tagged with their cohort month.
-- Used to build the cohort retention matrix in the mart layer.

CREATE OR REPLACE TABLE int_cohort_orders AS
WITH clean AS (
    SELECT
        customer_id,
        invoice_no,
        DATE_TRUNC('month', invoice_date) AS order_month
    FROM stg_transactions
    WHERE customer_id IS NOT NULL
      AND invoice_no NOT LIKE 'C%'
      AND quantity   > 0
      AND unit_price > 0
    GROUP BY customer_id, invoice_no, DATE_TRUNC('month', invoice_date)
)
SELECT
    c.customer_id,
    ic.cohort_month,
    c.order_month,
    -- Months since first purchase (0 = acquisition month)
    DATE_DIFF('month', ic.cohort_month, c.order_month) AS period_number
FROM clean c
JOIN int_customers ic ON c.customer_id = ic.customer_id;
