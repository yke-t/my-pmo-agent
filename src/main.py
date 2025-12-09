"""
myPMO Agent - Main Entry Point for Cloud Functions
Handles Google Chat webhook requests
"""

import os
import json
import functions_framework
from flask import Request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from brain.gemini_client import GeminiClient
from tools.sheets_client import SheetsClient


# Initialize clients
# In Cloud Functions, service account credentials are automatically available
# We only pass the service account key path if it exists (for local testing)
service_account_key = os.getenv('SERVICE_ACCOUNT_KEY_PATH')

sheets_client = SheetsClient(
    service_account_key_path=service_account_key if service_account_key and os.path.exists(service_account_key) else None,
    spreadsheet_id=os.getenv('SPREADSHEET_ID'),
    issue_sheet_name=os.getenv('ISSUE_SHEET_NAME', 'Issues'),
    schedule_sheet_name=os.getenv('SCHEDULE_SHEET_NAME', 'Schedule')
)

gemini_client = GeminiClient(
    project_id=os.getenv('GCP_PROJECT_ID'),
    service_account_key_path=service_account_key if service_account_key and os.path.exists(service_account_key) else None,
    location=os.getenv('GEMINI_LOCATION', 'us-central1'),
    model_name=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
)


@functions_framework.http
def handle_chat_message(request: Request):
    """
    Cloud Functions HTTP entry point for Google Chat
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response for Google Chat
    """
    # Parse request
    request_json = request.get_json(silent=True)
    
    if not request_json:
        return {"text": "Invalid request"}
    
    # Extract message
    message_text = request_json.get("message", {}).get("text", "")
    
    if not message_text:
        return {"text": "No message received"}
    
    # Route commands
    if message_text.startswith("/ask"):
        return handle_ask_command(message_text)
    
    elif message_text.startswith("/update-issue"):
        return handle_update_issue_command(message_text)
    
    elif message_text.startswith("/risk-alert"):
        return handle_risk_alert_command()
    
    else:
        return {
            "text": "使用可能なコマンド:\n"
                   "• `/ask [質問]` - Sheetsデータを参照して回答\n"
                   "• `/update-issue [内容]` - Issue Logに追記\n"
                   "• `/risk-alert` - リスク検出"
        }


def handle_ask_command(message_text: str):
    """Handle /ask command"""
    query = message_text.replace("/ask", "").strip()
    
    if not query:
        return {"text": "質問を入力してください。例: `/ask 期限が近いタスクは？`"}
    
    try:
        # Get data from sheets
        issues = sheets_client.get_all_issues()
        tasks = sheets_client.get_all_schedule_tasks()
        
        # Query Gemini AI
        result = gemini_client.analyze_with_context(
            user_query=query,
            issues_data=issues,
            schedule_data=tasks
        )
        
        # Check for errors
        if "error" in result:
            return {"text": f"❌ エラー: {result['error']}"}
        
        # Format response
        response_text = f"""**📊 分析結果**

{result.get('analysis', 'N/A')}

**💡 推奨事項**

{result.get('recommendation', 'N/A')}

**⚡ Next Action**

{result.get('next_action', 'N/A')}

---
_残りリクエスト: {result.get('remaining_requests', '?')}/250 (本日)_
"""
        
        return {"text": response_text}
    
    except Exception as e:
        return {"text": f"❌ システムエラー: {str(e)}"}


def handle_update_issue_command(message_text: str):
    """Handle /update-issue command"""
    # Parse command: /update-issue カテゴリ|内容|ベンダー名|担当者|優先度|期限
    parts = message_text.replace("/update-issue", "").strip().split("|")
    
    if len(parts) < 6:
        return {
            "text": "形式エラー。使用例:\n"
                   "`/update-issue 技術課題|API連携エラー|ベンダーA|鈴木|高|2025-12-15`"
        }
    
    category, content, vendor, assignee, priority, deadline = parts[:6]
    impact = parts[6] if len(parts) > 6 else ""
    
    try:
        success = sheets_client.add_issue(
            category=category.strip(),
            content=content.strip(),
            vendor=vendor.strip(),
            assignee=assignee.strip(),
            priority=priority.strip(),
            deadline=deadline.strip(),
            impact=impact.strip()
        )
        
        if success:
            return {"text": f"✅ Issue Logに追加しました:\n{content}"}
        else:
            return {"text": "❌ Issue追加に失敗しました"}
    
    except Exception as e:
        return {"text": f"❌ エラー: {str(e)}"}


def handle_risk_alert_command():
    """Handle /risk-alert command"""
    try:
        # Get overdue issues
        overdue = sheets_client.get_overdue_issues()
        
        # Get stalled tasks
        stalled = sheets_client.get_stalled_tasks()
        
        # Build alert message
        alerts = []
        
        if overdue:
            alerts.append(f"**🚨 期限超過課題: {len(overdue)}件**")
            for issue in overdue[:5]:
                alerts.append(
                    f"• [{issue.get('優先度')}] {issue.get('内容')} "
                    f"(期限: {issue.get('期限')}, 担当: {issue.get('担当者')})"
                )
        
        if stalled:
            alerts.append(f"\n**⚠️ 停滞タスク: {len(stalled)}件**")
            for task in stalled[:5]:
                alerts.append(
                    f"• {task.get('タスク')} (担当: {task.get('担当者')})"
                )
        
        if not alerts:
            return {"text": "✅ リスクは検出されませんでした"}
        
        return {"text": "\n".join(alerts)}
    
    except Exception as e:
        return {"text": f"❌ エラー: {str(e)}"}


if __name__ == "__main__":
    # Local testing
    print("myPMO Agent - Local Test Mode")
    print("=" * 50)
    
    # Test /ask command
    print("\n[TEST] /ask command")
    test_request = type('Request', (), {
        'get_json': lambda self, silent=True: {
            "message": {"text": "/ask 現在の課題数は？"}
        }
    })()
    
    response = handle_chat_message(test_request)
    print(json.dumps(response, ensure_ascii=False, indent=2))
