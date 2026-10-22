# Ejecutor unico - TransControl API. Uso:
#   $env:RUN_LABEL = "before" ; .\scripts\run_security_checks.ps1
$ErrorActionPreference = "Stop"
$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "No existe $python. Crea o selecciona el .venv del laboratorio." }

$label = $env:RUN_LABEL
if ([string]::IsNullOrWhiteSpace($label)) { $label = Get-Date -Format "yyyyMMdd-HHmmss" }
$evidenceDir = Join-Path "evidence" $label
New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
$script:failed = $false

function Invoke-Check {
    param([string]$Name, [string[]]$Arguments)
    $log = Join-Path $evidenceDir "$Name.log"
    "COMMAND: $python $($Arguments -join ' ')" | Set-Content $log
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"      # stderr de las herramientas no debe abortar
    & $python @Arguments 2>&1 | Tee-Object -FilePath $log -Append
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prev
    "EXIT_CODE=$code" | Add-Content $log
    if ($code -ne 0) { $script:failed = $true }
}

$meta = Join-Path $evidenceDir "metadata.txt"
"RUN_LABEL=$label"                          | Set-Content $meta
"DATE=$(Get-Date -Format o)"                | Add-Content $meta
"PYTHON=$(& $python --version 2>&1)"        | Add-Content $meta
"BRANCH=$(git branch --show-current)"       | Add-Content $meta
"COMMIT=$(git rev-parse HEAD)"              | Add-Content $meta
"STATUS=$(git status --short)"              | Add-Content $meta
& $python -m pip freeze | Set-Content (Join-Path $evidenceDir "pip-freeze.txt")

Invoke-Check "pytest"    @("-m","pytest","-q","--junitxml",(Join-Path $evidenceDir "pytest-junit.xml"))
Invoke-Check "bandit"    @("-m","bandit","-r",".","-x","./.venv,./tests,./evidence,./scripts","-f","json","-o",(Join-Path $evidenceDir "bandit.json"))
Invoke-Check "pip-audit" @("-m","pip_audit","-r","requirements.txt","--format","json","-o",(Join-Path $evidenceDir "pip-audit.json"))

# Hash SHA-256 de cada archivo de evidencia (integridad y respaldo de no repudio)
Get-ChildItem $evidenceDir -File | Where-Object { $_.Name -ne "hashes.txt" } |
    Get-FileHash -Algorithm SHA256 |
    ForEach-Object { "$($_.Hash)  $(Split-Path $_.Path -Leaf)" } |
    Set-Content (Join-Path $evidenceDir "hashes.txt")

if ($script:failed) { Write-Host "PIPELINE FAIL. Revisa $evidenceDir"; exit 1 }
Write-Host "PIPELINE PASS. Evidencia: $evidenceDir"; exit 0
