# 🎯 COMANDOS ESENCIALES PARA AZURE DEPLOYMENT

## ⚡ QUICK START (5 minutos)

### 1️⃣ Variables de Entorno Preparadas
```
✅ Archivo creado: .env.azure
✅ SECRET_KEY: qzx1h(l^*yi-z^gx&tpv^fr^gc%)@-9zu98!25v1l6v!of@-y0
✅ Listo para copiar a Azure Portal
```

### 2️⃣ Azure Portal
```
1. https://portal.azure.com
2. Create Resource → Web App
3. Name: rifatrust-app
4. Runtime: Python 3.11
5. Region: Brazil South
6. Plan: B1 Basic ($13/mes)
7. Create (esperar 2 min)
```

### 3️⃣ Configurar Variables
```
Azure Portal → rifatrust-app → Configuration → Application settings

Copiar TODO de .env.azure:
- DEBUG=False
- SECRET_KEY=qzx1h(l^*yi-z^gx&tpv^fr^gc%)@-9zu98!25v1l6v!of@-y0
- ALLOWED_HOSTS=rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net
- [... todas las demás variables ...]

Save → Restart
```

### 4️⃣ Conectar GitHub
```
Azure Portal → rifatrust-app → Deployment Center

Source: GitHub
Authorize GitHub
Organization: davidferradainacap
Repository: RifaTrust
Branch: main

Save (Azure configurará CI/CD automático)
```

### 5️⃣ Post-Deployment
```bash
# SSH a la aplicación
Azure Portal → rifatrust-app → SSH → Go

# Ejecutar migraciones
cd /home/site/wwwroot
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Verificar logs
tail -f /home/LogFiles/django.log
```

---

## 📋 VARIABLES DE ENTORNO (Copiar a Azure)

```env
DEBUG=False
SECRET_KEY=qzx1h(l^*yi-z^gx&tpv^fr^gc%)@-9zu98!25v1l6v!of@-y0
ALLOWED_HOSTS=rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net
WEBSITE_HTTPLOGGING_RETENTION_DAYS=7

DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=/home/site/wwwroot/db.sqlite3

EMAIL_BACKEND=apps.core.email_backend.SendGridEmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=YOUR_SENDGRID_API_KEY
EMAIL_TIMEOUT=30
DEFAULT_FROM_EMAIL=david.ferrada@inacapmail.cl

SITE_DOMAIN=rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net
SITE_URL=https://rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net

CSRF_TRUSTED_ORIGINS=https://rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net

STRIPE_PUBLIC_KEY=pk_live_TU_KEY_AQUI
STRIPE_SECRET_KEY=sk_live_TU_KEY_AQUI

ENCRYPTION_KEY=qzx1h(l^*yi-z^gx&tpv^fr^gc%)@-9zu98!25v1l6v!of@-y0
```

---

## 🔧 AZURE CLI (Opcional - Método Alternativo)

### Instalación Azure CLI
```bash
# Windows
winget install Microsoft.AzureCLI

# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Deployment Completo
```bash
# 1. Login
az login

# 2. Crear Resource Group
az group create --name RifaTrust-RG --location brazilsouth

# 3. Crear App Service Plan
az appservice plan create \
  --name RifaTrust-Plan \
  --resource-group RifaTrust-RG \
  --sku B1 \
  --is-linux

# 4. Crear Web App
az webapp create \
  --resource-group RifaTrust-RG \
  --plan RifaTrust-Plan \
  --name rifatrust-app \
  --runtime "PYTHON:3.11"

# 5. Configurar variables de entorno (una por línea)
az webapp config appsettings set \
  --resource-group RifaTrust-RG \
  --name rifatrust-app \
  --settings \
    DEBUG=False \
    SECRET_KEY='qzx1h(l^*yi-z^gx&tpv^fr^gc%)@-9zu98!25v1l6v!of@-y0' \
    ALLOWED_HOSTS='rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net'

# 6. Configurar deployment desde GitHub
az webapp deployment source config \
  --resource-group RifaTrust-RG \
  --name rifatrust-app \
  --repo-url https://github.com/davidferradainacap/RifaTrust \
  --branch main \
  --manual-integration

# 7. Ver logs
az webapp log tail \
  --resource-group RifaTrust-RG \
  --name rifatrust-app

# 8. SSH a la app
az webapp ssh \
  --resource-group RifaTrust-RG \
  --name rifatrust-app
```

---

## 🗄️ MYSQL EN AZURE (Recomendado para Producción)

### Crear MySQL Server
```bash
# 1. Crear servidor
az mysql server create \
  --resource-group RifaTrust-RG \
  --name rifatrust-mysql \
  --location brazilsouth \
  --admin-user adminuser \
  --admin-password 'TuPasswordSeguro123!' \
  --sku-name B_Gen5_1 \
  --version 8.0 \
  --ssl-enforcement Enabled

# 2. Configurar firewall
az mysql server firewall-rule create \
  --resource-group RifaTrust-RG \
  --server rifatrust-mysql \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# 3. Crear base de datos
az mysql db create \
  --resource-group RifaTrust-RG \
  --server-name rifatrust-mysql \
  --name rifatrust_db

# 4. Actualizar variables en Web App
az webapp config appsettings set \
  --resource-group RifaTrust-RG \
  --name rifatrust-app \
  --settings \
    DATABASE_ENGINE='django.db.backends.mysql' \
    DATABASE_NAME='rifatrust_db' \
    DATABASE_USER='adminuser@rifatrust-mysql' \
    DATABASE_PASSWORD='TuPasswordSeguro123!' \
    DATABASE_HOST='rifatrust-mysql.mysql.database.azure.com' \
    DATABASE_PORT='3306'
```

---

## 📊 MONITOREO

### Ver Logs en Tiempo Real
```bash
az webapp log tail \
  --resource-group RifaTrust-RG \
  --name rifatrust-app
```

### Descargar Logs
```bash
az webapp log download \
  --resource-group RifaTrust-RG \
  --name rifatrust-app \
  --log-file logs_azure.zip
```

### Ver Estado
```bash
az webapp show \
  --resource-group RifaTrust-RG \
  --name rifatrust-app \
  --query "{Name:name, State:state, URL:defaultHostName}"
```

### Ver Métricas
```bash
az monitor metrics list \
  --resource /subscriptions/{subscription-id}/resourceGroups/RifaTrust-RG/providers/Microsoft.Web/sites/rifatrust-app \
  --metric CpuTime RequestsInApplicationQueue Http2xx Http4xx Http5xx
```

---

## 🔄 OPERACIONES COMUNES

### Reiniciar Aplicación
```bash
az webapp restart \
  --resource-group RifaTrust-RG \
  --name rifatrust-app
```

### Detener Aplicación
```bash
az webapp stop \
  --resource-group RifaTrust-RG \
  --name rifatrust-app
```

### Iniciar Aplicación
```bash
az webapp start \
  --resource-group RifaTrust-RG \
  --name rifatrust-app
```

### Escalar Verticalmente
```bash
# Cambiar a B2 (2 cores, 3.5GB RAM)
az appservice plan update \
  --name RifaTrust-Plan \
  --resource-group RifaTrust-RG \
  --sku B2
```

### Escalar Horizontalmente
```bash
# Aumentar a 2 instancias
az appservice plan update \
  --name RifaTrust-Plan \
  --resource-group RifaTrust-RG \
  --number-of-workers 2
```

---

## 🧪 VERIFICACIÓN POST-DEPLOYMENT

### Checklist
```bash
# 1. Home page
curl -I https://rifatrust-app.azurewebsites.net
# Esperado: HTTP 200 OK

# 2. Admin panel
curl -I https://rifatrust-app.azurewebsites.net/admin/
# Esperado: HTTP 200 OK

# 3. API
curl https://rifatrust-app.azurewebsites.net/api/
# Esperado: JSON response

# 4. Static files
curl -I https://rifatrust-app.azurewebsites.net/static/css/styles.css
# Esperado: HTTP 200 OK
```

### Tests Funcionales
```
✅ Registro de usuario → /register/
✅ Login → /login/
✅ Panel admin → /admin/
✅ Crear rifa → /raffles/create/
✅ Comprar boletos → /raffles/
✅ Email de confirmación enviado
```

---

## 🚨 TROUBLESHOOTING

### Ver Logs de Error
```bash
# Logs de aplicación
az webapp log tail --name rifatrust-app --resource-group RifaTrust-RG

# Logs HTTP
az webapp log tail --name rifatrust-app --resource-group RifaTrust-RG --provider http

# Logs de deployment
az webapp log deployment show --name rifatrust-app --resource-group RifaTrust-RG
```

### Error 502 Bad Gateway
```bash
# Verificar startup command
az webapp config show \
  --resource-group RifaTrust-RG \
  --name rifatrust-app \
  --query "appCommandLine"

# Debería ser:
# gunicorn --bind=0.0.0.0 --timeout 600 --chdir backend config.wsgi
```

### Static Files No Cargan
```bash
# SSH y verificar
az webapp ssh --name rifatrust-app --resource-group RifaTrust-RG

cd /home/site/wwwroot
ls -la staticfiles/
python manage.py collectstatic --noinput
```

### Database Connection Error
```bash
# Verificar variables
az webapp config appsettings list \
  --resource-group RifaTrust-RG \
  --name rifatrust-app \
  --query "[?name=='DATABASE_ENGINE']"
```

---

## 💰 COSTOS ESTIMADOS

### Plan B1 (Básico)
```
Recursos:
- 1 vCPU
- 1.75 GB RAM
- 10 GB Storage

Precio: ~$13 USD/mes
Ideal para: Desarrollo, staging, apps pequeñas
```

### Plan B2 (Intermedio)
```
Recursos:
- 2 vCPU
- 3.5 GB RAM
- 10 GB Storage

Precio: ~$26 USD/mes
Ideal para: Apps medianas, ~1000 usuarios activos
```

### Plan S1 (Producción)
```
Recursos:
- 1 vCPU
- 1.75 GB RAM
- 50 GB Storage
- Auto-scaling
- Custom domains ilimitados

Precio: ~$70 USD/mes
Ideal para: Producción seria, ~5000 usuarios activos
```

### MySQL Básico
```
Recursos:
- 1 vCore
- 2 GB RAM
- 5 GB Storage

Precio: ~$26 USD/mes
Incluye: Backups automáticos, SSL, alta disponibilidad
```

**Total estimado inicial: $39-$45 USD/mes (B1 + MySQL)**

---

## 📚 RECURSOS ÚTILES

### Documentación
- 📘 AZURE_DEPLOYMENT_GUIDE.md - Guía completa paso a paso
- 📋 DEPLOYMENT_CHECKLIST.md - Checklist detallado
- 📊 READY_FOR_AZURE.md - Resumen visual
- 🔐 .env.azure - Variables de entorno

### Links Externos
- [Azure Portal](https://portal.azure.com)
- [Azure CLI Docs](https://docs.microsoft.com/cli/azure/)
- [Django Deployment](https://docs.djangoproject.com/en/5.0/howto/deployment/)
- [SendGrid Dashboard](https://sendgrid.com)
- [Stripe Dashboard](https://dashboard.stripe.com)

### Support
- Azure Support: https://azure.microsoft.com/support/
- Stack Overflow: [azure] [django] tags
- GitHub Issues: davidferradainacap/RifaTrust

---

## ✅ RESUMEN FINAL

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🚀 COMANDOS ESENCIALES LISTOS 🚀             ║
║                                                           ║
║  1. Variables de entorno preparadas en .env.azure        ║
║  2. SECRET_KEY generado y seguro                         ║
║  3. Archivos estáticos recolectados (174)                ║
║  4. Sistema verificado sin errores                       ║
║                                                           ║
║  📋 Próximo paso:                                         ║
║  → Crear Web App en portal.azure.com                     ║
║  → Copiar variables desde .env.azure                     ║
║  → Conectar GitHub para auto-deploy                      ║
║                                                           ║
║  ⏱️  Tiempo estimado: 20-30 minutos                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

_Generado: Diciembre 3, 2025 | RifaTrust v2.0_
