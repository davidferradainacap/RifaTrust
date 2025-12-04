#!/bin/bash
# Azure App Service startup script

echo "=== RifaTrust Startup ==="
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Contents of wwwroot:"
ls -la /home/site/wwwroot/ || ls -la .

# Activate virtual environment if exists
if [ -d "antenv" ]; then
    echo "Activating virtual environment..."
    source antenv/bin/activate
fi

# Set Python path
export PYTHONPATH="/home/site/wwwroot/backend:$PYTHONPATH"
echo "PYTHONPATH set to: $PYTHONPATH"

# Set Django settings
export DJANGO_SETTINGS_MODULE="config.settings"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn --bind=0.0.0.0:${PORT:-8000} \
    --timeout 600 \
    --workers 2 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --chdir /home/site/wwwroot \
    startup:app
