# Importación del sistema de modelos de Django para definir estructura de base de datos
from django.db import models
# Importación de configuración global del proyecto para acceder a AUTH_USER_MODEL
from django.conf import settings
# Importación de utilidades de zona horaria para manejar fechas/horas correctamente
from django.utils import timezone
# Importación de validador para asegurar valores mínimos en campos numéricos
from django.core.validators import MinValueValidator

class Raffle(models.Model):
    """
    Modelo principal de Rifa que representa una rifa en el sistema.
    Contiene toda la información necesaria: detalles, premios, estado, fechas, configuración.
    Implementa un workflow de estados desde creación hasta finalización.
    Soporta sistema de aprobación administrativa y pausas por revisión.
    """
    
    # Tupla de estados posibles para una rifa - define el ciclo de vida completo
    ESTADO_CHOICES = (
        ('borrador', 'Borrador'),                           # Estado inicial - rifa en construcción
        ('pendiente_aprobacion', 'Pendiente de Aprobación'), # Enviada para revisión admin
        ('aprobada', 'Aprobada'),                           # Aprobada por admin, lista para activar
        ('rechazada', 'Rechazada'),                         # Rechazada por admin, requiere cambios
        ('activa', 'Activa'),                               # Publicada y aceptando compras
        ('pausada', 'Pausada - En Revisión'),               # Pausada temporalmente por incidencias
        ('cerrada', 'Cerrada'),                             # Cerrada, no acepta más compras
        ('finalizada', 'Finalizada'),                       # Sorteo realizado, ganador seleccionado
        ('cancelada', 'Cancelada'),                         # Cancelada, se procesan reembolsos
    )
    
    # === CAMPOS DE IDENTIFICACIÓN Y PROPIETARIO ===
    # Relación con usuario organizador - CASCADE: si se elimina el usuario, se eliminan sus rifas
    # related_name permite acceder desde user.rifas_organizadas
    organizador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rifas_organizadas')
    
    # === INFORMACIÓN BÁSICA DE LA RIFA ===
    # Título descriptivo de la rifa - máximo 200 caracteres
    titulo = models.CharField(max_length=200, verbose_name='Título')
    # Descripción detallada de la rifa - texto ilimitado, puede incluir reglas y condiciones
    descripcion = models.TextField(verbose_name='Descripción')
    # Imagen principal de la rifa subida a media/raffles/ - opcional
    imagen = models.ImageField(upload_to='raffles/', blank=True, null=True, verbose_name='Imagen')
    
    # === CONFIGURACIÓN ECONÓMICA ===
    # Precio individual de cada boleto - decimal con 2 decimales, mínimo $0.01
    # max_digits=10: hasta 99,999,999.99 (casi 100 millones)
    precio_boleto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)], verbose_name='Precio por Boleto')
    # Cantidad total de boletos disponibles en esta rifa - mínimo 1 boleto
    total_boletos = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Total de Boletos')
    # Contador de boletos vendidos hasta el momento - se actualiza con cada compra
    boletos_vendidos = models.IntegerField(default=0, verbose_name='Boletos Vendidos')
    
    # === FECHAS IMPORTANTES ===
    # Fecha y hora en que la rifa se activa y puede recibir compras - por defecto ahora
    fecha_inicio = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Inicio')
    # Fecha y hora programada para realizar el sorteo del ganador - requerida
    fecha_sorteo = models.DateTimeField(verbose_name='Fecha del Sorteo')
    # Fecha y hora de creación del registro - se establece automáticamente una vez
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    # Fecha y hora de última modificación - se actualiza automáticamente en cada save()
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    # === ESTADO DE LA RIFA ===
    # Estado actual de la rifa - determina qué acciones se pueden realizar
    # Valor por defecto 'borrador' para nuevas rifas
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador', verbose_name='Estado')
    
    # === INFORMACIÓN DEL PREMIO ===
    # Nombre corto del premio principal - máximo 200 caracteres (ej: "iPhone 15 Pro Max")
    premio_principal = models.CharField(max_length=200, verbose_name='Premio Principal')
    # Descripción detallada del premio - opcional, puede incluir especificaciones técnicas
    descripcion_premio = models.TextField(blank=True, verbose_name='Descripción del Premio')
    # Imagen del premio subida a media/prizes/ - opcional
    imagen_premio = models.ImageField(upload_to='prizes/', blank=True, null=True, verbose_name='Imagen del Premio')
    # Valor comercial estimado del premio - opcional, hasta 9,999,999,999.99
    # Se usa para cálculos de viabilidad (ingreso total >= 2x valor del premio)
    valor_premio = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Valor Estimado del Premio')
    
    # === DOCUMENTACIÓN LEGAL ===
    # Archivo de autorización legal para realizar la rifa - subido a media/documentos_legales/
    # Puede ser PDF, Word o imagen - opcional pero recomendado
    # Requerido para cumplir con regulaciones locales sobre rifas y sorteos
    documento_legal = models.FileField(upload_to='documentos_legales/', null=True, blank=True, verbose_name='Documento de Autorización Legal', help_text='Sube el documento que autoriza la realización de esta rifa (PDF, Word, imagen)')
    
    # === CONFIGURACIÓN DE COMPRA ===
    # Permite que un mismo usuario compre múltiples boletos - True por defecto
    permite_multiples_boletos = models.BooleanField(default=True, verbose_name='Permitir Múltiples Boletos por Usuario')
    # Límite máximo de boletos que puede comprar un solo usuario - por defecto 10
    # Mínimo 1 boleto si se permiten múltiples compras
    max_boletos_por_usuario = models.IntegerField(default=10, validators=[MinValueValidator(1)], verbose_name='Máximo de Boletos por Usuario')
    
    # === SISTEMA DE APROBACIÓN ADMINISTRATIVA ===
    # Fecha y hora cuando el organizador envió la rifa para aprobación - null hasta envío
    fecha_solicitud = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Solicitud de Aprobación')
    # Usuario administrador que revisó la rifa - SET_NULL: si se elimina admin, se mantiene el registro
    # null=True: puede no tener revisor aún
    revisado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rifas_revisadas', verbose_name='Revisado por')
    # Fecha y hora cuando el admin completó la revisión (aprobación/rechazo)
    fecha_revision_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Revisión')
    # Comentarios del revisor sobre la rifa - puede incluir recomendaciones o felicitaciones
    comentarios_revision = models.TextField(blank=True, null=True, verbose_name='Comentarios de la Revisión')
    # Razón específica del rechazo - solo se llena si estado = 'rechazada'
    # El organizador ve este mensaje y puede hacer correcciones
    motivo_rechazo = models.TextField(blank=True, null=True, verbose_name='Motivo de Rechazo')
    
    # === SISTEMA DE REVISIÓN (PAUSAS Y EXTENSIONES) ===
    # Razón por la cual se pausó la rifa - ej: "Reporte de irregularidades", "Revisión de premio"
    motivo_pausa = models.TextField(blank=True, null=True, verbose_name='Motivo de Pausa')
    # Fecha y hora exacta cuando se pausó la rifa
    fecha_pausa = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Pausa')
    # Análisis y conclusiones del administrador tras revisar la pausa
    revision_admin = models.TextField(blank=True, null=True, verbose_name='Revisión del Administrador')
    # Fecha y hora cuando el admin completó la revisión de la pausa
    fecha_revision = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Revisión')
    # Nueva fecha de sorteo si se otorga extensión por pausa - reemplaza fecha_sorteo temporalmente
    nueva_fecha_sorteo = models.DateTimeField(null=True, blank=True, verbose_name='Nueva Fecha de Sorteo (Extensión)')
    
    class Meta:
        """Metadatos del modelo Raffle para configuración en Django Admin"""
        # Nombre singular mostrado en Django Admin
        verbose_name = 'Rifa'
        # Nombre plural mostrado en Django Admin
        verbose_name_plural = 'Rifas'
        # Ordenamiento por defecto: más recientes primero (DESC por fecha_creacion)
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        """
        Representación en string del objeto Raffle.
        Se usa en Django Admin, logs y al imprimir el objeto.
        
        Returns:
            str: Título de la rifa
        """
        return self.titulo
    
    @property
    def porcentaje_vendido(self):
        """
        Calcula el porcentaje de boletos vendidos respecto al total.
        Propiedad de solo lectura calculada dinámicamente.
        
        Returns:
            float: Porcentaje de 0 a 100 de boletos vendidos
            
        Example:
            Si total_boletos=1000 y boletos_vendidos=250 → retorna 25.0
        """
        # División segura: si total_boletos es 0, retorna 0 en lugar de error
        return (self.boletos_vendidos / self.total_boletos) * 100 if self.total_boletos > 0 else 0
    
    @property
    def boletos_disponibles(self):
        """
        Calcula la cantidad de boletos aún disponibles para compra.
        Propiedad de solo lectura calculada dinámicamente.
        
        Returns:
            int: Cantidad de boletos disponibles (nunca negativo)
            
        Example:
            Si total_boletos=1000 y boletos_vendidos=750 → retorna 250
        """
        # max() asegura que nunca retorne un valor negativo por inconsistencias de datos
        return max(0, self.total_boletos - self.boletos_vendidos)
    
    @property
    def esta_disponible(self):
        """
        Verifica si la rifa está disponible para recibir compras de boletos.
        Una rifa solo está disponible si su estado es 'activa'.
        Propiedad de solo lectura calculada dinámicamente.
        
        Returns:
            bool: True si se puede comprar boletos, False en caso contrario
            
        Note:
            No verifica si quedan boletos disponibles, solo el estado de la rifa.
            El sistema permite sobreventa intencional controlada.
        """
        return self.estado == 'activa'
    
    @property
    def ingreso_actual(self):
        """
        Calcula el ingreso total generado por los boletos ya vendidos.
        Propiedad de solo lectura calculada dinámicamente.
        
        Returns:
            Decimal: Monto total recaudado hasta el momento
            
        Example:
            Si precio_boleto=1000 y boletos_vendidos=250 → retorna 250000
        """
        return self.boletos_vendidos * self.precio_boleto
    
    @property
    def ingreso_potencial(self):
        """
        Calcula el ingreso máximo posible si se venden todos los boletos.
        Usado para análisis de viabilidad y proyecciones.
        Propiedad de solo lectura calculada dinámicamente.
        
        Returns:
            Decimal: Monto total si se vendieran todos los boletos
            
        Example:
            Si precio_boleto=1000 y total_boletos=1000 → retorna 1000000
            
        Note:
            Debe ser >= 2x valor_premio para que la rifa sea viable
        """
        return self.total_boletos * self.precio_boleto

class Ticket(models.Model):
    """
    Modelo de Boleto que representa un ticket individual comprado para una rifa.
    Cada boleto tiene un número único dentro de su rifa y un código QR para validación.
    Maneja estados desde reserva hasta ganador, pasando por pago y posible cancelación.
    """
    
    # Tupla de estados posibles para un boleto - define su ciclo de vida
    ESTADO_CHOICES = (
        ('reservado', 'Reservado'),   # Reservado temporalmente durante proceso de pago
        ('pagado', 'Pagado'),         # Pago confirmado, participa en sorteo
        ('cancelado', 'Cancelado'),   # Cancelado por usuario o sistema, no participa
        ('ganador', 'Ganador'),       # Boleto ganador del sorteo
    )
    
    # === RELACIONES ===
    # Rifa a la que pertenece este boleto - CASCADE: si se elimina rifa, se eliminan sus boletos
    rifa = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='boletos')
    # Usuario propietario del boleto - CASCADE: si se elimina usuario, se eliminan sus boletos
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='boletos')
    
    # === IDENTIFICACIÓN ===
    # Número único del boleto dentro de la rifa (1, 2, 3, ..., N)
    # Combinado con 'rifa' forma una clave única (unique_together)
    numero_boleto = models.IntegerField(verbose_name='Número de Boleto')
    
    # === INFORMACIÓN DE COMPRA ===
    # Fecha y hora exacta de la compra - se establece automáticamente una vez
    fecha_compra = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Compra')
    # Estado actual del boleto - por defecto 'reservado' hasta confirmar pago
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='reservado', verbose_name='Estado')
    
    # === VALIDACIÓN Y SEGURIDAD ===
    # Código QR único para validación del boleto - previene falsificaciones
    # UNIQUE a nivel de base de datos: no puede haber dos boletos con el mismo código
    # Generado con UUID o hash durante la creación del boleto
    codigo_qr = models.CharField(max_length=100, unique=True, verbose_name='Código QR')
    
    class Meta:
        """Metadatos del modelo Ticket"""
        # Nombre singular en Django Admin
        verbose_name = 'Boleto'
        # Nombre plural en Django Admin
        verbose_name_plural = 'Boletos'
        # Restricción de unicidad: no puede haber dos boletos con el mismo número en la misma rifa
        # Esto asegura que cada número de boleto sea único por rifa
        unique_together = ['rifa', 'numero_boleto']
        # Ordenamiento por defecto: por número de boleto ascendente (1, 2, 3, ...)
        ordering = ['numero_boleto']
    
    def __str__(self):
        """
        Representación en string del boleto.
        Formato: "Boleto #[número] - [Título de la rifa]"
        
        Returns:
            str: Descripción legible del boleto
            
        Example:
            "Boleto #42 - iPhone 15 Pro Max"
        """
        return f"Boleto #{self.numero_boleto} - {self.rifa.titulo}"

class SponsorshipRequest(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    )
    
    rifa = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='solicitudes_patrocinio')
    sponsor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes_patrocinio')
    
    # Información del aporte del sponsor
    nombre_premio_adicional = models.CharField(max_length=200, verbose_name='Nombre del Premio Adicional')
    descripcion_premio = models.TextField(verbose_name='Descripción del Premio')
    valor_premio = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Valor del Premio')
    imagen_premio = models.ImageField(upload_to='sponsor_prizes/', verbose_name='Imagen del Premio')
    
    # Información de la marca
    nombre_marca = models.CharField(max_length=200, verbose_name='Nombre de la Marca')
    logo_marca = models.ImageField(upload_to='sponsor_logos/', verbose_name='Logo de la Marca')
    sitio_web = models.URLField(blank=True, null=True, verbose_name='Sitio Web')
    mensaje_patrocinio = models.TextField(verbose_name='Mensaje de Patrocinio', help_text='Breve mensaje sobre por qué quieres patrocinar esta rifa')
    
    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name='Estado')
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Solicitud')
    fecha_respuesta = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Respuesta')
    motivo_rechazo = models.TextField(blank=True, null=True, verbose_name='Motivo de Rechazo')
    
    class Meta:
        verbose_name = 'Solicitud de Patrocinio'
        verbose_name_plural = 'Solicitudes de Patrocinio'
        ordering = ['-fecha_solicitud']
        # Nota: No se puede usar unique_together con 'estado' porque un sponsor puede tener múltiples solicitudes rechazadas
        # La validación de solicitudes pendientes duplicadas se hace en la vista
    
    def __str__(self):
        return f"{self.sponsor.nombre} → {self.rifa.titulo} ({self.estado})"

class OrganizerSponsorRequest(models.Model):
    """Solicitud de un organizador a un sponsor para que patrocine su rifa"""
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    )
    
    rifa = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='solicitudes_a_sponsors')
    sponsor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invitaciones_patrocinio')
    organizador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes_a_sponsors_enviadas')
    
    # Mensaje del organizador
    mensaje_invitacion = models.TextField(verbose_name='Mensaje de Invitación', help_text='Explica por qué te gustaría que este sponsor participe en tu rifa')
    beneficios_ofrecidos = models.TextField(verbose_name='Beneficios Ofrecidos', help_text='Qué beneficios ofreces al sponsor (exposición, espacio publicitario, etc.)')
    
    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name='Estado')
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Solicitud')
    fecha_respuesta = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Respuesta')
    motivo_rechazo = models.TextField(blank=True, null=True, verbose_name='Motivo de Rechazo')
    
    # Si el sponsor acepta, puede agregar esta información
    propuesta_premio = models.CharField(max_length=200, blank=True, null=True, verbose_name='Premio Propuesto')
    propuesta_valor = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Valor Propuesto')
    
    class Meta:
        verbose_name = 'Solicitud de Organizador a Sponsor'
        verbose_name_plural = 'Solicitudes de Organizadores a Sponsors'
        ordering = ['-fecha_solicitud']
        unique_together = ['rifa', 'sponsor']  # Un organizador solo puede enviar una solicitud por sponsor por rifa
    
    def __str__(self):
        return f"{self.organizador.nombre} invita a {self.sponsor.nombre} → {self.rifa.titulo} ({self.estado})"

class Winner(models.Model):
    rifa = models.OneToOneField(Raffle, on_delete=models.CASCADE, related_name='ganador')
    boleto = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='premio_ganado')
    fecha_sorteo = models.DateTimeField(auto_now_add=True, verbose_name='Fecha del Sorteo')
    verificado = models.BooleanField(default=False, verbose_name='Verificado')
    premio_entregado = models.BooleanField(default=False, verbose_name='Premio Entregado')
    fecha_entrega = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Entrega')
    notas = models.TextField(blank=True, verbose_name='Notas')
    
    # Campos de verificación del sorteo
    seed_aleatorio = models.CharField(max_length=64, null=True, blank=True, verbose_name='Semilla Aleatoria (SHA256)', help_text='Hash SHA256 usado como semilla para el sorteo')
    timestamp_sorteo = models.BigIntegerField(null=True, blank=True, verbose_name='Timestamp del Sorteo', help_text='Unix timestamp exacto del momento del sorteo')
    algoritmo = models.CharField(max_length=50, default='SHA256+Timestamp', verbose_name='Algoritmo Utilizado')
    hash_verificacion = models.CharField(max_length=64, null=True, blank=True, verbose_name='Hash de Verificación', help_text='Hash SHA256 de toda la información del sorteo')
    participantes_totales = models.IntegerField(null=True, blank=True, verbose_name='Total de Participantes', help_text='Número de boletos pagados al momento del sorteo')
    
    # Acta digital del sorteo
    acta_digital = models.TextField(null=True, blank=True, verbose_name='Acta Digital del Sorteo', help_text='Registro completo y auditable del sorteo')
    
    class Meta:
        verbose_name = 'Ganador'
        verbose_name_plural = 'Ganadores'
    
    def __str__(self):
        return f"Ganador: {self.boleto.usuario.nombre} - {self.rifa.titulo}"
