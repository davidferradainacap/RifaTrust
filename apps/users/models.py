# Importación del modelo base de usuario y gestor de Django para autenticación personalizada
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Importación del sistema de modelos de Django para definir tablas de base de datos
from django.db import models
# Importación de utilidades de zona horaria para manejar fechas y horas
from django.utils import timezone
# Importación de campos personalizados encriptados para proteger datos sensibles
from apps.core.fields import EncryptedCharField, EncryptedTextField

class UserManager(BaseUserManager):
    """
    Gestor personalizado de usuarios que maneja la creación de usuarios normales y superusuarios.
    Extiende BaseUserManager de Django para usar email como identificador principal.
    """
    
    def create_user(self, email, nombre, password=None, **extra_fields):
        """
        Crea y guarda un usuario normal con email, nombre y contraseña.
        
        Args:
            email (str): Dirección de correo electrónico del usuario (requerido)
            nombre (str): Nombre completo del usuario (requerido)
            password (str): Contraseña en texto plano que será hasheada
            **extra_fields: Campos adicionales como rol, teléfono, etc.
        
        Returns:
            User: Instancia del usuario creado
        
        Raises:
            ValueError: Si no se proporciona email
        """
        # Validación: el email es obligatorio para crear un usuario
        if not email:
            raise ValueError('El email es obligatorio')
        # Normaliza el email (convierte dominio a minúsculas)
        email = self.normalize_email(email)
        # Crea instancia del modelo User con los datos proporcionados
        user = self.model(email=email, nombre=nombre, **extra_fields)
        # Hashea la contraseña usando el algoritmo configurado (Argon2)
        user.set_password(password)
        # Guarda el usuario en la base de datos especificada
        user.save(using=self._db)
        # Retorna la instancia del usuario creado
        return user

    def create_superuser(self, email, nombre, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con permisos administrativos completos.
        
        Args:
            email (str): Dirección de correo electrónico del superusuario
            nombre (str): Nombre completo del superusuario
            password (str): Contraseña del superusuario
            **extra_fields: Campos adicionales
        
        Returns:
            User: Instancia del superusuario creado con permisos de admin
        """
        # Establece is_staff en True para acceso al panel de administración Django
        extra_fields.setdefault('is_staff', True)
        # Establece is_superuser en True para todos los permisos
        extra_fields.setdefault('is_superuser', True)
        # Establece el rol como 'admin' para lógica de negocio personalizada
        extra_fields.setdefault('rol', 'admin')
        # Llama a create_user con los campos configurados para superusuario
        return self.create_user(email, nombre, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Modelo personalizado de Usuario que extiende AbstractBaseUser y PermissionsMixin.
    Usa email como identificador único en lugar de username.
    Soporta 4 roles: participante, organizador, sponsor y administrador.
    Implementa encriptación para datos sensibles (teléfono).
    """
    
    # Tupla de opciones para el campo rol - define los 4 tipos de usuarios del sistema
    ROLES = (
        ('participante', 'Participante'),  # Usuario que compra boletos
        ('organizador', 'Organizador'),    # Usuario que crea y gestiona rifas
        ('sponsor', 'Sponsor'),            # Usuario que patrocina rifas
        ('admin', 'Administrador'),        # Usuario con permisos administrativos
    )
    
    # Campo email único que actúa como identificador principal del usuario
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')
    # Nombre completo del usuario con máximo 100 caracteres
    nombre = models.CharField(max_length=100, verbose_name='Nombre Completo')
    # Teléfono encriptado en base de datos usando Fernet (AES-128) - puede estar vacío
    # max_length=500 para permitir espacio suficiente después de encriptación
    telefono = EncryptedCharField(max_length=500, blank=True, verbose_name='Teléfono')
    # Rol del usuario - determina permisos y funcionalidades disponibles
    rol = models.CharField(max_length=20, choices=ROLES, default='participante', verbose_name='Rol')
    # Imagen de perfil subida a la carpeta media/avatars/ - opcional
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    # Indica si la cuenta ha sido validada por email - True por defecto
    cuenta_validada = models.BooleanField(default=True, verbose_name='Cuenta Validada')
    
    # Campo requerido por Django - indica si el usuario puede iniciar sesión
    is_active = models.BooleanField(default=True)
    # Campo requerido por Django - indica si puede acceder al admin de Django
    is_staff = models.BooleanField(default=False)
    # Fecha y hora de registro del usuario - se establece automáticamente
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Registro')
    # Fecha y hora de última conexión - se actualiza en cada login
    ultima_conexion = models.DateTimeField(null=True, blank=True, verbose_name='Última Conexión')
    
    # Asigna el gestor personalizado UserManager a este modelo
    objects = UserManager()
    
    # Define 'email' como el campo de identificación para login
    USERNAME_FIELD = 'email'
    # Campos requeridos además del USERNAME_FIELD al crear superusuario
    REQUIRED_FIELDS = ['nombre']
    
    class Meta:
        """Metadatos del modelo User para configuración en Django Admin y queries"""
        # Nombre singular del modelo en Django Admin
        verbose_name = 'Usuario'
        # Nombre plural del modelo en Django Admin
        verbose_name_plural = 'Usuarios'
        # Ordenamiento por defecto: más recientes primero (DESC por fecha_registro)
        ordering = ['-fecha_registro']
    
    def __str__(self):
        """
        Representación en string del objeto User.
        Se usa en Django Admin y al imprimir el objeto.
        
        Returns:
            str: Formato "Nombre (email@ejemplo.com)"
        """
        return f"{self.nombre} ({self.email})"
    
    def get_full_name(self):
        """
        Método requerido por AbstractBaseUser.
        
        Returns:
            str: Nombre completo del usuario
        """
        return self.nombre
    
    def get_short_name(self):
        """
        Método requerido por AbstractBaseUser.
        Retorna solo el primer nombre o el email si no hay nombre.
        
        Returns:
            str: Primer nombre del usuario o email completo
        """
        # Divide el nombre por espacios y toma el primer elemento, o usa email si falla
        return self.nombre.split()[0] if self.nombre else self.email

class Profile(models.Model):
    """
    Modelo de Perfil extendido para usuarios.
    Relación OneToOne con User - cada usuario tiene exactamente un perfil.
    Almacena información personal adicional con encriptación de datos sensibles.
    """
    
    # Relación uno a uno con User - si se elimina User, se elimina Profile (CASCADE)
    # related_name='profile' permite acceder desde user.profile
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Dirección completa encriptada - protege información personal sensible
    direccion = EncryptedTextField(blank=True, verbose_name='Dirección')
    # Ciudad encriptada - puede estar vacía
    ciudad = EncryptedCharField(max_length=255, blank=True, verbose_name='Ciudad')
    # Estado/Provincia encriptado - puede estar vacío
    estado = EncryptedCharField(max_length=255, blank=True, verbose_name='Estado')
    # Código postal encriptado - puede estar vacío
    codigo_postal = EncryptedCharField(max_length=255, blank=True, verbose_name='Código Postal')
    # País sin encriptar - valor por defecto 'México'
    pais = models.CharField(max_length=100, default='México', verbose_name='País')
    # Fecha de nacimiento opcional - usado para validación de edad mínima
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    
    class Meta:
        """Metadatos del modelo Profile"""
        # Nombre singular en Django Admin
        verbose_name = 'Perfil'
        # Nombre plural en Django Admin
        verbose_name_plural = 'Perfiles'
    
    def __str__(self):
        """
        Representación en string del perfil.
        
        Returns:
            str: "Perfil de [Nombre del Usuario]"
        """
        return f"Perfil de {self.user.nombre}"

class Notification(models.Model):
    """
    Modelo de Notificaciones para sistema de alertas en tiempo real.
    Permite notificar a usuarios sobre eventos importantes: compras, sorteos, aprobaciones.
    Sistema de notificaciones leídas/no leídas con timestamps.
    """
    
    # Tupla de tipos de notificaciones permitidos - categoriza las alertas
    TIPO_CHOICES = (
        ('compra', 'Compra de Boleto'),                    # Notifica compra exitosa de boleto
        ('ganador', 'Ganador de Rifa'),                    # Notifica que ganó una rifa
        ('sorteo', 'Sorteo Realizado'),                    # Notifica que se realizó sorteo
        ('cancelacion', 'Rifa Cancelada'),                 # Notifica cancelación de rifa
        ('nuevo_organizador', 'Nueva Rifa Disponible'),    # Notifica nueva rifa publicada
        ('recordatorio', 'Recordatorio de Sorteo'),        # Recordatorio antes del sorteo
        ('sistema', 'Notificación del Sistema'),           # Mensajes administrativos generales
        ('sponsor_aprobado', 'Sponsor Aprobado'),          # Aprobación de solicitud de sponsor
        ('sponsor_rechazado', 'Sponsor Rechazado'),        # Rechazo de solicitud de sponsor
        ('rifa', 'Rifa'),                                  # Notificaciones relacionadas a rifas
    )
    
    # Usuario destinatario de la notificación - se eliminan notificaciones si se elimina usuario
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    # Tipo/categoría de la notificación - debe ser uno de TIPO_CHOICES
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name='Tipo')
    # Título breve de la notificación (máximo 200 caracteres) - se muestra en lista
    titulo = models.CharField(max_length=200, verbose_name='Título')
    # Mensaje completo de la notificación - texto sin límite
    mensaje = models.TextField(verbose_name='Mensaje')
    # URL opcional para redirigir al hacer clic - puede estar vacío
    enlace = models.CharField(max_length=500, blank=True, verbose_name='Enlace')
    
    # Indica si el usuario ya leyó la notificación - False por defecto
    leida = models.BooleanField(default=False, verbose_name='Leída')
    # Fecha y hora de creación automática de la notificación
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Creación')
    # Fecha y hora cuando el usuario marcó como leída - null hasta que se lea
    fecha_lectura = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Lectura')
    
    # Referencia opcional a la rifa que generó esta notificación
    # null=True y blank=True porque no todas las notificaciones están ligadas a rifas
    rifa_relacionada = models.ForeignKey('raffles.Raffle', on_delete=models.CASCADE, null=True, blank=True, related_name='notificaciones')
    
    class Meta:
        """Metadatos del modelo Notification"""
        # Nombre singular en Django Admin
        verbose_name = 'Notificación'
        # Nombre plural en Django Admin
        verbose_name_plural = 'Notificaciones'
        # Ordenamiento: más recientes primero (DESC por fecha_creacion)
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        """
        Representación en string de la notificación.
        
        Returns:
            str: "Título - Nombre del Usuario"
        """
        return f"{self.titulo} - {self.usuario.nombre}"
    
    def marcar_como_leida(self):
        """
        Marca la notificación como leída y registra la fecha/hora de lectura.
        Solo se ejecuta si la notificación no estaba previamente leída.
        Guarda automáticamente los cambios en la base de datos.
        """
        # Verifica que no esté ya marcada como leída para evitar actualizaciones innecesarias
        if not self.leida:
            # Cambia el estado a leída
            self.leida = True
            # Registra el momento exacto de la lectura
            self.fecha_lectura = timezone.now()
            # Persiste los cambios en la base de datos
            self.save()
