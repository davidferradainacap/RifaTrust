# 📋 Términos y Condiciones - Documentación de Implementación

**Fecha de implementación**: Diciembre 2025  
**Versión**: 2.0  
**Estado**: ✅ Implementado y Funcionando

---

## 📋 RESUMEN DE IMPLEMENTACIÓN

Se ha implementado un sistema completo de términos y condiciones para el registro de usuarios en RifaTrust, con las siguientes características:

### ✅ Características Implementadas

1. **Campo obligatorio** en el formulario de registro
2. **Modal interactivo** con todos los términos completos
3. **Enlace clickeable** en "Términos y Condiciones"
4. **Aceptación explícita** mediante checkbox
5. **Validación del servidor** - no permite registro sin aceptar
6. **Diseño responsive** - funciona en móvil y desktop
7. **Animaciones profesionales** - transiciones suaves

### 🆕 NUEVAS SECCIONES AGREGADAS

#### 📦 Sección 6: Almacenamiento y Custodia de Premios Físicos
- **Almacenamiento obligatorio** de todos los premios físicos en instalaciones de RifaTrust
- **Verificación previa** del premio antes de activar la rifa
- **Custodia segura** con seguridad 24/7, seguros y control de acceso
- **Certificado de custodia** con documentación fotográfica/videográfica
- **Requisitos específicos** por tipo de premio (vehículos, electrónicos, joyas)
- **Acta de entrega** firmada por el organizador

#### 🏆 Sección 8: Retiro y Entrega de Premios Físicos
- **Retiro obligatorio en instalaciones** - no hay envíos a domicilio
- **Proceso de retiro detallado** paso a paso (8 pasos)
- **Documentación requerida** para retirar el premio
- **Plazo de 30 días** para retirar el premio
- **Retiro por terceros** mediante carta poder notariada
- **Responsabilidad de transporte** del ganador
- **Ubicación y horarios** de retiro especificados

---

## 🎯 POLÍTICA DE REEMBOLSOS CLAVE

### ✅ SE OTORGA REEMBOLSO EN:

1. **Extensión de plazo de la rifa** ⭐ (REQUERIMIENTO PRINCIPAL)
   - Si el organizador extiende la fecha de finalización después de la fecha original
   - El usuario tiene **48 horas** para solicitar el reembolso
   - Se reembolsa el **100%** del monto pagado

2. **Cancelación de rifa**
   - Reembolso automático del 100%

3. **Cambios sustanciales en premios**
   - Reducción del valor en más del 30%

4. **Error técnico**
   - Problemas del sistema que afectaron la compra

5. **Fraude comprobado**
   - Actividad fraudulenta del organizador

### ❌ NO SE OTORGA REEMBOLSO EN:

- Cambiar de opinión después de la compra
- No resultar ganador en el sorteo
- Desacuerdo con resultado del sorteo
- No poder asistir a entrega del premio
- Después de realizado el sorteo
- Más de 48 horas después del cambio de fechas

---

## 🛠️ ARCHIVOS MODIFICADOS

### 1. Backend - Formulario de Registro

**Archivo**: `backend/apps/users/forms.py`

```python
# Nuevo campo agregado
aceptar_terminos = forms.BooleanField(
    required=True,
    widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input'
    }),
    error_messages={
        'required': 'Debes aceptar los términos y condiciones para registrarte'
    },
    help_text='He leído y acepto los términos y condiciones'
)
```

**Funcionalidad**:
- Campo booleano obligatorio (`required=True`)
- Validación en el servidor
- Mensaje de error personalizado
- Widget checkbox con clases Bootstrap

### 2. Frontend - Template de Registro

**Archivo**: `frontend/templates/users/register.html`

#### Cambios realizados:

1. **Checkbox de aceptación**
```html
<div class="form-group">
    <div class="form-check">
        {{ form.aceptar_terminos }}
        <label class="form-check-label" for="...">
            He leído y acepto los 
            <a href="#" id="openTerms" onclick="openTermsModal(event)">
                Términos y Condiciones
            </a>
        </label>
    </div>
    {% if form.aceptar_terminos.errors %}
        <div class="form-error">{{ form.aceptar_terminos.errors.0 }}</div>
    {% endif %}
</div>
```

2. **Modal completo con términos**
- Overlay con blur effect
- Container scrollable
- 14 secciones completas de términos
- Diseño profesional con gradientes
- Sección especial destacada para política de reembolsos
- Botones de acción (Cerrar, Aceptar y Continuar)

3. **JavaScript para manejo del modal**
```javascript
// Funciones implementadas
openTermsModal(event)     // Abre el modal
closeTermsModal()         // Cierra el modal
acceptTermsAndClose()     // Acepta y cierra (marca checkbox)

// Event listeners
- Click fuera del modal → cierra
- Tecla ESC → cierra
```

---

## 📐 ESTRUCTURA DEL MODAL

### Secciones de Términos y Condiciones:

1. **Aceptación de los Términos**
   - Vinculación legal
   - Derecho a modificar términos

2. **Descripción del Servicio**
   - Qué ofrece RifaTrust
   - Funcionalidades principales

3. **Requisitos de Usuario**
   - Mayor de 18 años
   - Información precisa
   - Responsabilidad de cuenta

4. **Compra de Boletos y Pagos**
   - Proceso de compra (15 minutos)
   - Integración con Stripe
   - Precios y comisiones

5. **💰 Política de Reembolsos** ⭐
   - Casos de reembolso (con énfasis en extensión de plazo)
   - Casos sin reembolso
   - Proceso de solicitud

6. **📦 Almacenamiento y Custodia de Premios Físicos** ⭐ NUEVO
   - Almacenamiento obligatorio en instalaciones de RifaTrust
   - Verificación y certificación de premios
   - Seguridad 24/7 y seguros
   - Requisitos para almacenamiento
   - Premios NO almacenables

7. **🎲 Sistema de Sorteos**
   - Sorteo verificable SHA-256
   - Acta digital
   - Selección de ganadores

8. **🏆 Retiro y Entrega de Premios Físicos** ⭐ NUEVO
   - Retiro obligatorio en instalaciones
   - Proceso de retiro paso a paso
   - Documentación requerida
   - Retiro por terceros
   - Plazo de 30 días
   - Responsabilidad de transporte

9. **Responsabilidades del Organizador**
   - Información veraz
   - Entrega de premios a RifaTrust
   - Cumplimiento de fechas

10. **Propiedad Intelectual**
    - Derechos de RifaTrust
    - Licencias de contenido

11. **Privacidad y Protección de Datos**
    - Encriptación AES-256
    - Uso de datos
    - Cumplimiento GDPR

12. **Limitación de Responsabilidad**
    - Rol de intermediario
    - Exclusiones de responsabilidad

13. **Suspensión y Terminación**
    - Causas de suspensión
    - Cierre voluntario de cuenta

14. **Modificaciones del Servicio**
    - Derecho a cambios
    - Notificación de cambios

15. **Ley Aplicable y Jurisdicción**
    - Leyes aplicables
    - Resolución de disputas

16. **📧 Contacto y Soporte**
    - Email de soporte
    - Tiempos de respuesta

---

## 🎨 ESTILOS CSS

### Estilos del Modal

```css
.modal-overlay {
    position: fixed;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(8px);
    z-index: 9999;
    animation: fadeIn 0.3s ease;
}

.modal-container {
    background: linear-gradient(135deg, rgba(30, 30, 50, 0.98) 0%, rgba(20, 20, 40, 0.98) 100%);
    border-radius: 1rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(147, 51, 234, 0.3);
    max-width: 900px;
    max-height: 85vh;
}
```

### Características del diseño:

- ✅ Fondo oscuro con blur
- ✅ Container con gradiente
- ✅ Scroll interno personalizado
- ✅ Animaciones de entrada/salida
- ✅ Responsive (95vw en móvil)
- ✅ Colores consistentes con el tema

---

## 🔒 VALIDACIÓN Y SEGURIDAD

### Validación del Servidor

```python
# En forms.py
aceptar_terminos = forms.BooleanField(
    required=True,  # ← Campo obligatorio
    error_messages={
        'required': 'Debes aceptar los términos y condiciones para registrarte'
    }
)
```

### Flujo de Validación

1. **Cliente (JavaScript)**
   - Usuario debe marcar el checkbox manualmente
   - No se puede enviar el formulario sin aceptar

2. **Servidor (Django)**
   - Valida que `aceptar_terminos=True`
   - Si es `False` o no existe → error
   - Bloquea el registro

3. **Mensaje de Error**
   - Se muestra en rojo debajo del checkbox
   - Texto: "Debes aceptar los términos y condiciones para registrarte"

---

## 📱 RESPONSIVE DESIGN

### Desktop (> 768px)
- Modal: 900px de ancho máximo
- 85vh de alto máximo
- Padding: 2rem

### Mobile (≤ 768px)
- Modal: 95vw de ancho
- 90vh de alto máximo
- Padding: 1.5rem
- Título más pequeño (1.35rem)
- Secciones ajustadas

---

## 🧪 TESTING

### Casos de Prueba

#### ✅ Test 1: Registro sin aceptar términos
```
1. Ir a /register/
2. Llenar todos los campos
3. NO marcar checkbox de términos
4. Click en "Crear Cuenta"
5. Resultado esperado: Error "Debes aceptar los términos..."
```

#### ✅ Test 2: Abrir modal de términos
```
1. Ir a /register/
2. Click en "Términos y Condiciones"
3. Resultado esperado: Modal se abre
4. Verificar scroll funciona
5. Verificar botón "Cerrar" funciona
6. Verificar ESC cierra el modal
```

#### ✅ Test 3: Aceptar desde el modal
```
1. Abrir modal
2. Leer términos (scroll hasta abajo)
3. Click en "✓ Aceptar y Continuar"
4. Resultado esperado: 
   - Modal se cierra
   - Checkbox queda marcado
```

#### ✅ Test 4: Registro exitoso con términos
```
1. Llenar formulario completo
2. Marcar checkbox de términos (o aceptar desde modal)
3. Click en "Crear Cuenta"
4. Resultado esperado: Registro exitoso
```

---

## 🚀 DEPLOYMENT

### Archivos a Subir a Azure

```
backend/apps/users/forms.py                    # ← Campo nuevo
frontend/templates/users/register.html         # ← Modal + checkbox
requirements.txt                               # ← Dependencias actualizadas
```

### Comandos Post-Deployment

```bash
# 1. SSH a Azure
az webapp ssh --name rifatrust

# 2. Activar entorno virtual (si aplica)
source /home/site/wwwroot/.venv/bin/activate

# 3. Instalar nuevas dependencias
pip install -r requirements.txt

# 4. NO requiere migraciones (no hay cambios en DB)

# 5. Restart del app (automático)
```

**Nota**: No se requieren migraciones porque el campo `aceptar_terminos` es solo de formulario, no se guarda en la base de datos.

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs a Monitorear

1. **Tasa de apertura del modal**
   - % de usuarios que hacen click en "Términos y Condiciones"

2. **Tasa de aceptación**
   - % de usuarios que aceptan desde el modal vs manual

3. **Tasa de abandono**
   - % de usuarios que abandonan después de leer términos

4. **Errores de validación**
   - Cantidad de intentos de registro sin aceptar

### Agregar Analytics (Futuro)

```javascript
// Ejemplo con Google Analytics
function openTermsModal(event) {
    event.preventDefault();
    gtag('event', 'modal_opened', {
        'event_category': 'terms',
        'event_label': 'registration'
    });
    // ... resto del código
}
```

---

## 🔄 MANTENIMIENTO

### Actualizar Términos y Condiciones

1. Editar archivo: `frontend/templates/users/register.html`
2. Buscar sección: `<!-- Modal de Términos y Condiciones -->`
3. Modificar contenido del modal
4. Actualizar fecha: "Última actualización: [fecha]"
5. Incrementar versión: "Versión: [número]"
6. Deploy cambios

### Notificar Cambios a Usuarios

Si los términos cambian sustancialmente:
1. Enviar email masivo a usuarios registrados
2. Agregar notificación en el dashboard
3. (Opcional) Requerir aceptación de nuevos términos al login

---

## ❓ FAQ - Preguntas Frecuentes

### ¿El campo se guarda en la base de datos?
No, el campo `aceptar_terminos` es solo de validación en el formulario. No se crea una columna en la tabla User. Se valida solo al momento del registro.

### ¿Puedo personalizar los términos?
Sí, edita el contenido dentro del `<div class="modal-body">` en `register.html`.

### ¿Se puede omitir la validación?
No recomendado. Para development, puedes hacer el campo `required=False` temporalmente, pero NUNCA en producción.

### ¿Cómo traduzco los términos?
1. Crea templates diferentes por idioma
2. O usa Django i18n con `{% trans "..." %}`
3. Detecta idioma del usuario con `request.LANGUAGE_CODE`

### ¿Funciona en modo API (JSON)?
El campo actual es solo para formulario web. Para API, necesitas:
```python
# En serializer
aceptar_terminos = serializers.BooleanField(required=True)
```

---

## 📝 CHANGELOG

### Versión 2.0 (Diciembre 2025)

**Agregado**:
- ✅ Campo `aceptar_terminos` en RegisterForm
- ✅ Modal completo de términos y condiciones
- ✅ 14 secciones de términos legales
- ✅ Política de reembolsos destacada
- ✅ JavaScript para manejo del modal
- ✅ CSS responsive para el modal
- ✅ Validación obligatoria del servidor
- ✅ Animaciones de apertura/cierre

**Modificado**:
- 📝 `forms.py` - Agregado campo booleano
- 📝 `register.html` - Agregado modal y checkbox
- 📝 `requirements.txt` - Actualizadas versiones

**Dependencias nuevas**:
- `djangorestframework-simplejwt==5.5.1`
- `drf-spectacular==0.29.0`
- `PyJWT==2.10.1`
- `PyYAML==6.0.3`
- `jsonschema==4.25.1`

---

## 🎯 CUMPLIMIENTO DEL REQUERIMIENTO

### ✅ Requisitos Solicitados

1. ✅ **Campo checkbox en registro** - Implementado
2. ✅ **Enlace clickeable** - "Términos y Condiciones" abre modal
3. ✅ **Ventana emergente (modal)** - Implementado con diseño profesional
4. ✅ **Términos completos** - 14 secciones detalladas
5. ✅ **Política de reembolso específica** - Sección destacada que incluye:
   - ✅ Reembolso por extensión de plazo de rifa
   - ✅ Plazo de 48 horas para solicitar
   - ✅ Casos de reembolso y casos sin reembolso
   - ✅ Proceso de solicitud detallado

---

## 📧 SOPORTE

Para preguntas sobre esta implementación:
- **Email**: soporte@rifatrust.com
- **Repositorio**: https://github.com/davidferradainacap/RifaTrust
- **Documentación**: Ver `DOCUMENTACION_COMPLETA.md`

---

**Implementado por**: RifaTrust Development Team  
**Fecha**: Diciembre 2025  
**Estado**: ✅ Producción Ready
