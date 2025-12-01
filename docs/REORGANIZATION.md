# Proyecto Sistema de Rifas - Estructura Reorganizada

## 📋 Resumen de Cambios

Este documento describe la reorganización completa del proyecto para seguir las convenciones internacionales y mejores prácticas de Django.

## 🗂️ Nueva Estructura del Proyecto

```
RS_project/
├── .github/                    # GitHub Actions y workflows
│   └── workflows/
│       └── django.yml         # CI/CD pipeline
│
├── .vscode/                   # Configuración de VS Code
│   ├── extensions.json        # Extensiones recomendadas
│   ├── launch.json           # Configuración de debugging
│   └── settings.json         # Configuración del editor
│
├── apps/                      # Aplicaciones Django (reorganizado)
│   ├── __init__.py
│   ├── admin_panel/          # Panel de administración
│   ├── payments/             # Sistema de pagos
│   ├── raffles/              # Gestión de rifas
│   └── users/                # Gestión de usuarios
│
├── config/                    # Configuración del proyecto
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py           # Actualizado con nuevas rutas
│   ├── urls.py               # Actualizado con nuevas rutas
│   └── wsgi.py
│
├── docs/                      # Documentación (reorganizado)
│   ├── README.md
│   ├── DATABASE_POPULATION_SUMMARY.md
│   └── FIXES_APPLIED.md
│
├── media/                     # Archivos de usuario
│   ├── prizes/
│   └── raffles/
│
├── scripts/                   # Scripts de utilidad (reorganizado)
│   ├── __init__.py
│   ├── README.md
│   ├── add_roulette_participants.py
│   ├── add_test_participants.py
│   ├── create_special_raffle.py
│   ├── create_test_raffle.py
│   └── populate_db.py
│
├── static/                    # Archivos estáticos
│   ├── css/
│   └── js/
│
├── templates/                 # Plantillas HTML
│   ├── base.html
│   ├── home.html
│   ├── admin_panel/
│   ├── payments/
│   ├── raffles/
│   └── users/
│
├── tests/                     # Tests del proyecto (nuevo)
│   └── README.md
│
├── .editorconfig             # Configuración de editor (nuevo)
├── .env                      # Variables de entorno (no versionado)
├── .env.example             # Ejemplo de variables de entorno (nuevo)
├── .gitignore               # Archivos ignorados por git (nuevo)
├── db.sqlite3               # Base de datos SQLite
├── manage.py                # Comando de gestión Django
├── pyproject.toml           # Configuración de Python y herramientas (nuevo)
├── README.md                # Documentación principal (nuevo)
└── requirements.txt         # Dependencias del proyecto
```

## 🔄 Cambios Realizados

### 1. Reorganización de Aplicaciones
- ✅ Todas las apps Django movidas a `apps/`
- ✅ Actualizado `apps.py` de cada aplicación con nuevas rutas
- ✅ Configuración de `INSTALLED_APPS` actualizada en `settings.py`

### 2. Reorganización de Scripts
- ✅ Scripts movidos de raíz a `scripts/`
- ✅ Actualizado todos los imports en scripts
- ✅ Agregado `README.md` con documentación de scripts

### 3. Reorganización de Documentación
- ✅ Archivos `.md` movidos a `docs/`
- ✅ Creado `README.md` principal completo
- ✅ Agregado `README.md` en carpeta docs

### 4. Archivos de Configuración Nuevos
- ✅ `.gitignore` - Control de versionado
- ✅ `.env.example` - Plantilla de variables de entorno
- ✅ `pyproject.toml` - Configuración de proyecto y herramientas
- ✅ `.editorconfig` - Consistencia de código
- ✅ `.vscode/` - Configuración de VS Code

### 5. Configuración de CI/CD
- ✅ `.github/workflows/django.yml` - Pipeline de GitHub Actions

### 6. Actualización de Imports
- ✅ `config/settings.py` - Apps con prefijo `apps.`
- ✅ `config/urls.py` - Imports actualizados
- ✅ `apps/*/views.py` - Todos los imports corregidos
- ✅ `apps/*/models.py` - Imports entre apps corregidos
- ✅ `scripts/*.py` - Todos los imports actualizados

### 7. Tests
- ✅ Carpeta `tests/` creada con estructura
- ✅ Documentación de testing incluida

## ✅ Verificación

El proyecto fue verificado con:
```bash
python manage.py check
```
**Resultado**: System check identified no issues (0 silenced)

## 🚀 Próximos Pasos

1. **Activar entorno virtual** (si no está activo):
   ```bash
   venv\Scripts\activate  # Windows
   ```

2. **Verificar migraciones** (pueden necesitar regenerarse):
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Ejecutar el servidor**:
   ```bash
   python manage.py runserver
   ```

4. **Poblar base de datos** (si es necesario):
   ```bash
   python scripts/populate_db.py
   ```

## 📝 Convenciones Seguidas

### Estructura de Proyecto Django
- ✅ Separación de apps en carpeta `apps/`
- ✅ Configuración en carpeta `config/`
- ✅ Scripts separados de código fuente
- ✅ Documentación centralizada en `docs/`
- ✅ Tests en carpeta dedicada

### Configuración de Desarrollo
- ✅ Variables de entorno en `.env`
- ✅ `.gitignore` completo
- ✅ EditorConfig para consistencia
- ✅ Configuración de VS Code
- ✅ CI/CD con GitHub Actions

### Código Limpio
- ✅ Imports absolutos desde `apps/`
- ✅ Configuración de Black y Flake8
- ✅ Estructura modular y escalable
- ✅ Documentación en cada carpeta

## 🔍 Notas Importantes

1. **AUTH_USER_MODEL**: Se mantiene como `'users.User'` (sin prefijo `apps.`) según requerimientos de Django

2. **INSTALLED_APPS**: Usa prefijo `apps.` para aplicaciones locales

3. **Imports**: Usar siempre `from apps.app_name.module import ...` para imports entre apps

4. **Scripts**: Ejecutar desde la raíz del proyecto: `python scripts/nombre_script.py`

## 📚 Referencias

- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Django Project Structure](https://docs.djangoproject.com/en/stable/intro/reusable-apps/)

---

**Fecha de reorganización**: 29 de noviembre de 2025
**Estado**: ✅ Completado y verificado
