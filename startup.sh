#!/bin/bash

# Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate --noinput

# Colectar archivos estáticos
python manage.py collectstatic --noinput

# Iniciar Gunicorn
gunicorn config.wsgi:application --bind=0.0.0.0:8000 --timeout 600 --workers 4
