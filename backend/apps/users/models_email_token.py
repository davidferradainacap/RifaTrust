"""
Modelo para tokens de confirmación de email

Este modelo almacena tokens únicos para verificar cuentas de usuario por email
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import secrets
from datetime import timedelta

User = get_user_model()


class EmailConfirmationToken(models.Model):
    """
    Token de confirmación de email que expira en 24 horas

    Campos:
        user: Usuario asociado al token
        token: Token único generado con secrets (64 caracteres hex)
        created_at: Fecha de creación del token
        expires_at: Fecha de expiración (created_at + 24h)
        is_used: Si el token ya fue utilizado
        used_at: Fecha en que se usó el token
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_confirmation_tokens',
        verbose_name='Usuario'
    )

    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Token'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    expires_at = models.DateTimeField(
        verbose_name='Fecha de Expiración'
    )

    is_used = models.BooleanField(
        default=False,
        verbose_name='Token Utilizado'
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Uso'
    )

    class Meta:
        verbose_name = 'Token de Confirmación'
        verbose_name_plural = 'Tokens de Confirmación'
        ordering = ['-created_at']

    def __str__(self):
        return f"Token para {self.user.email} - {'Usado' if self.is_used else 'Activo'}"

    @classmethod
    def create_token(cls, user):
        """
        Crea un nuevo token de confirmación para el usuario

        Args:
            user: Instancia del usuario

        Returns:
            EmailConfirmationToken: Token creado
        """
        # Generar token único de 64 caracteres hexadecimales
        token = secrets.token_urlsafe(48)  # 48 bytes = 64 caracteres base64url

        # Calcular fecha de expiración (24 horas)
        expires_at = timezone.now() + timedelta(hours=24)

        # Crear y guardar el token
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

    def is_valid(self):
        """
        Verifica si el token es válido (no usado y no expirado)

        Returns:
            bool: True si el token es válido
        """
        if self.is_used:
            return False

        if timezone.now() > self.expires_at:
            return False

        return True

    def mark_as_used(self):
        """
        Marca el token como utilizado
        """
        self.is_used = True
        self.used_at = timezone.now()
        self.save()

    def time_remaining(self):
        """
        Retorna el tiempo restante antes de que expire el token

        Returns:
            timedelta: Tiempo restante
        """
        if timezone.now() > self.expires_at:
            return timedelta(0)

        return self.expires_at - timezone.now()

    def time_remaining_str(self):
        """
        Retorna el tiempo restante en formato legible

        Returns:
            str: Ejemplo "23 horas, 45 minutos"
        """
        remaining = self.time_remaining()

        if remaining.total_seconds() <= 0:
            return "Expirado"

        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60

        if hours > 0:
            return f"{hours} hora{'s' if hours != 1 else ''}, {minutes} minuto{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minuto{'s' if minutes != 1 else ''}"
