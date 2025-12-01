"""
Campos de modelo personalizados con encriptación
"""
from django.db import models
from .encryption import encrypt_data, decrypt_data

class EncryptedCharField(models.CharField):
    """
    CharField que encripta datos automáticamente
    """
    
    def from_db_value(self, value, expression, connection):
        """Desencripta al leer de la base de datos"""
        if value is None:
            return value
        return decrypt_data(value)
    
    def get_prep_value(self, value):
        """Encripta antes de guardar en la base de datos"""
        if value is None:
            return value
        return encrypt_data(str(value))

class EncryptedTextField(models.TextField):
    """
    TextField que encripta datos automáticamente
    """
    
    def from_db_value(self, value, expression, connection):
        """Desencripta al leer de la base de datos"""
        if value is None:
            return value
        return decrypt_data(value)
    
    def get_prep_value(self, value):
        """Encripta antes de guardar en la base de datos"""
        if value is None:
            return value
        return encrypt_data(str(value))

class EncryptedEmailField(models.EmailField):
    """
    EmailField que encripta datos automáticamente
    """
    
    def from_db_value(self, value, expression, connection):
        """Desencripta al leer de la base de datos"""
        if value is None:
            return value
        return decrypt_data(value)
    
    def get_prep_value(self, value):
        """Encripta antes de guardar en la base de datos"""
        if value is None:
            return value
        # Los emails se normalizan a minúsculas antes de encriptar
        return encrypt_data(str(value).lower())
