import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def test_repair_device_field():
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
    print(f"  - product_description: {repair.get('product_description', 'MISSING')}")
    print(f"  - issue_description: {repair.get('issue_description', 'MISSING')}")
    
    # Get repair using get_repair_job method
    repair_job = db_manager.get_repair_job(repair_id)
    
    if not repair_job:
        print(f"Repair job #{repair_id} not found using get_repair_job().")
        return
    
    # Check if 'device' and 'issue' fields are present
    print("\nRepair data from get_repair_job():")
    print(f"  - device: {repair_job.get('device', 'MISSING')}")
    print(f"  - issue: {repair_job.get('issue', 'MISSING')}")
    print(f"  - product_description: {repair_job.get('product_description', 'MISSING')}")
    print(f"  - issue_description: {repair_job.get('issue_description', 'MISSING')}")
    
    # Verify that device = product_description and issue = issue_description
    device_match = repair['device'] == repair['product_description']
    issue_match = repair['issue'] == repair['issue_description']
    
    print("\nVerification:")
    print(f"  - device == product_description: {device_match}")
    print(f"  - issue == issue_description: {issue_match}")
    
    if device_match and issue_match:
        print("\nFix successful! The 'device' and 'issue' fields are correctly mapped.")
    else:
        print("\nFix failed! The fields are not correctly mapped.")

if __name__ == "__main__":
    test_repair_device_field()