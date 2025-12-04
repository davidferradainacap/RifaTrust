#!/bin/bash
# Custom deployment script for Azure App Service

# Exit on error
set -e

echo "=== Custom Deployment Script Start ==="

# 1. Navigate to deployment source
cd "$DEPLOYMENT_SOURCE"

# 2. Install Python dependencies
echo "Installing Python packages..."
python -m pip install --upgrade pip
pip install -r requirements.txt --target="./.python_packages/lib/site-packages"

# 3. Collect static files
echo "Collecting static files..."
export PYTHONPATH="$DEPLOYMENT_SOURCE/backend:$PYTHONPATH"
python -c "import sys; sys.path.insert(0, 'backend'); import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); import django; django.setup(); from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])" || echo "Collectstatic failed, continuing..."

echo "=== Custom Deployment Script Complete ==="
