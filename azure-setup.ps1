# Configuración Rápida para Azure App Service - PowerShell
# Ejecutar en PowerShell con Azure CLI instalado

# Variables - MODIFICAR SEGÚN TU CONFIGURACIÓN
$RESOURCE_GROUP = "RifaTrust-RG"
$APP_NAME = "rifatrust-dhche4cabncab9d8"
$LOCATION = "brazilsouth"
$PLAN_NAME = "RifaTrust-Plan"

Write-Host "🚀 Iniciando configuración de Azure..." -ForegroundColor Cyan

# 1. Login (si no estás autenticado)
Write-Host "`n1. Verificando autenticación..." -ForegroundColor Yellow
az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Iniciando sesión en Azure..." -ForegroundColor Yellow
    az login
}

# 2. Crear Resource Group
Write-Host "`n2. Creando Resource Group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION

# 3. Crear App Service Plan
Write-Host "`n3. Creando App Service Plan..." -ForegroundColor Yellow
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku B1 --is-linux

# 4. Crear Web App
Write-Host "`n4. Creando Web App..." -ForegroundColor Yellow
az webapp create --resource-group $RESOURCE_GROUP --plan $PLAN_NAME --name $APP_NAME --runtime "PYTHON:3.11"

# 5. Configurar variables de entorno
Write-Host "`n5. Configurando variables de entorno..." -ForegroundColor Yellow
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings `
    DEBUG="False" `
    SECRET_KEY="CAMBIAR-POR-CLAVE-SEGURA-GENERADA" `
    ALLOWED_HOSTS="$APP_NAME.azurewebsites.net" `
    DATABASE_ENGINE="django.db.backends.sqlite3" `
    DATABASE_NAME="/home/site/wwwroot/db.sqlite3" `
    EMAIL_BACKEND="apps.core.email_backend.SendGridEmailBackend" `
    EMAIL_HOST="smtp.sendgrid.net" `
    EMAIL_PORT="587" `
    EMAIL_USE_TLS="True" `
    EMAIL_HOST_USER="apikey" `
    EMAIL_HOST_PASSWORD="YOUR_SENDGRID_API_KEY" `
    DEFAULT_FROM_EMAIL="david.ferrada@inacapmail.cl" `
    SITE_DOMAIN="$APP_NAME.azurewebsites.net" `
    SITE_URL="https://$APP_NAME.azurewebsites.net" `
    CSRF_TRUSTED_ORIGINS="https://$APP_NAME.azurewebsites.net"

# 6. Configurar startup command
Write-Host "`n6. Configurando comando de inicio..." -ForegroundColor Yellow
az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 --chdir backend config.wsgi"

# 7. Habilitar logs
Write-Host "`n7. Habilitando logs..." -ForegroundColor Yellow
az webapp log config --resource-group $RESOURCE_GROUP --name $APP_NAME --docker-container-logging filesystem

Write-Host "`n✅ Configuración completada" -ForegroundColor Green
Write-Host "🌐 URL: https://$APP_NAME.azurewebsites.net" -ForegroundColor Cyan
Write-Host "`nPróximos pasos:" -ForegroundColor Yellow
Write-Host "1. Configurar despliegue desde GitHub en Azure Portal" -ForegroundColor White
Write-Host "2. Generar un SECRET_KEY seguro y actualizar en Azure" -ForegroundColor White
Write-Host "3. Ver logs: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME" -ForegroundColor White
