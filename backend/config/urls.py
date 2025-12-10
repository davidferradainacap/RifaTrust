from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.raffles.views import home_view
from apps.core.views import health_check
from django.shortcuts import redirect

def redirect_to_admin(request):
    """Redirect /admin to admin panel"""
    if request.user.is_authenticated and request.user.rol == 'admin':
        return redirect('/admin-panel/dashboard/')
    else:
        return redirect('/login/')

urlpatterns = [
    # Health check para Azure
    path('health/', health_check, name='health_check'),

    path('admin/', redirect_to_admin),
    path('django-admin/', admin.site.urls),  # Django admin original

    # API REST
    path('api/', include('config.api_urls')),

    # Vistas tradicionales
    path('', home_view, name='home'),
    path('', include('apps.users.urls')),
    path('raffles/', include('apps.raffles.urls')),
    path('payments/', include('apps.payments.urls')),
    path('admin-panel/', include('apps.admin_panel.urls')),
]

# Custom error handlers
handler400 = 'config.error_handlers.bad_request_view'
handler403 = 'config.error_handlers.permission_denied_view'
handler404 = 'config.error_handlers.page_not_found_view'
handler500 = 'config.error_handlers.server_error_view'

# Servir archivos media en desarrollo Y producción
# En Azure App Service, los archivos media se sirven desde el sistema de archivos local
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
