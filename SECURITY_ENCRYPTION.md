# Configuración de Seguridad y Encriptación

## Resumen
Este proyecto implementa encriptación de datos sensibles en la base de datos para cumplir con las mejores prácticas de seguridad y protección de datos personales.

## Datos Encriptados

### Información Personal de Usuarios
- **Teléfono** (`User.telefono`): Encriptado con Fernet
- **Dirección** (`Profile.direccion`): Encriptado con Fernet
- **Ciudad** (`Profile.ciudad`): Encriptado con Fernet
- **Estado** (`Profile.estado`): Encriptado con Fernet
- **Código Postal** (`Profile.codigo_postal`): Encriptado con Fernet

### Información Financiera
- **Transaction ID** (`Payment.transaction_id`): Encriptado con Fernet
- **Payment Intent ID** (`Payment.payment_intent_id`): Encriptado con Fernet

### Contraseñas
- Las contraseñas de usuarios se hashean con **Argon2** (el algoritmo más seguro)
- Django NO guarda contraseñas en texto plano
- Hash irreversible: no se puede recuperar la contraseña original

## Tecnología de Encriptación

### Algoritmo: Fernet (Symmetric Encryption)
- **Algoritmo Base**: AES-128 en modo CBC
- **Autenticación**: HMAC con SHA256
- **Seguridad**: Resistente a ataques de fuerza bruta
- **Reversible**: Los datos se pueden desencriptar con la clave correcta

### Password Hashing: Argon2
- **Tipo**: Argon2id (resistente a ataques GPU y side-channel)
- **Configuración**: Parámetros seguros por defecto
- **Fallback**: PBKDF2, BCrypt como alternativas

## Variables de Entorno Requeridas

```env
# SECRET_KEY - Django secret key (OBLIGATORIO)
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria-aqui

# ENCRYPTION_KEY - Clave para encriptar datos sensibles (OPCIONAL)
# Si no se define, usa SECRET_KEY
ENCRYPTION_KEY=otra-clave-diferente-para-encriptacion

# DATABASE - Configuración MySQL
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=rifas_db
DATABASE_USER=rifas_user
DATABASE_PASSWORD=contraseña-segura-aqui
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

## Migración a MySQL

### Paso 1: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 2: Crear base de datos MySQL
```sql
CREATE DATABASE rifas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rifas_user'@'localhost' IDENTIFIED BY 'contraseña-segura-aqui';
GRANT ALL PRIVILEGES ON rifas_db.* TO 'rifas_user'@'localhost';
FLUSH PRIVILEGES;
```

### Paso 3: Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto con las variables mencionadas arriba.

### Paso 4: Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 5: Re-encriptar datos existentes (si migras desde SQLite)
```bash
python manage.py migrate_encrypted_data
```

## Seguridad de las Claves

### ⚠️ IMPORTANTE - Claves en Producción

1. **NUNCA** uses la clave por defecto en producción
2. **NUNCA** subas las claves al repositorio Git
3. Usa variables de entorno o servicios de gestión de secretos
4. Genera claves únicas con:
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```

### Rotación de Claves

Si necesitas cambiar las claves de encriptación:

1. Desencripta todos los datos con la clave antigua
2. Actualiza la variable `ENCRYPTION_KEY`
3. Re-encripta todos los datos con la nueva clave
4. Script disponible: `python manage.py rotate_encryption_key`

## Compatibilidad con MySQL

### Configuraciones Recomendadas

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rifas_db',
        'USER': 'rifas_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'isolation_level': 'read committed',
        },
        'CONN_MAX_AGE': 600,  # Conexiones persistentes
    }
}
```

### Índices para Campos Encriptados

⚠️ **IMPORTANTE**: Los campos encriptados NO pueden indexarse directamente.

Soluciones:
1. Crear campos hash separados para búsquedas
2. Usar búsqueda en memoria después de desencriptar
3. Para email: mantener versión no encriptada con unique=True

## Verificación de Seguridad

### Checklist de Seguridad

- [x] Contraseñas hasheadas con Argon2
- [x] Datos personales encriptados (teléfono, dirección)
- [x] Datos financieros encriptados (transaction_id, payment_intent_id)
- [x] SESSION_COOKIE_HTTPONLY activado
- [x] CSRF_COOKIE_HTTPONLY activado
- [x] SECURE_SSL_REDIRECT en producción
- [x] SECURE_HSTS configurado para HTTPS
- [x] Validación mínima de contraseñas (8 caracteres)

### Testing de Encriptación

```python
# Test básico de encriptación
from apps.core.encryption import encrypt_data, decrypt_data

original = "dato sensible"
encrypted = encrypt_data(original)
decrypted = decrypt_data(encrypted)

assert original == decrypted
assert original != encrypted
```

## Rendimiento

### Impacto en Performance

- **Encriptación**: ~1-2ms por campo
- **Desencriptación**: ~1-2ms por campo
- **Hash de contraseñas**: ~100-200ms (intencional)

### Optimización

Para queries con muchos registros:
```python
# Usar select_related y prefetch_related
users = User.objects.select_related('profile').all()

# Cargar solo campos necesarios
users = User.objects.only('nombre', 'email').all()
```

## Cumplimiento Legal

Esta implementación ayuda a cumplir con:
- **GDPR** (Reglamento General de Protección de Datos)
- **Ley Federal de Protección de Datos Personales (México)**
- **PCI DSS** (para datos de pagos)

## Soporte y Mantenimiento

Para dudas o problemas:
1. Revisar logs: `python manage.py check_encrypted_fields`
2. Verificar claves: Las claves deben ser consistentes
3. Backup: Siempre hacer backup antes de cambiar claves
