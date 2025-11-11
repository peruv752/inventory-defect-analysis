# Quick SQLite script - save as: load_to_sql.py
   import pandas as pd
   import sqlite3
   
   # Load CSV
   df = pd.read_csv('raw_inventory_data.csv')
   
   # Create SQLite database
   conn = sqlite3.connect('inventory.db')
   df.to_sql('inventory_transactions', conn, if_exists='replace', index=False)
   conn.close()
   
   print(" Data loaded to SQLite database: inventory.db")