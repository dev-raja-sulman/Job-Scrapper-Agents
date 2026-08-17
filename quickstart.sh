#!/bin/bash
# Job Scrapper Agent - Quick Start Script
# This script sets up and runs the complete job scraper application

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        🚀 Agentic AI Job Scraper - Quick Start                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check Python
echo "✓ Checking Python installation..."
python3 --version || python --version

# Step 2: Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
python3 -m venv venv 2>/dev/null || python -m venv venv
source venv/bin/activate 2>/dev/null || venv\Scripts\activate

# Step 3: Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install -q -r requirements.txt

# Step 4: Setup environment file
echo ""
echo "✓ Setting up environment configuration..."
if [ ! -f .env ]; then
    echo "GROQ_API_KEY=your_groq_api_key_here" > .env
    echo "REMOTEOK_KEYWORDS=python,fastapi,senior" >> .env
    echo "REMOTEOK_LIMIT=50" >> .env
    echo "  📝 Created .env file - please add your GROQ_API_KEY"
else
    echo "  ℹ️  .env file already exists"
fi

# Step 5: Initialize database
echo ""
echo "✓ Initializing database..."
python -c "
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
print('  ✓ Database tables created')
"

# Step 6: Start the application
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 Starting Application                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Dashboard:     http://localhost:8001/app"
echo "📖 API Docs:      http://localhost:8001/docs"
echo "🏥 Health Check:  http://localhost:8001/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
