# Guía de Producción - RifaTrust.com

## Estado Actual
✅ Aplicación Django funcionando completamente
✅ MySQL configurado con PyMySQL
✅ IIS + FastCGI operativo
✅ Archivos estáticos sirviendo correctamente
✅ Funciona perfectamente en Brave Browser

## Pasos para Producción Completa

### 1. Configuración de DNS (URGENTE)
**Acción requerida:** Configurar registros DNS en tu proveedor de dominio

```
Tipo: A
Nombre: @
Valor: 186.189.100.240
TTL: 3600

Tipo: A  
Nombre: www
Valor: 186.189.100.240
TTL: 3600
```

**Verificar después de 15-30 minutos:**
```powershell
nslookup RifaTrust.com
nslookup www.RifaTrust.com
```

### 2. Configuración de Firewall del Datacenter (CRÍTICO)
**Acción requerida:** Contactar equipo de datacenter

**Puertos a abrir en el firewall externo:**
- Puerto 80 (HTTP) - IP: 186.189.100.240
- Puerto 443 (HTTPS) - IP: 186.189.100.240

**Reglas necesarias:**
```
ALLOW TCP 80 FROM any TO 186.189.100.240
ALLOW TCP 443 FROM any TO 186.189.100.240
```

### 3. Certificado SSL con Let's Encrypt

**Una vez que DNS y firewall estén configurados:**

```powershell
cd C:\win-acme
.\wacs.exe
```

**Seleccionar opciones:**
1. N - Create certificate (simple for IIS)
2. 1 - Single binding of an IIS site
3. Seleccionar "SistemaRifas"
4. Seleccionar binding para RifaTrust.com
5. Aceptar términos de Let's Encrypt
6. Ingresar email: daldeaferrada@gmail.com

**El certificado se renovará automáticamente cada 60 días**

### 4. Habilitar Seguridad HTTPS en Django

**Editar:** `C:\Users\Administrator\Desktop\RS_project\config\settings.py`

**Descomentar líneas:**
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

**Reiniciar IIS:**
```powershell
Import-Module WebAdministration
Restart-WebAppPool -Name "RifasAppPool"
```

### 5. Configurar Stripe en Producción

**Editar:** `C:\Users\Administrator\Desktop\RS_project\.env`

```env
# Cambiar de test a producción
STRIPE_PUBLIC_KEY=pk_live_XXXXX
STRIPE_SECRET_KEY=sk_live_XXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXX
```

**Configurar webhook en Stripe Dashboard:**
- URL: https://RifaTrust.com/payments/webhook/stripe/
- Eventos: payment_intent.succeeded, payment_intent.payment_failed

### 6. Monitoreo y Logs

**Ubicación de logs:**
```
C:\Users\Administrator\Desktop\RS_project\logs\wfastcgi.log
C:\Users\Administrator\Desktop\RS_project\logs\django.log
```

**Ver logs en tiempo real:**
```powershell
Get-Content C:\Users\Administrator\Desktop\RS_project\logs\wfastcgi.log -Wait -Tail 50
```

### 7. Backups Automáticos

**Crear tarea programada para backup de MySQL:**
```powershell
$action = New-ScheduledTaskAction -Execute "mysqldump" -Argument "-u rifas_user -p'rifas_password' rifas_db > C:\Backups\rifas_db_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
Register-ScheduledTask -TaskName "Backup RifasDB" -Action $action -Trigger $trigger
```

### 8. Compatibilidad de Navegadores

**Estado actual:**
- ✅ Brave Browser: Funcionando perfectamente
- ⚠️ Chrome/Edge: Problema de compatibilidad en investigación

**Solución temporal para usuarios:**
- Recomendar usar Brave o Firefox
- Limpiar caché de Chrome si experimenta problemas

### 9. Verificación Final

**Checklist antes de ir a producción:**
- [ ] DNS apunta correctamente a 186.189.100.240
- [ ] Firewall del datacenter abre puertos 80/443
- [ ] Certificado SSL instalado y funcionando
- [ ] HTTPS forzado en Django
- [ ] Stripe configurado con keys de producción
- [ ] Backups automáticos configurados
- [ ] Logs monitoreados
- [ ] Pruebas de carga realizadas

### 10. Contactos y Soporte

**Administrador Sistema:**
- Email: daldeaferrada@gmail.com
- Usuario superadmin: daldeaferrada@gmail.com / admin123

**Servidor:**
- IP Pública: 186.189.100.240
- IP Privada: 10.0.2.15
- Dominio: RifaTrust.com
- SO: Windows Server 2022 Datacenter

**URLs de Acceso:**
- Sitio público: https://RifaTrust.com
- Panel admin: https://RifaTrust.com/admin-panel/
- Django admin: https://RifaTrust.com/django-admin/
- Página test: https://RifaTrust.com/test/

## Notas Importantes

1. **Seguridad:** El SECRET_KEY en producción debe mantenerse confidencial
2. **Stripe:** No compartir las keys de producción
3. **Base de datos:** Hacer backup antes de cualquier migración
4. **IIS:** Reiniciar el Application Pool después de cambios en código Python
5. **Static files:** Ejecutar `python manage.py collectstatic` después de cambios en CSS/JS
