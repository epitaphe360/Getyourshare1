# Script maître pour démarrer Backend + Frontend
# ShareYourSales - Système complet

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "   SHAREYOURSALES - DÉMARRAGE SYSTÈME COMPLET" -ForegroundColor Green  
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

$rootPath = "c:\Users\Admin\Desktop\shareyoursales\Getyourshare1"

# Arrêter tous les anciens processus
Write-Host "🧹 Nettoyage des anciens processus..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "✅ Processus nettoyés" -ForegroundColor Green
Write-Host ""

# Lancer le BACKEND dans un nouveau terminal PowerShell
Write-Host "🚀 Lancement du BACKEND (FastAPI)..." -ForegroundColor Cyan
$backendScript = Join-Path $rootPath "start_backend.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", $backendScript

Write-Host "   ⏳ Attente du démarrage (5 secondes)..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Lancer le FRONTEND dans un nouveau terminal PowerShell
Write-Host "🚀 Lancement du FRONTEND (React)..." -ForegroundColor Cyan
$frontendScript = Join-Path $rootPath "start_frontend.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", $frontendScript

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "   ✅ SYSTÈME LANCÉ AVEC SUCCÈS !" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📡 SERVEURS ACTIFS:" -ForegroundColor Yellow
Write-Host "   Backend:  http://localhost:8001" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "👤 COMPTES DE TEST:" -ForegroundColor Yellow
Write-Host "   Admin:      admin@shareyoursales.com / admin123" -ForegroundColor White
Write-Host "   Merchant:   contact@techstyle.fr / merchant123" -ForegroundColor White
Write-Host "   Influencer: emma.style@instagram.com / influencer123" -ForegroundColor White
Write-Host ""
Write-Host "📝 NOTES:" -ForegroundColor Yellow
Write-Host "   - Deux fenêtres PowerShell ont été ouvertes" -ForegroundColor Gray
Write-Host "   - NE PAS fermer ces fenêtres pour garder les serveurs actifs" -ForegroundColor Gray
Write-Host "   - Pour arrêter: CTRL+C dans chaque fenêtre" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "   Ouvrez http://localhost:3000 dans votre navigateur" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Ouvrir le navigateur automatiquement après 8 secondes
Start-Sleep -Seconds 3
Write-Host "🌐 Ouverture du navigateur..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✅ Tout est prêt ! Bon développement 🚀" -ForegroundColor Green
Write-Host ""
