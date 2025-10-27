#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script d'execution des tests pytest pour ShareYourSales Backend
.DESCRIPTION
    Execute les tests avec differentes options (coverage, markers, etc.)
.PARAMETER Type
    Type de tests a executer : all, sales, payments, unit
.PARAMETER Coverage
    Generer le rapport de coverage
.PARAMETER Verbose
    Mode verbeux
.PARAMETER Html
    Generer rapport HTML coverage
.EXAMPLE
    .\run_tests.ps1
.EXAMPLE
    .\run_tests.ps1 -Type sales -Coverage -Verbose
.EXAMPLE
    .\run_tests.ps1 -Coverage -Html
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "sales", "payments", "unit")]
    [string]$Type = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$Coverage,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose,
    
    [Parameter(Mandatory=$false)]
    [switch]$Html
)

$separator = "============================================================"

Write-Host "ShareYourSales - Execution des Tests Backend" -ForegroundColor Cyan
Write-Host $separator

# Verifier que pytest est installe
try {
    $null = Get-Command pytest -ErrorAction Stop
} catch {
    Write-Error "pytest n'est pas installe. Installez avec: pip install -r requirements-dev.txt"
    exit 1
}

# Construire la commande pytest
$pytestCmd = "pytest"

# Options de base
$pytestArgs = @()

if ($Verbose) {
    $pytestArgs += "-v"
}

# Selectionner le type de tests
switch ($Type) {
    "sales" {
        Write-Host "Type de tests : Sales uniquement" -ForegroundColor Yellow
        $pytestArgs += "-m"
        $pytestArgs += "sales"
    }
    "payments" {
        Write-Host "Type de tests : Payments uniquement" -ForegroundColor Yellow
        $pytestArgs += "-m"
        $pytestArgs += "payments"
    }
    "unit" {
        Write-Host "Type de tests : Unit uniquement" -ForegroundColor Yellow
        $pytestArgs += "-m"
        $pytestArgs += "unit"
    }
    default {
        Write-Host "Type de tests : Tous" -ForegroundColor Yellow
    }
}

# Coverage
if ($Coverage) {
    Write-Host "Coverage : Active" -ForegroundColor Green
    $pytestArgs += "--cov=services"
    $pytestArgs += "--cov-report=term-missing"
    
    if ($Html) {
        Write-Host "Rapport HTML : Active" -ForegroundColor Green
        $pytestArgs += "--cov-report=html"
    }
}

Write-Host $separator
Write-Host ""

# Executer pytest
$command = "$pytestCmd $($pytestArgs -join ' ')"
Write-Host "Commande : $command" -ForegroundColor Gray
Write-Host ""

try {
    & pytest @pytestArgs
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    Write-Host $separator
    
    if ($exitCode -eq 0) {
        Write-Host "SUCCES : Tous les tests ont reussi !" -ForegroundColor Green
        
        if ($Html -and $Coverage) {
            Write-Host ""
            Write-Host "Rapport HTML genere dans : htmlcov/index.html" -ForegroundColor Cyan
        }
    } else {
        Write-Host "ECHEC : Certains tests ont echoue" -ForegroundColor Red
        exit $exitCode
    }
    
    Write-Host $separator
    
} catch {
    Write-Error "Erreur lors de l'execution des tests : $_"
    exit 1
}
