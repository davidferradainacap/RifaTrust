# Sistema de Aprobación de Rifas

## 📋 Descripción General

Se ha implementado un sistema completo de aprobación administrativa para la creación de rifas. Los organizadores deben solicitar aprobación antes de poder activar sus rifas.

## 🔄 Flujo de Estados

```
┌─────────────┐
│  Borrador   │ (Organizador puede editar)
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│ Pendiente Aprobación │ (Esperando revisión admin)
└──────┬───────────────┘
       │
       ├─────────► ✅ Aprobada (Admin aprueba)
       │           └──► Activa (Organizador activa)
       │
       └─────────► ❌ Rechazada (Admin rechaza)
                   └──► Borrador (Organizador corrige)
```

## 👥 Roles y Permisos

### Organizador
- **Puede crear** rifas en estado "Borrador"
- **Puede solicitar** aprobación (cambia a "Pendiente de Aprobación")
- **NO puede** activar directamente sin aprobación administrativa
- **Puede activar** rifas aprobadas

### Administrador
- **Revisa** todas las rifas pendientes
- **Aprueba** o **Rechaza** rifas con comentarios
- **Notifica** al organizador de la decisión
- **Registra** auditoría de todas las decisiones

## 🛠️ Implementación Técnica

### 1. Modelo (apps/raffles/models.py)

#### Nuevos Estados:
```python
ESTADO_CHOICES = (
    ('borrador', 'Borrador'),
    ('pendiente_aprobacion', 'Pendiente de Aprobación'),  # NUEVO
    ('aprobada', 'Aprobada'),  # NUEVO
    ('rechazada', 'Rechazada'),  # NUEVO
    ('activa', 'Activa'),
    ('pausada', 'Pausada - En Revisión'),
    ('cerrada', 'Cerrada'),
    ('finalizada', 'Finalizada'),
    ('cancelada', 'Cancelada'),
)
```

#### Campos de Aprobación:
```python
# Sistema de Aprobación
fecha_solicitud = models.DateTimeField(null=True, blank=True)
revisado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rifas_revisadas')
fecha_revision_aprobacion = models.DateTimeField(null=True, blank=True)
comentarios_revision = models.TextField(blank=True, null=True)
motivo_rechazo = models.TextField(blank=True, null=True)
```

### 2. Formulario (apps/raffles/forms.py)

#### Lógica de Estados:
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    # Si la rifa está aprobada, permitir activarla
    if self.instance.pk and self.instance.estado == 'aprobada':
        self.fields['estado'].choices = [
            ('aprobada', 'Aprobada (en espera)'),
            ('activa', 'Activar Rifa'),
        ]
    else:
        self.fields['estado'].choices = [
            ('borrador', 'Borrador'),
            ('pendiente_aprobacion', 'Solicitar Aprobación'),
        ]
```

### 3. Vistas de Organizador (apps/raffles/views.py)

#### Creación con Solicitud de Aprobación:
```python
@login_required
def create_raffle_view(request):
    if request.method == 'POST':
        form = RaffleForm(request.POST, request.FILES)
        if form.is_valid():
            raffle = form.save(commit=False)
            raffle.organizador = request.user
            
            if raffle.estado == 'pendiente_aprobacion':
                raffle.fecha_solicitud = timezone.now()
                
                # Notificar a los administradores
                admins = User.objects.filter(rol='admin')
                for admin in admins:
                    Notification.objects.create(
                        usuario=admin,
                        tipo='admin',
                        titulo='Nueva rifa pendiente de aprobación',
                        mensaje=f'El organizador {request.user.nombre} ha solicitado aprobación para la rifa "{raffle.titulo}".',
                        enlace='/admin-panel/rifas-pendientes/'
                    )
            
            raffle.save()
            
            if raffle.estado == 'pendiente_aprobacion':
                messages.success(request, '¡Rifa enviada a revisión! Los administradores la revisarán pronto.')
            else:
                messages.success(request, '¡Rifa guardada como borrador!')
            
            return redirect('raffles:organizer_dashboard')
```

### 4. Vistas de Administrador (apps/admin_panel/views.py)

#### Vista de Rifas Pendientes:
```python
@login_required
@user_passes_test(is_admin)
def rifas_pendientes_view(request):
    """Vista para mostrar rifas pendientes de aprobación"""
    rifas_pendientes = Raffle.objects.filter(estado='pendiente_aprobacion').select_related('organizador').order_by('-fecha_solicitud')
    
    context = {
        'rifas_pendientes': rifas_pendientes,
        'total_pendientes': rifas_pendientes.count()
    }
    
    return render(request, 'admin_panel/rifas_pendientes.html', context)
```

#### Vista de Revisión (Aprobar/Rechazar):
```python
@login_required
@user_passes_test(is_admin)
def revisar_rifa_pendiente(request, rifa_id):
    """Vista para aprobar o rechazar una rifa pendiente"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        rifa = get_object_or_404(Raffle, id=rifa_id, estado='pendiente_aprobacion')
        accion = request.POST.get('accion')
        comentarios = request.POST.get('comentarios', '')
        
        if accion == 'aprobar':
            rifa.estado = 'aprobada'
            rifa.revisado_por = request.user
            rifa.fecha_revision_aprobacion = timezone.now()
            rifa.comentarios_revision = comentarios
            rifa.save()
            
            # Notificar al organizador
            Notification.objects.create(
                usuario=rifa.organizador,
                tipo='aprobacion',
                titulo='¡Tu rifa ha sido aprobada!',
                mensaje=f'Tu rifa "{rifa.titulo}" ha sido aprobada por {request.user.nombre}. Ahora puedes activarla para que sea visible al público.',
                enlace=f'/raffles/{rifa.id}/edit/',
                rifa_relacionada=rifa
            )
            
            # Registrar en el log de auditoría
            AuditLog.objects.create(
                usuario=request.user,
                accion='aprobar_rifa',
                modelo='Raffle',
                objeto_id=rifa.id,
                descripcion=f'Rifa "{rifa.titulo}" aprobada. Comentarios: {comentarios}'
            )
            
        elif accion == 'rechazar':
            motivo = request.POST.get('motivo_rechazo', '')
            
            rifa.estado = 'rechazada'
            rifa.revisado_por = request.user
            rifa.fecha_revision_aprobacion = timezone.now()
            rifa.motivo_rechazo = motivo
            rifa.comentarios_revision = comentarios
            rifa.save()
            
            # Notificar al organizador
            Notification.objects.create(
                usuario=rifa.organizador,
                tipo='rechazo',
                titulo='Tu rifa ha sido rechazada',
                mensaje=f'Tu rifa "{rifa.titulo}" ha sido rechazada. Motivo: {motivo}. Por favor revisa los comentarios y corrige los problemas.',
                enlace=f'/raffles/{rifa.id}/edit/',
                rifa_relacionada=rifa
            )
            
            # Registrar en el log de auditoría
            AuditLog.objects.create(
                usuario=request.user,
                accion='rechazar_rifa',
                modelo='Raffle',
                objeto_id=rifa.id,
                descripcion=f'Rifa "{rifa.titulo}" rechazada. Motivo: {motivo}. Comentarios: {comentarios}'
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Revisión completada exitosamente',
            'redirect': '/admin-panel/rifas-pendientes/'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
```

### 5. URLs (apps/admin_panel/urls.py)

```python
# Rifas Pendientes de Aprobación
path('rifas-pendientes/', views.rifas_pendientes_view, name='rifas_pendientes'),
path('rifas-pendientes/<int:rifa_id>/revisar/', views.revisar_rifa_pendiente, name='revisar_pendiente'),
```

### 6. Plantilla (templates/admin_panel/rifas_pendientes.html)

#### Características:
- **Lista de rifas pendientes** con información completa
- **Visualización de documento legal** para revisión
- **Botones de Aprobar/Rechazar** con modales
- **Formularios con campos de comentarios**
- **Notificación al organizador** automática
- **Registro en auditoría** de todas las acciones

### 7. Dashboard Admin (templates/admin_panel/dashboard.html)

#### Alerta de Rifas Pendientes:
```html
{% if rifas_pendientes_aprobacion > 0 %}
<div class="row mb-4">
    <div class="col-12">
        <div class="alert" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(99, 102, 241, 0.2)); border: 2px solid #6366f1; border-radius: 12px; padding: 1.5rem;">
            <div class="d-flex align-items-center">
                <div style="font-size: 3rem; margin-right: 1.5rem;">🔍</div>
                <div class="flex-grow-1">
                    <h5 style="color: #312e81; font-weight: 700; margin-bottom: 0.5rem;">
                        {{ rifas_pendientes_aprobacion }} Rifa{{ rifas_pendientes_aprobacion|pluralize }} Pendiente{{ rifas_pendientes_aprobacion|pluralize }} de Aprobación
                    </h5>
                    <p style="color: #3730a3; margin-bottom: 0;">
                        Organizadores han solicitado aprobación para publicar nuevas rifas. Se requiere revisión administrativa.
                    </p>
                </div>
                <a href="{% url 'admin_panel:rifas_pendientes' %}" class="btn" style="background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; font-weight: 600; padding: 0.75rem 2rem; border-radius: 8px; text-decoration: none; white-space: nowrap;">
                    Revisar Solicitudes →
                </a>
            </div>
        </div>
    </div>
</div>
{% endif %}
```

### 8. Dashboard Organizador (templates/raffles/organizer_dashboard.html)

#### Estados Visuales:
```html
{% if rifa.estado == 'aprobada' %}
<span style="background: rgba(34, 197, 94, 0.15); color: rgb(34, 197, 94);">✅ Aprobada</span>
{% elif rifa.estado == 'pendiente_aprobacion' %}
<span style="background: rgba(99, 102, 241, 0.15); color: rgb(99, 102, 241);">🔍 En Revisión</span>
{% elif rifa.estado == 'rechazada' %}
<span style="background: rgba(239, 68, 68, 0.15); color: rgb(239, 68, 68);">❌ Rechazada</span>
{% endif %}
```

### 9. Formulario de Edición (templates/raffles/edit.html)

#### UI Especial para Rifas Aprobadas:
```html
{% if raffle.estado == 'aprobada' %}
<!-- Mensaje de aprobación -->
<div style="background: rgba(34, 197, 94, 0.1); border: 2px solid rgba(34, 197, 94, 0.3);">
    <div style="font-size: 3rem;">✅</div>
    <div style="font-weight: 700; color: #10b981;">¡Rifa Aprobada!</div>
    <div>Tu rifa ha sido revisada y aprobada por el equipo administrativo.</div>
</div>

<!-- Opciones: Mantener Aprobada o Activar -->
<input type="radio" name="estado" value="aprobada" checked>
<div>Mantener Aprobada (Aún oculta al público)</div>

<input type="radio" name="estado" value="activa">
<div>🚀 Activar Rifa (Publicar para la venta de boletos)</div>
{% endif %}
```

## 🎯 Características del Sistema

### ✅ Aprobación
- Admin revisa toda la información de la rifa
- Verifica el documento legal
- Puede agregar comentarios para el organizador
- Notificación automática al organizador
- Registro en log de auditoría

### ❌ Rechazo
- Campo obligatorio para motivo del rechazo
- Comentarios adicionales opcionales
- Notificación detallada al organizador
- Rifa vuelve a estado "rechazada"
- Organizador puede corregir y volver a solicitar

### 🔔 Notificaciones
- **Al solicitar aprobación**: Todos los admins reciben notificación
- **Al aprobar**: Organizador recibe confirmación y puede activar
- **Al rechazar**: Organizador recibe motivo y puede corregir

### 📊 Auditoría
- Todas las aprobaciones quedan registradas
- Todos los rechazos quedan registrados
- Incluye: quién revisó, cuándo, y comentarios
- Visible en panel de auditoría

## 🔒 Seguridad

### Validaciones:
- Solo organizadores pueden crear rifas
- Solo admins pueden aprobar/rechazar
- No se puede activar sin aprobación previa
- No se puede cambiar estado sin permisos
- Documento legal obligatorio

### Trazabilidad:
- Fecha de solicitud registrada
- Admin que revisó registrado
- Fecha de revisión registrada
- Comentarios y motivos guardados
- Logs de auditoría completos

## 📝 Uso del Sistema

### Para Organizadores:

1. **Crear Rifa**
   - Completar todos los campos obligatorios
   - Subir documento legal (PDF/Word/Imagen, max 10MB)
   - Seleccionar "Solicitar Aprobación"
   - Enviar formulario

2. **Esperar Revisión**
   - Recibirás notificación cuando sea revisada
   - Estado: "🔍 En Revisión"

3. **Si es Aprobada**
   - Recibirás notificación con comentarios
   - Editar rifa y cambiar estado a "Activa"
   - Estado: "✅ Aprobada" → "🚀 Activa"

4. **Si es Rechazada**
   - Recibirás notificación con motivo
   - Revisar comentarios y corregir
   - Volver a solicitar aprobación
   - Estado: "❌ Rechazada" → Corregir → "🔍 En Revisión"

### Para Administradores:

1. **Revisar Notificaciones**
   - Recibirás notificación por cada nueva solicitud
   - Click en "Revisar Solicitudes" en el dashboard

2. **Evaluar Rifa**
   - Ver toda la información de la rifa
   - Descargar y revisar documento legal
   - Verificar coherencia de datos

3. **Aprobar**
   - Click en "✅ Aprobar"
   - Agregar comentarios (opcional)
   - Confirmar aprobación

4. **Rechazar**
   - Click en "❌ Rechazar"
   - Escribir motivo del rechazo (obligatorio)
   - Agregar comentarios adicionales (opcional)
   - Confirmar rechazo

## 📍 URLs del Sistema

- **Rifas Pendientes**: `/admin-panel/rifas-pendientes/`
- **Revisar Rifa**: `/admin-panel/rifas-pendientes/<id>/revisar/`
- **Dashboard Admin**: `/admin-panel/dashboard/`
- **Dashboard Organizador**: `/raffles/organizer-dashboard/`
- **Editar Rifa**: `/raffles/<id>/edit/`

## 🗂️ Archivos Modificados

1. `apps/raffles/models.py` - Nuevos estados y campos de aprobación
2. `apps/raffles/forms.py` - Lógica de estados permitidos
3. `apps/raffles/views.py` - Notificaciones en creación/edición
4. `apps/admin_panel/views.py` - Vistas de revisión
5. `apps/admin_panel/urls.py` - URLs de rifas pendientes
6. `templates/admin_panel/rifas_pendientes.html` - Template de revisión
7. `templates/admin_panel/dashboard.html` - Alerta de pendientes
8. `templates/raffles/edit.html` - UI para rifas aprobadas
9. `templates/raffles/organizer_dashboard.html` - Estados visuales
10. `apps/raffles/migrations/0007_add_sistema_aprobacion.py` - Migración

## ✨ Beneficios

1. **Control de Calidad**: Todas las rifas son revisadas antes de publicarse
2. **Cumplimiento Legal**: Verificación del documento legal obligatorio
3. **Transparencia**: Trazabilidad completa de decisiones
4. **Comunicación**: Notificaciones automáticas bidireccionales
5. **Auditoría**: Logs completos de todas las acciones
6. **Experiencia de Usuario**: UI clara con estados visuales

---

**Implementado**: Noviembre 2025
**Versión**: Django 5.0
**Estado**: ✅ Completo y Funcional
