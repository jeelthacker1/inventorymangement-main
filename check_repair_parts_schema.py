import sqlite3
import os

# Connect to the database
db_path = 'database/inventory.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get the schema of the repair_parts table
cursor.execute("PRAGMA table_info(repair_parts)")
columns = cursor.fetchall()

print("Repair Parts Table Schema:")
for column in columns:
    print(f"Column: {column[1]}, Type: {column[2]}")

# Get a sample repair part to see the actual field names
cursor.execute("SELECT * FROM repair_parts LIMIT 1")
repair_part = cursor.fetchone()

if repair_part:
    print("\nSample Repair Part Fields:")
    for key in repair_part.keys():
        print(f"Field: {key}, Value: {repair_part[key]}")
else:
    print("\nNo repair parts found in the database.")

# Close the connection
conn.close()