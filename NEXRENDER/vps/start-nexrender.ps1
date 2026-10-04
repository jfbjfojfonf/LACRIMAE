$ErrorActionPreference = "Stop"
if (-not $env:NEXRENDER_SECRET) {
    Write-Error "Set NEXRENDER_SECRET first, then re-run."
    exit 1
}
$Port = 3000
$HostUrl = "http://127.0.0.1:$Port"
$Work = "C:\nexrender\work"
New-Item -ItemType Directory -Force -Path $Work | Out-Null

$AerenderCandidates = @(
    "C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\aerender.exe",
    "C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\aerender.exe",
    "C:\Program Files\Adobe\Adobe After Effects 2023\Support Files\aerender.exe"
)
$Binary = $AerenderCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Binary) {
    Write-Error "aerender.exe not found. Install After Effects first."
    exit 1
}

Write-Host "aerender: $Binary"
Write-Host "starting nexrender-server on $HostUrl"
Start-Process -FilePath "nexrender-server" -ArgumentList "--port=$Port","--secret=$env:NEXRENDER_SECRET" -WindowStyle Minimized
Start-Sleep -Seconds 2
Write-Host "starting nexrender-worker"
Start-Process -FilePath "nexrender-worker" -ArgumentList "--host=$HostUrl","--secret=$env:NEXRENDER_SECRET","--binary=`"$Binary`"","--workpath=$Work" -WindowStyle Minimized
Write-Host "server + worker launched. Keep this session open."
