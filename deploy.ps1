# PowerShell version of deployment script for Windows
# myPMO Agent - Cloud Functions Deployment Script

Write-Host "============================================================"
Write-Host "myPMO Agent - Cloud Functions Deployment"
Write-Host "============================================================"

# Configuration
$PROJECT_ID = "my-pmo-agent-v1"
$FUNCTION_NAME = "my-pmo-agent"
$REGION = "us-central1"
$RUNTIME = "python311"
$ENTRY_POINT = "handle_chat_message"

# Environment variables
$SPREADSHEET_ID = "1C6ua596iFVCG2fx6YnYviqthrF3K4EYYxUPJhNUUt7A"
$ISSUE_SHEET_NAME = "Issues"
$SCHEDULE_SHEET_NAME = "Schedule"
$GEMINI_MODEL = "gemini-2.5-flash"
$GEMINI_LOCATION = "us-central1"

Write-Host ""
Write-Host "Deploying to Cloud Functions..."
Write-Host "  Project: $PROJECT_ID"
Write-Host "  Function: $FUNCTION_NAME"
Write-Host "  Region: $REGION"
Write-Host ""

# Deploy Cloud Function
gcloud functions deploy $FUNCTION_NAME `
  --gen2 `
  --runtime=$RUNTIME `
  --region=$REGION `
  --source=./src `
  --entry-point=$ENTRY_POINT `
  --trigger-http `
  --allow-unauthenticated `
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,SPREADSHEET_ID=$SPREADSHEET_ID,ISSUE_SHEET_NAME=$ISSUE_SHEET_NAME,SCHEDULE_SHEET_NAME=$SCHEDULE_SHEET_NAME,GEMINI_MODEL=$GEMINI_MODEL,GEMINI_LOCATION=$GEMINI_LOCATION" `
  --service-account=pmo-agent-sa@my-pmo-agent-v1.iam.gserviceaccount.com `
  --timeout=60s `
  --memory=512MB `
  --max-instances=10 `
  --project=$PROJECT_ID

if ($LASTEXITCODE -eq 0) {
  Write-Host ""
  Write-Host "============================================================"
  Write-Host "[SUCCESS] Deployment completed!"
  Write-Host "============================================================"
  Write-Host ""
  Write-Host "Function URL:"
  gcloud functions describe $FUNCTION_NAME --region=$REGION --project=$PROJECT_ID --format='value(serviceConfig.uri)'
  Write-Host ""
  Write-Host "Next steps:"
  Write-Host "1. Copy the Function URL above"
  Write-Host "2. Follow GOOGLE_CHAT_SETUP.md to configure Google Chat Webhook"
  Write-Host ""
} else {
  Write-Host ""
  Write-Host "============================================================"
  Write-Host "[ERROR] Deployment failed"
  Write-Host "============================================================"
  Write-Host ""
  Write-Host "Common issues:"
  Write-Host "1. Check if Cloud Functions API is enabled"
  Write-Host "2. Verify service account permissions"
  Write-Host "3. Check project billing status"
  Write-Host ""
  exit 1
}
