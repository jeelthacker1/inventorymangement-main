import sqlite3
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the DatabaseManager
from database.db_manager import DatabaseManager

def test_repair_parts():
    # Create a database manager instance
    db_manager = DatabaseManager()
    
    # Get all repairs to find a valid repair_id
    repairs = db_manager.get_all_repairs()
    
    if not repairs:
        print("No repairs found in the database. Please create a repair job first.")
        return
    
    # Use the first repair job's ID
    repair_id = repairs[0]['id']
    print(f"Testing with repair job ID: {repair_id}")
    
    # Get repair parts for this repair job
    repair_parts = db_manager.get_repair_parts(repair_id)
    
    if not repair_parts:
        print(f"No parts found for repair job {repair_id}")
        return
    
    # Check if each part has the required fields
    required_fields = ['name', 'quantity', 'cost', 'product_name']
    
    print(f"Found {len(repair_parts)} parts for repair job {repair_id}")
    
    for i, part in enumerate(repair_parts):
        print(f"\nPart {i+1}:")
        for field in required_fields:
            if field in part:
                print(f"  {field}: {part[field]}")
            else:
                print(f"  {field}: MISSING")
        
        # Print all available fields for reference
        print("\n  All available fields:")
        for key, value in part.items():
            print(f"  - {key}: {value}")

if __name__ == "__main__":
    test_repair_parts()