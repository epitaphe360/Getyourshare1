# 🚀 SCRIPT DE DÉMARRAGE AUTOMATIQUE
# Ce script démarre automatiquement le backend et le frontend

Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   SHAREYOURSALES - DÉMARRAGE AUTOMATIQUE   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Vérifier si on est dans le bon répertoire
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ Erreur: Ce script doit être exécuté depuis la racine du projet" -ForegroundColor Red
    Write-Host "   Répertoire actuel: $PWD" -ForegroundColor Yellow
    exit 1
}

# 1. Vérifier les dépendances Python
Write-Host "🔍 Vérification des dépendances Python..." -ForegroundColor Yellow
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  Fichier .env manquant dans backend/" -ForegroundColor Red
    Write-Host "   Veuillez créer le fichier .env avec vos credentials Supabase" -ForegroundColor Yellow
    exit 1
}

# 2. Démarrer le backend
Write-Host "`n🚀 Démarrage du serveur backend..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location backend
    python server.py
}

Write-Host "✅ Backend démarré (Job ID: $($backendJob.Id))" -ForegroundColor Green
Write-Host "   URL: http://localhost:8001" -ForegroundColor Gray

Start-Sleep -Seconds 3

# 3. Vérifier que le backend est actif
Write-Host "`n🔍 Vérification du backend..." -ForegroundColor Yellow
$maxRetries = 10
$retryCount = 0
$backendReady = $false

while ($retryCount -lt $maxRetries -and -not $backendReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/docs" -Method Get -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "✅ Backend opérationnel !" -ForegroundColor Green
        }
    } catch {
        $retryCount++
        Write-Host "   Tentative $retryCount/$maxRetries..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $backendReady) {
    Write-Host "⚠️  Le backend met du temps à démarrer, mais continuons..." -ForegroundColor Yellow
}

# 4. Vérifier si le build frontend existe
Write-Host "`n🔍 Vérification du build frontend..." -ForegroundColor Yellow
if (-not (Test-Path "frontend\build")) {
    Write-Host "⚠️  Build frontend manquant, création en cours..." -ForegroundColor Yellow
    Write-Host "   (Cela peut prendre 1-2 minutes)" -ForegroundColor Gray
    
    Set-Location frontend
    npm run build
    Set-Location ..
    
    if (-not (Test-Path "frontend\build")) {
        Write-Host "❌ Échec du build frontend" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Build frontend créé" -ForegroundColor Green
} else {
    Write-Host "✅ Build frontend existant" -ForegroundColor Green
}

# 5. Démarrer le frontend
Write-Host "`n🚀 Démarrage du serveur frontend..." -ForegroundColor Yellow

# Vérifier si 'serve' est installé
try {
    $null = serve --version 2>&1
    Write-Host "✅ serve est installé" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Installation de 'serve' en cours..." -ForegroundColor Yellow
    npm install -g serve
}

$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location frontend
    serve -s build -l 52112
}

Write-Host "✅ Frontend démarré (Job ID: $($frontendJob.Id))" -ForegroundColor Green
Write-Host "   URL: http://localhost:52112" -ForegroundColor Gray

Start-Sleep -Seconds 3

# 6. Afficher le résumé
Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║          ✅ TOUT EST DÉMARRÉ !             ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📊 Services actifs:" -ForegroundColor Cyan
Write-Host "   • Backend API:  http://localhost:8001" -ForegroundColor White
Write-Host "   • API Docs:     http://localhost:8001/docs" -ForegroundColor White
Write-Host "   • Frontend:     http://localhost:52112" -ForegroundColor White

Write-Host "`n🔑 Comptes de test:" -ForegroundColor Cyan
Write-Host "   • Admin:        admin@shareyoursales.com / Admin123!" -ForegroundColor White
Write-Host "   • Marchand:     contact@techstyle.fr / Merchant123!" -ForegroundColor White
Write-Host "   • Influenceur:  emma.style@instagram.com / Influencer123!" -ForegroundColor White

Write-Host "`n⚠️  IMPORTANT:" -ForegroundColor Yellow
Write-Host "   Si les tables Supabase ne sont pas créées:" -ForegroundColor Yellow
Write-Host "   1. Ouvrir: https://supabase.com/dashboard" -ForegroundColor Gray
Write-Host "   2. SQL Editor → Nouveau" -ForegroundColor Gray
Write-Host "   3. Exécuter: database/create_tables_missing.sql" -ForegroundColor Gray
Write-Host "   Voir: GUIDE_CREATION_TABLES.md" -ForegroundColor Gray

Write-Host "`n📝 Logs:" -ForegroundColor Cyan
Write-Host "   • Backend Job:  $($backendJob.Id)" -ForegroundColor White
Write-Host "   • Frontend Job: $($frontendJob.Id)" -ForegroundColor White

Write-Host "`n🛑 Pour arrêter les services:" -ForegroundColor Cyan
Write-Host "   Stop-Job -Id $($backendJob.Id), $($frontendJob.Id)" -ForegroundColor White
Write-Host "   Remove-Job -Id $($backendJob.Id), $($frontendJob.Id)" -ForegroundColor White

Write-Host "`n🌐 Ouverture du navigateur dans 3 secondes..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Ouvrir le navigateur
Start-Process "http://localhost:52112"

Write-Host "`n✨ Bonne utilisation !" -ForegroundColor Green
Write-Host "   Appuyez sur une touche pour voir les logs (Ctrl+C pour quitter)...`n" -ForegroundColor Gray

# Attendre une touche
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Afficher les logs
Write-Host "`n📋 Logs Backend:" -ForegroundColor Cyan
Receive-Job -Id $backendJob.Id

Write-Host "`n📋 Logs Frontend:" -ForegroundColor Cyan
Receive-Job -Id $frontendJob.Id

Write-Host "`n✅ Pour continuer à utiliser l'application, gardez cette fenêtre ouverte" -ForegroundColor Green
Write-Host "   (Ctrl+C pour tout arrêter)`n" -ForegroundColor Gray

# Garder le script actif
try {
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Vérifier si les jobs sont encore actifs
        $backendStatus = Get-Job -Id $backendJob.Id
        $frontendStatus = Get-Job -Id $frontendJob.Id
        
        if ($backendStatus.State -ne "Running") {
            Write-Host "⚠️  Backend arrêté !" -ForegroundColor Red
        }
        if ($frontendStatus.State -ne "Running") {
            Write-Host "⚠️  Frontend arrêté !" -ForegroundColor Red
        }
    }
} finally {
    # Nettoyage à la sortie
    Write-Host "`n🛑 Arrêt des services..." -ForegroundColor Yellow
    Stop-Job -Id $backendJob.Id, $frontendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $backendJob.Id, $frontendJob.Id -ErrorAction SilentlyContinue
    Write-Host "✅ Services arrêtés" -ForegroundColor Green
}
