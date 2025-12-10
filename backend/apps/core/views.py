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
