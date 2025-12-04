# 📁 Documentación Azure

Esta carpeta contiene toda la documentación relacionada con el deployment en **Microsoft Azure**.

## 📄 Archivos

### Guías de Deployment
- **`AZURE_DEPLOYMENT_GUIDE.md`** - Guía completa paso a paso para desplegar en Azure (600+ líneas)
- **`AZURE_COMMANDS.md`** - Comandos rápidos de Azure CLI y Azure Portal
- **`READY_FOR_AZURE.md`** - Resumen visual de readiness para deployment

### Configuración
- **`.env.azure`** - Variables de entorno para producción en Azure
  - ⚠️ **CONFIDENCIAL** - No subir a Git (incluido en .gitignore)
  - Contiene SECRET_KEY, credenciales de BD, API keys

## 🚀 Uso

### Pre-requisitos
1. Cuenta de Azure activa
2. Azure CLI instalado
3. Git configurado
4. Proyecto listo (migraciones aplicadas, tests pasando)

### Deployment Rápido
```bash
# 1. Revisar configuración
cat .env.azure

# 2. Seguir guía principal
cat AZURE_DEPLOYMENT_GUIDE.md

# 3. Usar comandos rápidos
cat AZURE_COMMANDS.md
```

## 📋 Checklist Pre-Deployment

- [ ] SECRET_KEY generado
- [ ] Variables de entorno configuradas
- [ ] Base de datos MySQL preparada
- [ ] Archivos estáticos recolectados
- [ ] Migraciones aplicadas
- [ ] Tests pasando al 100%

## 🔗 Referencias

- [Documentación oficial Azure App Service](https://docs.microsoft.com/azure/app-service/)
- [Django deployment checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)

---

**Última actualización:** Diciembre 2024  
**Estado:** Production Ready ✅
