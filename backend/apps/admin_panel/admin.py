from django.contrib import admin
from .models import AuditLog, SystemConfig

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['accion', 'modelo', 'usuario', 'ip_address', 'fecha']
    list_filter = ['accion', 'modelo', 'fecha']
    search_fields = ['usuario__email', 'descripcion', 'ip_address']
    readonly_fields = ['fecha']

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['clave', 'valor', 'actualizado_por', 'fecha_actualizacion']
    search_fields = ['clave', 'descripcion']
