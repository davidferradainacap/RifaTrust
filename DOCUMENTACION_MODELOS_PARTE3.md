# DOCUMENTACIÓN TÉCNICA - PARTE 3
## Modelos de Tickets, Pagos y Patrocinios - Sistema RifaTrust

---

## 🎫 MODELO TICKET

### Modelo: Ticket (Boleto de Rifa)

**Archivo**: `apps/raffles/models.py`

#### Descripción
Representa un boleto individual comprado para una rifa. Cada boleto tiene un número único dentro de su rifa y un código QR para validación anti-falsificación.

#### Relaciones
- **rifa**: ForeignKey(Raffle) CASCADE - Rifa a la que pertenece
- **usuario**: ForeignKey(User) CASCADE - Propietario del boleto

#### Estados del Ciclo de Vida

```
┌───────────┐
│ reservado │ ← Estado inicial durante checkout
└─────┬─────┘
      │
      ├─── Pago exitoso ──▶ ┌────────┐
      │                      │ pagado │ ← Participa en sorteo
      │                      └────┬───┘
      │                           │
      │                           ├─── Sorteo realizado ──▶ ┌─────────┐
      │                           │                         │ ganador │
      │                           │                         └─────────┘
      │                           │
      │                           └─── No ganó ──▶ Permanece 'pagado'
      │
      └─── Pago fallido ──▶ ┌───────────┐
           o Usuario cancela │ cancelado │
                             └───────────┘
```

#### Campos Detallados

```python
# === RELACIONES ===
rifa = ForeignKey(Raffle, on_delete=CASCADE)
# - Si se elimina la rifa, se eliminan todos sus boletos
# - related_name='boletos' permite: rifa.boletos.all()

usuario = ForeignKey(User, on_delete=CASCADE)
# - Si se elimina el usuario, se eliminan sus boletos
# - related_name='boletos' permite: user.boletos.all()

# === IDENTIFICACIÓN ===
numero_boleto = IntegerField()
# - Número único dentro de la rifa (1, 2, 3, ..., N)
# - unique_together con 'rifa' asegura unicidad
# - Se asigna secuencialmente al momento de compra

# === INFORMACIÓN DE COMPRA ===
fecha_compra = DateTimeField(auto_now_add=True)
# - Timestamp exacto de la compra
# - Se establece automáticamente una sola vez
# - Usado para ordenar boletos y auditoría

estado = CharField(20, choices=ESTADO_CHOICES, default='reservado')
# - Estado actual del boleto en su ciclo de vida
# - 'reservado': Durante proceso de pago (5-10 min)
# - 'pagado': Pago confirmado, participa en sorteo
# - 'cancelado': Pago falló o usuario canceló
# - 'ganador': Boleto seleccionado en sorteo

# === SEGURIDAD ===
codigo_qr = CharField(100, unique=True)
# - Código único para validación del boleto
# - Generado con UUID4 o hash SHA256
# - UNIQUE en base de datos: imposible duplicar
# - Usado en app móvil para escaneo
# - Formato típico: "RIFA-001-BOLETO-042-ABC123DEF456"
```

#### Restricciones de Unicidad

```python
class Meta:
    unique_together = ['rifa', 'numero_boleto']
    # Asegura que no haya dos boletos con el mismo número en la misma rifa
    # Ejemplo válido:
    #   - Rifa 1, Boleto #42 ✓
    #   - Rifa 2, Boleto #42 ✓ (diferente rifa)
    # Ejemplo inválido:
    #   - Rifa 1, Boleto #42 ✗ (ya existe)
```

#### Ejemplo de Creación

```python
from apps.raffles.models import Raffle, Ticket
from apps.users.models import User
import uuid

# Obtener rifa y usuario
rifa = Raffle.objects.get(id=1)
comprador = User.objects.get(email='juan@ejemplo.com')

# Generar número de boleto único
ultimo_boleto = Ticket.objects.filter(rifa=rifa).order_by('-numero_boleto').first()
numero = 1 if not ultimo_boleto else ultimo_boleto.numero_boleto + 1

# Generar código QR único
codigo_qr = f"RIFA-{rifa.id:04d}-BOLETO-{numero:04d}-{uuid.uuid4().hex[:12].upper()}"

# Crear boleto
boleto = Ticket.objects.create(
    rifa=rifa,
    usuario=comprador,
    numero_boleto=numero,
    codigo_qr=codigo_qr,
    estado='reservado'  # Inicialmente reservado
)

# Después de confirmar pago
boleto.estado = 'pagado'
boleto.save()

# Actualizar contador de la rifa
rifa.boletos_vendidos += 1
rifa.save()
```

#### Consultas Comunes

```python
# Boletos de un usuario en una rifa específica
mis_boletos = Ticket.objects.filter(
    usuario=user,
    rifa=rifa,
    estado='pagado'
)

# Total de boletos pagados de un usuario
total = Ticket.objects.filter(
    usuario=user,
    estado='pagado'
).count()

# Verificar si usuario ya tiene boletos en una rifa
tiene_boletos = Ticket.objects.filter(
    usuario=user,
    rifa=rifa,
    estado__in=['reservado', 'pagado']
).exists()

# Obtener boleto ganador de una rifa
ganador = Ticket.objects.get(
    rifa=rifa,
    estado='ganador'
)

# Validar código QR
try:
    boleto = Ticket.objects.get(codigo_qr=codigo_escaneado)
    if boleto.estado == 'pagado':
        print(f"Boleto válido: #{boleto.numero_boleto}")
    else:
        print(f"Boleto en estado: {boleto.estado}")
except Ticket.DoesNotExist:
    print("Código QR inválido")
```

---

## 💳 MODELO PAYMENT

### Modelo: Payment (Pago)

**Archivo**: `apps/payments/models.py`

#### Descripción
Registra transacciones de pago realizadas por usuarios al comprar boletos. Soporta múltiples métodos de pago y encripta información sensible de transacciones.

#### Relaciones
- **usuario**: ForeignKey(User) CASCADE - Usuario que realizó el pago
- **boletos**: ManyToMany(Ticket) - Boletos comprados en esta transacción

#### Campos Detallados

```python
# === RELACIONES ===
usuario = ForeignKey(User, on_delete=CASCADE, related_name='pagos')
# - Usuario que realizó el pago
# - Si se elimina usuario, se eliminan sus pagos
# - Acceso inverso: user.pagos.all()

boletos = ManyToManyField(Ticket, related_name='pagos')
# - Relación muchos a muchos: un pago puede incluir varios boletos
# - Un boleto puede tener múltiples registros de pago (intentos)
# - Acceso: payment.boletos.all() o ticket.pagos.all()

# === INFORMACIÓN FINANCIERA ===
monto = DecimalField(10, 2)
# - Monto total de la transacción
# - max_digits=10: hasta $99,999,999.99
# - decimal_places=2: centavos exactos
# - Ejemplo: 15000.00 ($15,000)

metodo_pago = CharField(20, choices=METODO_PAGO)
# Opciones:
# - 'tarjeta': Tarjeta de Crédito/Débito (Visa, Mastercard)
# - 'paypal': PayPal
# - 'stripe': Stripe (principal)
# - 'transferencia': Transferencia Bancaria
# - 'efectivo': Efectivo (presencial)

estado = CharField(20, choices=ESTADO_PAGO, default='pendiente')
# Estados:
# - 'pendiente': Pago iniciado, esperando confirmación
# - 'procesando': Procesador de pagos está validando
# - 'completado': Pago exitoso, boletos confirmados
# - 'fallido': Error en el pago, boletos cancelados
# - 'reembolsado': Dinero devuelto al usuario

# === DETALLES DE TRANSACCIÓN (ENCRIPTADOS) ===
transaction_id = EncryptedCharField(400, unique=True)
# - ID único de la transacción del procesador
# - ENCRIPTADO con Fernet para proteger datos sensibles
# - UNIQUE: no puede haber transacciones duplicadas
# - Formato Stripe: "ch_1A2B3C4D5E6F7G8H"

payment_intent_id = EncryptedCharField(400, blank=True)
# - ID del intent de pago en Stripe
# - ENCRIPTADO para seguridad
# - Usado para rastrear intento de pago completo
# - Formato Stripe: "pi_1A2B3C4D5E6F7G8H"

# === FECHAS ===
fecha_creacion = DateTimeField(auto_now_add=True)
# - Momento exacto en que se creó el registro
# - Se establece automáticamente una vez

fecha_completado = DateTimeField(null=True, blank=True)
# - Momento en que el pago se completó exitosamente
# - null hasta que estado='completado'

# === INFORMACIÓN ADICIONAL ===
descripcion = TextField(blank=True)
# - Descripción de la compra
# - Ejemplo: "3 boletos para Rifa iPhone 15"

notas_admin = TextField(blank=True)
# - Notas internas solo para administradores
# - Útil para seguimiento de casos especiales
```

#### Workflow de Pago

```
Usuario hace clic en "Comprar"
         │
         ▼
┌─────────────────┐
│ Payment creado  │
│ estado=pendiente│
└────────┬────────┘
         │
         ▼
Redirección a Stripe
         │
         ├─── Usuario paga ───▶ ┌──────────────┐
         │                      │   procesando │
         │                      └──────┬───────┘
         │                             │
         │                             ▼
         │                      Webhook de Stripe
         │                             │
         │                             ├─── Exitoso ───▶ ┌────────────┐
         │                             │                  │ completado │
         │                             │                  └──────┬─────┘
         │                             │                         │
         │                             │                         ▼
         │                             │                  Boletos → pagado
         │                             │                  Email confirmación
         │                             │
         │                             └─── Error ───▶ ┌─────────┐
         │                                             │ fallido │
         │                                             └─────────┘
         │
         └─── Usuario cancela ───▶ ┌─────────┐
              o Timeout             │ fallido │
                                    └─────────┘
```

#### Ejemplo de Creación

```python
from apps.payments.models import Payment
from apps.raffles.models import Ticket
from decimal import Decimal
import stripe

# Crear boletos reservados
boletos = []
for i in range(3):  # Comprar 3 boletos
    boleto = Ticket.objects.create(
        rifa=rifa,
        usuario=user,
        numero_boleto=next_number,
        codigo_qr=generate_qr(),
        estado='reservado'
    )
    boletos.append(boleto)

# Calcular monto total
monto = rifa.precio_boleto * len(boletos)

# Crear Payment Intent en Stripe
intent = stripe.PaymentIntent.create(
    amount=int(monto * 100),  # Stripe usa centavos
    currency='clp',
    metadata={'rifa_id': rifa.id, 'user_id': user.id}
)

# Crear registro de pago
payment = Payment.objects.create(
    usuario=user,
    monto=monto,
    metodo_pago='stripe',
    estado='pendiente',
    transaction_id=intent.id,
    payment_intent_id=intent.id,
    descripcion=f"{len(boletos)} boletos para {rifa.titulo}"
)

# Asociar boletos al pago
payment.boletos.set(boletos)

# Después del webhook de Stripe (pago exitoso)
payment.estado = 'completado'
payment.fecha_completado = timezone.now()
payment.save()

# Actualizar estado de boletos
for boleto in boletos:
    boleto.estado = 'pagado'
    boleto.save()
```

---

## 💰 MODELO REFUND

### Modelo: Refund (Reembolso)

**Archivo**: `apps/payments/models.py`

#### Descripción
Gestiona reembolsos de pagos completados. Relación OneToOne con Payment - cada pago puede tener un solo reembolso.

#### Campos

```python
pago = OneToOneField(Payment, on_delete=CASCADE)
# - Pago que se está reembolsando
# - OneToOne: solo un reembolso por pago
# - related_name='reembolso': payment.reembolso

monto = DecimalField(10, 2)
# - Monto a reembolsar
# - Puede ser parcial o total
# - Debe ser <= payment.monto

motivo = CharField(50, choices=MOTIVOS)
# Motivos disponibles:
# - 'duplicado': Pago Duplicado (error técnico)
# - 'cancelacion': Cancelación de Rifa
# - 'error_sistema': Error del Sistema
# - 'solicitud_usuario': Solicitud del Usuario
# - 'fraude': Sospecha de Fraude
# - 'otro': Otro Motivo

razon = TextField()
# - Explicación detallada del reembolso
# - Visible para admin y usuario

procesado_por = ForeignKey(User, SET_NULL, null=True)
# - Admin que procesó el reembolso
# - SET_NULL: se mantiene registro si se elimina admin

fecha_solicitud = DateTimeField(auto_now_add=True)
# - Cuándo se solicitó el reembolso

fecha_procesado = DateTimeField(null=True, blank=True)
# - Cuándo se completó el reembolso

estado = CharField(20, choices=[...])
# Estados:
# - 'solicitado': Solicitud pendiente de revisión
# - 'aprobado': Aprobado, esperando procesamiento
# - 'rechazado': Solicitud rechazada
# - 'completado': Reembolso procesado exitosamente
```

#### Ejemplo de Reembolso

```python
from apps.payments.models import Refund

# Rifa cancelada - reembolsar a todos los compradores
rifa_cancelada = Raffle.objects.get(id=123, estado='cancelada')

# Obtener todos los pagos completados de esta rifa
pagos = Payment.objects.filter(
    boletos__rifa=rifa_cancelada,
    estado='completado'
).distinct()

admin = User.objects.get(rol='admin', email='admin@rifatrust.com')

# Crear reembolsos
for pago in pagos:
    # Verificar que no tenga reembolso previo
    if hasattr(pago, 'reembolso'):
        continue
    
    # Crear solicitud de reembolso
    refund = Refund.objects.create(
        pago=pago,
        monto=pago.monto,  # Reembolso total
        motivo='cancelacion',
        razon=f'Rifa "{rifa_cancelada.titulo}" fue cancelada por el organizador',
        procesado_por=admin,
        estado='aprobado'
    )
    
    # Procesar reembolso en Stripe
    stripe_refund = stripe.Refund.create(
        payment_intent=pago.payment_intent_id,
        amount=int(refund.monto * 100)
    )
    
    # Actualizar estados
    refund.estado = 'completado'
    refund.fecha_procesado = timezone.now()
    refund.save()
    
    pago.estado = 'reembolsado'
    pago.save()
    
    # Notificar usuario
    Notification.objects.create(
        usuario=pago.usuario,
        tipo='sistema',
        titulo='Reembolso Procesado',
        mensaje=f'Se ha procesado el reembolso de ${refund.monto:,.2f} por la cancelación de "{rifa_cancelada.titulo}"',
        enlace='/profile/payments/'
    )
```

---

## 🤝 MODELOS DE PATROCINIO

### Modelo: SponsorshipRequest

**Archivo**: `apps/raffles/models.py`

#### Descripción
Solicitud de un sponsor para patrocinar una rifa con un premio adicional. El sponsor ofrece un premio y promociona su marca.

#### Campos Principales

```python
# Relaciones
rifa = ForeignKey(Raffle, CASCADE)
sponsor = ForeignKey(User, CASCADE)

# Premio Ofrecido
nombre_premio_adicional = CharField(200)
descripcion_premio = TextField()
valor_premio = DecimalField(12, 2)
imagen_premio = ImageField('sponsor_prizes/')

# Marca del Sponsor
nombre_marca = CharField(200)
logo_marca = ImageField('sponsor_logos/')
sitio_web = URLField(blank=True)
mensaje_patrocinio = TextField()

# Estado
estado = CharField(20, choices=ESTADO_CHOICES)
# Estados: pendiente, aceptada, rechazada, cancelada

fecha_solicitud = DateTimeField(auto_now_add=True)
fecha_respuesta = DateTimeField(null=True)
motivo_rechazo = TextField(blank=True)
```

#### Workflow

```
Sponsor ve rifa interesante
         │
         ▼
Envía solicitud con premio
         │
         ▼
┌──────────────────┐
│    pendiente     │
└────────┬─────────┘
         │
         ├─── Organizador acepta ──▶ ┌──────────┐
         │                            │ aceptada │
         │                            └────┬─────┘
         │                                 │
         │                                 ▼
         │                            Premio agregado a rifa
         │                            Logo sponsor visible
         │
         └─── Organizador rechaza ──▶ ┌───────────┐
              o Sponsor cancela        │ rechazada │
                                       │ cancelada │
                                       └───────────┘
```

---

### Modelo: OrganizerSponsorRequest

**Archivo**: `apps/raffles/models.py`

#### Descripción
Solicitud inversa: un organizador invita a un sponsor a patrocinar su rifa. El sponsor puede aceptar y proponer un premio.

#### Campos Principales

```python
# Relaciones
rifa = ForeignKey(Raffle, CASCADE)
sponsor = ForeignKey(User, CASCADE)
organizador = ForeignKey(User, CASCADE)

# Invitación
mensaje_invitacion = TextField()
beneficios_ofrecidos = TextField()

# Respuesta del Sponsor (si acepta)
propuesta_premio = CharField(200, blank=True)
propuesta_valor = DecimalField(12, 2, null=True)

# Estado
estado = CharField(20, choices=ESTADO_CHOICES)
fecha_solicitud = DateTimeField(auto_now_add=True)
fecha_respuesta = DateTimeField(null=True)
motivo_rechazo = TextField(blank=True)
```

#### Restricción de Unicidad

```python
class Meta:
    unique_together = ['rifa', 'sponsor']
    # Un organizador solo puede invitar una vez al mismo sponsor por rifa
```

---

## 🏆 MODELO WINNER

### Modelo: Winner (Ganador)

**Archivo**: `apps/raffles/models.py`

#### Descripción
Representa el ganador de una rifa con información del sorteo verificable. Incluye campos para auditoría y verificación transparente.

#### Campos de Sorteo Verificable

```python
# Relaciones
rifa = OneToOneField(Raffle, CASCADE)
# - Una rifa tiene un solo ganador
boleto = OneToOneField(Ticket, CASCADE)
# - Un boleto solo puede ganar una vez

# Información Básica
fecha_sorteo = DateTimeField(auto_now_add=True)
verificado = BooleanField(default=False)
premio_entregado = BooleanField(default=False)
fecha_entrega = DateTimeField(null=True)
notas = TextField(blank=True)

# === CAMPOS DE VERIFICACIÓN DEL SORTEO ===
seed_aleatorio = CharField(64, null=True)
# - Hash SHA256 usado como semilla para generar número aleatorio
# - Ejemplo: "a3d5f7e9b2c4..."

timestamp_sorteo = BigIntegerField(null=True)
# - Unix timestamp exacto del momento del sorteo
# - Ejemplo: 1733097600 (2025-12-01 18:00:00 UTC)

algoritmo = CharField(50, default='SHA256+Timestamp')
# - Algoritmo utilizado para el sorteo
# - Ejemplo: "SHA256+Timestamp+ModuloN"

hash_verificacion = CharField(64, null=True)
# - Hash SHA256 de toda la información del sorteo
# - Permite verificar que no se alteraron los datos

participantes_totales = IntegerField(null=True)
# - Total de boletos pagados al momento del sorteo
# - Usado para verificación posterior

acta_digital = TextField(null=True)
# - Registro completo y auditable del sorteo
# - JSON con todos los detalles
```

#### Ejemplo de Sorteo Verificable

```python
import hashlib
import time
import random
import json

def realizar_sorteo_verificable(rifa):
    """
    Realiza sorteo transparente y verificable.
    """
    # 1. Obtener boletos participantes
    boletos = Ticket.objects.filter(
        rifa=rifa,
        estado='pagado'
    ).order_by('numero_boleto')
    
    total_participantes = boletos.count()
    
    if total_participantes == 0:
        raise ValueError("No hay boletos pagados")
    
    # 2. Generar semilla aleatoria
    timestamp = int(time.time())
    seed_data = f"{rifa.id}-{timestamp}-{random.random()}"
    seed_hash = hashlib.sha256(seed_data.encode()).hexdigest()
    
    # 3. Generar número ganador usando seed
    seed_int = int(seed_hash, 16)
    indice_ganador = seed_int % total_participantes
    boleto_ganador = boletos[indice_ganador]
    
    # 4. Crear acta digital
    acta = {
        'rifa_id': rifa.id,
        'rifa_titulo': rifa.titulo,
        'timestamp_sorteo': timestamp,
        'seed_aleatorio': seed_hash,
        'algoritmo': 'SHA256+Timestamp+ModuloN',
        'participantes_totales': total_participantes,
        'indice_ganador': indice_ganador,
        'numero_ganador': boleto_ganador.numero_boleto,
        'ganador_usuario_id': boleto_ganador.usuario.id,
        'ganador_nombre': boleto_ganador.usuario.nombre,
        'fecha_sorteo_legible': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    }
    
    # 5. Hash de verificación
    acta_json = json.dumps(acta, sort_keys=True)
    hash_verificacion = hashlib.sha256(acta_json.encode()).hexdigest()
    
    # 6. Crear Winner
    winner = Winner.objects.create(
        rifa=rifa,
        boleto=boleto_ganador,
        fecha_sorteo=timezone.now(),
        verificado=False,
        premio_entregado=False,
        seed_aleatorio=seed_hash,
        timestamp_sorteo=timestamp,
        algoritmo='SHA256+Timestamp+ModuloN',
        hash_verificacion=hash_verificacion,
        participantes_totales=total_participantes,
        acta_digital=acta_json
    )
    
    # 7. Actualizar estados
    boleto_ganador.estado = 'ganador'
    boleto_ganador.save()
    
    rifa.estado = 'finalizada'
    rifa.save()
    
    # 8. Notificar ganador
    Notification.objects.create(
        usuario=boleto_ganador.usuario,
        tipo='ganador',
        titulo='🎉 ¡FELICIDADES! Has Ganado',
        mensaje=f'Tu boleto #{boleto_ganador.numero_boleto} ha ganado "{rifa.titulo}". Premio: {rifa.premio_principal}',
        enlace=f'/raffles/{rifa.id}/',
        rifa_relacionada=rifa
    )
    
    return winner
```

---

*Fin de Parte 3*

**Archivos de Documentación Creados:**
1. `DOCUMENTACION_TECNICA.md` - Información general, arquitectura, tecnologías
2. `DOCUMENTACION_MODELOS.md` - User, Profile, Notification, Raffle
3. `DOCUMENTACION_MODELOS_PARTE3.md` - Ticket, Payment, Refund, Sponsorship, Winner

**Siguiente Parte:** Views, Forms y Templates con código comentado línea por línea.
