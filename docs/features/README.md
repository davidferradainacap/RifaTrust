# 🎨 Features

Esta carpeta contiene documentación de **características y funcionalidades** implementadas en RifaTrust.

## 📄 Archivos

### Políticas y Reglas de Negocio
- **`ALMACENAMIENTO_RETIRO_PREMIOS.md`** - Políticas de almacenamiento y retiro de premios físicos
- **`TERMINOS_CONDICIONES_IMPLEMENTACION.md`** - Implementación del modal de Términos y Condiciones

### Restricciones del Sistema
- **`RESTRICCION_ORGANIZADORES.md`** - Restricción: organizadores no pueden comprar boletos

## 📋 Features Documentadas

### 1. Almacenamiento y Retiro de Premios 📦
**Implementado:** Sí ✅

Políticas de gestión de premios físicos:
- **Almacenamiento:** 60 días desde la fecha del sorteo
- **Horarios:** Lunes a Viernes, 9:00 AM - 6:00 PM
- **Documentación:** ID válido requerido
- **Ubicación:** [Dirección configurada en settings]

**Documentación:** `ALMACENAMIENTO_RETIRO_PREMIOS.md`

---

### 2. Términos y Condiciones ⚖️
**Implementado:** Sí ✅

Modal interactivo con 16 secciones:
- Aceptación obligatoria en registro
- Políticas de reembolso (48h post-extensión)
- Política de almacenamiento de premios
- Sistema de sorteo y ganadores
- Procedimiento de recogida

**Documentación:** `TERMINOS_CONDICIONES_IMPLEMENTACION.md`

---

### 3. Restricción de Organizadores 🚫
**Implementado:** Sí ✅

Los organizadores NO pueden comprar boletos:
- Solo pueden crear y administrar rifas
- Validación en backend y frontend
- API retorna `puede_comprar: false`
- UI muestra mensaje de "Solo Visualización"

**Documentación:** `RESTRICCION_ORGANIZADORES.md`

---

## 🎯 Reglas de Negocio

### Roles del Sistema

| Rol | Crear Rifas | Comprar Boletos | Ver Estadísticas | Administrar |
|-----|-------------|-----------------|------------------|-------------|
| **Participante** | ❌ | ✅ | ❌ | ❌ |
| **Organizador** | ✅ | ❌ | ✅ (propias) | ✅ (propias) |
| **Sponsor** | ❌ | ✅ | ✅ (patrocinadas) | ❌ |
| **Admin** | ✅ | ✅ | ✅ (todas) | ✅ (todas) |

### Flujo de Rifas

```
[Borrador] → [Pendiente Aprobación] → [Aprobada] → [Activa] → [Finalizada]
                                                        ↓
                                                   [Pausada]
                                                        ↓
                                                    [Activa]
```

### Compra de Boletos

**Restricciones:**
- ❌ Organizadores no pueden comprar
- ✅ Usuarios autenticados solamente
- ✅ Solo en rifas con estado "activa"
- ✅ Máximo de boletos por usuario (configurable)
- ✅ Stock disponible verificado con bloqueo

**Proceso:**
1. Seleccionar cantidad de boletos
2. Reservar boletos (bloqueo de BD)
3. Procesar pago con Stripe
4. Confirmar compra
5. Generar códigos QR únicos

## 📊 Métricas de Features

### T&C Modal
- **Secciones:** 16
- **Longitud:** ~3000 palabras
- **Tasa de Aceptación:** 100% (obligatorio)

### Restricción Organizadores
- **Validaciones:** 4 capas (vista, template, API, serializer)
- **Cobertura:** 100%
- **Impacto:** Solo organizadores

## 🔄 Próximas Features

### En Planificación
- [ ] Sistema de notificaciones push
- [ ] Chat entre organizador y participantes
- [ ] Sistema de referidos
- [ ] Programa de fidelidad
- [ ] Rifas colaborativas

### En Consideración
- [ ] Integración con redes sociales
- [ ] Sistema de ratings
- [ ] Marketplace de rifas
- [ ] App móvil nativa

## 📝 Agregar Nueva Feature

### 1. Documentación
Crear archivo `NOMBRE_FEATURE.md` en esta carpeta con:
- Descripción detallada
- Reglas de negocio
- Casos de uso
- Implementación técnica
- Screenshots/diagramas

### 2. Implementación
- Backend: `backend/apps/`
- Frontend: `frontend/templates/`
- Tests: `docs/testing/`

### 3. Actualizar este README
Agregar entrada en la sección "Features Documentadas"

## 🔗 Referencias

- [Documentación Completa](../DOCUMENTACION_COMPLETA.md)
- [Plan de Pruebas](../testing/PLAN_PRUEBAS_COMPLETO.md)
- [README Principal](../../README.md)

---

**Última actualización:** Diciembre 2024  
**Features Activas:** 3  
**En Desarrollo:** 0
