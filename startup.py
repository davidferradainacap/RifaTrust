"""
Startup script for Azure App Service
Configures Python path for backend structure
"""
import os
import sys

# Add backend directory to Python path at the very beginning
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

print(f"[STARTUP] Python path configured: {backend_path}", flush=True)
print(f"[STARTUP] sys.path: {sys.path[:3]}", flush=True)

# Create media directories in Azure's persistent storage
if os.environ.get('WEBSITE_HOSTNAME'):
    media_dirs = ['/home/media', '/home/media/avatars', '/home/media/raffles', '/home/media/prizes', '/home/media/documents']
    for dir_path in media_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"[STARTUP] Created media directory: {dir_path}", flush=True)
        else:
            print(f"[STARTUP] Media directory exists: {dir_path}", flush=True)

# Configure PyMySQL before Django loads
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("[STARTUP] PyMySQL configured as MySQLdb", flush=True)
except ImportError as e:
    print(f"[STARTUP] Warning: PyMySQL not available: {e}", flush=True)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
print(f"[STARTUP] DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}", flush=True)

# Import WSGI application
try:
    from config.wsgi import application
    print("[STARTUP] WSGI application loaded successfully", flush=True)
except Exception as e:
    print(f"[STARTUP] ERROR loading WSGI application: {e}", flush=True)
    import traceback
    traceback.print_exc()
    raise

# This is what gunicorn will use
app = application
print("[STARTUP] Startup complete, ready to serve requests", flush=True)
