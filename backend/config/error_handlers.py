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
    # Log error without exposing sensitive details
    logger.error(f"500 Internal Server Error: {request.path} from IP {request.META.get('REMOTE_ADDR')}")
    return render(request, '500.html', status=500)
