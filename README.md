# 🎲 RifaTrust - Sistema Profesional de Gestión de Rifas

**Plataforma completa para gestión de rifas en línea con integración de pagos y sorteos verificables.**

![Django](https://img.shields.io/badge/Django-5.0-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Azure](https://img.shields.io/badge/Azure-Ready-brightgreen)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

---

## 🚀 DEPLOYMENT A AZURE - LISTO!

```
✅ Proyecto 100% preparado para Azure
✅ Guías completas disponibles
✅ Configuración lista en .env.azure
✅ SECRET_KEY generado y seguro
✅ Archivos estáticos recolectados (174)
✅ Sistema verificado sin errores
✅ Tests al 100% (12/12 pasando)

📚 DOCUMENTACIÓN ORGANIZADA:
   📁 docs/azure/         → Guías de deployment en Azure
   📁 docs/testing/       → Plan y resultados de pruebas
   📁 docs/deployment/    → Scripts de deployment
   📁 docs/features/      → Funcionalidades implementadas
   📄 docs/INDICE_DOCUMENTACION.md → Índice completo

⏱️  Tiempo de deployment: 20-30 minutos
💰 Costo inicial: ~$13/mes (Azure B1)
```

---

## 🚀 Quick Start

```bash
# 1. Clonar
git clone https://github.com/davidferradainacap/RifaTrust.git
cd RifaTrust

# 2. Instalar dependencias
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Configurar .env (copiar de .env.example)
SECRET_KEY=tu-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 4. Inicializar base de datos
python manage.py migrate
python manage.py createsuperuser

# 5. Iniciar servidor
python manage.py runserver
```

Acceder a: **http://127.0.0.1:8000/**

---

## ✨ Características Principales

- ✅ Sistema de roles: Participante, Organizador, Sponsor, Admin
- ✅ Gestión completa de rifas con múltiples premios
- ✅ Integración con Stripe para pagos
- ✅ Sorteos verificables con hash SHA256
- ✅ Sistema de patrocinios y premios adicionales
- ✅ Panel de administración avanzado
- ✅ Notificaciones en tiempo real
- ✅ Encriptación AES-256 de datos sensibles
- ✅ Rate limiting (django-axes) contra fuerza bruta
- ✅ Recuperación de contraseña con tokens seguros
- ✅ Validación de emails con verificación MX
- ✅ Animaciones de carga profesionales
- ✅ Diseño responsive (mobile-first)

---

## 📚 Documentación Completa

**Ver archivo: [`DOCUMENTACION_COMPLETA.md`](DOCUMENTACION_COMPLETA.md)**

Incluye:
- Arquitectura del sistema
- Módulos y modelos explicados
- Seguridad y encriptación
- API REST endpoints
- Deployment en Azure
- Troubleshooting
- Y mucho más...

---

## 🛠️ Stack Tecnológico

**Backend:**
- Django 5.0 (Python 3.14)
- Django REST Framework
- PostgreSQL / MySQL / SQLite
- Argon2 (password hashing)
- Cryptography (AES-256)

**Frontend:**
- HTML5, CSS3, JavaScript vanilla
- Bootstrap 5
- Responsive design

**Seguridad:**
- django-axes (rate limiting)
- SendGrid (emails)
- Stripe (pagos)

**Deployment:**
- Azure App Service
- WhiteNoise (static files)
- Gunicorn (WSGI server)

---

## 📁 Estructura del Proyecto

```
RifaTrust/
├── backend/
│   ├── apps/
│   │   ├── users/          # Autenticación, perfiles, notificaciones
│   │   ├── raffles/        # Rifas, tickets, sorteos, patrocinios
│   │   ├── payments/       # Stripe, reembolsos
│   │   ├── admin_panel/    # Dashboard, reportes, auditoría
│   │   └── core/           # Encriptación, validadores, safe_errors
│   └── config/             # Settings, URLs, WSGI
├── frontend/
│   ├── static/             # CSS, JS (loading.js, main.js)
│   └── templates/          # HTML templates
├── media/                  # Uploads (avatares, imágenes)
├── logs/                   # Django logs
├── DOCUMENTACION_COMPLETA.md  # 📖 DOCUMENTACIÓN COMPLETA
├── requirements.txt
└── .env
```

---

## 🌐 Deployment en Azure

1. **Crear App Service:**
   ```bash
   az webapp create --name rifatrust --resource-group RifaTrust-RG --plan RifaTrust-Plan --runtime "PYTHON:3.11"
   ```

2. **Configurar variables de entorno** en Azure Portal

3. **Deploy:**
   ```bash
   git push azure main
   ```

4. **Migraciones:**
   ```bash
   az webapp ssh --name rifatrust
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

Ver guía completa en [`DOCUMENTACION_COMPLETA.md`](DOCUMENTACION_COMPLETA.md) sección 8.

---

## 🔒 Seguridad

- ✅ Hash Argon2 para contraseñas
- ✅ Encriptación AES-256 para datos sensibles
- ✅ Rate limiting (5 intentos, 1 hora bloqueo)
- ✅ Protección CSRF y XSS
- ✅ Manejo seguro de excepciones (no expone detalles)
- ✅ Validación de emails con MX records
- ✅ Tokens de recuperación con expiración (1 hora)
- ✅ Logs de auditoría completos

---

## 📧 Contacto

- **Repositorio**: https://github.com/davidferradainacap/RifaTrust
- **Documentación**: [`DOCUMENTACION_COMPLETA.md`](DOCUMENTACION_COMPLETA.md)
- **Admin Panel**: `/admin/`

---

## 📜 Licencia

Copyright © 2025 RifaTrust. Todos los derechos reservados.

---

**⭐ Para más detalles, consulta [`DOCUMENTACION_COMPLETA.md`](DOCUMENTACION_COMPLETA.md)**
