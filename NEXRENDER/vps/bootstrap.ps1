$ErrorActionPreference = "Stop"
$Root = "C:\nexrender"
$Dirs = @(
    "sources",
    "inbox",
    "outbox",
    "queue",
    "queue\jobs",
    "scripts",
    "presets",
    "templates",
    "work"
)
foreach ($Name in $Dirs) {
    New-Item -ItemType Directory -Force -Path (Join-Path $Root $Name) | Out-Null
}

$Repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path (Join-Path $Repo "NEXRENDER\scripts\apply_cc2.jsx"))) {
    $Repo = Split-Path -Parent $PSScriptRoot
}
$JsxSrc = Join-Path $Repo "NEXRENDER\scripts\apply_cc2.jsx"
if (Test-Path $JsxSrc) {
    Copy-Item $JsxSrc (Join-Path $Root "scripts\apply_cc2.jsx") -Force
    Write-Host "copied apply_cc2.jsx"
} else {
    Write-Host "WARNING: apply_cc2.jsx not found, clone the repo first"
}

Write-Host "nexrender folders ready under $Root"
Write-Host "NEXT: copy cc2.ffx to $Root\presets\cc2.ffx"
Write-Host "NEXT: save template.aep to $Root\templates\template.aep"
