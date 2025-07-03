import sqlite3
import os

# Connect to the database
db_path = 'database/inventory.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get the schema of the products table
cursor.execute("PRAGMA table_info(products)")
columns = cursor.fetchall()

print("Products Table Schema:")
for column in columns:
    print(f"Column: {column[1]}, Type: {column[2]}")

# Get a sample product to see the actual field names
cursor.execute("SELECT * FROM products LIMIT 1")
product = cursor.fetchone()

if product:
    print("\nSample Product Fields:")
    for key in product.keys():
        print(f"Field: {key}, Value: {product[key]}")
else:
    print("\nNo products found in the database.")

# Close the connection
conn.close()