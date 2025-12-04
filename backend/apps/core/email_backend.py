"""
Custom Email Backend for SendGrid with SSL certificate handling

En desarrollo (DEBUG=True): Desactiva verificación de certificados para evitar errores locales
En producción (DEBUG=False): Usa verificación completa de certificados SSL
"""
import ssl
from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend
from django.conf import settings


class SendGridEmailBackend(DjangoEmailBackend):
    """
    Custom email backend for SendGrid that handles SSL certificate issues
    - Development: Bypasses certificate verification (DEBUG=True)
    - Production: Full SSL certificate verification (DEBUG=False)
    """

    def open(self):
        """
        Override open method to handle SSL certificate verification based on environment
        """
        if self.connection:
            return False

        connection_params = {
            'timeout': self.timeout,
        }

        if self.use_ssl:
            connection_params['context'] = ssl.create_default_context()

        try:
            self.connection = self.connection_class(
                self.host,
                self.port,
                **connection_params
            )

            if not self.use_ssl and self.use_tls:
                # Create SSL context
                context = ssl.create_default_context()

                # ONLY disable certificate verification in development
                if settings.DEBUG:
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                # Production: Full SSL verification enabled automatically

                self.connection.starttls(context=context)

            if self.username and self.password:
                self.connection.login(self.username, self.password)

            return True
        except Exception as e:
            if not self.fail_silently:
                raise
            return False
