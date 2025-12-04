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
    return JsonResponse({
        'status': 'healthy',
        'service': 'RifaTrust',
    }, status=200)
