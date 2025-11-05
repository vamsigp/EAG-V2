# PowerShell script to download and install cloudflared

Write-Host "Downloading cloudflared..." -ForegroundColor Cyan

# Create a local bin directory if it doesn't exist
$binDir = Join-Path $PSScriptRoot "bin"
if (-not (Test-Path $binDir)) {
    New-Item -ItemType Directory -Path $binDir | Out-Null
}

$cloudflaredPath = Join-Path $binDir "cloudflared.exe"

# Download cloudflared
try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile $cloudflaredPath -ErrorAction Stop
    Write-Host "✅ cloudflared downloaded successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "cloudflared location: $cloudflaredPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To use cloudflared, run:" -ForegroundColor Cyan
    Write-Host "  .\bin\cloudflared.exe tunnel --url http://localhost:8080" -ForegroundColor White
    Write-Host ""
    Write-Host "Or add to PATH to use 'cloudflared' command directly."
} catch {
    Write-Host "❌ Error downloading cloudflared: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual installation:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://github.com/cloudflare/cloudflared/releases/latest" -ForegroundColor White
    Write-Host "2. Download: cloudflared-windows-amd64.exe" -ForegroundColor White
    Write-Host "3. Rename to cloudflared.exe and place in your PATH or project folder" -ForegroundColor White
    exit 1
}

