# 🚀 GUÍA DE DESPLIEGUE - RIFATRUST
# Sistema de Rifas Online con Seguridad Empresarial

---

## 📋 ÍNDICE

1. [Estándares de Codificación Segura](#estándares-de-codificación-segura)
2. [Despliegue con Docker](#despliegue-con-docker)
3. [Despliegue en Windows Server Datacenter](#despliegue-windows-server)
4. [Simulación de Despliegue en Azure](#despliegue-azure)

---

## 🔒 ESTÁNDARES DE CODIFICACIÓN SEGURA

### ✅ Implementaciones de Seguridad

#### 1. **Validación de Entradas**
- ✅ **Implementado**: Validación completa en formularios Django
- **Ubicación**: `apps/users/forms.py`, `apps/raffles/forms.py`
- **Herramientas**: Django Forms con métodos `clean()` personalizados
- **Funciones adicionales**: `apps/core/validators.py`

```python
# Ejemplos de validación implementada:
- Validación de email (formato y unicidad)
- Validación de edad (mayor de 18 años)
- Validación de números positivos
- Validación de rangos de valores
- Validación de RUT chileno
- Validación de formato de teléfono
```

#### 2. **Sanitización de Datos**
- ✅ **Implementado**: Utilidades de sanitización personalizadas
- **Ubicación**: `apps/core/validators.py`
- **Funciones**:
  - `sanitize_html()`: Escapa caracteres HTML especiales
  - `sanitize_sql_input()`: Previene inyección SQL
  - `sanitize_filename()`: Previene directory traversal
  - `sanitize_text_input()`: Limpieza general de texto

```python
from apps.core.validators import sanitize_html, sanitize_filename

# Uso en vistas
nombre = sanitize_html(request.POST.get('nombre'))
archivo = sanitize_filename(uploaded_file.name)
```

#### 3. **Hash de Contraseñas**
- ✅ **Implementado**: Argon2 (más seguro que bcrypt)
- **Configuración**: `config/settings.py` líneas 107-122
- **Algoritmo**: Argon2id (ganador Password Hashing Competition)

```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Primario
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',  # Fallback
]
```

**¿Por qué Argon2 y no bcrypt?**
- Resistente a ataques GPU/ASIC
- Memoria ajustable (más seguro contra fuerza bruta)
- Estándar recomendado por OWASP 2024
- Mayor seguridad que bcrypt para aplicaciones modernas

#### 4. **Uso de HTTPS**
- ✅ **Implementado**: Configuración completa para producción
- **Ubicación**: `config/settings.py` líneas 186-203
- **Características**:
  - Redirección automática HTTP → HTTPS
  - HSTS (HTTP Strict Transport Security) con 1 año
  - Cookies seguras (Secure, HTTPOnly, SameSite)
  - Protección XSS y Clickjacking

```python
# Configuración de producción (DEBUG=False)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
```

#### 5. **Manejo Seguro de Errores**
- ✅ **Implementado**: Páginas de error personalizadas sin filtración de datos
- **Ubicación**: 
  - Templates: `templates/400.html`, `403.html`, `404.html`, `500.html`
  - Handlers: `config/error_handlers.py`
  - Logging: `config/settings.py` (configuración LOGGING)

**Características**:
- No expone información sensible del sistema
- Logging separado para errores de seguridad
- Rotación automática de logs (15MB máximo)
- Alertas por email para errores críticos

```python
# Logs separados por tipo
- django.log: Errores generales
- security.log: Eventos de seguridad
```

#### 6. **Encriptación de Datos Sensibles**
- ✅ **Implementado**: Fernet (AES-128 + HMAC-SHA256)
- **Ubicación**: `apps/core/encryption.py`
- **Campos encriptados**:
  - Teléfonos de usuarios
  - Direcciones y datos personales
  - IDs de transacciones de pago
  - Payment intents de Stripe

#### 7. **Protección CSRF y XSS**
- ✅ **Implementado**: Django CSRF middleware + headers de seguridad
- Tokens CSRF en todos los formularios
- Content Security Policy en producción
- Escape automático de HTML en templates

---

## 🐳 DESPLIEGUE CON DOCKER

### Requisitos Previos
- Docker Desktop (Windows) o Docker Engine (Linux)
- Docker Compose v2.0+
- 4GB RAM mínimo
- 10GB espacio en disco

### Paso 1: Preparar Variables de Entorno

```powershell
# Copiar archivo de ejemplo
Copy-Item docker.env.example -Destination .env

# Editar .env con tus valores
notepad .env
```

**Variables críticas a configurar**:
```env
SECRET_KEY=tu-clave-secreta-de-50-caracteres-random-generada
MYSQL_ROOT_PASSWORD=password-root-mysql-seguro
MYSQL_PASSWORD=password-usuario-mysql-seguro
ENCRYPTION_KEY=clave-diferente-a-secret-key-para-encriptar
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com
```

### Paso 2: Construir y Ejecutar Contenedores

```powershell
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f web
```

### Paso 3: Inicializar Base de Datos

```powershell
# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Verificar encriptación
docker-compose exec web python manage.py check_encrypted_fields
```

### Paso 4: Acceder a la Aplicación

```
Web Application: http://localhost:8000
MySQL Database: localhost:3306
Admin Panel: http://localhost:8000/django-admin
```

### Comandos Útiles Docker

```powershell
# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener y eliminar todo (incluyendo volúmenes)
docker-compose down -v

# Ejecutar comando en contenedor
docker-compose exec web python manage.py <comando>

# Acceder a shell de Django
docker-compose exec web python manage.py shell

# Backup de base de datos
docker-compose exec db mysqldump -u root -p RifaTrust > backup.sql
```

### Estructura de Servicios Docker

```yaml
Servicios:
├── db (MySQL 8.0)
│   ├── Puerto: 3306
│   ├── Volumen: mysql_data
│   └── Healthcheck: mysqladmin ping
│
├── web (Django + Gunicorn)
│   ├── Puerto: 8000
│   ├── Workers: 4
│   ├── Timeout: 120s
│   └── Depends: db
│
└── nginx (Reverse Proxy)
    ├── Puerto: 80, 443
    ├── Gzip: Activado
    └── SSL: Configuración lista
```

---

## 🖥️ DESPLIEGUE EN WINDOWS SERVER DATACENTER

### Requisitos del Servidor
- Windows Server 2019/2022 Datacenter
- 4 CPU cores mínimo
- 8GB RAM mínimo
- 50GB disco SSD
- IIS 10.0+
- Python 3.11
- MySQL 8.0

### Opción 1: Despliegue Nativo (Sin Docker)

#### Paso 1: Instalar Dependencias

```powershell
# Instalar Python 3.11
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe" -OutFile "python-installer.exe"
Start-Process -Wait -FilePath "python-installer.exe" -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1"

# Instalar MySQL 8.0
Invoke-WebRequest -Uri "https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.35.0.msi" -OutFile "mysql-installer.msi"
Start-Process -Wait -FilePath "msiexec.exe" -ArgumentList "/i", "mysql-installer.msi", "/quiet"

# Instalar Git
winget install Git.Git
```

#### Paso 2: Configurar Proyecto

```powershell
# Clonar o copiar proyecto
cd C:\inetpub\wwwroot
git clone <tu-repositorio> rifatrust
cd rifatrust

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
pip install mysqlclient waitress
```

#### Paso 3: Configurar MySQL

```powershell
# Conectar a MySQL
mysql -u root -p

# Ejecutar comandos SQL
CREATE DATABASE RifaTrust CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rifatrust_user'@'localhost' IDENTIFIED BY 'password_seguro_aqui';
GRANT ALL PRIVILEGES ON RifaTrust.* TO 'rifatrust_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### Paso 4: Configurar Variables de Entorno

```powershell
# Crear archivo .env
@"
DEBUG=False
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=RifaTrust
DATABASE_USER=rifatrust_user
DATABASE_PASSWORD=password_seguro_aqui
DATABASE_HOST=localhost
DATABASE_PORT=3306
ALLOWED_HOSTS=localhost,servidor.dominio.com
"@ | Out-File -FilePath .env -Encoding UTF8
```

#### Paso 5: Inicializar Aplicación

```powershell
# Migrar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Verificar encriptación
python manage.py check_encrypted_fields
```

#### Paso 6: Configurar Servicio Windows

Crear archivo `rifatrust-service.py`:

```python
import waitress
import os
from config.wsgi import application

if __name__ == '__main__':
    os.chdir('C:\\inetpub\\wwwroot\\rifatrust')
    waitress.serve(application, host='0.0.0.0', port=8000, threads=4)
```

Crear servicio con NSSM:

```powershell
# Descargar NSSM
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "nssm.zip"
Expand-Archive -Path nssm.zip -DestinationPath C:\nssm
$env:Path += ";C:\nssm\nssm-2.24\win64"

# Instalar servicio
nssm install RifaTrust "C:\inetpub\wwwroot\rifatrust\venv\Scripts\python.exe"
nssm set RifaTrust AppParameters "C:\inetpub\wwwroot\rifatrust\rifatrust-service.py"
nssm set RifaTrust AppDirectory "C:\inetpub\wwwroot\rifatrust"
nssm set RifaTrust DisplayName "RifaTrust Web Application"
nssm set RifaTrust Description "Sistema de Rifas Online"
nssm set RifaTrust Start SERVICE_AUTO_START

# Iniciar servicio
nssm start RifaTrust
```

#### Paso 7: Configurar IIS como Reverse Proxy

```powershell
# Instalar Application Request Routing y URL Rewrite
Install-WindowsFeature -Name Web-Application-Proxy
Import-Module WebAdministration

# Configurar reverse proxy
$rule = @{
    Name = "RifaTrust Reverse Proxy"
    PatternSyntax = "Wildcard"
    StopProcessing = $true
}

# Agregar regla de reescritura
Add-WebConfigurationProperty -Filter "system.webServer/rewrite/rules" -PSPath "IIS:\Sites\Default Web Site" -Name "." -Value $rule
```

Archivo `web.config` en `C:\inetpub\wwwroot`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="RifaTrust" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://localhost:8000/{R:1}" />
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>
```

### Opción 2: Despliegue con Docker en Windows Server

```powershell
# Instalar Docker Desktop para Windows Server
Invoke-WebRequest -Uri "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" -OutFile "DockerInstaller.exe"
Start-Process -Wait -FilePath "DockerInstaller.exe" -ArgumentList "install", "--quiet"

# Reiniciar servidor
Restart-Computer -Force

# Después del reinicio, seguir pasos de Docker Compose anteriores
cd C:\rifatrust
docker-compose up -d
```

---

## ☁️ SIMULACIÓN DE DESPLIEGUE EN AZURE

### Arquitectura Azure Recomendada

```
Azure Resource Group: rifatrust-rg
├── App Service Plan (B2: 2 cores, 3.5GB RAM)
├── Web App (Python 3.11)
├── Azure Database for MySQL (Flexible Server)
├── Azure Storage Account (archivos media)
├── Application Insights (monitoreo)
├── Key Vault (secrets management)
└── Azure CDN (archivos estáticos)
```

### Opción 1: Despliegue con Azure Web App

#### Paso 1: Crear Recursos Azure (Portal o CLI)

```bash
# Instalar Azure CLI
winget install Microsoft.AzureCLI

# Login
az login

# Crear grupo de recursos
az group create --name rifatrust-rg --location eastus

# Crear App Service Plan
az appservice plan create \
  --name rifatrust-plan \
  --resource-group rifatrust-rg \
  --sku B2 \
  --is-linux

# Crear Web App
az webapp create \
  --name rifatrust-webapp \
  --resource-group rifatrust-rg \
  --plan rifatrust-plan \
  --runtime "PYTHON:3.11"

# Crear MySQL Database
az mysql flexible-server create \
  --name rifatrust-mysql \
  --resource-group rifatrust-rg \
  --location eastus \
  --admin-user rifaadmin \
  --admin-password "Password123!" \
  --sku-name Standard_B2s \
  --tier Burstable \
  --storage-size 32 \
  --version 8.0

# Crear base de datos
az mysql flexible-server db create \
  --resource-group rifatrust-rg \
  --server-name rifatrust-mysql \
  --database-name RifaTrust
```

#### Paso 2: Configurar Variables de Entorno en Azure

```bash
# Configurar settings de la Web App
az webapp config appsettings set \
  --name rifatrust-webapp \
  --resource-group rifatrust-rg \
  --settings \
    DEBUG=False \
    SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" \
    DATABASE_ENGINE=django.db.backends.mysql \
    DATABASE_NAME=RifaTrust \
    DATABASE_USER=rifaadmin \
    DATABASE_PASSWORD=Password123! \
    DATABASE_HOST=rifatrust-mysql.mysql.database.azure.com \
    DATABASE_PORT=3306 \
    ALLOWED_HOSTS=rifatrust-webapp.azurewebsites.net \
    WEBSITES_PORT=8000
```

#### Paso 3: Configurar Despliegue desde Git

```bash
# Configurar Git deployment
az webapp deployment source config \
  --name rifatrust-webapp \
  --resource-group rifatrust-rg \
  --repo-url https://github.com/tu-usuario/rifatrust.git \
  --branch main \
  --manual-integration

# O usar despliegue local
cd C:\rifatrust
az webapp up \
  --name rifatrust-webapp \
  --resource-group rifatrust-rg \
  --runtime PYTHON:3.11
```

#### Paso 4: Configurar Startup Command

En Azure Portal → Web App → Configuration → General Settings:

```bash
Startup Command: gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=120 config.wsgi:application
```

#### Paso 5: Configurar SSL/HTTPS

```bash
# Habilitar HTTPS only
az webapp update \
  --name rifatrust-webapp \
  --resource-group rifatrust-rg \
  --https-only true

# Agregar dominio personalizado (opcional)
az webapp config hostname add \
  --webapp-name rifatrust-webapp \
  --resource-group rifatrust-rg \
  --hostname www.tudominio.com

# Crear certificado SSL managed
az webapp config ssl create \
  --name rifatrust-webapp \
  --resource-group rifatrust-rg \
  --hostname www.tudominio.com
```

### Opción 2: Despliegue con Azure Container Instances (Docker)

```bash
# Crear Azure Container Registry
az acr create \
  --name rifatrustacr \
  --resource-group rifatrust-rg \
  --sku Basic \
  --admin-enabled true

# Build y push imagen Docker
az acr build \
  --registry rifatrustacr \
  --image rifatrust:latest \
  --file Dockerfile .

# Crear Container Instance
az container create \
  --name rifatrust-container \
  --resource-group rifatrust-rg \
  --image rifatrustacr.azurecr.io/rifatrust:latest \
  --cpu 2 \
  --memory 4 \
  --registry-login-server rifatrustacr.azurecr.io \
  --registry-username rifatrustacr \
  --registry-password $(az acr credential show --name rifatrustacr --query "passwords[0].value" -o tsv) \
  --dns-name-label rifatrust \
  --ports 80 8000 \
  --environment-variables \
    DEBUG=False \
    DATABASE_HOST=rifatrust-mysql.mysql.database.azure.com
```

### Opción 3: Despliegue con Azure Kubernetes Service (AKS)

```bash
# Crear AKS cluster
az aks create \
  --name rifatrust-aks \
  --resource-group rifatrust-rg \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --generate-ssh-keys \
  --attach-acr rifatrustacr

# Conectar a cluster
az aks get-credentials \
  --name rifatrust-aks \
  --resource-group rifatrust-rg

# Aplicar configuración Kubernetes
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml
```

### Monitoreo y Logging en Azure

```bash
# Habilitar Application Insights
az monitor app-insights component create \
  --app rifatrust-insights \
  --resource-group rifatrust-rg \
  --location eastus \
  --application-type web

# Vincular con Web App
az webapp config appsettings set \
  --name rifatrust-webapp \
  --resource-group rifatrust-rg \
  --settings \
    APPINSIGHTS_INSTRUMENTATIONKEY=$(az monitor app-insights component show --app rifatrust-insights -g rifatrust-rg --query instrumentationKey -o tsv)

# Ver logs en tiempo real
az webapp log tail \
  --name rifatrust-webapp \
  --resource-group rifatrust-rg
```

---

## 🔧 TROUBLESHOOTING

### Problemas Comunes Docker

**Error: Port 3306 already in use**
```powershell
# Detener MySQL local
Stop-Service MySQL80
# O cambiar puerto en docker-compose.yml
ports:
  - "3307:3306"
```

**Error: Cannot connect to MySQL**
```powershell
# Verificar que MySQL esté healthy
docker-compose exec db mysqladmin ping -p

# Ver logs de MySQL
docker-compose logs db
```

### Problemas Comunes Windows Server

**Error: mysqlclient installation failed**
```powershell
# Instalar Visual C++ Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools
# Seleccionar "Desktop development with C++"
```

**Error: Permission denied**
```powershell
# Ejecutar PowerShell como Administrador
# Agregar permisos a carpeta
icacls C:\inetpub\wwwroot\rifatrust /grant "IIS AppPool\DefaultAppPool:(OI)(CI)F" /T
```

### Problemas Comunes Azure

**Error: Deployment failed**
```bash
# Ver logs detallados
az webapp log tail --name rifatrust-webapp -g rifatrust-rg

# SSH a container
az webapp ssh --name rifatrust-webapp -g rifatrust-rg
```

**Error: Database connection refused**
```bash
# Verificar firewall rules
az mysql flexible-server firewall-rule create \
  --resource-group rifatrust-rg \
  --name rifatrust-mysql \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

---

## 📊 VERIFICACIÓN POST-DESPLIEGUE

### Checklist de Seguridad

```powershell
# 1. Verificar HTTPS
curl -I https://tu-dominio.com | Select-String "Strict-Transport-Security"

# 2. Verificar encriptación
python manage.py check_encrypted_fields

# 3. Verificar headers de seguridad
curl -I https://tu-dominio.com | Select-String "X-Frame-Options|X-Content-Type-Options"

# 4. Test de carga
# Instalar Apache Bench
choco install apache-httpd
ab -n 1000 -c 10 https://tu-dominio.com/

# 5. Backup de base de datos
docker-compose exec db mysqldump -u root -p RifaTrust > backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
```

---

## 📞 SOPORTE

Para problemas técnicos:
- Email: soporte@rifatrust.com
- Documentación: https://docs.rifatrust.com
- GitHub Issues: https://github.com/tu-repo/issues

---

**Fecha de última actualización**: Noviembre 2024
**Versión del documento**: 1.0
**Autor**: Equipo de Desarrollo RifaTrust
