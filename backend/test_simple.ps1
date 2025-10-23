# Script de test PowerShell pour les endpoints

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  TEST DES NOUVEAUX ENDPOINTS" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Test de connexion
Write-Host "🔐 Test de connexion..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@shareyoursales.com"
    password = "Admin123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.token
    Write-Host "✅ Connexion réussie - Token obtenu" -ForegroundColor Green
    
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    # Test produits
    Write-Host "`n📦 Test GET /api/products..." -ForegroundColor Yellow
    try {
        $products = Invoke-RestMethod -Uri "http://localhost:8001/api/products" -Method Get -Headers $headers
        Write-Host "✅ $($products.Count) produits trouvés" -ForegroundColor Green
        if ($products.Count -gt 0) {
            Write-Host "   Premier produit: $($products[0].name)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test campagnes
    Write-Host "`n🎯 Test GET /api/campaigns..." -ForegroundColor Yellow
    try {
        $campaigns = Invoke-RestMethod -Uri "http://localhost:8001/api/campaigns" -Method Get -Headers $headers
        Write-Host "✅ $($campaigns.Count) campagnes trouvées" -ForegroundColor Green
        if ($campaigns.Count -gt 0) {
            Write-Host "   Première campagne: $($campaigns[0].name)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test ventes
    Write-Host "`n💰 Test GET /api/sales/1..." -ForegroundColor Yellow
    try {
        $sales = Invoke-RestMethod -Uri "http://localhost:8001/api/sales/1" -Method Get -Headers $headers
        Write-Host "✅ $($sales.Count) ventes trouvées" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test commissions
    Write-Host "`n💵 Test GET /api/commissions/1..." -ForegroundColor Yellow
    try {
        $commissions = Invoke-RestMethod -Uri "http://localhost:8001/api/commissions/1" -Method Get -Headers $headers
        Write-Host "✅ $($commissions.Count) commissions trouvées" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test rapports
    Write-Host "`n📊 Test GET /api/reports/performance..." -ForegroundColor Yellow
    try {
        $report = Invoke-RestMethod -Uri "http://localhost:8001/api/reports/performance?user_id=1&start_date=2024-01-01&end_date=2025-12-31" -Method Get -Headers $headers
        Write-Host "✅ Rapport généré:" -ForegroundColor Green
        Write-Host "   Total ventes: $($report.total_sales)" -ForegroundColor Gray
        Write-Host "   Revenus: $($report.total_revenue)€" -ForegroundColor Gray
        Write-Host "   Commissions: $($report.total_commission)€" -ForegroundColor Gray
    } catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test settings
    Write-Host "`n⚙️  Test GET /api/settings..." -ForegroundColor Yellow
    try {
        $settings = Invoke-RestMethod -Uri "http://localhost:8001/api/settings" -Method Get -Headers $headers
        Write-Host "✅ $($settings.Count) paramètres trouvés" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Erreur de connexion: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  TESTS TERMINÉS" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan
