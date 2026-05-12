-- Campaign uplift: compare customer behaviour in the 60 days before
-- and after the Black Friday / holiday campaign window (2011-11-01).
-- Customers active in both windows are the "exposed" group;
-- customers only active before are the control baseline.

CREATE OR REPLACE TABLE fct_campaign_uplift AS
WITH clean AS (
    SELECT
        customer_id,
        invoice_no,
        invoice_date,
        quantity * unit_price AS revenue
    FROM stg_transactions
    WHERE customer_id IS NOT NULL
      AND invoice_no NOT LIKE 'C%'
      AND quantity   > 0
      AND unit_price > 0
),
pre AS (
    -- 60-day pre-campaign window: 2011-09-02 to 2011-11-01
    SELECT
        customer_id,
        COUNT(DISTINCT invoice_no)  AS pre_orders,
        ROUND(SUM(revenue), 2)      AS pre_revenue,
        ROUND(AVG(revenue), 2)      AS pre_avg_order
    FROM clean
    WHERE invoice_date BETWEEN DATE '2011-09-02' AND DATE '2011-10-31'
    GROUP BY customer_id
),
post AS (
    -- 60-day post-campaign window: 2011-11-01 to 2011-12-31
    SELECT
        customer_id,
        COUNT(DISTINCT invoice_no)  AS post_orders,
        ROUND(SUM(revenue), 2)      AS post_revenue,
        ROUND(AVG(revenue), 2)      AS post_avg_order
    FROM clean
    WHERE invoice_date BETWEEN DATE '2011-11-01' AND DATE '2011-12-31'
    GROUP BY customer_id
)
SELECT
    COALESCE(pre.customer_id, post.customer_id) AS customer_id,
    COALESCE(pre.pre_orders,  0)                AS pre_orders,
    COALESCE(pre.pre_revenue, 0)                AS pre_revenue,
    COALESCE(pre.pre_avg_order, 0)              AS pre_avg_order,
    COALESCE(post.post_orders,  0)              AS post_orders,
    COALESCE(post.post_revenue, 0)              AS post_revenue,
    COALESCE(post.post_avg_order, 0)            AS post_avg_order,
    -- Uplift metrics
    COALESCE(post.post_orders,  0) - COALESCE(pre.pre_orders,  0)  AS order_uplift,
    COALESCE(post.post_revenue, 0) - COALESCE(pre.pre_revenue, 0)  AS revenue_uplift,
    CASE
        WHEN pre.customer_id IS NOT NULL AND post.customer_id IS NOT NULL THEN 'retained'
        WHEN pre.customer_id IS NOT NULL AND post.customer_id IS NULL     THEN 'lapsed_post'
        WHEN pre.customer_id IS NULL     AND post.customer_id IS NOT NULL THEN 'new_post'
    END AS campaign_response
FROM pre
FULL OUTER JOIN post ON pre.customer_id = post.customer_id;
