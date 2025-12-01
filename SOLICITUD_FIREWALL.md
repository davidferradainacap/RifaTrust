# Solicitud de Apertura de Puertos - Firewall Datacenter

## Información del Servidor
- **IP Pública:** 186.189.100.240
- **IP Privada:** 10.0.2.15
- **Sistema Operativo:** Windows Server 2022 Datacenter
- **Servicio:** Servidor Web IIS para aplicación RifaTrust.com

## Solicitud
Solicito la apertura de los siguientes puertos en el firewall del datacenter para permitir acceso público al servidor web:

### Puertos Requeridos:
- **Puerto 80 (HTTP)**
  - Protocolo: TCP
  - Dirección: Entrada (Inbound)
  - Origen: Cualquier (0.0.0.0/0)
  - Destino: 186.189.100.240
  
- **Puerto 443 (HTTPS)**
  - Protocolo: TCP
  - Dirección: Entrada (Inbound)
  - Origen: Cualquier (0.0.0.0/0)
  - Destino: 186.189.100.240

### Reglas de Firewall Sugeridas:
```
ALLOW TCP FROM any TO 186.189.100.240:80
ALLOW TCP FROM any TO 186.189.100.240:443
```

## Propósito
Servidor web público para la aplicación RifaTrust.com - Sistema de gestión de rifas

## Contacto
- **Administrador:** David Ferrada
- **Email:** daldeaferrada@gmail.com

## Verificación
Una vez abiertos los puertos, se puede verificar con:
```bash
telnet 186.189.100.240 80
curl http://186.189.100.240
```

## Urgencia
**ALTA** - Necesario para poner el sitio en producción

---

**Fecha de Solicitud:** 01 de Diciembre de 2025
