import sqlite3
import os

# Connect to the database
db_path = 'database/inventory.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add serial_number column to repair_jobs table
    cursor.execute("ALTER TABLE repair_jobs ADD COLUMN serial_number TEXT")
    conn.commit()
    print("Successfully added serial_number column to repair_jobs table")
    
    # Add received_date and estimated_completion_date columns if they don't exist
    cursor.execute("PRAGMA table_info(repair_jobs)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'received_date' not in column_names:
        cursor.execute("ALTER TABLE repair_jobs ADD COLUMN received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        conn.commit()
        print("Successfully added received_date column to repair_jobs table")
    
    if 'estimated_completion_date' not in column_names:
        cursor.execute("ALTER TABLE repair_jobs ADD COLUMN estimated_completion_date TIMESTAMP")
        conn.commit()
        print("Successfully added estimated_completion_date column to repair_jobs table")
    
    if 'notes' not in column_names:
        cursor.execute("ALTER TABLE repair_jobs ADD COLUMN notes TEXT")
        conn.commit()
        print("Successfully added notes column to repair_jobs table")
    
    # Verify the changes
    cursor.execute("PRAGMA table_info(repair_jobs)")
    columns = cursor.fetchall()
    
    print("\nUpdated Repair Jobs Table Schema:")
    for column in columns:
        print(f"Column: {column[1]}, Type: {column[2]}")

except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

# Close the connection
conn.close()