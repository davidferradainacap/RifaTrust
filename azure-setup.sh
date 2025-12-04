# Configuración Rápida para Azure App Service
# Ejecutar estos comandos en el Azure Cloud Shell o Azure CLI

# Variables (MODIFICAR SEGÚN TU CONFIGURACIÓN)
RESOURCE_GROUP="RifaTrust-RG"
APP_NAME="rifatrust-dhche4cabncab9d8"
LOCATION="brazilsouth"
PLAN_NAME="RifaTrust-Plan"

# 1. Crear Resource Group (si no existe)
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Crear App Service Plan (si no existe)
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku B1 --is-linux

# 3. Crear Web App
az webapp create --resource-group $RESOURCE_GROUP --plan $PLAN_NAME --name $APP_NAME --runtime "PYTHON:3.11"

# 4. Configurar variables de entorno críticas
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings \
    DEBUG=False \
    SECRET_KEY="CAMBIAR-POR-CLAVE-SEGURA" \
    ALLOWED_HOSTS="$APP_NAME.azurewebsites.net" \
    DATABASE_ENGINE="django.db.backends.sqlite3" \
    DATABASE_NAME="/home/site/wwwroot/db.sqlite3" \
    EMAIL_BACKEND="apps.core.email_backend.SendGridEmailBackend" \
    EMAIL_HOST="smtp.sendgrid.net" \
    EMAIL_PORT="587" \
    EMAIL_USE_TLS="True" \
    EMAIL_HOST_USER="apikey" \
    EMAIL_HOST_PASSWORD="YOUR_SENDGRID_API_KEY" \
    DEFAULT_FROM_EMAIL="david.ferrada@inacapmail.cl" \
    SITE_DOMAIN="$APP_NAME.azurewebsites.net" \
    SITE_URL="https://$APP_NAME.azurewebsites.net" \
    CSRF_TRUSTED_ORIGINS="https://$APP_NAME.azurewebsites.net"

# 5. Configurar startup command
az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 --chdir backend config.wsgi"

# 6. Configurar despliegue desde GitHub
# NOTA: Esto requiere autenticación con GitHub - mejor hacerlo desde Azure Portal

# 7. Habilitar logs
az webapp log config --resource-group $RESOURCE_GROUP --name $APP_NAME --docker-container-logging filesystem

# 8. Ver logs en tiempo real
echo "Para ver logs ejecutar: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"

echo "✅ Configuración completada"
echo "🌐 URL: https://$APP_NAME.azurewebsites.net"
