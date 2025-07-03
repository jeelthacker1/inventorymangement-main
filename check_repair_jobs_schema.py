import sqlite3
import os

# Connect to the database
db_path = 'database/inventory.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get the schema of the repair_jobs table
cursor.execute("PRAGMA table_info(repair_jobs)")
columns = cursor.fetchall()

print("Repair Jobs Table Schema:")
for column in columns:
    print(f"Column: {column[1]}, Type: {column[2]}")

# Close the connection
conn.close()