# Cloud Functions HTTP API Test Script
# Tests the myPMO Agent Cloud Function directly without Google Chat

Write-Host "============================================================"
Write-Host "myPMO Agent - Cloud Functions API Test"
Write-Host "============================================================"

$FUNCTION_URL = "https://us-central1-my-pmo-agent-v1.cloudfunctions.net/my-pmo-agent"

Write-Host ""
Write-Host "Testing Cloud Function..."
Write-Host "URL: $FUNCTION_URL"
Write-Host ""

# Test 1: Simple /ask command
Write-Host "[TEST 1] Simple /ask command"
Write-Host "============================================================"

$body = @{
    message = @{
        text = "/ask What is the current status?"
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $FUNCTION_URL -Method Post -Body $body -ContentType "application/json"
    Write-Host "[SUCCESS] Response received:"
    Write-Host ($response | ConvertTo-Json -Depth 10)
}
catch {
    Write-Host "[ERROR] Request failed:"
    Write-Host $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody"
    }
}

Write-Host ""
Write-Host ""

# Test 2: Help command (no specific command)
Write-Host "[TEST 2] Help command"
Write-Host "============================================================"

$body2 = @{
    message = @{
        text = "help"
    }
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri $FUNCTION_URL -Method Post -Body $body2 -ContentType "application/json"
    Write-Host "[SUCCESS] Response received:"
    Write-Host ($response2 | ConvertTo-Json -Depth 10)
}
catch {
    Write-Host "[ERROR] Request failed:"
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host ""

# Test 3: Risk alert
Write-Host "[TEST 3] Risk alert command"
Write-Host "============================================================"

$body3 = @{
    message = @{
        text = "/risk-alert"
    }
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri $FUNCTION_URL -Method Post -Body $body3 -ContentType "application/json"
    Write-Host "[SUCCESS] Response received:"
    Write-Host ($response3 | ConvertTo-Json -Depth 10)
}
catch {
    Write-Host "[ERROR] Request failed:"
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "============================================================"
Write-Host "Testing Complete!"
Write-Host "============================================================"
