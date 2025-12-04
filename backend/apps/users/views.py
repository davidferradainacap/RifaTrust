# ============================================================================
# MÓDULO DE USUARIOS - VIEWS
# ============================================================================
# Gestiona autenticación, registro, perfiles y notificaciones
# Sistema de roles: Participante, Organizador, Sponsor, Admin
# Validación especial para cuentas de Sponsor (requiere aprobación admin)
# ============================================================================

# === IMPORTACIONES DJANGO CORE ===
from django.shortcuts import render, redirect, get_object_or_404
# - render: renderiza templates
# - redirect: redirige a otra vista
# - get_object_or_404: obtiene objeto o 404

from django.contrib.auth import login, authenticate, logout
# - login: inicia sesión de usuario (crea session)
# - authenticate: valida credenciales
# - logout: cierra sesión

from django.contrib.auth.decorators import login_required
# - Decorador que requiere autenticación

from django.contrib import messages
# - Sistema de mensajes flash

from django.utils import timezone
# - Manejo de fechas/horas con timezone awareness

from django.http import JsonResponse
# - Respuestas en formato JSON para AJAX

from django.core.paginator import Paginator
# - Paginación de resultados

# === IMPORTACIONES LOCALES ===
from .forms import RegisterForm, LoginForm, ProfileForm
# - Formularios de registro, login y perfil

from .models import Profile, Notification, EmailConfirmationToken, PasswordResetToken
# - Modelo Profile (OneToOne con User)
# - Modelo Notification (sistema de notificaciones)
# - Modelo EmailConfirmationToken (confirmación de email)
# - Modelo PasswordResetToken (recuperación de contraseña)

from .email_service import EmailConfirmationService, PasswordResetService
# - Servicio para envío de emails de confirmación
# - Servicio para envío de emails de recuperación de contraseña

from apps.core.email_validator import verify_email
# - Verificación de validez de emails

from django.contrib.auth import get_user_model
User = get_user_model()
# - Obtener modelo User de forma segura

# ============================================================================
# VISTA: register_view
# ============================================================================
# Registro de nuevos usuarios con validación de rol
#
# URL: /register/
# Método: GET (formulario), POST (creación)
# Autenticación: No requerida (pública)
#
# Flujo:
# 1. Validar que usuario no esté ya autenticado
# 2. Validar formulario de registro
# 3. Crear usuario con rol seleccionado
# 4. Si rol=sponsor: Marcar cuenta_validada=False (requiere aprobación admin)
# 5. Si rol!=sponsor: Auto-aprobar y hacer login automático
# 6. Crear perfil asociado con fecha de nacimiento
#
# Roles disponibles:
# - participante: Auto-aprobado
# - organizador: Auto-aprobado
# - sponsor: Requiere validación manual (cuenta_validada=False)
# - admin: Solo puede crear otro admin desde Django admin
# ============================================================================
def register_view(request):
    # === PASO 1: VERIFICAR SI YA ESTÁ AUTENTICADO ===
    # Si el usuario ya tiene sesión, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    # === PASO 2: PROCESAR FORMULARIO (POST) ===
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        # === PASO 3: VALIDAR FORMULARIO ===
        if form.is_valid():
            # commit=False: Crea instancia sin guardar en DB
            # Permite modificar campos antes del save()
            user = form.save(commit=False)

            # === PASO 4: CONFIGURAR VALIDACIÓN SEGÚN ROL ===
            # PARTICIPANTE y ORGANIZADOR: Requieren confirmación de email
            # SPONSOR: Requiere aprobación manual del administrador

            if user.rol in ['participante', 'organizador']:
                # Estas cuentas requieren confirmación de email
                user.cuenta_validada = False  # No validada hasta confirmar email
                user.is_active = True  # Activa pero no validada
            elif user.rol == 'sponsor':
                # Sponsors requieren aprobación del administrador, no confirmación de email
                user.cuenta_validada = False  # No validada hasta que admin apruebe
                user.is_active = False  # Inactiva hasta aprobación
            else:
                # Otros roles (si existen) se auto-aprueban
                user.cuenta_validada = True
                user.is_active = True

            user.save()

            # === PASO 5: CREAR PERFIL ===
            Profile.objects.create(
                user=user,
                fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento')
            )

            # === PASO 6: PROCESO SEGÚN ROL ===
            if user.rol in ['participante', 'organizador']:
                # PARTICIPANTES y ORGANIZADORES: Enviar email de confirmación
                try:
                    # Crear token de confirmación (expira en 24h)
                    token = EmailConfirmationToken.create_token(user)

                    # Enviar email con link de activación
                    email_sent = EmailConfirmationService.send_confirmation_email(
                        user=user,
                        token=token,
                        request=request
                    )

                    if email_sent:
                        messages.success(
                            request,
                            f'¡Cuenta creada exitosamente! Hemos enviado un email de confirmación a {user.email}. '
                            f'Por favor revisa tu bandeja de entrada y haz clic en el enlace para activar tu cuenta.'
                        )
                    else:
                        messages.warning(
                            request,
                            'Cuenta creada, pero hubo un problema al enviar el email de confirmación. '
                            'Contacta al soporte para activar tu cuenta.'
                        )

                except Exception as e:
                    # Log del error para debugging
                    import logging
                    import traceback
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error al enviar email de confirmación: {str(e)}")
                    logger.error(traceback.format_exc())

                    # Aún así permitir que vean el mensaje de éxito
                    messages.warning(
                        request,
                        f'Cuenta creada exitosamente. El email de confirmación no pudo enviarse, '
                        f'pero tu cuenta fue creada. Usa este link para confirmar: '
                        f'http://127.0.0.1:8000/confirm-email/{token.token}/'
                    )

                # Redirigir a página de confirmación pendiente
                return redirect('email_confirmation_sent')

            elif user.rol == 'sponsor':
                # SPONSORS: Notificar que requiere aprobación del administrador
                # Crear notificación para administradores
                admin_users = User.objects.filter(rol='admin', is_active=True)
                for admin in admin_users:
                    Notification.objects.create(
                        usuario=admin,
                        tipo='sistema',
                        titulo='Nueva solicitud de Sponsor',
                        mensaje=f'{user.nombre} ({user.email}) ha solicitado una cuenta de Sponsor y requiere aprobación.',
                        enlace=f'/admin-panel/users/'
                    )

                messages.info(
                    request,
                    '¡Cuenta de Sponsor creada exitosamente! Tu solicitud está siendo revisada por nuestro equipo. '
                    'Recibirás un email cuando tu cuenta sea aprobada.'
                )
                return redirect('login')

            else:
                # Otros roles: Login automático
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.nombre}!')
                return redirect('dashboard')

    # === PASO 6: MOSTRAR FORMULARIO (GET) ===
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})

# ============================================================================
# VISTA: login_view
# ============================================================================
# Autenticación de usuarios con validación de cuenta
#
# URL: /login/
# Método: GET (formulario), POST (autenticación)
# Autenticación: No requerida (pública)
#
# Validaciones de seguridad:
# 1. Verificar que credenciales sean correctas (email + password)
# 2. Verificar que cuenta esté validada (cuenta_validada=True)
# 3. Actualizar última_conexion para auditoría
#
# Sistema de autenticación:
# - Backend: settings.AUTHENTICATION_BACKENDS
# - Hasher: Argon2 (OWASP 2024 recomendado)
# - Sesión: Cookie HttpOnly con CSRF protection
# ============================================================================
def login_view(request):
    # === PASO 1: VERIFICAR SI YA ESTÁ AUTENTICADO ===
    if request.user.is_authenticated:
        return redirect('dashboard')

    # === PASO 2: PROCESAR LOGIN (POST) ===
    if request.method == 'POST':
        # LoginForm hereda de AuthenticationForm de Django
        # Requiere request como primer argumento
        form = LoginForm(request, data=request.POST)

        # === PASO 3: VALIDAR CREDENCIALES ===
        if form.is_valid():
            # 'username' es el campo del form (aunque sea email)
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # === PASO 4: AUTENTICAR USUARIO ===
            # authenticate() verifica:
            # 1. Usuario existe
            # 2. Password es correcto (compara hash Argon2)
            # 3. Usuario está activo (is_active=True)
            user = authenticate(username=email, password=password)

            if user is not None:
                # === PASO 5: VERIFICAR VALIDACIÓN DE CUENTA SEGÚN ROL ===
                if not user.cuenta_validada:
                    if user.rol == 'sponsor':
                        # Sponsors: Cuenta pendiente de aprobación del administrador
                        messages.error(
                            request,
                            'Tu solicitud de cuenta Sponsor está pendiente de aprobación. '
                            'El equipo administrativo revisará tu solicitud y te notificaremos por email.'
                        )
                    elif user.rol in ['participante', 'organizador']:
                        # Participantes y Organizadores: Email no confirmado
                        messages.error(
                            request,
                            'Debes confirmar tu email antes de iniciar sesión. '
                            'Revisa tu bandeja de entrada y haz clic en el enlace de confirmación.'
                        )
                    else:
                        # Otros roles
                        messages.error(
                            request,
                            'Tu cuenta está pendiente de validación. Contacta al administrador.'
                        )
                    return redirect('login')

                # === PASO 6: ACTUALIZAR ÚLTIMA CONEXIÓN ===
                # Útil para estadísticas y auditoría
                user.ultima_conexion = timezone.now()
                user.save()

                # === PASO 7: INICIAR SESIÓN ===
                # login() crea la session en la base de datos
                # y establece la cookie de sesión en el navegador
                login(request, user)

                messages.success(request, f'¡Bienvenido de nuevo, {user.nombre}!')
                return redirect('dashboard')

    # === PASO 8: MOSTRAR FORMULARIO (GET) ===
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

# ============================================================================
# VISTA: logout_view
# ============================================================================
# Cierra la sesión del usuario
#
# URL: /logout/
# Método: GET
# Autenticación: Requerida
#
# Acciones:
# 1. Eliminar sesión de la base de datos
# 2. Limpiar cookie de sesión del navegador
# 3. Redirigir a home con mensaje informativo
# ============================================================================
@login_required
def logout_view(request):
    # === CERRAR SESIÓN ===
    # logout() realiza:
    # 1. Elimina session_key de django_session table
    # 2. Borra cookie de sesión del navegador
    # 3. Limpia request.user (lo convierte en AnonymousUser)
    logout(request)

    # Mensaje informativo
    messages.info(request, 'Has cerrado sesión exitosamente.')

    # Redirigir a página principal
    return redirect('home')

# ============================================================================
# VISTA: dashboard_view
# ============================================================================
# Router central que redirige a dashboard específico según rol
#
# URL: /dashboard/
# Método: GET
# Autenticación: Requerida
#
# Redirecciones según rol:
# - admin → admin_panel:dashboard (gestión completa del sistema)
# - organizador → raffles:organizer_dashboard (mis rifas, estadísticas)
# - sponsor → raffles:sponsor_dashboard (oportunidades de patrocinio)
# - participante → raffles:participant_dashboard (mis boletos, rifas activas)
# ============================================================================
@login_required
def dashboard_view(request):
    user = request.user

    # === REDIRECCIÓN SEGÚN ROL ===
    # Cada rol tiene un dashboard personalizado con funcionalidades específicas

    if user.rol == 'admin':
        # Dashboard administrativo: usuarios, rifas, pagos, auditoría
        return redirect('admin_panel:dashboard')

    elif user.rol == 'organizador':
        # Dashboard de organizador: crear rifas, ver ventas, gestionar sorteos
        return redirect('raffles:organizer_dashboard')

    elif user.rol == 'sponsor':
        # Dashboard de sponsor: buscar rifas, enviar propuestas, ver colaboraciones
        return redirect('raffles:sponsor_dashboard')

    else:
        # Dashboard de participante: comprar boletos, ver mis rifas, verificar premios
        return redirect('raffles:participant_dashboard')

# ============================================================================
# VISTA: profile_view
# ============================================================================
# Edición de perfil de usuario con datos personales
#
# URL: /profile/
# Método: GET (formulario), POST (actualización)
# Autenticación: Requerida
#
# Campos editables:
# - User: telefono, avatar
# - Profile: fecha_nacimiento, direccion, ciudad, estado, codigo_postal, biografia
#
# Seguridad:
# - Campos de Profile con encriptación Fernet (direccion, ciudad, estado, codigo_postal)
# - Avatar con validación de tamaño y tipo de archivo
# ============================================================================
@login_required
def profile_view(request):
    # === PASO 1: OBTENER O CREAR PERFIL ===
    # get_or_create: Si no existe Profile, lo crea automáticamente
    # created: Boolean que indica si fue creado o ya existía
    profile, created = Profile.objects.get_or_create(user=request.user)

    # === PASO 2: PROCESAR ACTUALIZACIÓN (POST) ===
    if request.method == 'POST':
        # request.FILES: archivos subidos (avatar)
        # instance=profile: vincular formulario a perfil existente
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            # === GUARDAR TELÉFONO EN USER ===
            # El teléfono se almacena en User (campo encriptado)
            telefono = form.cleaned_data.get('telefono')
            if telefono:
                request.user.telefono = telefono

            # === GUARDAR AVATAR EN USER ===
            # Avatar también se guarda en User model
            avatar = form.cleaned_data.get('avatar')
            if avatar:
                request.user.avatar = avatar

            # Guardar cambios en User
            request.user.save()

            # === GUARDAR DATOS DE PROFILE ===
            # form.save() actualiza Profile con datos encriptados
            form.save()

            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('profile')

    # === PASO 3: MOSTRAR FORMULARIO (GET) ===
    else:
        # Inicializar formulario con datos existentes
        form = ProfileForm(instance=profile)

        # Pre-poblar campo teléfono desde User
        form.initial['telefono'] = request.user.telefono

    return render(request, 'users/profile.html', {'form': form})

# ============================================================================
# VISTA: notifications_view
# ============================================================================
# Buzón de notificaciones del usuario con filtros y paginación
#
# URL: /notifications/?filter=<tipo>&page=<numero>
# Método: GET
# Autenticación: Requerida
#
# Query Parameters:
# - filter: Tipo de notificación a mostrar
#   * 'all': Todas las notificaciones (default)
#   * 'unread': Solo no leídas
#   * 'sistema': Solo notificaciones del sistema
#   * 'compra': Solo notificaciones de compras
#   * 'sorteo': Solo notificaciones de sorteos
#   * 'ganador': Solo notificaciones de premios ganados
#   * 'patrocinio': Solo notificaciones de patrocinios
#   * 'aprobacion': Solo notificaciones de aprobaciones
#   * 'rechazo': Solo notificaciones de rechazos
#   * 'rifa': Solo notificaciones de rifas
# - page: Número de página (paginación de 15 items)
#
# Funcionalidades:
# - Filtrado por tipo de notificación
# - Paginación automática (15 por página)
# - Contador de notificaciones totales y no leídas
# - Marca visual de leídas/no leídas
# ============================================================================
@login_required
def notifications_view(request):
    """Vista del buzón de notificaciones"""

    # === PASO 1: OBTENER FILTRO DESDE URL ===
    # GET parameter 'filter' con valor default 'all'
    filter_type = request.GET.get('filter', 'all')

    # === PASO 2: OBTENER NOTIFICACIONES BASE ===
    # Todas las notificaciones del usuario actual
    # order_by('-fecha_creacion'): Más recientes primero
    notifications = Notification.objects.filter(
        usuario=request.user
    ).order_by('-fecha_creacion')

    # === PASO 3: APLICAR FILTROS ===
    if filter_type == 'unread':
        # Solo notificaciones no leídas
        notifications = notifications.filter(leida=False)

    elif filter_type != 'all':
        # Filtrar por tipo específico
        # Tipos: sistema, compra, sorteo, ganador, patrocinio,
        #        aprobacion, rechazo, rifa, rifa_finalizada
        notifications = notifications.filter(tipo=filter_type)

    # === PASO 4: CONTAR NOTIFICACIONES ===
    # Total: todas las notificaciones del usuario
    total_count = Notification.objects.filter(usuario=request.user).count()

    # No leídas: para mostrar badge en navbar
    unread_count = Notification.objects.filter(
        usuario=request.user,
        leida=False
    ).count()

    # === PASO 5: PAGINACIÓN ===
    # Paginator divide resultados en páginas
    # 15 notificaciones por página (balance entre UX y performance)
    paginator = Paginator(notifications, 15)

    # Obtener número de página desde GET parameter
    page_number = request.GET.get('page')

    # get_page() es seguro: si page es inválido, retorna página 1
    page_obj = paginator.get_page(page_number)

    # === PASO 6: PREPARAR CONTEXTO ===
    context = {
        'notifications': page_obj,  # Notificaciones de la página actual
        'filter_type': filter_type,  # Filtro activo (para mantener en UI)
        'total_count': total_count,  # Total de notificaciones
        'unread_count': unread_count,  # Total de no leídas
        'page_obj': page_obj,  # Objeto de paginación
        'is_paginated': page_obj.has_other_pages(),  # Boolean: ¿hay más páginas?
    }

    return render(request, 'users/notifications.html', context)

@login_required
def notification_count(request):
    """API para obtener el conteo de notificaciones no leídas"""
    unread_count = Notification.objects.filter(usuario=request.user, leida=False).count()
    return JsonResponse({'unread_count': unread_count})

@login_required
def notifications_api_list(request):
    """API para obtener la lista de notificaciones para el dropdown"""
    from django.utils import timezone
    from django.utils.timesince import timesince

    notifications = Notification.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:10]

    notifications_data = []
    for notif in notifications:
        time_ago = timesince(notif.fecha_creacion, timezone.now())
        notifications_data.append({
            'id': notif.id,
            'tipo': notif.tipo,
            'mensaje': notif.mensaje,
            'leido': notif.leida,
            'created_at': f'Hace {time_ago.split(",")[0]}'
        })

    return JsonResponse({'notifications': notifications_data})

@login_required
def mark_notification_read(request, notification_id):
    """Marcar una notificación como leída"""
    notification = get_object_or_404(Notification, id=notification_id, usuario=request.user)
    notification.leida = True
    notification.save()
    messages.success(request, 'Notificación marcada como leída.')
    return redirect('notifications')

@login_required
def mark_all_read(request):
    """Marcar todas las notificaciones como leídas"""
    if request.method == 'POST':
        Notification.objects.filter(usuario=request.user, leida=False).update(leida=True)
        messages.success(request, 'Todas las notificaciones han sido marcadas como leídas.')
    return redirect('notifications')


# ============================================================================
# VISTAS DE CONFIRMACIÓN DE EMAIL
# ============================================================================

def email_confirmation_sent_view(request):
    """
    Vista que muestra mensaje de confirmación enviada

    URL: /email-confirmation-sent/
    Método: GET
    Autenticación: No requerida
    """
    return render(request, 'users/email_confirmation_sent.html')


def confirm_email_view(request, token):
    """
    Vista para confirmar email con token

    URL: /confirm-email/<token>/
    Método: GET
    Autenticación: No requerida

    Flujo:
    1. Buscar token en la base de datos
    2. Verificar que sea válido (no usado, no expirado)
    3. Activar cuenta del usuario
    4. Marcar token como usado
    5. Enviar email de bienvenida
    6. Redirigir a login con mensaje de éxito
    """
    try:
        # Buscar el token
        token_obj = EmailConfirmationToken.objects.select_related('user').get(token=token)

        # Verificar si el token es válido
        if not token_obj.is_valid():
            if token_obj.is_used:
                messages.warning(
                    request,
                    'Este enlace de confirmación ya fue utilizado. '
                    'Tu cuenta ya está activada, puedes iniciar sesión.'
                )
            else:
                messages.error(
                    request,
                    'Este enlace de confirmación ha expirado. '
                    'Por favor solicita un nuevo enlace de confirmación.'
                )
            return redirect('login')

        # Token válido: activar cuenta
        user = token_obj.user
        user.cuenta_validada = True
        user.save()

        # Marcar token como usado
        token_obj.mark_as_used()

        # Enviar email de bienvenida
        try:
            EmailConfirmationService.send_welcome_email(user)
        except Exception as e:
            # No fallar si no se puede enviar el email de bienvenida
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar email de bienvenida: {str(e)}")

        # Mensaje de éxito
        messages.success(
            request,
            f'¡Cuenta activada exitosamente! Ya puedes iniciar sesión con tu email {user.email}.'
        )
        return redirect('login')

    except EmailConfirmationToken.DoesNotExist:
        messages.error(
            request,
            'Enlace de confirmación inválido. '
            'Por favor verifica que hayas copiado correctamente la URL.'
        )
        return redirect('login')


def resend_confirmation_email_view(request):
    """
    Vista para reenviar email de confirmación

    URL: /resend-confirmation/
    Método: GET (formulario), POST (reenvío)
    Autenticación: No requerida

    Permite a usuarios que no recibieron el email solicitar uno nuevo
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, 'Por favor ingresa tu email.')
            return render(request, 'users/resend_confirmation.html')

        try:
            # Buscar usuario por email
            user = User.objects.get(email=email)

            # Verificar si ya está validado
            if user.cuenta_validada:
                messages.info(
                    request,
                    'Tu cuenta ya está activada. Puedes iniciar sesión directamente.'
                )
                return redirect('login')

            # Invalidar tokens anteriores no usados
            EmailConfirmationToken.objects.filter(
                user=user,
                is_used=False
            ).update(is_used=True)

            # Crear nuevo token
            token = EmailConfirmationToken.create_token(user)

            # Enviar email
            email_sent = EmailConfirmationService.send_confirmation_email(
                user=user,
                token=token,
                request=request
            )

            if email_sent:
                messages.success(
                    request,
                    f'Email de confirmación reenviado a {email}. '
                    f'Por favor revisa tu bandeja de entrada.'
                )
            else:
                messages.error(
                    request,
                    'Hubo un problema al enviar el email. Por favor intenta nuevamente.'
                )

            return redirect('email_confirmation_sent')

        except User.DoesNotExist:
            # Por seguridad, no revelar si el email existe o no
            messages.success(
                request,
                'Si el email existe en nuestro sistema, recibirás un enlace de confirmación.'
            )
            return redirect('email_confirmation_sent')

    return render(request, 'users/resend_confirmation.html')


# ============================================================================
# RECUPERACIÓN DE CONTRASEÑA - VISTAS HTML
# ============================================================================

def password_reset_request_view(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, 'Por favor ingresa tu correo electrónico.')
            return render(request, 'users/password_reset_request.html')

        try:
            User = get_user_model()
            user = User.objects.get(email=email)

            # Verificar que la cuenta esté activa
            if not user.is_active:
                messages.success(
                    request,
                    'Si tu correo está registrado, recibirás instrucciones para recuperar tu contraseña.'
                )
                return redirect('password_reset_sent')

            # Invalidar tokens anteriores
            PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).update(is_used=True)

            # Crear nuevo token
            ip_address = get_client_ip(request)
            token = PasswordResetToken.create_token(user, ip_address=ip_address)

            # Enviar email
            PasswordResetService.send_reset_email(
                user=user,
                token=token,
                request=request
            )

            messages.success(
                request,
                'Si tu correo está registrado, recibirás instrucciones para recuperar tu contraseña.'
            )
            return redirect('password_reset_sent')

        except User.DoesNotExist:
            # Por seguridad, no revelar si el email existe
            messages.success(
                request,
                'Si tu correo está registrado, recibirás instrucciones para recuperar tu contraseña.'
            )
            return redirect('password_reset_sent')

    return render(request, 'users/password_reset_request.html')


def password_reset_sent_view(request):
    """Vista de confirmación de envío de email"""
    return render(request, 'users/password_reset_sent.html')


def password_reset_confirm_view(request, token):
    """Vista para confirmar nueva contraseña con el token"""
    # Verificar que el token sea válido
    try:
        reset_token = PasswordResetToken.objects.get(token=token)

        if not reset_token.is_valid():
            if reset_token.is_used:
                messages.error(
                    request,
                    'Este enlace ya fue utilizado. Si necesitas recuperar tu contraseña nuevamente, solicita un nuevo enlace.'
                )
            else:
                messages.error(
                    request,
                    'Este enlace ha expirado. Por favor solicita un nuevo enlace de recuperación.'
                )
            return redirect('password_reset_request')

        # Procesar formulario
        if request.method == 'POST':
            password = request.POST.get('password', '')
            password_confirm = request.POST.get('password_confirm', '')

            # Validaciones
            if not password or not password_confirm:
                messages.error(request, 'Ambas contraseñas son requeridas.')
                return render(request, 'users/password_reset_confirm.html', {
                    'token': token,
                    'email': reset_token.user.email
                })

            if password != password_confirm:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'users/password_reset_confirm.html', {
                    'token': token,
                    'email': reset_token.user.email
                })

            if len(password) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
                return render(request, 'users/password_reset_confirm.html', {
                    'token': token,
                    'email': reset_token.user.email
                })

            # Cambiar contraseña
            user = reset_token.user
            user.set_password(password)
            user.save()

            # Marcar token como usado
            reset_token.mark_as_used()

            # Enviar email de notificación
            PasswordResetService.send_password_changed_notification(user)

            messages.success(
                request,
                '¡Tu contraseña ha sido cambiada exitosamente! Ya puedes iniciar sesión con tu nueva contraseña.'
            )
            return redirect('login')

        # GET request - mostrar formulario
        return render(request, 'users/password_reset_confirm.html', {
            'token': token,
            'email': reset_token.user.email,
            'expires_in': reset_token.time_remaining_str()
        })

    except PasswordResetToken.DoesNotExist:
        messages.error(
            request,
            'El enlace de recuperación es inválido. Por favor solicita un nuevo enlace.'
        )
        return redirect('password_reset_request')


# ============================================================================
# RECUPERACIÓN DE CONTRASEÑA - API REST
# ============================================================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


def get_client_ip(request):
    """Obtiene la IP del cliente desde el request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    API endpoint para solicitar recuperación de contraseña

    POST /api/users/password-reset/request/
    Body: { "email": "usuario@ejemplo.com" }

    Returns:
        200: Email enviado (siempre, por seguridad)
        400: Datos inválidos
    """
    email = request.data.get('email', '').strip().lower()

    if not email:
        return Response(
            {'error': 'El email es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Buscar usuario
        User = get_user_model()
        user = User.objects.get(email=email)

        # Verificar que la cuenta esté activa
        if not user.is_active:
            # Por seguridad, no revelar que la cuenta existe pero está inactiva
            return Response(
                {
                    'success': True,
                    'message': 'Si el email existe en nuestro sistema, recibirás instrucciones para recuperar tu contraseña.'
                },
                status=status.HTTP_200_OK
            )

        # Invalidar tokens anteriores no usados
        PasswordResetToken.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)

        # Crear nuevo token
        ip_address = get_client_ip(request)
        token = PasswordResetToken.create_token(user, ip_address=ip_address)

        # Enviar email
        email_sent = PasswordResetService.send_reset_email(
            user=user,
            token=token,
            request=request
        )

        if email_sent:
            return Response(
                {
                    'success': True,
                    'message': 'Si el email existe en nuestro sistema, recibirás instrucciones para recuperar tu contraseña.',
                    'expires_in': '1 hora'
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'success': True,
                    'message': 'Si el email existe en nuestro sistema, recibirás instrucciones para recuperar tu contraseña.'
                },
                status=status.HTTP_200_OK
            )

    except User.DoesNotExist:
        # Por seguridad, no revelar si el email existe o no
        return Response(
            {
                'success': True,
                'message': 'Si el email existe en nuestro sistema, recibirás instrucciones para recuperar tu contraseña.'
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': 'Error al procesar la solicitud'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_reset_token(request, token):
    """
    API endpoint para verificar si un token de reset es válido

    GET /api/users/password-reset/verify/{token}/

    Returns:
        200: Token válido con información del usuario
        400: Token inválido, expirado o usado
    """
    try:
        reset_token = PasswordResetToken.objects.get(token=token)

        if not reset_token.is_valid():
            if reset_token.is_used:
                message = 'Este enlace ya fue utilizado'
            else:
                message = 'Este enlace ha expirado'

            return Response(
                {
                    'valid': False,
                    'error': message
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'valid': True,
                'email': reset_token.user.email,
                'expires_in': reset_token.time_remaining_str()
            },
            status=status.HTTP_200_OK
        )

    except PasswordResetToken.DoesNotExist:
        return Response(
            {
                'valid': False,
                'error': 'Token inválido'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request, token):
    """
    API endpoint para confirmar el cambio de contraseña

    POST /api/users/password-reset/confirm/{token}/
    Body: {
        "password": "nueva_contraseña",
        "password_confirm": "nueva_contraseña"
    }

    Returns:
        200: Contraseña cambiada exitosamente
        400: Token inválido o contraseñas no coinciden
    """
    password = request.data.get('password', '')
    password_confirm = request.data.get('password_confirm', '')

    # Validaciones
    if not password or not password_confirm:
        return Response(
            {'error': 'Ambas contraseñas son requeridas'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if password != password_confirm:
        return Response(
            {'error': 'Las contraseñas no coinciden'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 8:
        return Response(
            {'error': 'La contraseña debe tener al menos 8 caracteres'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        reset_token = PasswordResetToken.objects.get(token=token)

        if not reset_token.is_valid():
            if reset_token.is_used:
                message = 'Este enlace ya fue utilizado'
            else:
                message = 'Este enlace ha expirado'

            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cambiar contraseña
        user = reset_token.user
        user.set_password(password)
        user.save()

        # Marcar token como usado
        reset_token.mark_as_used()

        # Enviar notificación de cambio
        PasswordResetService.send_password_changed_notification(user)

        return Response(
            {
                'success': True,
                'message': 'Contraseña cambiada exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.'
            },
            status=status.HTTP_200_OK
        )

    except PasswordResetToken.DoesNotExist:
        return Response(
            {'error': 'Token inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': 'Error al cambiar la contraseña'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
