"""
Test Gemini 3.0 Pro API Connection
"""

import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from dotenv import load_dotenv
from brain.gemini_client import GeminiClient


def test_gemini_connection():
    """Test Gemini API connection and basic query"""
    load_dotenv()
    
    print("Testing Gemini 3.0 Pro API Connection...")
    print("=" * 60)
    
    try:
        client = GeminiClient(
            project_id=os.getenv('GCP_PROJECT_ID'),
            service_account_key_path=os.getenv('SERVICE_ACCOUNT_KEY_PATH'),
            location=os.getenv('GEMINI_LOCATION'),
            model_name=os.getenv('GEMINI_MODEL')
        )
        
        print("[OK] Gemini AI client initialized")
        print(f"  Model: {client.model_name}")
        print(f"  Remaining requests: {client.get_remaining_requests()}/250\n")
        
        # Test simple query
        print("[1/2] Testing basic query...")
        result = client.analyze_with_context(
            user_query="テストメッセージです。このシステムの役割を簡潔に説明してください。",
            issues_data=None,
            schedule_data=None
        )
        
        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return False
        
        print("[OK] Response received")
        print(f"  Analysis: {result.get('analysis', 'N/A')[:100]}...")
        print(f"  Remaining: {result.get('remaining_requests')}/250")
        
        # Test with mock data
        print("\n[2/2] Testing with mock PMO data...")
        mock_issues = [
            {
                "ID": "1",
                "内容": "API連携エラー",
                "ベンダー名": "ベンダーA",
                "優先度": "緊急",
                "期限": "2025-12-10",
                "担当者": "鈴木"
            }
        ]
        
        result2 = client.analyze_with_context(
            user_query="緊急課題の状況を教えてください",
            issues_data=mock_issues,
            schedule_data=None
        )
        
        if "error" in result2:
            print(f"[ERROR] {result2['error']}")
            return False
        
        print("[OK] Response with context received")
        print(f"  Next Action: {result2.get('next_action', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print(f"Remaining requests: {client.get_remaining_requests()}/250")
        return True
    
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_gemini_connection()
    sys.exit(0 if success else 1)
