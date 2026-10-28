# Prepare-ROMs.ps1 - build a runtime-ready Samurai Shodown ROM folder from
# your own dumps. This script extracts the MAME samsho and neogeo sets; it
# does not download anything and contains no ROM data.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\Prepare-ROMs.ps1
#   powershell -ExecutionPolicy Bypass -File .\Prepare-ROMs.ps1 -SamshoZip C:\path\samsho.zip -NeoGeoZip C:\path\neogeo.zip

param(
    [string]$SamshoZip = "",
    [string]$NeoGeoZip = "",
    [string]$OutDir = ""
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $OutDir) { $OutDir = Join-Path $here "roms" }

function Ask-Zip($label, $current) {
    if ($current -and (Test-Path $current)) { return (Resolve-Path $current).Path }
    while ($true) {
        $p = Read-Host "Path to $label"
        $p = $p.Trim('"').Trim()
        if (Test-Path $p) { return (Resolve-Path $p).Path }
        Write-Host "Not found: $p" -ForegroundColor Yellow
    }
}

$SamshoZip = Ask-Zip "samsho.zip" $SamshoZip
$NeoGeoZip = Ask-Zip "neogeo.zip" $NeoGeoZip

New-Item -ItemType Directory -Force $OutDir | Out-Null

Write-Host "Extracting $SamshoZip"
tar -xf $SamshoZip -C $OutDir
if ($LASTEXITCODE -ne 0) { throw "Could not extract samsho.zip with tar" }
Write-Host "Extracting $NeoGeoZip"
tar -xf $NeoGeoZip -C $OutDir
if ($LASTEXITCODE -ne 0) { throw "Could not extract neogeo.zip with tar" }

Write-Host ""
Write-Host "Done. Run:" -ForegroundColor Green
Write-Host "  .\`"Samurai Shodown.exe\`" --rom-path `"$OutDir`""
