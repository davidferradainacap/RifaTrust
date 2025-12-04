"""
Alternative WSGI configuration for Azure when backend structure fails
This version tries to work around path issues
"""
import os
import sys

# Print debug info
print("="*60, flush=True)
print("WSGI INITIALIZATION DEBUG", flush=True)
print("="*60, flush=True)
print(f"Current working directory: {os.getcwd()}", flush=True)
print(f"Script location: {__file__}", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Python path (first 5): {sys.path[:5]}", flush=True)

# Try multiple path configurations
root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, 'backend')

print(f"\nRoot directory: {root_dir}", flush=True)
print(f"Backend directory: {backend_dir}", flush=True)
print(f"Backend exists: {os.path.exists(backend_dir)}", flush=True)

# Add backend to path
if os.path.exists(backend_dir):
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
        print(f"✅ Added backend to path", flush=True)
else:
    print(f"⚠️ Backend directory not found!", flush=True)

# Configure PyMySQL
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("✅ PyMySQL configured", flush=True)
except ImportError as e:
    print(f"⚠️ PyMySQL import failed: {e}", flush=True)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
print(f"✅ DJANGO_SETTINGS_MODULE set to: {os.environ.get('DJANGO_SETTINGS_MODULE')}", flush=True)

# Try to import Django and show what's available
try:
    import django
    print(f"✅ Django imported, version: {django.get_version()}", flush=True)
except ImportError as e:
    print(f"❌ Django import failed: {e}", flush=True)
    print("Available in sys.modules:", list(sys.modules.keys())[:20], flush=True)

# List what's in backend directory
if os.path.exists(backend_dir):
    print(f"\nContents of backend/:", flush=True)
    for item in os.listdir(backend_dir):
        item_path = os.path.join(backend_dir, item)
        if os.path.isdir(item_path):
            print(f"  📁 {item}/", flush=True)
        else:
            print(f"  📄 {item}", flush=True)

# Try to import config module
try:
    import config
    print(f"✅ Config module found at: {config.__file__}", flush=True)
    print(f"   Config module contents: {dir(config)}", flush=True)
except ImportError as e:
    print(f"❌ Config module import failed: {e}", flush=True)
    print(f"   sys.path: {sys.path}", flush=True)

# Finally, try to import the WSGI app
print("\nAttempting to load WSGI application...", flush=True)
try:
    from config.wsgi import application
    print("✅ WSGI application loaded successfully!", flush=True)
    app = application
    print("✅ App exported for gunicorn", flush=True)
except Exception as e:
    print(f"❌ FAILED to load WSGI application: {e}", flush=True)
    import traceback
    print("Full traceback:", flush=True)
    traceback.print_exc()
    print("="*60, flush=True)
    raise

print("="*60, flush=True)
print("WSGI INITIALIZATION COMPLETE", flush=True)
print("="*60, flush=True)
