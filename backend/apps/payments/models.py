from django.db import models
from django.conf import settings
from apps.raffles.models import Ticket
from apps.core.fields import EncryptedCharField

class Payment(models.Model):
    METODO_PAGO = (
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('transferencia', 'Transferencia Bancaria'),
        ('efectivo', 'Efectivo'),
    )
    
    ESTADO_PAGO = (
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pagos')
    boletos = models.ManyToManyField(Ticket, related_name='pagos')
    
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO, verbose_name='Método de Pago')
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO, default='pendiente', verbose_name='Estado')
    
    # Detalles de la transacción (Encriptados)
    transaction_id = EncryptedCharField(max_length=400, unique=True, verbose_name='ID de Transacción')  # Encriptado
    payment_intent_id = EncryptedCharField(max_length=400, blank=True, verbose_name='Payment Intent ID')  # Encriptado
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_completado = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Completado')
    
    # Información adicional
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    notas_admin = models.TextField(blank=True, verbose_name='Notas del Administrador')
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pago {self.transaction_id} - ${self.monto}"

class Refund(models.Model):
    MOTIVOS = (
        ('duplicado', 'Pago Duplicado'),
        ('cancelacion', 'Cancelación de Rifa'),
        ('error_sistema', 'Error del Sistema'),
        ('solicitud_usuario', 'Solicitud del Usuario'),
        ('fraude', 'Sospecha de Fraude'),
        ('otro', 'Otro Motivo'),
    )
    
    pago = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='reembolso')
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto Reembolsado')
    
    # Información del reembolso
    motivo = models.CharField(max_length=50, choices=MOTIVOS, default='otro', verbose_name='Motivo del Reembolso')
    razon = models.TextField(verbose_name='Explicación Detallada')
    procesado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reembolsos_procesados', verbose_name='Procesado Por')
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Solicitud')
    fecha_procesado = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Procesado')
    estado = models.CharField(max_length=20, choices=[
        ('solicitado', 'Solicitado'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('completado', 'Completado'),
    ], default='solicitado')
    
    class Meta:
        verbose_name = 'Reembolso'
        verbose_name_plural = 'Reembolsos'
    
    def __str__(self):
        return f"Reembolso de {self.pago.transaction_id}"
