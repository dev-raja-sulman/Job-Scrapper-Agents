# Job Scrapper Agent - Quick Start Script (Windows PowerShell)
# This script sets up and runs the complete job scraper application

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        🚀 Agentic AI Job Scraper - Quick Start                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "✓ Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = & python --version 2>$null
    if ($null -eq $pythonVersion) {
        $pythonVersion = & python3 --version 2>$null
    }
    Write-Host "  Found: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "  ⚠️  Python not found. Please install Python 3.9+" -ForegroundColor Yellow
    exit 1
}

# Step 2: Create virtual environment
Write-Host ""
Write-Host "✓ Creating virtual environment..." -ForegroundColor Green
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "  Virtual environment created" -ForegroundColor Gray
} else {
    Write-Host "  Virtual environment already exists" -ForegroundColor Gray
}

# Step 3: Activate virtual environment
Write-Host ""
Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

# Step 4: Install dependencies
Write-Host ""
Write-Host "✓ Installing dependencies (this may take a minute)..." -ForegroundColor Green
pip install -q -r requirements.txt
Write-Host "  Dependencies installed successfully" -ForegroundColor Gray

# Step 5: Setup environment file
Write-Host ""
Write-Host "✓ Setting up environment configuration..." -ForegroundColor Green
if (-not (Test-Path ".env")) {
    @"
GROQ_API_KEY=your_groq_api_key_here
REMOTEOK_KEYWORDS=python,fastapi,senior
REMOTEOK_LIMIT=50
"@ | Out-File -FilePath .env -Encoding UTF8
    Write-Host "  📝 Created .env file - please add your GROQ_API_KEY" -ForegroundColor Yellow
} else {
    Write-Host "  ℹ️  .env file already exists" -ForegroundColor Gray
}

# Step 6: Initialize database
Write-Host ""
Write-Host "✓ Initializing database..." -ForegroundColor Green
python -c "
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
print('  Database tables created')
"

# Step 7: Start the application
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    🎉 Starting Application                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Dashboard:     http://localhost:8001/app" -ForegroundColor Yellow
Write-Host "📖 API Docs:      http://localhost:8001/docs" -ForegroundColor Yellow
Write-Host "🏥 Health Check:  http://localhost:8001/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
