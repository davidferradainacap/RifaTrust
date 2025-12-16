"""
Vista de Health Check para Azure App Service
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Endpoint de health check para Azure App Service.
    Retorna 200 OK si la aplicación está funcionando correctamente.
    """
    from django.db import connection
    import sys
    
    status_data = {
        'status': 'healthy',
        'service': 'RifaTrust',
        'python_version': sys.version,
    }
    
    # Verificar conexión a base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status_data['database'] = 'connected'
    except Exception as e:
        status_data['database'] = f'error: {str(e)}'
        status_data['status'] = 'degraded'
    
    # Verificar modelos
    try:
        from apps.raffles.models import Raffle
        raffle_count = Raffle.objects.count()
        status_data['raffles_count'] = raffle_count
    except Exception as e:
        status_data['raffles'] = f'error: {str(e)}'
        status_data['status'] = 'degraded'
    
    return JsonResponse(status_data, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def email_config_check(request):
    """
    Endpoint de diagnóstico para verificar configuración de email.
    Solo accesible con parámetro secreto.
    """
    from django.conf import settings
    
    # Verificar token secreto para seguridad
    secret = request.GET.get('secret', '')
    if secret != 'rifatrust2025':
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    config = {
        'email_backend': settings.EMAIL_BACKEND,
        'email_host': getattr(settings, 'EMAIL_HOST', 'not set'),
        'email_port': getattr(settings, 'EMAIL_PORT', 'not set'),
        'email_use_tls': getattr(settings, 'EMAIL_USE_TLS', 'not set'),
        'email_host_user': getattr(settings, 'EMAIL_HOST_USER', 'not set'),
        'email_host_password_set': bool(getattr(settings, 'EMAIL_HOST_PASSWORD', '')),
        'email_host_password_length': len(getattr(settings, 'EMAIL_HOST_PASSWORD', '')),
        'default_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'not set'),
        'site_domain': getattr(settings, 'SITE_DOMAIN', 'not set'),
    }
    
    return JsonResponse(config, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def test_send_email(request):
    """
    Endpoint de prueba para enviar un email real.
    Solo accesible con parámetro secreto.
    """
    from django.conf import settings
    from django.core.mail import send_mail
    import traceback
    
    # Verificar token secreto para seguridad
    secret = request.GET.get('secret', '')
    if secret != 'rifatrust2025':
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    # Email destino (opcional, por defecto usa el from_email)
    to_email = request.GET.get('to', 'daldeaferrada@gmail.com')
    
    try:
        result = send_mail(
            subject='[RifaTrust] Test de Email desde Azure',
            message='Este es un email de prueba enviado desde la aplicación RifaTrust en Azure. Si lo recibes, la configuración SMTP está funcionando correctamente.',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rifatrust.com'),
            recipient_list=[to_email],
            fail_silently=False,
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Email enviado exitosamente a {to_email}',
            'result': result,
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'not set'),
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc(),
        }, status=500)
