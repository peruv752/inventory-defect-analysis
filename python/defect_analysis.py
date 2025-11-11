"""
STEP 3: Python Data Analysis & Visualization
Run this after generating the data

This performs root cause analysis, creates visualizations,
and generates insights for your portfolio

Save as: defect_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

print(" Loading inventory data...")

# Load the generated data
try:
    df = pd.read_csv('raw_inventory_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    print(f" Loaded {len(df):,} records")
except FileNotFoundError:
    print(" ERROR: raw_inventory_data.csv not found!")
    print("   Please run data_generator.py first")
    exit()

print("\n" + "="*70)
print(" INVENTORY DEFECT ANALYSIS REPORT")
print("="*70)

# ============================================================
# 1. DATA INTEGRITY VALIDATION
# ============================================================

def validate_data_integrity(df):
    """Ensure data quality meets SOX compliance standards"""
    print("\n DATA INTEGRITY VALIDATION")
    print("-" * 70)
    
    total_records = len(df)
    null_counts = df.isnull().sum()
    
    # Calculate integrity score
    total_cells = total_records * len(df.columns)
    null_cells = null_counts.sum()
    integrity_score = (1 - (null_cells / total_cells)) * 100
    
    print(f"Total Records: {total_records:,}")
    print(f"Complete Records: {df.dropna().shape[0]:,}")
    print(f"Data Integrity Score: {integrity_score:.2f}%")
    
    if integrity_score >= 99:
        print(" PASSED - Meets SOX compliance requirements (99%+ threshold)")
    else:
        print("  WARNING - Below SOX compliance threshold")
    
    # Check for missing critical fields
    critical_fields = ['date', 'warehouse', 'operator_id', 'sku']
    print(f"\nCritical Fields Check:")
    for field in critical_fields:
        missing = df[field].isnull().sum()
        status = "" if missing == 0 else "❌"
        print(f"{status} {field}: {missing} missing values")
    
    return integrity_score


# ============================================================
# 2. ROOT CAUSE ANALYSIS
# ============================================================

def root_cause_analysis(df):
    """Identify primary causes of inventory defects"""
    print("\n ROOT CAUSE ANALYSIS")
    print("-" * 70)
    
    defects = df[df['has_defect'] == True]
    
    # By defect type
    cause_summary = defects.groupby('defect_type').agg({
        'transaction_id': 'count',
        'qty_variance': lambda x: abs(x).mean()
    }).rename(columns={
        'transaction_id': 'incident_count',
        'qty_variance': 'avg_variance'
    }).sort_values('incident_count', ascending=False)
    
    cause_summary['percentage'] = (cause_summary['incident_count'] / len(defects) * 100).round(2)
    
    print("\nTop Root Causes:")
    print(cause_summary.to_string())
    
    # Key finding
    top_cause = cause_summary.index[0]
    top_pct = cause_summary.iloc[0]['percentage']
    print(f"\n KEY INSIGHT: {top_cause} accounts for {top_pct}% of all defects")
    
    return cause_summary


# ============================================================
# 3. TREND ANALYSIS
# ============================================================

def analyze_trends(df):
    """Identify patterns and trends over time"""
    print("\n DEFECT TREND ANALYSIS")
    print("-" * 70)
    
    df['month'] = df['date'].dt.to_period('M')
    
    monthly_trends = df.groupby('month').agg({
        'transaction_id': 'count',
        'has_defect': ['sum', 'mean']
    })
    
    monthly_trends.columns = ['total_transactions', 'total_defects', 'defect_rate']
    monthly_trends['defect_rate'] = (monthly_trends['defect_rate'] * 100).round(2)
    
    print("\nMonthly Defect Trends:")
    print(monthly_trends.to_string())
    
    # Calculate improvement
    first_month = monthly_trends.iloc[0]['defect_rate']
    last_month = monthly_trends.iloc[-1]['defect_rate']
    improvement = ((first_month - last_month) / first_month * 100).round(2)
    
    if improvement > 0:
        print(f"\n TREND: {abs(improvement)}% improvement in defect rate over period")
    else:
        print(f"\n  TREND: {abs(improvement)}% increase in defect rate - investigation needed")
    
    return monthly_trends


# ============================================================
# 4. WAREHOUSE PERFORMANCE
# ============================================================

def warehouse_performance(df):
    """Compare warehouse accuracy and defect rates"""
    print("\n WAREHOUSE PERFORMANCE COMPARISON")
    print("-" * 70)
    
    wh_performance = df.groupby('warehouse').agg({
        'transaction_id': 'count',
        'has_defect': 'sum',
        'qty_variance': lambda x: abs(x).mean()
    }).rename(columns={
        'transaction_id': 'total_transactions',
        'has_defect': 'defect_count',
        'qty_variance': 'avg_variance'
    })
    
    wh_performance['defect_rate'] = (
        wh_performance['defect_count'] / wh_performance['total_transactions'] * 100
    ).round(2)
    wh_performance['accuracy_rate'] = (100 - wh_performance['defect_rate']).round(2)
    
    print(wh_performance.sort_values('defect_rate').to_string())
    
    # Best and worst performers
    best = wh_performance['defect_rate'].idxmin()
    worst = wh_performance['defect_rate'].idxmax()
    
    print(f"\n🏆 Best Performer: {best} ({wh_performance.loc[best, 'accuracy_rate']}% accuracy)")
    print(f"⚠️  Needs Improvement: {worst} ({wh_performance.loc[worst, 'defect_rate']}% defect rate)")
    
    return wh_performance


# ============================================================
# 5. ENTRY METHOD ANALYSIS
# ============================================================

def entry_method_analysis(df):
    """Compare defect rates by data entry method"""
    print("\n  ENTRY METHOD IMPACT ANALYSIS")
    print("-" * 70)
    
    method_analysis = df.groupby('entry_method').agg({
        'transaction_id': 'count',
        'has_defect': 'sum'
    }).rename(columns={
        'transaction_id': 'total_transactions',
        'has_defect': 'defect_count'
    })
    
    method_analysis['defect_rate'] = (
        method_analysis['defect_count'] / method_analysis['total_transactions'] * 100
    ).round(2)
    
    print(method_analysis.sort_values('defect_rate', ascending=False).to_string())
    
    # Recommendation
    worst_method = method_analysis['defect_rate'].idxmax()
    best_method = method_analysis['defect_rate'].idxmin()
    
    print(f"\n💡 RECOMMENDATION: Transition from {worst_method} to {best_method} entry")
    
    return method_analysis


# ============================================================
# 6. GENERATE VISUALIZATIONS
# ============================================================

def create_visualizations(df, cause_summary, monthly_trends, wh_performance):
    """Create comprehensive visualization dashboard"""
    print("\n GENERATING VISUALIZATIONS...")
    
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Defect Distribution by Root Cause
    ax1 = plt.subplot(2, 3, 1)
    cause_summary['incident_count'].plot(kind='bar', color='coral', ax=ax1)
    ax1.set_title('Defects by Root Cause', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Defect Type')
    ax1.set_ylabel('Incident Count')
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Warehouse Comparison
    ax2 = plt.subplot(2, 3, 2)
    wh_performance['defect_rate'].plot(kind='bar', color='skyblue', ax=ax2)
    ax2.set_title('Warehouse Defect Rates', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Warehouse')
    ax2.set_ylabel('Defect Rate (%)')
    ax2.axhline(y=2.5, color='r', linestyle='--', label='Target Threshold')
    ax2.legend()
    ax2.tick_params(axis='x', rotation=0)
    
    # 3. Monthly Trend
    ax3 = plt.subplot(2, 3, 3)
    monthly_trends['defect_rate'].plot(kind='line', marker='o', color='green', ax=ax3, linewidth=2)
    ax3.set_title('Defect Rate Trend Over Time', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Month')
    ax3.set_ylabel('Defect Rate (%)')
    ax3.grid(True, alpha=0.3)
    
    # 4. Entry Method Pie Chart
    ax4 = plt.subplot(2, 3, 4)
    entry_defects = df[df['has_defect']].groupby('entry_method').size()
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    ax4.pie(entry_defects, labels=entry_defects.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    ax4.set_title('Defects by Entry Method', fontsize=12, fontweight='bold')
    
    # 5. Severity Distribution
    ax5 = plt.subplot(2, 3, 5)
    defects = df[df['has_defect']]
    severity = pd.cut(abs(defects['qty_variance']), 
                      bins=[0, 10, 25, 50, 500], 
                      labels=['Low', 'Medium', 'High', 'Critical'])
    severity.value_counts().plot(kind='bar', color='orange', ax=ax5)
    ax5.set_title('Defect Severity Distribution', fontsize=12, fontweight='bold')
    ax5.set_xlabel('Severity Level')
    ax5.set_ylabel('Count')
    ax5.tick_params(axis='x', rotation=0)
    
    # 6. Summary Statistics Box
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    total_defects = df['has_defect'].sum()
    defect_rate = (total_defects / len(df) * 100)
    
    stats_text = f"""
    KEY METRICS
    {'='*30}
    
    Total Records: {len(df):,}
    Total Defects: {total_defects:,}
    Defect Rate: {defect_rate:.2f}%
    Accuracy Rate: {100-defect_rate:.2f}%
    
    Top Root Cause:
    {cause_summary.index[0]}
    ({cause_summary.iloc[0]['percentage']:.1f}% of defects)
    
    Best Warehouse:
    {wh_performance['defect_rate'].idxmin()}
    ({wh_performance['defect_rate'].min():.2f}% defect rate)
    """
    
    ax6.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
             verticalalignment='center', bbox=dict(boxstyle='round', 
             facecolor='lightblue', alpha=0.5))
    
    plt.suptitle('INVENTORY DEFECT ANALYSIS DASHBOARD', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    # Save visualization
    output_file = 'defect_analysis_dashboard.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    
    plt.show()


# ============================================================
# RUN ALL ANALYSES
# ============================================================

if __name__ == "__main__":
    # Execute all analyses
    integrity_score = validate_data_integrity(df)
    cause_summary = root_cause_analysis(df)
    monthly_trends = analyze_trends(df)
    wh_performance = warehouse_performance(df)
    method_analysis = entry_method_analysis(df)
    
    # Generate visualizations
    create_visualizations(df, cause_summary, monthly_trends, wh_performance)
    
    print("\n" + "="*70)
    print(" ANALYSIS COMPLETE!")
    print("="*70)
    print("\nFiles generated:")
    print("  1. defect_analysis_dashboard.png")
    print("\nNext steps:")
    print("  1. Upload raw_inventory_data.csv to MySQL/PostgreSQL")
    print("  2. Run the SQL queries")
    print("  3. Import query results into Tableau")
    print("  4. Create Excel dashboard with VBA macros")
    print("="*70)