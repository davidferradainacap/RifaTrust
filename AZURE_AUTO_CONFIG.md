# Configuración Automática de Azure App Service

Este proyecto está configurado para desplegarse automáticamente en Azure App Service sin necesidad de configuración manual.

## 🚀 Archivos de Configuración Automática

### 1. `oryx-manifest.yml`
Define la versión de Python y el **comando de inicio automático**:
```yaml
build:
  python:
    version: "3.11"

run:
  startupCommand: "gunicorn --config gunicorn.conf.py --chdir /home/site/wwwroot config.wsgi:application"
```

### 2. `.deployment`
Configura el proceso de build y post-build:
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT = true
SCM_REPOSITORY_PATH = .
PROJECT = .
POST_BUILD_COMMAND = bash .azure/post-build.sh
```

### 3. `gunicorn.conf.py`
Configuración completa de Gunicorn con rutas Python correctas:
- Cambia al directorio `/home/site/wwwroot`
- Añade `backend/` al Python path
- Configura workers, timeouts, logging

### 4. `.azure/post-build.sh`
Script que se ejecuta automáticamente después del build:
- Verifica la estructura de directorios
- Configura permisos
- Crea script de inicio

### 5. `.azureignore`
Excluye archivos innecesarios del despliegue:
- Cache de Python
- Virtual environments
- Logs locales
- Archivos de desarrollo

## 📋 Flujo de Despliegue Automático

1. **Push a GitHub** → GitHub detecta el cambio
2. **Azure Webhook** → Azure recibe notificación de GitHub
3. **Oryx Build** → Instala Python 3.11.14 y dependencias
4. **Post-Build** → Ejecuta `.azure/post-build.sh`
5. **Startup** → Usa el comando definido en `oryx-manifest.yml`
6. **App Running** → Django funcionando con Gunicorn

## ✅ Verificación

Después de cada push, verifica:

1. **Deployment Center** (Azure Portal):
   - Estado: Success ✓
   - Commit más reciente visible

2. **Log Stream**:
   ```
   [INFO] Starting gunicorn 23.0.0
   [INFO] Listening at: http://0.0.0.0:8000
   [INFO] Using worker: sync
   [INFO] Booting worker with pid: XXXX
   ```

3. **Website**:
   - Visita: https://rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net/
   - Debe cargar sin "Application Error"

## 🔧 NO Requiere Configuración Manual

Con esta configuración, **NO necesitas**:
- ❌ Configurar manualmente el Startup Command en Azure Portal
- ❌ Añadir Application Settings para PYTHONPATH
- ❌ Ejecutar comandos en SSH/Kudu
- ❌ Editar archivos en Azure

Todo se configura automáticamente con cada push a GitHub.

## 🐛 Troubleshooting

Si aparece "Application Error":

1. **Check Logs**: Azure Portal → Log stream
2. **Verificar Build**: Deployment Center → Ver logs del último deployment
3. **Estructura**: SSH/Kudu → Verificar que existe `/home/site/wwwroot/backend/`
4. **Gunicorn Config**: Verificar que existe `/home/site/wwwroot/gunicorn.conf.py`

## 📝 Comandos Útiles (Kudu/SSH)

```bash
# Ver estructura
ls -la /home/site/wwwroot/

# Verificar backend
ls -la /home/site/wwwroot/backend/

# Ver configuración de Gunicorn
cat /home/site/wwwroot/gunicorn.conf.py

# Probar import de WSGI manualmente
cd /home/site/wwwroot
source antenv/bin/activate
python -c "import sys; sys.path.insert(0, 'backend'); from config.wsgi import application; print('OK')"
```

## 🎯 Resultado Esperado

Con esta configuración, cada push a GitHub debe:
1. ✅ Build exitoso en Azure
2. ✅ Deployment exitoso
3. ✅ App iniciando automáticamente
4. ✅ Website accesible sin errores

---

**Última actualización**: Diciembre 4, 2025
