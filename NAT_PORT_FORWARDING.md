# Configuración NAT/Port Forwarding para RifaTrust

## Situación Actual
- **VM IP Interna:** 10.0.2.15
- **Gateway:** 10.0.2.2
- **IP Pública:** 186.189.100.240
- **Problema:** VM detrás de NAT - necesita port forwarding

## Solución Según Plataforma de Virtualización

### Si usas VMware ESXi / vSphere:
1. Accede a vSphere Client o ESXi Web UI
2. Ve a **Networking** → **Port groups**
3. Configura **promiscuous mode** si es necesario
4. Opción recomendada: Usar **bridged networking** en lugar de NAT

### Si usas Hyper-V (más común en Windows Server):
1. Abre **Hyper-V Manager**
2. Click derecho en tu VM → **Settings**
3. Ve a **Network Adapter**
4. Cambia de "Internal Network" a **"External Network"**
5. Selecciona el adaptador físico que tiene la IP pública
6. Aplica cambios
7. **Reinicia la VM**

Después del cambio, la VM tendrá directamente la IP 186.189.100.240

### Si usas un Router Físico del Datacenter:
Necesitas configurar **Port Forwarding** en el router:

**Reglas de Port Forwarding:**
```
External Port 80 → 10.0.2.15:80 (TCP)
External Port 443 → 10.0.2.15:443 (TCP)
```

**Acceso al router:**
- IP: 10.0.2.2
- Usuario/Password: (credenciales del datacenter)
- Busca sección: "Port Forwarding", "Virtual Servers", o "NAT"

### Si usas Proxmox:
1. SSH al host Proxmox
2. Edita: `/etc/network/interfaces`
3. Configura bridge directo en lugar de NAT
4. O usa iptables para port forwarding:
```bash
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.2.15:80
iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 10.0.2.15:443
```

## Opción FÁCIL (Recomendada): Cambiar a Bridge Network

Si tienes acceso al hipervisor:

1. **Apaga la VM** (desde Hyper-V/VMware)
2. **Cambia el adaptador de red a "Bridged"**
3. **Inicia la VM**
4. **Reconfigura la IP estática en la VM:**

```powershell
# En la VM, ejecuta:
$adapter = Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1

# Asignar IP pública directamente
New-NetIPAddress -InterfaceIndex $adapter.ifIndex -IPAddress "186.189.100.240" -PrefixLength 24 -DefaultGateway "186.189.100.1"

# Configurar DNS
Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses ("8.8.8.8","8.8.4.4")
```

*Nota: Ajusta el gateway (186.189.100.1) según la configuración de tu red*

## Verificar Después de Configurar

```powershell
# Desde la VM
ipconfig /all

# Probar conectividad externa
Test-NetConnection -ComputerName google.com -Port 80

# Probar que el puerto 80 está escuchando
netstat -an | findstr ":80"
```

## Alternativa: Cloudflare Tunnel (Sin Port Forwarding)

Si NO puedes configurar port forwarding, usa **Cloudflare Tunnel**:

1. Instala cloudflared en la VM
2. Crea un tunnel que conecta tu VM a Cloudflare
3. El sitio será accesible sin abrir puertos

```powershell
# Descargar cloudflared
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "C:\cloudflared.exe"

# Autenticar
C:\cloudflared.exe tunnel login

# Crear tunnel
C:\cloudflared.exe tunnel create rifatrust

# Configurar
C:\cloudflared.exe tunnel route dns rifatrust RifaTrust.com
```

## Siguiente Paso Inmediato

**Decide:**
1. ¿Cambiar a bridge network? (más simple, IP pública directa)
2. ¿Configurar port forwarding en router? (necesitas acceso al router)
3. ¿Usar Cloudflare Tunnel? (no necesita abrir puertos)

**¿Qué plataforma de virtualización usas?**
- [ ] Hyper-V
- [ ] VMware
- [ ] Proxmox
- [ ] VirtualBox
- [ ] Otro:___________
