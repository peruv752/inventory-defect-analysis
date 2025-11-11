 inventory-defect-analysis
Data analysis project using SQL, Python, and Excel VBA to analyze 50K+ inventory records

# Inventory Quality & Defect Analysis

**A data analysis project demonstrating SQL, Python, and statistical analysis skills**

## Project Overview

Analyzed 50,000+ inventory transactions to identify defect trends, perform root cause analysis, and improve data quality processes. This project simulates real-world inventory control quality assurance (ICQA) workflows.

## Technologies Used

- **Python**: Data generation, analysis, visualization (Pandas, NumPy, Matplotlib, Seaborn)
- **SQL**: Data extraction, aggregation, and transformation
- **SQLite**: Database management
- **Data Analysis**: Root cause analysis, trend analysis, statistical validation

##  Key Findings

-  **99.2% data integrity** achieved (meets SOX compliance standards)
-  **2.4% overall defect rate** across 50,000 transactions
-  **5 primary root causes** identified with 38% attributed to manual entry errors
-  **Warehouse performance variance** of 1.4% between best and worst performers
-  **Scanner-based entry** showed 60% fewer defects vs manual entry

##  Business Impact

- Identified training gaps for operators with >5% error rates
- Recommended scanner equipment investment based on data
- Provided warehouse-specific improvement targets
- Automated defect tracking reducing reporting time

##  Project Structure
├── data_generator.py      # Creates 50K simulated records
├── defect_analysis.py     # Python analysis & visualizations
├── sql_queries.sql        # Root cause SQL queries
├── results                # Analysis results & charts
└── README.md
##  Analysis Methodology

1. **Data Generation**: Created realistic inventory dataset with intentional defects
2. **Data Validation**: Ensured 99%+ data integrity for compliance
3. **Root Cause Analysis**: Identified top defect categories and contributing factors
4. **Trend Analysis**: Tracked defect rates over 6-month period
5. **Performance Benchmarking**: Compared warehouse and operator performance


##  Key Skills Demonstrated

- SQL data extraction and manipulation
- Python data analysis and visualization
- Root cause analysis methodologies
- Data integrity validation
- Statistical trend analysis
- Business insights and recommendations

##  How to Run

1. Clone this repository
2. Install requirements: `pip install pandas numpy matplotlib seaborn`
3. Generate data: `python data_generator.py`
4. Run analysis: `python defect_analysis.py`
5. Load data to SQL: `python load_to_sql.py`
6. Run SQL queries from `sql_queries.sql`

## 📧 Contact

Purnima | https://www.linkedin.com/in/purnimavr/ | purn0005@algonquinlive.com


--
