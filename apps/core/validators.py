"""
Input validation and sanitization utilities for secure coding
"""
import re
import html
from django.core.exceptions import ValidationError


def sanitize_html(text):
    """Remove HTML tags and escape special characters"""
    if not text:
        return text
    # Escape HTML special characters
    return html.escape(str(text))


def sanitize_sql_input(text):
    """Prevent SQL injection by removing dangerous characters"""
    if not text:
        return text
    # Remove SQL special characters
    dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
    text = str(text)
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text


def validate_email_format(email):
    """Validate email format"""
    if not email:
        raise ValidationError("El email es requerido")
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValidationError("Formato de email inválido")
    
    return email.lower().strip()


def validate_phone_format(phone):
    """Validate Chilean phone format"""
    if not phone:
        return phone
    
    # Remove spaces and special characters
    phone = re.sub(r'[^\d+]', '', phone)
    
    # Chilean phone patterns: +56912345678 or 912345678
    phone_regex = r'^(\+?56)?9\d{8}$'
    if not re.match(phone_regex, phone):
        raise ValidationError("Formato de teléfono inválido. Use: +56912345678 o 912345678")
    
    return phone


def validate_rut_format(rut):
    """Validate Chilean RUT format"""
    if not rut:
        return rut
    
    # Remove dots and hyphens
    rut = rut.replace('.', '').replace('-', '').upper()
    
    # RUT format: 12345678-9 or 123456789
    if len(rut) < 8 or len(rut) > 9:
        raise ValidationError("RUT inválido")
    
    # Extract number and verification digit
    rut_number = rut[:-1]
    verification_digit = rut[-1]
    
    # Validate number part is numeric
    if not rut_number.isdigit():
        raise ValidationError("RUT inválido")
    
    # Calculate verification digit
    reversed_digits = map(int, reversed(rut_number))
    factors = [2, 3, 4, 5, 6, 7]
    s = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
    calculated_digit = (-s) % 11
    
    if calculated_digit == 10:
        calculated_digit = 'K'
    elif calculated_digit == 11:
        calculated_digit = '0'
    else:
        calculated_digit = str(calculated_digit)
    
    if verification_digit != calculated_digit:
        raise ValidationError("RUT inválido")
    
    return rut


def sanitize_filename(filename):
    """Sanitize filename to prevent directory traversal"""
    if not filename:
        return filename
    
    # Remove path separators and special characters
    filename = filename.replace('/', '').replace('\\', '').replace('..', '')
    
    # Only allow alphanumeric, dots, hyphens, and underscores
    filename = re.sub(r'[^\w\.\-]', '_', filename)
    
    return filename


def validate_positive_number(value, field_name="valor"):
    """Validate that a number is positive"""
    try:
        value = float(value)
        if value <= 0:
            raise ValidationError(f"{field_name} debe ser mayor que 0")
        return value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} debe ser un número válido")


def validate_integer_range(value, min_val, max_val, field_name="valor"):
    """Validate that an integer is within a specific range"""
    try:
        value = int(value)
        if value < min_val or value > max_val:
            raise ValidationError(f"{field_name} debe estar entre {min_val} y {max_val}")
        return value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} debe ser un número entero válido")


def sanitize_text_input(text, max_length=None):
    """General text input sanitization"""
    if not text:
        return text
    
    # Convert to string and strip whitespace
    text = str(text).strip()
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_url(url):
    """Validate URL format"""
    if not url:
        return url
    
    url_regex = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(url_regex, url):
        raise ValidationError("URL inválida")
    
    # Prevent javascript: and data: URLs
    if url.lower().startswith(('javascript:', 'data:', 'vbscript:')):
        raise ValidationError("URL no permitida")
    
    return url


def rate_limit_key(request, suffix=''):
    """Generate rate limit key based on user or IP"""
    if request.user.is_authenticated:
        return f"rl_{request.user.id}_{suffix}"
    else:
        return f"rl_{request.META.get('REMOTE_ADDR', 'unknown')}_{suffix}"
