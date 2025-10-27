# Nettoyage processus
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Aller dans backend
Set-Location "c:\Users\Admin\Desktop\shareyoursales\Getyourshare1\backend"

# Lancer serveur
Write-Host "Backend demarre sur http://localhost:8001" -ForegroundColor Green
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --log-level info
