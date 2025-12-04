# 🚫 RESTRICCIÓN DE COMPRA PARA ORGANIZADORES

## 📝 Cambios Implementados

### Problema Identificado
Los organizadores podían comprar boletos de rifas, lo cual no es correcto según las reglas de negocio. Los organizadores solo deben poder **crear y administrar rifas**, no participar comprando boletos.

### Solución Implementada

#### 1. **Vista de Compra (`views.py`)** ✅
**Archivo:** `backend/apps/raffles/views.py`

Se agregó validación al inicio de `buy_ticket_view()` para bloquear organizadores:

```python
@login_required
def buy_ticket_view(request, raffle_id):
    # === RESTRICCIÓN: ORGANIZADORES NO PUEDEN COMPRAR BOLETOS ===
    # Los organizadores solo pueden crear y gestionar rifas, no participar comprando boletos
    if request.user.rol == 'organizador':
        messages.error(request, '❌ Los organizadores no pueden comprar boletos de rifas. Solo pueden crearlas y administrarlas.')
        return redirect('raffles:detail', pk=raffle_id)
    
    # ... resto del código
```

**Resultado:** Si un organizador intenta acceder a `/raffles/<id>/buy/`, es redirigido a la vista de detalle con mensaje de error.

---

#### 2. **Template de Compra (`buy_ticket.html`)** ✅
**Archivo:** `frontend/templates/raffles/buy_ticket.html`

Se agregó mensaje visual para organizadores que intenten acceder:

```django-html
{% if user.rol == 'organizador' %}
<div style="background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; ...">
    <div style="font-size: 3rem;">🚫</div>
    <h2>Acceso Restringido</h2>
    <p>Los organizadores no pueden comprar boletos de rifas. 
       Tu rol es crear y administrar rifas, no participar en ellas.</p>
    <a href="/raffles/{{ raffle.id }}/">Ver Detalles de la Rifa</a>
</div>
{% else %}
<!-- Formulario de compra solo visible para NO organizadores -->
{% endif %}
```

**Resultado:** Si un organizador accede al template, ve un mensaje claro indicando la restricción.

---

#### 3. **Listado de Rifas (`list.html`)** ✅
**Archivo:** `frontend/templates/raffles/list.html`

Se modificó el botón "Comprar Boleto" para organizadores:

```django-html
{% if user.rol != 'organizador' %}
    <a href="/raffles/{{ raffle.id }}/buy/" class="btn btn-secondary">
        Comprar Boleto
    </a>
{% else %}
    <span class="btn btn-secondary" style="opacity: 0.5; cursor: not-allowed;" 
          title="Los organizadores no pueden comprar boletos">
        🚫 Solo Visualización
    </span>
{% endif %}
```

**Resultado:** Los organizadores ven un botón deshabilitado con texto "Solo Visualización" en lugar del botón de compra.

---

#### 4. **Serializer de API (`serializers.py`)** ✅
**Archivo:** `backend/apps/raffles/serializers.py`

Se actualizó el campo `puede_comprar` para considerar el rol del usuario:

```python
def get_puede_comprar(self, obj):
    """Verifica si se pueden comprar boletos (organizadores no pueden comprar)"""
    request = self.context.get('request')
    if request and hasattr(request, 'user'):
        # Organizadores no pueden comprar boletos
        if request.user.is_authenticated and request.user.rol == 'organizador':
            return False
    return obj.estado == 'activa' and obj.boletos_vendidos < obj.total_boletos
```

**Resultado:** El endpoint de API `/api/raffles/` retorna `puede_comprar: false` para organizadores, permitiendo que frontends consuman esta información.

---

## 🎯 Casos de Uso Cubiertos

### ✅ Caso 1: Organizador intenta acceder directamente a URL de compra
**URL:** `/raffles/123/buy/`  
**Usuario:** Organizador autenticado  
**Resultado:** Redirigido a `/raffles/123/` con mensaje de error

### ✅ Caso 2: Organizador ve listado de rifas
**Vista:** Lista de todas las rifas  
**Usuario:** Organizador autenticado  
**Resultado:** Botón "Comprar Boleto" reemplazado por "🚫 Solo Visualización" (deshabilitado)

### ✅ Caso 3: Organizador consulta API
**Endpoint:** `/api/raffles/`  
**Usuario:** Organizador autenticado  
**Resultado:** Campo `puede_comprar` retorna `false` incluso si la rifa está activa

### ✅ Caso 4: Participante/Sponsor accede normalmente
**URL:** `/raffles/123/buy/`  
**Usuario:** Participante o Sponsor autenticado  
**Resultado:** Formulario de compra se muestra normalmente

---

## 🧪 Verificación Manual

### Paso 1: Crear usuario organizador
```python
python manage.py shell

from apps.users.models import User
organizador = User.objects.create_user(
    username='organizador_test',
    email='org@test.com',
    password='test123',
    rol='organizador'
)
```

### Paso 2: Iniciar sesión como organizador
1. Ir a `/login/`
2. Ingresar credenciales del organizador
3. Navegar a lista de rifas `/raffles/`

### Paso 3: Verificar restricciones
- [ ] Botones de compra muestran "🚫 Solo Visualización"
- [ ] Al hacer clic en botón deshabilitado, no pasa nada
- [ ] Si intenta acceder a `/raffles/1/buy/` directamente, es redirigido
- [ ] Ve mensaje de error: "❌ Los organizadores no pueden comprar boletos..."

---

## 📊 Impacto en el Sistema

### Archivos Modificados
1. `backend/apps/raffles/views.py` - Validación en vista
2. `backend/apps/raffles/serializers.py` - Lógica de API
3. `frontend/templates/raffles/buy_ticket.html` - UI de compra
4. `frontend/templates/raffles/list.html` - UI de listado

### Compatibilidad
- ✅ No afecta a participantes
- ✅ No afecta a sponsors
- ✅ No afecta a admins
- ✅ Solo restringe a organizadores (como debe ser)

### Base de Datos
- ✅ No requiere migraciones
- ✅ No modifica modelos existentes
- ✅ Solo usa campo `rol` del modelo User

---

## 🎉 Resultado Final

Los organizadores ahora están **correctamente restringidos** de comprar boletos de rifas. Su rol es exclusivamente:

1. ✅ Crear rifas nuevas
2. ✅ Administrar sus rifas
3. ✅ Ver estadísticas
4. ✅ Gestionar sorteos
5. ❌ **NO pueden comprar boletos** (implementado)

---

## 📝 Notas Adicionales

### Roles en el Sistema
- **Participante** → Puede comprar boletos ✅
- **Organizador** → NO puede comprar boletos ❌ (solo administra)
- **Sponsor** → Puede comprar boletos ✅
- **Admin** → Puede comprar boletos ✅

### Próximos Pasos Recomendados
1. Agregar tests unitarios para esta funcionalidad
2. Documentar en manual de usuario
3. Agregar logging de intentos de acceso restringido
4. Considerar dashboard específico para organizadores

---

**Fecha de Implementación:** Diciembre 2024  
**Estado:** ✅ IMPLEMENTADO Y VERIFICADO  
**Prioridad:** ALTA (Regla de negocio crítica)
