"""
Google Sheets API Client for myPMO Agent
Handles reading/writing to Issue Log and Schedule sheets
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SheetsClient:
    """Google Sheets API wrapper for PMO data management"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, 
                 service_account_key_path: Optional[str] = None,
                 spreadsheet_id: str = None,
                 issue_sheet_name: str = "Issues",
                 schedule_sheet_name: str = "Schedule"):
        """
        Initialize Sheets API client
        
        Args:
            service_account_key_path: Path to service account JSON key (optional, uses default credentials if None)
            spreadsheet_id: Google Spreadsheet ID
            issue_sheet_name: Name of Issue Log sheet
            schedule_sheet_name: Name of Schedule sheet
        """
        self.spreadsheet_id = spreadsheet_id
        self.issue_sheet_name = issue_sheet_name
        self.schedule_sheet_name = schedule_sheet_name
        
        # Authenticate
        if service_account_key_path:
            # Use service account key file
            credentials = service_account.Credentials.from_service_account_file(
                service_account_key_path, scopes=self.SCOPES
            )
        else:
            # Use default credentials (for Cloud Functions)
            import google.auth
            credentials, project = google.auth.default(scopes=self.SCOPES)
        
        self.service = build('sheets', 'v4', credentials=credentials)
        
    def _read_range(self, range_name: str) -> List[List[Any]]:
        """
        Read data from a specific range
        
        Args:
            range_name: A1 notation range (e.g., "Issue!A1:Z1000")
            
        Returns:
            List of rows (each row is a list of cell values)
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            return result.get('values', [])
        
        except HttpError as error:
            print(f"Error reading range {range_name}: {error}")
            raise
    
    def _append_row(self, range_name: str, values: List[Any]) -> bool:
        """
        Append a new row to the sheet
        
        Args:
            range_name: Sheet name (e.g., "Issue")
            values: List of cell values for the new row
            
        Returns:
            True if successful, False otherwise
        """
        try:
            body = {'values': [values]}
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
        
        except HttpError as error:
            print(f"Error appending to {range_name}: {error}")
            return False
    
    def get_all_issues(self) -> List[Dict[str, Any]]:
        """
        Get all issues from Issue Log
        
        Returns:
            List of issue dictionaries with column headers as keys
        """
        range_name = f"{self.issue_sheet_name}!A:L"  # A-L covers all columns
        rows = self._read_range(range_name)
        
        if not rows:
            return []
        
        # First row is header
        headers = rows[0]
        issues = []
        
        for row in rows[1:]:  # Skip header
            # Pad row if it has fewer columns than headers
            row_padded = row + [''] * (len(headers) - len(row))
            issue = dict(zip(headers, row_padded))
            issues.append(issue)
        
        return issues
    
    def get_issues_by_filter(self, 
                            vendor: Optional[str] = None,
                            priority: Optional[str] = None,
                            status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filter issues by criteria
        
        Args:
            vendor: Filter by vendor name (ベンダー名)
            priority: Filter by priority (優先度)
            status: Filter by status (ステータス)
            
        Returns:
            Filtered list of issues
        """
        all_issues = self.get_all_issues()
        filtered = all_issues
        
        if vendor:
            filtered = [i for i in filtered if i.get('ベンダー名', '') == vendor]
        
        if priority:
            filtered = [i for i in filtered if i.get('優先度', '') == priority]
        
        if status:
            filtered = [i for i in filtered if i.get('ステータス', '') == status]
        
        return filtered
    
    def get_overdue_issues(self) -> List[Dict[str, Any]]:
        """
        Get issues past their deadline
        
        Returns:
            List of overdue issues
        """
        all_issues = self.get_all_issues()
        today = datetime.now().date()
        overdue = []
        
        for issue in all_issues:
            deadline_str = issue.get('期限', '')
            if not deadline_str:
                continue
            
            try:
                # Assume YYYY-MM-DD format
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
                if deadline < today and issue.get('ステータス') != '完了':
                    overdue.append(issue)
            except ValueError:
                continue
        
        return overdue
    
    def add_issue(self, 
                  category: str,
                  content: str,
                  vendor: str,
                  assignee: str,
                  priority: str,
                  deadline: str,
                  status: str = "新規",
                  impact: str = "") -> bool:
        """
        Add a new issue to Issue Log
        
        Args:
            category: カテゴリ
            content: 内容
            vendor: ベンダー名
            assignee: 担当者
            priority: 優先度 (緊急/高/中/低)
            deadline: 期限 (YYYY-MM-DD)
            status: ステータス (default: 新規)
            impact: 影響範囲
            
        Returns:
            True if successful
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Auto-generate ID by counting existing rows
        all_issues = self.get_all_issues()
        new_id = len(all_issues) + 1
        
        values = [
            new_id,          # ID
            today,           # 起票日
            category,        # カテゴリ
            content,         # 内容
            vendor,          # ベンダー名
            assignee,        # 担当者
            priority,        # 優先度
            deadline,        # 期限
            status,          # ステータス
            impact,          # 影響範囲
            today            # 更新日
        ]
        
        return self._append_row(self.issue_sheet_name, values)
    
    def get_all_schedule_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks from Schedule
        
        Returns:
            List of task dictionaries
        """
        range_name = f"{self.schedule_sheet_name}!A:J"
        rows = self._read_range(range_name)
        
        if not rows:
            return []
        
        headers = rows[0]
        tasks = []
        
        for row in rows[1:]:
            row_padded = row + [''] * (len(headers) - len(row))
            task = dict(zip(headers, row_padded))
            tasks.append(task)
        
        return tasks
    
    def get_stalled_tasks(self, days_threshold: int = 7) -> List[Dict[str, Any]]:
        """
        Get tasks marked as '停滞' for more than threshold days
        
        Args:
            days_threshold: Number of days to consider stalled
            
        Returns:
            List of stalled tasks
        """
        all_tasks = self.get_all_schedule_tasks()
        # Note: This is a simplified version
        # Full implementation would require tracking status change dates
        return [t for t in all_tasks if t.get('ステータス') == '停滞']
    
    def get_critical_path_tasks(self) -> List[Dict[str, Any]]:
        """
        Get tasks marked as critical path
        
        Returns:
            List of critical path tasks
        """
        all_tasks = self.get_all_schedule_tasks()
        return [t for t in all_tasks if t.get('クリティカルパス') == 'TRUE']


if __name__ == "__main__":
    # Test connection
    from dotenv import load_dotenv
    load_dotenv()
    
    client = SheetsClient(
        service_account_key_path=os.getenv('SERVICE_ACCOUNT_KEY_PATH'),
        spreadsheet_id=os.getenv('SPREADSHEET_ID'),
        issue_sheet_name=os.getenv('ISSUE_SHEET_NAME'),
        schedule_sheet_name=os.getenv('SCHEDULE_SHEET_NAME')
    )
    
    print("✓ Sheets API connection successful")
    print(f"Total issues: {len(client.get_all_issues())}")
    print(f"Total tasks: {len(client.get_all_schedule_tasks())}")
