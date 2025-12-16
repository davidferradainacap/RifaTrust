"""
Servicio de envío de emails para confirmación de cuenta

Maneja el envío de emails de confirmación con tokens de activación
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class EmailConfirmationService:
    """
    Servicio para enviar emails de confirmación de cuenta
    """

    @staticmethod
    def send_confirmation_email(user, token, request=None):
        """
        Envía email de confirmación al usuario con link de activación

        Args:
            user: Usuario que se registró
            token: Token de confirmación generado
            request: Request de Django (opcional, para obtener dominio)

        Returns:
            bool: True si el email se envió exitosamente
        """
        try:
            # Construir URL de confirmación
            if request:
                domain = request.get_host()
                protocol = 'https' if request.is_secure() else 'http'
            else:
                domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
                protocol = 'http' if settings.DEBUG else 'https'

            confirmation_url = f"{protocol}://{domain}/confirm-email/{token.token}/"

            # Contexto para el template
            context = {
                'user': user,
                'confirmation_url': confirmation_url,
                'expires_in': '24 horas',
                'site_name': 'RifaTrust',
            }

            # Versión en texto plano (principal)
            plain_message = f"""
Hola {user.nombre},

¡Bienvenido a RifaTrust!

Para completar tu registro, por favor confirma tu dirección de correo electrónico haciendo clic en el siguiente enlace:

{confirmation_url}

Este enlace expirará en 24 horas.

Si no solicitaste crear una cuenta, puedes ignorar este mensaje.

Saludos,
El equipo de RifaTrust
            """.strip()

            # Intentar renderizar HTML (opcional)
            html_message = None
            try:
                html_message = render_to_string('users/emails/confirm_email.html', context)
            except Exception as template_error:
                logger.warning(f"No se pudo renderizar template HTML: {str(template_error)}")

            # Enviar email
            send_mail(
                subject='Confirma tu cuenta en RifaTrust',
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rifatrust.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Email de confirmación enviado exitosamente a {user.email}")
            return True

        except Exception as e:
            logger.error(f"Error al enviar email de confirmación a {user.email}: {str(e)}")
            return False

    @staticmethod
    def send_welcome_email(user):
        """
        Envía email de bienvenida después de confirmar la cuenta

        Args:
            user: Usuario que confirmó su cuenta

        Returns:
            bool: True si el email se envió exitosamente
        """
        try:
            context = {
                'user': user,
                'site_name': 'RifaTrust',
                'dashboard_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/dashboard/",
            }

            plain_message = f"""
¡Hola {user.nombre}!

Tu cuenta ha sido activada exitosamente. ¡Bienvenido a RifaTrust!

Ya puedes iniciar sesión y comenzar a participar en rifas, crear tus propias rifas o patrocinar eventos.

Saludos,
El equipo de RifaTrust
            """.strip()

            # Intentar renderizar HTML (opcional)
            html_message = None
            try:
                html_message = render_to_string('users/emails/welcome_email.html', context)
            except Exception as template_error:
                logger.warning(f"No se pudo renderizar template HTML de bienvenida: {str(template_error)}")

            send_mail(
                subject='¡Bienvenido a RifaTrust!',
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rifatrust.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Email de bienvenida enviado a {user.email}")
            return True

        except Exception as e:
            logger.error(f"Error al enviar email de bienvenida a {user.email}: {str(e)}")
            return False


class PasswordResetService:
    """
    Servicio para enviar emails de recuperación de contraseña
    """

    @staticmethod
    def send_reset_email(user, token, request=None):
        """
        Envía email de recuperación de contraseña con link de reset

        Args:
            user: Usuario que solicitó resetear contraseña
            token: Token de recuperación generado
            request: Request de Django (opcional, para obtener dominio)

        Returns:
            bool: True si el email se envió exitosamente
        """
        try:
            # Construir URL de reset
            if request:
                domain = request.get_host()
                protocol = 'https' if request.is_secure() else 'http'
            else:
                domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
                protocol = 'http' if settings.DEBUG else 'https'

            # URL correcta según urls.py: /reset-password/<token>/
            token_str = token.token if hasattr(token, 'token') else str(token)
            reset_url = f"{protocol}://{domain}/reset-password/{token_str}/"

            # Contexto para el template
            context = {
                'user': user,
                'reset_url': reset_url,
                'expires_in': '1 hora',
                'site_name': 'RifaTrust',
            }

            # Versión en texto plano (principal)
            plain_message = f"""
Hola {user.nombre},

Recibimos una solicitud para restablecer la contraseña de tu cuenta en RifaTrust.

Para crear una nueva contraseña, haz clic en el siguiente enlace:

{reset_url}

Este enlace expirará en 1 hora por seguridad.

Si no solicitaste restablecer tu contraseña, puedes ignorar este mensaje. Tu contraseña actual permanecerá sin cambios.

Saludos,
El equipo de RifaTrust
            """.strip()

            # Intentar renderizar HTML (opcional)
            html_message = None
            try:
                html_message = render_to_string('users/emails/password_reset.html', context)
            except Exception as template_error:
                logger.warning(f"No se pudo renderizar template HTML: {str(template_error)}")

            # Enviar email
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rifatrust.com')
            logger.info(f"Intentando enviar email desde {from_email} a {user.email}")
            logger.info(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

            if settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
                logger.info(f"SMTP Config - Host: {settings.EMAIL_HOST}, Port: {settings.EMAIL_PORT}, TLS: {settings.EMAIL_USE_TLS}")

            send_mail(
                subject='Recuperación de contraseña - RifaTrust',
                message=plain_message,
                from_email=from_email,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"✅ Email de recuperación enviado exitosamente a {user.email}")
            return True

        except Exception as e:
            import traceback
            logger.error(f"❌ Error al enviar email de recuperación a {user.email}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return False

    @staticmethod
    def send_password_changed_notification(user):
        """
        Envía email de notificación cuando la contraseña fue cambiada

        Args:
            user: Usuario que cambió su contraseña

        Returns:
            bool: True si el email se envió exitosamente
        """
        try:
            context = {
                'user': user,
                'site_name': 'RifaTrust',
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'soporte@rifatrust.com'),
            }

            plain_message = f"""
Hola {user.nombre},

Te confirmamos que la contraseña de tu cuenta en RifaTrust ha sido cambiada exitosamente.

Fecha y hora: {timezone.now().strftime('%d/%m/%Y a las %H:%M')}

Si no realizaste este cambio, por favor contacta inmediatamente a nuestro equipo de soporte en {context['support_email']}.

Saludos,
El equipo de RifaTrust
            """.strip()

            # Intentar renderizar HTML (opcional)
            html_message = None
            try:
                html_message = render_to_string('users/emails/password_changed.html', context)
            except Exception as template_error:
                logger.warning(f"No se pudo renderizar template HTML: {str(template_error)}")

            send_mail(
                subject='Contraseña actualizada - RifaTrust',
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rifatrust.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Notificación de cambio de contraseña enviada a {user.email}")
            return True

        except Exception as e:
            logger.error(f"Error al enviar notificación de cambio de contraseña a {user.email}: {str(e)}")
            return False
