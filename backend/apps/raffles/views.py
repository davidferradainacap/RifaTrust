# ============================================================================
# MÓDULO DE RIFAS - VIEWS
# ============================================================================
# Gestiona el ciclo completo de rifas desde creación hasta sorteo
# Incluye dashboards personalizados por rol (participante, organizador, sponsor)
# Sistema de sorteo verificable con SHA256+Timestamp
# Integración con sistema de patrocinios
# ============================================================================

# === IMPORTACIONES DJANGO CORE ===
from django.shortcuts import render, redirect, get_object_or_404
# - render: renderiza templates
# - redirect: redirige a otra vista
# - get_object_or_404: obtiene objeto o 404

from django.contrib.auth.decorators import login_required
# - Decorador para proteger vistas que requieren autenticación

from django.contrib import messages
# - Sistema de mensajes flash para feedback al usuario

from django.db.models import Count, Sum, Q, F, FloatField, ExpressionWrapper
# - Count: contar registros relacionados
# - Sum: sumar valores de campos
# - Q: consultas complejas con OR, AND, NOT
# - F: referencias a campos en la base de datos
# - FloatField: tipo de campo decimal
# - ExpressionWrapper: expresiones aritméticas en queries

# === IMPORTACIONES DE MODELOS ===
from .models import Raffle, Ticket, Winner
# - Raffle: modelo de rifas
# - Ticket: boletos de rifas
# - Winner: ganadores de sorteos

from .forms import RaffleForm
# - Formulario para crear/editar rifas

from apps.users.models import User, Notification
# - User: modelo de usuarios
# - Notification: sistema de notificaciones

# === IMPORTACIONES DJANGO HTTP ===
from django.http import JsonResponse
# - Respuestas JSON para AJAX

from django.views.decorators.http import require_http_methods
# - Decorador para restringir métodos HTTP (GET, POST, etc.)

from django.utils import timezone
# - Manejo de fechas con timezone awareness

# === IMPORTACIONES PYTHON STANDARD LIBRARY ===
import uuid
# - Generador de identificadores únicos (código QR de boletos)

import hashlib
# - Algoritmos de hash criptográficos (SHA256 para sorteos verificables)

import time
# - Manejo de timestamps para sorteos

import random
# - Generador de números aleatorios (con semilla para determinismo)

import json
# - Serialización de datos para JavaScript

# ============================================================================
# FUNCIÓN: generar_sorteo_verificable
# ============================================================================
# Genera un sorteo verificable y auditable usando SHA256+Timestamp
#
# Propósito:
# - Garantizar transparencia en el proceso de sorteo
# - Permitir verificación posterior del resultado
# - Prevenir manipulación del sorteo
#
# Algoritmo:
# 1. Capturar timestamp en microsegundos (precisión máxima)
# 2. Combinar datos inmutables: timestamp + rifa_id + título + IDs de boletos
# 3. Generar hash SHA256 como semilla aleatoria
# 4. Usar semilla para selección determinística del ganador
# 5. Generar hash de verificación del proceso completo
# 6. Crear acta digital con toda la información
#
# Características de seguridad:
# - Determinístico: misma entrada = mismo resultado
# - Verificable: cualquiera puede validar el sorteo
# - Inmutable: no se puede alterar sin cambiar el hash
# - Transparente: toda la información es pública
#
# Parámetros:
# - raffle: Instancia de Raffle (la rifa a sortear)
# - tickets: Lista de Ticket instances (boletos participantes)
#
# Retorna:
# - dict con: winning_ticket, seed_aleatorio, timestamp_sorteo,
#             hash_verificacion, participantes_totales, acta_digital
# ============================================================================
def generar_sorteo_verificable(raffle, tickets):
    """
    Genera un sorteo verificable con aleatoriedad transparente
    """
    # === PASO 1: TIMESTAMP DE MÁXIMA PRECISIÓN ===
    # Usar microsegundos (millonésimas de segundo) para unicidad
    # Ejemplo: 1701436800000000 (6 dígitos más que segundos)
    # Esto hace prácticamente imposible predecir el momento exacto
    timestamp = int(time.time() * 1000000)  # Microsegundos

    # === PASO 2: CREAR SEMILLA COMBINANDO DATOS INMUTABLES ===
    # Ordenar boletos por ID para consistencia
    # sorted() asegura que el orden siempre sea el mismo
    boletos_ids = ','.join(str(t.id) for t in sorted(tickets, key=lambda x: x.id))

    # Combinar en string separado por pipes |
    # Formato: "timestamp|rifa_id|titulo|id1,id2,id3..."
    # Ejemplo: "1701436800000000|42|iPhone 15|101,102,103"
    seed_string = f"{timestamp}|{raffle.id}|{raffle.titulo}|{boletos_ids}"

    # === PASO 3: GENERAR HASH SHA256 DE LA SEMILLA ===
    # SHA256 produce un hash de 64 caracteres hexadecimales
    # Ejemplo: "a3f5e9b2c4d7f1a8e6b9d2c5f8a1e4b7..."
    # Es prácticamente imposible encontrar dos inputs con mismo hash
    seed_hash = hashlib.sha256(seed_string.encode('utf-8')).hexdigest()

    # === PASO 4: CONVERTIR HASH A NÚMERO PARA RANDOM ===
    # El hash hexadecimal se convierte a entero
    # int('a3f5...', 16) convierte de base 16 a base 10
    # Este número se usa como semilla para random
    seed_number = int(seed_hash, 16)

    # === PASO 5: SELECCIÓN DETERMINÍSTICA DEL GANADOR ===
    # random.seed() inicializa el generador con la semilla
    # Con la misma semilla, random.choice() siempre retorna el mismo elemento
    # Esto permite verificar que el sorteo fue justo
    random.seed(seed_number)
    winning_ticket = random.choice(tickets)

    # === PASO 6: HASH DE VERIFICACIÓN DEL PROCESO COMPLETO ===
    # Combinar todos los datos del sorteo en un string
    # Incluye: semilla + timestamp + id del ganador + número de boleto
    verificacion_string = f"{seed_hash}|{timestamp}|{winning_ticket.id}|{winning_ticket.numero_boleto}"

    # Generar hash final de verificación
    # Este hash permite validar que ningún dato fue alterado
    hash_verificacion = hashlib.sha256(verificacion_string.encode('utf-8')).hexdigest()

    # === PASO 7: GENERAR ACTA DIGITAL ===
    # Documento legible con toda la información del sorteo
    # Puede ser firmado digitalmente o impreso para auditoría
    acta = f"""ACTA DIGITAL DE SORTEO - {raffle.titulo}
ID Rifa: {raffle.id}
Fecha sorteo: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
Timestamp: {timestamp}
Participantes: {len(tickets)}
Algoritmo: SHA256+Timestamp
Semilla: {seed_hash}
Hash Verificación: {hash_verificacion}
Ganador: {winning_ticket.usuario.nombre} - Boleto #{winning_ticket.numero_boleto}
"""

    # === RETORNAR RESULTADO COMPLETO ===
    return {
        'winning_ticket': winning_ticket,          # Boleto ganador
        'seed_aleatorio': seed_hash,                # Semilla SHA256
        'timestamp_sorteo': timestamp,              # Timestamp en microsegundos
        'hash_verificacion': hash_verificacion,     # Hash de verificación
        'participantes_totales': len(tickets),      # Total de participantes
        'acta_digital': acta                        # Documento del sorteo
    }

# ============================================================================
# VISTA: home_view
# ============================================================================
# Página principal del sitio con rifas destacadas
#
# URL: /
# Método: GET
# Autenticación: No requerida (pública)
#
# Muestra:
# - Las 6 rifas más recientes en estado 'activa'
# - Ordenadas por fecha de creación (más nuevas primero)
# ============================================================================
def home_view(request):
    # === OBTENER RIFAS ACTIVAS ===
    # Filtro: estado='activa' (rifas visibles para compra)
    # Order: -fecha_creacion (más recientes primero, - indica DESC)
    # Slice: [:6] limita a las primeras 6 rifas
    raffles_activas = Raffle.objects.filter(
        estado='activa'
    ).order_by('-fecha_creacion')[:6]

    # Renderizar home con rifas destacadas
    return render(request, 'home.html', {'raffles': raffles_activas})

# ============================================================================
# VISTA: raffles_list_view
# ============================================================================
# Lista de rifas con filtros por estado
#
# URL: /raffles/?estado=<filtro>
# Método: GET
# Autenticación: No requerida (pública)
#
# Query Parameters:
# - estado: Filtro de estado de rifas
#   * 'activa': Solo rifas activas (default)
#   * 'finalizada': Solo rifas finalizadas
#   * 'todas': Rifas activas y finalizadas
#
# Estados excluidos de vistas públicas:
# - 'borrador': Solo visible para organizador
# - 'pendiente_aprobacion': Solo visible para admin
# - 'aprobada': Solo visible para organizador
# - 'cancelada': Solo visible en panel admin
# ============================================================================
def raffles_list_view(request):
    # === PASO 1: OBTENER FILTRO DESDE URL ===
    # GET parameter 'estado' con valor default 'activa'
    # Ejemplo: /raffles/?estado=finalizada
    estado_filter = request.GET.get('estado', 'activa')

    # === PASO 2: FILTRAR RIFAS SEGÚN ESTADO ===
    if estado_filter == 'todas':
        # Mostrar activas y finalizadas
        # estado__in: filtro OR en Django
        # order_by('-fecha_creacion'): más recientes primero
        raffles = Raffle.objects.filter(
            estado__in=['activa', 'finalizada']
        ).order_by('-fecha_creacion')

    elif estado_filter == 'finalizada':
        # Solo rifas finalizadas
        # order_by('-fecha_sorteo'): sorteos más recientes primero
        raffles = Raffle.objects.filter(
            estado='finalizada'
        ).order_by('-fecha_sorteo')

    else:  # 'activa' por defecto
        # Solo rifas activas (disponibles para compra)
        # order_by('-fecha_creacion'): más nuevas primero
        raffles = Raffle.objects.filter(
            estado='activa'
        ).order_by('-fecha_creacion')

    # === PASO 3: PREPARAR CONTEXTO ===
    context = {
        'raffles': raffles,              # QuerySet de rifas filtradas
        'estado_filter': estado_filter,  # Filtro activo (para mantener en UI)
    }

    return render(request, 'raffles/list.html', context)

def raffle_detail_view(request, pk):
    import logging
    import json
    logger = logging.getLogger(__name__)
    
    # Inicializar variables por defecto para evitar errores
    sold_tickets = 0
    available_tickets = 0
    progress_percentage = 0
    tickets_data = []
    tickets_json = '[]'
    sold_tickets_qs = None
    sponsors_aceptados = []
    
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        logger.info(f"Accediendo a detalle de rifa ID: {pk}")
        raffle = get_object_or_404(Raffle, pk=pk)
        logger.info(f"Rifa encontrada: {raffle.titulo}, Estado: {raffle.estado}")

        # Validar campos requeridos
        if not raffle.total_boletos or raffle.total_boletos <= 0:
            logger.warning(f"Rifa {pk} tiene total_boletos inválido: {raffle.total_boletos}")
            raffle.total_boletos = 100  # Valor por defecto

        # Tickets sold - ORDENAR por ID para mantener consistencia con la ruleta
        try:
            sold_tickets_qs = Ticket.objects.filter(rifa=raffle, estado='pagado').select_related('usuario').order_by('id')
            sold_tickets = sold_tickets_qs.count()
            available_tickets = raffle.total_boletos - sold_tickets
            progress_percentage = int((sold_tickets / raffle.total_boletos) * 100) if raffle.total_boletos > 0 else 0
            logger.info(f"Tickets vendidos: {sold_tickets}/{raffle.total_boletos}")
        except Exception as e:
            logger.error(f"Error obteniendo tickets: {str(e)}", exc_info=True)
            sold_tickets_qs = Ticket.objects.none()

        # Check if user is organizer (verificar autenticación primero)
        is_organizer = False
        if request.user.is_authenticated:
            is_organizer = request.user == raffle.organizador
            logger.info(f"Usuario autenticado: {request.user.email}, Es organizador: {is_organizer}")
        else:
            logger.info("Usuario no autenticado")

        # Check if draw time has passed
        now = timezone.now()
        is_past_draw_time = now > raffle.fecha_sorteo

        # Verificar si ya llegó la hora del sorteo y aún no hay ganador
        has_winner = False
        try:
            has_winner = Winner.objects.filter(rifa=raffle).exists()
        except Exception as e:
            logger.warning(f"Error verificando ganador: {str(e)}")

        # Si hay ganador pero la rifa sigue activa, actualizarla a finalizada
        if has_winner and raffle.estado == 'activa':
            raffle.estado = 'finalizada'
            raffle.save()

        # VENTANA DE ANIMACIÓN: Solo 3 minutos para mostrar la ruleta animada
        tiempo_limite_sorteo = raffle.fecha_sorteo + timedelta(minutes=3)
        is_live_draw = raffle.fecha_sorteo <= now <= tiempo_limite_sorteo and not has_winner

        # La ruleta ANIMADA solo se muestra durante los primeros 3 minutos
        show_roulette = is_live_draw and raffle.estado == 'activa' and sold_tickets > 0
        show_draw_button = now >= raffle.fecha_sorteo and not has_winner and raffle.estado == 'activa' and sold_tickets > 0

        # Prepare tickets data for roulette
        try:
            if sold_tickets_qs and sold_tickets_qs.exists():
                tickets_data = []
                for ticket in sold_tickets_qs:
                    try:
                        tickets_data.append({
                            'id': ticket.id,
                            'numero_boleto': ticket.numero_boleto,
                            'nombre': ticket.usuario.nombre if ticket.usuario else 'Usuario',
                            'email': ticket.usuario.email if ticket.usuario else 'N/A'
                        })
                    except Exception as ticket_error:
                        logger.error(f"Error procesando ticket {ticket.id}: {str(ticket_error)}")
                        continue
                logger.info(f"Datos de {len(tickets_data)} tickets preparados")
        except Exception as e:
            logger.error(f"Error preparando datos de tickets: {str(e)}", exc_info=True)
            tickets_data = []

        # Convert fecha_sorteo to timestamp (milliseconds since epoch) for JavaScript
        fecha_sorteo_timestamp = 0
        try:
            if raffle.fecha_sorteo:
                fecha_sorteo_timestamp = int(raffle.fecha_sorteo.timestamp() * 1000)
        except Exception as e:
            logger.error(f"Error convirtiendo fecha_sorteo: {str(e)}", exc_info=True)
            
        tickets_json = json.dumps(tickets_data) if tickets_data else '[]'

        # Obtener sponsors aceptados para mostrar sus premios adicionales
        sponsors_aceptados = []
        try:
            from .models import SponsorshipRequest
            sponsors_aceptados = list(SponsorshipRequest.objects.filter(
                rifa=raffle,
                estado='aceptada'
            ).select_related('sponsor'))
            logger.info(f"Sponsors aceptados: {len(sponsors_aceptados)}")
        except ImportError as e:
            logger.warning(f"SponsorshipRequest model no disponible: {str(e)}")
        except Exception as e:
            logger.error(f"Error obteniendo sponsors: {str(e)}", exc_info=True)

        # Asegurar que sold_tickets_qs no sea None
        if sold_tickets_qs is None:
            sold_tickets_qs = Ticket.objects.none()

        context = {
            'raffle': raffle,
            'sold_tickets': sold_tickets,
            'available_tickets': available_tickets,
            'progress_percentage': progress_percentage,
            'sold_tickets_list': tickets_data,
            'tickets_json': tickets_json,
            'show_roulette': show_roulette,
            'show_draw_button': show_draw_button,
            'is_organizer': is_organizer,
            'is_past_draw_time': is_past_draw_time,
            'is_live_draw': is_live_draw,
            'has_winner': has_winner,
            'fecha_sorteo_timestamp': fecha_sorteo_timestamp,
            'tickets': sold_tickets_qs,
            'sponsors_aceptados': sponsors_aceptados,
        }

        logger.info(f"Renderizando template detail.html con {len(tickets_data)} tickets")
        return render(request, 'raffles/detail.html', context)
        
    except Raffle.DoesNotExist:
        logger.error(f"Rifa no encontrada: ID={pk}")
        from django.contrib import messages
        messages.error(request, f'La rifa #{pk} no existe.')
        return redirect('raffles:raffle_list')
    except Exception as e:
        logger.error(f"ERROR CRÍTICO en raffle_detail_view (pk={pk}): {str(e)}", exc_info=True)
        logger.error(f"Tipo de error: {type(e).__name__}")
        from django.contrib import messages
        messages.error(request, f'Error al cargar los detalles de la rifa: {str(e)}')
        return redirect('raffles:raffle_list')

@login_required
def participant_dashboard_view(request):
    from datetime import datetime, timedelta
    user = request.user

    # Boletos del usuario
    mis_boletos = Ticket.objects.filter(usuario=user).select_related('rifa').order_by('-fecha_compra')
    boletos_pagados = mis_boletos.filter(estado='pagado')

    # Total gastado
    total_gastado = boletos_pagados.aggregate(
        total=Sum('rifa__precio_boleto')
    )['total'] or 0

    # Rifas únicas en las que participa
    rifas_participando = Raffle.objects.filter(
        boletos__usuario=user,
        boletos__estado='pagado',
        estado='activa'
    ).distinct().annotate(
        mis_boletos_count=Count('boletos', filter=Q(boletos__usuario=user, boletos__estado='pagado'))
    )

    # Rifas próximas a finalizar (próximos 7 días)
    fecha_limite = datetime.now() + timedelta(days=7)
    rifas_proximas = Raffle.objects.filter(
        estado='activa',
        fecha_sorteo__lte=fecha_limite,
        fecha_sorteo__gte=datetime.now()
    ).order_by('fecha_sorteo')[:5]

    # Rifas ganadas (a través del modelo Winner)
    rifas_ganadas = Winner.objects.filter(
        boleto__usuario=user
    ).count()

    context = {
        'mis_boletos': mis_boletos[:10],  # Últimos 10 boletos
        'total_boletos': boletos_pagados.count(),
        'total_gastado': total_gastado,
        'rifas_participando': rifas_participando,
        'rifas_proximas': rifas_proximas,
        'rifas_ganadas': rifas_ganadas,
        'boletos_activos': boletos_pagados.filter(rifa__estado='activa').count(),
    }
    return render(request, 'raffles/participant_dashboard.html', context)

@login_required
def organizer_dashboard_view(request):
    from datetime import datetime, timedelta
    from .models import SponsorshipRequest, OrganizerSponsorRequest

    if request.user.rol not in ['organizador', 'admin']:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard')

    # Rifas del organizador con estadísticas
    mis_rifas = Raffle.objects.filter(organizador=request.user).annotate(
        total_vendidos=Count('boletos', filter=Q(boletos__estado='pagado')),
        total_participantes=Count('boletos__usuario', filter=Q(boletos__estado='pagado'), distinct=True)
    ).order_by('-fecha_creacion')

    # Ingresos totales
    total_ingresos = sum(
        rifa.precio_boleto * rifa.boletos_vendidos for rifa in mis_rifas
    )

    # Rifas por estado
    rifas_activas = mis_rifas.filter(estado='activa')
    rifas_finalizadas = mis_rifas.filter(estado='finalizada')
    rifas_canceladas = mis_rifas.filter(estado='cancelada')

    # Rifa con más ventas
    rifa_mas_vendida = mis_rifas.filter(estado='activa').order_by('-boletos_vendidos').first()

    # Rifas próximas a sortear (próximos 3 días)
    fecha_limite = datetime.now() + timedelta(days=3)
    rifas_proximas_sorteo = rifas_activas.filter(
        fecha_sorteo__lte=fecha_limite,
        fecha_sorteo__gte=datetime.now()
    ).order_by('fecha_sorteo')

    # Total de participantes únicos
    total_participantes = Ticket.objects.filter(
        rifa__organizador=request.user,
        estado='pagado'
    ).values('usuario').distinct().count()

    # Ventas recientes (últimos 7 días)
    fecha_inicio = datetime.now() - timedelta(days=7)
    ventas_recientes = Ticket.objects.filter(
        rifa__organizador=request.user,
        estado='pagado',
        fecha_compra__gte=fecha_inicio
    ).select_related('rifa', 'usuario').order_by('-fecha_compra')[:10]

    # Solicitudes de patrocinio recibidas (de sponsors)
    solicitudes_patrocinio = SponsorshipRequest.objects.filter(
        rifa__organizador=request.user
    ).select_related('rifa', 'sponsor').order_by('-fecha_solicitud')[:10]

    # Estadísticas de solicitudes recibidas
    total_solicitudes_patrocinio = SponsorshipRequest.objects.filter(rifa__organizador=request.user).count()
    solicitudes_pendientes = SponsorshipRequest.objects.filter(rifa__organizador=request.user, estado='pendiente').count()

    # Invitaciones enviadas a sponsors
    invitaciones_enviadas = OrganizerSponsorRequest.objects.filter(
        organizador=request.user
    ).select_related('rifa', 'sponsor').order_by('-fecha_solicitud')[:10]

    # Estadísticas de invitaciones enviadas
    total_invitaciones_enviadas = OrganizerSponsorRequest.objects.filter(organizador=request.user).count()
    invitaciones_pendientes = OrganizerSponsorRequest.objects.filter(organizador=request.user, estado='pendiente').count()

    context = {
        'mis_rifas': mis_rifas[:5],  # Últimas 5 rifas
        'total_rifas': mis_rifas.count(),
        'total_ingresos': total_ingresos,
        'rifas_activas': rifas_activas.count(),
        'rifas_finalizadas': rifas_finalizadas.count(),
        'rifas_canceladas': rifas_canceladas.count(),
        'rifa_mas_vendida': rifa_mas_vendida,
        'rifas_proximas_sorteo': rifas_proximas_sorteo,
        'total_participantes': total_participantes,
        'ventas_recientes': ventas_recientes,
        'solicitudes_patrocinio': solicitudes_patrocinio,
        'total_solicitudes_patrocinio': total_solicitudes_patrocinio,
        'solicitudes_pendientes': solicitudes_pendientes,
        'invitaciones_enviadas': invitaciones_enviadas,
        'total_invitaciones_enviadas': total_invitaciones_enviadas,
        'invitaciones_pendientes': invitaciones_pendientes,
    }
    return render(request, 'raffles/organizer_dashboard.html', context)

@login_required
def sponsor_dashboard_view(request):
    from datetime import datetime, timedelta
    from .models import SponsorshipRequest, OrganizerSponsorRequest

    if request.user.rol not in ['sponsor', 'admin']:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard')

    # Solicitudes de patrocinio enviadas por el sponsor
    mis_solicitudes = SponsorshipRequest.objects.filter(sponsor=request.user).select_related('rifa').order_by('-fecha_solicitud')

    # Estadísticas de solicitudes enviadas
    total_solicitudes = mis_solicitudes.count()
    solicitudes_pendientes = mis_solicitudes.filter(estado='pendiente').count()
    solicitudes_aceptadas = mis_solicitudes.filter(estado='aceptada').count()
    solicitudes_rechazadas = mis_solicitudes.filter(estado='rechazada').count()

    # Invitaciones recibidas de organizadores
    invitaciones_recibidas = OrganizerSponsorRequest.objects.filter(
        sponsor=request.user
    ).select_related('rifa', 'organizador').order_by('-fecha_solicitud')[:10]

    # Estadísticas de invitaciones recibidas
    total_invitaciones = invitaciones_recibidas.count()
    invitaciones_pendientes = OrganizerSponsorRequest.objects.filter(sponsor=request.user, estado='pendiente').count()

    # Rifas activas disponibles para patrocinar
    rifas_disponibles = Raffle.objects.filter(estado='activa').annotate(
        total_vendidos=Count('boletos', filter=Q(boletos__estado='pagado')),
        porcentaje_calc=ExpressionWrapper(
            F('boletos_vendidos') * 100.0 / F('total_boletos'),
            output_field=FloatField()
        )
    ).order_by('-fecha_creacion')[:10]

    # Rifas con más participación (top 5)
    rifas_populares = Raffle.objects.filter(estado='activa').annotate(
        total_participantes=Count('boletos__usuario', filter=Q(boletos__estado='pagado'), distinct=True)
    ).order_by('-total_participantes')[:5]

    # Rifas próximas a finalizar (próximos 5 días)
    fecha_limite = datetime.now() + timedelta(days=5)
    rifas_proximas = Raffle.objects.filter(
        estado='activa',
        fecha_sorteo__lte=fecha_limite,
        fecha_sorteo__gte=datetime.now()
    ).order_by('fecha_sorteo')[:5]

    # Estadísticas generales del sistema
    total_rifas_activas = Raffle.objects.filter(estado='activa').count()
    total_participantes_sistema = Ticket.objects.filter(estado='pagado').values('usuario').distinct().count()
    total_organizadores = User.objects.filter(rol='organizador').count()

    # Oportunidades de patrocinio (rifas con baja venta pero alta calidad)
    # Calculamos el porcentaje vendido con anotación
    oportunidades_patrocinio = Raffle.objects.filter(
        estado='activa'
    ).annotate(
        total_vendidos=Count('boletos', filter=Q(boletos__estado='pagado')),
        porcentaje_calc=ExpressionWrapper(
            F('total_vendidos') * 100.0 / F('total_boletos'),
            output_field=FloatField()
        )
    ).filter(
        porcentaje_calc__lt=50
    ).order_by('porcentaje_calc')[:5]

    context = {
        'mis_solicitudes': mis_solicitudes,
        'total_solicitudes': total_solicitudes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aceptadas': solicitudes_aceptadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'invitaciones_recibidas': invitaciones_recibidas,
        'total_invitaciones': total_invitaciones,
        'invitaciones_pendientes': invitaciones_pendientes,
        'rifas_disponibles': rifas_disponibles,
        'rifas_populares': rifas_populares,
        'rifas_proximas': rifas_proximas,
        'total_rifas_activas': total_rifas_activas,
        'total_participantes_sistema': total_participantes_sistema,
        'total_organizadores': total_organizadores,
        'oportunidades_patrocinio': oportunidades_patrocinio,
    }
    return render(request, 'raffles/sponsor_dashboard.html', context)

# ============================================================================
# VISTA: create_raffle_view
# ============================================================================
# Permite a organizadores crear nuevas rifas
#
# URL: /raffles/create/
# Método: GET (formulario), POST (creación)
# Autenticación: Requerida
# Roles Permitidos: organizador, admin
#
# Estados Posibles al Crear:
# - 'borrador': Rifa guardada pero no publicada (default)
# - 'pendiente_aprobacion': Rifa enviada a revisión de admin
#
# Flujo:
# 1. Validar rol de usuario (organizador o admin)
# 2. Procesar formulario con datos de la rifa
# 3. Asignar organizador automáticamente
# 4. Si estado='pendiente_aprobacion': notificar a todos los admins
# 5. Guardar rifa y redirigir a dashboard
# ============================================================================
@login_required
def create_raffle_view(request):
    # === PASO 1: VALIDAR ROL ===
    # Solo organizadores y admins pueden crear rifas
    if request.user.rol not in ['organizador', 'admin']:
        messages.error(request, 'Solo los organizadores pueden crear rifas.')
        return redirect('dashboard')

    # === PASO 2: PROCESAR FORMULARIO (POST) ===
    if request.method == 'POST':
        # request.FILES: archivos subidos (imagen_rifa, imagen_premio, documentos)
        form = RaffleForm(request.POST, request.FILES)

        if form.is_valid():
            # === PASO 3: ASIGNAR ORGANIZADOR ===
            # commit=False: crear instancia sin guardar en DB
            raffle = form.save(commit=False)
            raffle.organizador = request.user  # Asignar automáticamente

            # === PASO 4: MANEJO DE APROBACIÓN ===
            # Si el estado es 'pendiente_aprobacion', guardar fecha y notificar
            if raffle.estado == 'pendiente_aprobacion':
                # Registrar cuándo se solicitó la aprobación
                raffle.fecha_solicitud = timezone.now()

                # === NOTIFICAR A TODOS LOS ADMINS ===
                admins = User.objects.filter(rol='admin')
                for admin in admins:
                    Notification.objects.create(
                        usuario=admin,
                        tipo='sistema',
                        titulo='Nueva rifa pendiente de aprobación',
                        mensaje=f'El organizador {request.user.nombre} ha solicitado aprobación para la rifa "{raffle.titulo}".',
                        enlace='/admin-panel/rifas-pendientes/'
                    )

            # === PASO 5: GUARDAR RIFA ===
            raffle.save()

            # === PASO 6: MENSAJE DE ÉXITO Y REDIRECCIÓN ===
            if raffle.estado == 'pendiente_aprobacion':
                messages.success(request, '¡Rifa enviada a revisión! Los administradores la revisarán pronto.')
            else:
                messages.success(request, '¡Rifa guardada como borrador!')

            return redirect('raffles:organizer_dashboard')

    # === PASO 7: MOSTRAR FORMULARIO (GET) ===
    else:
        form = RaffleForm()

    return render(request, 'raffles/create.html', {'form': form})

# ============================================================================
# VISTA: edit_raffle_view
# ============================================================================
# Permite editar rifas existentes con restricciones por estado
#
# URL: /raffles/<pk>/edit/
# Método: GET (formulario), POST (actualización)
# Autenticación: Requerida
# Validación: Solo el organizador propietario puede editar
#
# Estados Editables:
# - 'borrador': Edición completa de todos los campos
# - 'aprobada': Solo puede activar la rifa (cambiar a 'activa')
#
# Estados NO Editables:
# - 'activa': Rifa publicada, no se puede editar
# - 'finalizada': Sorteo realizado, inmutable
# - 'cancelada': Rifa cancelada, no se puede reactivar
# - 'pausada': Solo admin puede editar
# - 'pendiente_aprobacion': Solo admin puede aprobar/rechazar
#
# Flujo Especial - Activación:
# Si rifa.estado='aprobada' y POST.activar='true':
#   1. Cambiar estado a 'activa'
#   2. Establecer fecha_inicio
#   3. Notificar al organizador
#   4. Rifa ahora visible públicamente
# ============================================================================
@login_required
def edit_raffle_view(request, pk):
    # === PASO 1: OBTENER RIFA Y VALIDAR PROPIETARIO ===
    # get_object_or_404 con organizador=request.user
    # Asegura que solo el organizador puede editar SU rifa
    raffle = get_object_or_404(Raffle, pk=pk, organizador=request.user)

    # === PASO 2: VALIDAR ESTADO EDITABLE ===
    # Solo se permite editar rifas en estado 'borrador' o 'aprobada'
    # Estados activos, finalizados o cancelados son inmutables
    if raffle.estado not in ['borrador', 'aprobada']:
        messages.error(request, 'Solo puedes editar rifas en estado borrador o activar rifas aprobadas.')
        return redirect('raffles:organizer_dashboard')

    # === PASO 3: PROCESAR FORMULARIO (POST) ===
    if request.method == 'POST':
        # === CASO ESPECIAL: ACTIVACIÓN DIRECTA ===
        # Si la rifa está aprobada y se envía activar='true'
        # El organizador puede activarla sin editar otros campos
        if raffle.estado == 'aprobada' and request.POST.get('activar') == 'true':
            # Cambiar estado a activa
            raffle.estado = 'activa'

            # Registrar fecha de inicio (cuando se publicó)
            raffle.fecha_inicio = timezone.now()
            raffle.save()

            # === NOTIFICAR AL ORGANIZADOR ===
            Notification.objects.create(
                usuario=request.user,
                tipo='rifa',
                titulo='🎉 ¡Rifa Activada!',
                mensaje=f'Tu rifa "{raffle.titulo}" ha sido activada exitosamente y ahora es visible para todos los usuarios.',
                enlace=f'/raffles/{raffle.id}/'
            )

            messages.success(request, f'🎉 ¡Rifa "{raffle.titulo}" activada exitosamente! Ahora es visible para todos los usuarios y pueden comprar boletos.')
            return redirect('raffles:organizer_dashboard')

        # === EDICIÓN NORMAL CON FORMULARIO ===
        # request.FILES: archivos actualizados (imágenes, documentos)
        # instance=raffle: vincular formulario a rifa existente
        form = RaffleForm(request.POST, request.FILES, instance=raffle)

        if form.is_valid():
            # commit=False: obtener instancia sin guardar
            updated_raffle = form.save(commit=False)

            # === MANEJO DE CAMBIO A PENDIENTE_APROBACION ===
            # Si el organizador cambia el estado a 'pendiente_aprobacion'
            # (solicita aprobación de admin)
            if updated_raffle.estado == 'pendiente_aprobacion' and raffle.estado != 'pendiente_aprobacion':
                # Registrar fecha de solicitud
                updated_raffle.fecha_solicitud = timezone.now()

                # === NOTIFICAR A TODOS LOS ADMINS ===
                admins = User.objects.filter(rol='admin')
                for admin in admins:
                    Notification.objects.create(
                        usuario=admin,
                        tipo='sistema',
                        titulo='Rifa actualizada - Pendiente de aprobación',
                        mensaje=f'El organizador {request.user.nombre} ha solicitado aprobación para la rifa "{updated_raffle.titulo}".',
                        enlace='/admin-panel/rifas-pendientes/'
                    )

                messages.success(request, 'Rifa enviada a revisión administrativa.')
            else:
                messages.success(request, 'Rifa actualizada exitosamente.')

            # Guardar cambios en la base de datos
            updated_raffle.save()
            return redirect('raffles:organizer_dashboard')

    # === PASO 4: MOSTRAR FORMULARIO (GET) ===
    else:
        # Inicializar formulario con datos existentes de la rifa
        form = RaffleForm(instance=raffle)

    # === PASO 5: MENSAJE INFORMATIVO PARA RIFAS APROBADAS ===
    # Si la rifa está aprobada, recordar al organizador que debe activarla
    if raffle.estado == 'aprobada':
        messages.info(request, 'Tu rifa ha sido aprobada. Cambia el estado a "Activar Rifa" para que sea visible para todos.')

    return render(request, 'raffles/edit.html', {'form': form, 'raffle': raffle})

# ============================================================================
# VISTA: buy_ticket_view
# ============================================================================
# Permite comprar boletos para una rifa activa
#
# URL: /raffles/<raffle_id>/buy/
# Método: GET (formulario), POST (compra)
# Autenticación: Requerida
#
# Características Críticas de Concurrencia:
# - Usa transaction.atomic() para garantizar consistencia
# - select_for_update() bloquea la fila durante la transacción
# - Previene race conditions cuando múltiples usuarios compran simultáneamente
#
# Flujo:
# 1. Obtener rifa activa
# 2. Usuario selecciona cantidad de boletos
# 3. Iniciar transacción atómica con bloqueo
# 4. Verificar disponibilidad de boletos
# 5. Crear tickets en estado 'reservado'
# 6. Incrementar contador de boletos vendidos
# 7. Commit de transacción
# 8. Redirigir a proceso de pago
#
# Estados de Tickets:
# - 'reservado': Creado pero pago pendiente (5-10 min)
# - 'pagado': Pago confirmado, participa en sorteo
# - 'cancelado': Pago falló o usuario canceló
#
# Problema de Race Condition (SIN select_for_update):
# Usuario A: Lee boletos_vendidos = 98 (quedan 2)
# Usuario B: Lee boletos_vendidos = 98 (quedan 2)
# Usuario A: Compra 2 boletos → boletos_vendidos = 100 ✓
# Usuario B: Compra 2 boletos → boletos_vendidos = 102 ✗ (oversold)
#
# Solución (CON select_for_update):
# Usuario A: Bloquea fila → Lee 98 → Compra 2 → Guarda 100 → Libera
# Usuario B: Espera bloqueo → Lee 100 → Error "no disponible" ✓
# ============================================================================
@login_required
def buy_ticket_view(request, raffle_id):
    # Importar transaction para manejo de transacciones atómicas
    from django.db import transaction
    import logging
    logger = logging.getLogger(__name__)

    # === RESTRICCIÓN: ORGANIZADORES NO PUEDEN COMPRAR BOLETOS ===
    # Los organizadores solo pueden crear y gestionar rifas, no participar comprando boletos
    if request.user.rol == 'organizador':
        messages.error(request, '❌ Los organizadores no pueden comprar boletos de rifas. Solo pueden crearlas y administrarlas.')
        return redirect('raffles:detail', pk=raffle_id)

    # === PASO 1: OBTENER RIFA ACTIVA ===
    # Solo rifas en estado 'activa' permiten compra de boletos
    raffle = get_object_or_404(Raffle, pk=raffle_id, estado='activa')

    # === PASO 2: PROCESAR COMPRA (POST) ===
    if request.method == 'POST':
        # Obtener cantidad de boletos a comprar
        # default=1 si no se especifica
        cantidad = int(request.POST.get('cantidad', 1))

        # === PASO 3: TRANSACCIÓN ATÓMICA CON BLOQUEO ===
        # transaction.atomic() garantiza que todas las operaciones
        # se ejecuten completamente o ninguna (rollback automático en error)
        try:
            with transaction.atomic():
                # === PASO 4: BLOQUEAR FILA DE LA RIFA ===
                # select_for_update() crea un SELECT ... FOR UPDATE en SQL
                # Bloquea la fila hasta que termine la transacción
                # Otros queries esperarán hasta que se libere el bloqueo
                raffle = Raffle.objects.select_for_update().get(pk=raffle_id, estado='activa')

                # === PASO 5: VERIFICAR DISPONIBILIDAD ===
                # Calcular si hay suficientes boletos disponibles
                # raffle.boletos_disponibles es una property calculada
                if raffle.boletos_vendidos + cantidad > raffle.total_boletos:
                    messages.error(request, f'Solo hay {raffle.boletos_disponibles} boletos disponibles.')
                    return redirect('raffles:detail', pk=raffle_id)

                # === PASO 6: CREAR BOLETOS ===
                tickets_creados = []
                
                # Obtener números de boletos ya vendidos
                numeros_ocupados = set(Ticket.objects.filter(rifa=raffle).values_list('numero_boleto', flat=True))
                
                # Obtener números disponibles
                numeros_disponibles = [n for n in range(1, raffle.total_boletos + 1) if n not in numeros_ocupados]
                
                # Verificar que hay suficientes números disponibles
                if len(numeros_disponibles) < cantidad:
                    messages.error(request, f'Solo hay {len(numeros_disponibles)} boletos disponibles.')
                    return redirect('raffles:detail', pk=raffle_id)
                
                # Tomar los primeros N números disponibles
                numeros_a_usar = numeros_disponibles[:cantidad]
                
                for numero_boleto in numeros_a_usar:
                    # Código QR único para validación
                    # UUID4 genera identificador aleatorio único
                    # Ejemplo: "a3f5e9b2-c4d7-f1a8-e6b9-d2c5f8a1e4b7"
                    codigo_qr = str(uuid.uuid4())

                    # Crear ticket en estado 'reservado'
                    # El pago se procesa después
                    ticket = Ticket.objects.create(
                        rifa=raffle,
                        usuario=request.user,
                        numero_boleto=numero_boleto,
                        codigo_qr=codigo_qr,
                        estado='reservado'  # Pago pendiente
                    )
                    tickets_creados.append(ticket)

                    # Incrementar contador de boletos vendidos
                    raffle.boletos_vendidos += 1

                # === PASO 7: GUARDAR CAMBIOS ===
                # Guardar el contador actualizado de boletos vendidos
                raffle.save()

            # === PASO 8: REDIRIGIR A PAGO (FUERA DE TRANSACCIÓN) ===
            # La transacción ya se completó (commit automático al salir del with)
            # Crear string con IDs separados por comas: "1,2,3"
            ticket_ids_str = ','.join(str(t.id) for t in tickets_creados)

            # Redirigir a vista de procesamiento de pago
            return redirect('payments:process_payment', ticket_ids=ticket_ids_str)

        # === MANEJO DE ERRORES ===
        except Exception as e:
            # Si hay error, transaction.atomic() hace rollback automático
            # Los tickets creados se eliminan y el contador no se incrementa
            logger.error(f"Error en compra de boletos: {str(e)}")
            messages.error(request, f'Error al procesar la compra: {str(e)}. Por favor, intenta nuevamente.')
            return redirect('raffles:detail', pk=raffle_id)

    # === PASO 9: MOSTRAR FORMULARIO (GET) ===
    return render(request, 'raffles/buy_ticket.html', {'raffle': raffle})

# ============================================================================
# VISTA: roulette_view
# ============================================================================
# Vista de la ruleta animada para el sorteo
#
# URL: /raffles/<pk>/roulette/
# Método: GET
# Autenticación: No requerida (pública)
#
# Propósito:
# Mostrar animación de ruleta con todos los participantes
# La ruleta gira y selecciona un ganador de forma visual
#
# Datos preparados para JavaScript:
# - Lista de todos los boletos pagados
# - Información de cada participante (nombre, número de boleto)
# - JSON serializado para consumo en frontend
#
# Animación:
# La ruleta JavaScript usa los datos para:
# 1. Mostrar nombres de participantes girando
# 2. Acelerar y desacelerar el giro
# 3. Detenerse en el ganador cuando el servidor lo confirma
# 4. Mostrar confetti y celebración
# ============================================================================
def roulette_view(request, pk):
    # === OBTENER RIFA ===
    raffle = get_object_or_404(Raffle, pk=pk)

    # === OBTENER BOLETOS PAGADOS ===
    # select_related('usuario'): optimización para evitar N+1 queries
    # Solo boletos con estado='pagado' participan en el sorteo
    tickets = Ticket.objects.filter(
        rifa=raffle,
        estado='pagado'
    ).select_related('usuario')

    # === PREPARAR DATOS PARA JAVASCRIPT ===
    # Crear lista de diccionarios con información de cada ticket
    # Estos datos se usarán en la animación de la ruleta
    tickets_data = [
        {
            'id': ticket.id,                      # ID del ticket
            'numero_boleto': ticket.numero_boleto, # Número visible (#1, #2, #3...)
            'usuario__nombre': ticket.usuario.nombre  # Nombre del participante
        }
        for ticket in tickets
    ]

    # === RENDERIZAR TEMPLATE ===
    return render(request, 'raffles/roulette.html', {
        'raffle': raffle,              # Instancia de Raffle
        'tickets': tickets,             # QuerySet de tickets
        'tickets_json': json.dumps(tickets_data)  # JSON para JavaScript
    })

@require_http_methods(["POST"])
def perform_raffle_draw(request, pk):
    """Realiza el sorteo de la rifa en el servidor"""
    raffle = get_object_or_404(Raffle, pk=pk)

    # Verificar si ya hay un ganador
    existing_winner = Winner.objects.filter(rifa=raffle).first()
    if existing_winner:
        return JsonResponse({
            'success': True,
            'already_drawn': True,
            'winner': {
                'id': existing_winner.boleto.id,
                'numero_boleto': existing_winner.boleto.numero_boleto,
                'usuario__nombre': existing_winner.boleto.usuario.nombre,
                'email': existing_winner.boleto.usuario.email
            }
        })

    # Verificar que haya boletos vendidos
    tickets = list(Ticket.objects.filter(rifa=raffle, estado='pagado').select_related('usuario'))
    if not tickets:
        return JsonResponse({'success': False, 'error': 'No hay boletos vendidos'}, status=400)

    # Realizar sorteo verificable
    resultado_sorteo = generar_sorteo_verificable(raffle, tickets)
    winning_ticket = resultado_sorteo['winning_ticket']

    # Crear registro de ganador con datos de verificación
    winner = Winner.objects.create(
        rifa=raffle,
        boleto=winning_ticket,
        verificado=False,
        premio_entregado=False,
        seed_aleatorio=resultado_sorteo['seed_aleatorio'],
        timestamp_sorteo=resultado_sorteo['timestamp_sorteo'],
        hash_verificacion=resultado_sorteo['hash_verificacion'],
        participantes_totales=resultado_sorteo['participantes_totales'],
        acta_digital=resultado_sorteo['acta_digital'],
        algoritmo='SHA256+Timestamp'
    )

    # Actualizar estado de la rifa
    raffle.estado = 'finalizada'
    raffle.save()

    # Crear notificación para el ganador
    Notification.objects.create(
        usuario=winning_ticket.usuario,
        tipo='ganador',
        titulo='🎉 ¡Felicidades! Has ganado',
        mensaje=f'¡Felicitaciones! Has ganado el sorteo "{raffle.titulo}". Premio: {raffle.premio_principal}',
        enlace=f'/raffles/{raffle.id}/',
        rifa_relacionada=raffle
    )

    # Crear notificaciones para todos los participantes (excepto el ganador)
    participantes = set([t.usuario for t in tickets if t.usuario != winning_ticket.usuario])
    for participante in participantes:
        Notification.objects.create(
            usuario=participante,
            tipo='sorteo',
            titulo=f'Sorteo finalizado: {raffle.titulo}',
            mensaje=f'El sorteo ha finalizado. El ganador es {winning_ticket.usuario.nombre}.',
            enlace=f'/raffles/{raffle.id}/',
            rifa_relacionada=raffle
        )

    return JsonResponse({
        'success': True,
        'already_drawn': False,
        'winner': {
            'id': winning_ticket.id,
            'numero_boleto': winning_ticket.numero_boleto,
            'usuario__nombre': winning_ticket.usuario.nombre,
            'email': winning_ticket.usuario.email
        }
    })

@require_http_methods(["GET"])
def check_raffle_winner(request, pk):
    """Verifica si ya hay un ganador para la rifa"""
    raffle = get_object_or_404(Raffle, pk=pk)
    winner = Winner.objects.filter(rifa=raffle).select_related('boleto__usuario').first()

    if winner:
        return JsonResponse({
            'has_winner': True,
            'winner': {
                'id': winner.boleto.id,
                'numero_boleto': winner.boleto.numero_boleto,
                'usuario__nombre': winner.boleto.usuario.nombre,
                'email': winner.boleto.usuario.email
            }
        })
    else:
        return JsonResponse({'has_winner': False})

@login_required
@require_http_methods(["POST"])
def select_winner_view(request, pk):
    """Automatically select winner from roulette"""
    import random
    from django.utils import timezone

    raffle = get_object_or_404(Raffle, pk=pk)

    # Allow automatic sorteo if draw time has passed OR if user is organizer/admin
    is_past_draw_time = timezone.now() >= raffle.fecha_sorteo
    is_authorized = request.user == raffle.organizador or request.user.rol == 'admin'

    if not is_past_draw_time and not is_authorized:
        return JsonResponse({'success': False, 'error': 'No tienes permisos para realizar esta acción'})

    # Check if raffle is active
    if raffle.estado != 'activa':
        return JsonResponse({'success': False, 'error': 'La rifa no está activa'})

    # Check if winner already exists
    if Winner.objects.filter(rifa=raffle).exists():
        return JsonResponse({'success': False, 'error': 'Esta rifa ya tiene un ganador'})

    # Get ticket ID from request
    try:
        ticket_id = None
        if request.body:
            try:
                data = json.loads(request.body)
                ticket_id = data.get('ticket_id')
            except:
                pass

        # Obtener todos los boletos pagados
        tickets = list(Ticket.objects.filter(rifa=raffle, estado='pagado').select_related('usuario'))
        if not tickets:
            return JsonResponse({'success': False, 'error': 'No hay boletos vendidos'})

        # Realizar sorteo verificable
        resultado_sorteo = generar_sorteo_verificable(raffle, tickets)
        ticket = resultado_sorteo['winning_ticket']

        # Create winner con datos de verificación
        winner = Winner.objects.create(
            rifa=raffle,
            boleto=ticket,
            seed_aleatorio=resultado_sorteo['seed_aleatorio'],
            timestamp_sorteo=resultado_sorteo['timestamp_sorteo'],
            hash_verificacion=resultado_sorteo['hash_verificacion'],
            participantes_totales=resultado_sorteo['participantes_totales'],
            acta_digital=resultado_sorteo['acta_digital'],
            algoritmo='SHA256+Timestamp'
        )

        # Update raffle status
        raffle.estado = 'finalizada'
        raffle.save()

        # Notify winner
        Notification.objects.create(
            usuario=ticket.usuario,
            tipo='ganador',
            titulo='🎉 ¡Felicidades! Has ganado',
            mensaje=f'Has ganado la rifa "{raffle.titulo}". Premio: {raffle.premio_principal}',
            enlace=f'/raffles/{raffle.id}/',
            rifa_relacionada=raffle
        )

        # Notify participants
        participants = Ticket.objects.filter(rifa=raffle, estado='pagado').exclude(usuario=ticket.usuario).select_related('usuario').distinct('usuario')
        for participant_ticket in participants:
            Notification.objects.create(
                usuario=participant_ticket.usuario,
                tipo='sorteo',
                titulo=f'Sorteo finalizado: {raffle.titulo}',
                mensaje=f'La rifa ha finalizado. El ganador es {ticket.usuario.nombre}',
                enlace=f'/raffles/{raffle.id}/',
                rifa_relacionada=raffle
            )

        return JsonResponse({
            'success': True,
            'winner': {
                'id': ticket.id,
                'numero_boleto': ticket.numero_boleto,
                'nombre': ticket.usuario.nombre,
                'email': ticket.usuario.email
            }
        })

    except Exception as e:
        return JsonResponse(safe_json_error(e, get_error_message('winner')))

def acta_sorteo_view(request, pk):
    """Vista para mostrar el acta digital del sorteo de forma pública"""
    raffle = get_object_or_404(Raffle, pk=pk)

    # Verificar que el sorteo haya sido realizado
    try:
        winner = Winner.objects.select_related('boleto__usuario', 'rifa__organizador').get(rifa=raffle)
    except Winner.DoesNotExist:
        messages.error(request, 'Este sorteo aún no se ha realizado.')
        return redirect('raffles:detail', pk=pk)

    # Obtener todos los participantes para verificación
    participantes = Ticket.objects.filter(rifa=raffle, estado='pagado').select_related('usuario').order_by('numero_boleto')

    context = {
        'raffle': raffle,
        'winner': winner,
        'participantes': participantes,
        'total_participantes': participantes.count()
    }

    return render(request, 'raffles/acta_sorteo.html', context)

@login_required
def create_sponsorship_request_view(request, pk):
    """Vista para que un sponsor envíe una solicitud de patrocinio"""
    from .models import SponsorshipRequest

    if request.user.rol not in ['sponsor', 'admin']:
        messages.error(request, 'Solo los sponsors pueden enviar solicitudes de patrocinio.')
        return redirect('raffles:detail', pk=pk)

    raffle = get_object_or_404(Raffle, pk=pk)

    # Verificar que la rifa esté activa
    if raffle.estado != 'activa':
        messages.error(request, 'Solo puedes patrocinar rifas activas.')
        return redirect('raffles:detail', pk=pk)

    # Verificar si ya tiene una solicitud pendiente
    solicitud_existente = SponsorshipRequest.objects.filter(
        rifa=raffle,
        sponsor=request.user,
        estado='pendiente'
    ).first()

    if solicitud_existente:
        messages.warning(request, 'Ya tienes una solicitud de patrocinio pendiente para esta rifa.')
        return redirect('raffles:detail', pk=pk)

    if request.method == 'POST':
        try:
            # Crear la solicitud de patrocinio
            solicitud = SponsorshipRequest(
                rifa=raffle,
                sponsor=request.user,
                nombre_premio_adicional=request.POST.get('nombre_premio_adicional'),
                descripcion_premio=request.POST.get('descripcion_premio'),
                valor_premio=request.POST.get('valor_premio'),
                nombre_marca=request.POST.get('nombre_marca'),
                sitio_web=request.POST.get('sitio_web', ''),
                mensaje_patrocinio=request.POST.get('mensaje_patrocinio'),
            )

            # Manejar archivos
            if 'imagen_premio' in request.FILES:
                solicitud.imagen_premio = request.FILES['imagen_premio']
            if 'logo_marca' in request.FILES:
                solicitud.logo_marca = request.FILES['logo_marca']

            solicitud.save()

            # Notificar al organizador
            Notification.objects.create(
                usuario=raffle.organizador,
                tipo='sistema',
                titulo='Nueva Solicitud de Patrocinio',
                mensaje=f'{request.user.nombre} quiere patrocinar tu rifa "{raffle.titulo}" con un premio adicional.',
                enlace=f'/raffles/sponsorship/{solicitud.id}/'
            )

            messages.success(request, '¡Solicitud de patrocinio enviada! El organizador la revisará pronto.')
            return redirect('raffles:sponsor_dashboard')

        except Exception as e:
            error_msg = handle_exception_safely(e, 'notification', 'Solicitud de patrocinio')
            messages.error(request, error_msg)
            return redirect('raffles:detail', pk=pk)

    context = {
        'raffle': raffle
    }
    return render(request, 'raffles/create_sponsorship_request.html', context)

@login_required
def sponsorship_request_detail_view(request, pk):
    """Vista para ver los detalles de una solicitud de patrocinio"""
    from .models import SponsorshipRequest

    solicitud = get_object_or_404(SponsorshipRequest, pk=pk)

    # Solo el organizador de la rifa o el sponsor pueden ver la solicitud
    if request.user != solicitud.rifa.organizador and request.user != solicitud.sponsor and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para ver esta solicitud.')
        return redirect('dashboard')

    context = {
        'solicitud': solicitud
    }
    return render(request, 'raffles/sponsorship_request_detail.html', context)

@login_required
@require_http_methods(["POST"])
def accept_sponsorship_request_view(request, pk):
    """Vista para que un organizador acepte una solicitud de patrocinio"""
    from .models import SponsorshipRequest

    solicitud = get_object_or_404(SponsorshipRequest, pk=pk)

    # Verificar que el usuario sea el organizador de la rifa
    if request.user != solicitud.rifa.organizador and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para aceptar esta solicitud.')
        return redirect('raffles:organizer_dashboard')

    if solicitud.estado != 'pendiente':
        messages.warning(request, 'Esta solicitud ya fue procesada.')
        return redirect('raffles:organizer_dashboard')

    solicitud.estado = 'aceptada'
    solicitud.fecha_respuesta = timezone.now()
    solicitud.save()

    # Notificar al sponsor
    Notification.objects.create(
        usuario=solicitud.sponsor,
        tipo='sponsor_aprobado',
        titulo='Solicitud de Patrocinio Aceptada',
        mensaje=f'Tu solicitud de patrocinio para "{solicitud.rifa.titulo}" ha sido aceptada.',
        enlace=f'/raffles/{solicitud.rifa.id}/'
    )

    messages.success(request, f'Has aceptado el patrocinio de {solicitud.sponsor.nombre}.')
    return redirect('raffles:organizer_dashboard')

@login_required
@require_http_methods(["POST"])
def reject_sponsorship_request_view(request, pk):
    """Vista para que un organizador rechace una solicitud de patrocinio"""
    from .models import SponsorshipRequest

    solicitud = get_object_or_404(SponsorshipRequest, pk=pk)

    # Verificar que el usuario sea el organizador de la rifa
    if request.user != solicitud.rifa.organizador and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para rechazar esta solicitud.')
        return redirect('raffles:organizer_dashboard')

    if solicitud.estado != 'pendiente':
        messages.warning(request, 'Esta solicitud ya fue procesada.')
        return redirect('raffles:organizer_dashboard')

    solicitud.estado = 'rechazada'
    solicitud.fecha_respuesta = timezone.now()
    solicitud.motivo_rechazo = request.POST.get('motivo_rechazo', 'No especificado')
    solicitud.save()

    # Notificar al sponsor
    Notification.objects.create(
        usuario=solicitud.sponsor,
        tipo='sponsor_rechazado',
        titulo='Solicitud de Patrocinio Rechazada',
        mensaje=f'Tu solicitud de patrocinio para "{solicitud.rifa.titulo}" fue rechazada.',
        enlace=f'/raffles/sponsorship/{solicitud.id}/'
    )

    messages.info(request, f'Has rechazado el patrocinio de {solicitud.sponsor.nombre}.')
    return redirect('raffles:organizer_dashboard')

@login_required
def browse_sponsors_view(request):
    """Vista para que un organizador vea los sponsors disponibles"""
    from .models import OrganizerSponsorRequest

    if request.user.rol not in ['organizador', 'admin']:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard')

    # Obtener todos los sponsors activos
    sponsors_disponibles = User.objects.filter(
        rol='sponsor',
        is_active=True
    ).order_by('-fecha_registro')

    # Obtener rifas activas del organizador
    mis_rifas_activas = Raffle.objects.filter(
        organizador=request.user,
        estado='activa'
    ).order_by('-fecha_creacion')

    context = {
        'sponsors_disponibles': sponsors_disponibles,
        'mis_rifas_activas': mis_rifas_activas,
    }
    return render(request, 'raffles/browse_sponsors.html', context)

@login_required
def send_sponsor_invitation_view(request, sponsor_id):
    """Vista para que un organizador envíe una invitación a un sponsor"""
    from .models import OrganizerSponsorRequest
    from .forms import OrganizerSponsorInvitationForm

    if request.user.rol not in ['organizador', 'admin']:
        messages.error(request, 'No tienes permisos para enviar invitaciones.')
        return redirect('dashboard')

    sponsor = get_object_or_404(User, pk=sponsor_id, rol='sponsor')

    if request.method == 'POST':
        form = OrganizerSponsorInvitationForm(request.POST, organizador=request.user)

        if form.is_valid():
            # Verificar si ya existe una solicitud
            rifa = form.cleaned_data['rifa']
            solicitud_existente = OrganizerSponsorRequest.objects.filter(
                rifa=rifa,
                sponsor=sponsor
            ).first()

            if solicitud_existente:
                messages.warning(request, f'Ya has enviado una invitación a {sponsor.nombre} para esta rifa.')
                return redirect('raffles:browse_sponsors')

            try:
                # Crear la invitación
                invitacion = form.save(commit=False)
                invitacion.sponsor = sponsor
                invitacion.organizador = request.user
                invitacion.save()

                # Notificar al sponsor
                Notification.objects.create(
                    usuario=sponsor,
                    tipo='sistema',
                    titulo='Invitación para Patrocinar una Rifa',
                    mensaje=f'{request.user.nombre} te invita a patrocinar su rifa "{rifa.titulo}".',
                    enlace=f'/raffles/organizer-request/{invitacion.id}/'
                )

                messages.success(request, f'¡Invitación enviada a {sponsor.nombre}!')
                return redirect('raffles:organizer_dashboard')

            except Exception as e:
                error_msg = handle_exception_safely(e, 'notification', 'Invitación de sponsor')
                messages.error(request, error_msg)
                return redirect('raffles:browse_sponsors')
    else:
        form = OrganizerSponsorInvitationForm(organizador=request.user)

    context = {
        'sponsor': sponsor,
        'form': form,
    }
    return render(request, 'raffles/send_sponsor_invitation.html', context)

@login_required
def organizer_request_detail_view(request, pk):
    """Vista para ver los detalles de una invitación de organizador"""
    from .models import OrganizerSponsorRequest

    invitacion = get_object_or_404(OrganizerSponsorRequest, pk=pk)

    # Solo el sponsor o el organizador pueden ver la invitación
    if request.user != invitacion.sponsor and request.user != invitacion.organizador and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para ver esta invitación.')
        return redirect('dashboard')

    context = {
        'invitacion': invitacion
    }
    return render(request, 'raffles/organizer_request_detail.html', context)

@login_required
@require_http_methods(["POST"])
def accept_organizer_request_view(request, pk):
    """Vista para que un sponsor acepte una invitación de un organizador"""
    from .models import OrganizerSponsorRequest

    invitacion = get_object_or_404(OrganizerSponsorRequest, pk=pk)

    # Verificar que el usuario sea el sponsor
    if request.user != invitacion.sponsor and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para aceptar esta invitación.')
        return redirect('raffles:sponsor_dashboard')

    if invitacion.estado != 'pendiente':
        messages.warning(request, 'Esta invitación ya fue procesada.')
        return redirect('raffles:sponsor_dashboard')

    invitacion.estado = 'aceptada'
    invitacion.fecha_respuesta = timezone.now()
    invitacion.propuesta_premio = request.POST.get('propuesta_premio', '')
    invitacion.propuesta_valor = request.POST.get('propuesta_valor', None)
    invitacion.save()

    # Notificar al organizador
    Notification.objects.create(
        usuario=invitacion.organizador,
        tipo='sponsor_aprobado',
        titulo='Invitación de Patrocinio Aceptada',
        mensaje=f'{invitacion.sponsor.nombre} ha aceptado patrocinar tu rifa "{invitacion.rifa.titulo}".',
        enlace=f'/raffles/{invitacion.rifa.id}/'
    )

    messages.success(request, f'Has aceptado patrocinar la rifa "{invitacion.rifa.titulo}".')
    return redirect('raffles:sponsor_dashboard')

@login_required
@require_http_methods(["POST"])
def reject_organizer_request_view(request, pk):
    """Vista para que un sponsor rechace una invitación de un organizador"""
    from .models import OrganizerSponsorRequest

    invitacion = get_object_or_404(OrganizerSponsorRequest, pk=pk)

    # Verificar que el usuario sea el sponsor
    if request.user != invitacion.sponsor and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para rechazar esta invitación.')
        return redirect('raffles:sponsor_dashboard')

    if invitacion.estado != 'pendiente':
        messages.warning(request, 'Esta invitación ya fue procesada.')
        return redirect('raffles:sponsor_dashboard')

    invitacion.estado = 'rechazada'
    invitacion.fecha_respuesta = timezone.now()
    invitacion.motivo_rechazo = request.POST.get('motivo_rechazo', 'No especificado')
    invitacion.save()

    # Notificar al organizador
    Notification.objects.create(
        usuario=invitacion.organizador,
        tipo='sponsor_rechazado',
        titulo='Invitación de Patrocinio Rechazada',
        mensaje=f'{invitacion.sponsor.nombre} ha rechazado tu invitación para patrocinar "{invitacion.rifa.titulo}".',
        enlace=f'/raffles/organizer-request/{invitacion.id}/'
    )

    messages.info(request, f'Has rechazado la invitación para patrocinar "{invitacion.rifa.titulo}".')
    return redirect('raffles:sponsor_dashboard')
