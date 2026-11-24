# Le site complet en local, pour tester sans la prod : sans Docker, sans MongoDB,
# sans envoi de mail. Voir dev\run_local.py.
#   powershell -ExecutionPolicy Bypass -File dev\run_local.ps1
#   ... -Rebuild    reconstruit le frontend (après une modification)
param([switch]$Rebuild)
$ErrorActionPreference = "Stop"
$Site = Split-Path $PSScriptRoot -Parent
Set-Location $Site

# 1. Environnement Python du serveur (.venv-dev, créé une fois)
$py = Join-Path $Site ".venv-dev\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "[local] Création de .venv-dev..." -ForegroundColor Cyan
    if (Get-Command py.exe -ErrorAction SilentlyContinue) { py -3 -m venv .venv-dev } else { python -m venv .venv-dev }
    if (-not (Test-Path $py)) { throw "Python introuvable : installe Python 3.10+ (winget install Python.Python.3.12)." }
}
& $py -m pip install --quiet --disable-pip-version-check -r dev\requirements-local.txt
if ($LASTEXITCODE -ne 0) { throw "pip install a échoué." }

# 2. Frontend construit, servi par le serveur sur la même adresse
if ($Rebuild -or -not (Test-Path "frontend\dist\index.html")) {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw "Node.js manque : winget install OpenJS.NodeJS.LTS" }
    Push-Location frontend
    try {
        if (-not (Test-Path node_modules)) { npm ci --legacy-peer-deps --no-audit --no-fund; if ($LASTEXITCODE) { throw "npm ci a échoué." } }
        $env:VITE_BACKEND_URL = ""          # API sur la même adresse que le site, comme en prod
        npm run build; if ($LASTEXITCODE) { throw "npm run build a échoué." }
    } finally { Pop-Location; Remove-Item Env:VITE_BACKEND_URL -ErrorAction SilentlyContinue }
}

# 3. Le serveur
& $py dev\run_local.py
