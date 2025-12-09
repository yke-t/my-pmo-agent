"""
Spreadsheet Structure Setup Script
Automatically adds required columns to Issue and Schedule sheets
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build


class SheetStructureSetup:
    """Automate spreadsheet structure improvements"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, service_account_key_path, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        
        # Authenticate
        credentials = service_account.Credentials.from_service_account_file(
            service_account_key_path, scopes=self.SCOPES
        )
        self.service = build('sheets', 'v4', credentials=credentials)
    
    def setup_issue_sheet(self, sheet_name="Issues"):
        """Add required columns to Issue sheet"""
        print(f"\n[1/2] Setting up {sheet_name} sheet...")
        
        try:
            # Get current sheet structure
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!1:1"
            ).execute()
            
            current_headers = result.get('values', [[]])[0]
            print(f"  Current columns: {current_headers}")
            
            # Define required columns
            required_columns = ['ベンダー名', '優先度', '期限', '影響範囲', '更新日']
            
            # Check which columns are missing
            missing_columns = [col for col in required_columns if col not in current_headers]
            
            if not missing_columns:
                print("  [OK] All required columns already exist!")
                return True
            
            print(f"  Adding columns: {missing_columns}")
            
            # Append missing columns to header row
            new_headers = current_headers + missing_columns
            
            # Update header row
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!1:1",
                valueInputOption='RAW',
                body={'values': [new_headers]}
            ).execute()
            
            # Add data validation for dropdown columns
            self._add_dropdown_validation(
                sheet_name,
                column_name='優先度',
                values=['緊急', '高', '中', '低'],
                current_headers=new_headers
            )
            
            self._add_dropdown_validation(
                sheet_name,
                column_name='影響範囲',
                values=['全体', '特定ベンダー', '限定的'],
                current_headers=new_headers
            )
            
            print(f"  [OK] {sheet_name} sheet setup complete!")
            return True
        
        except Exception as e:
            print(f"  [ERROR] {e}")
            return False
    
    def setup_schedule_sheet(self, sheet_name="Schedule"):
        """Add required columns to Schedule sheet"""
        print(f"\n[2/2] Setting up {sheet_name} sheet...")
        
        try:
            # Get current sheet structure
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!1:1"
            ).execute()
            
            current_headers = result.get('values', [[]])[0]
            print(f"  Current columns: {current_headers}")
            
            # Define required columns
            required_new_columns = {
                'ベンダー名': None,
                '担当者': None,
                'ステータス': None
            }
            
            # Check if ID column exists at the beginning
            if current_headers and current_headers[0] != 'ID':
                print("  Adding 'ID' column at the beginning...")
                self._insert_column_at_position(sheet_name, 0, 'ID')
                current_headers.insert(0, 'ID')
            
            # Add other missing columns at the end
            missing_columns = [col for col in required_new_columns if col not in current_headers]
            
            if not missing_columns:
                print("  [OK] All required columns already exist!")
                return True
            
            print(f"  Adding columns: {missing_columns}")
            
            # Append missing columns
            new_headers = current_headers + missing_columns
            
            # Update header row
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!1:1",
                valueInputOption='RAW',
                body={'values': [new_headers]}
            ).execute()
            
            # Add data validation for status
            self._add_dropdown_validation(
                sheet_name,
                column_name='ステータス',
                values=['未着手', '進行中', '停滞', '完了', '保留'],
                current_headers=new_headers
            )
            
            print(f"  [OK] {sheet_name} sheet setup complete!")
            return True
        
        except Exception as e:
            print(f"  [ERROR] {e}")
            return False
    
    def _insert_column_at_position(self, sheet_name, position, column_name):
        """Insert a column at a specific position"""
        # Get sheet ID
        sheet_metadata = self.service.spreadsheets().get(
            spreadsheetId=self.spreadsheet_id
        ).execute()
        
        sheet_id = None
        for sheet in sheet_metadata['sheets']:
            if sheet['properties']['title'] == sheet_name:
                sheet_id = sheet['properties']['sheetId']
                break
        
        if sheet_id is None:
            raise ValueError(f"Sheet '{sheet_name}' not found")
        
        # Insert column
        requests = [{
            'insertDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': position,
                    'endIndex': position + 1
                }
            }
        }]
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        # Add column header
        col_letter = chr(65 + position)  # A=65
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet_name}!{col_letter}1",
            valueInputOption='RAW',
            body={'values': [[column_name]]}
        ).execute()
    
    def _add_dropdown_validation(self, sheet_name, column_name, values, current_headers):
        """Add dropdown validation to a column"""
        try:
            # Get sheet ID
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheet_id = None
            for sheet in sheet_metadata['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                return
            
            # Find column index
            if column_name not in current_headers:
                return
            
            column_index = current_headers.index(column_name)
            
            # Create validation rule
            requests = [{
                'setDataValidation': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 1,
                        'endRowIndex': 1000,
                        'startColumnIndex': column_index,
                        'endColumnIndex': column_index + 1
                    },
                    'rule': {
                        'condition': {
                            'type': 'ONE_OF_LIST',
                            'values': [{'userEnteredValue': v} for v in values]
                        },
                        'showCustomUi': True,
                        'strict': False
                    }
                }
            }]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            print(f"    [OK] Added dropdown for '{column_name}'")
        
        except Exception as e:
            print(f"    [WARNING] Could not add dropdown for '{column_name}': {e}")


def main():
    """Main setup script"""
    load_dotenv()
    
    print("=" * 60)
    print("myPMO Agent - Spreadsheet Structure Setup")
    print("=" * 60)
    
    service_account_key = os.getenv('SERVICE_ACCOUNT_KEY_PATH')
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    issue_sheet_name = os.getenv('ISSUE_SHEET_NAME', 'Issues')
    schedule_sheet_name = os.getenv('SCHEDULE_SHEET_NAME', 'Schedule')
    
    if not service_account_key or not spreadsheet_id:
        print("\n[ERROR] Missing environment variables")
        print("  Please configure .env file with:")
        print("  - SERVICE_ACCOUNT_KEY_PATH")
        print("  - SPREADSHEET_ID")
        return False
    
    print(f"\nUsing service account: {service_account_key}")
    print(f"Target spreadsheet: {spreadsheet_id}")
    print(f"Issue sheet: {issue_sheet_name}")
    print(f"Schedule sheet: {schedule_sheet_name}")
    print("\n[IMPORTANT] Ensure the service account has EDITOR access!")
    print("   Email: pmo-agent-sa@my-pmo-agent-v1.iam.gserviceaccount.com")
    
    input("\nPress ENTER to continue...")
    
    try:
        setup = SheetStructureSetup(service_account_key, spreadsheet_id)
        
        # Setup Issue sheet
        issue_success = setup.setup_issue_sheet(issue_sheet_name)
        
        # Setup Schedule sheet
        schedule_success = setup.setup_schedule_sheet(schedule_sheet_name)
        
        print("\n" + "=" * 60)
        if issue_success and schedule_success:
            print("[SUCCESS] Spreadsheet structure setup complete!")
            print("\nNext steps:")
            print("1. Verify changes in your spreadsheet")
            print("2. Run tests: python tests/test_sheets_client.py")
            return True
        else:
            print("[WARNING] Setup completed with some errors")
            print("   Please check the output above")
            return False
    
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
