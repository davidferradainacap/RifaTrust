# DOCUMENTACIÓN TÉCNICA - PARTE 4
## Views (Vistas) - Sistema RifaTrust

---

## 📋 ÍNDICE DE MÓDULOS

1. **Payments** - Procesamiento de pagos con Stripe
2. **Users** - Autenticación, perfiles y notificaciones
3. **Raffles** - Gestión de rifas y sorteos
4. **Admin Panel** - Panel de administración

---

## 💳 MÓDULO PAYMENTS

### 1. process_payment_view

**Propósito**: Procesar el pago de boletos reservados

**URL**: `/payments/process/<ticket_ids>/`

**Métodos**: GET, POST

**Autenticación**: Requerida

**Parámetros**:
- `ticket_ids` (URL): String con IDs separados por comas (ej: "1,2,3")

**Flujo de Trabajo**:

```
Usuario hace clic "Comprar boletos"
         │
         ▼
GET /payments/process/1,2,3/
         │
         ├─── Validar boletos existen
         ├─── Verificar usuario es propietario
         ├─── Verificar estado='reservado'
         └─── Calcular monto total
         │
         ▼
Mostrar formulario de pago
         │
         ▼
POST /payments/process/1,2,3/
         │
         ├─── Crear Payment (estado='procesando')
         ├─── Integrar con Stripe
         │    ├─── Crear PaymentIntent
         │    ├─── Cobrar tarjeta
         │    └─── Recibir confirmación
         │
         ├─── SI ÉXITO:
         │    ├─── Payment.estado = 'completado'
         │    ├─── Tickets.estado = 'pagado'
         │    ├─── Crear Notification
         │    └─── Redirect: payment_success
         │
         └─── SI ERROR:
              ├─── Payment.estado = 'fallido'
              ├─── Mostrar error
              └─── Redirect: payment_failed
```

**Validaciones de Seguridad**:
1. Usuario autenticado
2. Boletos pertenecen al usuario
3. Boletos están en estado 'reservado'
4. Transaction ID único (UUID4)

**Integración con Stripe**:
```python
# Configuración
stripe.api_key = settings.STRIPE_SECRET_KEY

# Crear Payment Intent
intent = stripe.PaymentIntent.create(
    amount=int(total_amount * 100),  # Convertir a centavos
    currency='mxn',  # Peso Mexicano
    metadata={
        'transaction_id': transaction_id,
        'user_id': request.user.id
    }
)

# Guardar Payment Intent ID (encriptado)
payment.payment_intent_id = intent.id
```

**Manejo de Errores Stripe**:
- `CardError`: Tarjeta declinada, sin fondos
- `InvalidRequestError`: Parámetros inválidos
- `AuthenticationError`: API key incorrecta
- `APIConnectionError`: Sin conexión a Stripe

**Código de Ejemplo**:
```python
# Comprar 3 boletos de una rifa
ticket_ids = "42,43,44"
url = f"/payments/process/{ticket_ids}/"

# POST con método de pago
data = {
    'metodo_pago': 'stripe'
}

# Si éxito: redirect a /payments/success/123/
# Si fallo: redirect a /payments/failed/123/
```

---

### 2. payment_success_view

**Propósito**: Página de confirmación de pago exitoso

**URL**: `/payments/success/<payment_id>/`

**Método**: GET

**Autenticación**: Requerida

**Información Mostrada**:
- Detalles del pago (monto, método, fecha)
- Lista de boletos comprados con números
- Código QR de cada boleto
- Link para descargar recibo
- Próximos pasos

**Seguridad**:
- Solo el usuario propietario puede ver su pago
- Validación: `usuario=request.user`

---

### 3. payment_failed_view

**Propósito**: Página de error cuando el pago falla

**URL**: `/payments/failed/<payment_id>/`

**Método**: GET

**Autenticación**: Requerida

**Información Mostrada**:
- Mensaje de error detallado
- Motivo del fallo (tarjeta declinada, fondos insuficientes, etc.)
- Opciones para reintentar el pago
- Link para contactar soporte

---

## 👥 MÓDULO USERS

### 1. register_view

**Propósito**: Registro de nuevos usuarios con validación de rol

**URL**: `/register/`

**Métodos**: GET, POST

**Autenticación**: No requerida (pública)

**Roles Disponibles**:
1. **Participante**: Auto-aprobado, puede comprar boletos
2. **Organizador**: Auto-aprobado, puede crear rifas
3. **Sponsor**: Requiere aprobación manual del admin
4. **Admin**: Solo desde Django admin

**Flujo de Registro**:

```
Usuario llena formulario de registro
         │
         ▼
¿Rol seleccionado = sponsor?
         │
         ├─── SÍ (SPONSOR):
         │    ├─── cuenta_validada = False
         │    ├─── Guardar en BD
         │    ├─── Crear Profile
         │    ├─── Mensaje: "Pendiente de validación"
         │    └─── Redirect: login (sin auto-login)
         │
         └─── NO (PARTICIPANTE/ORGANIZADOR):
              ├─── cuenta_validada = True
              ├─── Guardar en BD
              ├─── Crear Profile
              ├─── Auto-login (login automático)
              ├─── Mensaje: "Bienvenido"
              └─── Redirect: dashboard
```

**Validaciones**:
- Email único (no duplicado)
- Password fuerte (mínimo 8 caracteres)
- Fecha de nacimiento válida
- RUT válido (Chile) o RFC (México) según configuración

**Seguridad**:
- Password hasheado con Argon2 (OWASP 2024)
- CSRF protection en formulario
- Validación de cuenta para sponsors

**Código de Ejemplo**:
```python
# Formulario de registro
form = RegisterForm({
    'nombre': 'Juan Pérez',
    'email': 'juan@ejemplo.com',
    'password1': 'password_seguro123',
    'password2': 'password_seguro123',
    'rol': 'organizador',
    'fecha_nacimiento': '1990-05-15'
})

if form.is_valid():
    user = form.save()
    # Organizador auto-aprobado
    # Login automático
    # Redirect a dashboard
```

---

### 2. login_view

**Propósito**: Autenticación de usuarios

**URL**: `/login/`

**Métodos**: GET, POST

**Autenticación**: No requerida (pública)

**Validaciones de Seguridad**:
1. Credenciales correctas (email + password)
2. Cuenta validada (`cuenta_validada=True`)
3. Usuario activo (`is_active=True`)

**Flujo de Login**:

```
Usuario ingresa email y password
         │
         ▼
authenticate(email, password)
         │
         ├─── Usuario no existe → Error: "Credenciales inválidas"
         ├─── Password incorrecto → Error: "Credenciales inválidas"
         └─── Usuario encontrado
              │
              ▼
¿cuenta_validada = True?
         │
         ├─── NO: Error "Cuenta pendiente de validación"
         │        └─── Redirect: login
         │
         └─── SÍ: 
              ├─── Actualizar ultima_conexion
              ├─── Crear session (login())
              ├─── Mensaje: "Bienvenido de nuevo"
              └─── Redirect: dashboard
```

**Sistema de Autenticación**:
- Backend: `EmailBackend` (custom en settings.py)
- Hasher: Argon2PasswordHasher
- Sesión: Cookie HttpOnly con CSRF

**Auditoría**:
- Campo `ultima_conexion` actualizado en cada login
- Útil para estadísticas y seguridad

---

### 3. logout_view

**Propósito**: Cerrar sesión del usuario

**URL**: `/logout/`

**Método**: GET

**Autenticación**: Requerida

**Acciones**:
1. Eliminar sesión de `django_session` table
2. Limpiar cookie de sesión del navegador
3. Convertir `request.user` en `AnonymousUser`

**Flujo**:
```python
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')
```

---

### 4. dashboard_view

**Propósito**: Router central que redirige a dashboard específico según rol

**URL**: `/dashboard/`

**Método**: GET

**Autenticación**: Requerida

**Redirecciones por Rol**:

| Rol | Redirect | Descripción |
|-----|----------|-------------|
| `admin` | `admin_panel:dashboard` | Gestión completa del sistema |
| `organizador` | `raffles:organizer_dashboard` | Mis rifas, estadísticas |
| `sponsor` | `raffles:sponsor_dashboard` | Oportunidades de patrocinio |
| `participante` | `raffles:participant_dashboard` | Mis boletos, rifas activas |

**Código**:
```python
@login_required
def dashboard_view(request):
    user = request.user
    
    if user.rol == 'admin':
        return redirect('admin_panel:dashboard')
    elif user.rol == 'organizador':
        return redirect('raffles:organizer_dashboard')
    elif user.rol == 'sponsor':
        return redirect('raffles:sponsor_dashboard')
    else:
        return redirect('raffles:participant_dashboard')
```

---

### 5. profile_view

**Propósito**: Edición de perfil de usuario

**URL**: `/profile/`

**Métodos**: GET, POST

**Autenticación**: Requerida

**Campos Editables**:

**User (apps/users/models.py)**:
- `telefono` (EncryptedCharField)
- `avatar` (ImageField)

**Profile (apps/users/models.py)**:
- `fecha_nacimiento` (DateField)
- `direccion` (EncryptedCharField)
- `ciudad` (EncryptedCharField)
- `estado` (EncryptedCharField)
- `codigo_postal` (EncryptedCharField)
- `biografia` (TextField)

**Seguridad - Campos Encriptados**:
```python
# Los siguientes campos usan Fernet encryption (AES-128):
- User.telefono
- Profile.direccion
- Profile.ciudad
- Profile.estado
- Profile.codigo_postal

# Configuración en settings.py:
FERNET_KEY = os.environ.get('FERNET_KEY')
```

**Validaciones**:
- Avatar: Máximo 2MB, formatos: JPG, PNG, GIF
- Teléfono: Formato internacional
- Código postal: Validación según país
- Fecha de nacimiento: Usuario debe ser mayor de 18 años

**Flujo**:
```
GET /profile/
    ├─── get_or_create Profile
    ├─── Inicializar formulario con datos existentes
    └─── Renderizar template

POST /profile/
    ├─── Validar formulario
    ├─── Guardar telefono y avatar en User
    ├─── Guardar otros campos en Profile (encriptados)
    ├─── Mensaje: "Perfil actualizado"
    └─── Redirect: profile
```

---

### 6. notifications_view

**Propósito**: Buzón de notificaciones con filtros y paginación

**URL**: `/notifications/?filter=<tipo>&page=<numero>`

**Método**: GET

**Autenticación**: Requerida

**Query Parameters**:

| Parameter | Valores | Descripción |
|-----------|---------|-------------|
| `filter` | `all` | Todas las notificaciones (default) |
| | `unread` | Solo no leídas |
| | `sistema` | Notificaciones del sistema |
| | `compra` | Notificaciones de compras |
| | `sorteo` | Notificaciones de sorteos |
| | `ganador` | Notificaciones de premios |
| | `patrocinio` | Notificaciones de patrocinios |
| | `aprobacion` | Notificaciones de aprobaciones |
| | `rechazo` | Notificaciones de rechazos |
| | `rifa` | Notificaciones de rifas |
| `page` | Número | Página actual (paginación) |

**Funcionalidades**:
1. Filtrado por tipo de notificación
2. Paginación automática (15 por página)
3. Contador de totales y no leídas
4. Marca visual de leídas/no leídas
5. Link directo desde notificación a recurso relacionado

**Tipos de Notificaciones**:

```python
TIPO_CHOICES = [
    ('sistema', 'Sistema'),           # Mensajes del sistema
    ('compra', 'Compra'),              # Compra de boletos
    ('sorteo', 'Sorteo'),              # Sorteo realizado
    ('ganador', 'Ganador'),            # Has ganado un premio
    ('patrocinio', 'Patrocinio'),      # Solicitudes de patrocinio
    ('aprobacion', 'Aprobación'),      # Aprobación de cuenta/rifa
    ('rechazo', 'Rechazo'),            # Rechazo de solicitud
    ('rifa', 'Rifa'),                  # Nueva rifa publicada
    ('rifa_finalizada', 'Rifa Finalizada'),  # Rifa completada
]
```

**Campos de Notification**:
```python
class Notification(models.Model):
    usuario = ForeignKey(User)
    tipo = CharField(choices=TIPO_CHOICES)
    titulo = CharField(200)
    mensaje = TextField()
    leida = BooleanField(default=False)
    fecha_creacion = DateTimeField(auto_now_add=True)
    enlace = URLField(blank=True)  # Link al recurso
    rifa_relacionada = ForeignKey(Raffle, null=True)
```

**Ejemplo de Uso**:
```python
# Crear notificación de compra
Notification.objects.create(
    usuario=comprador,
    tipo='compra',
    titulo='Compra de boletos exitosa',
    mensaje=f'Has comprado 3 boleto(s) para "{rifa.titulo}"',
    enlace=f'/raffles/{rifa.id}/',
    rifa_relacionada=rifa
)

# Marcar como leída
notificacion.marcar_como_leida()

# Consultar no leídas
unread = Notification.objects.filter(
    usuario=user,
    leida=False
).count()
```

**Paginación**:
```python
# Django Paginator
paginator = Paginator(notifications, 15)  # 15 por página
page_obj = paginator.get_page(page_number)

# En el template:
{% for notification in page_obj %}
    <div class="notification {{ notification.tipo }}">
        <h4>{{ notification.titulo }}</h4>
        <p>{{ notification.mensaje }}</p>
        <a href="{{ notification.enlace }}">Ver detalles</a>
    </div>
{% endfor %}

{% if page_obj.has_other_pages %}
    <!-- Controles de paginación -->
{% endif %}
```

---

## 🎫 MÓDULO RAFFLES (Resumen)

### Views Principales:

1. **home_view**: Página principal con rifas activas
2. **raffles_list_view**: Lista de rifas con filtros
3. **raffle_detail_view**: Detalle de rifa con ruleta de sorteo
4. **participant_dashboard_view**: Dashboard de participante
5. **organizer_dashboard_view**: Dashboard de organizador
6. **sponsor_dashboard_view**: Dashboard de sponsor
7. **create_raffle_view**: Crear nueva rifa
8. **edit_raffle_view**: Editar rifa existente
9. **buy_ticket_view**: Comprar boletos
10. **roulette_view**: Vista de ruleta animada
11. **select_winner_view**: Ejecutar sorteo verificable
12. **acta_sorteo_view**: Generar acta digital del sorteo

### Views de Patrocinio:

13. **create_sponsorship_request_view**: Solicitar patrocinio
14. **accept_sponsorship_request_view**: Aceptar solicitud
15. **reject_sponsorship_request_view**: Rechazar solicitud
16. **browse_sponsors_view**: Buscar sponsors
17. **send_sponsor_invitation_view**: Invitar sponsor

*(Documentación detallada de Raffles en la siguiente parte)*

---

## 🔧 ADMIN PANEL (Resumen)

### Views Administrativas:

1. **admin_dashboard_view**: Dashboard principal de admin
2. **users_management_view**: Gestión de usuarios
3. **raffles_management_view**: Gestión de rifas
4. **payments_management_view**: Gestión de pagos
5. **audit_logs_view**: Registro de auditoría
6. **superuser_dashboard_view**: Dashboard de superusuario

*(Documentación detallada de Admin Panel en la siguiente parte)*

---

## 📊 RESUMEN DE SEGURIDAD

### Decoradores de Autenticación

```python
# Requiere login
@login_required
def vista(request):
    pass

# Requiere rol específico (custom decorator)
@require_role('organizador')
def vista(request):
    pass

# Requiere permisos Django
@permission_required('raffles.change_raffle')
def vista(request):
    pass
```

### Validaciones Comunes

1. **Usuario autenticado**: `@login_required`
2. **Pertenencia de recursos**: `usuario=request.user`
3. **CSRF protection**: Automático en forms
4. **XSS protection**: Template auto-escaping
5. **SQL Injection protection**: ORM de Django

### Campos Encriptados

```python
# Configuración Fernet
from cryptography.fernet import Fernet

FERNET_KEY = os.environ.get('FERNET_KEY')
cipher = Fernet(FERNET_KEY)

# Campos encriptados:
User.telefono
Profile.direccion
Profile.ciudad
Profile.estado
Profile.codigo_postal
Payment.transaction_id
Payment.payment_intent_id
```

---

*Fin de Parte 4*

**Próxima Parte**: Raffles Views detalladas y Admin Panel

**Archivos de Código Comentados**:
- ✅ `apps/payments/views.py` - 100% documentado
- ✅ `apps/users/views.py` - 100% documentado
- ⏳ `apps/raffles/views.py` - Siguiente
- ⏳ `apps/admin_panel/views.py` - Siguiente
