# 📘 RIFATRUST - Documentación Completa del Sistema

**Sistema de Gestión de Rifas Profesional**  
Versión: 2.0  
Fecha: Diciembre 2025  
Estado: Producción

---

## 📋 ÍNDICE

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Módulos del Sistema](#módulos-del-sistema)
5. [Seguridad](#seguridad)
6. [Base de Datos](#base-de-datos)
7. [API REST](#api-rest)
8. [Deployment en Azure](#deployment-en-azure)
9. [Mantenimiento](#mantenimiento)
10. [Troubleshooting](#troubleshooting)

---

## 1. DESCRIPCIÓN GENERAL

### 1.1 ¿Qué es RifaTrust?

RifaTrust es un sistema web profesional para la gestión completa de rifas en línea. Permite a organizadores crear rifas, vender boletos de forma segura, realizar sorteos verificables y gestionar ganadores con transparencia total.

### 1.2 Características Principales

#### Gestión de Usuarios
- ✅ Sistema de roles: Participante, Organizador, Sponsor, Admin
- ✅ Registro con validación de email
- ✅ Autenticación segura con Argon2
- ✅ Recuperación de contraseña
- ✅ Rate limiting contra fuerza bruta (5 intentos, 1 hora)
- ✅ Perfiles personalizables con avatar

#### Gestión de Rifas
- ✅ Creación de rifas con múltiples premios
- ✅ Venta de boletos en línea
- ✅ Sistema de sorteo verificable (SHA256 + Timestamp)
- ✅ Acta digital del sorteo
- ✅ Notificaciones en tiempo real
- ✅ Dashboard por rol (participante, organizador, sponsor)

#### Sistema de Patrocinios
- ✅ Sponsors pueden ofrecer premios adicionales
- ✅ Sistema de solicitudes y aprobaciones
- ✅ Invitaciones de organizadores a sponsors
- ✅ Gestión de contratos digitales

#### Procesamiento de Pagos
- ✅ Integración con Stripe
- ✅ Pagos seguros con tarjeta
- ✅ Sistema de reembolsos automatizado
- ✅ Historial completo de transacciones

#### Panel de Administración
- ✅ Dashboard completo de métricas
- ✅ Gestión de usuarios y roles
- ✅ Moderación de rifas
- ✅ Sistema de auditoría completo
- ✅ Reportes en PDF y Excel
- ✅ Validación de emails masiva

#### Seguridad
- ✅ Encriptación de datos sensibles
- ✅ Protección CSRF y XSS
- ✅ Rate limiting en login
- ✅ Logs de auditoría
- ✅ Manejo seguro de excepciones
- ✅ Validación de emails con verificación MX

### 1.3 Stack Tecnológico

**Backend:**
- Django 5.0 (Python 3.14)
- Django REST Framework
- PostgreSQL / MySQL / SQLite
- Argon2 para hashing de contraseñas
- Cryptography para encriptación AES-256

**Frontend:**
- HTML5, CSS3, JavaScript vanilla
- Bootstrap 5
- Diseño responsive (mobile-first)

**Seguridad:**
- django-axes (rate limiting)
- SendGrid (emails transaccionales)
- Stripe (procesamiento de pagos)

**Deployment:**
- Azure App Service
- WhiteNoise (archivos estáticos)
- Gunicorn (servidor WSGI)

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Estructura del Proyecto

```
RS_project/
├── backend/                      # Backend Django
│   ├── apps/                     # Aplicaciones del proyecto
│   │   ├── users/               # Gestión de usuarios
│   │   │   ├── models.py        # User, Profile, Notification, EmailConfirmationToken, PasswordResetToken
│   │   │   ├── views.py         # Autenticación, registro, perfiles
│   │   │   ├── forms.py         # Formularios de usuario
│   │   │   ├── admin.py         # Admin personalizado
│   │   │   ├── email_service.py # Envío de emails
│   │   │   └── notifications.py # Sistema de notificaciones
│   │   │
│   │   ├── raffles/             # Gestión de rifas
│   │   │   ├── models.py        # Raffle, Ticket, Winner, Sponsorship
│   │   │   ├── views.py         # CRUD rifas, sorteos, patrocinios
│   │   │   ├── forms.py         # Formularios de rifas
│   │   │   └── admin.py         # Admin de rifas
│   │   │
│   │   ├── payments/            # Procesamiento de pagos
│   │   │   ├── models.py        # Payment, Refund
│   │   │   ├── views.py         # Integración Stripe
│   │   │   └── admin.py         # Admin de pagos
│   │   │
│   │   ├── admin_panel/         # Panel administrativo
│   │   │   ├── models.py        # AuditLog
│   │   │   ├── views.py         # Dashboard, reportes, moderación
│   │   │   └── admin.py         # Configuración admin
│   │   │
│   │   └── core/                # Utilidades compartidas
│   │       ├── encryption.py    # Encriptación AES-256
│   │       ├── fields.py        # Campos encriptados
│   │       ├── validators.py    # Validadores personalizados
│   │       ├── email_validator.py # Validación de emails
│   │       └── safe_errors.py   # Manejo seguro de excepciones
│   │
│   └── config/                  # Configuración Django
│       ├── settings.py          # Configuración principal
│       ├── urls.py              # URLs principales
│       └── wsgi.py              # WSGI para producción
│
├── frontend/                    # Frontend
│   ├── static/                  # Archivos estáticos
│   │   ├── css/                 # Estilos
│   │   │   ├── styles.css       # Estilos principales
│   │   │   ├── loading.css      # Animaciones de carga
│   │   │   └── ...
│   │   └── js/                  # JavaScript
│   │       ├── main.js          # Funciones principales
│   │       └── loading.js       # Sistema de loading
│   │
│   └── templates/               # Templates HTML
│       ├── base.html            # Template base
│       ├── home.html            # Página principal
│       ├── users/               # Templates de usuarios
│       ├── raffles/             # Templates de rifas
│       ├── payments/            # Templates de pagos
│       └── admin_panel/         # Templates de admin
│
├── logs/                        # Archivos de log
│   ├── django.log               # Logs generales
│   └── security.log             # Logs de seguridad
│
├── media/                       # Archivos subidos
│   ├── avatars/                 # Avatares de usuarios
│   ├── prizes/                  # Imágenes de premios
│   └── raffles/                 # Imágenes de rifas
│
├── manage.py                    # CLI de Django
├── requirements.txt             # Dependencias Python
├── .env                         # Variables de entorno
└── README.md                    # Este archivo
```

### 2.2 Flujo de Datos

```
Cliente (Browser)
    ↓
Frontend (HTML/CSS/JS)
    ↓
Django Views (Python)
    ↓
Models (ORM)
    ↓
Base de Datos (PostgreSQL/MySQL/SQLite)
```

### 2.3 Patrones de Diseño Implementados

1. **MVT (Model-View-Template)** - Arquitectura Django
2. **Repository Pattern** - Separación de lógica de negocio
3. **Dependency Injection** - Forms y servicios inyectados
4. **Observer Pattern** - Sistema de notificaciones
5. **Strategy Pattern** - Múltiples métodos de pago

---

## 3. INSTALACIÓN Y CONFIGURACIÓN

### 3.1 Requisitos Previos

- Python 3.14+
- pip (gestor de paquetes Python)
- Git
- Base de datos (PostgreSQL/MySQL/SQLite)

### 3.2 Instalación Local

#### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/davidferradainacap/RifaTrust.git
cd RifaTrust
```

#### Paso 2: Crear Entorno Virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### Paso 4: Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```env
# Django Settings
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite por defecto)
DATABASE_ENGINE=django.db.backends.sqlite3

# O usar MySQL
# DATABASE_ENGINE=django.db.backends.mysql
# DATABASE_NAME=rifatrust
# DATABASE_USER=root
# DATABASE_PASSWORD=tu_password
# DATABASE_HOST=localhost
# DATABASE_PORT=3306

# Email (SendGrid)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
SENDGRID_API_KEY=tu-api-key-de-sendgrid
DEFAULT_FROM_EMAIL=noreply@rifatrust.com

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Encryption
ENCRYPTION_KEY=tu-encryption-key-32-bytes

# Azure (producción)
# ALLOWED_HOSTS=rifatrust.azurewebsites.net
# CSRF_TRUSTED_ORIGINS=https://rifatrust.azurewebsites.net
```

#### Paso 5: Aplicar Migraciones
```bash
python manage.py migrate
```

#### Paso 6: Crear Superusuario
```bash
python manage.py createsuperuser
```

#### Paso 7: Iniciar Servidor
```bash
python manage.py runserver
```

Acceder a: http://127.0.0.1:8000/

### 3.3 Configuración de Producción

#### Variables de Entorno Azure
```env
DEBUG=False
ALLOWED_HOSTS=rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net
CSRF_TRUSTED_ORIGINS=https://rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
```

#### Archivos Estáticos
```bash
python manage.py collectstatic --noinput
```

---

## 4. MÓDULOS DEL SISTEMA

### 4.1 Módulo de Usuarios (apps/users)

#### Modelos

**User (Usuario del Sistema)**
```python
class User(AbstractBaseUser, PermissionsMixin):
    """
    Modelo personalizado de usuario que usa email como identificador.
    Hereda de AbstractBaseUser para autenticación personalizada.
    """
    # Campos principales
    email = models.EmailField(unique=True)           # Email único (username)
    nombre = models.CharField(max_length=150)        # Nombre completo
    telefono = models.CharField(max_length=20)       # Teléfono de contacto
    rol = models.CharField(max_length=20, choices=ROLES)  # Rol del usuario
    avatar = models.ImageField(upload_to='avatars/') # Foto de perfil
    
    # Seguridad
    cuenta_validada = models.BooleanField(default=False)  # Email confirmado
    ultima_conexion = models.DateTimeField()              # Última sesión
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # Permisos
    is_active = models.BooleanField(default=True)    # Usuario activo
    is_staff = models.BooleanField(default=False)    # Acceso al admin
    is_superuser = models.BooleanField(default=False) # Superusuario
```

**Roles Disponibles:**
- `participante`: Usuario que compra boletos
- `organizador`: Crea y gestiona rifas
- `sponsor`: Ofrece premios adicionales
- `admin`: Administrador del sistema

**EmailConfirmationToken**
```python
class EmailConfirmationToken(models.Model):
    """
    Token de confirmación de email con expiración de 24 horas.
    Se genera al registrarse y se envía por email.
    """
    usuario = models.ForeignKey(User)
    token = models.CharField(max_length=64, unique=True)  # Token único
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()                   # Expira en 24h
    is_used = models.BooleanField(default=False)          # Usado una sola vez
```

**PasswordResetToken**
```python
class PasswordResetToken(models.Model):
    """
    Token de recuperación de contraseña con expiración de 1 hora.
    Incluye tracking de IP para seguridad.
    """
    usuario = models.ForeignKey(User)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()                   # Expira en 1h
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField()           # IP del solicitante
```

**Notification**
```python
class Notification(models.Model):
    """
    Sistema de notificaciones en tiempo real.
    Se crean automáticamente en eventos importantes.
    """
    usuario = models.ForeignKey(User)
    tipo = models.CharField(max_length=20)      # info, pago, rifa, ganador, etc.
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    enlace = models.URLField(blank=True)        # URL para acción
    leido = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Vistas Principales

**register_view** - Registro de usuarios
- Valida email con verificación MX
- Envía email de confirmación
- Crea token de 24 horas
- Hash de contraseña con Argon2

**login_view** - Inicio de sesión
- Protección con django-axes (5 intentos, 1 hora bloqueo)
- Verifica cuenta validada
- Actualiza última conexión
- Redirección según rol

**confirm_email_view** - Confirmación de email
- Valida token único
- Verifica expiración
- Activa cuenta
- Auto-login después de confirmar

**password_reset_request_view** - Solicitar recuperación
- Valida existencia del usuario
- Crea token de 1 hora
- Envía email con enlace
- Registra IP del solicitante

**password_reset_confirm_view** - Cambiar contraseña
- Valida token y expiración
- Verifica fortaleza de contraseña
- Hash con Argon2
- Invalida token usado

#### Servicios de Email

**EmailConfirmationService**
```python
def send_confirmation_email(user, token):
    """
    Envía email de confirmación con enlace único.
    Template: users/emails/email_confirmation.html
    """
    # Genera URL con token
    confirmation_url = f"{BASE_URL}/confirm-email/{token}/"
    
    # Envía email HTML profesional
    send_mail(
        subject='Confirma tu email - RifaTrust',
        message=f'Confirma tu cuenta: {confirmation_url}',
        html_message=render_to_string('...'),
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )
```

**PasswordResetService**
```python
def send_reset_email(user, token):
    """
    Envía email de recuperación de contraseña.
    Template: users/emails/password_reset.html
    """
    reset_url = f"{BASE_URL}/password-reset/confirm/{token}/"
    # Similar a EmailConfirmationService
```

### 4.2 Módulo de Rifas (apps/raffles)

#### Modelos

**Raffle (Rifa)**
```python
class Raffle(models.Model):
    """
    Modelo principal de rifas.
    Gestiona todo el ciclo de vida de una rifa.
    """
    # Información básica
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='raffles/')
    
    # Configuración
    precio_boleto = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_boletos = models.IntegerField()              # Total de boletos
    boletos_vendidos = models.IntegerField(default=0)     # Vendidos
    boletos_disponibles = models.IntegerField()           # Calculado
    
    # Fechas
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    fecha_sorteo = models.DateTimeField()
    
    # Estados
    estado = models.CharField(choices=[
        ('activa', 'Activa'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada')
    ])
    
    # Relaciones
    organizador = models.ForeignKey(User, related_name='rifas_organizadas')
    ganador = models.ForeignKey(User, null=True, blank=True)
    
    # Premios
    premio_principal = models.CharField(max_length=200)
    premios_adicionales = models.JSONField(default=list)  # Array de premios
```

**Ticket (Boleto)**
```python
class Ticket(models.Model):
    """
    Boleto de rifa con número único.
    Gestiona estados de pago y reserva.
    """
    rifa = models.ForeignKey(Raffle, related_name='tickets')
    usuario = models.ForeignKey(User, related_name='mis_boletos')
    numero_boleto = models.IntegerField()                # Número único en la rifa
    
    # Estados
    estado = models.CharField(choices=[
        ('reservado', 'Reservado'),      # 15 minutos
        ('pagado', 'Pagado'),
        ('expirado', 'Expirado'),
        ('reembolsado', 'Reembolsado')
    ])
    
    # Fechas
    fecha_compra = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()            # Para reservas
    
    # Pago
    payment = models.ForeignKey('payments.Payment', null=True)
```

**Winner (Ganador)**
```python
class Winner(models.Model):
    """
    Registro del ganador del sorteo.
    Incluye verificación criptográfica.
    """
    rifa = models.OneToOneField(Raffle)
    boleto = models.ForeignKey(Ticket)
    
    # Verificación
    hash_verificacion = models.CharField(max_length=64)  # SHA256
    timestamp_sorteo = models.DateTimeField()
    seed_sorteo = models.CharField(max_length=100)       # Semilla aleatoria
    
    # Confirmación
    premio_entregado = models.BooleanField(default=False)
    fecha_entrega = models.DateTimeField(null=True)
    notas = models.TextField(blank=True)
```

**Sponsorship (Patrocinio)**
```python
class Sponsorship(models.Model):
    """
    Relación entre sponsor y rifa.
    Gestiona premios adicionales.
    """
    rifa = models.ForeignKey(Raffle, related_name='patrocinios')
    sponsor = models.ForeignKey(User, related_name='patrocinios')
    
    # Premio ofrecido
    nombre_premio = models.CharField(max_length=200)
    descripcion_premio = models.TextField()
    valor_premio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_premio = models.ImageField(upload_to='prizes/')
    
    # Estados
    estado = models.CharField(choices=[
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado')
    ])
    
    # Fechas
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True)
```

#### Vistas Principales

**create_raffle_view** - Crear rifa
- Solo organizadores y admins
- Validación de fechas
- Subida de imágenes
- Generación automática de boletos

**buy_tickets_view** - Comprar boletos
- Selección de cantidad
- Reserva temporal (15 minutos)
- Generación de números aleatorios únicos
- Transaction atómica (rollback en error)

**raffle_draw_view** - Realizar sorteo
- Solo organizador de la rifa
- Verifica estado activo
- Selección aleatoria de boleto ganador
- Generación de hash SHA256
- Creación de acta digital

**verify_draw_view** - Verificar sorteo
- Público
- Muestra hash de verificación
- Timestamp del sorteo
- Información del ganador

### 4.3 Módulo de Pagos (apps/payments)

#### Modelos

**Payment (Pago)**
```python
class Payment(models.Model):
    """
    Registro completo de transacciones.
    Integración con Stripe.
    """
    # Relaciones
    usuario = models.ForeignKey(User)
    rifa = models.ForeignKey(Raffle)
    tickets = models.ManyToManyField(Ticket)
    
    # Montos
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    comision = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Stripe
    stripe_payment_intent_id = models.CharField(max_length=200, unique=True)
    stripe_charge_id = models.CharField(max_length=200)
    
    # Estados
    estado = models.CharField(choices=[
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado')
    ])
    
    # Método
    metodo_pago = models.CharField(choices=[
        ('stripe', 'Tarjeta (Stripe)'),
        ('paypal', 'PayPal'),
        ('transferencia', 'Transferencia'),
        ('efectivo', 'Efectivo')
    ])
    
    # Fechas
    fecha_pago = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True)
```

**Refund (Reembolso)**
```python
class Refund(models.Model):
    """
    Gestión de reembolsos.
    """
    payment = models.OneToOneField(Payment, related_name='reembolso')
    monto_reembolsado = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=100)
    explicacion = models.TextField()
    stripe_refund_id = models.CharField(max_length=200)
    estado = models.CharField(choices=[...])
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_procesado = models.DateTimeField(null=True)
```

#### Integración con Stripe

**Flujo de Pago:**
1. Usuario selecciona boletos
2. Se crean boletos en estado "reservado"
3. Redirección a vista de pago
4. Stripe Payment Intent creado
5. Usuario ingresa datos de tarjeta
6. Stripe procesa el pago
7. Webhook confirma el pago
8. Boletos pasan a estado "pagado"
9. Notificaciones enviadas

**Código de Integración:**
```python
import stripe

def process_payment(request, ticket_ids):
    # Obtener boletos reservados
    tickets = Ticket.objects.filter(id__in=ticket_ids, estado='reservado')
    
    # Calcular monto
    total = sum(t.rifa.precio_boleto for t in tickets)
    
    # Crear Payment Intent en Stripe
    intent = stripe.PaymentIntent.create(
        amount=int(total * 100),  # Centavos
        currency='usd',
        metadata={'tickets': ticket_ids}
    )
    
    # Crear registro de pago
    payment = Payment.objects.create(
        usuario=request.user,
        monto=total,
        stripe_payment_intent_id=intent.id,
        estado='pendiente'
    )
    
    # Renderizar formulario de Stripe
    return render(request, 'payments/process.html', {
        'client_secret': intent.client_secret,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })
```

### 4.4 Módulo de Administración (apps/admin_panel)

#### Funcionalidades

**Dashboard Principal**
- Métricas en tiempo real
- Gráficos de ventas
- Usuarios activos
- Rifas activas
- Ingresos totales

**Gestión de Usuarios**
- Listar todos los usuarios
- Cambiar roles
- Suspender/Activar cuentas
- Ver historial completo
- Validar emails masivamente

**Moderación de Rifas**
- Aprobar/Rechazar rifas
- Cancelar rifas activas
- Realizar sorteos como admin
- Ver actas digitales

**Sistema de Auditoría**
```python
class AuditLog(models.Model):
    """
    Registro completo de acciones administrativas.
    Inmutable y con firma digital.
    """
    usuario = models.ForeignKey(User)
    accion = models.CharField(max_length=100)
    descripcion = models.TextField()
    modelo_afectado = models.CharField(max_length=100)
    objeto_id = models.IntegerField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['accion']),
        ]
```

**Reportes**
- Exportar usuarios a Excel
- Generar PDF de rifas
- Reporte de pagos
- Estadísticas generales

---

## 5. SEGURIDAD

### 5.1 Autenticación y Autorización

#### Hash de Contraseñas
```python
# settings.py
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Más seguro
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

#### Rate Limiting (django-axes)
```python
# Configuración
AXES_FAILURE_LIMIT = 5          # 5 intentos fallidos
AXES_COOLOFF_TIME = 1           # 1 hora de bloqueo
AXES_LOCKOUT_PARAMETERS = ['ip_address', 'username']
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'

# Comandos útiles
python manage.py axes_reset                    # Reset todos
python manage.py axes_reset_username email@... # Reset usuario
python manage.py axes_reset_ip 192.168.1.1    # Reset IP
```

### 5.2 Encriptación de Datos

#### Campos Encriptados (AES-256)
```python
from apps.core.fields import EncryptedCharField, EncryptedTextField

class User(AbstractBaseUser):
    telefono = EncryptedCharField(max_length=20)  # Encriptado en BD
    
# Se encripta automáticamente al guardar
user.telefono = "555-1234"
user.save()

# Se desencripta automáticamente al leer
print(user.telefono)  # "555-1234"
```

#### Generación de Key de Encriptación
```python
from cryptography.fernet import Fernet

# Generar key (ejecutar una vez)
key = Fernet.generate_key()
print(key.decode())  # Copiar a .env como ENCRYPTION_KEY
```

### 5.3 Protección CSRF y XSS

#### CSRF
```python
# settings.py
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True  # Solo HTTPS en producción
CSRF_TRUSTED_ORIGINS = ['https://rifatrust.azurewebsites.net']

# En templates
{% csrf_token %}
```

#### XSS
- Todos los inputs escapados automáticamente por Django
- Validación de datos en forms
- ContentSecurityPolicy headers (futuro)

### 5.4 Manejo Seguro de Excepciones

#### Sistema Implementado
```python
from apps.core.safe_errors import safe_json_error, handle_exception_safely

try:
    process_payment()
except Exception as e:
    # PRODUCCIÓN: Mensaje genérico al usuario
    # DEBUG: Mensaje + detalles
    # LOGS: Error completo con stack trace
    return JsonResponse(safe_json_error(e, get_error_message('payment')))
```

#### Beneficios
- ✅ Información sensible protegida
- ✅ Logs completos en servidor
- ✅ Mensajes amigables al usuario
- ✅ Debugging facilitado en desarrollo
- ✅ Cumplimiento OWASP Top 10

### 5.5 Validación de Emails

```python
from apps.core.email_validator import verify_email

# Validación completa
result = verify_email('user@example.com')

# result = {
#     'is_valid': True/False,
#     'format_valid': True/False,
#     'mx_valid': True/False,
#     'disposable': True/False,
#     'domain': 'example.com',
#     'mx_records': [...],
#     'message': '...'
# }
```

---

## 6. BASE DE DATOS

### 6.1 Diagrama ER Simplificado

```
User (Usuario)
    ├── Profile (1:1)
    ├── EmailConfirmationToken (1:N)
    ├── PasswordResetToken (1:N)
    ├── Notification (1:N)
    ├── Raffle (1:N) - como organizador
    ├── Ticket (1:N) - como comprador
    ├── Payment (1:N)
    └── Sponsorship (1:N)

Raffle (Rifa)
    ├── Ticket (1:N)
    ├── Winner (1:1)
    ├── Sponsorship (1:N)
    └── Payment (1:N)

Ticket (Boleto)
    └── Payment (N:M)

Payment (Pago)
    └── Refund (1:1)
```

### 6.2 Índices y Optimizaciones

```python
class Meta:
    indexes = [
        models.Index(fields=['email']),
        models.Index(fields=['rol']),
        models.Index(fields=['-fecha_registro']),
        models.Index(fields=['cuenta_validada', 'is_active']),
    ]
    ordering = ['-fecha_registro']
```

### 6.3 Migraciones

```bash
# Crear migraciones
python manage.py makemigrations

# Ver SQL de migración
python manage.py sqlmigrate users 0001

# Aplicar migraciones
python manage.py migrate

# Revertir migración
python manage.py migrate users 0005

# Ver migraciones aplicadas
python manage.py showmigrations
```

---

## 7. API REST

### 7.1 Endpoints de Usuarios

**POST /api/users/register/**
```json
Request:
{
  "email": "user@example.com",
  "nombre": "Juan Pérez",
  "telefono": "555-1234",
  "password": "SecurePass123",
  "rol": "participante"
}

Response (201):
{
  "success": true,
  "message": "Usuario registrado. Revisa tu email para confirmar.",
  "user_id": 123
}
```

**POST /api/users/request-password-reset/**
```json
Request:
{
  "email": "user@example.com"
}

Response (200):
{
  "success": true,
  "message": "Email de recuperación enviado."
}
```

**POST /api/users/confirm-password-reset/<token>/**
```json
Request:
{
  "password": "NewSecurePass123"
}

Response (200):
{
  "success": true,
  "message": "Contraseña actualizada exitosamente."
}
```

### 7.2 Endpoints de Notificaciones

**GET /notifications/api/count/**
```json
Response (200):
{
  "unread_count": 5
}
```

**GET /notifications/api/list/**
```json
Response (200):
{
  "notifications": [
    {
      "id": 1,
      "tipo": "pago",
      "titulo": "Pago Confirmado",
      "mensaje": "Tu pago de $50 fue procesado.",
      "enlace": "/payments/1/",
      "leido": false,
      "created_at": "2025-12-03T10:30:00Z"
    }
  ]
}
```

### 7.3 Endpoints de Rifas

**GET /raffles/api/<id>/winner/**
```json
Response (200):
{
  "has_winner": true,
  "winner": {
    "boleto_numero": 42,
    "usuario": "Juan Pérez",
    "fecha_sorteo": "2025-12-03T15:00:00Z"
  }
}
```

---

## 8. DEPLOYMENT EN AZURE

### 8.1 Configuración de Azure App Service

#### Paso 1: Crear App Service
```bash
# Azure CLI
az login
az group create --name RifaTrust-RG --location brazilsouth
az appservice plan create --name RifaTrust-Plan --resource-group RifaTrust-RG --sku B1
az webapp create --name rifatrust --resource-group RifaTrust-RG --plan RifaTrust-Plan --runtime "PYTHON:3.11"
```

#### Paso 2: Configurar Variables de Entorno
En Azure Portal → App Service → Configuration → Application Settings:

```
SECRET_KEY = [tu-secret-key]
DEBUG = False
ALLOWED_HOSTS = rifatrust.azurewebsites.net
CSRF_TRUSTED_ORIGINS = https://rifatrust.azurewebsites.net
DATABASE_ENGINE = django.db.backends.mysql
DATABASE_NAME = rifatrust_db
DATABASE_USER = rifaadmin
DATABASE_PASSWORD = [password]
DATABASE_HOST = rifatrust-mysql.mysql.database.azure.com
SENDGRID_API_KEY = [tu-api-key]
STRIPE_PUBLIC_KEY = [tu-public-key]
STRIPE_SECRET_KEY = [tu-secret-key]
ENCRYPTION_KEY = [tu-encryption-key]
```

#### Paso 3: Configurar Deployment
```bash
# Configurar repositorio Git
git remote add azure https://rifatrust.scm.azurewebsites.net/rifatrust.git

# Deployment
git push azure main
```

#### Paso 4: Startup Command
En Configuration → General Settings → Startup Command:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --chdir /home/site/wwwroot/backend
```

### 8.2 Base de Datos en Azure

#### Azure Database for MySQL
```bash
# Crear servidor MySQL
az mysql flexible-server create \
  --name rifatrust-mysql \
  --resource-group RifaTrust-RG \
  --location brazilsouth \
  --admin-user rifaadmin \
  --admin-password [password] \
  --sku-name Standard_B1ms \
  --storage-size 32

# Crear base de datos
az mysql flexible-server db create \
  --resource-group RifaTrust-RG \
  --server-name rifatrust-mysql \
  --database-name rifatrust_db
```

#### Aplicar Migraciones en Azure
```bash
# SSH a App Service
az webapp ssh --name rifatrust --resource-group RifaTrust-RG

# En la consola
cd /home/site/wwwroot
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 8.3 Archivos Estáticos

#### WhiteNoise Configuration
```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Después de SecurityMiddleware
    ...
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 8.4 Monitoreo y Logs

#### Application Insights
```python
# Instalar
pip install opencensus-ext-azure opencensus-ext-django

# settings.py
MIDDLEWARE += ['opencensus.ext.django.middleware.OpencensusMiddleware']

OPENCENSUS = {
    'TRACE': {
        'SAMPLER': 'opencensus.trace.samplers.ProbabilitySampler(rate=1.0)',
        'EXPORTER': 'opencensus.ext.azure.trace_exporter.AzureExporter(connection_string="...")',
    }
}
```

#### Ver Logs
```bash
# Azure CLI
az webapp log tail --name rifatrust --resource-group RifaTrust-RG

# O en Azure Portal
App Service → Monitoring → Log stream
```

---

## 9. MANTENIMIENTO

### 9.1 Tareas Periódicas

#### Limpieza de Tokens Expirados
```bash
# Agregar a cron o Azure Functions
python manage.py shell

from apps.users.models import EmailConfirmationToken, PasswordResetToken
from django.utils import timezone

# Eliminar tokens expirados
EmailConfirmationToken.objects.filter(
    expires_at__lt=timezone.now(),
    is_used=False
).delete()

PasswordResetToken.objects.filter(
    expires_at__lt=timezone.now(),
    is_used=False
).delete()
```

#### Liberar Boletos Reservados Expirados
```bash
from apps.raffles.models import Ticket
from django.utils import timezone

# Marcar como expirados
Ticket.objects.filter(
    estado='reservado',
    fecha_expiracion__lt=timezone.now()
).update(estado='expirado')
```

#### Backup de Base de Datos
```bash
# MySQL
mysqldump -h rifatrust-mysql.mysql.database.azure.com \
  -u rifaadmin -p rifatrust_db > backup_$(date +%Y%m%d).sql

# PostgreSQL
pg_dump -h ... -U ... rifatrust_db > backup_$(date +%Y%m%d).sql
```

### 9.2 Actualización de Dependencias

```bash
# Ver dependencias desactualizadas
pip list --outdated

# Actualizar requirements.txt
pip freeze > requirements.txt

# Actualizar en producción
git push azure main
```

### 9.3 Comandos Útiles de Django

```bash
# Shell interactivo
python manage.py shell

# Crear datos de prueba
python manage.py loaddata fixtures/initial_data.json

# Limpiar sesiones expiradas
python manage.py clearsessions

# Verificar integridad
python manage.py check --deploy

# Optimizar base de datos
python manage.py optimize_db
```

---

## 10. TROUBLESHOOTING

### 10.1 Problemas Comunes

#### Error: "No module named 'apps'"
```bash
# Verificar estructura
echo $PYTHONPATH

# Agregar al path
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot"

# O en settings.py
import sys
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
```

#### Error: "CSRF verification failed"
```python
# settings.py
CSRF_TRUSTED_ORIGINS = [
    'https://rifatrust.azurewebsites.net',
    'https://rifatrust-dhche4cabncab9d8.brazilsouth-01.azurewebsites.net',
]
```

#### Error: "Static files not found"
```bash
# Regenerar archivos estáticos
python manage.py collectstatic --clear --noinput

# Verificar WhiteNoise
python manage.py findstatic css/styles.css
```

#### Error: Rate limiting bloqueó admin
```bash
# Resetear bloqueo
python manage.py axes_reset_username admin@rifatrust.com

# O agregar a whitelist
# settings.py
AXES_IP_WHITELIST = ['127.0.0.1', 'TU_IP']
```

#### Error: Emails no se envían
```bash
# Verificar configuración
python manage.py shell

from django.core.mail import send_mail
send_mail('Test', 'Mensaje', 'from@email.com', ['to@email.com'])

# Ver logs de SendGrid
# https://app.sendgrid.com/activity
```

### 10.2 Debugging en Producción

```python
# NO usar DEBUG=True en producción
# En su lugar, configurar logging

LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/home/site/wwwroot/logs/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    }
}
```

### 10.3 Performance

#### Optimización de Queries
```python
# Usar select_related para ForeignKey
users = User.objects.select_related('profile').all()

# Usar prefetch_related para ManyToMany
raffles = Raffle.objects.prefetch_related('tickets').all()

# Contar sin cargar objetos
count = Ticket.objects.filter(estado='pagado').count()

# Valores específicos
tickets = Ticket.objects.values('id', 'numero_boleto')
```

#### Caché
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# En views
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 minutos
def raffle_list(request):
    ...
```

---

## 11. GLOSARIO

- **Rifa**: Sorteo donde se venden boletos numerados
- **Boleto**: Número participante en una rifa
- **Sorteo**: Selección aleatoria del ganador
- **Hash de Verificación**: SHA256 que prueba transparencia del sorteo
- **Sponsor**: Usuario que ofrece premios adicionales
- **Organizador**: Usuario que crea y gestiona rifas
- **Rate Limiting**: Límite de intentos para prevenir fuerza bruta
- **Token**: Cadena única para confirmaciones de email/password
- **Webhook**: Endpoint que recibe notificaciones de Stripe
- **CSRF**: Cross-Site Request Forgery (protección implementada)
- **XSS**: Cross-Site Scripting (protección implementada)
- **AES-256**: Algoritmo de encriptación simétrica

---

## 12. CONTACTO Y SOPORTE

- **Repositorio**: https://github.com/davidferradainacap/RifaTrust
- **Email**: soporte@rifatrust.com
- **Documentación**: /docs/
- **Admin Panel**: /admin/

---

## 13. LICENCIA

Copyright © 2025 RifaTrust. Todos los derechos reservados.

---

## 14. CHANGELOG

### v2.0 (Diciembre 2025)
- ✅ Sistema de recuperación de contraseña
- ✅ Validación de emails con MX records
- ✅ Rate limiting con django-axes
- ✅ Encriptación de datos sensibles
- ✅ Manejo seguro de excepciones
- ✅ Animaciones de loading
- ✅ Menú hamburguesa responsive
- ✅ Sistema de patrocinios completo
- ✅ Panel de administración avanzado
- ✅ Deployment en Azure App Service
- ✅ Documentación completa

### v1.0 (Noviembre 2025)
- ✅ Sistema básico de rifas
- ✅ Autenticación de usuarios
- ✅ Procesamiento de pagos con Stripe
- ✅ Sistema de sorteos
- ✅ Notificaciones

---

**Fin de la Documentación**

*Última actualización: Diciembre 2025*
*Versión del documento: 2.0*
