# PowerShell script to start the Dermalens API server
Write-Host "🚀 Starting Dermalens API Server..." -ForegroundColor Green
Write-Host ""

# Navigate to the API directory
Set-Location $PSScriptRoot

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if uvicorn is installed
try {
    python -c "import uvicorn" 2>$null
    Write-Host "✅ Uvicorn is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Uvicorn not found! Installing..." -ForegroundColor Yellow
    pip install uvicorn[standard]
}

Write-Host ""
Write-Host "🌐 Starting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "📖 API docs will be available at http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "⏹️  Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start the server
try {
    python main.py
} catch {
    Write-Host ""
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check if port 8000 is already in use" -ForegroundColor Yellow
    Write-Host "2. Verify all dependencies are installed: pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host "3. Check config.py for missing environment variables" -ForegroundColor Yellow
    exit 1
}

