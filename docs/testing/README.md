# 🧪 Testing

Esta carpeta contiene toda la documentación y scripts relacionados con **pruebas y QA** del sistema RifaTrust.

## 📄 Archivos

### Documentación de Pruebas
- **`PLAN_PRUEBAS_COMPLETO.md`** - Plan maestro con 150 casos de prueba organizados en 8 módulos
- **`INFORME_PRUEBAS_FINAL.md`** - Informe técnico completo de ejecución de pruebas
- **`RESUMEN_FINAL_TESTS.md`** - Resumen ejecutivo para stakeholders

### Scripts de Testing
- **`test_suite_runner.py`** - Suite de pruebas automatizadas de endpoints (12 tests)
- **`test_organizer_restriction.py`** - Test de restricción de compra para organizadores
- **`test_password_reset.py`** - Test de recuperación de contraseña

## 📊 Resultados de Última Ejecución

**Fecha:** Diciembre 2024  
**Tests Ejecutados:** 12  
**Tasa de Éxito:** 100% ✅  
**Tiempo Total:** 0.470 segundos  

### Módulos Verificados
- ✅ Páginas principales (Home, Login, Register, Raffles)
- ✅ Panel administrativo con seguridad
- ✅ Archivos estáticos (CSS, JS)
- ✅ API REST (Root, Raffles, Schema)
- ✅ Recuperación de contraseña

## 🚀 Ejecutar Tests

### Tests Automatizados
```bash
# Ejecutar suite completa de endpoint tests
python docs/testing/test_suite_runner.py

# Tests de Django
python manage.py test

# Con coverage
python manage.py test --verbosity=2
```

### Verificación del Sistema
```bash
# Check de sistema
python manage.py check

# Check para deployment
python manage.py check --deploy
```

## 📋 Plan de Pruebas

### 8 Módulos de Testing

1. **Usuarios** (27 casos) - Registro, login, perfiles, recuperación
2. **Rifas** (26 casos) - Visualización, compra, creación, sorteos
3. **Pagos** (15 casos) - Stripe, webhooks, reembolsos
4. **Administración** (20 casos) - Dashboard, gestión, auditoría
5. **Seguridad** (19 casos) - Autenticación, rate limiting, validación
6. **Rendimiento** (13 casos) - Tiempos de respuesta, carga
7. **Integración** (15 casos) - SendGrid, Stripe, APIs externas
8. **Regresión** (15 casos) - Flujos críticos, compatibilidad

### Prioridades
- 🔴 Alta: 78 casos (52%)
- 🟡 Media: 56 casos (37%)
- 🟢 Baja: 16 casos (11%)

## 🎯 Cobertura Actual

### Tests Automatizados ✅
- Endpoints principales
- Autenticación básica
- Archivos estáticos
- API REST

### Pendiente Manual ⏳
- Flujos completos de pago
- Integraciones externas en producción
- Pruebas de carga
- Compatibilidad de navegadores

## 📝 Agregar Nuevos Tests

### Test de Endpoint
```python
def test_endpoint(name, url, method="GET", expected_status=200):
    response = requests.get(url)
    assert response.status_code == expected_status
```

### Test Unitario Django
```python
from django.test import TestCase

class MyModelTest(TestCase):
    def test_something(self):
        # Tu test aquí
        self.assertEqual(1, 1)
```

## 🔗 Referencias

- [Django Testing](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Última actualización:** Diciembre 2024  
**Estado del Sistema:** Production Ready ✅  
**Próxima Revisión:** Post-deployment en Azure
