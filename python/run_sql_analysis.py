"""
SIMPLE SQL ANALYSIS - NO DB BROWSER NEEDED!
This script loads your data into SQLite and runs all SQL queries automatically

Save as: run_sql_analysis.py
Put it in the same folder as your raw_inventory_data.csv
"""

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

print("  SQL ANALYSIS TOOL")
print("="*70)

# Find the CSV file (checking Desktop and current directory)
desktop_path = Path.home() / "Desktop" / "inventory-defect-analysis" / "raw_inventory_data.csv"
local_path = Path("raw_inventory_data.csv")
onedrive_path = Path.home() / "OneDrive - Algonquin College" / "Documents" / "Project" / "inventory-defect-analysis" / "python" / "raw_inventory_data.csv"

if onedrive_path.exists():
    csv_file = onedrive_path
    output_folder = onedrive_path.parent
    print(f"Found data in OneDrive: {csv_file}")
elif desktop_path.exists():
    csv_file = desktop_path
    output_folder = desktop_path.parent
    print(f"Found data on Desktop: {csv_file}")
elif local_path.exists():
    csv_file = local_path
    output_folder = Path(".")
    print(f" Found data in current directory: {csv_file}")
else:
    print(" ERROR: Cannot find raw_inventory_data.csv")
    print("   Please run the data generator first!")
    exit()

# Load data
print(f"\n Loading {csv_file.name}...")
df = pd.read_csv(csv_file)
print(f"    Loaded {len(df):,} records")
print(f"   Columns: {', '.join(df.columns.tolist())}")

# Create SQLite database
db_file = output_folder / "inventory_analysis.db"
print(f"\n Creating SQLite database: {db_file}")

conn = sqlite3.connect(db_file)
df.to_sql('inventory_transactions', conn, if_exists='replace', index=False)
print("    Data loaded into database!")

# Create output file for results
output_file = output_folder / "sql_analysis_results.txt"
results = []

def run_query(title, query):
    """Run a SQL query and save results"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print("="*70)
    
    try:
        result_df = pd.read_sql_query(query, conn)
        print(result_df.to_string(index=False))
        
        # Save to results file
        results.append(f"\n{'='*70}")
        results.append(f"{title}")
        results.append(f"{'='*70}")
        results.append(result_df.to_string(index=False))
        results.append("\n")
        
        return result_df
    except Exception as e:
        print(f"    Error: {e}")
        return None

print("\n" + "="*70)
print("RUNNING SQL ANALYSES")
print("="*70)

# Query 1: Overall Summary
query1 = """
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) as total_defects,
    ROUND(
        SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) as defect_rate_pct,
    ROUND(
        100 - (SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
        2
    ) as accuracy_rate_pct
FROM inventory_transactions
"""
result1 = run_query("1️  OVERALL DEFECT SUMMARY", query1)

# Query 2: Root Cause Analysis
query2 = """
SELECT 
    defect_type,
    COUNT(*) as incident_count,
    ROUND(AVG(ABS(qty_variance)), 2) as avg_variance,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM inventory_transactions WHERE has_defect = 1), 2) as percentage
FROM inventory_transactions
WHERE has_defect = 1
GROUP BY defect_type
ORDER BY incident_count DESC
"""
result2 = run_query("2️  ROOT CAUSE ANALYSIS", query2)

# Query 3: Warehouse Performance
query3 = """
SELECT 
    warehouse,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) as defect_count,
    ROUND(
        SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) as defect_rate,
    ROUND(
        100 - (SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
        2
    ) as accuracy_rate
FROM inventory_transactions
GROUP BY warehouse
ORDER BY defect_rate ASC
"""
result3 = run_query("3️  WAREHOUSE PERFORMANCE", query3)

# Query 4: Entry Method Comparison
query4 = """
SELECT 
    entry_method,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) as defect_count,
    ROUND(
        SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) as defect_rate
FROM inventory_transactions
GROUP BY entry_method
ORDER BY defect_rate DESC
"""
result4 = run_query("4️  ENTRY METHOD IMPACT", query4)

# Query 5: Top Problematic Operators
query5 = """
SELECT 
    operator_id,
    COUNT(*) as transactions,
    SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) as errors,
    ROUND(
        SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) as error_rate
FROM inventory_transactions
WHERE entry_method = 'Manual'
GROUP BY operator_id
HAVING COUNT(*) > 100
ORDER BY error_rate DESC
LIMIT 10
"""
result5 = run_query("5️  TOP 10 OPERATORS NEEDING TRAINING", query5)

# Query 6: Severity Analysis
query6 = """
SELECT 
    CASE 
        WHEN ABS(qty_variance) > 50 THEN 'Critical'
        WHEN ABS(qty_variance) > 20 THEN 'High'
        WHEN ABS(qty_variance) > 5 THEN 'Medium'
        ELSE 'Low'
    END as severity,
    COUNT(*) as incident_count,
    ROUND(AVG(ABS(qty_variance)), 2) as avg_variance
FROM inventory_transactions
WHERE has_defect = 1
GROUP BY 
    CASE 
        WHEN ABS(qty_variance) > 50 THEN 'Critical'
        WHEN ABS(qty_variance) > 20 THEN 'High'
        WHEN ABS(qty_variance) > 5 THEN 'Medium'
        ELSE 'Low'
    END
ORDER BY 
    CASE severity
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        ELSE 4
    END
"""
result6 = run_query("6️  DEFECT SEVERITY DISTRIBUTION", query6)

# Query 7: Monthly Trends
query7 = """
SELECT 
    SUBSTR(date, 1, 7) as month,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) as defects,
    ROUND(
        SUM(CASE WHEN has_defect = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) as defect_rate
FROM inventory_transactions
GROUP BY SUBSTR(date, 1, 7)
ORDER BY month
"""
result7 = run_query("7️  MONTHLY DEFECT TRENDS", query7)

# Close connection
conn.close()

# Save all results to file
print("\n" + "="*70)
print(" SAVING RESULTS TO FILE")
print("="*70)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("INVENTORY DEFECT ANALYSIS - SQL QUERY RESULTS\n")
    f.write(f"Generated: {datetime.now()}\n")
    f.write(''.join(results))

print(f"\n All results saved to: {output_file}")
print(f"\n Summary of Key Findings:")

if result1 is not None:
    print(f"   • Total Records: {result1['total_records'][0]:,}")
    print(f"   • Total Defects: {result1['total_defects'][0]:,}")
    print(f"   • Defect Rate: {result1['defect_rate_pct'][0]}%")
    print(f"   • Accuracy Rate: {result1['accuracy_rate_pct'][0]}%")

if result2 is not None and len(result2) > 0:
    print(f"\n    Top Root Cause: {result2['defect_type'][0]}")
    print(f"      ({result2['percentage'][0]}% of all defects)")

if result3 is not None and len(result3) > 0:
    best_wh = result3.iloc[0]
    worst_wh = result3.iloc[-1]
    print(f"\n    Best Warehouse: {best_wh['warehouse']} ({best_wh['accuracy_rate']}% accuracy)")
    print(f"     Needs Work: {worst_wh['warehouse']} ({worst_wh['defect_rate']}% defect rate)")

print("\n" + "="*70)
print(" SQL ANALYSIS COMPLETE!")
print("="*70)
print("\nFiles created:")
print(f"   1. {db_file}")
print(f"   2. {output_file}")
print("\nNext steps:")
print("   1. Review the results above")
print("   2. Open sql_analysis_results.txt for full report")
print("   3. Take screenshots for your portfolio")
print("   4. You can also import the .db file into DB Browser if you want")
print("="*70)