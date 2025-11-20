# NBA Fantasy Backend - Setup Script (PowerShell)
# This script automates the initial setup process for Windows

Write-Host "🏀 NBA Fantasy Game - Backend Setup" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-Not (Test-Path .env)) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env file created. You can edit it if needed." -ForegroundColor Green
} else {
    Write-Host "ℹ️  .env file already exists." -ForegroundColor Cyan
}

# Remove old database if exists
if (Test-Path db.sqlite3) {
    Write-Host ""
    Write-Host "⚠️  Existing database found." -ForegroundColor Yellow
    Write-Host "🗑️  Removing old database..." -ForegroundColor Yellow
    Remove-Item db.sqlite3 -Force
    Write-Host "✅ Old database removed." -ForegroundColor Green
}

# Run migrations
Write-Host ""
Write-Host "🗄️  Running database migrations..." -ForegroundColor Yellow
python manage.py migrate

# Load fixtures
Write-Host "👥 Loading player fixtures (25 NBA players)..." -ForegroundColor Yellow
python manage.py loaddata players

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Fixtures loaded successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: Fixtures may not have loaded correctly." -ForegroundColor Yellow
}

# Create superuser prompt
Write-Host ""
$createSuperuser = Read-Host "👤 Would you like to create a superuser for Django Admin? (y/n)"

if ($createSuperuser -eq "y" -or $createSuperuser -eq "Y") {
    python manage.py createsuperuser
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 To start the development server, run:" -ForegroundColor Cyan
Write-Host "   python manage.py runserver 8000" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   Swagger UI: http://localhost:8000/swagger/" -ForegroundColor White
Write-Host "   Admin Panel: http://localhost:8000/admin/" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/redoc/" -ForegroundColor White
Write-Host ""
Write-Host "📖 Quick Start Guide: QUICKSTART.md" -ForegroundColor Cyan
Write-Host "🔧 Troubleshooting: TROUBLESHOOTING.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Happy coding! 🏀" -ForegroundColor Green
