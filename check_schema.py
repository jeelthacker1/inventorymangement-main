import sqlite3
import os

# Connect to the database
db_path = 'database/inventory.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the schema of the repair_jobs table
cursor.execute("PRAGMA table_info(repair_jobs)")
columns = cursor.fetchall()

print("Repair Jobs Table Schema:")
for column in columns:
    print(f"Column: {column[1]}, Type: {column[2]}")

# Check if serial_number column exists
serial_number_exists = any(column[1] == 'serial_number' for column in columns)
print(f"\nSerial Number column exists: {serial_number_exists}")

# Close the connection
conn.close()