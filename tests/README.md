# Tests del Proyecto

Este directorio contiene los tests del proyecto.

## Estructura de Tests

```
tests/
├── unit/              # Tests unitarios
├── integration/       # Tests de integración
├── functional/        # Tests funcionales
└── fixtures/          # Datos de prueba
```

## Ejecutar Tests

Para ejecutar todos los tests:
```bash
python manage.py test
```

Para ejecutar tests de una app específica:
```bash
python manage.py test apps.users
python manage.py test apps.raffles
```

Para ejecutar con cobertura:
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Escribir Tests

Cada app debe tener sus propios tests en su directorio `tests.py` o en una carpeta `tests/`.

Ejemplo de test básico:
```python
from django.test import TestCase
from apps.users.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
```

## Mejores Prácticas

1. Usar nombres descriptivos para tests
2. Un test debe probar una sola cosa
3. Usar fixtures para datos de prueba reutilizables
4. Limpiar datos después de cada test
5. Mantener tests independientes entre sí
