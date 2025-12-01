# DOCUMENTACIÓN TÉCNICA - PARTE 5
## Views de Raffles - Sistema RifaTrust

---

## 📋 ÍNDICE DE VIEWS RAFFLES

### Vistas Públicas:
1. `home_view` - Página principal
2. `raffles_list_view` - Lista de rifas con filtros
3. `raffle_detail_view` - Detalle de rifa con ruleta

### Dashboards por Rol:
4. `participant_dashboard_view` - Dashboard de participante
5. `organizer_dashboard_view` - Dashboard de organizador
6. `sponsor_dashboard_view` - Dashboard de sponsor

### Gestión de Rifas:
7. `create_raffle_view` - Crear nueva rifa
8. `edit_raffle_view` - Editar rifa
9. `buy_ticket_view` - Comprar boletos

### Sistema de Sorteo:
10. `roulette_view` - Vista de ruleta animada
11. `select_winner_view` - Ejecutar sorteo verificable
12. `acta_sorteo_view` - Generar acta digital

### Sistema de Patrocinios:
13. `create_sponsorship_request_view` - Solicitar patrocinio
14. `accept_sponsorship_request_view` - Aceptar solicitud
15. `reject_sponsorship_request_view` - Rechazar solicitud
16. `browse_sponsors_view` - Buscar sponsors
17. `send_sponsor_invitation_view` - Invitar sponsor

---

## 🔐 FUNCIÓN: generar_sorteo_verificable

### Propósito
Genera un sorteo completamente verificable y auditable usando criptografía SHA256.

### Características de Seguridad

**1. Determinístico**: Misma entrada = mismo resultado
**2. Verificable**: Cualquiera puede validar el sorteo
**3. Inmutable**: No se puede alterar sin cambiar el hash
**4. Transparente**: Toda la información es pública

### Algoritmo (7 Pasos)

```
PASO 1: Capturar Timestamp
    ├─── Usar microsegundos (1/1,000,000 seg)
    └─── Ejemplo: 1701436800000000

PASO 2: Crear Semilla
    ├─── Combinar: timestamp + rifa_id + título + IDs de boletos
    └─── Formato: "1701436800000000|42|iPhone 15|101,102,103"

PASO 3: Hash SHA256 de Semilla
    ├─── Generar hash de 64 caracteres
    └─── Ejemplo: "a3f5e9b2c4d7f1a8e6b9d2c5f8a1e4b7..."

PASO 4: Convertir a Número
    ├─── int(hash, 16) convierte hex a decimal
    └─── Usar como semilla de random()

PASO 5: Selección Determinística
    ├─── random.seed(seed_number)
    └─── random.choice(tickets) → Ganador

PASO 6: Hash de Verificación
    ├─── Combinar: semilla + timestamp + ganador
    └─── SHA256 final para validación

PASO 7: Acta Digital
    └─── Documento legible con toda la información
```

### Código de Ejemplo

```python
# Realizar sorteo
tickets = Ticket.objects.filter(rifa=rifa, estado='pagado')
resultado = generar_sorteo_verificable(rifa, tickets)

# Resultado contiene:
{
    'winning_ticket': Ticket instance,
    'seed_aleatorio': 'a3f5e9b2c4d7...',
    'timestamp_sorteo': 1701436800000000,
    'hash_verificacion': 'e4b7d2c5f8a1...',
    'participantes_totales': 150,
    'acta_digital': 'ACTA DIGITAL DE SORTEO...'
}

# Crear Winner con datos de verificación
winner = Winner.objects.create(
    rifa=rifa,
    boleto=resultado['winning_ticket'],
    seed_aleatorio=resultado['seed_aleatorio'],
    timestamp_sorteo=resultado['timestamp_sorteo'],
    hash_verificacion=resultado['hash_verificacion'],
    participantes_totales=resultado['participantes_totales'],
    acta_digital=resultado['acta_digital'],
    algoritmo='SHA256+Timestamp'
)
```

### Verificación del Sorteo

Cualquier persona puede verificar el sorteo:

```python
# Paso 1: Obtener datos del Winner
winner = Winner.objects.get(rifa_id=42)

# Paso 2: Recrear la semilla
boletos_ids = ','.join(str(t.id) for t in sorted(tickets, key=lambda x: x.id))
seed_string = f"{winner.timestamp_sorteo}|{rifa.id}|{rifa.titulo}|{boletos_ids}"
seed_hash = hashlib.sha256(seed_string.encode('utf-8')).hexdigest()

# Paso 3: Comparar con el seed guardado
assert seed_hash == winner.seed_aleatorio  # ✓ Verificado

# Paso 4: Recrear la selección
seed_number = int(seed_hash, 16)
random.seed(seed_number)
ganador_verificado = random.choice(tickets)

# Paso 5: Comparar ganadores
assert ganador_verificado.id == winner.boleto.id  # ✓ Verificado

# Paso 6: Verificar hash de verificación
verificacion_string = f"{seed_hash}|{winner.timestamp_sorteo}|{winner.boleto.id}|{winner.boleto.numero_boleto}"
hash_verificacion = hashlib.sha256(verificacion_string.encode('utf-8')).hexdigest()
assert hash_verificacion == winner.hash_verificacion  # ✓ Verificado
```

---

## 🏠 VISTA: home_view

### Información Básica

**URL**: `/`  
**Método**: GET  
**Autenticación**: No requerida (pública)

### Propósito
Página principal del sitio mostrando rifas destacadas.

### Lógica

```python
def home_view(request):
    # Obtener últimas 6 rifas activas
    raffles_activas = Raffle.objects.filter(
        estado='activa'
    ).order_by('-fecha_creacion')[:6]
    
    return render(request, 'home.html', {
        'raffles': raffles_activas
    })
```

### Filtros Aplicados

- **Estado**: Solo `'activa'` (rifas visibles para compra)
- **Orden**: `-fecha_creacion` (más recientes primero)
- **Límite**: 6 rifas (optimal para UI)

---

## 📋 VISTA: raffles_list_view

### Información Básica

**URL**: `/raffles/?estado=<filtro>`  
**Método**: GET  
**Autenticación**: No requerida (pública)

### Query Parameters

| Parámetro | Valores | Descripción |
|-----------|---------|-------------|
| `estado` | `activa` | Rifas activas (default) |
| | `finalizada` | Rifas finalizadas con ganador |
| | `todas` | Activas + finalizadas |

### Estados Excluidos

Los siguientes estados **NO** son visibles públicamente:

- `borrador`: Solo visible para el organizador
- `pendiente_aprobacion`: Solo visible para admins
- `aprobada`: Solo visible para el organizador (antes de activar)
- `cancelada`: Solo visible en panel admin
- `pausada`: Solo visible para admin

### Lógica de Filtrado

```python
def raffles_list_view(request):
    estado_filter = request.GET.get('estado', 'activa')
    
    if estado_filter == 'todas':
        raffles = Raffle.objects.filter(
            estado__in=['activa', 'finalizada']
        ).order_by('-fecha_creacion')
    
    elif estado_filter == 'finalizada':
        raffles = Raffle.objects.filter(
            estado='finalizada'
        ).order_by('-fecha_sorteo')
    
    else:  # 'activa' por defecto
        raffles = Raffle.objects.filter(
            estado='activa'
        ).order_by('-fecha_creacion')
    
    return render(request, 'raffles/list.html', {
        'raffles': raffles,
        'estado_filter': estado_filter
    })
```

### Ejemplos de URLs

```
/raffles/                    → Rifas activas
/raffles/?estado=activa      → Rifas activas (explícito)
/raffles/?estado=finalizada  → Rifas finalizadas
/raffles/?estado=todas       → Todas las públicas
```

---

## 🎫 VISTA: raffle_detail_view

### Información Básica

**URL**: `/raffles/<pk>/`  
**Método**: GET  
**Autenticación**: No requerida (pública)

### Propósito
Muestra el detalle completo de una rifa incluyendo:
- Información de la rifa (premio, precio, fechas)
- Progreso de venta de boletos
- Lista de participantes
- Ruleta de sorteo (si aplica)
- Sponsors aceptados y sus premios
- Ganador (si ya se sorteó)

### Lógica Compleja: Ventana de Animación

**Problema**: La ruleta animada debe mostrarse solo durante un periodo limitado.

**Solución**: Ventana de 3 minutos desde la hora del sorteo.

```python
from datetime import timedelta

# Hora del sorteo configurada
raffle.fecha_sorteo = datetime(2025, 12, 1, 18, 0, 0)  # 18:00

# Ventana de animación: 18:00 a 18:03
tiempo_limite_sorteo = raffle.fecha_sorteo + timedelta(minutes=3)

# Verificar si estamos en la ventana
now = timezone.now()
is_live_draw = (
    raffle.fecha_sorteo <= now <= tiempo_limite_sorteo 
    and not has_winner
)

# Mostrar ruleta solo en ventana de animación
show_roulette = (
    is_live_draw 
    and raffle.estado == 'activa' 
    and sold_tickets > 0
)

# Después de la ventana, mostrar botón sin animación
show_draw_button = (
    now >= raffle.fecha_sorteo 
    and not has_winner 
    and raffle.estado == 'activa' 
    and sold_tickets > 0
)
```

### Estados de la Rifa en Detail View

```
ANTES de fecha_sorteo:
    ├─── show_roulette = False
    ├─── show_draw_button = False
    └─── Mostrar: Cuenta regresiva hasta sorteo

DURANTE ventana (fecha_sorteo a fecha_sorteo + 3min):
    ├─── show_roulette = True (si no hay ganador)
    ├─── Mostrar: Ruleta animada
    └─── Auto-ejecutar sorteo al llegar a la hora

DESPUÉS de ventana (+ 3 min):
    ├─── show_roulette = False
    ├─── show_draw_button = True (si no hay ganador)
    └─── Mostrar: Botón "Ejecutar Sorteo Ahora"

CON GANADOR:
    ├─── show_roulette = False
    ├─── show_draw_button = False
    ├─── raffle.estado = 'finalizada'
    └─── Mostrar: Tarjeta de ganador con datos
```

### Datos para Ruleta (JavaScript)

```python
# Obtener boletos pagados ordenados por ID
sold_tickets_qs = Ticket.objects.filter(
    rifa=raffle, 
    estado='pagado'
).select_related('usuario').order_by('id')

# Preparar datos para JavaScript
tickets_data = [
    {
        'id': ticket.id,
        'numero_boleto': ticket.numero_boleto,
        'nombre': ticket.usuario.nombre,
        'email': ticket.usuario.email
    }
    for ticket in sold_tickets_qs
]

# Serializar a JSON para template
tickets_json = json.dumps(tickets_data)

# Convertir fecha_sorteo a timestamp para countdown
fecha_sorteo_timestamp = int(raffle.fecha_sorteo.timestamp() * 1000)
```

### Sponsors Aceptados

```python
from .models import SponsorshipRequest

# Obtener sponsors con estado 'aceptada'
sponsors_aceptados = SponsorshipRequest.objects.filter(
    rifa=raffle,
    estado='aceptada'
).select_related('sponsor')

# En el template:
{% for sponsorship in sponsors_aceptados %}
    <div class="sponsor-prize">
        <img src="{{ sponsorship.logo_marca.url }}">
        <h4>{{ sponsorship.nombre_premio_adicional }}</h4>
        <p>{{ sponsorship.descripcion_premio }}</p>
        <span>Valor: ${{ sponsorship.valor_premio|floatformat:0 }}</span>
    </div>
{% endfor %}
```

### Permisos del Organizador

```python
# Verificar si el usuario es el organizador
is_organizer = (
    request.user.is_authenticated 
    and request.user == raffle.organizador
)

# En el template:
{% if is_organizer %}
    <div class="organizer-controls">
        <a href="{% url 'raffles:edit' raffle.id %}">Editar Rifa</a>
        {% if show_draw_button %}
            <button onclick="ejecutarSorteo()">Ejecutar Sorteo Ahora</button>
        {% endif %}
    </div>
{% endif %}
```

---

## 👤 VISTA: participant_dashboard_view

### Información Básica

**URL**: `/participant-dashboard/`  
**Método**: GET  
**Autenticación**: Requerida  
**Rol**: Participante (o cualquier usuario autenticado)

### Propósito
Dashboard personalizado para participantes mostrando su actividad en el sistema.

### Estadísticas Mostradas

**1. Mis Boletos**
```python
mis_boletos = Ticket.objects.filter(
    usuario=user
).select_related('rifa').order_by('-fecha_compra')[:10]

boletos_pagados = mis_boletos.filter(estado='pagado')
total_boletos = boletos_pagados.count()
```

**2. Total Gastado**
```python
total_gastado = boletos_pagados.aggregate(
    total=Sum('rifa__precio_boleto')
)['total'] or 0
```

**3. Rifas en las que Participo**
```python
rifas_participando = Raffle.objects.filter(
    boletos__usuario=user,
    boletos__estado='pagado',
    estado='activa'
).distinct().annotate(
    mis_boletos_count=Count('boletos', 
        filter=Q(boletos__usuario=user, boletos__estado='pagado')
    )
)
```

**4. Rifas Próximas a Finalizar**
```python
from datetime import datetime, timedelta

fecha_limite = datetime.now() + timedelta(days=7)
rifas_proximas = Raffle.objects.filter(
    estado='activa',
    fecha_sorteo__lte=fecha_limite,
    fecha_sorteo__gte=datetime.now()
).order_by('fecha_sorteo')[:5]
```

**5. Rifas Ganadas**
```python
rifas_ganadas = Winner.objects.filter(
    boleto__usuario=user
).count()
```

**6. Boletos Activos**
```python
boletos_activos = boletos_pagados.filter(
    rifa__estado='activa'
).count()
```

### Context Completo

```python
context = {
    'mis_boletos': mis_boletos[:10],          # Últimos 10
    'total_boletos': total_boletos,            # Total comprados
    'total_gastado': total_gastado,            # Suma de gastos
    'rifas_participando': rifas_participando,  # Rifas activas
    'rifas_proximas': rifas_proximas,          # Próximas a sortear
    'rifas_ganadas': rifas_ganadas,            # Total ganadas
    'boletos_activos': boletos_activos,        # En rifas activas
}
```

---

## 🎯 VISTA: organizer_dashboard_view

### Información Básica

**URL**: `/organizer-dashboard/`  
**Método**: GET  
**Autenticación**: Requerida  
**Roles Permitidos**: `organizador`, `admin`

### Validación de Rol

```python
if request.user.rol not in ['organizador', 'admin']:
    messages.error(request, 'No tienes permisos para acceder a esta página.')
    return redirect('dashboard')
```

### Estadísticas Principales

**1. Mis Rifas con Estadísticas**
```python
mis_rifas = Raffle.objects.filter(
    organizador=request.user
).annotate(
    total_vendidos=Count('boletos', 
        filter=Q(boletos__estado='pagado')
    ),
    total_participantes=Count('boletos__usuario', 
        filter=Q(boletos__estado='pagado'), 
        distinct=True
    )
).order_by('-fecha_creacion')
```

**2. Ingresos Totales**
```python
total_ingresos = sum(
    rifa.precio_boleto * rifa.boletos_vendidos 
    for rifa in mis_rifas
)
```

**3. Rifas por Estado**
```python
rifas_activas = mis_rifas.filter(estado='activa')
rifas_finalizadas = mis_rifas.filter(estado='finalizada')
rifas_canceladas = mis_rifas.filter(estado='cancelada')
```

**4. Rifa Más Vendida**
```python
rifa_mas_vendida = mis_rifas.filter(
    estado='activa'
).order_by('-boletos_vendidos').first()
```

**5. Rifas Próximas a Sortear**
```python
from datetime import datetime, timedelta

fecha_limite = datetime.now() + timedelta(days=3)
rifas_proximas_sorteo = rifas_activas.filter(
    fecha_sorteo__lte=fecha_limite,
    fecha_sorteo__gte=datetime.now()
).order_by('fecha_sorteo')
```

**6. Total de Participantes Únicos**
```python
total_participantes = Ticket.objects.filter(
    rifa__organizador=request.user,
    estado='pagado'
).values('usuario').distinct().count()
```

**7. Ventas Recientes (Últimos 7 Días)**
```python
fecha_inicio = datetime.now() - timedelta(days=7)
ventas_recientes = Ticket.objects.filter(
    rifa__organizador=request.user,
    estado='pagado',
    fecha_compra__gte=fecha_inicio
).select_related('rifa', 'usuario').order_by('-fecha_compra')[:10]
```

### Sistema de Patrocinios

**Solicitudes Recibidas (de Sponsors)**
```python
from .models import SponsorshipRequest

solicitudes_patrocinio = SponsorshipRequest.objects.filter(
    rifa__organizador=request.user
).select_related('rifa', 'sponsor').order_by('-fecha_solicitud')[:10]

total_solicitudes_patrocinio = SponsorshipRequest.objects.filter(
    rifa__organizador=request.user
).count()

solicitudes_pendientes = SponsorshipRequest.objects.filter(
    rifa__organizador=request.user, 
    estado='pendiente'
).count()
```

**Invitaciones Enviadas (a Sponsors)**
```python
from .models import OrganizerSponsorRequest

invitaciones_enviadas = OrganizerSponsorRequest.objects.filter(
    organizador=request.user
).select_related('rifa', 'sponsor').order_by('-fecha_solicitud')[:10]

total_invitaciones_enviadas = OrganizerSponsorRequest.objects.filter(
    organizador=request.user
).count()

invitaciones_pendientes = OrganizerSponsorRequest.objects.filter(
    organizador=request.user, 
    estado='pendiente'
).count()
```

---

## 💼 VISTA: sponsor_dashboard_view

### Información Básica

**URL**: `/sponsor-dashboard/`  
**Método**: GET  
**Autenticación**: Requerida  
**Roles Permitidos**: `sponsor`, `admin`

### Validación de Rol

```python
if request.user.rol not in ['sponsor', 'admin']:
    messages.error(request, 'No tienes permisos para acceder a esta página.')
    return redirect('dashboard')
```

### Estadísticas de Solicitudes

**Mis Solicitudes Enviadas**
```python
mis_solicitudes = SponsorshipRequest.objects.filter(
    sponsor=request.user
).select_related('rifa').order_by('-fecha_solicitud')

total_solicitudes = mis_solicitudes.count()
solicitudes_pendientes = mis_solicitudes.filter(estado='pendiente').count()
solicitudes_aceptadas = mis_solicitudes.filter(estado='aceptada').count()
solicitudes_rechazadas = mis_solicitudes.filter(estado='rechazada').count()
```

**Invitaciones Recibidas**
```python
invitaciones_recibidas = OrganizerSponsorRequest.objects.filter(
    sponsor=request.user
).select_related('rifa', 'organizador').order_by('-fecha_solicitud')[:10]

total_invitaciones = invitaciones_recibidas.count()
invitaciones_pendientes = OrganizerSponsorRequest.objects.filter(
    sponsor=request.user, 
    estado='pendiente'
).count()
```

### Oportunidades de Patrocinio

**Rifas Disponibles**
```python
rifas_disponibles = Raffle.objects.filter(
    estado='activa'
).annotate(
    total_vendidos=Count('boletos', filter=Q(boletos__estado='pagado')),
    porcentaje_calc=ExpressionWrapper(
        F('boletos_vendidos') * 100.0 / F('total_boletos'),
        output_field=FloatField()
    )
).order_by('-fecha_creacion')[:10]
```

**Rifas Populares (Top 5)**
```python
rifas_populares = Raffle.objects.filter(
    estado='activa'
).annotate(
    total_participantes=Count('boletos__usuario', 
        filter=Q(boletos__estado='pagado'), 
        distinct=True
    )
).order_by('-total_participantes')[:5]
```

**Rifas Próximas a Finalizar**
```python
fecha_limite = datetime.now() + timedelta(days=5)
rifas_proximas = Raffle.objects.filter(
    estado='activa',
    fecha_sorteo__lte=fecha_limite,
    fecha_sorteo__gte=datetime.now()
).order_by('fecha_sorteo')[:5]
```

**Oportunidades (Baja Venta, Alta Calidad)**
```python
# Rifas con menos del 50% vendido
oportunidades_patrocinio = Raffle.objects.filter(
    estado='activa'
).annotate(
    total_vendidos=Count('boletos', filter=Q(boletos__estado='pagado')),
    porcentaje_calc=ExpressionWrapper(
        F('total_vendidos') * 100.0 / F('total_boletos'),
        output_field=FloatField()
    )
).filter(
    porcentaje_calc__lt=50  # Menos del 50% vendido
).order_by('porcentaje_calc')[:5]
```

### Estadísticas del Sistema

```python
total_rifas_activas = Raffle.objects.filter(estado='activa').count()

total_participantes_sistema = Ticket.objects.filter(
    estado='pagado'
).values('usuario').distinct().count()

total_organizadores = User.objects.filter(rol='organizador').count()
```

---

*Continúa en siguiente sección...*

**Próxima Parte**: Gestión de rifas (create, edit, buy_ticket) y sistema de sorteos

**Archivos Comentados Hasta Ahora**:
- ✅ `apps/payments/views.py` - 100% documentado
- ✅ `apps/users/views.py` - 100% documentado
- 🔄 `apps/raffles/views.py` - 40% documentado (función verificable + vistas principales)
