from django.contrib import admin
from .models import Payment, Refund

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'usuario', 'monto', 'metodo_pago', 'estado', 'fecha_creacion']
    list_filter = ['estado', 'metodo_pago', 'fecha_creacion']
    search_fields = ['transaction_id', 'usuario__nombre', 'usuario__email']
    readonly_fields = ['transaction_id', 'fecha_creacion']

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['pago', 'monto', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'fecha_solicitud']
