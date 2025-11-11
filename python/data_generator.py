"""
STEP 1: Generate Sample Inventory Data
Run this first to create your dataset!

This creates 50,000 inventory records with intentional defects
Save as: data_generator.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

print("🚀 Starting data generation...")

# Configuration
n_records = 50000
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 6, 30)

# Generate base inventory data
print("📊 Generating 50,000 inventory records...")

data = {
    'transaction_id': range(1, n_records + 1),
    'date': [start_date + timedelta(days=np.random.randint(0, 180)) for _ in range(n_records)],
    'warehouse': np.random.choice(['WH-A', 'WH-B', 'WH-C', 'WH-D'], n_records),
    'sku': [f'SKU-{np.random.randint(1000, 9999)}' for _ in range(n_records)],
    'expected_qty': np.random.randint(1, 500, n_records),
    'actual_qty': np.random.randint(1, 500, n_records),
    'location': [f'Aisle-{np.random.randint(1,20)}-Bin-{np.random.randint(1,50)}' for _ in range(n_records)],
    'operator_id': np.random.choice([f'OP-{i:03d}' for i in range(1, 51)], n_records),
    'entry_method': np.random.choice(['Manual', 'Scanner', 'System'], n_records, p=[0.4, 0.5, 0.1])
}

df = pd.DataFrame(data)

# Create defects (intentional discrepancies)
print("🔍 Introducing defects for analysis...")

df['qty_variance'] = df['actual_qty'] - df['expected_qty']
df['has_defect'] = abs(df['qty_variance']) > 5

# Categorize defect types
defect_types = []
for idx, row in df.iterrows():
    if row['has_defect']:
        if abs(row['qty_variance']) > 50:
            defect_types.append('Count Discrepancy')
        elif row['entry_method'] == 'Manual':
            defect_types.append('Manual Entry Error')
        elif row['entry_method'] == 'Scanner':
            defect_types.append('Scanner Malfunction')
        else:
            defect_types.append('System Error')
    else:
        defect_types.append('No Defect')

df['defect_type'] = defect_types

# Add additional defect flags
df['is_damaged'] = np.random.choice([True, False], n_records, p=[0.03, 0.97])
df['label_missing'] = np.random.choice([True, False], n_records, p=[0.04, 0.96])

# Calculate warehouse-specific defect rates
df['defect_rate'] = df.groupby('warehouse')['has_defect'].transform('mean') * 100

# Save to CSV
output_file = 'raw_inventory_data.csv'
df.to_csv(output_file, index=False)

# Print summary
print("\n✅ DATA GENERATION COMPLETE!")
print("=" * 60)
print(f"📁 File saved: {output_file}")
print(f"📊 Total records: {n_records:,}")
print(f"❌ Total defects: {df['has_defect'].sum():,}")
print(f"📈 Overall defect rate: {(df['has_defect'].sum() / n_records * 100):.2f}%")
print("\n🏢 Warehouse Breakdown:")
print(df.groupby('warehouse').agg({
    'transaction_id': 'count',
    'has_defect': 'sum'
}).rename(columns={'transaction_id': 'Total', 'has_defect': 'Defects'}))

print("\n🔍 Defect Type Distribution:")
print(df[df['has_defect']]['defect_type'].value_counts())

print("\n" + "=" * 60)
print("NEXT STEP: Run the SQL queries on this data!")
print("File location:", output_file)