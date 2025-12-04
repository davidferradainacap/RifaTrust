"""
============================================================================
MANEJO SEGURO DE EXCEPCIONES - RifaTrust
============================================================================
Funciones para manejar excepciones sin exponer detalles internos.
Previene ataques de reconocimiento y exposición de información sensible.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_safe_error_message(exception, user_message="Ocurrió un error inesperado", log_prefix="Error"):
    """
    Registra el error completo en logs y devuelve un mensaje seguro para el usuario.

    Args:
        exception: La excepción capturada
        user_message: Mensaje genérico para mostrar al usuario
        log_prefix: Prefijo para el log

    Returns:
        str: Mensaje seguro para mostrar al usuario
    """
    # Log completo del error (solo visible en logs del servidor)
    logger.error(f"{log_prefix}: {str(exception)}", exc_info=True)

    # En DEBUG, mostrar el error real (solo desarrollo)
    if settings.DEBUG:
        return f"{user_message}. Detalle (solo DEBUG): {str(exception)}"

    # En producción, solo mensaje genérico
    return user_message


def safe_json_error(exception, default_message="Ocurrió un error al procesar la solicitud"):
    """
    Genera un diccionario de error seguro para respuestas JSON.

    Args:
        exception: La excepción capturada
        default_message: Mensaje por defecto para el usuario

    Returns:
        dict: Diccionario con error seguro
    """
    message = get_safe_error_message(exception, default_message, "JSON Error")

    return {
        'success': False,
        'error': default_message if not settings.DEBUG else f"{default_message}: {str(exception)}"
    }


def log_and_get_user_message(exception, context="", user_message="Operación fallida"):
    """
    Registra la excepción con contexto y retorna mensaje para el usuario.

    Args:
        exception: Excepción capturada
        context: Contexto adicional para el log
        user_message: Mensaje amigable para el usuario

    Returns:
        str: Mensaje seguro para mostrar
    """
    logger.error(f"{context} - {str(exception)}", exc_info=True)

    # Solo en DEBUG mostrar detalles
    if settings.DEBUG:
        return f"{user_message}. Debug: {str(exception)}"

    return user_message


# Mensajes genéricos predefinidos
ERROR_MESSAGES = {
    'payment': 'Error al procesar el pago. Por favor, intenta nuevamente.',
    'email': 'Error al enviar el correo electrónico. Contacta a soporte si el problema persiste.',
    'database': 'Error al acceder a la base de datos. Intenta nuevamente más tarde.',
    'validation': 'Los datos ingresados no son válidos. Verifica e intenta nuevamente.',
    'permission': 'No tienes permisos para realizar esta acción.',
    'not_found': 'El recurso solicitado no existe.',
    'server': 'Error interno del servidor. Nuestro equipo ha sido notificado.',
    'raffle': 'Error al procesar la rifa. Contacta al organizador.',
    'ticket': 'Error al procesar el boleto. Intenta nuevamente.',
    'winner': 'Error al seleccionar ganador. Contacta a soporte.',
    'refund': 'Error al procesar el reembolso. Contacta a soporte.',
    'notification': 'Error al enviar la notificación.',
    'upload': 'Error al subir el archivo. Verifica el formato y tamaño.',
    'authentication': 'Error en la autenticación. Intenta iniciar sesión nuevamente.',
    'authorization': 'No estás autorizado para acceder a este recurso.',
}


def get_error_message(error_type='server'):
    """
    Obtiene un mensaje de error genérico según el tipo.

    Args:
        error_type: Tipo de error (ver ERROR_MESSAGES)

    Returns:
        str: Mensaje de error genérico
    """
    return ERROR_MESSAGES.get(error_type, ERROR_MESSAGES['server'])


def handle_exception_safely(exception, error_type='server', extra_context=None):
    """
    Maneja una excepción de forma segura, registrándola y retornando mensaje genérico.

    Args:
        exception: Excepción a manejar
        error_type: Tipo de error para seleccionar mensaje
        extra_context: Contexto adicional para el log

    Returns:
        str: Mensaje seguro para el usuario
    """
    # Log con contexto
    context = f"[{error_type.upper()}]"
    if extra_context:
        context += f" {extra_context}"

    logger.error(f"{context}: {str(exception)}", exc_info=True)

    # Mensaje para el usuario
    user_message = get_error_message(error_type)

    # Solo en DEBUG agregar detalles
    if settings.DEBUG:
        user_message += f" [DEBUG: {str(exception)}]"

    return user_message
