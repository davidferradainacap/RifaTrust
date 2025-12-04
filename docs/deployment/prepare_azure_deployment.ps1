# ============================================================
# SCRIPT DE PREPARACIÓN PARA AZURE DEPLOYMENT
# ============================================================
# Genera nuevo SECRET_KEY y prepara configuración para Azure
# ============================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PREPARACIÓN PARA AZURE DEPLOYMENT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual
Write-Host "1. Activando entorno virtual..." -ForegroundColor Yellow
& "C:\Users\Administrator\Desktop\RS_project\.venv\Scripts\Activate.ps1"

# Generar nuevo SECRET_KEY
Write-Host ""
Write-Host "2. Generando nuevo SECRET_KEY seguro..." -ForegroundColor Yellow
$pythonCode = "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$secretKey = & python -c $pythonCode
Write-Host "   ✓ SECRET_KEY generado" -ForegroundColor Green

# Crear archivo .env.azure con configuración de producción
Write-Host ""
Write-Host "3. Creando archivo .env.azure..." -ForegroundColor Yellow

$azureEnv = @"
# ============================================================
# VARIABLES DE ENTORNO PARA AZURE APP SERVICE
# ============================================================
# Generado: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
#
# INSTRUCCIONES:
# 1. Copiar estas variables a: Azure Portal → App Service → Configuration
# 2. Pegar una por una en "Application settings"
# 3. Guardar cambios y reiniciar la aplicación
# ============================================================

# ================================
# DJANGO CORE
# ================================
DEBUG=False
SECRET_KEY=$secretKey
ALLOWED_HOSTS=rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net
WEBSITE_HTTPLOGGING_RETENTION_DAYS=7

# ================================
# DATABASE - SQLite (Temporal)
# ⚠️ CAMBIAR A MYSQL EN PRODUCCIÓN
# ================================
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=/home/site/wwwroot/db.sqlite3

# ================================
# DATABASE - MySQL (Producción)
# Descomentar estas líneas cuando MySQL esté configurado
# ================================
# DATABASE_ENGINE=django.db.backends.mysql
# DATABASE_NAME=rifatrust_db
# DATABASE_USER=adminuser@rifatrust-mysql
# DATABASE_PASSWORD=TU_PASSWORD_MYSQL_AQUI
# DATABASE_HOST=rifatrust-mysql.mysql.database.azure.com
# DATABASE_PORT=3306

# ================================
# SENDGRID EMAIL CONFIGURATION
# ⚠️ VERIFICAR QUE LA API KEY NO HAYA EXPIRADO
# ================================
EMAIL_BACKEND=apps.core.email_backend.SendGridEmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=YOUR_SENDGRID_API_KEY
EMAIL_TIMEOUT=30
DEFAULT_FROM_EMAIL=david.ferrada@inacapmail.cl

# ================================
# SITE CONFIGURATION
# ================================
SITE_DOMAIN=rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net
SITE_URL=https://rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net

# ================================
# CSRF PROTECTION
# ================================
CSRF_TRUSTED_ORIGINS=https://rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net

# ================================
# STRIPE PAYMENT (Opcional)
# ⚠️ USAR KEYS DE PRODUCCIÓN, NO TEST
# ================================
STRIPE_PUBLIC_KEY=pk_live_TU_PUBLIC_KEY_AQUI
STRIPE_SECRET_KEY=sk_live_TU_SECRET_KEY_AQUI

# ================================
# EMAIL VERIFICATION API (Opcional)
# ================================
EMAIL_VERIFICATION_API_KEY=TU_ABSTRACTAPI_KEY_AQUI

# ================================
# ENCRYPTION (Usar diferente a SECRET_KEY)
# ================================
ENCRYPTION_KEY=$secretKey

"@

# Guardar archivo
$azureEnv | Out-File -FilePath ".env.azure" -Encoding UTF8
Write-Host "   ✓ Archivo .env.azure creado" -ForegroundColor Green

# Verificar checks de Django
Write-Host ""
Write-Host "4. Verificando configuración de Django..." -ForegroundColor Yellow
python manage.py check
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ No se encontraron errores" -ForegroundColor Green
}
else {
    Write-Host "   ⚠ Hay warnings (normales en desarrollo)" -ForegroundColor Yellow
}

# Verificar archivos estáticos
Write-Host ""
Write-Host "5. Verificando archivos estáticos..." -ForegroundColor Yellow
if (Test-Path "staticfiles") {
    $staticCount = (Get-ChildItem -Path "staticfiles" -Recurse -File | Measure-Object).Count
    Write-Host "   ✓ $staticCount archivos estáticos listos" -ForegroundColor Green
}
else {
    Write-Host "   ⚠ Ejecutar: python manage.py collectstatic" -ForegroundColor Yellow
}

# Verificar requirements.txt
Write-Host ""
Write-Host "6. Verificando dependencias..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    $depCount = (Get-Content "requirements.txt" | Where-Object { $_ -match '\S' }).Count
    Write-Host "   ✓ $depCount dependencias listadas" -ForegroundColor Green
}
else {
    Write-Host "   ✗ requirements.txt no encontrado" -ForegroundColor Red
}

# Verificar archivos críticos
Write-Host ""
Write-Host "7. Verificando archivos de deployment..." -ForegroundColor Yellow
$criticalFiles = @(
    ".deployment",
    "runtime.txt",
    "startup.txt",
    "requirements.txt",
    "AZURE_DEPLOYMENT_GUIDE.md"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    }
    else {
        Write-Host "   ✗ $file FALTA" -ForegroundColor Red
    }
}

# Resumen final
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMEN DE PREPARACIÓN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ SECRET_KEY generado:" -ForegroundColor Green
Write-Host "   $secretKey" -ForegroundColor White
Write-Host ""
Write-Host "✅ Archivo .env.azure creado con todas las variables" -ForegroundColor Green
Write-Host ""
Write-Host "📋 PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host "   1. Abrir .env.azure y revisar todas las variables" -ForegroundColor White
Write-Host "   2. Verificar/actualizar SendGrid API key si es necesario" -ForegroundColor White
Write-Host "   3. Ir a Azure Portal → App Service → Configuration" -ForegroundColor White
Write-Host "   4. Copiar cada variable de .env.azure a Application Settings" -ForegroundColor White
Write-Host "   5. Seguir guía completa en: AZURE_DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "   - NO commitear .env.azure a Git (contiene secretos)" -ForegroundColor White
Write-Host "   - Guardar .env.azure en lugar seguro como respaldo" -ForegroundColor White
Write-Host "   - Cambiar Stripe keys a producción antes de deploy" -ForegroundColor White
Write-Host ""
Write-Host "🚀 TODO LISTO PARA DEPLOYMENT!" -ForegroundColor Green
Write-Host ""

# Preguntar si desea abrir la guía
$openGuide = Read-Host "¿Deseas abrir la guía de deployment ahora? (S/N)"
if ($openGuide -eq "S" -or $openGuide -eq "s") {
    Start-Process "AZURE_DEPLOYMENT_GUIDE.md"
}

Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
