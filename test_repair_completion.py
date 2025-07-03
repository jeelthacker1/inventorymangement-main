import os
import sys
import sqlite3
from PyQt5.QtWidgets import QApplication
from database.db_manager import DatabaseManager

# Initialize the application
app = QApplication(sys.argv)

# Create a database manager instance
db_manager = DatabaseManager()

# Test repair completion and invoice generation
def test_repair_completion():
    print("Testing repair completion and invoice generation...")
    
    # Get all customers
    customers = db_manager.get_all_customers()
    if not customers:
        print("No customers found in the database.")
        return False
    
    # Get a customer for the test
    test_customer = customers[0]
    print(f"Using customer: {test_customer['name']} (ID: {test_customer['id']})")
    
    # Create a test repair
    repair_data = {
        'customer_id': test_customer['id'],
        'product_description': 'Test Device',
        'issue_description': 'Test Issue',
        'serial_number': 'TEST123456',
        'status': 'pending',
        'received_date': '2023-06-01',
        'estimated_completion_date': '2023-06-05',
        'assigned_to': 'Test Technician',
        'notes': 'Test repair notes',
        'estimated_cost': 100,
        'parts': []
    }
    
    # Add the repair
    success = db_manager.add_repair(repair_data)
    if not success:
        print("Failed to create test repair.")
        return False
    
    print("Test repair created successfully.")
    
    # Get all repairs to find our test repair
    repairs = db_manager.get_all_repairs()
    test_repair = None
    for repair in repairs:
        if (repair['customer_id'] == test_customer['id'] and 
            repair['product_description'] == 'Test Device' and
            repair['serial_number'] == 'TEST123456'):
            test_repair = repair
            break
    
    if not test_repair:
        print("Could not find the test repair in the database.")
        return False
    
    print(f"Found test repair: ID {test_repair['id']}")
    
    # Add a test part to the repair
    # First, get a product to use as a part
    products = db_manager.get_all_products()
    if not products:
        print("No products found in the database.")
        return False
    
    test_product = products[0]
    print(f"Using product: {test_product['name']} (ID: {test_product['id']})")
    
    # Add the part to the repair
    db_manager.connect()
    db_manager.cursor.execute("""
    INSERT INTO repair_parts (repair_job_id, product_id, quantity, unit_price, total_price)
    VALUES (?, ?, ?, ?, ?)
    """, (
        test_repair['id'],
        test_product['id'],
        1,  # quantity
        test_product['selling_price'],  # unit_price
        test_product['selling_price']  # total_price
    ))
    db_manager.commit()
    db_manager.close()
    
    print(f"Added part {test_product['name']} to repair")
    
    # Complete the repair
    completion_data = {
        'status': 'completed',
        'service_charge': 500,  # Default service charge
        'completion_notes': 'Test completion notes'
    }
    
    success = db_manager.complete_repair(test_repair['id'], completion_data)
    if not success:
        print("Failed to complete test repair.")
        return False
    
    print("Test repair completed successfully.")
    
    # Verify the repair was completed correctly
    completed_repair = db_manager.get_repair(test_repair['id'])
    if not completed_repair:
        print("Could not find the completed repair in the database.")
        return False
    
    print(f"Completed repair status: {completed_repair['status']}")
    print(f"Service charge: ₹{completed_repair['service_charge']}")
    print(f"Total parts cost: ₹{completed_repair['total_parts_cost']}")
    print(f"Final cost: ₹{completed_repair['final_cost']}")
    
    # Verify the repair parts are correctly associated
    repair_parts = db_manager.get_repair_parts(test_repair['id'])
    if not repair_parts:
        print("No parts found for the completed repair.")
    else:
        print(f"Found {len(repair_parts)} parts for the repair:")
        for part in repair_parts:
            print(f"  - {part['product_name']}: {part['quantity']} x ₹{part['unit_price']} = ₹{part['total_price']}")
    
    # Clean up - delete the test repair and its parts
    db_manager.connect()
    db_manager.cursor.execute("DELETE FROM repair_parts WHERE repair_job_id = ?", (test_repair['id'],))
    db_manager.cursor.execute("DELETE FROM repair_jobs WHERE id = ?", (test_repair['id'],))
    db_manager.commit()
    db_manager.close()
    print("Test repair and parts deleted.")
    
    return True

# Test invoice generation
def test_invoice_generation(repair_id):
    print("\nTesting invoice generation...")
    
    # We can't directly test the UI components in this script,
    # but we can verify that the necessary data is available for invoice generation
    
    # Get the repair data
    repair_data = db_manager.get_repair(repair_id)
    if not repair_data:
        print("Could not find the repair data for invoice generation.")
        return False
    
    # Get the customer data
    customer_data = db_manager.get_customer(repair_data['customer_id'])
    if not customer_data:
        print("Could not find the customer data for invoice generation.")
        return False
    
    # Get the repair parts
    repair_parts = db_manager.get_repair_parts(repair_id)
    
    # Verify the data needed for invoice generation
    print(f"Repair data available: {bool(repair_data)}")
    print(f"Customer data available: {bool(customer_data)}")
    print(f"Repair parts available: {bool(repair_parts)}")
    print(f"Number of parts: {len(repair_parts)}")
    
    # Check if all required data is available
    if repair_data and customer_data:
        print("All required data for invoice generation is available.")
        return True
    else:
        print("Missing required data for invoice generation.")
        return False

# Run the test
if __name__ == "__main__":
    print("=== Testing Repair Completion and Invoice Generation ===\n")
    
    completion_result = test_repair_completion()
    
    # If repair completion was successful, test invoice generation
    invoice_result = False
    if completion_result:
        # Get all repairs to find our test repair
        repairs = db_manager.get_all_repairs()
        test_repair = None
        for repair in repairs:
            if (repair['status'] == 'completed' and
                repair['product_description'] == 'Test Device' and
                repair['serial_number'] == 'TEST123456'):
                test_repair = repair
                break
        
        if test_repair:
            invoice_result = test_invoice_generation(test_repair['id'])
    
    print("\n=== Test Results ===")
    print(f"Repair Completion: {'PASSED' if completion_result else 'FAILED'}")
    print(f"Invoice Generation: {'PASSED' if invoice_result else 'NOT TESTED' if not completion_result else 'FAILED'}")
    
    if completion_result and invoice_result:
        print("\nAll tests PASSED! The repair completion and invoice generation functionality is working correctly.")
    elif completion_result:
        print("\nRepair completion PASSED but invoice generation FAILED. The invoice generation functionality may have issues.")
    else:
        print("\nSome tests FAILED. The repair completion and invoice generation functionality may have issues.")