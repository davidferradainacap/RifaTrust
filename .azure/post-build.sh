#!/bin/bash
# Post-build script para Azure App Service
# Este script se ejecuta automáticamente después del build de Oryx

echo "======================================"
echo "RifaTrust Post-Build Configuration"
echo "======================================"

# Verificar que estamos en el directorio correcto
if [ ! -d "/home/site/wwwroot/backend" ]; then
    echo "ERROR: No se encuentra el directorio backend"
    exit 1
fi

echo "✓ Estructura de directorios verificada"

# Asegurarse de que el archivo gunicorn.conf.py tiene permisos correctos
if [ -f "/home/site/wwwroot/gunicorn.conf.py" ]; then
    chmod 644 /home/site/wwwroot/gunicorn.conf.py
    echo "✓ Permisos de gunicorn.conf.py configurados"
else
    echo "⚠ ADVERTENCIA: gunicorn.conf.py no encontrado"
fi

# Verificar que el archivo wsgi.py existe
if [ -f "/home/site/wwwroot/backend/config/wsgi.py" ]; then
    echo "✓ Archivo WSGI encontrado"
else
    echo "ERROR: wsgi.py no encontrado en backend/config/"
    exit 1
fi

# Crear el archivo de comando de inicio si no existe
STARTUP_FILE="/home/site/wwwroot/startup_command.sh"
cat > "$STARTUP_FILE" << 'EOF'
#!/bin/bash
cd /home/site/wwwroot
exec gunicorn --config gunicorn.conf.py --chdir /home/site/wwwroot config.wsgi:application
EOF

chmod +x "$STARTUP_FILE"
echo "✓ Script de inicio creado en $STARTUP_FILE"

echo "======================================"
echo "Post-Build completado exitosamente"
echo "======================================"
