"""
URLs de la API REST para RifaTrust.
Configura todos los endpoints con Django REST Router.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from apps.users.api_views import UserViewSet, NotificationViewSet, EmailConfirmationViewSet
from apps.raffles.api_views import (
    RaffleViewSet, TicketViewSet, SponsorshipRequestViewSet,
    OrganizerSponsorRequestViewSet, WinnerViewSet
)
from apps.payments.api_views import PaymentViewSet, RefundViewSet

# Crear router principal
router = DefaultRouter()

# Registrar ViewSets de users
router.register(r'users', UserViewSet, basename='user')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'email-confirmations', EmailConfirmationViewSet, basename='email-confirmation')

# Registrar ViewSets de raffles
router.register(r'raffles', RaffleViewSet, basename='raffle')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'sponsorship-requests', SponsorshipRequestViewSet, basename='sponsorship-request')
router.register(r'organizer-sponsor-requests', OrganizerSponsorRequestViewSet, basename='organizer-sponsor-request')
router.register(r'winners', WinnerViewSet, basename='winner')

# Registrar ViewSets de payments
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'refunds', RefundViewSet, basename='refund')

# URLs de la API
urlpatterns = [
    # Autenticación JWT
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Documentación de la API
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Incluir todas las rutas del router
    path('', include(router.urls)),
]
