# CONFIGURACIÓN CRÍTICA - EJECUTAR AHORA EN AZURE PORTAL

## ERROR ACTUAL:
```
ModuleNotFoundError: No module named 'startup'
```

El archivo startup.py no está en /home/site/wwwroot en Azure.

## ✅ SOLUCIÓN INMEDIATA:

### CAMBIAR EL STARTUP COMMAND:

1. Azure Portal → rifatrust-dhche4cabncab9d8
2. **Settings** → **Configuration** → **General settings**
3. **Startup Command**, REEMPLAZAR con esto:

```bash
cd /home/site/wwwroot && python -m gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 --chdir /home/site/wwwroot --pythonpath /home/site/wwwroot/backend --access-logfile - --error-logfile - --log-level debug backend.config.wsgi:application
```

4. Click **Save**
5. Click **Overview** → **Restart**

## Application Settings que DEBEN estar:

```
PYTHONPATH = /home/site/wwwroot/backend
DJANGO_SETTINGS_MODULE = config.settings  
WEBSITE_RUN_FROM_PACKAGE = 0
```

## Verificación después de restart:

En **Log stream** deberías ver:
- `[INFO] Starting gunicorn`
- `[INFO] Listening at: http://0.0.0.0:8000`
- Sin errores "ModuleNotFoundError"
