# CONFIGURACIÓN CRÍTICA AZURE - EJECUTAR AHORA

## ⚠️ PROBLEMA ACTUAL
La app no está levantando porque Azure está usando configuración automática incorrecta.

## ✅ SOLUCIÓN: Configurar manualmente en Azure Portal

### PASO 1: Configuración General (General Settings)

1. Ir a Azure Portal → rifatrust-dhche4cabncab9d8
2. **Settings** → **Configuration** → **General settings**
3. En **Startup Command**, pegar EXACTAMENTE esto:

```bash
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 --access-logfile - --error-logfile - --log-level debug startup:app
```

4. Click **Save** (arriba)
5. Click **Continue** en el diálogo de confirmación

### PASO 2: Application Settings

En la misma página (**Configuration** → **Application settings**):

Agregar estos 4 settings (click "+ New application setting" para cada uno):

```
Nombre: PYTHONPATH
Valor: /home/site/wwwroot/backend

Nombre: DJANGO_SETTINGS_MODULE  
Valor: config.settings

Nombre: POST_BUILD_SCRIPT_PATH
Valor: deploy.sh

Nombre: WEBSITE_RUN_FROM_PACKAGE
Valor: 0
```

Click **Save** (arriba) después de agregar todos

### PASO 3: Reiniciar App Service

1. Click **Overview** (menú izquierdo)
2. Click **Restart** (arriba)
3. Click **Yes** para confirmar
4. Esperar 2-3 minutos

### PASO 4: Verificar logs

1. **Monitoring** → **Log stream**
2. Deberías ver:
   - `[STARTUP] Python path configured`
   - `[STARTUP] WSGI application loaded successfully`
   - `Starting gunicorn 21.2.0`
   - `Listening at: http://0.0.0.0:8000`

## 🔍 SI AÚN NO FUNCIONA

Copia los logs completos de **Log stream** y mándamelos.

## 📝 VERIFICACIÓN FINAL

Una vez configurado, probar:
- https://rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net/
- https://rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net/health/

Ambos deben cargar sin errores.
