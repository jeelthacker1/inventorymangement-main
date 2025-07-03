import os
import sys
import sqlite3
from PyQt5.QtWidgets import QApplication
from database.db_manager import DatabaseManager

# Initialize the application
app = QApplication(sys.argv)

# Create a database manager instance
db_manager = DatabaseManager()

# Test customer selection functionality
def test_customer_selection():
    print("Testing customer selection functionality...")
    
    # Get all customers
    customers = db_manager.get_all_customers()
    if not customers:
        print("No customers found in the database.")
        return False
    
    print(f"Found {len(customers)} customers in the database.")
    for i, customer in enumerate(customers[:5]):  # Print first 5 customers
        print(f"Customer {i+1}: {customer['name']} - {customer['phone']}")
    
    # Test search_customers method
    first_customer = customers[0]
    search_term = first_customer['name'][:3]  # Use first 3 characters of the first customer's name
    print(f"\nSearching for customers with term: '{search_term}'")
    
    search_results = db_manager.search_customers(search_term)
    if not search_results:
        print(f"No customers found with search term '{search_term}'")
        return False
    
    print(f"Found {len(search_results)} customers matching '{search_term}'")
    for i, customer in enumerate(search_results[:5]):  # Print first 5 search results
        print(f"Result {i+1}: {customer['name']} - {customer['phone']}")
    
    return True

# Test repair creation with customer
def test_repair_creation():
    print("\nTesting repair creation with customer...")
    
    # Get a customer for the test
    customers = db_manager.get_all_customers()
    if not customers:
        print("No customers found in the database.")
        return False
    
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
        'estimated_cost': 100
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
    print(f"Customer name in repair: {test_repair['customer_name']}")
    
    # Clean up - delete the test repair
    db_manager.connect()
    db_manager.cursor.execute("DELETE FROM repair_jobs WHERE id = ?", (test_repair['id'],))
    db_manager.commit()
    db_manager.close()
    print("Test repair deleted.")
    
    return True

# Run the tests
if __name__ == "__main__":
    print("=== Testing Repair Customer Selection ===\n")
    
    customer_selection_result = test_customer_selection()
    repair_creation_result = test_repair_creation()
    
    print("\n=== Test Results ===")
    print(f"Customer Selection: {'PASSED' if customer_selection_result else 'FAILED'}")
    print(f"Repair Creation: {'PASSED' if repair_creation_result else 'FAILED'}")
    
    if customer_selection_result and repair_creation_result:
        print("\nAll tests PASSED! The customer selection functionality is working correctly.")
    else:
        print("\nSome tests FAILED. The customer selection functionality may have issues.")