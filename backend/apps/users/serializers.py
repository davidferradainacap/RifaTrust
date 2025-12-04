"""
Serializers REST para la app users.
Convierte modelos a JSON y viceversa, valida datos y controla permisos.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile, Notification, EmailConfirmationToken


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Profile con datos desencriptados"""
    
    class Meta:
        model = Profile
        fields = [
            'direccion', 'ciudad', 'estado', 
            'codigo_postal', 'pais', 'fecha_nacimiento'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer completo para User con profile anidado"""
    
    profile = ProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'nombre', 'telefono', 'rol', 
            'avatar', 'cuenta_validada', 'is_active', 
            'fecha_registro', 'ultima_conexion', 'profile', 'password'
        ]
        read_only_fields = ['id', 'fecha_registro', 'ultima_conexion', 'cuenta_validada']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Crea un nuevo usuario con perfil"""
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        
        # Crear usuario
        user = User.objects.create_user(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        # Crear perfil si se proporcionaron datos
        if profile_data:
            Profile.objects.create(user=user, **profile_data)
        else:
            Profile.objects.create(user=user)
        
        return user
    
    def update(self, instance, validated_data):
        """Actualiza usuario y perfil"""
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        
        # Actualizar usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        
        # Actualizar perfil
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de usuarios"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'nombre', 'rol', 'avatar', 'cuenta_validada']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos usuarios"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'nombre', 'telefono', 'password', 'password_confirm', 'rol']
        extra_kwargs = {
            'rol': {'default': 'participante'}
        }
    
    def validate(self, attrs):
        """Valida que las contraseñas coincidan"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        """Crea un nuevo usuario"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.cuenta_validada = False  # Requiere confirmación de email
        user.save()
        
        # Crear perfil vacío
        Profile.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login con JWT"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Valida credenciales y genera tokens JWT"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = authenticate(email=email, password=password)
        
        if user is None:
            raise serializers.ValidationError('Credenciales inválidas.')
        
        if not user.is_active:
            raise serializers.ValidationError('Usuario inactivo.')
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña"""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Valida que las contraseñas nuevas coincidan"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden."})
        return attrs
    
    def validate_old_password(self, value):
        """Valida que la contraseña antigua sea correcta"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Contraseña actual incorrecta.")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""
    
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    rifa_titulo = serializers.CharField(source='rifa_relacionada.titulo', read_only=True, allow_null=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'usuario', 'usuario_nombre', 'tipo', 'titulo', 
            'mensaje', 'enlace', 'leida', 'fecha_creacion', 
            'fecha_lectura', 'rifa_relacionada', 'rifa_titulo', 
            'tiempo_transcurrido'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_lectura']
    
    def get_tiempo_transcurrido(self, obj):
        """Calcula tiempo transcurrido desde la creación"""
        from django.utils.timesince import timesince
        return timesince(obj.fecha_creacion)


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de notificaciones"""
    
    class Meta:
        model = Notification
        fields = ['id', 'tipo', 'titulo', 'leida', 'fecha_creacion', 'enlace']


class EmailConfirmationTokenSerializer(serializers.ModelSerializer):
    """Serializer para tokens de confirmación de email"""
    
    usuario_email = serializers.EmailField(source='user.email', read_only=True)
    tiempo_restante = serializers.SerializerMethodField()
    es_valido = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailConfirmationToken
        fields = [
            'id', 'usuario_email', 'token', 'created_at', 
            'expires_at', 'is_used', 'used_at', 
            'tiempo_restante', 'es_valido'
        ]
        read_only_fields = ['token', 'created_at', 'expires_at', 'is_used', 'used_at']
    
    def get_tiempo_restante(self, obj):
        """Retorna el tiempo restante en formato legible"""
        return obj.time_remaining_str()
    
    def get_es_valido(self, obj):
        """Indica si el token es válido"""
        return obj.is_valid()
