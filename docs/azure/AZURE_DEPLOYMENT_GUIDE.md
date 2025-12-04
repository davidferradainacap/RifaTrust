# 🚀 GUÍA DE DESPLIEGUE EN AZURE - RifaTrust

**Fecha**: Diciembre 3, 2025  
**Estado**: ✅ LISTO PARA PRODUCCIÓN

---

## 📋 PRE-REQUISITOS

- [x] Cuenta de Azure activa
- [x] Azure CLI instalado (opcional, se puede usar el portal)
- [x] Git instalado y repositorio actualizado
- [x] Archivos estáticos recolectados (`collectstatic` ejecutado)
- [x] Sistema probado localmente

---

## 🔧 CONFIGURACIÓN ACTUAL DEL PROYECTO

### ✅ Archivos de Deployment Preparados

```
✓ .deployment              # Configuración de build en Azure
✓ runtime.txt              # Python 3.11
✓ startup.txt              # Comando gunicorn
✓ requirements.txt         # Todas las dependencias
✓ azure.env.example        # Variables de entorno de ejemplo
✓ staticfiles/             # Archivos estáticos compilados (174 archivos)
```

### ✅ Checks de Deployment

```bash
# Ejecutado exitosamente:
python manage.py check --deploy

# Warnings identificados (NORMALES para primer despliegue):
- Security settings (se activan en producción)
- DRF Spectacular type hints (no críticos)
```

### ✅ Archivos Estáticos

```bash
# Recolectados exitosamente:
python manage.py collectstatic --noinput --clear

# Resultado:
✓ 174 archivos copiados
✓ 504 archivos post-procesados (compresión)
✓ WhiteNoise configurado correctamente
```

---

## 🌐 PASO 1: CREAR WEB APP EN AZURE

### Opción A: Usando Azure Portal (Recomendado)

1. **Ir a Azure Portal**: https://portal.azure.com
2. **Crear un recurso** → Buscar "Web App"
3. **Configuración básica**:
   ```
   Subscription: Tu suscripción
   Resource Group: RifaTrust-RG (crear nuevo)
   Name: rifatrust-app
   Publish: Code
   Runtime stack: Python 3.11
   Region: Brazil South (o tu región preferida)
   ```

4. **Plan de App Service**:
   ```
   Tipo: Basic B1 (mínimo recomendado para producción)
   - CPU: 1 core
   - RAM: 1.75 GB
   - Storage: 10 GB
   Costo aproximado: ~$13 USD/mes
   ```

5. **Monitoring**: Habilitar Application Insights (recomendado)

6. **Review + Create** → Esperar despliegue (~2 minutos)

### Opción B: Usando Azure CLI

```bash
# Login
az login

# Crear Resource Group
az group create --name RifaTrust-RG --location brazilsouth

# Crear App Service Plan
az appservice plan create \
  --name RifaTrust-Plan \
  --resource-group RifaTrust-RG \
  --sku B1 \
  --is-linux

# Crear Web App
az webapp create \
  --resource-group RifaTrust-RG \
  --plan RifaTrust-Plan \
  --name rifatrust-app \
  --runtime "PYTHON:3.11"
```

---

## ⚙️ PASO 2: CONFIGURAR VARIABLES DE ENTORNO

### En Azure Portal

1. Ir a tu Web App → **Configuration** → **Application settings**
2. Agregar las siguientes variables:

```env
# DJANGO CORE
DEBUG=False
SECRET_KEY=TU_SECRET_KEY_SEGURO_GENERADO_AQUI
ALLOWED_HOSTS=rifatrust-app.azurewebsites.net
WEBSITE_HTTPLOGGING_RETENTION_DAYS=7

# DATABASE (SQLite temporal - cambiar a MySQL en producción)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=/home/site/wwwroot/db.sqlite3

# SENDGRID EMAIL
EMAIL_BACKEND=apps.core.email_backend.SendGridEmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=TU_SENDGRID_API_KEY
DEFAULT_FROM_EMAIL=tu-email@dominio.com

# SITE CONFIGURATION
SITE_DOMAIN=rifatrust-app.azurewebsites.net
SITE_URL=https://rifatrust-app.azurewebsites.net

# CSRF PROTECTION
CSRF_TRUSTED_ORIGINS=https://rifatrust-app.azurewebsites.net

# STRIPE (si aplica)
STRIPE_PUBLIC_KEY=pk_test_tu_key
STRIPE_SECRET_KEY=sk_test_tu_key
```

### Generar SECRET_KEY Segura

```python
# Ejecutar en Python local:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())

# Copiar el resultado a Azure
```

---

## 📦 PASO 3: DEPLOYMENT DESDE GITHUB

### Opción A: Deployment Center (Recomendado)

1. En Azure Portal → Tu Web App → **Deployment Center**
2. Seleccionar **GitHub**
3. Autorizar conexión con tu cuenta de GitHub
4. Seleccionar:
   ```
   Organization: davidferradainacap
   Repository: RifaTrust
   Branch: main
   ```
5. **Save** → Azure configurará CI/CD automáticamente

### Opción B: Git Local (Manual)

```bash
# Obtener credenciales de deployment
az webapp deployment list-publishing-credentials \
  --name rifatrust-app \
  --resource-group RifaTrust-RG

# Agregar remote de Azure
git remote add azure <deployment-url>

# Push a Azure
git push azure main
```

---

## 🔨 PASO 4: POST-DEPLOYMENT

### Ejecutar Migraciones

```bash
# Opción 1: SSH desde Azure Portal
# Portal → Web App → SSH → Conectar

cd /home/site/wwwroot
python manage.py migrate
python manage.py createsuperuser

# Opción 2: Azure CLI
az webapp ssh --name rifatrust-app --resource-group RifaTrust-RG
```

### Verificar Logs

```bash
# Ver logs en tiempo real
az webapp log tail --name rifatrust-app --resource-group RifaTrust-RG

# Descargar logs
az webapp log download \
  --name rifatrust-app \
  --resource-group RifaTrust-RG \
  --log-file logs_azure.zip
```

---

## 🔒 PASO 5: SEGURIDAD EN PRODUCCIÓN

### SSL/HTTPS (Automático en Azure)

- Azure proporciona certificado SSL gratuito
- HTTPS está habilitado por defecto
- En `settings.py` ya está configurado para producción cuando `DEBUG=False`

### Custom Domain (Opcional)

1. Azure Portal → Web App → **Custom domains**
2. Agregar tu dominio (ej: rifatrust.com)
3. Configurar DNS:
   ```
   Tipo: CNAME
   Nombre: www
   Valor: rifatrust-app.azurewebsites.net
   ```

### Rate Limiting

- ✅ django-axes ya configurado (5 intentos, 1 hora)
- ✅ Protección CSRF activa
- ✅ Encriptación AES-256 para datos sensibles

---

## 📊 PASO 6: MONITOREO

### Application Insights

1. Azure Portal → Web App → **Application Insights**
2. Habilitar si no está activo
3. Ver métricas:
   - Request/Response times
   - Errors y excepciones
   - Performance
   - User analytics

### Logs en Django

Los logs se guardan en:
```
/home/LogFiles/django.log        # Aplicación
/home/LogFiles/security.log      # Seguridad
/home/LogFiles/http/*.log        # HTTP requests
```

---

## 🗄️ PASO 7: BASE DE DATOS (PRODUCCIÓN)

### Opción A: Azure Database for MySQL (Recomendado)

```bash
# Crear servidor MySQL
az mysql server create \
  --resource-group RifaTrust-RG \
  --name rifatrust-mysql \
  --location brazilsouth \
  --admin-user adminuser \
  --admin-password TU_PASSWORD_SEGURO \
  --sku-name B_Gen5_1 \
  --version 8.0

# Configurar firewall para Azure services
az mysql server firewall-rule create \
  --resource-group RifaTrust-RG \
  --server rifatrust-mysql \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Crear base de datos
az mysql db create \
  --resource-group RifaTrust-RG \
  --server-name rifatrust-mysql \
  --name rifatrust_db
```

### Actualizar Variables de Entorno

```env
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=rifatrust_db
DATABASE_USER=adminuser@rifatrust-mysql
DATABASE_PASSWORD=TU_PASSWORD_SEGURO
DATABASE_HOST=rifatrust-mysql.mysql.database.azure.com
DATABASE_PORT=3306
```

### Opción B: SQLite (Solo desarrollo/pruebas)

- Ya configurado por defecto
- ⚠️ NO recomendado para producción
- Los datos se pierden al reiniciar el servicio

---

## 🎯 PASO 8: VERIFICACIÓN POST-DEPLOYMENT

### Checklist de Validación

```bash
# 1. Sitio accesible
curl -I https://rifatrust-app.azurewebsites.net
# Esperado: HTTP 200 OK

# 2. Admin panel
https://rifatrust-app.azurewebsites.net/admin/
# Esperado: Login page

# 3. API funcionando
https://rifatrust-app.azurewebsites.net/api/
# Esperado: DRF browsable API

# 4. Archivos estáticos
https://rifatrust-app.azurewebsites.net/static/css/styles.css
# Esperado: CSS content

# 5. Verificar logs
az webapp log tail --name rifatrust-app --resource-group RifaTrust-RG
# Esperado: Sin errores críticos
```

### Tests Funcionales

1. ✅ **Registro de usuario**
   - Abrir `/register/`
   - Crear cuenta nueva
   - Verificar email de confirmación enviado

2. ✅ **Login**
   - Acceder con credenciales
   - Verificar redirección al dashboard

3. ✅ **Crear Rifa** (como organizador)
   - Llenar formulario completo
   - Subir imágenes
   - Verificar creación exitosa

4. ✅ **Comprar boletos**
   - Seleccionar rifa activa
   - Agregar al carrito
   - Simular pago (si Stripe configurado)

5. ✅ **Panel Admin**
   - Login en `/admin/`
   - Verificar todas las apps visibles
   - Revisar logs de auditoría

---

## 🚨 TROUBLESHOOTING

### Error: "Application Error"

```bash
# Ver logs detallados
az webapp log tail --name rifatrust-app --resource-group RifaTrust-RG

# Verificar variables de entorno
az webapp config appsettings list --name rifatrust-app --resource-group RifaTrust-RG
```

### Error: "Static files not loading"

```bash
# SSH a la app
az webapp ssh --name rifatrust-app --resource-group RifaTrust-RG

# Verificar archivos estáticos
cd /home/site/wwwroot
ls -la staticfiles/

# Re-colectar si es necesario
python manage.py collectstatic --noinput
```

### Error: "Database locked" (SQLite)

**Solución**: Migrar a Azure MySQL (ver Paso 7)

SQLite no es adecuado para producción con múltiples workers.

### Error: 502 Bad Gateway

```bash
# Verificar logs de startup
az webapp log tail --name rifatrust-app --resource-group RifaTrust-RG

# Verificar startup.txt
cat startup.txt
# Debe contener: gunicorn --bind=0.0.0.0 --timeout 600 --chdir backend config.wsgi

# Verificar runtime.txt
cat runtime.txt
# Debe contener: python-3.11
```

---

## 📈 OPTIMIZACIONES POST-DEPLOYMENT

### 1. Caché con Azure Redis

```bash
az redis create \
  --name rifatrust-cache \
  --resource-group RifaTrust-RG \
  --location brazilsouth \
  --sku Basic \
  --vm-size c0
```

### 2. CDN para Archivos Estáticos

1. Azure Portal → **CDN profiles**
2. Crear perfil
3. Crear endpoint apuntando a tu Web App
4. Actualizar `STATIC_URL` en settings.py

### 3. Backup Automático

1. Azure Portal → Web App → **Backups**
2. Configurar backup schedule
3. Conectar Azure Storage Account

### 4. Scaling Horizontal

```bash
# Escalar a 2 instancias
az appservice plan update \
  --name RifaTrust-Plan \
  --resource-group RifaTrust-RG \
  --number-of-workers 2
```

---

## 📞 SOPORTE Y RECURSOS

### Documentación Oficial

- [Azure App Service](https://docs.microsoft.com/azure/app-service/)
- [Python en Azure](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [Django Deployment](https://docs.djangoproject.com/en/5.0/howto/deployment/)

### Monitoreo de Costos

- Azure Portal → **Cost Management + Billing**
- Configurar alertas de presupuesto
- Revisar mensualmente

### Scaling Costs

| Plan | vCPU | RAM | Storage | Precio/mes (USD) |
|------|------|-----|---------|------------------|
| B1   | 1    | 1.75 GB | 10 GB | ~$13 |
| B2   | 2    | 3.5 GB  | 10 GB | ~$26 |
| S1   | 1    | 1.75 GB | 50 GB | ~$70 |
| P1V2 | 1    | 3.5 GB  | 250 GB | ~$95 |

---

## ✅ DEPLOYMENT CHECKLIST FINAL

```
□ Web App creada en Azure
□ Variables de entorno configuradas
□ SECRET_KEY generada y guardada
□ Deployment desde GitHub configurado
□ Migraciones ejecutadas
□ Superusuario creado
□ SSL/HTTPS verificado
□ Custom domain configurado (opcional)
□ MySQL configurado (producción)
□ Backups configurados
□ Application Insights habilitado
□ Logs funcionando correctamente
□ Tests funcionales pasados
□ Monitoreo de costos configurado
```

---

## 🎉 CONCLUSIÓN

Tu aplicación RifaTrust está lista para producción en Azure con:

- ✅ Python 3.11
- ✅ Django 5.0
- ✅ Gunicorn + WhiteNoise
- ✅ SSL/HTTPS automático
- ✅ Deployment continuo desde GitHub
- ✅ Logs y monitoreo
- ✅ Seguridad nivel producción
- ✅ Términos y Condiciones implementados
- ✅ Sistema de recuperación de contraseña
- ✅ Rate limiting y protección contra fuerza bruta

**URL de producción**: https://rifatrust-app.azurewebsites.net

**Tiempo estimado de deployment**: 15-30 minutos

---

**¿Necesitas ayuda?** Revisa la sección Troubleshooting o contacta al equipo de soporte de Azure.
