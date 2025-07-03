import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def test_complete_repair_functionality():
    db_manager = DatabaseManager()
    
    # Get all repairs
    repairs = db_manager.get_all_repairs()
    
    if not repairs:
        print("No repair jobs found in the database.")
        return
    
    # Test the first repair job
    repair_id = repairs[0]['id']
    print(f"Testing repair job #{repair_id}")
    
    # Get repair using get_repair method
    repair = db_manager.get_repair(repair_id)
    
    if not repair:
        print(f"Repair job #{repair_id} not found.")
        return
    
    # Check if 'device' and 'issue' fields are present
    print("\nRepair data from get_repair():")
    print(f"  - device: {repair.get('device', 'MISSING')}")
    print(f"  - issue: {repair.get('issue', 'MISSING')}")
    
    # Get repair parts
    repair_parts = db_manager.get_repair_parts(repair_id)
    
    if not repair_parts:
        print("No repair parts found for this repair job.")
    else:
        print(f"\nFound {len(repair_parts)} repair parts:")
        for i, part in enumerate(repair_parts, 1):
            print(f"  Part #{i}:")
            print(f"    - name: {part.get('name', 'MISSING')}")
            print(f"    - product_name: {part.get('product_name', 'MISSING')}")
            print(f"    - quantity: {part.get('quantity', 'MISSING')}")
            print(f"    - cost: {part.get('cost', 'MISSING')}")
            print(f"    - unit_price: {part.get('unit_price', 'MISSING')}")
    
    # Simulate completing a repair
    print("\nSimulating repair completion...")
    
    # Calculate total parts cost
    total_parts_cost = sum(part['total_price'] for part in repair_parts) if repair_parts else 0
    
    # Set service charge
    service_charge = 500  # Example service charge
    
    # Calculate final cost
    final_cost = total_parts_cost + service_charge
    
    # Update repair status
    status = 'completed'
    
    success = db_manager.update_repair_status(repair_id, status, service_charge)
    
    if success:
        print("Repair job successfully marked as completed.")
        print(f"  - Service charge: ₹{service_charge:.2f}")
        print(f"  - Total parts cost: ₹{total_parts_cost:.2f}")
        print(f"  - Final cost: ₹{final_cost:.2f}")
    else:
        print("Failed to complete repair job.")
    
    # Get updated repair
    updated_repair = db_manager.get_repair(repair_id)
    print(f"\nUpdated repair status: {updated_repair.get('status', 'MISSING')}")

if __name__ == "__main__":
    test_complete_repair_functionality()