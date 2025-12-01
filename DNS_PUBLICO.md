# Configuración DNS Público para RifaTrust.com

## Problema Actual
❌ El DNS configurado en Windows Server es solo LOCAL
❌ Internet no puede resolver www.rifatrust.com
✅ Funciona internamente: http://local.RifaTrust.com

## Solución: DNS Público con Cloudflare (GRATIS)

### Paso 1: Crear Cuenta en Cloudflare
1. Ve a: https://dash.cloudflare.com/sign-up
2. Crea cuenta con: daldeaferrada@gmail.com
3. Verifica tu email

### Paso 2: Agregar Dominio
1. Click en **"Add a Site"**
2. Ingresa: **RifaTrust.com**
3. Selecciona plan **FREE** (gratis)
4. Click **"Continue"**

### Paso 3: Configurar Registros DNS
Cloudflare detectará los registros automáticamente, pero necesitas agregar/modificar:

**Eliminar cualquier registro A existente para @ y www**

**Agregar estos dos registros:**

```
Tipo: A
Nombre: @
Contenido: 186.189.100.240
Proxy: ✅ Activado (nube naranja)
TTL: Auto
```

```
Tipo: A
Nombre: www
Contenido: 186.189.100.240
Proxy: ✅ Activado (nube naranja)
TTL: Auto
```

### Paso 4: Cambiar Nameservers
Cloudflare te dará 2 nameservers, algo como:
```
dana.ns.cloudflare.com
walt.ns.cloudflare.com
```

**IMPORTANTE:** Necesitas ir donde COMPRASTE el dominio RifaTrust.com y cambiar los nameservers a estos.

#### ¿Dónde compraste el dominio?
- **GoDaddy:** https://www.godaddy.com → My Products → Domains → RifaTrust.com → Manage DNS → Nameservers → Change → Custom
- **Namecheap:** https://www.namecheap.com → Domain List → Manage → Domain → Nameservers → Custom DNS
- **Google Domains:** https://domains.google.com → DNS → Name servers → Use custom name servers
- **Otro:** Busca "Nameservers" o "DNS Settings" en tu panel

**Ingresa los nameservers que Cloudflare te dio**

### Paso 5: Verificar en Cloudflare
1. Vuelve a Cloudflare
2. Click **"Done, check nameservers"**
3. Espera 5-30 minutos
4. Recibirás un email cuando esté activo

### Paso 6: Configurar SSL/TLS en Cloudflare
1. En Cloudflare, ve a **SSL/TLS**
2. Selecciona **"Flexible"** (mientras no tengas certificado en el servidor)
3. Más tarde cambiaremos a **"Full (strict)"** cuando instalemos Let's Encrypt

---

## Opción 2: Usar Proveedor de Dominio Directamente

Si NO quieres usar Cloudflare, configura directamente en donde compraste el dominio:

### Configuración Manual en tu Proveedor

**Busca en tu panel:** "DNS Management", "DNS Settings", o "Manage DNS"

**Agrega/Modifica estos registros:**

```
Tipo: A
Host: @
Valor: 186.189.100.240
TTL: 3600
```

```
Tipo: A
Host: www
Valor: 186.189.100.240
TTL: 3600
```

---

## Verificar Propagación DNS

Después de configurar, verifica en:
- https://dnschecker.org (busca: rifatrust.com)
- https://whatsmydns.net

**Tiempo de propagación:**
- 5-15 minutos: Algunos servidores DNS
- 1-4 horas: Mayoría de ubicaciones
- 24-48 horas: Propagación completa global

---

## Mientras Esperas la Propagación

### Abrir Puertos en Firewall del Datacenter

**IMPORTANTE:** Contacta al equipo de red del datacenter y solicita:

**Asunto del Ticket:** Apertura de puertos para servidor web RifaTrust.com

**Mensaje:**
```
Solicito la apertura de los siguientes puertos en el firewall para mi servidor:

IP del Servidor: 186.189.100.240
Puertos a abrir:
- Puerto 80 (HTTP) - Entrada desde cualquier origen
- Puerto 443 (HTTPS) - Entrada desde cualquier origen

Protocolo: TCP
Dirección: Entrada (Inbound)

Propósito: Servidor web público para aplicación RifaTrust.com

Gracias.
```

---

## Prueba de Conectividad Externa

**Desde tu teléfono (usando datos móviles, NO wifi del datacenter):**
1. Desactiva WiFi
2. Abre navegador
3. Ve a: http://186.189.100.240

Si funciona → El servidor está accesible, solo falta DNS público
Si NO funciona → El firewall del datacenter está bloqueando

---

## Resumen de Estado Actual

✅ **Funcionando:**
- Servidor web operativo
- Django + MySQL funcionando
- DNS local configurado
- Acceso interno: http://local.RifaTrust.com

❌ **Pendiente:**
- DNS público (Cloudflare o proveedor de dominio)
- Firewall del datacenter (puerto 80 y 443)
- Certificado SSL (Let's Encrypt)

---

## Siguiente Paso INMEDIATO

1. **Identifica dónde compraste el dominio RifaTrust.com**
2. **Decide:** ¿Cloudflare (recomendado) o DNS directo del proveedor?
3. **Configura DNS público con IP: 186.189.100.240**
4. **Contacta al equipo del datacenter para abrir puertos**

**¿Dónde compraste el dominio RifaTrust.com?**
