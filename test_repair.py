import sqlite3
import os

# Connect to the database
db_path = 'database/inventory.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # This enables column access by name
cursor = conn.cursor()

# Test data for a new repair job
repair_data = {
    'customer_id': 1,  # Using an existing customer ID
    'product_description': 'Test Device',
    'issue_description': 'Test Issue',
    'serial_number': 'TEST123456',
    'status': 'pending',
    'estimated_cost': 100.0,
    'assigned_to': None,
    'received_date': '2023-06-01',
    'estimated_completion_date': '2023-06-10',
    'notes': 'Test notes'
}

try:
    # Insert a test repair job
    cursor.execute('''
    INSERT INTO repair_jobs (
        customer_id, product_description, issue_description, 
        status, estimated_cost, assigned_to, serial_number,
        received_date, estimated_completion_date, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        repair_data['customer_id'],
        repair_data['product_description'],
        repair_data['issue_description'],
        repair_data['status'],
        repair_data['estimated_cost'],
        repair_data['assigned_to'],
        repair_data['serial_number'],
        repair_data['received_date'],
        repair_data['estimated_completion_date'],
        repair_data['notes']
    ))
    
    repair_id = cursor.lastrowid
    conn.commit()
    print(f"Successfully added test repair job with ID: {repair_id}")
    
    # Retrieve the repair job to verify
    cursor.execute('''
    SELECT * FROM repair_jobs WHERE id = ?
    ''', (repair_id,))
    
    repair = cursor.fetchone()
    
    if repair:
        print("\nRetrieved repair job:")
        for key in repair.keys():
            print(f"{key}: {repair[key]}")
        
        # Verify serial_number was saved correctly
        if repair['serial_number'] == repair_data['serial_number']:
            print("\nSUCCESS: Serial number was saved and retrieved correctly!")
        else:
            print(f"\nERROR: Serial number mismatch. Expected: {repair_data['serial_number']}, Got: {repair['serial_number']}")
    else:
        print("\nERROR: Could not retrieve the repair job")
    
    # Clean up - delete the test repair job
    cursor.execute("DELETE FROM repair_jobs WHERE id = ?", (repair_id,))
    conn.commit()
    print("\nTest repair job deleted")
    
except Exception as e:
    print(f"\nERROR: {e}")
    conn.rollback()

# Close the connection
conn.close()