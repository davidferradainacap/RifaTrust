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


def serve_media(request, path):
    """
    Sirve archivos media desde /home/media en Azure.
    En desarrollo usa la carpeta media del proyecto.
    """
    import os
    import mimetypes
    from django.http import FileResponse, Http404
    from django.conf import settings

    # Determinar la ruta base de media
    if os.environ.get('WEBSITE_HOSTNAME'):
        # Azure - usar /home/media
        media_root = '/home/media'
    else:
        # Desarrollo local
        media_root = settings.MEDIA_ROOT

    # Construir ruta completa del archivo
    file_path = os.path.join(media_root, path)

    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        raise Http404(f"Media file not found: {path}")

    # Verificar que es un archivo (no directorio)
    if not os.path.isfile(file_path):
        raise Http404(f"Not a file: {path}")

    # Determinar el content type
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'

    # Servir el archivo
    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'

    return response


@csrf_exempt
@require_http_methods(["GET"])
def debug_media(request):
    """
    Endpoint de diagnóstico para verificar el sistema de archivos media.
    Solo accesible con parámetro secreto.
    """
    import os
    from django.conf import settings

    secret = request.GET.get('secret', '')
    if secret != 'rifatrust2025':
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Determinar rutas
    is_azure = bool(os.environ.get('WEBSITE_HOSTNAME'))

    if is_azure:
        media_root = '/home/media'
    else:
        media_root = str(settings.MEDIA_ROOT)

    result = {
        'is_azure': is_azure,
        'media_root': media_root,
        'media_url': settings.MEDIA_URL,
        'media_root_exists': os.path.exists(media_root),
        'website_hostname': os.environ.get('WEBSITE_HOSTNAME', 'not set'),
    }

    # Listar contenido de media_root
    if os.path.exists(media_root):
        try:
            result['media_root_contents'] = os.listdir(media_root)

            # Listar avatars si existe
            avatars_path = os.path.join(media_root, 'avatars')
            if os.path.exists(avatars_path):
                result['avatars_exists'] = True
                result['avatars_contents'] = os.listdir(avatars_path)
            else:
                result['avatars_exists'] = False

            # Listar raffles si existe
            raffles_path = os.path.join(media_root, 'raffles')
            if os.path.exists(raffles_path):
                result['raffles_exists'] = True
                result['raffles_contents'] = os.listdir(raffles_path)[:10]  # Solo primeros 10
            else:
                result['raffles_exists'] = False

        except Exception as e:
            result['list_error'] = str(e)
    else:
        result['media_root_contents'] = 'Directory does not exist'

    # Verificar permisos de escritura
    try:
        test_file = os.path.join(media_root, 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        result['write_permission'] = True
    except Exception as e:
        result['write_permission'] = False
        result['write_error'] = str(e)

    return JsonResponse(result, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def debug_user_avatar(request):
    """
    Endpoint para diagnosticar el avatar de un usuario específico.
    """
    import os
    from django.conf import settings

    secret = request.GET.get('secret', '')
    if secret != 'rifatrust2025':
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    email = request.GET.get('email', '')

    from apps.users.models import User

    try:
        user = User.objects.get(email=email)

        result = {
            'user_found': True,
            'email': user.email,
            'nombre': user.nombre,
            'avatar_field': str(user.avatar) if user.avatar else None,
            'avatar_name': user.avatar.name if user.avatar else None,
            'has_avatar': bool(user.avatar),
        }

        if user.avatar:
            try:
                result['avatar_url'] = user.avatar.url
            except Exception as e:
                result['avatar_url_error'] = str(e)

            # Verificar si el archivo existe físicamente
            is_azure = bool(os.environ.get('WEBSITE_HOSTNAME'))
            if is_azure:
                media_root = '/home/media'
            else:
                media_root = str(settings.MEDIA_ROOT)

            file_path = os.path.join(media_root, user.avatar.name)
            result['file_path'] = file_path
            result['file_exists'] = os.path.exists(file_path)

    except User.DoesNotExist:
        result = {'user_found': False, 'email': email}
    except Exception as e:
        result = {'error': str(e)}

    return JsonResponse(result, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def create_demo_raffles_view(request):
    """
    Endpoint para crear rifas de demostración.
    Acceso protegido con parámetro secreto.
    """
    import random
    import uuid
    from datetime import datetime, timedelta
    from decimal import Decimal
    from django.utils import timezone
    from apps.users.models import User
    from apps.raffles.models import Raffle, Ticket
    from apps.payments.models import Payment
    import pytz
    
    # Verificar secreto
    secret = request.GET.get('secret', '')
    if secret != 'rifatrust2025':
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    CHILE_TZ = pytz.timezone('America/Santiago')
    now_chile = timezone.now().astimezone(CHILE_TZ)
    hoy = now_chile.date()
    
    result = {
        'fecha': str(hoy),
        'hora_chile': now_chile.strftime('%H:%M:%S'),
        'rifas_creadas': [],
        'total_boletos': 0
    }
    
    # Limpiar datos existentes
    try:
        Payment.objects.all().delete()
        Ticket.objects.all().delete()
        Raffle.objects.all().delete()
        result['limpieza'] = 'OK'
    except Exception as e:
        result['limpieza_error'] = str(e)
    
    # Obtener organizador
    organizador = User.objects.filter(rol='organizador', is_active=True).first()
    if not organizador:
        organizador = User.objects.filter(is_active=True).first()
    
    if not organizador:
        return JsonResponse({'error': 'No hay usuarios'}, status=400)
    
    result['organizador'] = organizador.email
    
    # Obtener participantes
    participantes = list(User.objects.filter(is_active=True))
    
    # Datos de rifas
    rifas_data = [
        {"titulo": "🎮 PlayStation 5 Digital Edition", "premio_principal": "PlayStation 5 Digital Edition", "valor_premio": Decimal("450000"), "precio_boleto": Decimal("2500"), "total_boletos": 200, "hora_sorteo": "18:30"},
        {"titulo": "📱 iPhone 15 Pro Max 256GB", "premio_principal": "iPhone 15 Pro Max 256GB", "valor_premio": Decimal("1200000"), "precio_boleto": Decimal("5000"), "total_boletos": 300, "hora_sorteo": "18:45"},
        {"titulo": "💻 MacBook Air M3 15 pulgadas", "premio_principal": "MacBook Air M3 15\"", "valor_premio": Decimal("1400000"), "precio_boleto": Decimal("7000"), "total_boletos": 250, "hora_sorteo": "19:00"},
        {"titulo": "🎧 AirPods Pro 2da Generación", "premio_principal": "AirPods Pro 2da Gen", "valor_premio": Decimal("280000"), "precio_boleto": Decimal("1500"), "total_boletos": 200, "hora_sorteo": "19:15"},
        {"titulo": "🖥️ Monitor Gaming Samsung 27\" 144Hz", "premio_principal": "Monitor Samsung Odyssey G5", "valor_premio": Decimal("350000"), "precio_boleto": Decimal("2000"), "total_boletos": 200, "hora_sorteo": "19:30"},
        {"titulo": "⌚ Apple Watch Series 9 GPS", "premio_principal": "Apple Watch Series 9 45mm", "valor_premio": Decimal("500000"), "precio_boleto": Decimal("2500"), "total_boletos": 220, "hora_sorteo": "19:45"},
        {"titulo": "🎮 Nintendo Switch OLED + Juegos", "premio_principal": "Nintendo Switch OLED Bundle", "valor_premio": Decimal("450000"), "precio_boleto": Decimal("2000"), "total_boletos": 250, "hora_sorteo": "20:00"},
        {"titulo": "📷 GoPro Hero 12 Black", "premio_principal": "GoPro Hero 12 Black", "valor_premio": Decimal("380000"), "precio_boleto": Decimal("2000"), "total_boletos": 200, "hora_sorteo": "20:15"},
        {"titulo": "🎤 Micrófono Blue Yeti X Pro", "premio_principal": "Blue Yeti X Professional", "valor_premio": Decimal("180000"), "precio_boleto": Decimal("1000"), "total_boletos": 200, "hora_sorteo": "20:30"},
        {"titulo": "🖱️ Setup Gaming Completo", "premio_principal": "Kit Gaming Premium", "valor_premio": Decimal("320000"), "precio_boleto": Decimal("1500"), "total_boletos": 230, "hora_sorteo": "18:35"},
        {"titulo": "📚 Kindle Paperwhite + Crédito Amazon", "premio_principal": "Kindle Paperwhite Bundle", "valor_premio": Decimal("200000"), "precio_boleto": Decimal("1000"), "total_boletos": 220, "hora_sorteo": "19:10"},
        {"titulo": "🎵 Parlante JBL PartyBox 310", "premio_principal": "JBL PartyBox 310", "valor_premio": Decimal("550000"), "precio_boleto": Decimal("3000"), "total_boletos": 200, "hora_sorteo": "19:50"},
        {"titulo": "🏠 Robot Aspiradora Roomba j7+", "premio_principal": "iRobot Roomba j7+", "valor_premio": Decimal("700000"), "precio_boleto": Decimal("3500"), "total_boletos": 220, "hora_sorteo": "20:20"},
        {"titulo": "☕ Cafetera Nespresso Vertuo Plus", "premio_principal": "Nespresso Vertuo Plus Bundle", "valor_premio": Decimal("250000"), "precio_boleto": Decimal("1500"), "total_boletos": 180, "hora_sorteo": "18:50"},
        {"titulo": "🎒 Mochila Peak Design + Accesorios", "premio_principal": "Peak Design Everyday Backpack 30L", "valor_premio": Decimal("380000"), "precio_boleto": Decimal("2000"), "total_boletos": 200, "hora_sorteo": "19:25"},
    ]
    
    for data in rifas_data:
        try:
            hora, minuto = map(int, data["hora_sorteo"].split(":"))
            fecha_sorteo = CHILE_TZ.localize(datetime(hoy.year, hoy.month, hoy.day, hora, minuto, 0))
            fecha_inicio = timezone.now() - timedelta(days=7)
            
            rifa = Raffle.objects.create(
                organizador=organizador,
                titulo=data["titulo"],
                descripcion=f"Rifa de {data['premio_principal']}. ¡Participa y gana!",
                precio_boleto=data["precio_boleto"],
                total_boletos=data["total_boletos"],
                boletos_vendidos=data["total_boletos"],
                fecha_inicio=fecha_inicio,
                fecha_sorteo=fecha_sorteo,
                estado='activa',
                premio_principal=data["premio_principal"],
                descripcion_premio=f"Premio: {data['premio_principal']}",
                valor_premio=data["valor_premio"],
                permite_multiples_boletos=True,
                max_boletos_por_usuario=20,
            )
            
            # Crear boletos
            boletos_bulk = []
            for num in range(1, data["total_boletos"] + 1):
                participante = random.choice(participantes)
                boletos_bulk.append(Ticket(
                    rifa=rifa,
                    usuario=participante,
                    numero_boleto=num,
                    estado='pagado',
                    codigo_qr=f"QR-{rifa.id}-{num}-{uuid.uuid4().hex[:8].upper()}"
                ))
            
            Ticket.objects.bulk_create(boletos_bulk)
            
            result['rifas_creadas'].append({
                'titulo': data["titulo"],
                'sorteo': data["hora_sorteo"],
                'boletos': data["total_boletos"]
            })
            result['total_boletos'] += data["total_boletos"]
            
        except Exception as e:
            result['rifas_creadas'].append({
                'titulo': data["titulo"],
                'error': str(e)
            })
    
    result['success'] = True
    result['mensaje'] = f'{len(rifas_data)} rifas creadas con {result["total_boletos"]} boletos'
    
    return JsonResponse(result, status=200)

