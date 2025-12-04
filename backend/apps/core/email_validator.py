"""
Email verification service using AbstractAPI (free tier: 100 requests/month)
Alternative: EmailListVerify, ZeroBounce, or Hunter.io

Para obtener tu API key gratuita:
1. Visita: https://www.abstractapi.com/api/email-verification-validation-api
2. Regístrate gratis (100 requests/mes)
3. Copia tu API key
4. Agrégala al archivo .env como: EMAIL_VERIFICATION_API_KEY=tu_api_key
"""

import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class EmailVerificationService:
    """
    Servicio de verificación de emails usando AbstractAPI

    Verifica:
    - Formato válido del email
    - Si el dominio existe (MX records)
    - Si el email es desechable/temporal
    - Si el email es de un proveedor gratuito (Gmail, Yahoo, etc.)
    - Score de calidad del email
    """

    API_URL = "https://emailvalidation.abstractapi.com/v1/"

    def __init__(self):
        self.api_key = getattr(settings, 'EMAIL_VERIFICATION_API_KEY', None)
        self.enabled = bool(self.api_key)

    def verify_email(self, email: str) -> dict:
        """
        Verifica un email usando AbstractAPI

        Args:
            email (str): Email a verificar

        Returns:
            dict: {
                'is_valid': bool,
                'is_smtp_valid': bool,
                'is_disposable': bool,
                'is_free_email': bool,
                'quality_score': float,
                'error': str (opcional)
            }
        """
        # Si no está configurada la API, retornar validación básica
        if not self.enabled:
            logger.warning("Email verification API not configured. Using basic validation.")
            return self._basic_validation(email)

        # Verificar cache (evitar llamadas repetidas)
        cache_key = f"email_verification_{email.lower()}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Email verification from cache: {email}")
            return cached_result

        try:
            # Realizar petición a AbstractAPI
            response = requests.get(
                self.API_URL,
                params={
                    'api_key': self.api_key,
                    'email': email
                },
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                result = {
                    'is_valid': data.get('is_valid_format', {}).get('value', False) and
                               data.get('is_mx_found', {}).get('value', False),
                    'is_smtp_valid': data.get('is_smtp_valid', {}).get('value', False),
                    'is_disposable': data.get('is_disposable_email', {}).get('value', False),
                    'is_free_email': data.get('is_free_email', {}).get('value', False),
                    'quality_score': data.get('quality_score', 0.0),
                    'email': email,
                }

                # Guardar en cache por 7 días
                cache.set(cache_key, result, 60 * 60 * 24 * 7)

                logger.info(f"Email verified successfully: {email} - Valid: {result['is_valid']}")
                return result

            else:
                error_msg = f"API returned status {response.status_code}"
                logger.error(f"Email verification failed: {error_msg}")
                return {**self._basic_validation(email), 'error': error_msg}

        except requests.exceptions.Timeout:
            logger.error("Email verification timeout")
            return {**self._basic_validation(email), 'error': 'Timeout'}

        except requests.exceptions.RequestException as e:
            logger.error(f"Email verification request failed: {str(e)}")
            return {**self._basic_validation(email), 'error': str(e)}

        except Exception as e:
            logger.error(f"Unexpected error during email verification: {str(e)}")
            return {**self._basic_validation(email), 'error': str(e)}

    def _basic_validation(self, email: str) -> dict:
        """
        Validación básica de email sin API (fallback)

        Args:
            email (str): Email a validar

        Returns:
            dict: Resultado básico de validación
        """
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(email_regex, email))

        # Detectar dominios desechables comunes
        disposable_domains = [
            'tempmail.com', 'guerrillamail.com', '10minutemail.com',
            'mailinator.com', 'throwaway.email', 'temp-mail.org'
        ]
        domain = email.split('@')[-1].lower() if '@' in email else ''
        is_disposable = domain in disposable_domains

        # Detectar proveedores gratuitos comunes
        free_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        is_free = domain in free_domains

        return {
            'is_valid': is_valid and not is_disposable,
            'is_smtp_valid': is_valid,
            'is_disposable': is_disposable,
            'is_free_email': is_free,
            'quality_score': 0.8 if is_valid and not is_disposable else 0.3,
            'email': email,
        }

    def is_email_valid(self, email: str) -> bool:
        """
        Método simplificado que retorna solo True/False

        Args:
            email (str): Email a verificar

        Returns:
            bool: True si el email es válido
        """
        result = self.verify_email(email)
        return result.get('is_valid', False)

    def get_detailed_report(self, email: str) -> str:
        """
        Genera un reporte legible del estado del email

        Args:
            email (str): Email a verificar

        Returns:
            str: Reporte en texto
        """
        result = self.verify_email(email)

        if result.get('error'):
            return f"❌ Error al verificar: {result['error']}"

        report = []
        report.append(f"📧 Email: {email}")
        report.append(f"✅ Formato válido: {'Sí' if result['is_valid'] else 'No'}")
        report.append(f"📬 SMTP válido: {'Sí' if result['is_smtp_valid'] else 'No'}")
        report.append(f"🗑️ Email desechable: {'Sí' if result['is_disposable'] else 'No'}")
        report.append(f"🆓 Proveedor gratuito: {'Sí' if result['is_free_email'] else 'No'}")
        report.append(f"⭐ Puntuación de calidad: {result['quality_score']:.2f}")

        return "\n".join(report)


# Instancia global del servicio
email_verifier = EmailVerificationService()


# Funciones helper para uso rápido
def verify_email(email: str) -> dict:
    """Verifica un email y retorna el resultado completo"""
    return email_verifier.verify_email(email)


def is_valid_email(email: str) -> bool:
    """Verifica si un email es válido (True/False)"""
    return email_verifier.is_email_valid(email)


def get_email_report(email: str) -> str:
    """Obtiene un reporte detallado del email"""
    return email_verifier.get_detailed_report(email)
