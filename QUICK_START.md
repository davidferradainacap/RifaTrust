# 🚀 INICIO RÁPIDO - RIFATRUST

## Opción 1: Desarrollo Local (SQLite)

```powershell
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear logs directory
mkdir logs

# 3. Migrar base de datos
python manage.py migrate

# 4. Crear superusuario
python manage.py createsuperuser

# 5. Ejecutar servidor
python manage.py runserver

# Acceder: http://localhost:8000
```

---

## Opción 2: Docker Compose (MySQL)

```powershell
# 1. Copiar variables de entorno
Copy-Item docker.env.example -Destination .env

# 2. Editar .env con tus valores
notepad .env

# 3. Construir e iniciar
docker-compose up -d

# 4. Migrar base de datos
docker-compose exec web python manage.py migrate

# 5. Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Acceder: http://localhost:8000
```

---

## Opción 3: Despliegue Producción

Ver documentación completa: **DEPLOYMENT_GUIDE.md**

---

## 🔒 Verificación de Seguridad

```powershell
# Verificar encriptación
python manage.py check_encrypted_fields

# Verificar configuración de seguridad
python manage.py check --deploy

# Ver logs de seguridad
Get-Content logs\security.log -Tail 20
```

---

## 📚 Documentación Completa

- **SECURITY_COMPLIANCE.md** - Cumplimiento de estándares de seguridad
- **DEPLOYMENT_GUIDE.md** - Guía completa de despliegue
- **SECURITY_ENCRYPTION.md** - Sistema de encriptación
- **QUICK_START_MYSQL.md** - Migración a MySQL

---

## 🆘 Problemas Comunes

**Error: Port 8000 already in use**
```powershell
# Encontrar proceso
netstat -ano | findstr :8000
# Matar proceso
taskkill /PID <PID> /F
```

**Error: mysqlclient not found**
```powershell
pip install mysqlclient
# Si falla, instalar Visual C++ Build Tools
```

**Error: logs directory not found**
```powershell
mkdir logs
```

---

Para más ayuda, consulta la documentación completa en `DEPLOYMENT_GUIDE.md`
