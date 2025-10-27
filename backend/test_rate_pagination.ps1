# Script de test pour Rate Limiting et Pagination

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "TEST 1: PAGINATION - /api/products" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "📄 Page 1 (limit=3, offset=0):" -ForegroundColor Cyan
$response1 = Invoke-RestMethod -Uri "http://localhost:8002/api/products?limit=3&offset=0" -Method GET
Write-Host "Nombre de produits: $($response1.products.Count)" -ForegroundColor Yellow
if ($response1.pagination) {
    Write-Host "Pagination: limit=$($response1.pagination.limit), offset=$($response1.pagination.offset), total=$($response1.pagination.total)" -ForegroundColor Yellow
}

Write-Host "`n📄 Page 2 (limit=3, offset=3):" -ForegroundColor Cyan
$response2 = Invoke-RestMethod -Uri "http://localhost:8002/api/products?limit=3&offset=3" -Method GET
Write-Host "Nombre de produits: $($response2.products.Count)" -ForegroundColor Yellow
if ($response2.pagination) {
    Write-Host "Pagination: limit=$($response2.pagination.limit), offset=$($response2.pagination.offset), total=$($response2.pagination.total)" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "TEST 2: RATE LIMITING - /api/auth/login" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
Write-Host "⚠️  Limite: 5 tentatives/minute" -ForegroundColor Yellow

for ($i = 1; $i -le 6; $i++) {
    Write-Host "`n🔐 Tentative $i/6..." -ForegroundColor Cyan
    
    try {
        $body = @{
            email = "test@test.com"
            password = "wrongpassword"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8002/api/auth/login" `
                                       -Method POST `
                                       -Headers @{"Content-Type"="application/json"} `
                                       -Body $body `
                                       -ErrorAction Stop
        
        Write-Host "   ✅ Réponse reçue (status: $($response.StatusCode))" -ForegroundColor Green
        
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        
        if ($statusCode -eq 429) {
            Write-Host "   🚫 BLOQUÉ! Rate limit atteint (429 Too Many Requests)" -ForegroundColor Red
            Write-Host "   ✅ RATE LIMITING FONCTIONNE!" -ForegroundColor Green
        } elseif ($statusCode -eq 401) {
            Write-Host "   ❌ Authentification échouée (normal - mauvais mot de passe)" -ForegroundColor Yellow
        } else {
            Write-Host "   ⚠️  Erreur $statusCode : $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ TESTS TERMINÉS" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
