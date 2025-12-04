# 📦 Deployment

Esta carpeta contiene scripts y documentación para el **deployment** del sistema RifaTrust.

## 📄 Archivos

### Documentación
- **`DEPLOYMENT_READY.md`** - Estado de preparación para deployment
- **`.deployment`** - Configuración de deployment para Azure

### Scripts
- **`prepare_azure_deployment.ps1`** - Script PowerShell para preparar deployment en Azure

## 🚀 Proceso de Deployment

### 1. Pre-Deployment Checklist
```bash
# Verificar sistema
python manage.py check --deploy

# Ejecutar tests
python docs/testing/test_suite_runner.py

# Aplicar migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### 2. Preparar Azure
```powershell
# Ejecutar script de preparación
.\docs\deployment\prepare_azure_deployment.ps1
```

### 3. Deployment
Ver guía completa en: `docs/azure/AZURE_DEPLOYMENT_GUIDE.md`

## 📋 Configuración

### Variables de Entorno Requeridas
- `SECRET_KEY` - Clave secreta de Django
- `DEBUG` - False en producción
- `ALLOWED_HOSTS` - Hosts permitidos
- `DATABASE_*` - Configuración de MySQL
- `SENDGRID_API_KEY` - Para emails
- `STRIPE_*` - Claves de Stripe

### Archivos de Configuración
- `.env.azure` - En `docs/azure/`
- `docker-compose.yml` - En raíz del proyecto
- `Dockerfile` - En raíz del proyecto

## 🔍 Verificación Post-Deployment

### Health Checks
```bash
# Verificar que el sitio responde
curl https://tu-app.azurewebsites.net

# Verificar endpoints críticos
curl https://tu-app.azurewebsites.net/api/
curl https://tu-app.azurewebsites.net/health/
```

### Monitoring
- Azure Application Insights
- Logs en Azure Portal
- Métricas de rendimiento

## 🛠️ Troubleshooting

### Problemas Comunes

**Error de módulos Python:**
```bash
pip install -r requirements.txt
```

**Error de migraciones:**
```bash
python manage.py showmigrations
python manage.py migrate
```

**Error de archivos estáticos:**
```bash
python manage.py collectstatic --clear --noinput
```

## 📊 Métricas de Deployment

### Última Ejecución Exitosa
- **Fecha:** Diciembre 2024
- **Duración:** ~5 minutos
- **Tests:** 12/12 pasando (100%)
- **Estado:** Production Ready ✅

## 🔗 Referencias

- [Documentación Azure](../azure/AZURE_DEPLOYMENT_GUIDE.md)
- [Plan de Pruebas](../testing/PLAN_PRUEBAS_COMPLETO.md)
- [Django Deployment](https://docs.djangoproject.com/en/5.0/howto/deployment/)

---

**Última actualización:** Diciembre 2024  
**Próximo Deployment:** Pendiente aprobación
