# Guía Paso a Paso: Cloudflare para RifaTrust.com

## Paso 1: Crear Cuenta en Cloudflare
1. Abre Brave y ve a: **https://dash.cloudflare.com/sign-up**
2. Email: **daldeaferrada@gmail.com**
3. Crea una contraseña segura
4. Verifica tu email

## Paso 2: Agregar Sitio
1. Click en **"Add a Site"**
2. Ingresa: **rifatrust.com** (sin www)
3. Selecciona plan: **Free ($0/month)**
4. Click **"Continue"**

## Paso 3: Cloudflare Escaneará DNS
Cloudflare intentará encontrar registros DNS existentes.

**Si encuentra registros:** Elimina cualquiera que apunte a IPs incorrectas

**Agrega/Verifica estos registros:**

### Registro 1: Dominio Principal
```
Type: A
Name: @
IPv4 address: 186.189.100.240
Proxy status: ✅ Proxied (nube naranja)
TTL: Auto
```

### Registro 2: Subdominio WWW
```
Type: A
Name: www
IPv4 address: 186.189.100.240
Proxy status: ✅ Proxied (nube naranja)
TTL: Auto
```

### Registro 3: Subdominio Local (Opcional - Solo para uso interno)
```
Type: A
Name: local
IPv4 address: 10.0.2.15
Proxy status: ❌ DNS only (nube gris)
TTL: Auto
```

Click **"Continue"**

## Paso 4: Cambiar Nameservers

Cloudflare te dará 2 nameservers personalizados, algo como:
```
dana.ns.cloudflare.com
walt.ns.cloudflare.com
```

**IMPORTANTE:** Como TÚ creaste el dominio en Windows Server, NO necesitas cambiar nameservers en ningún proveedor externo. Windows Server actuará como DNS autoritativo.

### Opción A: Usar Solo Cloudflare (Recomendado)
**Delegar el dominio completamente a Cloudflare:**

En Windows Server, ejecuta:
```powershell
# Eliminar zona DNS local (Cloudflare manejará todo)
Remove-DnsServerZone -Name "RifaTrust.com" -Force

# Configurar DNS para usar Cloudflare
$adapter = Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1
Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses ("1.1.1.1","1.0.0.1")
```

Luego ve a tu **Registrador de Dominio** (donde compraste rifatrust.com) y cambia los nameservers a los que Cloudflare te dio.

### Opción B: DNS Híbrido (No Recomendado)
Mantener DNS en Windows Server y solo usar Cloudflare como proxy.
*Esto es más complejo y no recomendado para producción*

## Paso 5: Verificar Nameservers en Cloudflare
1. En Cloudflare, click **"Done, check nameservers"**
2. Cloudflare verificará si los nameservers están configurados
3. Espera 5-30 minutos (puede tardar hasta 24 horas)
4. Recibirás un email cuando esté activo: "Your site is active on Cloudflare"

## Paso 6: Configurar SSL/TLS en Cloudflare

**Mientras NO tengas certificado SSL en el servidor:**
1. Ve a **SSL/TLS** (menú izquierdo)
2. Overview → Selecciona **"Flexible"**

**Cuando instales Let's Encrypt (más adelante):**
1. Ve a **SSL/TLS** → Overview
2. Cambia a **"Full (strict)"**

## Paso 7: Configuraciones Adicionales Recomendadas

### 7.1. Activar HTTP/3 y QUIC
1. **Network** → HTTP/3: **On**
2. **0-RTT Connection Resumption:** **On**

### 7.2. Configurar Page Rules (Opcional)
1. **Rules** → **Page Rules**
2. Crear regla: `http://*rifatrust.com/*`
   - Setting: **Always Use HTTPS**

### 7.3. Activar Rocket Loader (Optimización)
1. **Speed** → **Optimization**
2. **Auto Minify:** Selecciona JavaScript, CSS, HTML
3. **Rocket Loader:** **On**

### 7.4. Configurar Caché
1. **Caching** → **Configuration**
2. **Caching Level:** **Standard**
3. **Browser Cache TTL:** 4 hours

## Paso 8: Verificar Funcionamiento

### Desde Línea de Comandos:
```powershell
# Verificar DNS
nslookup rifatrust.com
nslookup www.rifatrust.com

# Debe resolver a IPs de Cloudflare (no a 186.189.100.240 directamente)
```

### Desde Navegador:
1. Abre Brave
2. Ve a: **http://rifatrust.com**
3. Debe redirigir a: **https://rifatrust.com** (SSL de Cloudflare)
4. El sitio debe cargar

## Troubleshooting

### "Error 521: Web server is down"
- El servidor no es accesible desde Cloudflare
- Verifica que port forwarding esté configurado
- Verifica que IIS esté corriendo

### "Error 522: Connection timed out"
- Firewall bloqueando conexiones de Cloudflare
- Agrega IPs de Cloudflare al firewall permitido

### "Error 523: Origin is unreachable"
- La IP 186.189.100.240 no responde
- Verifica configuración de red

### "Too many redirects"
- Cloudflare en modo "Flexible" + Django forzando HTTPS
- Solución: Desactiva `SECURE_SSL_REDIRECT` en Django temporalmente

## Ventajas de Cloudflare

✅ **CDN Global:** Contenido cacheado en 200+ ciudades
✅ **Protección DDoS:** Automática y gratuita  
✅ **SSL Gratis:** Certificado SSL universal
✅ **Optimización:** Minificación, compresión, HTTP/3
✅ **Analytics:** Estadísticas de tráfico gratis
✅ **Firewall:** Reglas de seguridad personalizables

## Resumen de IPs de Cloudflare para Whitelist

Si necesitas whitelist en firewall, agrega estos rangos:
```
173.245.48.0/20
103.21.244.0/22
103.22.200.0/22
103.31.4.0/22
141.101.64.0/18
108.162.192.0/18
190.93.240.0/20
188.114.96.0/20
197.234.240.0/22
198.41.128.0/17
162.158.0.0/15
104.16.0.0/13
104.24.0.0/14
172.64.0.0/13
131.0.72.0/22
```

## Siguiente Paso

**PRIMERO resuelve el port forwarding/NAT** (ver archivo NAT_PORT_FORWARDING.md)

**DESPUÉS configura Cloudflare** siguiendo esta guía

---

**Dudas frecuentes:**

Q: ¿Necesito pagar por Cloudflare?
A: No, el plan Free es suficiente

Q: ¿Cloudflare reemplaza al DNS de Windows Server?
A: Sí, es recomendado dejar que Cloudflare maneje el DNS

Q: ¿Puedo usar Cloudflare sin abrir puertos?
A: Sí, usando Cloudflare Tunnel (ver NAT_PORT_FORWARDING.md)
