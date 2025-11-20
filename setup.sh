#!/bin/bash

# NBA Fantasy Backend - Setup Script
# This script automates the initial setup process

echo "🏀 NBA Fantasy Game - Backend Setup"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. You can edit it if needed."
else
    echo "ℹ️  .env file already exists."
fi

# Remove old database if exists
if [ -f db.sqlite3 ]; then
    echo ""
    echo "⚠️  Existing database found."
    echo "🗑️  Removing old database..."
    rm db.sqlite3
    echo "✅ Old database removed."
fi

# Run migrations
echo ""
echo "🗄️  Running database migrations..."
python manage.py migrate

# Load fixtures
echo "👥 Loading player fixtures (25 NBA players)..."
python manage.py loaddata players

# Check if fixtures loaded successfully
if [ $? -eq 0 ]; then
    echo "✅ Fixtures loaded successfully!"
else
    echo "⚠️  Warning: Fixtures may not have loaded correctly."
fi

# Create superuser prompt
echo ""
echo "👤 Would you like to create a superuser for Django Admin? (y/n)"
read -r create_superuser

if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
fi

echo ""
echo "=" * 50
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the development server, run:"
echo "   python manage.py runserver 8000"
echo ""
echo "📚 Documentation:"
echo "   Swagger UI: http://localhost:8000/swagger/"
echo "   Admin Panel: http://localhost:8000/admin/"
echo "   API Docs: http://localhost:8000/redoc/"
echo ""
echo "📖 Quick Start Guide: QUICKSTART.md"
echo "🔧 Troubleshooting: TROUBLESHOOTING.md"
echo ""
echo "Happy coding! 🏀"
