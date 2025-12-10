"""
Custom error handlers for secure error display
No sensitive information is leaked in error responses
"""
from django.shortcuts import render
from django.http import HttpResponseServerError
import logging

logger = logging.getLogger(__name__)


def bad_request_view(request, exception=None):
    """Handle 400 Bad Request errors"""
    logger.warning(f"400 Bad Request: {request.path} from IP {request.META.get('REMOTE_ADDR')}")
    return render(request, '400.html', status=400)


def permission_denied_view(request, exception=None):
    """Handle 403 Permission Denied errors"""
    logger.warning(f"403 Permission Denied: {request.path} by user {request.user} from IP {request.META.get('REMOTE_ADDR')}")
    return render(request, '403.html', status=403)


def page_not_found_view(request, exception=None):
    """Handle 404 Page Not Found errors"""
    logger.info(f"404 Not Found: {request.path} from IP {request.META.get('REMOTE_ADDR')}")
    return render(request, '404.html', status=404)


def server_error_view(request):
    """Handle 500 Internal Server Error"""
    import traceback
    import sys
    
    # Capturar información del error
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    # Log detallado del error
    logger.error(f"500 Internal Server Error: {request.path}")
    logger.error(f"User: {request.user if hasattr(request, 'user') else 'Anonymous'}")
    logger.error(f"IP: {request.META.get('REMOTE_ADDR')}")
    logger.error(f"Method: {request.method}")
    
    if exc_type:
        logger.error(f"Exception Type: {exc_type.__name__}")
        logger.error(f"Exception Value: {str(exc_value)}")
        logger.error(f"Traceback:\n{''.join(traceback.format_tb(exc_traceback))}")
    
    return render(request, '500.html', status=500)
