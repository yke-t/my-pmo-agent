"""
Test Google Sheets API Connection
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from dotenv import load_dotenv
from tools.sheets_client import SheetsClient


def test_sheets_connection():
    """Test Sheets API connection and data retrieval"""
    load_dotenv()
    
    print("Testing Google Sheets API Connection...")
    print("=" * 60)
    
    try:
        client = SheetsClient(
            service_account_key_path=os.getenv('SERVICE_ACCOUNT_KEY_PATH'),
            spreadsheet_id=os.getenv('SPREADSHEET_ID'),
            issue_sheet_name=os.getenv('ISSUE_SHEET_NAME'),
            schedule_sheet_name=os.getenv('SCHEDULE_SHEET_NAME')
        )
        
        print("[OK] Sheets API client initialized\n")
        
        # Test Issue Log
        print("[1/3] Testing Issue Log retrieval...")
        issues = client.get_all_issues()
        print(f"[OK] Retrieved {len(issues)} issues")
        
        if issues:
            print(f"  First issue columns: {list(issues[0].keys())}")
        
        # Test Schedule
        print("\n[2/3] Testing Schedule retrieval...")
        tasks = client.get_all_schedule_tasks()
        print(f"[OK] Retrieved {len(tasks)} tasks")
        
        if tasks:
            print(f"  First task columns: {list(tasks[0].keys())}")
        
        # Test filtering
        print("\n[3/3] Testing overdue issues detection...")
        overdue = client.get_overdue_issues()
        print(f"[OK] Found {len(overdue)} overdue issues")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        return True
    
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_sheets_connection()
    sys.exit(0 if success else 1)
