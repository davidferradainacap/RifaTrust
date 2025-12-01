# Configuración DNS para RifaTrust.com

## IP del Servidor
**IP Pública:** `186.189.100.240`

---

## Instrucciones por Proveedor

### GoDaddy
1. Inicia sesión en https://www.godaddy.com
2. Ve a **"Mis Productos"** → **"Dominios"**
3. Click en **RifaTrust.com** → **"DNS"** o **"Administrar DNS"**
4. En la sección **"Registros"**, agrega:

**Registro A para dominio raíz:**
```
Tipo: A
Nombre: @
Valor: 186.189.100.240
TTL: 600 (10 minutos) o 3600 (1 hora)
```

**Registro A para www:**
```
Tipo: A
Nombre: www
Valor: 186.189.100.240
TTL: 600
```

5. Click **"Guardar"** o **"Agregar registro"**
6. Espera 15-30 minutos para propagación

---

### Namecheap
1. Inicia sesión en https://www.namecheap.com
2. Click en **"Domain List"** → Selecciona **RifaTrust.com**
3. Click en **"Manage"** → Pestaña **"Advanced DNS"**
4. En **"Host Records"**, agrega:

**Registro para dominio raíz:**
```
Type: A Record
Host: @
Value: 186.189.100.240
TTL: Automatic
```

**Registro para www:**
```
Type: A Record
Host: www
Value: 186.189.100.240
TTL: Automatic
```

5. Click **"Save All Changes"**
6. Espera 15-30 minutos para propagación

---

### Cloudflare (Recomendado para CDN y protección)
1. Inicia sesión en https://dash.cloudflare.com
2. Agrega el dominio **RifaTrust.com** si no está agregado
3. Ve a **"DNS"** → **"Records"**
4. Agrega los siguientes registros:

**Registro A para dominio raíz:**
```
Type: A
Name: @
IPv4 address: 186.189.100.240
Proxy status: Proxied (nube naranja) ✅
TTL: Auto
```

**Registro A para www:**
```
Type: A
Name: www
IPv4 address: 186.189.100.240
Proxy status: Proxied (nube naranja) ✅
TTL: Auto
```

5. Cloudflare te dará nameservers (ej: dana.ns.cloudflare.com)
6. Ve a tu proveedor de dominio original y cambia los nameservers a los de Cloudflare
7. Espera 24-48 horas para propagación completa (pero funciona en ~1 hora)

**Ventajas de Cloudflare:**
- ✅ CDN gratis (carga más rápida globalmente)
- ✅ Protección DDoS
- ✅ SSL/TLS automático
- ✅ Analytics de tráfico

---

### Google Domains
1. Inicia sesión en https://domains.google.com
2. Click en tu dominio **RifaTrust.com**
3. En el menú lateral, click en **"DNS"**
4. Scroll hasta **"Custom records"**
5. Agrega:

**Registro para dominio raíz:**
```
Host name: @
Type: A
TTL: 3600
Data: 186.189.100.240
```

**Registro para www:**
```
Host name: www
Type: A
TTL: 3600
Data: 186.189.100.240
```

6. Click **"Save"**

---

### Proveedor Genérico (Otros)

**Busca en tu panel de control:**
- "DNS Management", "DNS Settings", "Manage DNS", "Zone File", o "Nameservers"

**Agrega estos dos registros A:**

| Tipo | Nombre/Host | Valor/Destino      | TTL  |
|------|-------------|-------------------|------|
| A    | @           | 186.189.100.240   | 3600 |
| A    | www         | 186.189.100.240   | 3600 |

**Notas importantes:**
- `@` representa el dominio raíz (RifaTrust.com)
- `www` es el subdominio (www.RifaTrust.com)
- TTL en segundos (3600 = 1 hora)
- Algunos proveedores usan `*` en lugar de `@`

---

## Verificar Propagación DNS

### Desde Windows Server (local):
```powershell
nslookup RifaTrust.com
nslookup www.RifaTrust.com
```

**Resultado esperado:**
```
Address: 186.189.100.240
```

### Verificación Online:
- https://dnschecker.org - Ver propagación global
- https://whatsmydns.net - Verificar en múltiples países
- https://www.nslookup.io - Lookup detallado

Busca: `RifaTrust.com` y verifica que aparezca `186.189.100.240`

---

## Tiempos de Propagación

- **Local (tu ISP):** 5-30 minutos
- **Global:** 1-4 horas
- **Completo:** 24-48 horas máximo

**Tip:** Usa `ipconfig /flushdns` en Windows para limpiar caché DNS local.

---

## Después de Configurar DNS

Una vez que el DNS esté propagado y `nslookup RifaTrust.com` devuelva `186.189.100.240`:

1. **Abrir puertos en firewall del datacenter** (contactar equipo de datacenter)
2. **Instalar certificado SSL** con win-acme:
   ```powershell
   cd C:\win-acme
   .\wacs.exe
   ```
3. **Habilitar HTTPS** en Django (descomentar configuraciones de seguridad)

---

## Contacto y Soporte

Si tienes problemas:
1. Verifica que los registros estén guardados correctamente
2. Espera al menos 30 minutos antes de probar
3. Limpia caché DNS: `ipconfig /flushdns`
4. Prueba desde otro dispositivo/red
5. Usa herramientas online de verificación

**¿No sabes quién es tu proveedor?**
Busca en tu email la confirmación de compra del dominio o usa:
```powershell
nslookup -type=NS RifaTrust.com
```
(Cuando ya tenga DNS configurado, mostrará los nameservers)
