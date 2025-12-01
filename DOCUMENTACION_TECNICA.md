# DOCUMENTACIÓN TÉCNICA COMPLETA
## Sistema de Gestión de Rifas - RifaTrust

---

## 📋 ÍNDICE

1. [Información General del Proyecto](#información-general)
2. [Arquitectura del Sistema](#arquitectura)
3. [Tecnologías Utilizadas](#tecnologías)
4. [Estructura del Proyecto](#estructura)
5. [Modelos de Datos](#modelos)
6. [Seguridad](#seguridad)
7. [APIs y Endpoints](#apis)
8. [Guía de Instalación](#instalación)
9. [Guía de Despliegue](#despliegue)

---

## 📌 INFORMACIÓN GENERAL

### Descripción del Proyecto
**RifaTrust** es una plataforma web completa para la gestión, organización y participación en rifas digitales. El sistema permite a los usuarios crear rifas, comprar boletos, realizar sorteos verificables y gestionar patrocinios.

### Características Principales
- ✅ Sistema de usuarios con 4 roles (Participante, Organizador, Sponsor, Admin)
- ✅ Creación y gestión de rifas con sistema de aprobación
- ✅ Sistema de compra de boletos con códigos QR únicos
- ✅ Integración de pagos con Stripe
- ✅ Sistema de notificaciones en tiempo real
- ✅ Panel administrativo completo
- ✅ Encriptación de datos sensibles (Fernet AES-128)
- ✅ Hash de contraseñas con Argon2 (OWASP 2024)
- ✅ Sistema de patrocinios para rifas
- ✅ Sorteos verificables con timestamps
- ✅ Logs de auditoría completos

### Información del Proyecto
- **Nombre**: RifaTrust
- **Versión**: 1.0.0
- **Framework**: Django 5.0
- **Python**: 3.11+
- **Base de Datos**: SQLite (desarrollo) / MySQL 8.0 (producción)
- **Autor**: Sistema de Rifas INACAP
- **Fecha**: Diciembre 2025

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Patrón de Arquitectura
El sistema utiliza el patrón **MVT (Model-View-Template)** de Django:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Cliente   │────▶│   URLs.py    │────▶│   Views.py  │
│  (Browser)  │     │  (Routing)   │     │  (Lógica)   │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
                                                ▼
                    ┌──────────────┐     ┌─────────────┐
                    │ Templates    │◀────│  Models.py  │
                    │   (HTML)     │     │    (DB)     │
                    └──────────────┘     └─────────────┘
```

### Capas del Sistema

#### 1. Capa de Presentación (Templates)
- **Ubicación**: `/templates/`
- **Tecnología**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Función**: Interfaz de usuario responsive y moderna

#### 2. Capa de Lógica de Negocio (Views)
- **Ubicación**: `/apps/*/views.py`
- **Función**: Controladores que procesan peticiones HTTP
- **Decoradores**: `@login_required`, `@role_required`

#### 3. Capa de Datos (Models)
- **Ubicación**: `/apps/*/models.py`
- **ORM**: Django ORM
- **Función**: Abstracción de base de datos

#### 4. Capa de Seguridad
- **Ubicación**: `/apps/core/`
- **Componentes**:
  - `encryption.py` - Encriptación Fernet
  - `validators.py` - Validación y sanitización
  - `error_handlers.py` - Manejo seguro de errores

---

## 💻 TECNOLOGÍAS UTILIZADAS

### Backend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.11+ | Lenguaje principal |
| Django | 5.0.0 | Framework web |
| Django REST Framework | 3.14.0 | API REST |
| MySQL Client | 2.2.0 | Conector MySQL |
| Gunicorn | 21.2.0 | Servidor WSGI producción |

### Seguridad
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| cryptography | 46.0.3 | Encriptación Fernet (AES) |
| argon2-cffi | 25.1.0 | Hash de contraseñas |
| python-decouple | 3.8 | Variables de entorno |

### Pagos y Procesamiento
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Stripe | 7.8.0 | Procesamiento de pagos |
| Pillow | 10.1.0 | Procesamiento de imágenes |
| ReportLab | 4.0.7 | Generación de PDFs |
| OpenPyXL | 3.1.2 | Exportación Excel |

### Frontend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Bootstrap | 5.3.0 | Framework CSS |
| Font Awesome | 6.4.0 | Iconografía |
| JavaScript | ES6+ | Interactividad |
| Chart.js | 4.0.0 | Gráficos y estadísticas |

### Infraestructura
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Docker | 24.0+ | Contenedorización |
| Nginx | 1.24 | Servidor web / proxy |
| MySQL | 8.0 | Base de datos producción |

---

## 📁 ESTRUCTURA DEL PROYECTO

```
RS_project/
│
├── 📁 apps/                          # Aplicaciones Django
│   ├── 📁 users/                     # Gestión de usuarios
│   │   ├── models.py                 # User, Profile, Notification
│   │   ├── views.py                  # Registro, login, perfil
│   │   ├── forms.py                  # Formularios de usuario
│   │   ├── urls.py                   # URLs de usuarios
│   │   ├── admin.py                  # Admin de Django
│   │   ├── notifications.py          # Sistema de notificaciones
│   │   └── migrations/               # Migraciones de BD
│   │
│   ├── 📁 raffles/                   # Gestión de rifas
│   │   ├── models.py                 # Raffle, Ticket, SponsorshipRequest
│   │   ├── views.py                  # CRUD rifas, compra boletos
│   │   ├── forms.py                  # Formularios de rifas
│   │   ├── urls.py                   # URLs de rifas
│   │   ├── admin.py                  # Admin de rifas
│   │   └── migrations/               # Migraciones de BD
│   │
│   ├── 📁 payments/                  # Procesamiento de pagos
│   │   ├── models.py                 # Payment, Refund
│   │   ├── views.py                  # Stripe webhooks, confirmaciones
│   │   ├── urls.py                   # URLs de pagos
│   │   ├── admin.py                  # Admin de pagos
│   │   └── migrations/               # Migraciones de BD
│   │
│   ├── 📁 admin_panel/               # Panel administrativo
│   │   ├── models.py                 # AuditLog
│   │   ├── views.py                  # Dashboard, gestión usuarios/rifas
│   │   ├── urls.py                   # URLs del admin
│   │   └── admin.py                  # Admin Django
│   │
│   └── 📁 core/                      # Utilidades centrales
│       ├── encryption.py             # Encriptación Fernet
│       ├── validators.py             # Validación y sanitización
│       └── fields.py                 # Campos personalizados Django
│
├── 📁 config/                        # Configuración del proyecto
│   ├── settings.py                   # Configuración Django
│   ├── urls.py                       # URLs principales
│   ├── wsgi.py                       # Servidor WSGI
│   ├── asgi.py                       # Servidor ASGI
│   └── error_handlers.py             # Manejadores de errores
│
├── 📁 templates/                     # Plantillas HTML
│   ├── base.html                     # Template base
│   ├── home.html                     # Página principal
│   ├── 📁 users/                     # Templates de usuarios
│   ├── 📁 raffles/                   # Templates de rifas
│   ├── 📁 payments/                  # Templates de pagos
│   ├── 📁 admin_panel/               # Templates del admin
│   └── 📁 errors/                    # Páginas de error (400, 403, 404, 500)
│
├── 📁 static/                        # Archivos estáticos
│   ├── 📁 css/                       # Hojas de estilo
│   │   └── styles.css
│   └── 📁 js/                        # JavaScript
│       └── main.js
│
├── 📁 media/                         # Archivos subidos por usuarios
│   ├── 📁 raffles/                   # Imágenes de rifas
│   ├── 📁 prizes/                    # Imágenes de premios
│   ├── 📁 avatars/                   # Avatares de usuarios
│   └── 📁 documentos_legales/        # Documentos legales de rifas
│
├── 📁 logs/                          # Logs del sistema
│   ├── django.log                    # Log general
│   ├── security.log                  # Log de seguridad
│   └── errors.log                    # Log de errores
│
├── 📁 docker/                        # Configuración Docker
│   ├── 📁 nginx/                     # Configuración Nginx
│   │   └── nginx.conf
│   └── 📁 mysql/                     # Scripts MySQL
│       └── init.sql
│
├── 📄 manage.py                      # Script principal Django
├── 📄 requirements.txt               # Dependencias Python
├── 📄 .env.example                   # Variables de entorno ejemplo
├── 📄 Dockerfile                     # Imagen Docker
├── 📄 docker-compose.yml             # Orquestación Docker
├── 📄 .dockerignore                  # Exclusiones Docker
├── 📄 .gitignore                     # Exclusiones Git
├── 📄 db.sqlite3                     # Base de datos desarrollo
├── 📄 clean_database.py              # Script limpieza BD
│
└── 📄 DOCUMENTACION/                 # Documentación adicional
    ├── DEPLOYMENT_GUIDE.md           # Guía de despliegue
    ├── SECURITY_COMPLIANCE.md        # Certificación seguridad
    ├── IMPLEMENTATION_SUMMARY.md     # Resumen implementación
    └── QUICK_START.md                # Inicio rápido
```

---

## 🗄️ MODELOS DE DATOS

### Diagrama Entidad-Relación

```
┌─────────────────┐
│      USER       │
│─────────────────│
│ id (PK)         │
│ email (UNIQUE)  │◀────────┐
│ nombre          │         │
│ telefono (ENC)  │         │
│ rol             │         │
│ avatar          │         │
│ is_active       │         │
│ fecha_registro  │         │
└─────────────────┘         │
        │                   │
        │ 1:1               │
        ▼                   │
┌─────────────────┐         │
│    PROFILE      │         │
│─────────────────│         │
│ id (PK)         │         │
│ user_id (FK)    │         │
│ direccion (ENC) │         │
│ ciudad (ENC)    │         │
│ estado (ENC)    │         │
│ codigo_postal   │         │
│ fecha_nacimiento│         │
└─────────────────┘         │
                            │
        │                   │
        │ 1:N               │
        ▼                   │
┌─────────────────┐         │
│     RAFFLE      │         │
│─────────────────│         │
│ id (PK)         │         │
│ organizador (FK)│─────────┘
│ titulo          │
│ descripcion     │
│ imagen          │
│ precio_boleto   │
│ total_boletos   │
│ boletos_vendidos│
│ fecha_sorteo    │
│ estado          │
│ premio_principal│
│ valor_premio    │
└─────────────────┘
        │
        │ 1:N
        ▼
┌─────────────────┐
│     TICKET      │
│─────────────────│
│ id (PK)         │
│ rifa_id (FK)    │
│ usuario_id (FK) │
│ numero_boleto   │
│ fecha_compra    │
│ estado          │
│ codigo_qr       │
└─────────────────┘
        │
        │ 1:1
        ▼
┌─────────────────┐
│    PAYMENT      │
│─────────────────│
│ id (PK)         │
│ boleto_id (FK)  │
│ usuario_id (FK) │
│ monto           │
│ metodo_pago     │
│ estado          │
│ stripe_id       │
│ fecha_creacion  │
└─────────────────┘
```

### Leyenda:
- **PK**: Primary Key (Clave Primaria)
- **FK**: Foreign Key (Clave Foránea)
- **ENC**: Campo Encriptado
- **1:1**: Relación Uno a Uno
- **1:N**: Relación Uno a Muchos

---

## 🔒 SEGURIDAD

### Estándares Implementados

#### 1. Encriptación de Datos
- **Algoritmo**: Fernet (AES-128-CBC + HMAC-SHA256)
- **Biblioteca**: `cryptography 46.0.3`
- **Campos Encriptados**:
  - `User.telefono`
  - `Profile.direccion`
  - `Profile.ciudad`
  - `Profile.estado`
  - `Profile.codigo_postal`

#### 2. Hash de Contraseñas
- **Algoritmo**: Argon2id (OWASP 2024 recomendado)
- **Biblioteca**: `argon2-cffi 25.1.0`
- **Configuración**:
  ```python
  PASSWORD_HASHERS = [
      'django.contrib.auth.hashers.Argon2PasswordHasher',  # Principal
      'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Fallback
  ]
  ```

#### 3. Validación de Entradas
- Validación de email (RFC compliant)
- Validación de teléfono (formato chileno +56)
- Validación de RUT chileno con dígito verificador
- Sanitización de HTML (XSS prevention)
- Validación de URLs (javascript: prevention)
- Validación de archivos (tipo y tamaño)

#### 4. Sanitización
- Escape de HTML entities
- Prevención de SQL injection
- Sanitización de nombres de archivo
- Prevención de path traversal

#### 5. HTTPS y Headers de Seguridad
```python
# Producción
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

#### 6. Manejo Seguro de Errores
- Páginas de error personalizadas (400, 403, 404, 500)
- Sin exposición de stack traces en producción
- Logging estructurado con rotación
- Separación de logs por nivel de severidad

---

## 🔌 APIS Y ENDPOINTS

### Autenticación
```
POST   /login/              - Iniciar sesión
POST   /register/           - Registro de usuario
GET    /logout/             - Cerrar sesión
GET    /profile/            - Ver perfil
POST   /profile/edit/       - Editar perfil
```

### Rifas
```
GET    /raffles/            - Listar rifas activas
GET    /raffles/<id>/       - Detalle de rifa
POST   /raffles/create/     - Crear rifa (organizador)
PUT    /raffles/<id>/edit/  - Editar rifa (organizador)
DELETE /raffles/<id>/delete/- Eliminar rifa (organizador)
POST   /raffles/<id>/buy/   - Comprar boleto
GET    /raffles/organizer/dashboard/ - Dashboard organizador
```

### Pagos
```
POST   /payments/process/   - Procesar pago Stripe
GET    /payments/success/   - Confirmación exitosa
GET    /payments/failed/    - Pago fallido
POST   /payments/webhook/   - Webhook Stripe
```

### Administración
```
GET    /admin-panel/dashboard/        - Dashboard admin
GET    /admin-panel/users/            - Gestión usuarios
GET    /admin-panel/raffles/          - Gestión rifas
GET    /admin-panel/payments/         - Gestión pagos
GET    /admin-panel/audit-logs/       - Logs de auditoría
POST   /admin-panel/rifas-pendientes/<id>/revisar/ - Aprobar/Rechazar rifa
```

### Notificaciones
```
GET    /notifications/             - Listar notificaciones
GET    /notifications/count/       - Contador no leídas
POST   /notifications/<id>/mark-read/ - Marcar como leída
```

---

*Continúa en siguientes partes...*
