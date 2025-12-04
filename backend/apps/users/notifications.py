from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    TIPO_CHOICES = (
        ('compra', 'Compra de Boleto'),
        ('ganador', 'Ganador de Rifa'),
        ('sorteo', 'Sorteo Realizado'),
        ('cancelacion', 'Rifa Cancelada'),
        ('nuevo_organizador', 'Nueva Rifa Disponible'),
        ('recordatorio', 'Recordatorio de Sorteo'),
        ('sistema', 'Notificación del Sistema'),
        ('sponsor_aprobado', 'Sponsor Aprobado'),
        ('sponsor_rechazado', 'Sponsor Rechazado'),
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name='Tipo')
    titulo = models.CharField(max_length=200, verbose_name='Título')
    mensaje = models.TextField(verbose_name='Mensaje')
    enlace = models.CharField(max_length=500, blank=True, verbose_name='Enlace')
    
    leida = models.BooleanField(default=False, verbose_name='Leída')
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Creación')
    fecha_lectura = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Lectura')
    
    # Referencia opcional a la rifa relacionada
    rifa_relacionada = models.ForeignKey('raffles.Raffle', on_delete=models.CASCADE, null=True, blank=True, related_name='notificaciones')
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f"{self.titulo} - {self.usuario.nombre}"
    
    def marcar_como_leida(self):
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save()
