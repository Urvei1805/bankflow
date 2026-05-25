# BankFlow Local Smoke Test Script

$ErrorActionPreference = "Stop"

function Assert-Success($condition, $message) {
    if ($condition) {
        Write-Host "[PASS] $message" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $message" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Running BankFlow Local Smoke Test..." -ForegroundColor Cyan

# 1. Docker Containers
$containers = docker compose ps -a
Assert-Success ($containers -match "bankflow-postgres.*Up") "postgres container running"
Assert-Success ($containers -match "bankflow-redis.*Up") "redis container running"
Assert-Success ($containers -match "bankflow-auth.*Up") "auth-service container running"
Assert-Success ($containers -match "bankflow-banking.*Up") "banking-api-service container running"
Assert-Success ($containers -match "bankflow-analytics.*Up") "analytics-service container running"
Assert-Success ($containers -match "bankflow-frontend.*Up") "frontend container running"

# 2. Health Checks
try {
    $authHealth = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -ErrorAction Stop
    Assert-Success ($authHealth.status -eq "healthy") "auth-service healthy"
} catch {
    Assert-Success $false "auth-service healthy"
}

try {
    $bankHealth = Invoke-RestMethod -Uri "http://localhost:8002/health" -Method Get -ErrorAction Stop
    Assert-Success ($bankHealth.status -eq "healthy") "banking-api-service healthy"
} catch {
    Assert-Success $false "banking-api-service healthy"
}

try {
    $analyticsHealth = Invoke-RestMethod -Uri "http://localhost:8003/health" -Method Get -ErrorAction Stop
    Assert-Success ($analyticsHealth.status -eq "healthy") "analytics-service healthy"
} catch {
    Assert-Success $false "analytics-service healthy"
}

# 3. Auth Service
$username = "smokeuser_$([guid]::NewGuid().ToString().Substring(0,8))"
$email = "$username@example.com"
$password = "SmokeTest123!"

try {
    $regBody = '{"email":"' + $email + '","username":"' + $username + '","password":"' + $password + '","role":"user"}'
    $regResp = Invoke-RestMethod -Uri "http://localhost:8001/v1/auth/register" -Method Post -Body $regBody -ContentType "application/json"
    Assert-Success ($null -ne $regResp.id) "user registration successful"

    $loginBody = '{"username":"' + $username + '","password":"' + $password + '"}'
    $loginResp = Invoke-RestMethod -Uri "http://localhost:8001/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    Assert-Success ($null -ne $loginResp.access_token) "login successful"
    $token = $loginResp.access_token
} catch {
    Assert-Success $false "Auth APIs failed: $_"
}

# 4. Banking API Service
try {
    $seedResp = Invoke-RestMethod -Uri "http://localhost:8002/v1/demo/seed" -Method Post -Headers @{Authorization="Bearer $token"}
    $account_id = $seedResp.account_id
    Assert-Success ($null -ne $account_id) "demo data seeded"

    $payBody = '{"debtor_account_id":"' + $account_id + '","creditor_account_id":"ACC002","creditor_name":"Jane Smith","amount":100.0,"currency":"GBP"}'
    $payResp = Invoke-RestMethod -Uri "http://localhost:8002/v1/payments" -Method Post -Body $payBody -ContentType "application/json" -Headers @{Authorization="Bearer $token"}
    Assert-Success ($null -ne $payResp.data.id) "payment created"

    $txResp = Invoke-RestMethod -Uri "http://localhost:8002/v1/accounts/$account_id/transactions?limit=10" -Method Get -Headers @{Authorization="Bearer $token"}
    Assert-Success ($txResp.data.Count -gt 0) "transaction fetch successful"

    $consentBody = '{"tpp_id":"00000000-0000-0000-0000-000000000001","permissions":["READ_TRANSACTIONS"],"expires_in_days":90}'
    $consentResp = Invoke-RestMethod -Uri "http://localhost:8002/v1/consent" -Method Post -Body $consentBody -ContentType "application/json" -Headers @{Authorization="Bearer $token"}
    Assert-Success ($null -ne $consentResp.data.id) "consent created"
} catch {
    Assert-Success $false "Banking APIs failed: $_"
}

# 5. Analytics API Service
try {
    $analyticsSummary = Invoke-RestMethod -Uri "http://localhost:8003/v1/analytics/summary" -Method Get
    Assert-Success ($null -ne $analyticsSummary.data.id) "analytics summary endpoint working"
} catch {
    Assert-Success $false "Analytics APIs failed: $_"
}

Write-Host "All smoke tests passed successfully!" -ForegroundColor Green
