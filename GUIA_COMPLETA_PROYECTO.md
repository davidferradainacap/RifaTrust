# GUÍA COMPLETA DEL PROYECTO RIFATRUST
## Documentación Técnica Integral

---

## 🎯 OBJETIVO DEL PROYECTO

**RifaTrust** es una plataforma web profesional para la gestión de rifas online con las siguientes características:

### Características Principales:
1. **Sistema de Usuarios Multi-Rol**
   - Participantes: Compran boletos
   - Organizadores: Crean y gestionan rifas
   - Sponsors: Patrocinan rifas con premios adicionales
   - Administradores: Supervisan todo el sistema

2. **Gestión Completa de Rifas**
   - Creación con validaciones de rentabilidad
   - Aprobación administrativa opcional
   - Estados configurables (borrador → activa → finalizada)
   - Límites de boletos personalizables

3. **Sistema de Sorteo Verificable**
   - Algoritmo SHA256+Timestamp transparente
   - Acta digital pública
   - Imposible de manipular
   - Auditable por cualquiera

4. **Procesamiento de Pagos**
   - Integración con Stripe
   - Múltiples métodos de pago
   - Sistema de reembolsos
   - Transacciones encriptadas

5. **Sistema de Patrocinios**
   - Sponsors pueden ofrecer premios adicionales
   - Organizadores pueden invitar sponsors
   - Aprobación bilateral

6. **Seguridad Avanzada**
   - Argon2 para passwords (OWASP 2024)
   - Fernet (AES-128) para campos sensibles
   - HTTPS/HSTS obligatorio
   - CSRF protection automático

---

## 📐 ARQUITECTURA DEL SISTEMA

### Patrón MVT (Model-View-Template) de Django

```
┌─────────────────────────────────────────────────────────┐
│                      CLIENTE (Browser)                   │
│  HTML + CSS + JavaScript + Bootstrap 5                  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP Request
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    DJANGO MIDDLEWARE                     │
│  • SecurityMiddleware (HTTPS, HSTS)                     │
│  • SessionMiddleware (Manejo de sesiones)               │
│  • CsrfViewMiddleware (Protección CSRF)                 │
│  • AuthenticationMiddleware (Usuario actual)            │
│  • MessageMiddleware (Mensajes flash)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                      URLS (Routing)                      │
│  config/urls.py → apps/*/urls.py                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                     VIEWS (Lógica)                       │
│  • apps/users/views.py (Auth, Profile)                  │
│  • apps/raffles/views.py (Rifas, Sorteos)               │
│  • apps/payments/views.py (Pagos)                        │
│  • apps/admin_panel/views.py (Administración)           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    MODELS (Datos)                        │
│  • User, Profile, Notification                          │
│  • Raffle, Ticket, Winner                               │
│  • Payment, Refund                                       │
│  • SponsorshipRequest                                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  DATABASE (PostgreSQL)                   │
│  Producción: PostgreSQL 14+                             │
│  Desarrollo: SQLite3                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ ESTRUCTURA DEL PROYECTO

```
RS_project/
│
├── config/                          # Configuración del proyecto
│   ├── settings.py                  # Settings principal
│   ├── urls.py                      # URLs raíz
│   ├── wsgi.py                      # Servidor WSGI
│   └── asgi.py                      # Servidor ASGI (async)
│
├── apps/                            # Aplicaciones Django
│   │
│   ├── users/                       # Gestión de usuarios
│   │   ├── models.py                # User, Profile, Notification
│   │   ├── views.py                 # Register, Login, Dashboard
│   │   ├── forms.py                 # RegisterForm, LoginForm
│   │   ├── admin.py                 # Admin de Django
│   │   └── urls.py                  # URLs de users
│   │
│   ├── raffles/                     # Gestión de rifas
│   │   ├── models.py                # Raffle, Ticket, Winner
│   │   ├── views.py                 # CRUD rifas, Sorteos
│   │   ├── forms.py                 # RaffleForm
│   │   └── urls.py                  # URLs de raffles
│   │
│   ├── payments/                    # Procesamiento de pagos
│   │   ├── models.py                # Payment, Refund
│   │   ├── views.py                 # process_payment
│   │   └── urls.py                  # URLs de payments
│   │
│   └── admin_panel/                 # Panel administrativo
│       ├── views.py                 # Gestión completa
│       └── urls.py                  # URLs de admin
│
├── templates/                       # Plantillas HTML
│   ├── base.html                    # Template base
│   ├── home.html                    # Página principal
│   ├── users/                       # Templates de users
│   ├── raffles/                     # Templates de raffles
│   ├── payments/                    # Templates de payments
│   └── admin_panel/                 # Templates de admin
│
├── static/                          # Archivos estáticos
│   ├── css/
│   │   └── styles.css               # Estilos personalizados
│   ├── js/
│   │   └── main.js                  # JavaScript principal
│   └── images/                      # Imágenes del sitio
│
├── media/                           # Archivos subidos
│   ├── raffles/                     # Imágenes de rifas
│   ├── prizes/                      # Imágenes de premios
│   └── avatars/                     # Avatares de usuarios
│
├── db.sqlite3                       # Base de datos (desarrollo)
├── manage.py                        # CLI de Django
├── requirements.txt                 # Dependencias Python
│
└── DOCUMENTACION/                   # Documentación técnica
    ├── DOCUMENTACION_TECNICA.md
    ├── DOCUMENTACION_MODELOS.md
    ├── DOCUMENTACION_MODELOS_PARTE3.md
    ├── DOCUMENTACION_VIEWS_PARTE4.md
    ├── DOCUMENTACION_VIEWS_PARTE5.md
    └── RESUMEN_DOCUMENTACION_COMPLETA.md
```

---

## 🔐 MODELOS DE DATOS

### 1. User (apps/users/models.py)

```python
class User(AbstractBaseUser):
    """Usuario personalizado con email como username"""
    
    # Identificación
    email = EmailField(unique=True)           # Username del sistema
    nombre = CharField(100)                   # Nombre completo
    
    # Seguridad
    password = CharField(128)                 # Hasheado con Argon2
    telefono = EncryptedCharField(15)         # Encriptado con Fernet
    
    # Rol
    ROL_CHOICES = [
        ('participante', 'Participante'),
        ('organizador', 'Organizador'),
        ('sponsor', 'Sponsor'),
        ('admin', 'Administrador'),
    ]
    rol = CharField(20, choices=ROL_CHOICES)
    
    # Estado
    is_active = BooleanField(default=True)
    cuenta_validada = BooleanField(default=False)  # Para sponsors
    
    # Auditoría
    fecha_registro = DateTimeField(auto_now_add=True)
    ultima_conexion = DateTimeField(null=True)
    
    # Avatar
    avatar = ImageField('avatars/', null=True)
```

**Relaciones:**
- `OneToOne` con Profile
- `ForeignKey` desde Notification
- `ForeignKey` desde Raffle (organizador)
- `ForeignKey` desde Ticket (usuario)

---

### 2. Raffle (apps/raffles/models.py)

```python
class Raffle(Model):
    """Rifa con workflow completo"""
    
    # Identificación
    titulo = CharField(200)
    descripcion = TextField()
    imagen = ImageField('raffles/')
    
    # Organizador
    organizador = ForeignKey(User, CASCADE)
    
    # Economía
    precio_boleto = DecimalField(10, 2)
    total_boletos = IntegerField()
    boletos_vendidos = IntegerField(default=0)
    
    # Premio
    premio_principal = CharField(200)
    descripcion_premio = TextField()
    imagen_premio = ImageField('prizes/')
    valor_premio = DecimalField(12, 2)
    
    # Fechas
    fecha_creacion = DateTimeField(auto_now_add=True)
    fecha_inicio = DateTimeField(null=True)
    fecha_sorteo = DateTimeField()
    fecha_finalizacion = DateTimeField(null=True)
    
    # Estados
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('pendiente_aprobacion', 'Pendiente Aprobación'),
        ('aprobada', 'Aprobada'),
        ('activa', 'Activa'),
        ('pausada', 'Pausada'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    estado = CharField(20, choices=ESTADO_CHOICES)
    
    # Configuración
    permite_multiples_boletos = BooleanField(default=True)
    max_boletos_por_usuario = IntegerField(default=10)
    
    # Aprobación
    fecha_solicitud = DateTimeField(null=True)
    fecha_aprobacion = DateTimeField(null=True)
    aprobado_por = ForeignKey(User, SET_NULL, null=True)
    motivo_rechazo = TextField(blank=True)
    
    # Legal
    documento_legal = FileField('legal_docs/')
```

**Propiedades Calculadas:**
```python
@property
def boletos_disponibles(self):
    return self.total_boletos - self.boletos_vendidos

@property
def porcentaje_vendido(self):
    if self.total_boletos > 0:
        return (self.boletos_vendidos / self.total_boletos) * 100
    return 0

@property
def ingreso_actual(self):
    return self.precio_boleto * self.boletos_vendidos

@property
def ingreso_potencial(self):
    return self.precio_boleto * self.total_boletos
```

---

### 3. Ticket (apps/raffles/models.py)

```python
class Ticket(Model):
    """Boleto de rifa"""
    
    # Relaciones
    rifa = ForeignKey(Raffle, CASCADE)
    usuario = ForeignKey(User, CASCADE)
    
    # Identificación
    numero_boleto = IntegerField()          # Número único en la rifa
    codigo_qr = CharField(100, unique=True) # UUID para validación
    
    # Estado
    ESTADO_CHOICES = [
        ('reservado', 'Reservado'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
        ('ganador', 'Ganador'),
    ]
    estado = CharField(20, default='reservado')
    
    # Auditoría
    fecha_compra = DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['rifa', 'numero_boleto']
```

---

### 4. Payment (apps/payments/models.py)

```python
class Payment(Model):
    """Registro de pago"""
    
    # Relaciones
    usuario = ForeignKey(User, CASCADE)
    boletos = ManyToManyField(Ticket)
    
    # Montos
    monto = DecimalField(10, 2)
    
    # Método
    METODO_PAGO = [
        ('tarjeta', 'Tarjeta'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('transferencia', 'Transferencia'),
        ('efectivo', 'Efectivo'),
    ]
    metodo_pago = CharField(20, choices=METODO_PAGO)
    
    # Estado
    ESTADO_PAGO = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    ]
    estado = CharField(20, default='pendiente')
    
    # IDs de Stripe (ENCRIPTADOS)
    transaction_id = EncryptedCharField(400, unique=True)
    payment_intent_id = EncryptedCharField(400, blank=True)
    
    # Fechas
    fecha_creacion = DateTimeField(auto_now_add=True)
    fecha_completado = DateTimeField(null=True)
    
    # Notas
    descripcion = TextField(blank=True)
    notas_admin = TextField(blank=True)
```

---

### 5. Winner (apps/raffles/models.py)

```python
class Winner(Model):
    """Ganador de sorteo con datos de verificación"""
    
    # Relaciones
    rifa = OneToOneField(Raffle, CASCADE)
    boleto = OneToOneField(Ticket, CASCADE)
    
    # Sorteo
    fecha_sorteo = DateTimeField(auto_now_add=True)
    verificado = BooleanField(default=False)
    premio_entregado = BooleanField(default=False)
    fecha_entrega = DateTimeField(null=True)
    
    # DATOS DE VERIFICACIÓN
    seed_aleatorio = CharField(64, null=True)      # Hash SHA256
    timestamp_sorteo = BigIntegerField(null=True)   # Microsegundos
    algoritmo = CharField(50, default='SHA256+Timestamp')
    hash_verificacion = CharField(64, null=True)    # Hash final
    participantes_totales = IntegerField(null=True)
    acta_digital = TextField(null=True)             # Documento completo
    
    # Notas
    notas = TextField(blank=True)
```

---

## 🔄 FLUJOS DEL SISTEMA

### Flujo 1: Registro y Login

```
Usuario visita /register/
         │
         ▼
Selecciona rol: participante | organizador | sponsor
         │
         ▼
¿Rol = sponsor?
    │
    ├─── SÍ → cuenta_validada = False
    │         Notificar admins
    │         Redirect /login/ (sin auto-login)
    │
    └─── NO → cuenta_validada = True
              Auto-login
              Redirect /dashboard/
         │
         ▼
Dashboard redirige según rol:
    • participante → /participant-dashboard/
    • organizador → /organizer-dashboard/
    • sponsor → /sponsor-dashboard/
    • admin → /admin-panel/
```

---

### Flujo 2: Crear Rifa

```
Organizador en /raffles/create/
         │
         ▼
Completa formulario:
    • Título, descripción, imagen
    • Precio y cantidad de boletos
    • Fecha de sorteo
    • Premio (descripción, valor, imagen)
    • Documento legal
         │
         ▼
Validaciones:
    ✓ Total boletos ≥ 100
    ✓ Ingreso total ≥ 2× valor premio
    ✓ Documento legal < 10MB
         │
         ▼
Selecciona estado:
    • Borrador → Guardar sin publicar
    • Pendiente Aprobación → Notificar admins
         │
         ▼
Estado = Pendiente Aprobación
         │
         ▼
Admin revisa en /admin-panel/
         │
         ├─── APROBAR → estado = 'aprobada'
         │              Notificar organizador
         │              Organizador puede activar
         │
         └─── RECHAZAR → estado = 'borrador'
                        Agregar motivo_rechazo
                        Notificar organizador
         │
         ▼
Organizador activa rifa
         │
         ▼
estado = 'activa'
fecha_inicio = now()
Rifa visible públicamente
```

---

### Flujo 3: Comprar Boletos

```
Usuario en /raffles/<id>/
         │
         ▼
Clic "Comprar Boletos"
         │
         ▼
Selecciona cantidad (1-10)
         │
         ▼
POST /raffles/<id>/buy/
         │
         ▼
TRANSACCIÓN ATÓMICA:
    1. SELECT FOR UPDATE (bloquear fila)
    2. Verificar disponibilidad
    3. Crear Tickets (estado='reservado')
    4. Incrementar boletos_vendidos
    5. COMMIT
         │
         ▼
Redirect /payments/process/1,2,3/
         │
         ▼
Crear Payment (estado='procesando')
         │
         ▼
Integración Stripe:
    • PaymentIntent.create()
    • Cobrar tarjeta
         │
         ├─── ÉXITO → Payment.estado = 'completado'
         │            Tickets.estado = 'pagado'
         │            Notificar usuario
         │            Redirect /payments/success/
         │
         └─── ERROR → Payment.estado = 'fallido'
                      Tickets quedan 'reservado' (timeout 10min)
                      Redirect /payments/failed/
```

---

### Flujo 4: Sorteo Verificable

```
Fecha sorteo alcanzada
         │
         ▼
Ventana de animación (3 minutos)
    • Mostrar ruleta animada
    • Usuarios ven participantes girando
         │
         ▼
POST /raffles/<id>/select-winner/
         │
         ▼
ALGORITMO VERIFICABLE:
    1. timestamp = now() en microsegundos
    2. seed_string = timestamp|rifa_id|titulo|boletos_ids
    3. seed_hash = SHA256(seed_string)
    4. seed_number = int(seed_hash, 16)
    5. random.seed(seed_number)
    6. winning_ticket = random.choice(tickets)
    7. hash_verificacion = SHA256(seed_hash|timestamp|ganador)
    8. acta_digital = documento completo
         │
         ▼
Crear Winner:
    • boleto = winning_ticket
    • seed_aleatorio = seed_hash
    • timestamp_sorteo = timestamp
    • hash_verificacion = hash_verificacion
    • acta_digital = acta
         │
         ▼
Actualizar estados:
    • Raffle.estado = 'finalizada'
    • Ticket.estado = 'ganador'
         │
         ▼
Notificaciones:
    • Ganador: "¡Felicidades! Has ganado"
    • Participantes: "Sorteo finalizado. Ganador: X"
         │
         ▼
Acta pública en /raffles/<id>/acta/
    • Cualquiera puede verificar el sorteo
    • Datos públicos: seed, timestamp, hash
    • Proceso auditable
```

---

## 🔒 SEGURIDAD

### 1. Passwords (Argon2)

```python
# settings.py
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Argon2 es el estándar OWASP 2024
# Resistente a:
#   - Ataques de fuerza bruta
#   - Rainbow tables
#   - GPU cracking
```

### 2. Encriptación de Campos (Fernet)

```python
from cryptography.fernet import Fernet

# Configuración
FERNET_KEY = os.environ.get('FERNET_KEY')
cipher = Fernet(FERNET_KEY)

# Campos encriptados:
User.telefono                    # EncryptedCharField
Profile.direccion                # EncryptedCharField
Profile.ciudad                   # EncryptedCharField
Profile.estado                   # EncryptedCharField
Profile.codigo_postal            # EncryptedCharField
Payment.transaction_id           # EncryptedCharField (UNIQUE)
Payment.payment_intent_id        # EncryptedCharField

# Fernet usa:
#   - AES-128 en modo CBC
#   - HMAC para autenticación
#   - Timestamp para prevenir replay attacks
```

### 3. HTTPS/HSTS

```python
# settings.py (producción)
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 4. CSRF Protection

```html
<!-- En todos los formularios -->
<form method="POST">
    {% csrf_token %}
    <!-- campos del formulario -->
</form>
```

Django genera un token único por sesión y lo valida en cada POST.

---

## 🚀 DESPLIEGUE

### Requisitos de Sistema

```
Python: 3.11+
Django: 5.0+
PostgreSQL: 14+ (producción)
Redis: 7.0+ (caché, opcional)
Nginx: 1.24+ (servidor web)
Gunicorn: 20.1+ (WSGI server)
```

### Variables de Entorno

```bash
# .env
SECRET_KEY=tu-clave-secreta-muy-larga
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/rifatrust

# Encriptación
FERNET_KEY=tu-clave-fernet-generada

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

### Comandos de Despliegue

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Migrar base de datos
python manage.py migrate

# 3. Crear superusuario
python manage.py createsuperuser

# 4. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 5. Ejecutar servidor (desarrollo)
python manage.py runserver

# 6. Ejecutar con Gunicorn (producción)
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

## 📈 MÉTRICAS DEL PROYECTO

### Líneas de Código

```
Models:          ~2,000 líneas
Views:           ~1,500 líneas
Forms:           ~400 líneas
Templates:       ~3,000 líneas
JavaScript:      ~500 líneas
CSS:             ~800 líneas
Tests:           ~1,000 líneas
───────────────────────────
TOTAL:           ~9,200 líneas
```

### Documentación

```
Archivos MD:     6 documentos
Líneas totales:  ~4,000 líneas
Comentarios:     ~1,000 líneas
Ejemplos:        ~100 snippets
```

### Modelos de Datos

```
Modelos:         12 modelos
Campos total:    ~150 campos
Relaciones:      ~30 ForeignKey/M2M
```

### Vistas

```
Vistas totales:  ~35 vistas
URLs:            ~40 endpoints
Formularios:     ~8 forms
```

---

## 🎓 CONCLUSIÓN

RifaTrust es un sistema completo, profesional y seguro para gestión de rifas online con:

✅ **Arquitectura sólida** (MVT Django)  
✅ **Seguridad avanzada** (Argon2, Fernet, HTTPS)  
✅ **Sorteos verificables** (SHA256+Timestamp)  
✅ **Pagos integrados** (Stripe)  
✅ **Multi-rol completo** (4 roles)  
✅ **Documentación exhaustiva** (4,000+ líneas)  
✅ **Código comentado** (1,000+ comentarios)  
✅ **Listo para producción** (PostgreSQL, Gunicorn, Nginx)

---

*Documentación actualizada: 1 de diciembre de 2025*
