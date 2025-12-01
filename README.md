# Sistema de Rifas (Raffle System)

Sistema completo de gestión de rifas online desarrollado con Django, que permite crear, administrar y participar en rifas con integración de pagos.

## 🚀 Características

- **Gestión de Usuarios**: Registro, autenticación y perfiles con diferentes roles (Participante, Organizador, Patrocinador, Administrador)
- **Gestión de Rifas**: Crear, editar y administrar rifas con diferentes tipos (normales y ruleta)
- **Sistema de Pagos**: Integración con Stripe para procesamiento seguro de pagos
- **Panel de Administración**: Dashboard completo para administradores con auditoría y gestión
- **Notificaciones**: Sistema de notificaciones en tiempo real para usuarios
- **Sistema de Boletos**: Compra y gestión de boletos de rifas
- **Responsive**: Diseño adaptable a diferentes dispositivos

## 📋 Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- virtualenv (recomendado)
- SQLite (incluido) o PostgreSQL (opcional)

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd RS_project
```

### 2. Crear y activar entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo `.env.example` a `.env` y configurar las variables:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Editar `.env` con tus configuraciones específicas.

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Poblar la base de datos (opcional)

```bash
python scripts/populate_db.py
```

### 8. Ejecutar el servidor

```bash
python manage.py runserver
```

Acceder a: `http://localhost:8000`

## 📁 Estructura del Proyecto

```
RS_project/
├── apps/                      # Aplicaciones Django
│   ├── admin_panel/          # Panel de administración
│   ├── payments/             # Sistema de pagos
│   ├── raffles/              # Gestión de rifas
│   └── users/                # Gestión de usuarios
├── config/                   # Configuración del proyecto
│   ├── settings.py          # Configuraciones Django
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # WSGI configuration
├── docs/                     # Documentación
├── media/                    # Archivos de usuario (imágenes, etc.)
├── scripts/                  # Scripts de utilidad
├── static/                   # Archivos estáticos (CSS, JS)
├── templates/                # Plantillas HTML
├── tests/                    # Tests del proyecto
├── .env                      # Variables de entorno (no versionar)
├── .env.example             # Ejemplo de variables de entorno
├── .gitignore               # Archivos ignorados por git
├── manage.py                # Comando de administración Django
├── requirements.txt         # Dependencias del proyecto
└── README.md               # Este archivo
```

## 🎯 Uso

### Roles de Usuario

1. **Participante**: Puede comprar boletos y participar en rifas
2. **Organizador**: Puede crear y gestionar sus propias rifas
3. **Patrocinador**: Puede patrocinar rifas y obtener visibilidad
4. **Administrador**: Acceso completo al sistema y panel de administración
5. **Superusuario**: Control total del sistema

### Crear una Rifa

1. Iniciar sesión como Organizador o Administrador
2. Ir a "Crear Rifa"
3. Completar el formulario con detalles de la rifa
4. Agregar premios y configurar boletos
5. Publicar la rifa

### Comprar Boletos

1. Iniciar sesión como Participante
2. Explorar rifas disponibles
3. Seleccionar rifa y número de boletos
4. Procesar pago con Stripe
5. Recibir confirmación y notificación

## 🧪 Testing

Ejecutar tests:

```bash
python manage.py test
```

Ejecutar tests con cobertura:

```bash
coverage run --source='.' manage.py test
coverage report
```

## 📦 Dependencias Principales

- Django 5.0.0
- Django REST Framework 3.14.0
- Pillow 10.1.0 (procesamiento de imágenes)
- Stripe 7.8.0 (pagos)
- ReportLab 4.0.7 (generación de PDFs)
- django-crispy-forms (formularios)
- python-decouple (variables de entorno)

## 🔒 Seguridad

- Autenticación basada en sesiones de Django
- Protección CSRF activada
- Validación de permisos por rol
- Variables sensibles en archivos .env
- Sanitización de entrada de usuarios

## 🚀 Despliegue

### Preparación para Producción

1. Configurar `DEBUG=False` en `.env`
2. Configurar `ALLOWED_HOSTS` con tu dominio
3. Configurar base de datos PostgreSQL
4. Configurar servidor web (Nginx/Apache)
5. Usar gunicorn como servidor WSGI
6. Configurar archivos estáticos: `python manage.py collectstatic`
7. Configurar certificado SSL

### Variables de Entorno para Producción

```env
DEBUG=False
SECRET_KEY=tu-clave-secreta-muy-segura
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=raffle_db
DATABASE_USER=raffle_user
DATABASE_PASSWORD=contraseña-segura
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Licencia

Este proyecto es privado y confidencial.

## 👥 Autores

- Equipo de Desarrollo INACAP

## 📧 Contacto

Para preguntas o soporte, contactar a: [tu-email@ejemplo.com]

## 🔄 Changelog

Ver [docs/FIXES_APPLIED.md](docs/FIXES_APPLIED.md) para historial de cambios.

## 📚 Recursos Adicionales

- [Documentación de Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Stripe API Documentation](https://stripe.com/docs/api)
