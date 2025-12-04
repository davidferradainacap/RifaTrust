# 🧪 PLAN DE PRUEBAS COMPLETO - RIFATRUST

**Proyecto**: RifaTrust - Sistema de Gestión de Rifas  
**Versión**: 2.0  
**Fecha**: Diciembre 3, 2025  
**Ambiente**: Pre-producción / Azure Staging

---

## 📋 ÍNDICE

1. [Módulo de Usuarios](#1-módulo-de-usuarios)
2. [Módulo de Rifas](#2-módulo-de-rifas)
3. [Módulo de Pagos](#3-módulo-de-pagos)
4. [Panel de Administración](#4-panel-de-administración)
5. [Seguridad](#5-seguridad)
6. [Performance](#6-performance)
7. [Integración](#7-integración)
8. [Regresión](#8-regresión)

---

## 1. MÓDULO DE USUARIOS

### 1.1 Registro de Usuario

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| US-01 | Registro exitoso con datos válidos | 1. Acceder a /register/<br>2. Llenar formulario completo<br>3. Aceptar términos<br>4. Click en "Registrarse" | Email: test@example.com<br>Password: Test1234!<br>Nombre: Juan Pérez<br>RUT: 12345678-9 | - Usuario creado<br>- Email de confirmación enviado<br>- Redirección a página de confirmación | ⚪ Pendiente | 🔴 Alta | QA |
| US-02 | Registro con email duplicado | 1. Intentar registrar email existente | Email ya registrado | Error: "Este email ya está registrado" | ⚪ Pendiente | 🔴 Alta | QA |
| US-03 | Registro con contraseña débil | 1. Ingresar contraseña sin números | Password: password | Error: "La contraseña debe contener números" | ⚪ Pendiente | 🟡 Media | QA |
| US-04 | Registro sin aceptar términos | 1. Llenar form<br>2. No marcar checkbox T&C<br>3. Intentar registrar | Checkbox sin marcar | Error: "Debes aceptar los términos" | ⚪ Pendiente | 🔴 Alta | QA |
| US-05 | Validación de email MX records | 1. Ingresar email con dominio inválido | Email: test@dominiofalso999.com | Error: "Email no válido" | ⚪ Pendiente | 🟡 Media | QA |
| US-06 | Validación de RUT chileno | 1. Ingresar RUT inválido | RUT: 12345678-0 | Error: "RUT inválido" | ⚪ Pendiente | 🟡 Media | QA |
| US-07 | Modal de Términos y Condiciones | 1. Click en "Términos y Condiciones"<br>2. Verificar contenido<br>3. Scroll completo<br>4. Click en aceptar | - | Modal se abre<br>16 secciones visibles<br>Checkbox se marca | ⚪ Pendiente | 🔴 Alta | QA |
| US-08 | Campos obligatorios vacíos | 1. Dejar campos en blanco<br>2. Intentar registrar | Campos vacíos | Errores de validación | ⚪ Pendiente | 🟡 Media | QA |

### 1.2 Login y Autenticación

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| US-09 | Login exitoso con credenciales válidas | 1. Ir a /login/<br>2. Ingresar email y password<br>3. Click "Iniciar sesión" | Email confirmado<br>Password correcto | Redirección a dashboard<br>Sesión iniciada | ⚪ Pendiente | 🔴 Alta | QA |
| US-10 | Login con email no confirmado | 1. Intentar login sin confirmar email | Email sin confirmar | Error: "Confirma tu email" | ⚪ Pendiente | 🔴 Alta | QA |
| US-11 | Login con contraseña incorrecta | 1. Ingresar password incorrecta | Password incorrecta | Error: "Credenciales inválidas" | ⚪ Pendiente | 🔴 Alta | QA |
| US-12 | Rate limiting - 5 intentos fallidos | 1. Intentar login 5 veces con password incorrecta | 5 intentos fallidos | Cuenta bloqueada 1 hora<br>Mensaje de bloqueo | ⚪ Pendiente | 🔴 Alta | QA |
| US-13 | Login después de rate limit | 1. Esperar 1 hora después de bloqueo<br>2. Intentar login | Credenciales correctas | Login exitoso | ⚪ Pendiente | 🟡 Media | QA |
| US-14 | Sesión persistente con "Recuérdame" | 1. Marcar checkbox "Recuérdame"<br>2. Login<br>3. Cerrar navegador<br>4. Abrir nuevamente | Checkbox marcado | Sesión mantiene activa | ⚪ Pendiente | 🟢 Baja | QA |
| US-15 | Logout exitoso | 1. Click en "Cerrar sesión" | Usuario autenticado | Sesión cerrada<br>Redirección a home | ⚪ Pendiente | 🟡 Media | QA |

### 1.3 Recuperación de Contraseña

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| US-16 | Solicitar reset con email válido | 1. Ir a "¿Olvidaste tu contraseña?"<br>2. Ingresar email<br>3. Enviar | Email registrado | Email con link enviado<br>Mensaje de confirmación | ⚪ Pendiente | 🔴 Alta | QA |
| US-17 | Solicitar reset con email no registrado | 1. Ingresar email no existente | Email no registrado | Mensaje genérico (seguridad) | ⚪ Pendiente | 🟡 Media | QA |
| US-18 | Verificar token de reset válido | 1. Click en link de email<br>2. Verificar acceso a página | Token válido no expirado | Página de cambio de contraseña | ⚪ Pendiente | 🔴 Alta | QA |
| US-19 | Verificar token expirado (24h) | 1. Intentar usar token después de 24h | Token expirado | Error: "Link expirado" | ⚪ Pendiente | 🟡 Media | QA |
| US-20 | Cambiar contraseña exitosamente | 1. Ingresar nueva contraseña<br>2. Confirmar contraseña<br>3. Guardar | Password nueva válida | Contraseña actualizada<br>Email de confirmación<br>Redirección a login | ⚪ Pendiente | 🔴 Alta | QA |
| US-21 | Validar passwords no coinciden | 1. Ingresar passwords diferentes | Passwords distintas | Error: "Las contraseñas no coinciden" | ⚪ Pendiente | 🟡 Media | QA |

### 1.4 Perfil de Usuario

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| US-22 | Ver perfil de usuario | 1. Login<br>2. Ir a "Mi Perfil" | Usuario autenticado | Datos del perfil visibles | ⚪ Pendiente | 🟡 Media | QA |
| US-23 | Editar información personal | 1. Click en "Editar perfil"<br>2. Modificar nombre y teléfono<br>3. Guardar | Datos válidos | Perfil actualizado<br>Mensaje de éxito | ⚪ Pendiente | 🟡 Media | QA |
| US-24 | Subir foto de perfil | 1. Click en avatar<br>2. Seleccionar imagen<br>3. Subir | JPG/PNG < 5MB | Avatar actualizado | ⚪ Pendiente | 🟢 Baja | QA |
| US-25 | Cambiar contraseña desde perfil | 1. Ir a "Seguridad"<br>2. Ingresar contraseña actual<br>3. Nueva contraseña<br>4. Guardar | Contraseña actual correcta | Password actualizada<br>Email notificación | ⚪ Pendiente | 🔴 Alta | QA |
| US-26 | Ver historial de compras | 1. Ir a "Mis Boletos" | Usuario con compras | Lista de boletos comprados | ⚪ Pendiente | 🟡 Media | QA |
| US-27 | Ver notificaciones | 1. Click en campana de notificaciones | Usuario con notificaciones | Lista de notificaciones | ⚪ Pendiente | 🟢 Baja | QA |

---

## 2. MÓDULO DE RIFAS

### 2.1 Visualización de Rifas

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| RF-01 | Ver lista de rifas activas | 1. Acceder a /raffles/ | - | Lista de rifas con estado "activa" | ⚪ Pendiente | 🔴 Alta | QA |
| RF-02 | Ver detalle de rifa | 1. Click en una rifa | ID de rifa | Detalle completo:<br>- Premio<br>- Precio<br>- Boletos disponibles<br>- Fecha sorteo | ⚪ Pendiente | 🔴 Alta | QA |
| RF-03 | Filtrar rifas por categoría | 1. Seleccionar categoría del menú | Categoría específica | Rifas filtradas | ⚪ Pendiente | 🟡 Media | QA |
| RF-04 | Buscar rifas por nombre | 1. Ingresar texto en buscador | "iPhone" | Rifas coincidentes | ⚪ Pendiente | 🟡 Media | QA |
| RF-05 | Ordenar rifas por precio | 1. Click en "Ordenar por precio" | - | Rifas ordenadas ascendente | ⚪ Pendiente | 🟢 Baja | QA |
| RF-06 | Ver contador de tiempo restante | 1. Observar timer en rifa | Rifa con fecha cercana | Contador en tiempo real | ⚪ Pendiente | 🟡 Media | QA |
| RF-07 | Ver progreso de boletos vendidos | 1. Ver barra de progreso | Rifa con ventas | % correcto de boletos vendidos | ⚪ Pendiente | 🟡 Media | QA |

### 2.2 Compra de Boletos

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| RF-08 | Seleccionar cantidad de boletos | 1. Ingresar cantidad<br>2. Ver precio total | Cantidad: 5 | Precio total actualizado | ⚪ Pendiente | 🔴 Alta | QA |
| RF-09 | Agregar boletos al carrito | 1. Click "Agregar al carrito" | Cantidad válida | Carrito actualizado<br>Contador badge | ⚪ Pendiente | 🔴 Alta | QA |
| RF-10 | Ver carrito de compras | 1. Click en ícono carrito | Carrito con items | Lista de boletos<br>Total a pagar | ⚪ Pendiente | 🔴 Alta | QA |
| RF-11 | Eliminar item del carrito | 1. Click en "Eliminar" | Item en carrito | Item removido<br>Total actualizado | ⚪ Pendiente | 🟡 Media | QA |
| RF-12 | Validar cantidad máxima por usuario | 1. Intentar comprar más de 10 boletos | Cantidad: 15 | Error: "Máximo 10 boletos por usuario" | ⚪ Pendiente | 🔴 Alta | QA |
| RF-13 | Compra sin estar autenticado | 1. Intentar comprar sin login | Usuario anónimo | Redirección a login | ⚪ Pendiente | 🔴 Alta | QA |
| RF-14 | Validar boletos disponibles | 1. Intentar comprar cuando quedan pocos | Cantidad > disponibles | Error: "Solo quedan X boletos" | ⚪ Pendiente | 🔴 Alta | QA |

### 2.3 Creación de Rifas (Organizador)

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| RF-15 | Crear rifa con datos válidos | 1. Ir a "Crear rifa"<br>2. Llenar formulario completo<br>3. Subir imágenes<br>4. Guardar | Datos completos<br>Imágenes JPG | Rifa creada en estado "borrador" | ⚪ Pendiente | 🔴 Alta | QA |
| RF-16 | Validar campos obligatorios | 1. Intentar guardar sin llenar campos | Campos vacíos | Errores de validación | ⚪ Pendiente | 🔴 Alta | QA |
| RF-17 | Subir múltiples imágenes del premio | 1. Seleccionar 5 imágenes | JPG/PNG < 5MB c/u | 5 imágenes subidas | ⚪ Pendiente | 🟡 Media | QA |
| RF-18 | Validar precio mínimo de boleto | 1. Ingresar precio < 1000 | Precio: 500 | Error: "Precio mínimo $1,000" | ⚪ Pendiente | 🟡 Media | QA |
| RF-19 | Validar cantidad de boletos | 1. Ingresar cantidad válida | 50-10000 | Aceptado | ⚪ Pendiente | 🟡 Media | QA |
| RF-20 | Editar rifa en borrador | 1. Abrir rifa borrador<br>2. Modificar datos<br>3. Guardar | Rifa en borrador | Cambios guardados | ⚪ Pendiente | 🟡 Media | QA |
| RF-21 | Publicar rifa | 1. Rifa completa<br>2. Click "Publicar" | Rifa aprobada | Estado cambia a "activa" | ⚪ Pendiente | 🔴 Alta | QA |
| RF-22 | Intentar publicar sin aprobación admin | 1. Intentar publicar sin aprobación | Rifa no aprobada | Error: "Requiere aprobación" | ⚪ Pendiente | 🔴 Alta | QA |

### 2.4 Sorteos

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| RF-23 | Ejecutar sorteo manual | 1. Rifa con fecha cumplida<br>2. Click "Realizar sorteo" | Rifa con todos los boletos vendidos | Ganador seleccionado<br>Notificaciones enviadas | ⚪ Pendiente | 🔴 Alta | QA |
| RF-24 | Verificar hash SHA-256 del sorteo | 1. Ver detalles del sorteo | Sorteo realizado | Hash visible<br>Verificable | ⚪ Pendiente | 🟡 Media | QA |
| RF-25 | Ver lista de ganadores | 1. Ir a "Ganadores" | Sorteos finalizados | Lista completa de ganadores | ⚪ Pendiente | 🟡 Media | QA |
| RF-26 | Notificación al ganador | 1. Verificar email del ganador | Ganador seleccionado | Email con instrucciones | ⚪ Pendiente | 🔴 Alta | QA |

---

## 3. MÓDULO DE PAGOS

### 3.1 Procesamiento de Pagos

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| PG-01 | Pago exitoso con tarjeta válida | 1. Proceder al pago<br>2. Ingresar datos tarjeta<br>3. Confirmar | Card: 4242 4242 4242 4242<br>Exp: 12/25<br>CVC: 123 | - Pago aprobado<br>- Boletos asignados<br>- Email confirmación | ⚪ Pendiente | 🔴 Alta | QA |
| PG-02 | Pago rechazado por fondos insuficientes | 1. Usar tarjeta sin fondos | Card: 4000 0000 0000 9995 | Error: "Pago rechazado" | ⚪ Pendiente | 🔴 Alta | QA |
| PG-03 | Pago con tarjeta expirada | 1. Ingresar tarjeta expirada | Exp: 01/20 | Error: "Tarjeta expirada" | ⚪ Pendiente | 🟡 Media | QA |
| PG-04 | Validar CVC incorrecto | 1. Ingresar CVC inválido | CVC: 000 | Error: "CVC inválido" | ⚪ Pendiente | 🟡 Media | QA |
| PG-05 | Ver comprobante de pago | 1. Después de pago exitoso<br>2. Click "Ver comprobante" | Pago completado | PDF con detalles | ⚪ Pendiente | 🟡 Media | QA |
| PG-06 | Historial de transacciones | 1. Ir a "Mis pagos" | Usuario con compras | Lista de pagos con estados | ⚪ Pendiente | 🟡 Media | QA |

### 3.2 Reembolsos

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| PG-07 | Solicitar reembolso por rifa extendida | 1. Rifa extendida en plazo<br>2. Solicitar reembolso dentro de 48h | Dentro de ventana válida | Solicitud aceptada<br>Reembolso procesado | ⚪ Pendiente | 🔴 Alta | QA |
| PG-08 | Rechazar reembolso fuera de plazo | 1. Intentar reembolso después de 48h | Fuera de ventana | Error: "Plazo vencido" | ⚪ Pendiente | 🔴 Alta | QA |
| PG-09 | Rechazar reembolso sin causa válida | 1. Solicitar reembolso de rifa normal | Rifa sin extensión | Error: "No aplica reembolso" | ⚪ Pendiente | 🟡 Media | QA |
| PG-10 | Verificar estado de reembolso | 1. Ver estado en "Mis pagos" | Reembolso solicitado | Estado: "Procesando" o "Completado" | ⚪ Pendiente | 🟡 Media | QA |
| PG-11 | Recibir notificación de reembolso | 1. Reembolso procesado | Reembolso completado | Email de confirmación | ⚪ Pendiente | 🟡 Media | QA |

### 3.3 Webhooks de Stripe

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| PG-12 | Webhook payment_intent.succeeded | 1. Simular webhook exitoso | Event: payment_intent.succeeded | Pago registrado<br>Boletos asignados | ⚪ Pendiente | 🔴 Alta | Dev |
| PG-13 | Webhook payment_intent.failed | 1. Simular webhook fallido | Event: payment_intent.failed | Pago marcado como fallido | ⚪ Pendiente | 🔴 Alta | Dev |
| PG-14 | Validar firma de webhook | 1. Enviar webhook sin firma válida | Firma inválida | Request rechazado | ⚪ Pendiente | 🔴 Alta | Dev |
| PG-15 | Webhook charge.refunded | 1. Simular reembolso desde Stripe | Event: charge.refunded | Reembolso registrado | ⚪ Pendiente | 🟡 Media | Dev |

---

## 4. PANEL DE ADMINISTRACIÓN

### 4.1 Dashboard

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| AD-01 | Ver métricas del dashboard | 1. Login como admin<br>2. Ver dashboard | Usuario admin | - Usuarios totales<br>- Rifas activas<br>- Ventas del mes<br>- Gráficos | ⚪ Pendiente | 🔴 Alta | QA |
| AD-02 | Filtrar métricas por fecha | 1. Seleccionar rango de fechas | Fecha inicio/fin | Datos actualizados | ⚪ Pendiente | 🟡 Media | QA |
| AD-03 | Exportar reporte a Excel | 1. Click "Exportar"<br>2. Seleccionar Excel | - | Archivo .xlsx descargado | ⚪ Pendiente | 🟡 Media | QA |
| AD-04 | Ver actividad reciente | 1. Scroll a "Actividad" | - | Últimas 20 acciones | ⚪ Pendiente | 🟢 Baja | QA |

### 4.2 Gestión de Usuarios

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| AD-05 | Listar todos los usuarios | 1. Ir a "Usuarios" | - | Tabla con todos los usuarios | ⚪ Pendiente | 🔴 Alta | QA |
| AD-06 | Buscar usuario por email | 1. Ingresar email en buscador | Email específico | Usuario encontrado | ⚪ Pendiente | 🟡 Media | QA |
| AD-07 | Ver detalle de usuario | 1. Click en usuario | ID usuario | - Perfil completo<br>- Historial compras<br>- Rifas creadas | ⚪ Pendiente | 🟡 Media | QA |
| AD-08 | Suspender cuenta de usuario | 1. Seleccionar usuario<br>2. Click "Suspender"<br>3. Confirmar | Usuario activo | - Usuario suspendido<br>- No puede login | ⚪ Pendiente | 🔴 Alta | QA |
| AD-09 | Reactivar cuenta suspendida | 1. Usuario suspendido<br>2. Click "Reactivar" | Usuario suspendido | Usuario puede login nuevamente | ⚪ Pendiente | 🟡 Media | QA |
| AD-10 | Cambiar rol de usuario | 1. Editar usuario<br>2. Cambiar rol<br>3. Guardar | Nuevo rol | Permisos actualizados | ⚪ Pendiente | 🔴 Alta | QA |

### 4.3 Gestión de Rifas

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| AD-11 | Ver rifas pendientes de aprobación | 1. Ir a "Rifas Pendientes" | - | Lista de rifas en revisión | ⚪ Pendiente | 🔴 Alta | QA |
| AD-12 | Aprobar rifa | 1. Revisar rifa<br>2. Click "Aprobar" | Rifa válida | Rifa puede ser publicada | ⚪ Pendiente | 🔴 Alta | QA |
| AD-13 | Rechazar rifa con motivo | 1. Revisar rifa<br>2. Click "Rechazar"<br>3. Ingresar motivo | Motivo: "Imágenes poco claras" | - Rifa rechazada<br>- Organizador notificado | ⚪ Pendiente | 🔴 Alta | QA |
| AD-14 | Editar rifa existente | 1. Seleccionar rifa<br>2. Modificar datos<br>3. Guardar | Cambios válidos | Rifa actualizada | ⚪ Pendiente | 🟡 Media | QA |
| AD-15 | Cancelar rifa activa | 1. Seleccionar rifa<br>2. Click "Cancelar"<br>3. Confirmar reembolsos | Rifa activa | - Rifa cancelada<br>- Reembolsos procesados | ⚪ Pendiente | 🔴 Alta | QA |
| AD-16 | Extender plazo de rifa | 1. Editar fecha de sorteo<br>2. Guardar | Nueva fecha válida | - Fecha actualizada<br>- Compradores notificados | ⚪ Pendiente | 🔴 Alta | QA |

### 4.4 Logs de Auditoría

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| AD-17 | Ver logs de sistema | 1. Ir a "Auditoría" | - | Lista de acciones con timestamp | ⚪ Pendiente | 🟡 Media | QA |
| AD-18 | Filtrar logs por usuario | 1. Seleccionar usuario<br>2. Aplicar filtro | ID usuario | Logs de ese usuario | ⚪ Pendiente | 🟡 Media | QA |
| AD-19 | Filtrar logs por tipo de acción | 1. Seleccionar "Login" | Tipo: login | Solo eventos de login | ⚪ Pendiente | 🟡 Media | QA |
| AD-20 | Exportar logs | 1. Click "Exportar logs" | Rango de fechas | Archivo CSV descargado | ⚪ Pendiente | 🟢 Baja | QA |

---

## 5. SEGURIDAD

### 5.1 Autenticación y Autorización

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| SEC-01 | Acceso sin autenticación a rutas protegidas | 1. Sin login acceder a /dashboard/ | Usuario anónimo | Redirección a login | ⚪ Pendiente | 🔴 Alta | QA |
| SEC-02 | Acceso de usuario normal a panel admin | 1. Login como participante<br>2. Intentar acceder /admin/ | Usuario sin permisos | Error 403 Forbidden | ⚪ Pendiente | 🔴 Alta | QA |
| SEC-03 | Token JWT expirado | 1. Esperar expiración (1h)<br>2. Hacer request API | Token expirado | Error 401 Unauthorized | ⚪ Pendiente | 🔴 Alta | Dev |
| SEC-04 | Refresh token válido | 1. Token expirado<br>2. Usar refresh token | Refresh token válido | Nuevo access token | ⚪ Pendiente | 🔴 Alta | Dev |
| SEC-05 | CSRF token válido en POST | 1. Hacer POST sin CSRF token | Sin token | Request rechazado | ⚪ Pendiente | 🔴 Alta | Dev |

### 5.2 Rate Limiting

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| SEC-06 | Bloqueo después de 5 intentos fallidos | 1. Login fallido 5 veces | Password incorrecta | - Cuenta bloqueada<br>- Mensaje de error | ⚪ Pendiente | 🔴 Alta | QA |
| SEC-07 | Verificar bloqueo por IP | 1. Intentos desde misma IP | 5 intentos desde IP X | IP bloqueada 1 hora | ⚪ Pendiente | 🔴 Alta | QA |
| SEC-08 | Verificar bloqueo por username | 1. Intentos a misma cuenta desde IPs diferentes | 5 intentos a cuenta X | Cuenta bloqueada | ⚪ Pendiente | 🔴 Alta | QA |
| SEC-09 | Desbloqueo automático después de 1h | 1. Esperar 1 hora<br>2. Intentar login | Después de cooldown | Login permitido | ⚪ Pendiente | 🟡 Media | QA |
| SEC-10 | Reset de intentos después de login exitoso | 1. Login exitoso<br>2. Verificar contador | Login correcto | Contador en 0 | ⚪ Pendiente | 🟡 Media | QA |

### 5.3 Validación y Sanitización

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| SEC-11 | XSS en campos de texto | 1. Ingresar script en campo | `<script>alert('XSS')</script>` | Script sanitizado | ⚪ Pendiente | 🔴 Alta | QA |
| SEC-12 | SQL Injection en búsqueda | 1. Buscar con SQL injection | `' OR '1'='1` | Query segura (ORM) | ⚪ Pendiente | 🔴 Alta | Dev |
| SEC-13 | Validar upload de archivos | 1. Intentar subir .exe | Archivo .exe | Error: "Tipo no permitido" | ⚪ Pendiente | 🔴 Alta | QA |
| SEC-14 | Validar tamaño máximo de archivo | 1. Subir imagen > 5MB | Archivo 10MB | Error: "Tamaño máximo 5MB" | ⚪ Pendiente | 🟡 Media | QA |
| SEC-15 | Path traversal en uploads | 1. Filename con ../ | `../../etc/passwd` | Filename sanitizado | ⚪ Pendiente | 🔴 Alta | Dev |

### 5.4 Encriptación

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| SEC-16 | Contraseñas hasheadas con Argon2 | 1. Crear usuario<br>2. Verificar en DB | Nueva contraseña | Hash Argon2 en DB | ⚪ Pendiente | 🔴 Alta | Dev |
| SEC-17 | Datos sensibles encriptados AES-256 | 1. Guardar datos sensibles<br>2. Verificar en DB | RUT, teléfono | Datos encriptados | ⚪ Pendiente | 🔴 Alta | Dev |
| SEC-18 | HTTPS en producción | 1. Acceder a sitio en Azure | URL http:// | Redirección a https:// | ⚪ Pendiente | 🔴 Alta | QA |
| SEC-19 | Cookies seguras (httpOnly, secure) | 1. Inspeccionar cookies | Después de login | Flags correctas | ⚪ Pendiente | 🔴 Alta | Dev |

---

## 6. PERFORMANCE

### 6.1 Tiempos de Respuesta

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| PERF-01 | Carga de página home | 1. Medir tiempo de carga | - | < 2 segundos | ⚪ Pendiente | 🟡 Media | QA |
| PERF-02 | Carga de lista de rifas | 1. Medir tiempo /raffles/ | 100 rifas | < 1.5 segundos | ⚪ Pendiente | 🟡 Media | QA |
| PERF-03 | API response time | 1. Medir endpoint /api/raffles/ | GET request | < 500ms | ⚪ Pendiente | 🟡 Media | Dev |
| PERF-04 | Tiempo de procesamiento de pago | 1. Medir checkout completo | Pago válido | < 3 segundos | ⚪ Pendiente | 🟡 Media | QA |
| PERF-05 | Carga de dashboard admin | 1. Medir carga inicial | Usuario admin | < 2 segundos | ⚪ Pendiente | 🟡 Media | QA |

### 6.2 Carga y Estrés

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| PERF-06 | 100 usuarios concurrentes | 1. Simular 100 usuarios simultáneos | JMeter/Locust | Sin errores<br>Respuesta < 3s | ⚪ Pendiente | 🟡 Media | Dev |
| PERF-07 | 500 usuarios concurrentes | 1. Simular 500 usuarios | JMeter/Locust | Max 5% errores<br>Respuesta < 5s | ⚪ Pendiente | 🟢 Baja | Dev |
| PERF-08 | Compra masiva de boletos | 1. 50 compras simultáneas a misma rifa | 50 requests paralelos | - Sin overselling<br>- Boletos correctos | ⚪ Pendiente | 🔴 Alta | Dev |
| PERF-09 | Upload masivo de imágenes | 1. Subir 10 imágenes simultáneas | 10 uploads paralelos | Todas procesadas correctamente | ⚪ Pendiente | 🟢 Baja | Dev |

### 6.3 Optimización

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| PERF-10 | Archivos estáticos comprimidos | 1. Verificar response headers | Request a /static/ | Content-Encoding: gzip | ⚪ Pendiente | 🟡 Media | Dev |
| PERF-11 | Imágenes optimizadas | 1. Verificar tamaño de imágenes | Imágenes de rifas | Comprimidas con Pillow | ⚪ Pendiente | 🟡 Media | Dev |
| PERF-12 | Queries N+1 optimizadas | 1. Verificar logs de queries | Vista con relaciones | select_related usado | ⚪ Pendiente | 🟡 Media | Dev |
| PERF-13 | Paginación en listas grandes | 1. Ver lista con 1000+ items | Lista de usuarios | Paginación activa | ⚪ Pendiente | 🟡 Media | QA |

---

## 7. INTEGRACIÓN

### 7.1 Email (SendGrid)

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| INT-01 | Email de confirmación de registro | 1. Registrar usuario | Email válido | Email recibido en < 1 min | ⚪ Pendiente | 🔴 Alta | QA |
| INT-02 | Email de recuperación de contraseña | 1. Solicitar reset | Email válido | Email con link recibido | ⚪ Pendiente | 🔴 Alta | QA |
| INT-03 | Email de confirmación de compra | 1. Completar compra | Pago exitoso | Email con boletos | ⚪ Pendiente | 🔴 Alta | QA |
| INT-04 | Email de notificación de ganador | 1. Ejecutar sorteo | Ganador seleccionado | Email al ganador | ⚪ Pendiente | 🔴 Alta | QA |
| INT-05 | Email de contraseña cambiada | 1. Cambiar password | Nueva contraseña | Email de confirmación | ⚪ Pendiente | 🟡 Media | QA |
| INT-06 | Template HTML correcto | 1. Verificar diseño email | Cualquier email | HTML responsive<br>Logos visibles | ⚪ Pendiente | 🟡 Media | QA |
| INT-07 | Manejo de error en SendGrid | 1. Simular fallo de SendGrid | API error | - Error logueado<br>- Usuario notificado | ⚪ Pendiente | 🟡 Media | Dev |

### 7.2 Pagos (Stripe)

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| INT-08 | Crear PaymentIntent | 1. Iniciar checkout | Monto válido | PaymentIntent creado | ⚪ Pendiente | 🔴 Alta | Dev |
| INT-09 | Confirmar pago | 1. Completar Stripe Elements | Tarjeta válida | Payment confirmed | ⚪ Pendiente | 🔴 Alta | QA |
| INT-10 | Procesar reembolso | 1. Solicitar refund | Pago completado | Refund processed | ⚪ Pendiente | 🔴 Alta | Dev |
| INT-11 | Webhook signature validation | 1. Recibir webhook | Signature válida | Webhook procesado | ⚪ Pendiente | 🔴 Alta | Dev |
| INT-12 | Manejo de error de Stripe | 1. Simular card_declined | Error de tarjeta | - Error capturado<br>- Usuario informado | ⚪ Pendiente | 🟡 Media | Dev |

### 7.3 Validación de Email (AbstractAPI)

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| INT-13 | Validar email con MX records | 1. Registrar con email válido | Email con MX válido | Validación aprobada | ⚪ Pendiente | 🟡 Media | QA |
| INT-14 | Rechazar email sin MX | 1. Registrar con dominio falso | Email sin MX | Error: "Email inválido" | ⚪ Pendiente | 🟡 Media | QA |
| INT-15 | Manejo de límite de API | 1. Exceder 100 validaciones/mes | Límite excedido | Fallback a validación básica | ⚪ Pendiente | 🟢 Baja | Dev |

---

## 8. REGRESIÓN

### 8.1 Flujos Críticos

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| REG-01 | Flujo completo: Registro → Login → Compra | 1. Registro<br>2. Confirmar email<br>3. Login<br>4. Comprar boletos<br>5. Pagar | Usuario nuevo completo | Todos los pasos exitosos | ⚪ Pendiente | 🔴 Alta | QA |
| REG-02 | Flujo organizador: Crear → Publicar → Sortear | 1. Crear rifa<br>2. Aprobar<br>3. Publicar<br>4. Vender boletos<br>5. Sortear | Organizador válido | Sorteo exitoso | ⚪ Pendiente | 🔴 Alta | QA |
| REG-03 | Flujo admin: Aprobar → Monitorear → Reportes | 1. Revisar rifa<br>2. Aprobar<br>3. Ver métricas<br>4. Exportar reporte | Admin | Todas las operaciones OK | ⚪ Pendiente | 🔴 Alta | QA |
| REG-04 | Flujo recuperación: Olvidé contraseña completo | 1. Solicitar reset<br>2. Recibir email<br>3. Click link<br>4. Nueva password<br>5. Login | Email registrado | Login exitoso con nueva pass | ⚪ Pendiente | 🔴 Alta | QA |
| REG-05 | Flujo reembolso: Extensión → Solicitud → Procesamiento | 1. Rifa extendida<br>2. Solicitar reembolso<br>3. Aprobar<br>4. Verificar fondos | Dentro de 48h | Reembolso completado | ⚪ Pendiente | 🔴 Alta | QA |

### 8.2 Compatibilidad de Navegadores

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| REG-06 | Chrome (última versión) | 1. Probar todos los flujos | Chrome 120+ | Funcionalidad completa | ⚪ Pendiente | 🔴 Alta | QA |
| REG-07 | Firefox (última versión) | 1. Probar todos los flujos | Firefox 120+ | Funcionalidad completa | ⚪ Pendiente | 🔴 Alta | QA |
| REG-08 | Safari (macOS/iOS) | 1. Probar todos los flujos | Safari 17+ | Funcionalidad completa | ⚪ Pendiente | 🟡 Media | QA |
| REG-09 | Edge (última versión) | 1. Probar todos los flujos | Edge 120+ | Funcionalidad completa | ⚪ Pendiente | 🟡 Media | QA |
| REG-10 | Mobile Chrome (Android) | 1. Probar en dispositivo móvil | Android 10+ | UI responsive | ⚪ Pendiente | 🔴 Alta | QA |
| REG-11 | Mobile Safari (iOS) | 1. Probar en iPhone | iOS 15+ | UI responsive | ⚪ Pendiente | 🔴 Alta | QA |

### 8.3 Responsive Design

| ID | Caso de Prueba | Pasos a Seguir | Datos de Entrada | Resultado Esperado | Estado | Prioridad | Responsable |
|----|----------------|----------------|------------------|-------------------|---------|-----------|-------------|
| REG-12 | Vista móvil (320px - 480px) | 1. Redimensionar a 320px | Smartphone pequeño | Layout correcto<br>Menú hamburguesa | ⚪ Pendiente | 🔴 Alta | QA |
| REG-13 | Vista tablet (768px - 1024px) | 1. Redimensionar a 768px | Tablet | Layout adaptado | ⚪ Pendiente | 🟡 Media | QA |
| REG-14 | Vista desktop (1920px+) | 1. Pantalla completa | Desktop HD | Layout aprovecha espacio | ⚪ Pendiente | 🟡 Media | QA |
| REG-15 | Orientación landscape móvil | 1. Rotar dispositivo | Landscape mode | Layout se adapta | ⚪ Pendiente | 🟢 Baja | QA |

---

## 📊 RESUMEN DE COBERTURA

### Por Módulo
- **Usuarios**: 27 casos
- **Rifas**: 26 casos
- **Pagos**: 15 casos
- **Administración**: 20 casos
- **Seguridad**: 19 casos
- **Performance**: 13 casos
- **Integración**: 15 casos
- **Regresión**: 15 casos

**TOTAL: 150 casos de prueba**

### Por Prioridad
- 🔴 **Alta**: 78 casos (52%)
- 🟡 **Media**: 56 casos (37%)
- 🟢 **Baja**: 16 casos (11%)

### Por Estado
- ⚪ **Pendiente**: 150 casos (100%)
- ✅ **Aprobado**: 0 casos
- ❌ **Fallido**: 0 casos
- 🔄 **En progreso**: 0 casos

---

## 🎯 CRITERIOS DE ACEPTACIÓN

### Criterios de Éxito
- ✅ 100% de casos **Alta prioridad** aprobados
- ✅ 95%+ de casos **Media prioridad** aprobados
- ✅ 0 errores críticos (bloquean funcionalidad core)
- ✅ < 5 errores menores (UI/UX)
- ✅ Performance dentro de límites establecidos
- ✅ Seguridad: 0 vulnerabilidades críticas

### Criterios de Rechazo
- ❌ Errores críticos en flujos principales
- ❌ Vulnerabilidades de seguridad alta/crítica
- ❌ Performance > 50% por encima de límites
- ❌ Rate de fallos > 1% en producción

---

## 🔄 PROCESO DE EJECUCIÓN

### Fase 1: Preparación (1 día)
1. Setup de ambiente de testing
2. Creación de datos de prueba
3. Configuración de herramientas (Selenium, Postman)
4. Revisión del plan con el equipo

### Fase 2: Ejecución Smoke Tests (2 días)
1. Ejecutar casos **Alta prioridad** críticos
2. Validar flujos principales
3. Reporte de blockers inmediatos

### Fase 3: Ejecución Completa (5 días)
1. Ejecutar todos los casos **Alta prioridad**
2. Ejecutar casos **Media prioridad**
3. Ejecutar casos **Baja prioridad**
4. Regression testing

### Fase 4: Re-testing (2 días)
1. Verificar bugs corregidos
2. Re-ejecutar casos fallidos
3. Validación final

### Fase 5: Reporte Final (1 día)
1. Consolidar resultados
2. Generar métricas
3. Recomendaciones
4. Sign-off

**Duración Total: 11 días hábiles**

---

## 🛠️ HERRAMIENTAS NECESARIAS

### Testing Manual
- Navegadores: Chrome, Firefox, Safari, Edge
- Dispositivos: iPhone, Android, Tablet
- Extensiones: ModHeader, JSONView, EditThisCookie

### Testing Automatizado
- **Selenium WebDriver**: Tests E2E
- **Pytest**: Unit tests Python
- **Postman/Newman**: API testing
- **JMeter/Locust**: Load testing

### Gestión y Reporte
- **Jira/Trello**: Tracking de bugs
- **TestRail**: Gestión de casos
- **Allure/HTML Reports**: Reportes visuales

---

## 📝 PLANTILLA DE REPORTE DE BUG

```markdown
**ID**: BUG-XXX
**Título**: [Breve descripción del bug]
**Severidad**: Crítica / Alta / Media / Baja
**Prioridad**: Alta / Media / Baja
**Módulo**: [Usuarios/Rifas/Pagos/etc]
**Ambiente**: [Desarrollo/Staging/Producción]

**Pasos para Reproducir**:
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

**Resultado Esperado**: [Qué debería pasar]
**Resultado Actual**: [Qué está pasando]

**Evidencia**: [Screenshots/Videos/Logs]
**Navegador/OS**: [Chrome 120 / Windows 11]
**Asignado a**: [Developer]
**Estado**: [Nuevo/En progreso/Resuelto/Cerrado]
```

---

## ✅ CHECKLIST PRE-DEPLOYMENT

Antes de aprobar el deployment a producción:

- [ ] Todos los casos **Alta prioridad** aprobados
- [ ] 95%+ casos **Media prioridad** aprobados
- [ ] 0 bugs críticos abiertos
- [ ] < 3 bugs menores abiertos
- [ ] Performance tests aprobados
- [ ] Security scan aprobado (0 critical/high)
- [ ] Load testing aprobado (500 usuarios)
- [ ] Backup y rollback plan documentado
- [ ] Monitoreo configurado en Azure
- [ ] Logs configurados correctamente
- [ ] Documentación actualizada
- [ ] Sign-off de Product Owner
- [ ] Sign-off de Tech Lead
- [ ] Sign-off de QA Lead

---

## 📞 CONTACTOS

**QA Lead**: [Nombre]  
**Tech Lead**: [Nombre]  
**Product Owner**: [Nombre]  
**DevOps**: [Nombre]

---

**Documento creado**: Diciembre 3, 2025  
**Última actualización**: Diciembre 3, 2025  
**Versión**: 1.0  
**Estado**: ✅ Aprobado para uso
