# 🔐 Guía Rápida: Migración a MySQL con Encriptación

## ⚡ Inicio Rápido (5 minutos)

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

**Nuevas dependencias instaladas:**
- `cryptography==41.0.7` - Encriptación de datos
- `argon2-cffi==23.1.0` - Hashing seguro de contraseñas
- `mysqlclient==2.2.0` - Conector MySQL

### 2. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# OBLIGATORIO
SECRET_KEY=django-insecure-CAMBIAR-ESTO-POR-ALGO-MUY-LARGO-Y-ALEATORIO

# Para MySQL (comentar si usas SQLite de momento)
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=rifas_db
DATABASE_USER=rifas_user
DATABASE_PASSWORD=tu_contraseña_segura
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Stripe (si tienes las claves)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### 3. Crear Base de Datos MySQL

```sql
CREATE DATABASE rifas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rifas_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON rifas_db.* TO 'rifas_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Aplicar Migraciones

```bash
# Crear migraciones para los nuevos campos encriptados
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Verificar que todo funciona
python manage.py check_encrypted_fields
```

### 5. Listo! 🎉

El servidor ya está configurado con:
- ✅ Contraseñas hasheadas con Argon2
- ✅ Datos personales encriptados
- ✅ Datos financieros encriptados
- ✅ Base de datos MySQL lista

## 📊 ¿Qué Datos se Encriptan?

### Información Personal
- 📱 Teléfonos
- 🏠 Direcciones
- 🌆 Ciudades
- 📮 Códigos postales

### Información Financiera
- 💳 IDs de transacciones
- 💰 IDs de pagos Stripe

### Contraseñas
- 🔒 Hasheadas con Argon2 (NO encriptadas, irreversibles)

## 🔧 Comandos Útiles

```bash
# Verificar integridad de campos encriptados
python manage.py check_encrypted_fields

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

## ⚠️ IMPORTANTE - Seguridad

### Antes de subir a producción:

1. ✅ Cambiar `SECRET_KEY` por una clave única y aleatoria
2. ✅ Establecer `DEBUG=False`
3. ✅ Configurar `ALLOWED_HOSTS` correctamente
4. ✅ Usar HTTPS en producción
5. ✅ Hacer backups regulares de la base de datos
6. ✅ NO subir el archivo `.env` al repositorio

### Generar clave segura:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 🐛 Solución de Problemas

### Error: "No module named 'cryptography'"
```bash
pip install cryptography==41.0.7
```

### Error: "No module named 'argon2'"
```bash
pip install argon2-cffi==23.1.0
```

### Error: "Access denied for user"
Verificar credenciales MySQL en `.env`

### Error al desencriptar datos
1. Verificar que `SECRET_KEY` no ha cambiado
2. Ejecutar: `python manage.py check_encrypted_fields`

## 📚 Documentación Completa

Ver `SECURITY_ENCRYPTION.md` para:
- Detalles técnicos de encriptación
- Rotación de claves
- Cumplimiento legal (GDPR, PCI DSS)
- Mejores prácticas

## 🚀 Próximos Pasos

Después de la migración:
1. Probar login/registro de usuarios
2. Verificar que los pagos funcionan
3. Comprobar que los datos se guardan correctamente
4. Hacer backup de la base de datos

## 💬 Soporte

Si encuentras problemas:
1. Verificar logs: `python manage.py runserver`
2. Revisar `.env` está configurado correctamente
3. Ejecutar: `python manage.py check_encrypted_fields`
