# test_api.ps1
Write-Host "Testing Movie Sentiment Analysis API" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Base URL
$baseUrl = "http://localhost:5000"

# Function to test endpoint
function Test-Endpoint {
    param($Name, $Method, $Endpoint, $Body)
    
    Write-Host "`n$Name" -ForegroundColor Yellow
    Write-Host "------------------------" -ForegroundColor Yellow
    
    try {
        if ($Method -eq "POST") {
            $jsonBody = $Body | ConvertTo-Json -Depth 5
            $response = Invoke-RestMethod -Uri "$baseUrl$Endpoint" -Method Post -Body $jsonBody -ContentType "application/json"
        } else {
            $response = Invoke-RestMethod -Uri "$baseUrl$Endpoint" -Method Get
        }
        
        $response | ConvertTo-Json -Depth 5
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test endpoints
Test-Endpoint -Name "1. Health Check" -Method "GET" -Endpoint "/health"

Test-Endpoint -Name "2. Single Prediction (Positive)" -Method "POST" -Endpoint "/predict" -Body @{review="This movie is absolutely fantastic and amazing! I loved every moment of it."}

Test-Endpoint -Name "3. Single Prediction (Negative)" -Method "POST" -Endpoint "/predict" -Body @{review="The movie was terrible and boring, complete waste of time and money."}

Test-Endpoint -Name "4. Single Prediction (Neutral)" -Method "POST" -Endpoint "/predict" -Body @{review="The movie was okay, nothing special but not bad either."}

Test-Endpoint -Name "5. Batch Prediction" -Method "POST" -Endpoint "/batch-predict" -Body @{reviews=@("Great movie!", "Terrible film", "It was okay", "Amazing cinematography", "Poor acting")}

Test-Endpoint -Name "6. Get Reviews" -Method "GET" -Endpoint "/reviews?page=1&limit=5"

Test-Endpoint -Name "7. Get Statistics" -Method "GET" -Endpoint "/stats"

Write-Host "`nAll tests completed!" -ForegroundColor Green
