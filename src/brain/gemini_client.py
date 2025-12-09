"""
Gemini 3.0 Pro AI Client for myPMO Agent
Handles AI-powered analysis and recommendations
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.oauth2 import service_account


class GeminiClient:
    """Gemini 3.0 Pro API wrapper for PMO analysis"""
    
    # Rate limit tracking (250 requests/day)
    DAILY_LIMIT = 250
    _request_count = 0
    _last_reset_date = None
    
    def __init__(self, 
                 project_id: str,
                 service_account_key_path: Optional[str] = None,
                 location: str = "us-central1",
                 model_name: str = "gemini-3.0-pro-preview-1118"):
        """
        Initialize Gemini AI client
        
        Args:
            project_id: GCP project ID
            service_account_key_path: Path to service account JSON key file
            location: Vertex AI location
            model_name: Gemini model name
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        
        # Initialize Vertex AI with service account credentials
        if service_account_key_path:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_key_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            vertexai.init(project=project_id, location=location, credentials=credentials)
        else:
            vertexai.init(project=project_id, location=location)
        
        self.model = GenerativeModel(model_name)
        
        # Reset counter if new day
        self._check_reset_counter()
    
    def _check_reset_counter(self):
        """Reset request counter if it's a new day (Pacific Time)"""
        today = datetime.now().date()
        
        if GeminiClient._last_reset_date != today:
            GeminiClient._request_count = 0
            GeminiClient._last_reset_date = today
    
    def _increment_request_count(self) -> bool:
        """
        Increment request counter and check if limit exceeded
        
        Returns:
            True if request allowed, False if limit exceeded
        """
        self._check_reset_counter()
        
        if GeminiClient._request_count >= GeminiClient.DAILY_LIMIT:
            return False
        
        GeminiClient._request_count += 1
        return True
    
    def get_remaining_requests(self) -> int:
        """Get remaining requests for today"""
        self._check_reset_counter()
        return GeminiClient.DAILY_LIMIT - GeminiClient._request_count
    
    def analyze_with_context(self,
                            user_query: str,
                            issues_data: Optional[list] = None,
                            schedule_data: Optional[list] = None) -> Dict[str, Any]:
        """
        Analyze user query with PMO context
        
        Args:
            user_query: User's question or request
            issues_data: Issue Log data (list of dicts)
            schedule_data: Schedule data (list of dicts)
            
        Returns:
            Dict with 'analysis', 'recommendation', 'next_action'
        """
        # Check rate limit
        if not self._increment_request_count():
            return {
                "error": f"Daily request limit ({self.DAILY_LIMIT}) exceeded. Resets at midnight Pacific Time.",
                "remaining_requests": 0
            }
        
        # Build context from data
        context = self._build_context(issues_data, schedule_data)
        
        # Load PMO persona
        persona = self._load_pmo_persona()
        
        # Construct prompt
        prompt = f"""{persona}

# Data Context

{context}

# User Query

{user_query}

# Response Format (JSON)

Respond ONLY with valid JSON in this exact format:
{{
  "analysis": "事実/推測/リスクの整理",
  "recommendation": "具体的指示（To-Do形式）",
  "next_action": "PMが直ちに行うべきアクション1つ"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove ```
            
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            result["remaining_requests"] = self.get_remaining_requests()
            
            return result
        
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse AI response as JSON: {e}",
                "raw_response": response.text,
                "remaining_requests": self.get_remaining_requests()
            }
        
        except Exception as e:
            return {
                "error": f"AI request failed: {str(e)}",
                "remaining_requests": self.get_remaining_requests()
            }
    
    def _build_context(self, issues_data, schedule_data) -> str:
        """Build context string from data"""
        context_parts = []
        
        if issues_data:
            context_parts.append(f"## Issue Log ({len(issues_data)}件)")
            
            # Summarize by priority
            priorities = {}
            for issue in issues_data:
                p = issue.get('優先度', '不明')
                priorities[p] = priorities.get(p, 0) + 1
            
            context_parts.append(f"優先度別: {priorities}")
            
            # Show urgent/high priority issues
            urgent = [i for i in issues_data if i.get('優先度') in ['緊急', '高']]
            if urgent:
                context_parts.append(f"\n緊急・高優先度課題 ({len(urgent)}件):")
                for issue in urgent[:5]:  # Top 5
                    context_parts.append(
                        f"- [{issue.get('ベンダー名', 'N/A')}] {issue.get('内容', 'N/A')} "
                        f"(期限: {issue.get('期限', 'N/A')}, 担当: {issue.get('担当者', 'N/A')})"
                    )
        
        if schedule_data:
            context_parts.append(f"\n## Schedule ({len(schedule_data)}タスク)")
            
            # Summarize by status
            statuses = {}
            for task in schedule_data:
                s = task.get('ステータス', '不明')
                statuses[s] = statuses.get(s, 0) + 1
            
            context_parts.append(f"ステータス別: {statuses}")
            
            # Show stalled tasks
            stalled = [t for t in schedule_data if t.get('ステータス') == '停滞']
            if stalled:
                context_parts.append(f"\n停滞中タスク ({len(stalled)}件):")
                for task in stalled[:5]:
                    context_parts.append(
                        f"- {task.get('タスク', 'N/A')} (担当: {task.get('担当者', 'N/A')})"
                    )
        
        return "\n".join(context_parts) if context_parts else "データなし"
    
    def _load_pmo_persona(self) -> str:
        """Load PMO persona prompt from knowledge base"""
        persona_path = os.path.join(
            os.path.dirname(__file__), 
            '../../resources/knowledge/pmo_persona.md'
        )
        
        if os.path.exists(persona_path):
            with open(persona_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Fallback persona
        return """# Role
あなたは極めて優秀な「影のPMO（myPMO)」です。
ユーザー（孤独なPM）の参謀として、PMBOKの知識と冷徹な分析力でプロジェクトを成功に導きます。

# Behavioral Guidelines
1. **思考整理ファースト**: 曖昧な相談を「事実」「推測」「リスク」「決定事項」に構造化
2. **具体的指示**: ベンダーへの依頼は「To-Doリスト形式」で出力
3. **会議ハック**: アジェンダ案+「この会議で決まらないとヤバい論点」を提示
4. **トーン**: 丁寧だが断定調
5. **Next Action**: 回答の最後に必ず1つ提示
"""


if __name__ == "__main__":
    # Test connection
    from dotenv import load_dotenv
    load_dotenv()
    
    client = GeminiClient(
        project_id=os.getenv('GCP_PROJECT_ID'),
        service_account_key_path=os.getenv('SERVICE_ACCOUNT_KEY_PATH'),
        location=os.getenv('GEMINI_LOCATION'),
        model_name=os.getenv('GEMINI_MODEL')
    )
    
    print("[OK] Gemini AI connection initialized")
    print(f"Remaining requests today: {client.get_remaining_requests()}/{client.DAILY_LIMIT}")
    
    # Simple test
    result = client.analyze_with_context(
        user_query="テストメッセージです。動作確認。",
        issues_data=None,
        schedule_data=None
    )
    
    print("\nTest response:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
