# Script de configuración de IIS para Django en producción
# Debe ejecutarse como Administrador

Write-Host "=== Configuración de IIS para Sistema de Rifas ===" -ForegroundColor Green

# 1. Instalar IIS y características necesarias
Write-Host "`n[1/7] Instalando IIS y CGI..." -ForegroundColor Yellow
Install-WindowsFeature -name Web-Server -IncludeManagementTools
Install-WindowsFeature -name Web-CGI

# 2. Habilitar wfastcgi
Write-Host "`n[2/7] Habilitando wfastcgi..." -ForegroundColor Yellow
C:\Users\Administrator\AppData\Local\Programs\Python\Python314\Scripts\wfastcgi-enable.exe

# 3. Crear Application Pool
Write-Host "`n[3/7] Creando Application Pool..." -ForegroundColor Yellow
Import-Module WebAdministration
$appPoolName = "RifasAppPool"
if (Test-Path IIS:\AppPools\$appPoolName) {
    Remove-WebAppPool -Name $appPoolName
}
New-WebAppPool -Name $appPoolName
Set-ItemProperty IIS:\AppPools\$appPoolName -name "managedRuntimeVersion" -value ""

# 4. Crear sitio web
Write-Host "`n[4/7] Creando sitio web en IIS..." -ForegroundColor Yellow
$siteName = "SistemaRifas"
$sitePath = "C:\Users\Administrator\Desktop\RS_project"
$port = 80

if (Test-Path IIS:\Sites\$siteName) {
    Remove-Website -Name $siteName
}

New-Website -Name $siteName -Port $port -PhysicalPath $sitePath -ApplicationPool $appPoolName

# 5. Configurar permisos
Write-Host "`n[5/7] Configurando permisos..." -ForegroundColor Yellow
$acl = Get-Acl $sitePath
$permission = "IIS_IUSRS","FullControl","ContainerInherit,ObjectInherit","None","Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl $sitePath $acl

# Permisos especiales para media y logs
$mediaPath = "$sitePath\media"
$logsPath = "$sitePath\logs"
if (Test-Path $mediaPath) {
    icacls $mediaPath /grant "IIS_IUSRS:(OI)(CI)F" /T
}
if (Test-Path $logsPath) {
    icacls $logsPath /grant "IIS_IUSRS:(OI)(CI)F" /T
}

# 6. Configurar Firewall
Write-Host "`n[6/7] Configurando Firewall..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow -ErrorAction SilentlyContinue

# 7. Reiniciar IIS
Write-Host "`n[7/7] Reiniciando IIS..." -ForegroundColor Yellow
iisreset

Write-Host "`n=== Configuración completada! ===" -ForegroundColor Green
Write-Host "`nEl sitio está disponible en:" -ForegroundColor Cyan
Write-Host "  - http://localhost" -ForegroundColor White
Write-Host "  - http://$(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Ethernet*' | Select-Object -First 1 -ExpandProperty IPAddress)" -ForegroundColor White
Write-Host "`nIMPORTANTE:" -ForegroundColor Red
Write-Host "  1. Actualiza ALLOWED_HOSTS en .env con tu IP pública o dominio" -ForegroundColor Yellow
Write-Host "  2. Configura SSL/HTTPS para producción" -ForegroundColor Yellow
Write-Host "  3. Revisa los permisos de archivos si hay errores" -ForegroundColor Yellow
