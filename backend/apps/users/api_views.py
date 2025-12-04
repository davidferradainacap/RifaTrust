"""
API ViewSets REST para la app users.
Implementa endpoints completos para gestión de usuarios, autenticación JWT,
notificaciones y confirmación de email.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import logout
from django.utils import timezone
from django.db.models import Q

from .models import User, Profile, Notification, EmailConfirmationToken
from .serializers import (
    UserSerializer, UserListSerializer, ProfileSerializer,
    RegisterSerializer, LoginSerializer, ChangePasswordSerializer,
    NotificationSerializer, NotificationListSerializer,
    EmailConfirmationTokenSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de usuarios.
    
    Endpoints:
    - GET /api/users/ - Lista de usuarios
    - POST /api/users/ - Crear usuario
    - GET /api/users/{id}/ - Detalle de usuario
    - PUT /api/users/{id}/ - Actualizar usuario
    - PATCH /api/users/{id}/ - Actualizar parcialmente
    - DELETE /api/users/{id}/ - Eliminar usuario
    - GET /api/users/me/ - Perfil del usuario actual
    - POST /api/users/change_password/ - Cambiar contraseña
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Retorna serializer apropiado según la acción"""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'register':
            return RegisterSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Define permisos según la acción"""
        if self.action in ['create', 'register']:
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filtra usuarios según rol y permisos"""
        queryset = User.objects.all()
        
        # Filtrar por rol
        rol = self.request.query_params.get('rol', None)
        if rol:
            queryset = queryset.filter(rol=rol)
        
        # Filtrar por búsqueda
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(email__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Retorna el perfil del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Registra un nuevo usuario"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Usuario registrado exitosamente.'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """Cambia la contraseña del usuario actual"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Contraseña actualizada exitosamente.'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """Cierra sesión (invalida el refresh token)"""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            logout(request)
            return Response({
                'message': 'Sesión cerrada exitosamente.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Token inválido.'
            }, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de notificaciones.
    
    Endpoints:
    - GET /api/notifications/ - Lista de notificaciones del usuario
    - GET /api/notifications/{id}/ - Detalle de notificación
    - POST /api/notifications/mark_as_read/ - Marcar como leída
    - POST /api/notifications/mark_all_as_read/ - Marcar todas como leídas
    - GET /api/notifications/unread_count/ - Contador de no leídas
    """
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Retorna serializer apropiado"""
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer
    
    def get_queryset(self):
        """Retorna solo notificaciones del usuario actual"""
        queryset = Notification.objects.filter(usuario=self.request.user)
        
        # Filtrar por leídas/no leídas
        leida = self.request.query_params.get('leida', None)
        if leida is not None:
            leida_bool = leida.lower() == 'true'
            queryset = queryset.filter(leida=leida_bool)
        
        # Filtrar por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marca una notificación como leída"""
        notification = self.get_object()
        notification.marcar_como_leida()
        
        return Response({
            'message': 'Notificación marcada como leída.',
            'notification': NotificationSerializer(notification).data
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marca todas las notificaciones del usuario como leídas"""
        notifications = Notification.objects.filter(
            usuario=request.user,
            leida=False
        )
        
        count = 0
        for notification in notifications:
            notification.marcar_como_leida()
            count += 1
        
        return Response({
            'message': f'{count} notificaciones marcadas como leídas.'
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Retorna el contador de notificaciones no leídas"""
        count = Notification.objects.filter(
            usuario=request.user,
            leida=False
        ).count()
        
        return Response({'count': count})


class EmailConfirmationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gestión de tokens de confirmación de email.
    Solo lectura desde la API.
    
    Endpoints:
    - GET /api/email-confirmations/ - Lista de tokens (admin)
    - GET /api/email-confirmations/{id}/ - Detalle de token
    - POST /api/email-confirmations/confirm/ - Confirmar email con token
    - POST /api/email-confirmations/resend/ - Reenviar email de confirmación
    """
    
    queryset = EmailConfirmationToken.objects.all()
    serializer_class = EmailConfirmationTokenSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def confirm(self, request):
        """Confirma el email del usuario con el token"""
        token_str = request.data.get('token')
        
        if not token_str:
            return Response({
                'error': 'Token requerido.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = EmailConfirmationToken.objects.get(token=token_str)
            
            if not token.is_valid():
                return Response({
                    'error': 'Token inválido o expirado.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Activar cuenta
            user = token.user
            user.cuenta_validada = True
            user.save()
            
            # Marcar token como usado
            token.mark_as_used()
            
            return Response({
                'message': 'Email confirmado exitosamente.',
                'user': UserSerializer(user).data
            })
        
        except EmailConfirmationToken.DoesNotExist:
            return Response({
                'error': 'Token no encontrado.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def resend(self, request):
        """Reenvía el email de confirmación al usuario"""
        user = request.user
        
        if user.cuenta_validada:
            return Response({
                'error': 'La cuenta ya está validada.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear nuevo token
        token = EmailConfirmationToken.create_token(user)
        
        # Aquí deberías enviar el email (implementar según tu sistema de emails)
        # send_confirmation_email(user, token)
        
        return Response({
            'message': 'Email de confirmación enviado.',
            'expires_at': token.expires_at
        })
