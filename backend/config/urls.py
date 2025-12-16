from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from apps.raffles.views import home_view
from apps.core.views import health_check, email_config_check, test_send_email, serve_media, debug_media, debug_user_avatar
from django.shortcuts import redirect
import os

def redirect_to_admin(request):
    """Redirect /admin to admin panel"""
    if request.user.is_authenticated and request.user.rol == 'admin':
        return redirect('/admin-panel/dashboard/')
    else:
        return redirect('/login/')

urlpatterns = [
    # Health check para Azure
    path('health/', health_check, name='health_check'),
    path('email-check/', email_config_check, name='email_config_check'),
    path('test-email/', test_send_email, name='test_send_email'),
    path('debug-media/', debug_media, name='debug_media'),
    path('debug-user-avatar/', debug_user_avatar, name='debug_user_avatar'),

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

# Servir archivos media
# En Azure, usamos una vista personalizada para servir desde /home/media
if os.environ.get('WEBSITE_HOSTNAME'):
    # Azure - usar vista personalizada para servir media desde /home/media
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media, name='serve_media'),
    ]
else:
    # Desarrollo local - usar static() de Django
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
