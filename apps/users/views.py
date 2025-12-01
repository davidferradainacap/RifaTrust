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

from .models import Profile, Notification
# - Modelo Profile (OneToOne con User)
# - Modelo Notification (sistema de notificaciones)

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
            
            # === PASO 4: VALIDACIÓN ESPECIAL PARA SPONSORS ===
            # Los sponsors requieren aprobación manual del admin
            # Esto previene fraudes y asegura sponsors legítimos
            if user.rol == 'sponsor':
                # Marcar cuenta como NO validada
                user.cuenta_validada = False
                user.save()
                
                # === CREAR PERFIL DEL SPONSOR ===
                Profile.objects.create(
                    user=user,
                    fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento')
                )
                
                # Mensaje informativo
                messages.warning(
                    request, 
                    f'Tu cuenta de Sponsor ha sido creada y está pendiente de validación por el administrador. Te notificaremos cuando sea aprobada.'
                )
                return redirect('login')
            
            # === PASO 5: AUTO-APROBAR OTROS ROLES ===
            else:
                # Participantes y organizadores se auto-aprueban
                user.cuenta_validada = True
                user.save()
                
                # === CREAR PERFIL ===
                Profile.objects.create(
                    user=user,
                    fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento')
                )
                
                # === LOGIN AUTOMÁTICO ===
                # Iniciar sesión sin requerir login manual
                login(request, user)
                
                messages.success(
                    request, 
                    f'¡Bienvenido {user.nombre}! Tu cuenta ha sido creada exitosamente.'
                )
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
                # === PASO 5: VERIFICAR VALIDACIÓN DE CUENTA ===
                # Importante para sponsors que requieren aprobación
                if not user.cuenta_validada:
                    messages.error(
                        request, 
                        'Tu cuenta está pendiente de validación por el administrador. Por favor, espera a que sea aprobada.'
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
