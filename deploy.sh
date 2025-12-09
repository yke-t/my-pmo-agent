#!/bin/bash

# myPMO Agent - Cloud Functions Deployment Script

echo "============================================================"
echo "myPMO Agent - Cloud Functions Deployment"
echo "============================================================"

# Configuration
PROJECT_ID="my-pmo-agent-v1"
FUNCTION_NAME="my-pmo-agent"
REGION="us-central1"
RUNTIME="python311"
ENTRY_POINT="handle_chat_message"

# Environment variables
SPREADSHEET_ID="1C6ua596iFVCG2fx6YnYviqthrF3K4EYYxUPJhNUUt7A"
ISSUE_SHEET_NAME="Issues"
SCHEDULE_SHEET_NAME="Schedule"
GEMINI_MODEL="gemini-2.5-flash"
GEMINI_LOCATION="us-central1"

echo ""
echo "Deploying to Cloud Functions..."
echo "  Project: $PROJECT_ID"
echo "  Function: $FUNCTION_NAME"
echo "  Region: $REGION"
echo ""

# Deploy Cloud Function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=$RUNTIME \
  --region=$REGION \
  --source=./src \
  --entry-point=$ENTRY_POINT \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,SPREADSHEET_ID=$SPREADSHEET_ID,ISSUE_SHEET_NAME=$ISSUE_SHEET_NAME,SCHEDULE_SHEET_NAME=$SCHEDULE_SHEET_NAME,GEMINI_MODEL=$GEMINI_MODEL,GEMINI_LOCATION=$GEMINI_LOCATION \
  --service-account=pmo-agent-sa@my-pmo-agent-v1.iam.gserviceaccount.com \
  --timeout=60s \
  --memory=512MB \
  --max-instances=10 \
  --project=$PROJECT_ID

if [ $? -eq 0 ]; then
  echo ""
  echo "============================================================"
  echo "[SUCCESS] Deployment completed!"
  echo "============================================================"
  echo ""
  echo "Function URL:"
  gcloud functions describe $FUNCTION_NAME --region=$REGION --project=$PROJECT_ID --format='value(serviceConfig.uri)'
  echo ""
  echo "Next steps:"
  echo "1. Copy the Function URL above"
  echo "2. Follow GOOGLE_CHAT_SETUP.md to configure Google Chat Webhook"
  echo ""
else
  echo ""
  echo "============================================================"
  echo "[ERROR] Deployment failed"
  echo "============================================================"
  echo ""
  echo "Common issues:"
  echo "1. Check if Cloud Functions API is enabled"
  echo "2. Verify service account permissions"
  echo "3. Check project billing status"
  echo ""
  exit 1
fi
