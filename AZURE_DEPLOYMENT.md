# Despliegue en Azure - RifaTrust

## Beneficios de Azure para Estudiantes INACAP

✅ **Azure for Students:** $100 USD en créditos gratis por 12 meses
✅ **Dominio gratis:** rifatrust.azurewebsites.net (sin costo)
✅ **SSL automático:** HTTPS incluido sin configuración
✅ **Base de datos:** Azure Database for MySQL gratis
✅ **Sin tarjeta de crédito:** Solo correo institucional INACAP

## Opción 1: Azure App Service (Recomendado - Más Fácil)

### Paso 1: Activar Azure for Students
1. Ve a: **https://azure.microsoft.com/es-es/free/students/**
2. Click en **"Activar ahora"**
3. Inicia sesión con tu correo INACAP (@inacapmail.cl o @alumnos.inacap.cl)
4. Verifica tu identidad estudiantil
5. Obtendrás $100 USD en créditos

### Paso 2: Crear App Service
1. En Azure Portal: **https://portal.azure.com**
2. Click **"Create a resource"** → **"Web App"**
3. Configuración:
   ```
   Subscription: Azure for Students
   Resource Group: Crear nuevo → "RifaTrust-RG"
   Name: rifatrust (será rifatrust.azurewebsites.net)
   Publish: Code
   Runtime stack: Python 3.11
   Operating System: Windows
   Region: Brazil South (más cercano a Chile)
   Pricing Plan: Free F1 (gratis, suficiente para pruebas)
   ```
4. Click **"Review + create"** → **"Create"**
5. Espera 2-3 minutos

### Paso 3: Crear Base de Datos MySQL en Azure
1. En Azure Portal → **"Create a resource"** → **"Azure Database for MySQL"**
2. Selecciona **"Flexible Server"**
3. Configuración:
   ```
   Resource Group: RifaTrust-RG
   Server name: rifatrust-mysql
   Region: Brazil South
   MySQL version: 8.0
   Compute + storage: Burstable, B1ms (1 vCore, 2 GB RAM) - ~$12/mes
   Admin username: rifasadmin
   Password: [Crear contraseña segura]
   ```
4. En **"Networking"**:
   - Allow public access: Yes
   - Add current client IP: Yes (para acceder desde tu VM)
5. Click **"Review + create"** → **"Create"**

### Paso 4: Configurar Variables de Entorno en App Service
1. Ve a tu App Service → **"Configuration"** → **"Application settings"**
2. Agregar estas variables:
   ```
   SECRET_KEY = [tu SECRET_KEY actual del .env]
   DEBUG = False
   DATABASE_NAME = rifas_db
   DATABASE_USER = rifasadmin
   DATABASE_PASSWORD = [password de MySQL Azure]
   DATABASE_HOST = rifatrust-mysql.mysql.database.azure.com
   DATABASE_PORT = 3306
   ALLOWED_HOSTS = rifatrust.azurewebsites.net
   ```
3. Click **"Save"**

### Paso 5: Configurar Deployment (Git Local o GitHub)

#### Opción A: GitHub (Recomendado)
1. Sube tu proyecto a GitHub (si no está ya)
2. En App Service → **"Deployment Center"**
3. Source: **GitHub**
4. Autoriza tu cuenta GitHub
5. Selecciona:
   - Organization: Tu usuario
   - Repository: RS_project (o como lo hayas nombrado)
   - Branch: main
6. Azure creará automáticamente un workflow de GitHub Actions
7. Cada push a GitHub desplegará automáticamente

#### Opción B: Git Local
1. En App Service → **"Deployment Center"** → **"Local Git"**
2. Copia la URL de Git (ejemplo: https://rifatrust.scm.azurewebsites.net/rifatrust.git)
3. En tu VM:
   ```powershell
   cd C:\Users\Administrator\Desktop\RS_project
   git init
   git add .
   git commit -m "Initial commit"
   git remote add azure https://rifatrust.scm.azurewebsites.net/rifatrust.git
   git push azure master
   ```

### Paso 6: Configurar startup.txt para Django
1. Crea archivo `startup.txt` en la raíz del proyecto:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   gunicorn config.wsgi:application --bind=0.0.0.0:8000 --timeout 600
   ```
2. En App Service → **"Configuration"** → **"General settings"**
3. Startup Command: `startup.txt`
4. Click **"Save"**

### Paso 7: Migrar Base de Datos
Opción 1 - Exportar desde MySQL local e importar a Azure:
```powershell
# Exportar desde MySQL local
mysqldump -u rifas_user -p rifas_db > rifas_backup.sql

# Importar a Azure MySQL
mysql -h rifatrust-mysql.mysql.database.azure.com -u rifasadmin -p rifas_db < rifas_backup.sql
```

Opción 2 - Ejecutar migraciones en Azure (limpio):
Azure ejecutará automáticamente `python manage.py migrate` en el startup

### Paso 8: Verificar Funcionamiento
1. Ve a: **https://rifatrust.azurewebsites.net**
2. Debe cargar el sitio con SSL automático
3. Crea superuser (si es necesario):
   ```powershell
   # En Azure Portal → App Service → SSH o Console
   python manage.py createsuperuser
   ```

---

## Opción 2: Azure Virtual Machine (Tu VM Actual)

Si prefieres usar tu VM actual y exponerla públicamente:

### Paso 1: Asignar IP Pública Estática
1. En Azure Portal → Tu VM
2. **"Networking"** → **"Public IP address"**
3. Click en la IP → **"Configuration"**
4. Assignment: **Static**
5. DNS name label: **rifatrust** (será rifatrust.brazilsouth.cloudapp.azure.com)

### Paso 2: Abrir Puertos en NSG (Network Security Group)
1. En tu VM → **"Networking"** → **"Add inbound port rule"**
2. Regla HTTP:
   ```
   Source: Any
   Source port ranges: *
   Destination: Any
   Service: HTTP
   Destination port ranges: 80
   Protocol: TCP
   Action: Allow
   Priority: 100
   Name: Allow-HTTP
   ```
3. Regla HTTPS:
   ```
   Destination port ranges: 443
   Service: HTTPS
   Priority: 110
   Name: Allow-HTTPS
   ```

### Paso 3: Configurar Dominio Personalizado (Opcional)
Si quieres usar rifatrust.com (debes comprarlo):
1. Compra el dominio en un registrador
2. En Azure → **"DNS zones"** → **"Create"**
3. Agrega registros A apuntando a la IP pública de tu VM
4. Cambia nameservers del registrador a los de Azure

---

## Costos Estimados (con Azure for Students)

### App Service (Opción 1)
- **App Service Free F1:** $0/mes (limitado pero funcional)
- **App Service Basic B1:** ~$13/mes (mejor rendimiento)
- **Azure MySQL Flexible Server B1ms:** ~$12/mes
- **Total:** $0-25/mes (gratis con Free tier por proyecto académico)

### VM Existente (Opción 2)
- **IP Pública Estática:** ~$3.65/mes
- **VM ya tienes corriendo:** Sin costo adicional
- **Total:** ~$3.65/mes

---

## Recomendación

Para proyecto académico INACAP: **Opción 1 (App Service)**
- ✅ Más profesional
- ✅ SSL automático
- ✅ Escalable
- ✅ Dominio .azurewebsites.net gratis
- ✅ CI/CD con GitHub Actions
- ✅ Sin configuración de IIS/Windows

Para producción real con control total: **Opción 2 (VM)**
- ✅ Control completo
- ✅ Ya tienes todo configurado
- ✅ Más barato si ya tienes la VM
- ✅ Puedes usar cualquier tecnología

---

## Siguiente Paso

**¿Qué opción prefieres?**

A) **App Service** - Más fácil, despliegue automático, SSL gratis
B) **VM Pública** - Usar tu configuración actual, solo abrir puertos

Dime cuál prefieres y te ayudo a configurarla paso a paso.
