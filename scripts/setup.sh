#!/usr/bin/env bash
set -e

echo "====================================================================="
echo "  Karnataka Politician Tracking System — One-Command Setup Script    "
echo "====================================================================="

# 1. Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed."
    exit 1
fi

# 2. Check Node version
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not installed."
    exit 1
fi

echo "✓ Python & Node.js environment detected."

# 3. Copy example env files if missing
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

if [ ! -f frontend/.env.local ]; then
    echo "Creating frontend/.env.local from frontend/.env.example..."
    cp frontend/.env.example frontend/.env.local
fi

# 4. Setup Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Installing backend dependencies..."
source venv/bin/activate
pip install -r politicians_tracker/requirements.txt --quiet

# 5. Apply migrations & seed database
echo "Applying database migrations and seeding public data..."
USE_SQLITE=true DJANGO_SECRET_KEY=dev_secret_key python politicians_tracker/manage.py migrate

# 6. Setup Frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm ci --quiet
cd ..

echo "====================================================================="
echo "✓ SETUP COMPLETE!"
echo ""
echo "To start the application:"
echo "  Backend : USE_SQLITE=true python politicians_tracker/manage.py runserver 0.0.0.0:8000"
echo "  Frontend: cd frontend && npm run dev"
echo "====================================================================="
