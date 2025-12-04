#!/bin/bash
set -e  # Exit on error

echo "========================================="
echo "🚀 Starting RifaTrust Azure Deployment"
echo "========================================="
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Configure Python path for backend structure
export PYTHONPATH="/home/site/wwwroot/backend:${PYTHONPATH}"
echo "✅ PYTHONPATH configured: $PYTHONPATH"

# Upgrade pip first
echo ""
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt --no-cache-dir

# Check Django installation
echo ""
echo "🔍 Checking Django installation..."
python -c "import django; print(f'Django version: {django.get_version()}')"

# Run migrations (with error handling)
echo ""
echo "🗄️ Running database migrations..."
if python manage.py migrate --noinput; then
    echo "✅ Migrations completed successfully"
else
    echo "⚠️ Warning: Migrations failed, but continuing..."
fi

# Collect static files
echo ""
echo "📁 Collecting static files..."
if python manage.py collectstatic --noinput; then
    echo "✅ Static files collected successfully"
else
    echo "⚠️ Warning: Static files collection failed, but continuing..."
fi

# Verify backend structure
echo ""
echo "🔍 Verifying backend structure..."
ls -la backend/

echo ""
echo "========================================="
echo "✅ Deployment completed successfully"
echo "========================================="
