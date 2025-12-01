# DOCUMENTACIÓN TÉCNICA - PARTE 2
## Modelos de Datos Detallados - Sistema RifaTrust

---

## 📊 MÓDULO USERS - Gestión de Usuarios

### Modelo: User (Usuario Personalizado)

**Archivo**: `apps/users/models.py`

#### Descripción
Modelo personalizado de usuario que reemplaza el User por defecto de Django. Implementa autenticación por email en lugar de username, soporta 4 roles diferentes y encripta datos sensibles.

#### Herencia
- `AbstractBaseUser`: Proporciona funcionalidad core de autenticación
- `PermissionsMixin`: Proporciona sistema de permisos y grupos de Django

#### Campos

| Campo | Tipo | Descripción | Encriptado | Requerido |
|-------|------|-------------|------------|-----------|
| `id` | AutoField | ID autoincrementable (PK) | No | Auto |
| `email` | EmailField | Email único del usuario | No | Sí |
| `nombre` | CharField(100) | Nombre completo | No | Sí |
| `telefono` | EncryptedCharField(255) | Teléfono | **Sí (Fernet)** | No |
| `rol` | CharField(20) | Rol del usuario | No | Sí |
| `avatar` | ImageField | Imagen de perfil | No | No |
| `cuenta_validada` | BooleanField | Cuenta verificada | No | Sí |
| `is_active` | BooleanField | Usuario activo | No | Sí |
| `is_staff` | BooleanField | Acceso a admin Django | No | Sí |
| `fecha_registro` | DateTimeField | Fecha de registro | No | Auto |
| `ultima_conexion` | DateTimeField | Última vez que inició sesión | No | No |

#### Roles Disponibles

```python
ROLES = (
    ('participante', 'Participante'),    # Compra boletos, participa en rifas
    ('organizador', 'Organizador'),      # Crea y gestiona rifas
    ('sponsor', 'Sponsor'),              # Patrocina rifas con premios adicionales
    ('admin', 'Administrador'),          # Gestión completa del sistema
)
```

#### Métodos Importantes

##### `create_user(email, nombre, password, **extra_fields)`
```python
"""
Crea un usuario normal con validación de email y hash de contraseña.

Proceso:
1. Valida que el email no esté vacío
2. Normaliza el email (lowercase domain)
3. Crea instancia del modelo
4. Hashea la contraseña con Argon2
5. Guarda en base de datos

Args:
    email (str): Email único del usuario
    nombre (str): Nombre completo
    password (str): Contraseña en texto plano
    **extra_fields: Campos adicionales (rol, telefono, etc.)

Returns:
    User: Instancia del usuario creado

Raises:
    ValueError: Si email está vacío

Example:
    user = User.objects.create_user(
        email='juan@ejemplo.com',
        nombre='Juan Pérez',
        password='ContraseñaSegura123!',
        rol='participante'
    )
"""
```

##### `create_superuser(email, nombre, password, **extra_fields)`
```python
"""
Crea un superusuario con permisos administrativos completos.

Configuración automática:
- is_staff = True (acceso a Django Admin)
- is_superuser = True (todos los permisos)
- rol = 'admin' (lógica de negocio)

Args:
    email (str): Email del superusuario
    nombre (str): Nombre completo
    password (str): Contraseña
    **extra_fields: Campos adicionales

Returns:
    User: Instancia del superusuario

Example:
    admin = User.objects.create_superuser(
        email='admin@rifatrust.com',
        nombre='Administrador',
        password='AdminPass123!'
    )
"""
```

##### `get_full_name()`
```python
"""
Retorna el nombre completo del usuario.
Método requerido por AbstractBaseUser.

Returns:
    str: Nombre completo

Example:
    >>> user.get_full_name()
    'Juan Pérez González'
"""
```

##### `get_short_name()`
```python
"""
Retorna solo el primer nombre o el email si no hay nombre.

Returns:
    str: Primer nombre o email

Example:
    >>> user.get_short_name()
    'Juan'
"""
```

#### Seguridad

1. **Hash de Contraseñas**: Argon2id (OWASP 2024)
   ```python
   PASSWORD_HASHERS = [
       'django.contrib.auth.hashers.Argon2PasswordHasher',  # 40% más seguro que bcrypt
   ]
   ```

2. **Encriptación de Teléfono**: Fernet (AES-128)
   - Encriptación simétrica
   - Permite búsquedas exactas
   - Desencriptación solo con clave secreta

3. **Validación de Email**: RFC 5322 compliant
   - Formato válido
   - Dominio existente (opcional)
   - Unicidad en base de datos

---

### Modelo: Profile (Perfil Extendido)

**Archivo**: `apps/users/models.py`

#### Descripción
Perfil extendido del usuario con información personal adicional. Relación OneToOne con User. Todos los campos de ubicación están encriptados para proteger privacidad.

#### Relaciones
- **User**: OneToOne CASCADE (se elimina con el usuario)

#### Campos

| Campo | Tipo | Descripción | Encriptado | Requerido |
|-------|------|-------------|------------|-----------|
| `id` | AutoField | ID autoincrementable (PK) | No | Auto |
| `user` | OneToOneField | Referencia al usuario | No | Sí |
| `direccion` | EncryptedTextField | Dirección completa | **Sí (Fernet)** | No |
| `ciudad` | EncryptedCharField(255) | Ciudad de residencia | **Sí (Fernet)** | No |
| `estado` | EncryptedCharField(255) | Estado/Provincia | **Sí (Fernet)** | No |
| `codigo_postal` | EncryptedCharField(255) | Código postal | **Sí (Fernet)** | No |
| `pais` | CharField(100) | País | No | No |
| `fecha_nacimiento` | DateField | Fecha de nacimiento | No | No |

#### Ejemplo de Uso

```python
# Crear perfil automáticamente al crear usuario
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Acceder al perfil desde el usuario
user = User.objects.get(email='juan@ejemplo.com')
direccion_encriptada = user.profile.direccion  # Se desencripta automáticamente

# Actualizar perfil
user.profile.ciudad = "Santiago"
user.profile.codigo_postal = "8320000"
user.profile.save()  # Se encripta automáticamente antes de guardar
```

---

### Modelo: Notification (Notificaciones)

**Archivo**: `apps/users/models.py`

#### Descripción
Sistema de notificaciones en tiempo real para alertar a usuarios sobre eventos importantes. Soporta 9 tipos diferentes de notificaciones con sistema de leídas/no leídas.

#### Relaciones
- **User**: ForeignKey CASCADE (se eliminan con el usuario)
- **Raffle**: ForeignKey CASCADE opcional (notificaciones ligadas a rifas)

#### Campos

| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| `id` | AutoField | ID autoincrementable (PK) | Auto |
| `usuario` | ForeignKey(User) | Destinatario de la notificación | Sí |
| `tipo` | CharField(30) | Tipo/categoría de notificación | Sí |
| `titulo` | CharField(200) | Título breve | Sí |
| `mensaje` | TextField | Mensaje completo | Sí |
| `enlace` | CharField(500) | URL opcional | No |
| `leida` | BooleanField | Marcador de lectura | Sí |
| `fecha_creacion` | DateTimeField | Timestamp de creación | Auto |
| `fecha_lectura` | DateTimeField | Timestamp de lectura | No |
| `rifa_relacionada` | ForeignKey(Raffle) | Rifa asociada (opcional) | No |

#### Tipos de Notificaciones

```python
TIPO_CHOICES = (
    ('compra', 'Compra de Boleto'),              # Usuario compró boleto exitosamente
    ('ganador', 'Ganador de Rifa'),              # Usuario ganó una rifa
    ('sorteo', 'Sorteo Realizado'),              # Se realizó el sorteo de una rifa
    ('cancelacion', 'Rifa Cancelada'),           # Rifa fue cancelada, se procesarán reembolsos
    ('nuevo_organizador', 'Nueva Rifa Disponible'),  # Nueva rifa publicada
    ('recordatorio', 'Recordatorio de Sorteo'),  # Recordatorio previo al sorteo
    ('sistema', 'Notificación del Sistema'),     # Mensajes administrativos generales
    ('sponsor_aprobado', 'Sponsor Aprobado'),    # Solicitud de sponsor aprobada
    ('sponsor_rechazado', 'Sponsor Rechazado'),  # Solicitud de sponsor rechazada
    ('rifa', 'Rifa'),                            # Notificaciones generales sobre rifas
)
```

#### Métodos

##### `marcar_como_leida()`
```python
"""
Marca la notificación como leída y registra el timestamp.
Solo se ejecuta si la notificación no estaba previamente leída.

Proceso:
1. Verifica estado actual (no leída)
2. Cambia leida a True
3. Registra fecha_lectura con timezone.now()
4. Guarda cambios en base de datos

Returns:
    None

Example:
    notificacion = Notification.objects.get(id=123)
    notificacion.marcar_como_leida()
    # Ahora: leida=True, fecha_lectura='2025-12-01 10:30:00'
"""
```

#### Ejemplo de Creación

```python
# Notificar compra de boleto
Notification.objects.create(
    usuario=comprador,
    tipo='compra',
    titulo='✓ Compra Exitosa',
    mensaje=f'Has comprado el boleto #{numero} para "{rifa.titulo}"',
    enlace=f'/raffles/{rifa.id}/',
    rifa_relacionada=rifa
)

# Notificar ganador
Notification.objects.create(
    usuario=ganador,
    tipo='ganador',
    titulo='🎉 ¡FELICIDADES! Has Ganado',
    mensaje=f'Tu boleto #{boleto.numero_boleto} ha ganado "{rifa.titulo}"',
    enlace=f'/raffles/{rifa.id}/',
    rifa_relacionada=rifa
)

# Notificar a administradores
admins = User.objects.filter(rol='admin')
for admin in admins:
    Notification.objects.create(
        usuario=admin,
        tipo='sistema',
        titulo='Nueva Rifa Pendiente',
        mensaje=f'{organizador.nombre} solicita aprobación para "{rifa.titulo}"',
        enlace='/admin-panel/rifas-pendientes/',
        rifa_relacionada=rifa
    )
```

#### Consultas Comunes

```python
# Obtener notificaciones no leídas de un usuario
no_leidas = Notification.objects.filter(
    usuario=user,
    leida=False
).order_by('-fecha_creacion')

# Contar notificaciones no leídas
count = Notification.objects.filter(usuario=user, leida=False).count()

# Marcar todas como leídas
Notification.objects.filter(usuario=user, leida=False).update(
    leida=True,
    fecha_lectura=timezone.now()
)

# Obtener últimas 10 notificaciones
ultimas = Notification.objects.filter(usuario=user)[:10]

# Eliminar notificaciones antiguas (más de 30 días)
from datetime import timedelta
fecha_limite = timezone.now() - timedelta(days=30)
Notification.objects.filter(
    leida=True,
    fecha_lectura__lt=fecha_limite
).delete()
```

---

## 📊 MÓDULO RAFFLES - Gestión de Rifas

### Modelo: Raffle (Rifa)

**Archivo**: `apps/raffles/models.py`

#### Descripción
Modelo principal del sistema que representa una rifa completa. Incluye workflow de estados, sistema de aprobación administrativa, configuración de boletos, información de premios y sistema de pausas/extensiones.

#### Relaciones
- **organizador**: ForeignKey(User) CASCADE - Creador de la rifa
- **revisado_por**: ForeignKey(User) SET_NULL - Admin que revisó la rifa

#### Estados del Workflow

```
┌──────────┐
│ borrador │ ← Estado inicial al crear
└────┬─────┘
     │ Organizador envía a revisión
     ▼
┌──────────────────────┐
│ pendiente_aprobacion │
└──────┬───────────────┘
       │
       ├─── Admin aprueba ──▶ ┌──────────┐
       │                       │ aprobada │
       │                       └────┬─────┘
       │                            │ Organizador activa
       │                            ▼
       │                       ┌────────┐
       │                       │ activa │ ← Acepta compras
       │                       └────┬───┘
       │                            │
       │                            ├─── Admin pausa ──▶ ┌─────────┐
       │                            │                     │ pausada │
       │                            │                     └────┬────┘
       │                            │                          │
       │                            │                          └─ Revisión ─▶ activa
       │                            │
       │                            ├─── Fecha sorteo ──▶ ┌─────────┐
       │                            │                      │ cerrada │
       │                            │                      └────┬────┘
       │                            │                           │ Sorteo
       │                            │                           ▼
       │                            │                      ┌────────────┐
       │                            │                      │finalizada  │
       │                            │                      └────────────┘
       │                            │
       │                            └─── Admin/User ────▶ ┌────────────┐
       │                                                   │ cancelada  │
       │                                                   └────────────┘
       │
       └─── Admin rechaza ──▶ ┌────────────┐
                               │ rechazada  │
                               └────────────┘
```

#### Campos Principales

##### Identificación y Básicos
```python
organizador = ForeignKey(User)     # Creador y dueño de la rifa
titulo = CharField(200)            # "iPhone 15 Pro Max - Sorteo Diciembre"
descripcion = TextField()          # Descripción detallada, reglas, condiciones
imagen = ImageField()              # Imagen principal de la rifa
```

##### Configuración Económica
```python
precio_boleto = DecimalField(10, 2)     # $1,000.00 por boleto
total_boletos = IntegerField()          # 1000 boletos disponibles
boletos_vendidos = IntegerField()       # 750 vendidos hasta ahora
```

##### Fechas Importantes
```python
fecha_inicio = DateTimeField()           # Cuándo se activa la rifa
fecha_sorteo = DateTimeField()          # Cuándo se realiza el sorteo
fecha_creacion = DateTimeField()        # Cuándo se creó el registro
fecha_actualizacion = DateTimeField()   # Última modificación
```

##### Estado y Workflow
```python
estado = CharField(20)                  # Estado actual del workflow
```

##### Premio
```python
premio_principal = CharField(200)       # "iPhone 15 Pro Max 256GB"
descripcion_premio = TextField()        # Especificaciones técnicas
imagen_premio = ImageField()            # Foto del premio
valor_premio = DecimalField(12, 2)      # $1,200,000.00 valor comercial
```

##### Documentación Legal
```python
documento_legal = FileField()           # PDF/Word con autorización legal
```

##### Configuración de Compra
```python
permite_multiples_boletos = BooleanField()   # ¿Un usuario puede comprar varios?
max_boletos_por_usuario = IntegerField()     # Límite por usuario (ej: 10)
```

##### Sistema de Aprobación
```python
fecha_solicitud = DateTimeField()            # Cuándo se envió a revisión
revisado_por = ForeignKey(User)              # Qué admin revisó
fecha_revision_aprobacion = DateTimeField()  # Cuándo se revisó
comentarios_revision = TextField()           # Comentarios del revisor
motivo_rechazo = TextField()                 # Por qué se rechazó
```

##### Sistema de Pausas
```python
motivo_pausa = TextField()              # Por qué se pausó
fecha_pausa = DateTimeField()           # Cuándo se pausó
revision_admin = TextField()            # Análisis del admin
fecha_revision = DateTimeField()        # Cuándo se revisó la pausa
nueva_fecha_sorteo = DateTimeField()    # Extensión de fecha (si aplica)
```

#### Propiedades Calculadas

##### `porcentaje_vendido`
```python
@property
def porcentaje_vendido(self):
    """
    Calcula % de boletos vendidos.
    
    Formula: (vendidos / total) * 100
    
    Returns:
        float: 0.0 a 100.0
        
    Example:
        total_boletos=1000, boletos_vendidos=750
        → retorna 75.0
    """
    return (self.boletos_vendidos / self.total_boletos) * 100 if self.total_boletos > 0 else 0
```

##### `boletos_disponibles`
```python
@property
def boletos_disponibles(self):
    """
    Calcula boletos aún disponibles.
    
    Formula: max(0, total - vendidos)
    
    Returns:
        int: Nunca negativo
        
    Example:
        total_boletos=1000, boletos_vendidos=750
        → retorna 250
    """
    return max(0, self.total_boletos - self.boletos_vendidos)
```

##### `esta_disponible`
```python
@property
def esta_disponible(self):
    """
    Verifica si acepta compras.
    
    Returns:
        bool: True solo si estado=='activa'
        
    Note:
        No verifica boletos disponibles.
        Sistema permite sobreventa controlada.
    """
    return self.estado == 'activa'
```

##### `ingreso_actual`
```python
@property
def ingreso_actual(self):
    """
    Calcula ingreso generado.
    
    Formula: vendidos * precio
    
    Returns:
        Decimal: Monto recaudado
        
    Example:
        boletos_vendidos=750, precio_boleto=1000
        → retorna 750000
    """
    return self.boletos_vendidos * self.precio_boleto
```

##### `ingreso_potencial`
```python
@property
def ingreso_potencial(self):
    """
    Calcula ingreso máximo posible.
    
    Formula: total * precio
    
    Returns:
        Decimal: Ingreso si se venden todos
        
    Example:
        total_boletos=1000, precio_boleto=1000
        → retorna 1000000
        
    Note:
        Debe ser >= 2 * valor_premio
        (Regla de viabilidad)
    """
    return self.total_boletos * self.precio_boleto
```

---

*Continúa en siguiente archivo...*
