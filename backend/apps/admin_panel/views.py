from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import models
from django.db.models import Count, Sum, Q
from django.http import HttpResponse, JsonResponse
from apps.users.models import User, Notification, Profile
from apps.raffles.models import Raffle, Ticket, Winner
from apps.payments.models import Payment
from .models import AuditLog
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import random
from django.utils import timezone
from apps.core.email_validator import verify_email, get_email_report
from apps.core.safe_errors import safe_json_error, handle_exception_safely, get_error_message

def is_admin(user):
    return user.is_authenticated and user.rol == 'admin'

def is_superuser_check(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def user_profile_view(request, user_id):
    """Vista para mostrar el perfil de un usuario específico en el panel de administración"""
    user = get_object_or_404(User, id=user_id)
    profile = Profile.objects.filter(user=user).first()
    context = {
        'user_obj': user,
        'profile': profile,
    }
    return render(request, 'admin_panel/user_profile.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    from datetime import datetime, timedelta
    from django.db.models.functions import TruncDate
    import json

    # Estadísticas principales
    total_users = User.objects.count()
    total_raffles = Raffle.objects.count()
    total_payments = Payment.objects.count()
    total_revenue = Payment.objects.filter(estado='completado').aggregate(Sum('monto'))['monto__sum'] or 0
    active_raffles = Raffle.objects.filter(estado='activa').count()
    active_users = User.objects.filter(is_active=True).count()

    # Estadísticas secundarias
    tickets_sold = Ticket.objects.count()
    total_winners = Raffle.objects.filter(ganador__isnull=False).count()
    total_sponsors = User.objects.filter(rol='sponsor').count()
    rifas_pausadas = Raffle.objects.filter(estado='pausada').count()
    rifas_pendientes_aprobacion = Raffle.objects.filter(estado='pendiente_aprobacion').count()
    sponsors_pendientes = User.objects.filter(rol='sponsor', cuenta_validada=False).count()

    # Distribución por roles
    participantes_count = User.objects.filter(rol='participante').count()
    organizadores_count = User.objects.filter(rol='organizador').count()
    sponsors_count = User.objects.filter(rol='sponsor').count()
    admins_count = User.objects.filter(rol__in=['admin', 'superuser']).count()

    # Crecimiento (últimos 30 días vs 30 días anteriores)
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    users_last_30 = User.objects.filter(fecha_registro__gte=last_30_days).count()
    users_growth = 5  # Placeholder - calcular real después
    revenue_growth = 12  # Placeholder
    completed_payments = Payment.objects.filter(estado='completado').count()

    # Datos para gráficos - Últimos 7 días
    last_7_days = today - timedelta(days=6)
    users_by_day = User.objects.filter(
        fecha_registro__gte=last_7_days,
        fecha_registro__isnull=False
    ).annotate(
        day=TruncDate('fecha_registro')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    # Crear labels y data para el gráfico
    date_dict = {today - timedelta(days=i): 0 for i in range(6, -1, -1)}
    for entry in users_by_day:
        if entry['day'] is not None:
            date_dict[entry['day']] = entry['count']

    chart_labels = [date.strftime('%d/%m') for date in sorted(date_dict.keys())]
    chart_data = [date_dict[date] for date in sorted(date_dict.keys())]

    # Usuarios recientes
    recent_users = User.objects.order_by('-fecha_registro')[:10]

    # Rifas recientes
    recent_raffles = Raffle.objects.order_by('-fecha_creacion')[:10]

    # Sponsors pendientes (para el modal)
    sponsors_pendientes_list = list(User.objects.filter(
        rol='sponsor',
        cuenta_validada=False
    ).values(
        'id', 'nombre', 'email', 'telefono', 'fecha_registro'
    ).order_by('-fecha_registro'))

    # Formatear fechas para JSON
    for sponsor in sponsors_pendientes_list:
        if sponsor['fecha_registro']:
            sponsor['fecha_registro'] = sponsor['fecha_registro'].strftime('%d/%m/%Y %H:%M')

    # Logs de auditoría
    recent_logs = AuditLog.objects.select_related('usuario').order_by('-fecha')[:15]

    # Alertas del sistema
    pending_validations = User.objects.filter(cuenta_validada=False).count()
    expiring_raffles = Raffle.objects.filter(
        estado='activa',
        fecha_sorteo__lte=timezone.now() + timedelta(days=7)
    ).count()
    first_day_of_month = today.replace(day=1)
    failed_payments = Payment.objects.filter(
        estado='fallido',
        fecha_creacion__gte=first_day_of_month
    ).count()

    # Métricas de rendimiento
    total_tickets = Ticket.objects.count()
    sold_tickets = Ticket.objects.filter(estado='pagado').count()
    conversion_rate = round((sold_tickets / total_tickets * 100) if total_tickets > 0 else 0, 1)

    total_capacity = Raffle.objects.filter(estado='activa').aggregate(
        total=Sum('total_boletos')
    )['total'] or 0
    sold_capacity = Ticket.objects.filter(rifa__estado='activa', estado='pagado').count()
    occupancy_rate = round((sold_capacity / total_capacity * 100) if total_capacity > 0 else 0, 1)

    satisfaction_rate = 85  # Placeholder

    # Notificaciones sin leer
    unread_notifications = Notification.objects.filter(
        usuario=request.user,
        leida=False
    ).count()

    context = {
        # Stats principales
        'total_users': total_users,
        'total_raffles': total_raffles,
        'total_payments': total_payments,
        'total_revenue': total_revenue,
        'active_raffles': active_raffles,
        'users_growth': users_growth,
        'revenue_growth': revenue_growth,
        'completed_payments': completed_payments,
        'unread_notifications_count': unread_notifications,

        # Stats secundarias
        'active_users': active_users,
        'tickets_sold': tickets_sold,
        'total_winners': total_winners,
        'total_sponsors': total_sponsors,

        # Distribución por roles
        'participantes_count': participantes_count,
        'organizadores_count': organizadores_count,
        'sponsors_count': sponsors_count,
        'admins_count': admins_count,

        # Datos para gráficos
        'users_chart_labels': json.dumps(chart_labels),
        'users_chart_data': json.dumps(chart_data),

        # Datos recientes
        'recent_users': recent_users,
        'recent_raffles': recent_raffles,
        'recent_logs': recent_logs,
        'rifas_pausadas': rifas_pausadas,
        'rifas_pendientes_aprobacion': rifas_pendientes_aprobacion,
        'sponsors_pendientes': sponsors_pendientes,
        'sponsors_pendientes_list': json.dumps(sponsors_pendientes_list),

        # Alertas
        'pending_validations': pending_validations,
        'expiring_raffles': expiring_raffles,
        'failed_payments': failed_payments,

        # Métricas de rendimiento
        'conversion_rate': conversion_rate,
        'occupancy_rate': occupancy_rate,
        'satisfaction_rate': satisfaction_rate,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def users_management_view(request):
    """
    Vista avanzada de gestión de usuarios con estadísticas completas,
    filtros, búsqueda y acciones masivas.
    """
    from django.core.paginator import Paginator
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta

    # Estadísticas generales
    total_users = User.objects.count()
    users_participantes = User.objects.filter(rol='participante').count()
    users_organizadores = User.objects.filter(rol='organizador').count()
    users_sponsors = User.objects.filter(rol='sponsor').count()
    users_admins = User.objects.filter(rol__in=['admin', 'superuser']).count()
    active_users = User.objects.filter(is_active=True).count()
    validated_users = User.objects.filter(cuenta_validada=True).count()
    users_with_tickets = User.objects.filter(boletos__estado='pagado').distinct().count()

    # Query base optimizada
    users = User.objects.annotate(
        tickets_count=Count('boletos', filter=Q(boletos__estado='pagado')),
        raffles_count=Count('rifas_organizadas'),
        total_spent=Sum('pagos__monto', filter=Q(pagos__estado='completado'))
    ).order_by('-fecha_registro')

    # Filtros avanzados
    rol_filter = request.GET.get('rol')
    if rol_filter:
        users = users.filter(rol=rol_filter)

    status_filter = request.GET.get('status')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    validated_filter = request.GET.get('validated')
    if validated_filter == 'yes':
        users = users.filter(cuenta_validada=True)
    elif validated_filter == 'no':
        users = users.filter(cuenta_validada=False)

    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(nombre__icontains=search) |
            Q(email__icontains=search) |
            Q(telefono__icontains=search) |
            Q(id__icontains=search)
        )

    # Ordenamiento
    sort_by = request.GET.get('sort', '-fecha_registro')
    users = users.order_by(sort_by)

    # Filtro de actividad reciente
    activity_filter = request.GET.get('activity')
    if activity_filter == 'today':
        users = users.filter(ultima_conexion__gte=datetime.now() - timedelta(days=1))
    elif activity_filter == 'week':
        users = users.filter(ultima_conexion__gte=datetime.now() - timedelta(days=7))
    elif activity_filter == 'month':
        users = users.filter(ultima_conexion__gte=datetime.now() - timedelta(days=30))

    # Estadísticas de usuarios
    users_today = User.objects.filter(
        fecha_registro__gte=datetime.now() - timedelta(days=1)
    ).count()
    users_this_week = User.objects.filter(
        fecha_registro__gte=datetime.now() - timedelta(days=7)
    ).count()
    users_this_month = User.objects.filter(
        fecha_registro__gte=datetime.now() - timedelta(days=30)
    ).count()

    # Usuarios más activos
    top_buyers = User.objects.annotate(
        tickets=Count('boletos', filter=Q(boletos__estado='pagado'))
    ).filter(tickets__gt=0).order_by('-tickets')[:5]

    top_organizers = User.objects.annotate(
        raffles=Count('rifas_organizadas')
    ).filter(raffles__gt=0).order_by('-raffles')[:5]

    # Paginación
    paginator = Paginator(users, 20)  # 20 usuarios por página
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    context = {
        'users': users_page,
        'total_users': total_users,
        'users_participantes': users_participantes,
        'users_organizadores': users_organizadores,
        'users_sponsors': users_sponsors,
        'users_admins': users_admins,
        'active_users': active_users,
        'validated_users': validated_users,
        'users_with_tickets': users_with_tickets,
        'users_today': users_today,
        'users_this_week': users_this_week,
        'users_this_month': users_this_month,
        'top_buyers': top_buyers,
        'top_organizers': top_organizers,
        # Filtros activos
        'current_rol': rol_filter,
        'current_status': status_filter,
        'current_validated': validated_filter,
        'current_activity': activity_filter,
        'current_search': search,
        'current_sort': sort_by,
    }

    return render(request, 'admin_panel/users.html', context)

@login_required
@user_passes_test(is_admin)
def raffles_management_view(request):
    from django.core.paginator import Paginator
    from datetime import datetime

    raffles = Raffle.objects.select_related('organizador').order_by('-fecha_creacion')

    # Búsqueda
    search = request.GET.get('search')
    if search:
        raffles = raffles.filter(
            Q(titulo__icontains=search) |
            Q(organizador__nombre__icontains=search) |
            Q(organizador__email__icontains=search) |
            Q(id__icontains=search)
        )

    # Filtro de estado
    estado_filter = request.GET.get('estado')
    if estado_filter:
        raffles = raffles.filter(estado=estado_filter)

    # Filtros de fecha
    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            raffles = raffles.filter(fecha_sorteo__gte=fecha_desde_obj)
        except ValueError:
            pass

    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            raffles = raffles.filter(fecha_sorteo__lte=fecha_hasta_obj)
        except ValueError:
            pass

    # Ordenamiento
    sort = request.GET.get('sort', '-fecha_creacion')
    if sort:
        raffles = raffles.order_by(sort)

    # Estadísticas (antes de paginar)
    total_raffles = Raffle.objects.count()
    raffles_activas = Raffle.objects.filter(estado='activa').count()
    raffles_finalizadas = Raffle.objects.filter(estado='finalizada').count()
    raffles_canceladas = Raffle.objects.filter(estado='cancelada').count()

    # Paginación
    paginator = Paginator(raffles, 20)
    page_number = request.GET.get('page')
    raffles_page = paginator.get_page(page_number)

    context = {
        'raffles': raffles_page,
        'total_raffles': total_raffles,
        'raffles_activas': raffles_activas,
        'raffles_finalizadas': raffles_finalizadas,
        'raffles_canceladas': raffles_canceladas,
        'current_search': search,
    }

    return render(request, 'admin_panel/raffles.html', context)

@login_required
@user_passes_test(is_admin)
def payments_management_view(request):
    from django.core.paginator import Paginator
    from datetime import datetime

    payments = Payment.objects.select_related('usuario').all()

    # Búsqueda avanzada
    search = request.GET.get('search', '')
    if search:
        payments = payments.filter(
            Q(transaction_id__icontains=search) |
            Q(usuario__nombre__icontains=search) |
            Q(usuario__email__icontains=search) |
            Q(descripcion__icontains=search)
        )

    # Filtro por estado
    estado_filter = request.GET.get('estado', '')
    if estado_filter:
        payments = payments.filter(estado=estado_filter)

    # Filtro por método de pago
    metodo_filter = request.GET.get('metodo', '')
    if metodo_filter:
        payments = payments.filter(metodo_pago=metodo_filter)

    # Filtro por rango de fechas
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            payments = payments.filter(fecha_creacion__gte=fecha_desde_dt)
        except ValueError:
            pass

    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            # Agregar 1 día para incluir todo el día
            fecha_hasta_dt = fecha_hasta_dt.replace(hour=23, minute=59, second=59)
            payments = payments.filter(fecha_creacion__lte=fecha_hasta_dt)
        except ValueError:
            pass

    # Filtro por rango de monto
    monto_min = request.GET.get('monto_min', '')
    monto_max = request.GET.get('monto_max', '')

    if monto_min:
        try:
            payments = payments.filter(monto__gte=float(monto_min))
        except ValueError:
            pass

    if monto_max:
        try:
            payments = payments.filter(monto__lte=float(monto_max))
        except ValueError:
            pass

    # Ordenamiento
    sort = request.GET.get('sort', '-fecha_creacion')
    valid_sorts = ['fecha_creacion', '-fecha_creacion', 'monto', '-monto', 'usuario__nombre', '-usuario__nombre']
    if sort in valid_sorts:
        payments = payments.order_by(sort)
    else:
        payments = payments.order_by('-fecha_creacion')

    # Estadísticas generales (sin filtros para dashboard)
    total_pagos = Payment.objects.count()
    pagos_completados = Payment.objects.filter(estado='completado').count()
    pagos_pendientes = Payment.objects.filter(estado='pendiente').count()
    pagos_procesando = Payment.objects.filter(estado='procesando').count()
    pagos_fallidos = Payment.objects.filter(estado='fallido').count()
    pagos_reembolsados = Payment.objects.filter(estado='reembolsado').count()

    # Ingresos
    total_ingresos = Payment.objects.filter(estado='completado').aggregate(total=Sum('monto'))['total'] or 0
    ingresos_pendientes = Payment.objects.filter(estado='pendiente').aggregate(total=Sum('monto'))['total'] or 0
    monto_reembolsado = Payment.objects.filter(estado='reembolsado').aggregate(total=Sum('monto'))['total'] or 0

    # Estadísticas por método de pago
    pagos_por_metodo = Payment.objects.filter(estado='completado').values('metodo_pago').annotate(
        total=Count('id'),
        monto_total=Sum('monto')
    ).order_by('-monto_total')

    # Últimas transacciones (para estadísticas rápidas)
    today = timezone.now().date()
    pagos_hoy = Payment.objects.filter(fecha_creacion__date=today).count()
    ingresos_hoy = Payment.objects.filter(
        fecha_creacion__date=today,
        estado='completado'
    ).aggregate(total=Sum('monto'))['total'] or 0

    # Top usuarios por gasto
    top_clientes = Payment.objects.filter(estado='completado').values(
        'usuario__nombre', 'usuario__email', 'usuario__id'
    ).annotate(
        total_gastado=Sum('monto'),
        num_pagos=Count('id')
    ).order_by('-total_gastado')[:10]

    # Estadísticas de los pagos filtrados
    filtered_count = payments.count()
    filtered_ingresos = payments.filter(estado='completado').aggregate(total=Sum('monto'))['total'] or 0

    # Lista de usuarios únicos para filtro
    usuarios_list = User.objects.filter(
        pagos__isnull=False
    ).distinct().order_by('nombre')[:100]

    # Paginación
    paginator = Paginator(payments, 20)  # 20 pagos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'payments': page_obj,  # Para compatibilidad
        'total_pagos': total_pagos,
        'pagos_completados': pagos_completados,
        'pagos_pendientes': pagos_pendientes,
        'pagos_procesando': pagos_procesando,
        'pagos_fallidos': pagos_fallidos,
        'pagos_reembolsados': pagos_reembolsados,
        'total_ingresos': total_ingresos,
        'ingresos_pendientes': ingresos_pendientes,
        'monto_reembolsado': monto_reembolsado,
        'pagos_por_metodo': pagos_por_metodo,
        'pagos_hoy': pagos_hoy,
        'ingresos_hoy': ingresos_hoy,
        'top_clientes': top_clientes,
        'filtered_count': filtered_count,
        'filtered_ingresos': filtered_ingresos,
        'usuarios_list': usuarios_list,
        'current_search': search,
        'current_estado': estado_filter,
        'current_metodo': metodo_filter,
        'current_sort': sort,
    }

    return render(request, 'admin_panel/payments.html', context)

@login_required
@user_passes_test(is_admin)
def audit_logs_view(request):
    from django.core.paginator import Paginator
    from datetime import datetime, timedelta

    logs = AuditLog.objects.select_related('usuario').order_by('-fecha')

    # Búsqueda
    search = request.GET.get('search')
    if search:
        logs = logs.filter(
            Q(usuario__nombre__icontains=search) |
            Q(usuario__email__icontains=search) |
            Q(accion__icontains=search) |
            Q(descripcion__icontains=search)
        )

    # Filtro de acción
    accion_filter = request.GET.get('accion')
    if accion_filter:
        logs = logs.filter(accion=accion_filter)

    # Filtro de usuario
    usuario_filter = request.GET.get('usuario')
    if usuario_filter:
        logs = logs.filter(usuario_id=usuario_filter)

    # Filtros de fecha
    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
            logs = logs.filter(fecha__gte=fecha_desde_obj)
        except ValueError:
            pass

    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            # Agregar 1 día para incluir todo el día hasta
            fecha_hasta_obj = fecha_hasta_obj + timedelta(days=1)
            logs = logs.filter(fecha__lt=fecha_hasta_obj)
        except ValueError:
            pass

    # Ordenamiento
    sort = request.GET.get('sort', '-fecha')
    if sort:
        logs = logs.order_by(sort)

    # Estadísticas
    today = timezone.now().date()
    total_logs = AuditLog.objects.count()
    logs_today = AuditLog.objects.filter(fecha__date=today).count()
    logs_this_week = AuditLog.objects.filter(
        fecha__gte=today - timedelta(days=7)
    ).count()
    unique_users = AuditLog.objects.values('usuario').distinct().count()

    # Lista de usuarios para el filtro
    users_list = User.objects.filter(
        id__in=AuditLog.objects.values_list('usuario_id', flat=True).distinct()
    ).order_by('nombre')

    # Paginación
    paginator = Paginator(logs, 30)
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)

    context = {
        'logs': logs_page,
        'total_logs': total_logs,
        'logs_today': logs_today,
        'logs_this_week': logs_this_week,
        'unique_users': unique_users,
        'users_list': users_list,
        'current_search': search,
    }

    return render(request, 'admin_panel/audit_logs.html', context)

@login_required
@user_passes_test(is_admin)
def audit_log_details(request, log_id):
    """
    Vista para obtener los detalles de un registro de auditoría específico.
    Retorna JSON con todos los detalles del log.
    """
    try:
        log = get_object_or_404(AuditLog, id=log_id)

        data = {
            'success': True,
            'log': {
                'id': log.id,
                'fecha': log.fecha.strftime('%d/%m/%Y %H:%M:%S'),
                'usuario': {
                    'nombre': log.usuario.get_full_name() if log.usuario else 'Sistema',
                    'email': log.usuario.email if log.usuario else 'sistema@rifatrust.com',
                    'rol': log.usuario.get_rol_display() if log.usuario else 'Sistema',
                },
                'accion': log.accion,
                'descripcion': log.descripcion,
                'ip_address': log.ip_address or 'No disponible',
                'user_agent': log.user_agent or 'No disponible',
            }
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse(safe_json_error(e, get_error_message('database')), status=500)

@login_required
@user_passes_test(is_admin)
def export_users_excel(request):
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Usuarios"

    # Encabezados
    headers = ['ID', 'Nombre', 'Email', 'Rol', 'Fecha Registro', 'Última Conexión']
    ws.append(headers)

    # Datos
    users = User.objects.all()
    for user in users:
        ws.append([
            user.id,
            user.nombre,
            user.email,
            user.rol,
            user.fecha_registro.strftime('%Y-%m-%d %H:%M'),
            user.ultima_conexion.strftime('%Y-%m-%d %H:%M') if user.ultima_conexion else 'Nunca'
        ])

    # Crear response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=usuarios.xlsx'
    wb.save(response)
    return response

@login_required
@user_passes_test(is_admin)
def export_raffles_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Reporte de Rifas")

    # Datos
    y = 720
    raffles = Raffle.objects.all()[:50]

    p.setFont("Helvetica", 10)
    for raffle in raffles:
        p.drawString(100, y, f"{raffle.titulo} - ${raffle.precio_boleto} - {raffle.estado}")
        y -= 20
        if y < 100:
            p.showPage()
            y = 750

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=rifas.pdf'
    return response

# ==================== SUPERUSER PANEL ====================

@login_required
@user_passes_test(is_superuser_check)
def superuser_dashboard_view(request):
    """Comprehensive superuser control panel"""

    # User statistics by role
    users_stats = {
        'total': User.objects.count(),
        'participantes': User.objects.filter(rol='participante').count(),
        'organizadores': User.objects.filter(rol='organizador').count(),
        'sponsors': User.objects.filter(rol='sponsor').count(),
        'admins': User.objects.filter(rol='admin').count(),
        'pending_sponsors': User.objects.filter(rol='sponsor', cuenta_validada=False).count(),
    }

    # Raffle statistics
    raffles_stats = {
        'total': Raffle.objects.count(),
        'activas': Raffle.objects.filter(estado='activa').count(),
        'completadas': Raffle.objects.filter(estado='finalizada').count(),
        'canceladas': Raffle.objects.filter(estado='cancelada').count(),
    }

    # Payment statistics
    payments_stats = {
        'total': Payment.objects.count(),
        'completados': Payment.objects.filter(estado='completado').count(),
        'pendientes': Payment.objects.filter(estado='pendiente').count(),
        'fallidos': Payment.objects.filter(estado='fallido').count(),
        'total_amount': Payment.objects.filter(estado='completado').aggregate(Sum('monto'))['monto__sum'] or 0,
    }

    # Tickets statistics
    tickets_stats = {
        'total': Ticket.objects.count(),
        'vendidos': Ticket.objects.filter(estado='vendido').count(),
    }

    # Recent activity
    recent_users = User.objects.order_by('-fecha_registro')[:10]
    recent_raffles = Raffle.objects.select_related('organizador').order_by('-fecha_creacion')[:10]
    recent_payments = Payment.objects.select_related('usuario').order_by('-fecha_creacion')[:10]
    pending_sponsors = User.objects.filter(rol='sponsor', cuenta_validada=False).order_by('-fecha_registro')

    # All users for management
    all_users = User.objects.all().order_by('-fecha_registro')

    # All raffles for management
    all_raffles = Raffle.objects.select_related('organizador').order_by('-fecha_creacion')

    context = {
        'users_stats': users_stats,
        'raffles_stats': raffles_stats,
        'payments_stats': payments_stats,
        'tickets_stats': tickets_stats,
        'recent_users': recent_users,
        'recent_raffles': recent_raffles,
        'recent_payments': recent_payments,
        'pending_sponsors': pending_sponsors,
        'all_users': all_users,
        'all_raffles': all_raffles,
    }

    return render(request, 'admin_panel/superuser_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def approve_sponsor_ajax(request, user_id):
    """Approve sponsor account"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.cuenta_validada = True
        user.save()

        # Notificar al sponsor
        Notification.objects.create(
            usuario=user,
            tipo='sponsor_aprobado',
            titulo='¡Cuenta de Sponsor Aprobada!',
            mensaje=f'Tu cuenta de sponsor ha sido aprobada por {request.user.nombre}. Ya puedes patrocinar rifas.',
            enlace='/raffles/'
        )

        # Log action
        AuditLog.objects.create(
            usuario=request.user,
            accion='aprobar_sponsor',
            descripcion=f'Sponsor {user.email} aprobado por administrador'
        )

        return JsonResponse({'success': True, 'message': 'Sponsor aprobado exitosamente'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@user_passes_test(is_admin)
def reject_sponsor_ajax(request, user_id):
    """Reject sponsor account"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        motivo = request.POST.get('motivo', 'No especificado')

        # Notificar al sponsor antes de eliminar
        Notification.objects.create(
            usuario=user,
            tipo='sponsor_rechazado',
            titulo='Cuenta de Sponsor Rechazada',
            mensaje=f'Tu solicitud de cuenta sponsor ha sido rechazada. Motivo: {motivo}',
            enlace='/'
        )

        # Log action before deletion
        AuditLog.objects.create(
            usuario=request.user,
            accion='rechazar_sponsor',
            descripcion=f'Sponsor {user.email} rechazado. Motivo: {motivo}'
        )

        user.delete()

        return JsonResponse({'success': True, 'message': 'Sponsor rechazado y eliminado'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@user_passes_test(is_superuser_check)
def change_user_role_ajax(request, user_id):
    """Change user role"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        new_role = request.POST.get('role')

        if new_role in ['participante', 'organizador', 'sponsor', 'admin']:
            old_role = user.rol
            user.rol = new_role
            user.save()

            # Log action
            AuditLog.objects.create(
                usuario=request.user,
                accion='cambiar_rol',
                descripcion=f'Rol de {user.email} cambiado de {old_role} a {new_role}'
            )

            return JsonResponse({'success': True, 'message': f'Rol cambiado a {new_role}'})
        return JsonResponse({'success': False, 'message': 'Rol inválido'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@user_passes_test(is_superuser_check)
def suspend_user_ajax(request, user_id):
    """Suspend user account"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = False
        user.save()

        # Log action
        AuditLog.objects.create(
            usuario=request.user,
            accion='suspender_usuario',
            descripcion=f'Usuario {user.email} suspendido'
        )

        return JsonResponse({'success': True, 'message': 'Usuario suspendido'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@user_passes_test(is_superuser_check)
def activate_user_ajax(request, user_id):
    """Activate user account"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = True
        user.save()

        # Log action
        AuditLog.objects.create(
            usuario=request.user,
            accion='activar_usuario',
            descripcion=f'Usuario {user.email} activado'
        )

        return JsonResponse({'success': True, 'message': 'Usuario activado'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@user_passes_test(is_superuser_check)
def delete_user_ajax(request, user_id):
    """Delete user account"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        email = user.email

        # Log action before deletion
        AuditLog.objects.create(
            usuario=request.user,
            accion='eliminar_usuario',
            descripcion=f'Usuario {email} eliminado permanentemente'
        )

        user.delete()

        return JsonResponse({'success': True, 'message': 'Usuario eliminado'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@user_passes_test(is_superuser_check)
def cancel_raffle_ajax(request, raffle_id):
    """Cancel raffle and refund tickets"""
    if request.method == 'POST':
        raffle = get_object_or_404(Raffle, id=raffle_id)

        if raffle.estado == 'cancelada':
            return JsonResponse({'success': False, 'message': 'La rifa ya está cancelada'})

        # Cancel raffle
        raffle.estado = 'cancelada'
        raffle.save()

        # Count tickets to refund
        tickets_count = Ticket.objects.filter(rifa=raffle, estado='vendido').count()

        # Log action
        AuditLog.objects.create(
            usuario=request.user,
            accion='cancelar_rifa',
            descripcion=f'Rifa "{raffle.titulo}" cancelada. {tickets_count} boletos afectados.'
        )

        return JsonResponse({
            'success': True,
            'message': f'Rifa cancelada. {tickets_count} boletos afectados.'
        })
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@user_passes_test(is_superuser_check)
def force_winner_ajax(request, raffle_id):
    """Manually select a winner for a raffle using verifiable algorithm"""
    if request.method == 'POST':
        raffle = get_object_or_404(Raffle, id=raffle_id)

        # Verificar si ya hay un ganador
        if Winner.objects.filter(rifa=raffle).exists():
            return JsonResponse({'success': False, 'message': 'La rifa ya tiene un ganador'})

        # Get sold tickets (pagado, no vendido)
        tickets = list(Ticket.objects.filter(rifa=raffle, estado='pagado').select_related('usuario'))

        if not tickets:
            return JsonResponse({'success': False, 'message': 'No hay boletos pagados'})

        # Importar función de sorteo verificable
        from apps.raffles.views import generar_sorteo_verificable

        # Realizar sorteo verificable
        resultado_sorteo = generar_sorteo_verificable(raffle, tickets)
        winning_ticket = resultado_sorteo['winning_ticket']

        # Create winner with verification data
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

        # Update raffle status
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

        # Log action
        AuditLog.objects.create(
            usuario=request.user,
            accion='sorteo_manual',
            descripcion=f'Sorteo realizado manualmente para "{raffle.titulo}": Ganador {winning_ticket.usuario.nombre} (Boleto #{winning_ticket.numero_boleto}). Hash: {resultado_sorteo["hash_verificacion"][:16]}...'
        )

        return JsonResponse({
            'success': True,
            'message': f'Ganador seleccionado: {winning_ticket.usuario.nombre} (Boleto #{winning_ticket.numero_boleto})',
            'hash_verificacion': resultado_sorteo['hash_verificacion']
        })
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@user_passes_test(is_superuser_check)
def delete_raffle_ajax(request, raffle_id):
    """Delete raffle permanently"""
    if request.method == 'POST':
        raffle = get_object_or_404(Raffle, id=raffle_id)
        titulo = raffle.titulo

        # Log action before deletion
        AuditLog.objects.create(
            usuario=request.user,
            accion='eliminar_rifa',
            descripcion=f'Rifa "{titulo}" eliminada permanentemente'
        )

        raffle.delete()

        return JsonResponse({'success': True, 'message': 'Rifa eliminada'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@user_passes_test(is_superuser_check)
def refund_payment_ajax(request, payment_id):
    """Issue refund for a payment with reason and explanation"""
    if request.method == 'POST':
        payment = get_object_or_404(Payment, id=payment_id)

        # Validar estado del pago
        if payment.estado != 'completado':
            return JsonResponse({'success': False, 'message': 'Solo se pueden reembolsar pagos completados'})

        # Validar que no tenga ya un reembolso
        if hasattr(payment, 'reembolso'):
            return JsonResponse({'success': False, 'message': 'Este pago ya tiene un reembolso asociado'})

        # Obtener motivo y explicación
        motivo = request.POST.get('motivo', '')
        explicacion = request.POST.get('explicacion', '')

        # Validar campos requeridos
        if not motivo:
            return JsonResponse({'success': False, 'message': 'El motivo es requerido'})
        if not explicacion or len(explicacion.strip()) < 10:
            return JsonResponse({'success': False, 'message': 'La explicación debe tener al menos 10 caracteres'})

        try:
            # Crear registro de reembolso
            from apps.payments.models import Refund
            from django.utils import timezone

            refund = Refund.objects.create(
                pago=payment,
                monto=payment.monto,
                motivo=motivo,
                razon=explicacion,
                procesado_por=request.user,
                estado='completado',
                fecha_procesado=timezone.now()
            )

            # Actualizar estado del pago
            payment.estado = 'reembolsado'
            payment.notas_admin = f"Reembolsado: {motivo} - {explicacion[:100]}"
            payment.save()

            # Registrar en audit log
            AuditLog.objects.create(
                usuario=request.user,
                accion='reembolso',
                modelo='Payment',
                objeto_id=payment.id,
                descripcion=f'Reembolso de CLP${payment.monto} para {payment.usuario.email}. Motivo: {dict(Refund.MOTIVOS).get(motivo)}. Explicación: {explicacion[:100]}...'
            )

            return JsonResponse({
                'success': True,
                'message': 'Reembolso procesado exitosamente',
                'refund_id': refund.id
            })

        except Exception as e:
            return JsonResponse(safe_json_error(e, get_error_message('refund')))

    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@user_passes_test(is_admin)
def rifas_pausadas_view(request):
    """Vista para gestionar rifas pausadas que requieren revisión"""

    # Obtener todas las rifas pausadas
    rifas_pausadas = Raffle.objects.filter(estado='pausada').order_by('-fecha_pausa')

    context = {
        'rifas_pausadas': rifas_pausadas,
        'total_pausadas': rifas_pausadas.count(),
    }

    return render(request, 'admin_panel/rifas_pausadas.html', context)

@login_required
@user_passes_test(is_admin)
def revisar_rifa_pausada(request, rifa_id):
    """Procesar la decisión del administrador sobre una rifa pausada"""

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})

    try:
        rifa = get_object_or_404(Raffle, id=rifa_id, estado='pausada')

        accion = request.POST.get('accion')
        comentarios = request.POST.get('comentarios', '')

        if accion == 'extender':
            # Extender el plazo
            dias_extension = int(request.POST.get('dias_extension', 7))
            nueva_fecha = timezone.now() + timezone.timedelta(days=dias_extension)

            rifa.nueva_fecha_sorteo = nueva_fecha
            rifa.fecha_sorteo = nueva_fecha
            rifa.estado = 'activa'
            rifa.revision_admin = f"Plazo extendido por {dias_extension} días. {comentarios}"
            rifa.fecha_revision = timezone.now()
            rifa.save()

            # Registrar en audit log
            AuditLog.objects.create(
                usuario=request.user,
                accion='extender_plazo',
                modelo='Raffle',
                objeto_id=rifa.id,
                descripcion=f'Plazo de rifa "{rifa.titulo}" extendido hasta {nueva_fecha.strftime("%d/%m/%Y %H:%M")}. {comentarios[:100]}'
            )

            messages.success(request, f'✅ Plazo extendido. Nueva fecha: {nueva_fecha.strftime("%d/%m/%Y %H:%M")}')

        elif accion == 'cancelar':
            # Obtener todos los boletos pagados de esta rifa
            boletos_pagados = Ticket.objects.filter(rifa=rifa, estado='pagado')
            total_boletos_reembolsar = boletos_pagados.count()

            if total_boletos_reembolsar > 0:
                # Procesar reembolsos automáticos
                from apps.payments.models import Payment, Refund

                reembolsos_exitosos = 0
                reembolsos_fallidos = 0
                monto_total_reembolsado = 0

                for boleto in boletos_pagados:
                    try:
                        # Buscar el pago asociado al boleto
                        pago = Payment.objects.filter(
                            usuario=boleto.usuario,
                            rifa=rifa,
                            estado='completado'
                        ).first()

                        if pago:
                            # Crear registro de reembolso
                            refund = Refund.objects.create(
                                pago=pago,
                                procesado_por=request.user,
                                motivo='cancelacion',
                                razon=f'Reembolso automático por cancelación de rifa. Motivo: {comentarios[:100]}',
                                monto=pago.monto,
                                estado='completado',
                                fecha_procesado=timezone.now()
                            )

                            # Actualizar estado del pago
                            pago.estado = 'reembolsado'
                            pago.notas_admin = f'Reembolso automático por cancelación de rifa #{rifa.id}. {comentarios[:50]}'
                            pago.save()

                            # Actualizar estado del boleto
                            boleto.estado = 'cancelado'
                            boleto.save()

                            monto_total_reembolsado += pago.monto
                            reembolsos_exitosos += 1

                            # Registrar en audit log individual
                            AuditLog.objects.create(
                                usuario=request.user,
                                accion='reembolso_automatico',
                                modelo='Payment',
                                objeto_id=pago.id,
                                descripcion=f'Reembolso automático de ${pago.monto} a {boleto.usuario.email} por cancelación de rifa "{rifa.titulo}"'
                            )

                    except Exception as e:
                        reembolsos_fallidos += 1
                        # Log del error pero continuar con los demás
                        AuditLog.objects.create(
                            usuario=request.user,
                            accion='error_reembolso',
                            modelo='Ticket',
                            objeto_id=boleto.id,
                            descripcion=f'Error al reembolsar boleto #{boleto.numero_boleto} a {boleto.usuario.email}: {str(e)}'
                        )

                # Actualizar estado de la rifa
                rifa.estado = 'cancelada'
                rifa.revision_admin = f"Rifa cancelada. {comentarios}. Reembolsos: {reembolsos_exitosos} exitosos, {reembolsos_fallidos} fallidos. Total reembolsado: ${monto_total_reembolsado:,.0f}"
                rifa.fecha_revision = timezone.now()
                rifa.save()

                # Registrar en audit log principal
                AuditLog.objects.create(
                    usuario=request.user,
                    accion='cancelar_rifa_con_reembolsos',
                    modelo='Raffle',
                    objeto_id=rifa.id,
                    descripcion=f'Rifa "{rifa.titulo}" cancelada con {reembolsos_exitosos} reembolsos automáticos (${monto_total_reembolsado:,.0f}). Motivo: {comentarios[:100]}'
                )

                if reembolsos_fallidos > 0:
                    messages.warning(request, f'⚠️ Rifa cancelada. {reembolsos_exitosos} reembolsos exitosos, {reembolsos_fallidos} fallidos. Revisar logs.')
                else:
                    messages.success(request, f'✅ Rifa cancelada. {reembolsos_exitosos} reembolsos procesados automáticamente (${monto_total_reembolsado:,.0f})')
            else:
                # No hay boletos vendidos, cancelar directamente
                rifa.estado = 'cancelada'
                rifa.revision_admin = f"Rifa cancelada por administración. Sin boletos vendidos. {comentarios}"
                rifa.fecha_revision = timezone.now()
                rifa.save()

                # Registrar en audit log
                AuditLog.objects.create(
                    usuario=request.user,
                    accion='cancelar_rifa',
                    modelo='Raffle',
                    objeto_id=rifa.id,
                    descripcion=f'Rifa "{rifa.titulo}" cancelada sin boletos vendidos. Motivo: {comentarios[:100]}'
                )

                messages.success(request, '✅ Rifa cancelada exitosamente (sin boletos vendidos)')

        elif accion == 'aprobar':
            # Aprobar para sorteo aunque no se vendieron todos los boletos
            boletos_vendidos_count = Ticket.objects.filter(rifa=rifa, estado='pagado').count()

            rifa.estado = 'cerrada'
            rifa.revision_admin = f"Aprobada para sorteo con {boletos_vendidos_count} boletos vendidos. {comentarios}"
            rifa.fecha_revision = timezone.now()
            rifa.save()

            # Registrar en audit log
            AuditLog.objects.create(
                usuario=request.user,
                accion='aprobar_sorteo_parcial',
                modelo='Raffle',
                objeto_id=rifa.id,
                descripcion=f'Rifa "{rifa.titulo}" aprobada para sorteo con {boletos_vendidos_count}/{rifa.total_boletos} boletos vendidos. {comentarios[:100]}'
            )

            messages.success(request, f'✅ Rifa aprobada para sorteo ({boletos_vendidos_count} boletos vendidos)')

        else:
            return JsonResponse({'success': False, 'message': 'Acción no válida'})

        return JsonResponse({
            'success': True,
            'message': 'Decisión registrada exitosamente',
            'redirect': '/admin-panel/rifas-pausadas/'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

@login_required
@user_passes_test(is_admin)
def rifas_pendientes_view(request):
    """Vista para mostrar rifas pendientes de aprobación"""
    rifas_pendientes = Raffle.objects.filter(estado='pendiente_aprobacion').select_related('organizador').order_by('-fecha_solicitud')

    context = {
        'rifas_pendientes': rifas_pendientes,
        'total_pendientes': rifas_pendientes.count()
    }

    return render(request, 'admin_panel/rifas_pendientes.html', context)

@login_required
@user_passes_test(is_admin)
def revisar_rifa_pendiente(request, rifa_id):
    """Vista para aprobar o rechazar una rifa pendiente"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})

    try:
        rifa = get_object_or_404(Raffle, id=rifa_id, estado='pendiente_aprobacion')
        accion = request.POST.get('accion')
        comentarios = request.POST.get('comentarios', '')

        if accion == 'aprobar':
            rifa.estado = 'aprobada'
            rifa.revisado_por = request.user
            rifa.fecha_revision_aprobacion = timezone.now()
            rifa.comentarios_revision = comentarios
            rifa.save()

            # Notificar al organizador
            Notification.objects.create(
                usuario=rifa.organizador,
                tipo='sistema',
                titulo='¡Tu rifa ha sido aprobada!',
                mensaje=f'Tu rifa "{rifa.titulo}" ha sido aprobada por {request.user.nombre}. Ahora puedes activarla para que sea visible al público.',
                enlace=f'/raffles/{rifa.id}/edit/',
                rifa_relacionada=rifa
            )

            # Registrar en el log de auditoría
            AuditLog.objects.create(
                usuario=request.user,
                accion='aprobar_rifa',
                modelo='Raffle',
                objeto_id=rifa.id,
                descripcion=f'Rifa "{rifa.titulo}" aprobada. Comentarios: {comentarios}'
            )

            messages.success(request, f'Rifa "{rifa.titulo}" aprobada exitosamente.')

        elif accion == 'rechazar':
            motivo = request.POST.get('motivo_rechazo', '')

            rifa.estado = 'rechazada'
            rifa.revisado_por = request.user
            rifa.fecha_revision_aprobacion = timezone.now()
            rifa.motivo_rechazo = motivo
            rifa.comentarios_revision = comentarios
            rifa.save()

            # Notificar al organizador
            Notification.objects.create(
                usuario=rifa.organizador,
                tipo='cancelacion',
                titulo='Tu rifa ha sido rechazada',
                mensaje=f'Tu rifa "{rifa.titulo}" ha sido rechazada. Motivo: {motivo}. Por favor revisa los comentarios y corrige los problemas.',
                enlace=f'/raffles/{rifa.id}/edit/',
                rifa_relacionada=rifa
            )

            # Registrar en el log de auditoría
            AuditLog.objects.create(
                usuario=request.user,
                accion='rechazar_rifa',
                modelo='Raffle',
                objeto_id=rifa.id,
                descripcion=f'Rifa "{rifa.titulo}" rechazada. Motivo: {motivo}. Comentarios: {comentarios}'
            )

            messages.warning(request, f'Rifa "{rifa.titulo}" rechazada.')

        else:
            return JsonResponse({'success': False, 'message': 'Acción no válida'})

        return JsonResponse({
            'success': True,
            'message': 'Revisión completada exitosamente',
            'redirect': '/admin-panel/rifas-pendientes/'
        })

    except Exception as e:
        return JsonResponse(safe_json_error(e, get_error_message('server')))


@login_required
@user_passes_test(is_admin)
def test_email_verification_view(request):
    """
    Vista de prueba para verificar emails usando la API de AbstractAPI

    Uso: /admin-panel/test-email/?email=test@gmail.com

    Retorna:
        JSON con el resultado de la verificación o HTML si no se proporciona email
    """
    email = request.GET.get('email', '').strip()

    # Si no hay email, mostrar formulario de prueba
    if not email:
        return render(request, 'admin_panel/test_email_verification.html')

    # Verificar el email
    result = verify_email(email)

    # Si es petición AJAX, retornar JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(result)

    # Si es petición normal, mostrar resultado en HTML
    context = {
        'email': email,
        'result': result,
        'report': get_email_report(email)
    }
    return render(request, 'admin_panel/test_email_verification.html', context)
