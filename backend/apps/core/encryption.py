"""
Utilidades de encriptación para datos sensibles
"""
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib

def get_encryption_key():
    """
    Genera una clave de encriptación basada en SECRET_KEY
    """
    # Usar SECRET_KEY como base para la clave de encriptación
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_data(data):
    """
    Encripta datos sensibles
    """
    if not data:
        return data
    
    try:
        fernet = Fernet(get_encryption_key())
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode()
    except Exception as e:
        # En caso de error, loguear y retornar dato sin encriptar
        # Esto previene que la aplicación falle
        print(f"Error al encriptar: {e}")
        return data

def decrypt_data(encrypted_data):
    """
    Desencripta datos sensibles
    """
    if not encrypted_data:
        return encrypted_data
    
    try:
        fernet = Fernet(get_encryption_key())
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        # Si no se puede desencriptar, retornar el valor original
        # Esto permite compatibilidad con datos no encriptados
        return encrypted_data

def hash_sensitive_data(data):
    """
    Hashea datos sensibles de forma irreversible (para búsquedas)
    """
    if not data:
        return data
    
    return hashlib.sha256(data.encode()).hexdigest()
