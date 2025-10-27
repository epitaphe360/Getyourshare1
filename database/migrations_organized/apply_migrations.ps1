#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script d'application automatique des migrations SQL pour ShareYourSales
.DESCRIPTION
    Applique toutes les migrations SQL dans l'ordre numerique depuis migrations_organized/
.PARAMETER DatabaseUrl
    URL de connexion PostgreSQL (ex: postgresql://user:pass@localhost:5432/dbname)
.PARAMETER MigrationsPath
    Chemin vers le dossier des migrations (defaut: ./migrations_organized)
.PARAMETER DryRun
    Mode simulation : affiche les migrations sans les executer
.EXAMPLE
    .\apply_migrations.ps1 -DatabaseUrl "postgresql://postgres:password@localhost:5432/shareyoursales"
.EXAMPLE
    .\apply_migrations.ps1 -DryRun
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$DatabaseUrl = $env:DATABASE_URL,
    
    [Parameter(Mandatory=$false)]
    [string]$MigrationsPath = ".",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

# Verifier que psql est disponible (sauf en DRY RUN)
if (-not $DryRun) {
    try {
        $null = Get-Command psql -ErrorAction Stop
    } catch {
        Write-Error "psql n'est pas installe ou n'est pas dans le PATH"
        Write-Host "   Installez PostgreSQL client: https://www.postgresql.org/download/"
        exit 1
    }
}

# Verifier l'URL de la base de donnees (sauf en DRY RUN)
if (-not $DryRun -and -not $DatabaseUrl) {
    Write-Error "DATABASE_URL non definie. Utilisez -DatabaseUrl ou definissez DATABASE_URL"
    exit 1
}

$separator = "============================================================"

Write-Host "ShareYourSales - Application des migrations SQL" -ForegroundColor Cyan
Write-Host $separator
if (-not $DryRun) {
    Write-Host "Base de donnees : $DatabaseUrl" -ForegroundColor Yellow
}
Write-Host "Dossier migrations : $MigrationsPath" -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "Mode : DRY RUN (simulation)" -ForegroundColor Magenta
} else {
    Write-Host "Mode : EXECUTION" -ForegroundColor Green
}
Write-Host $separator
Write-Host ""

# Recuperer tous les fichiers .sql dans l'ordre numerique
$migrationFiles = Get-ChildItem -Path $MigrationsPath -Filter "*.sql" | 
    Where-Object { $_.Name -match '^\d{3}_.*\.sql$' } |
    Sort-Object Name

if ($migrationFiles.Count -eq 0) {
    Write-Warning "Aucune migration trouvee dans $MigrationsPath"
    exit 0
}

Write-Host "Migrations detectees : $($migrationFiles.Count)" -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failedCount = 0
$skippedCount = 0

foreach ($file in $migrationFiles) {
    $migrationName = $file.Name
    $migrationPath = $file.FullName
    
    Write-Host "Migration : $migrationName" -ForegroundColor White
    
    if ($DryRun) {
        Write-Host "   [DRY RUN] Serait executee : $migrationPath" -ForegroundColor Gray
        $skippedCount++
        continue
    }
    
    try {
        # Executer la migration via psql
        $output = psql $DatabaseUrl -f $migrationPath 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   Succes" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "   Echec (code: $LASTEXITCODE)" -ForegroundColor Red
            Write-Host "   Erreur : $output" -ForegroundColor Red
            $failedCount++
            
            # Arreter en cas d'erreur
            Write-Host ""
            Write-Error "Migration echouee : $migrationName. Arret du processus."
            break
        }
    } catch {
        Write-Host "   Exception : $_" -ForegroundColor Red
        $failedCount++
        break
    }
    
    Write-Host ""
}

# Resume
Write-Host $separator
Write-Host "RESUME" -ForegroundColor Cyan
Write-Host $separator

if ($DryRun) {
    Write-Host "Migrations simulees : $skippedCount" -ForegroundColor Yellow
} else {
    Write-Host "Migrations reussies : $successCount" -ForegroundColor Green
    Write-Host "Migrations echouees : $failedCount" -ForegroundColor Red
    
    if ($failedCount -eq 0 -and $successCount -gt 0) {
        Write-Host ""
        Write-Host "Toutes les migrations ont ete appliquees avec succes !" -ForegroundColor Green
    } elseif ($failedCount -gt 0) {
        Write-Host ""
        Write-Host "Certaines migrations ont echoue. Verifiez les erreurs ci-dessus." -ForegroundColor Yellow
        exit 1
    }
}

Write-Host $separator
