#!/bin/bash

# Script de despliegue para Azure App Service
# Este script se ejecuta automáticamente durante el despliegue

echo "==================================="
echo "🚀 Iniciando despliegue en Azure"
echo "==================================="

# Agregar backend al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot/backend"
echo "✅ PYTHONPATH configurado"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt --upgrade

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "==================================="
echo "✅ Despliegue completado"
echo "==================================="
