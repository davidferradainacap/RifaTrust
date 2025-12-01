# Script para instalar certificado SSL en IIS
# Ejecutar como Administrador

Write-Host "=== Configuración SSL para RifaTrust.com ===" -ForegroundColor Green

# Opción 1: Crear certificado autofirmado (SOLO PARA PRUEBAS)
Write-Host "`n[Opción 1] Crear certificado autofirmado temporal..." -ForegroundColor Yellow
$cert = New-SelfSignedCertificate -DnsName "RifaTrust.com", "www.RifaTrust.com" -CertStoreLocation "cert:\LocalMachine\My"
Write-Host "Certificado creado con Thumbprint: $($cert.Thumbprint)" -ForegroundColor Green

# Agregar binding HTTPS
Write-Host "`nConfigurando binding HTTPS en IIS..." -ForegroundColor Yellow
New-WebBinding -Name "SistemaRifas" -Protocol "https" -Port 443 -HostHeader "RifaTrust.com" -SslFlags 1
New-WebBinding -Name "SistemaRifas" -Protocol "https" -Port 443 -HostHeader "www.RifaTrust.com" -SslFlags 1

# Asignar certificado al binding
$binding = Get-WebBinding -Name "SistemaRifas" -Protocol "https" -Port 443
$binding.AddSslCertificate($cert.Thumbprint, "my")

Write-Host "`n=== SSL Configurado ===" -ForegroundColor Green
Write-Host "El sitio ahora está disponible en:" -ForegroundColor Cyan
Write-Host "  - https://RifaTrust.com" -ForegroundColor White
Write-Host "  - https://www.RifaTrust.com" -ForegroundColor White

Write-Host "`nIMPORTANTE PARA PRODUCCION:" -ForegroundColor Red
Write-Host "Este certificado es AUTOFIRMADO y solo sirve para pruebas." -ForegroundColor Yellow
Write-Host "Para produccion, necesitas un certificado valido de:" -ForegroundColor Yellow
Write-Host "  1. Let's Encrypt (gratis) - usa win-acme" -ForegroundColor White
Write-Host "  2. Comprar certificado SSL comercial" -ForegroundColor White
Write-Host "`nPara Let's Encrypt:" -ForegroundColor Cyan
Write-Host "  Descargar win-acme desde: https://github.com/win-acme/win-acme/releases" -ForegroundColor White
