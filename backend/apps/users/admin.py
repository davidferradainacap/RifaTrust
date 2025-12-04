from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import User, Profile, Notification, EmailConfirmationToken, PasswordResetToken

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administrador avanzado de usuarios con funcionalidades empresariales.
    Diseñado siguiendo las mejores prácticas de gestión de usuarios.
    """

    # Configuración de listado
    list_display = [
        'id',
        'colored_email',
        'nombre_completo',
        'rol_badge',
        'status_badge',
        'cuenta_validada_icon',
        'tickets_count',
        'rifas_organizadas_count',
        'total_gastado_display',
        'fecha_registro_formatted',
        'ultima_actividad',
        'actions_column',
    ]

    list_display_links = ['id', 'colored_email']

    list_filter = [
        'rol',
        'is_active',
        'cuenta_validada',
        'is_staff',
        'is_superuser',
        ('fecha_registro', admin.DateFieldListFilter),
        ('ultima_conexion', admin.DateFieldListFilter),
    ]

    search_fields = [
        'email',
        'nombre',
        'telefono',
        'id',
    ]

    readonly_fields = [
        'fecha_registro',
        'ultima_conexion',
        'user_statistics',
        'activity_timeline',
        'notifications_summary',
    ]

    ordering = ['-fecha_registro']

    list_per_page = 25

    date_hierarchy = 'fecha_registro'

    # Acciones masivas
    actions = [
        'activate_users',
        'deactivate_users',
        'validate_accounts',
        'promote_to_organizer',
        'send_notification',
        'export_users_csv',
    ]

    # Fieldsets para vista de detalle/edición
    fieldsets = (
        ('🔐 Credenciales de Acceso', {
            'fields': ('email', 'password'),
            'classes': ('wide',),
        }),
        ('👤 Información Personal', {
            'fields': ('nombre', 'telefono', 'avatar'),
            'classes': ('wide',),
        }),
        ('🎭 Roles y Permisos', {
            'fields': (
                'rol',
                'cuenta_validada',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
            'classes': ('collapse',),
        }),
        ('📊 Estadísticas del Usuario', {
            'fields': ('user_statistics',),
            'classes': ('wide',),
        }),
        ('⏱️ Actividad y Seguimiento', {
            'fields': ('activity_timeline',),
            'classes': ('wide',),
        }),
        ('📬 Notificaciones', {
            'fields': ('notifications_summary',),
            'classes': ('wide',),
        }),
        ('📅 Información Temporal', {
            'fields': ('fecha_registro', 'ultima_conexion'),
            'classes': ('collapse',),
        }),
    )

    # Fieldsets para agregar usuario
    add_fieldsets = (
        ('🔐 Crear Nuevo Usuario', {
            'classes': ('wide',),
            'fields': (
                'email',
                'nombre',
                'telefono',
                'rol',
                'password1',
                'password2',
                'cuenta_validada',
                'is_active',
            ),
            'description': 'Complete los siguientes campos para crear un nuevo usuario en el sistema.',
        }),
    )

    # Métodos personalizados para el listado

    @admin.display(description='📧 Email', ordering='email')
    def colored_email(self, obj):
        """Email con color según el estado del usuario"""
        color = '#28a745' if obj.is_active else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: 500;">{}</span>',
            color,
            obj.email
        )

    @admin.display(description='👤 Nombre', ordering='nombre')
    def nombre_completo(self, obj):
        """Nombre con avatar si existe"""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 30px; height: 30px; border-radius: 50%; '
                'object-fit: cover; margin-right: 8px; vertical-align: middle;"> {}',
                obj.avatar.url,
                obj.nombre
            )
        return obj.nombre

    @admin.display(description='🎭 Rol', ordering='rol')
    def rol_badge(self, obj):
        """Badge con color según el rol"""
        colors = {
            'participante': '#007bff',
            'organizador': '#28a745',
            'sponsor': '#ffc107',
            'admin': '#dc3545',
        }
        icons = {
            'participante': '👤',
            'organizador': '🎯',
            'sponsor': '💼',
            'admin': '⚙️',
        }
        color = colors.get(obj.rol, '#6c757d')
        icon = icons.get(obj.rol, '❓')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600; '
            'display: inline-block; white-space: nowrap;">{} {}</span>',
            color,
            icon,
            obj.get_rol_display()
        )

    @admin.display(description='✅ Estado', ordering='is_active')
    def status_badge(self, obj):
        """Badge de estado activo/inactivo"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: 600;">✓ Activo</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">✗ Inactivo</span>'
        )

    @admin.display(description='🔒 Validado', ordering='cuenta_validada', boolean=True)
    def cuenta_validada_icon(self, obj):
        """Icono de validación de cuenta"""
        return obj.cuenta_validada

    @admin.display(description='🎫 Boletos', ordering='tickets_count')
    def tickets_count(self, obj):
        """Cantidad de boletos comprados"""
        from apps.raffles.models import Ticket
        count = Ticket.objects.filter(usuario=obj, estado='pagado').count()
        if count > 0:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
                count
            )
        return format_html('<span style="color: #999;">0</span>')

    @admin.display(description='🎯 Rifas Org.', ordering='rifas_count')
    def rifas_organizadas_count(self, obj):
        """Cantidad de rifas organizadas"""
        from apps.raffles.models import Raffle
        count = Raffle.objects.filter(organizador=obj).count()
        if count > 0:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
                count
            )
        return format_html('<span style="color: #999;">-</span>')

    @admin.display(description='💰 Total Gastado')
    def total_gastado_display(self, obj):
        """Total gastado en boletos"""
        from apps.payments.models import Payment
        from django.db.models import Sum
        total = Payment.objects.filter(
            usuario=obj,
            estado='completado'
        ).aggregate(total=Sum('monto'))['total'] or 0

        if total > 0:
            return format_html(
                '<span style="color: #28a745; font-weight: 600;">${:,.0f}</span>',
                total
            )
        return format_html('<span style="color: #999;">$0</span>')

    @admin.display(description='📅 Registro', ordering='fecha_registro')
    def fecha_registro_formatted(self, obj):
        """Fecha de registro formateada"""
        return obj.fecha_registro.strftime('%d/%m/%Y %H:%M')

    @admin.display(description='⏰ Última Actividad', ordering='ultima_conexion')
    def ultima_actividad(self, obj):
        """Última conexión con indicador de actividad reciente"""
        if not obj.ultima_conexion:
            return format_html('<span style="color: #999;">Nunca</span>')

        now = timezone.now()
        diff = now - obj.ultima_conexion

        if diff < timedelta(hours=1):
            color = '#28a745'
            text = 'Hace minutos'
        elif diff < timedelta(days=1):
            color = '#ffc107'
            text = 'Hoy'
        elif diff < timedelta(days=7):
            color = '#17a2b8'
            text = f'Hace {diff.days} días'
        else:
            color = '#6c757d'
            text = obj.ultima_conexion.strftime('%d/%m/%Y')

        return format_html(
            '<span style="color: {}; font-size: 11px;">{}</span>',
            color,
            text
        )

    @admin.display(description='⚡ Acciones')
    def actions_column(self, obj):
        """Botones de acción rápida"""
        return format_html(
            '<a class="button" href="{}" style="padding: 4px 8px; margin: 2px; '
            'background-color: #17a2b8; color: white; border-radius: 4px; '
            'text-decoration: none; font-size: 11px;">Ver Perfil</a> '
            '<a class="button" href="{}" style="padding: 4px 8px; margin: 2px; '
            'background-color: #28a745; color: white; border-radius: 4px; '
            'text-decoration: none; font-size: 11px;">Editar</a>',
            reverse('admin:users_user_change', args=[obj.pk]),
            reverse('admin:users_user_change', args=[obj.pk])
        )

    # Métodos personalizados para los fieldsets

    @admin.display(description='📊 Estadísticas Completas')
    def user_statistics(self, obj):
        """Panel de estadísticas completo del usuario"""
        from apps.raffles.models import Ticket, Raffle, Winner
        from apps.payments.models import Payment
        from django.db.models import Sum

        # Obtener estadísticas
        tickets_comprados = Ticket.objects.filter(usuario=obj, estado='pagado').count()
        rifas_organizadas = Raffle.objects.filter(organizador=obj).count()
        rifas_ganadas = Winner.objects.filter(boleto__usuario=obj).count()

        total_pagado = Payment.objects.filter(
            usuario=obj,
            estado='completado'
        ).aggregate(total=Sum('monto'))['total'] or 0

        total_recaudado = 0
        if rifas_organizadas > 0:
            from apps.raffles.models import Ticket
            total_recaudado = Ticket.objects.filter(
                rifa__organizador=obj,
                estado='pagado'
            ).aggregate(
                total=Sum('rifa__precio_boleto')
            )['total'] or 0

        notificaciones_no_leidas = Notification.objects.filter(
            usuario=obj,
            leida=False
        ).count()

        return format_html(
            '''
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;
                        border-left: 4px solid #007bff;">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                    <div style="background: white; padding: 15px; border-radius: 6px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="color: #6c757d; font-size: 12px; margin-bottom: 5px;">
                            🎫 BOLETOS COMPRADOS
                        </div>
                        <div style="font-size: 24px; font-weight: bold; color: #007bff;">
                            {}
                        </div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 6px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="color: #6c757d; font-size: 12px; margin-bottom: 5px;">
                            🎯 RIFAS ORGANIZADAS
                        </div>
                        <div style="font-size: 24px; font-weight: bold; color: #28a745;">
                            {}
                        </div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 6px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="color: #6c757d; font-size: 12px; margin-bottom: 5px;">
                            🏆 RIFAS GANADAS
                        </div>
                        <div style="font-size: 24px; font-weight: bold; color: #ffc107;">
                            {}
                        </div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 6px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="color: #6c757d; font-size: 12px; margin-bottom: 5px;">
                            💰 TOTAL PAGADO
                        </div>
                        <div style="font-size: 20px; font-weight: bold; color: #dc3545;">
                            ${:,.0f}
                        </div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 6px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="color: #6c757d; font-size: 12px; margin-bottom: 5px;">
                            💵 TOTAL RECAUDADO
                        </div>
                        <div style="font-size: 20px; font-weight: bold; color: #28a745;">
                            ${:,.0f}
                        </div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 6px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="color: #6c757d; font-size: 12px; margin-bottom: 5px;">
                            📬 NOTIFICACIONES
                        </div>
                        <div style="font-size: 20px; font-weight: bold; color: #17a2b8;">
                            {} sin leer
                        </div>
                    </div>
                </div>
            </div>
            ''',
            tickets_comprados,
            rifas_organizadas,
            rifas_ganadas,
            total_pagado,
            total_recaudado,
            notificaciones_no_leidas
        )

    @admin.display(description='📈 Línea de Tiempo')
    def activity_timeline(self, obj):
        """Línea de tiempo de actividad del usuario"""
        from apps.raffles.models import Ticket, Raffle
        from apps.payments.models import Payment

        # Obtener actividad reciente
        recent_tickets = Ticket.objects.filter(
            usuario=obj,
            estado='pagado'
        ).order_by('-fecha_compra')[:5]

        recent_raffles = Raffle.objects.filter(
            organizador=obj
        ).order_by('-fecha_creacion')[:5]

        html = '<div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">'
        html += '<h4 style="margin-top: 0; color: #495057;">Actividad Reciente</h4>'

        if recent_tickets:
            html += '<div style="margin-bottom: 20px;"><strong>🎫 Últimas Compras:</strong><ul style="margin: 10px 0;">'
            for ticket in recent_tickets:
                html += f'<li style="margin: 5px 0;">{ticket.rifa.titulo} - {ticket.fecha_compra.strftime("%d/%m/%Y")}</li>'
            html += '</ul></div>'

        if recent_raffles:
            html += '<div><strong>🎯 Últimas Rifas Creadas:</strong><ul style="margin: 10px 0;">'
            for raffle in recent_raffles:
                html += f'<li style="margin: 5px 0;">{raffle.titulo} - {raffle.fecha_creacion.strftime("%d/%m/%Y")}</li>'
            html += '</ul></div>'

        if not recent_tickets and not recent_raffles:
            html += '<p style="color: #6c757d; font-style: italic;">No hay actividad reciente</p>'

        html += '</div>'
        return mark_safe(html)

    @admin.display(description='📬 Resumen de Notificaciones')
    def notifications_summary(self, obj):
        """Resumen de notificaciones del usuario"""
        notifications = Notification.objects.filter(usuario=obj).order_by('-fecha_creacion')[:10]
        no_leidas = notifications.filter(leida=False).count()

        html = '<div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">'
        html += f'<h4 style="margin-top: 0; color: #495057;">📬 Notificaciones ({no_leidas} sin leer)</h4>'

        if notifications:
            html += '<ul style="list-style: none; padding: 0; margin: 0;">'
            for notif in notifications:
                icon = '🔵' if not notif.leida else '✅'
                html += f'''
                <li style="padding: 10px; margin: 5px 0; background: white;
                           border-radius: 4px; border-left: 3px solid {"#007bff" if not notif.leida else "#28a745"};">
                    {icon} <strong>{notif.titulo}</strong><br>
                    <small style="color: #6c757d;">{notif.fecha_creacion.strftime("%d/%m/%Y %H:%M")}</small>
                </li>
                '''
            html += '</ul>'
        else:
            html += '<p style="color: #6c757d; font-style: italic;">No hay notificaciones</p>'

        html += '</div>'
        return mark_safe(html)

    # Optimización de queries
    def get_queryset(self, request):
        """Optimiza las consultas con prefetch"""
        qs = super().get_queryset(request)
        return qs.select_related('profile').prefetch_related(
            'rifas_organizadas',
            'boletos_comprados',
            'notificaciones'
        )

    # Acciones masivas personalizadas

    @admin.action(description='✅ Activar usuarios seleccionados')
    def activate_users(self, request, queryset):
        """Activa usuarios masivamente"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} usuario(s) activado(s) exitosamente.',
            level='success'
        )

    @admin.action(description='🚫 Desactivar usuarios seleccionados')
    def deactivate_users(self, request, queryset):
        """Desactiva usuarios masivamente"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} usuario(s) desactivado(s) exitosamente.',
            level='warning'
        )

    @admin.action(description='🔓 Validar cuentas seleccionadas')
    def validate_accounts(self, request, queryset):
        """Valida cuentas masivamente"""
        updated = queryset.update(cuenta_validada=True)
        self.message_user(
            request,
            f'{updated} cuenta(s) validada(s) exitosamente.',
            level='success'
        )

    @admin.action(description='⬆️ Promover a Organizador')
    def promote_to_organizer(self, request, queryset):
        """Promueve usuarios a organizador"""
        updated = queryset.filter(rol='participante').update(rol='organizador')
        self.message_user(
            request,
            f'{updated} usuario(s) promovido(s) a Organizador.',
            level='success'
        )

    @admin.action(description='📧 Enviar notificación')
    def send_notification(self, request, queryset):
        """Envía notificación a usuarios seleccionados"""
        for user in queryset:
            Notification.objects.create(
                usuario=user,
                tipo='sistema',
                titulo='Notificación del Sistema',
                mensaje='Este es un mensaje enviado desde el panel administrativo.',
            )
        self.message_user(
            request,
            f'Notificación enviada a {queryset.count()} usuario(s).',
            level='success'
        )

    @admin.action(description='📥 Exportar a CSV')
    def export_users_csv(self, request, queryset):
        """Exporta usuarios a CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Email', 'Nombre', 'Rol', 'Activo', 'Fecha Registro'])

        for user in queryset:
            writer.writerow([
                user.id,
                user.email,
                user.nombre,
                user.rol,
                'Sí' if user.is_active else 'No',
                user.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Administrador de perfiles de usuario.
    """
    list_display = [
        'user_info',
        'ciudad_pais',
        'edad_calculada',
        'profile_completion',
    ]

    list_filter = ['pais', 'ciudad']

    search_fields = [
        'user__nombre',
        'user__email',
        'ciudad',
        'pais',
    ]

    readonly_fields = ['user']

    fieldsets = (
        ('👤 Usuario', {
            'fields': ('user',)
        }),
        ('📍 Ubicación', {
            'fields': ('direccion', 'ciudad', 'estado', 'codigo_postal', 'pais')
        }),
        ('📅 Información Personal', {
            'fields': ('fecha_nacimiento',)
        }),
    )

    @admin.display(description='Usuario')
    def user_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color: #6c757d;">{}</small>',
            obj.user.nombre,
            obj.user.email
        )

    @admin.display(description='Ubicación')
    def ciudad_pais(self, obj):
        if obj.ciudad and obj.pais:
            return f"{obj.ciudad}, {obj.pais}"
        return obj.pais or '-'

    @admin.display(description='Edad')
    def edad_calculada(self, obj):
        if obj.fecha_nacimiento:
            from datetime import date
            today = date.today()
            edad = today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
            return f"{edad} años"
        return '-'

    @admin.display(description='Completitud')
    def profile_completion(self, obj):
        total_fields = 6
        completed_fields = sum([
            bool(obj.direccion),
            bool(obj.ciudad),
            bool(obj.estado),
            bool(obj.codigo_postal),
            bool(obj.pais),
            bool(obj.fecha_nacimiento),
        ])
        percentage = (completed_fields / total_fields) * 100

        color = '#28a745' if percentage >= 80 else '#ffc107' if percentage >= 50 else '#dc3545'

        return format_html(
            '<div style="width: 100px; background: #e9ecef; border-radius: 10px; '
            'height: 20px; position: relative;">'
            '<div style="width: {}%; background: {}; border-radius: 10px; '
            'height: 100%; display: flex; align-items: center; justify-content: center;">'
            '<span style="font-size: 10px; color: white; font-weight: bold;">{:.0f}%</span>'
            '</div></div>',
            percentage,
            color,
            percentage
        )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Administrador de notificaciones.
    """
    list_display = [
        'id',
        'usuario_info',
        'tipo_badge',
        'titulo_corto',
        'leida_icon',
        'fecha_creacion_formatted',
        'rifa_relacionada_link',
    ]

    list_filter = ['tipo', 'leida', 'fecha_creacion']

    search_fields = ['usuario__nombre', 'usuario__email', 'titulo', 'mensaje']

    readonly_fields = ['fecha_creacion', 'fecha_lectura']

    date_hierarchy = 'fecha_creacion'

    actions = ['mark_as_read', 'mark_as_unread', 'delete_read_notifications']

    @admin.display(description='Usuario')
    def usuario_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.usuario.nombre,
            obj.usuario.email
        )

    @admin.display(description='Tipo', ordering='tipo')
    def tipo_badge(self, obj):
        colors = {
            'compra': '#007bff',
            'ganador': '#28a745',
            'sorteo': '#ffc107',
            'cancelacion': '#dc3545',
            'nuevo_organizador': '#17a2b8',
            'recordatorio': '#6610f2',
            'sistema': '#6c757d',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 10px; font-weight: 600;">{}</span>',
            colors.get(obj.tipo, '#6c757d'),
            obj.get_tipo_display()
        )

    @admin.display(description='Título')
    def titulo_corto(self, obj):
        return obj.titulo[:50] + '...' if len(obj.titulo) > 50 else obj.titulo

    @admin.display(description='Leída', ordering='leida', boolean=True)
    def leida_icon(self, obj):
        return obj.leida

    @admin.display(description='Fecha', ordering='fecha_creacion')
    def fecha_creacion_formatted(self, obj):
        return obj.fecha_creacion.strftime('%d/%m/%Y %H:%M')

    @admin.display(description='Rifa')
    def rifa_relacionada_link(self, obj):
        if obj.rifa_relacionada:
            return format_html(
                '<a href="{}" style="color: #007bff;">{}</a>',
                reverse('admin:raffles_raffle_change', args=[obj.rifa_relacionada.pk]),
                obj.rifa_relacionada.titulo[:30]
            )
        return '-'

    @admin.action(description='✅ Marcar como leídas')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(leida=True, fecha_lectura=timezone.now())
        self.message_user(request, f'{updated} notificación(es) marcada(s) como leídas.')

    @admin.action(description='📭 Marcar como no leídas')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(leida=False, fecha_lectura=None)
        self.message_user(request, f'{updated} notificación(es) marcada(s) como no leídas.')

    @admin.action(description='🗑️ Eliminar notificaciones leídas')
    def delete_read_notifications(self, request, queryset):
        deleted = queryset.filter(leida=True).delete()[0]
        self.message_user(request, f'{deleted} notificación(es) leída(s) eliminada(s).')


@admin.register(EmailConfirmationToken)
class EmailConfirmationTokenAdmin(admin.ModelAdmin):
    """
    Administrador de tokens de confirmación de email
    """

    list_display = [
        'id',
        'user_email',
        'token_short',
        'status_badge',
        'created_at_formatted',
        'expires_at_formatted',
        'time_remaining_display',
        'used_at_formatted',
    ]

    list_filter = [
        'is_used',
        ('created_at', admin.DateFieldListFilter),
        ('expires_at', admin.DateFieldListFilter),
    ]

    search_fields = [
        'user__email',
        'user__nombre',
        'token',
    ]

    readonly_fields = [
        'user',
        'token',
        'created_at',
        'expires_at',
        'is_used',
        'used_at',
        'is_valid_display',
        'time_remaining_display',
    ]

    list_per_page = 50

    fieldsets = (
        ('Información del Token', {
            'fields': ('user', 'token', 'is_valid_display')
        }),
        ('Fechas', {
            'fields': ('created_at', 'expires_at', 'time_remaining_display')
        }),
        ('Estado', {
            'fields': ('is_used', 'used_at')
        }),
    )

    @admin.display(description='Email del Usuario')
    def user_email(self, obj):
        return format_html(
            '<a href="{}" style="color: #007bff;">{}</a>',
            reverse('admin:users_user_change', args=[obj.user.pk]),
            obj.user.email
        )

    @admin.display(description='Token')
    def token_short(self, obj):
        return f"{obj.token[:16]}...{obj.token[-8:]}"

    @admin.display(description='Estado')
    def status_badge(self, obj):
        if obj.is_used:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">✓ USADO</span>'
            )
        elif obj.is_valid():
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">⏱ ACTIVO</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">⌛ EXPIRADO</span>'
            )

    @admin.display(description='Creado')
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')

    @admin.display(description='Expira')
    def expires_at_formatted(self, obj):
        return obj.expires_at.strftime('%d/%m/%Y %H:%M')

    @admin.display(description='Tiempo Restante')
    def time_remaining_display(self, obj):
        if obj.is_used:
            return "N/A (usado)"
        return obj.time_remaining_str()

    @admin.display(description='Usado')
    def used_at_formatted(self, obj):
        if obj.used_at:
            return obj.used_at.strftime('%d/%m/%Y %H:%M')
        return '-'

    @admin.display(description='¿Es Válido?')
    def is_valid_display(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green; font-weight: bold;">✓ SÍ</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ NO</span>')

    def has_add_permission(self, request):
        """No permitir crear tokens manualmente desde el admin"""
        return False

    def has_change_permission(self, request, obj=None):
        """No permitir editar tokens desde el admin"""
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Administrador de tokens de recuperación de contraseña
    """

    list_display = [
        'id',
        'user_email',
        'token_short',
        'status_badge',
        'ip_address_display',
        'created_at_formatted',
        'expires_at_formatted',
        'time_remaining_display',
        'used_at_formatted',
    ]

    list_filter = [
        'is_used',
        ('created_at', admin.DateFieldListFilter),
        ('expires_at', admin.DateFieldListFilter),
    ]

    search_fields = [
        'user__email',
        'user__nombre',
        'token',
        'ip_address',
    ]

    readonly_fields = [
        'user',
        'token',
        'created_at',
        'expires_at',
        'is_used',
        'used_at',
        'ip_address',
        'is_valid_display',
        'time_remaining_display',
    ]

    list_per_page = 50

    fieldsets = (
        ('Información del Token', {
            'fields': ('user', 'token', 'is_valid_display')
        }),
        ('Fechas', {
            'fields': ('created_at', 'expires_at', 'time_remaining_display')
        }),
        ('Estado', {
            'fields': ('is_used', 'used_at')
        }),
        ('Seguridad', {
            'fields': ('ip_address',)
        }),
    )

    @admin.display(description='Email del Usuario')
    def user_email(self, obj):
        return format_html(
            '<a href="{}" style="color: #007bff;">{}</a>',
            reverse('admin:users_user_change', args=[obj.user.pk]),
            obj.user.email
        )

    @admin.display(description='Token')
    def token_short(self, obj):
        return f"{obj.token[:16]}...{obj.token[-8:]}"

    @admin.display(description='Estado')
    def status_badge(self, obj):
        if obj.is_used:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">✓ USADO</span>'
            )
        elif obj.is_valid():
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">⏱ ACTIVO</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">⌛ EXPIRADO</span>'
            )

    @admin.display(description='IP')
    def ip_address_display(self, obj):
        if obj.ip_address:
            return format_html(
                '<code style="background-color: #f8f9fa; padding: 2px 6px; border-radius: 3px;">{}</code>',
                obj.ip_address
            )
        return '-'

    @admin.display(description='Creado')
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')

    @admin.display(description='Expira')
    def expires_at_formatted(self, obj):
        return obj.expires_at.strftime('%d/%m/%Y %H:%M')

    @admin.display(description='Tiempo Restante')
    def time_remaining_display(self, obj):
        if obj.is_used:
            return "N/A (usado)"
        return obj.time_remaining_str()

    @admin.display(description='Usado')
    def used_at_formatted(self, obj):
        if obj.used_at:
            return obj.used_at.strftime('%d/%m/%Y %H:%M')
        return '-'

    @admin.display(description='¿Es Válido?')
    def is_valid_display(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green; font-weight: bold;">✓ SÍ</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ NO</span>')

    def has_add_permission(self, request):
        """No permitir crear tokens manualmente desde el admin"""
        return False

    def has_change_permission(self, request, obj=None):
        """No permitir editar tokens desde el admin"""
        return False

    def get_queryset(self, request):
        """Ordenar por más recientes primero"""
        return super().get_queryset(request).select_related('user').order_by('-created_at')


# ============================================================================
# DJANGO-AXES: RATE LIMITING
# ============================================================================
# Los modelos de Axes se registran automáticamente en el admin cuando
# AXES_ENABLE_ADMIN=True en settings.py
# Para ver intentos fallidos, ir al admin: /admin/ → Axes

# Fin del archivo
        qs = super().get_queryset(request)
        return qs.select_related('user').order_by('-created_at')
