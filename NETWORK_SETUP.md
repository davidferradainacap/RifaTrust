# Guía para Configurar Red en VirtualBox/VMware

## OPCIÓN 1: Port Forwarding (NAT) - Recomendado para pruebas

### VirtualBox:
1. Apaga la VM
2. Ve a Configuración → Red → Avanzadas → Reenvío de puertos
3. Agrega estas reglas:
   - Nombre: HTTP, Protocolo: TCP, IP Anfitrión: 127.0.0.1, Puerto Anfitrión: 8080, IP Invitado: 10.0.2.15, Puerto Invitado: 80
   - Nombre: HTTPS, Protocolo: TCP, IP Anfitrión: 127.0.0.1, Puerto Anfitrión: 8443, IP Invitado: 10.0.2.15, Puerto Invitado: 443
4. Inicia la VM
5. Accede desde: http://localhost:8080

### VMware:
1. Ve a Configuración de VM → Network Adapter → NAT Settings
2. Agrega Port Forwarding similar

---

## OPCIÓN 2: Modo Bridge - Para acceso desde cualquier PC en la red

### VirtualBox:
1. Apaga la VM
2. Ve a Configuración → Red
3. Cambiar "Conectado a:" de NAT a "Adaptador puente"
4. Selecciona tu adaptador de red físico
5. Inicia la VM

### VMware:
1. Ve a Configuración de VM → Network Adapter
2. Cambia a "Bridged" mode
3. Selecciona tu adaptador de red físico

### Después de cambiar a Bridge:
La VM obtendrá una IP de tu router (ej: 192.168.1.x)

Ejecuta en PowerShell para ver la nueva IP:
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}
```

Actualiza ALLOWED_HOSTS con la nueva IP en .env

---

## OPCIÓN 3: Solo acceso local desde el servidor
Si solo necesitas acceder desde la propia VM:
- Ya está funcionando en: http://localhost
- Usa el navegador dentro de la VM

---

## Para Producción Real:
- Usa un servidor físico o VPS con IP pública
- Configura DNS apuntando a la IP pública
- Instala certificado SSL válido (Let's Encrypt)

## Verificar estado actual:
```powershell
# Ver IP actual
ipconfig

# Ver si IIS está escuchando
Get-NetTCPConnection -LocalPort 80,443 -State Listen

# Probar acceso local
Invoke-WebRequest http://localhost -UseBasicParsing
```
