"""
Startup script for Azure App Service
Configures Python path for backend structure
"""
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).resolve().parent / 'backend'
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Configure PyMySQL
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import WSGI application
from config.wsgi import application

# This is what gunicorn will use
app = application
