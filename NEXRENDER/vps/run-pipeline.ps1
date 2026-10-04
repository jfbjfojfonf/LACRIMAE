$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path (Join-Path $Repo "pipeline.py"))) {
    $Repo = Split-Path -Parent $PSScriptRoot
}
Set-Location $Repo
$Dry = $args -contains "-DryRun"
if ($Dry) {
    python pipeline.py --dry-run
} else {
    python pipeline.py
}
