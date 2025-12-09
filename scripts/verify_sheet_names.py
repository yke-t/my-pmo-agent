"""
Verify actual sheet names in the spreadsheet
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build


def list_sheet_names():
    """List all sheet names in the spreadsheet"""
    load_dotenv()
    
    service_account_key = os.getenv('SERVICE_ACCOUNT_KEY_PATH')
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    credentials = service_account.Credentials.from_service_account_file(
        service_account_key, scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=credentials)
    
    print("=" * 60)
    print("Spreadsheet Sheet Names")
    print("=" * 60)
    
    try:
        # Get spreadsheet metadata
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        sheets = spreadsheet.get('sheets', [])
        
        print(f"\nFound {len(sheets)} sheet(s):\n")
        
        for i, sheet in enumerate(sheets, 1):
            properties = sheet.get('properties', {})
            sheet_name = properties.get('title', 'Unknown')
            sheet_id = properties.get('sheetId', 'N/A')
            
            print(f"{i}. '{sheet_name}' (ID: {sheet_id})")
            
            # Try to read first row to see headers
            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=f"'{sheet_name}'!1:1"
                ).execute()
                
                headers = result.get('values', [[]])[0]
                if headers:
                    print(f"   Headers: {headers}")
                else:
                    print(f"   (Empty sheet)")
            except Exception as e:
                print(f"   (Could not read headers: {e})")
            
            print()
        
        print("=" * 60)
        print("\n✓ Sheet names listed successfully")
        print("\nRecommendation:")
        print("- Update .env file with correct sheet names:")
        print("  ISSUE_SHEET_NAME=<actual_name>")
        print("  SCHEDULE_SHEET_NAME=<actual_name>")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    list_sheet_names()
