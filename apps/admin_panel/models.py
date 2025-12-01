from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    ACCIONES = (
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('eliminar_usuario', 'Eliminar Usuario'),
        ('eliminar_rifa', 'Eliminar Rifa'),
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('compra', 'Compra'),
        ('pago', 'Pago'),
        ('sorteo', 'Sorteo'),
        ('sorteo_manual', 'Sorteo Manual'),
        ('aprobar_sponsor', 'Aprobar Sponsor'),
        ('rechazar_sponsor', 'Rechazar Sponsor'),
        ('cambiar_rol', 'Cambiar Rol'),
        ('suspender_usuario', 'Suspender Usuario'),
        ('activar_usuario', 'Activar Usuario'),
        ('cancelar_rifa', 'Cancelar Rifa'),
        ('cancelar_rifa_con_reembolsos', 'Cancelar Rifa con Reembolsos'),
        ('reembolso', 'Reembolso'),
        ('reembolso_automatico', 'Reembolso Automático'),
        ('error_reembolso', 'Error en Reembolso'),
        ('extender_plazo', 'Extender Plazo'),
        ('aprobar_sorteo_parcial', 'Aprobar Sorteo Parcial'),
        ('aprobar_rifa', 'Aprobar Rifa'),
        ('rechazar_rifa', 'Rechazar Rifa'),
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=50, choices=ACCIONES, verbose_name='Acción')
    modelo = models.CharField(max_length=100, verbose_name='Modelo Afectado')
    objeto_id = models.IntegerField(null=True, blank=True, verbose_name='ID del Objeto')
    descripcion = models.TextField(verbose_name='Descripción')
    
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Dirección IP')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    
    class Meta:
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-fecha']
    
    def __str__(self):
        usuario_str = self.usuario.email if self.usuario else 'Anónimo'
        return f"{self.accion} - {self.modelo} por {usuario_str}"

class SystemConfig(models.Model):
    clave = models.CharField(max_length=100, unique=True, verbose_name='Clave')
    valor = models.TextField(verbose_name='Valor')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
    
    def __str__(self):
        return self.clave
