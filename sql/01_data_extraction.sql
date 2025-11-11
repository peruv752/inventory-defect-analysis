-- 01_data_extraction.sql
-- Extract inventory records with defects

SELECT 
    transaction_id,
    date,
    warehouse,
    sku,
    expected_qty,
    actual_qty,
    qty_variance,
    defect_type,
    entry_method,
    operator_id,
    CASE 
        WHEN ABS(qty_variance) > 50 THEN 'Critical'
        WHEN ABS(qty_variance) > 20 THEN 'High'
        WHEN ABS(qty_variance) > 5 THEN 'Medium'
        ELSE 'Low'
    END AS severity_level
FROM inventory_transactions
WHERE has_defect = 1
ORDER BY date DESC;

-- 02_defect_analysis.sql
-- Root cause analysis by defect type

SELECT 
    defect_type,
    COUNT(*) AS incident_count,
    AVG(ABS(qty_variance)) AS avg_variance,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS percentage
FROM inventory_transactions
WHERE has_defect = 1
GROUP BY defect_type
ORDER BY incident_count DESC;

-- Warehouse performance comparison
SELECT 
    warehouse,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) AS defect_count,
    ROUND(
        SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) AS defect_rate,
    ROUND(
        100 - (SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
        2
    ) AS accuracy_rate
FROM inventory_transactions
GROUP BY warehouse
ORDER BY defect_rate ASC;

-- Operator performance (root cause: training gap)
SELECT 
    operator_id,
    COUNT(*) AS transactions_processed,
    SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) AS errors,
    ROUND(
        SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) AS error_rate,
    entry_method
FROM inventory_transactions
WHERE entry_method = 'Manual'
GROUP BY operator_id, entry_method
HAVING COUNT(*) > 100
ORDER BY error_rate DESC
LIMIT 10;

-- Trend analysis by month
SELECT 
    DATE_FORMAT(date, '%Y-%m') AS month,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) AS defects,
    ROUND(
        SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) AS defect_rate
FROM inventory_transactions
GROUP BY DATE_FORMAT(date, '%Y-%m')
ORDER BY month;

-- 03_sox_compliance_validation.sql
-- Data integrity check (ensures 100% audit trail)

SELECT 
    'Total Records' AS metric,
    COUNT(*) AS value
FROM inventory_transactions
UNION ALL
SELECT 
    'Records with Timestamps' AS metric,
    COUNT(*) AS value
FROM inventory_transactions
WHERE date IS NOT NULL
UNION ALL
SELECT 
    'Data Integrity Score' AS metric,
    ROUND(
        COUNT(CASE WHEN date IS NOT NULL 
              AND warehouse IS NOT NULL 
              AND operator_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS value
FROM inventory_transactions;