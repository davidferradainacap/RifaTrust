"""
Gunicorn configuration file for Azure App Service
"""
import os
import sys

# Get the base directory (should be /home/site/wwwroot in Azure)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

# Change to base directory
os.chdir(BASE_DIR)

# Add backend directory to Python path so we can import config.wsgi
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Also add base directory to path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 600
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'rifatrust'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (not used, but keeping for reference)
keyfile = None
certfile = None
