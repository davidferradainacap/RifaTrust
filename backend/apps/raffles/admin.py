from django.contrib import admin
from .models import Raffle, Ticket, Winner, SponsorshipRequest, OrganizerSponsorRequest

@admin.register(Raffle)
class RaffleAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'organizador', 'estado', 'precio_boleto', 'boletos_vendidos', 'total_boletos', 'fecha_sorteo']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['titulo', 'organizador__nombre']
    readonly_fields = ['boletos_vendidos', 'fecha_creacion', 'fecha_actualizacion']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['rifa', 'numero_boleto', 'usuario', 'estado', 'fecha_compra']
    list_filter = ['estado', 'fecha_compra']
    search_fields = ['rifa__titulo', 'usuario__nombre', 'codigo_qr']

@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ['rifa', 'boleto', 'fecha_sorteo', 'verificado', 'premio_entregado']
    list_filter = ['verificado', 'premio_entregado', 'fecha_sorteo']

@admin.register(SponsorshipRequest)
class SponsorshipRequestAdmin(admin.ModelAdmin):
    list_display = ['rifa', 'sponsor', 'nombre_marca', 'estado', 'valor_premio', 'fecha_solicitud']
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['rifa__titulo', 'sponsor__nombre', 'nombre_marca']
    readonly_fields = ['fecha_solicitud', 'fecha_respuesta']

@admin.register(OrganizerSponsorRequest)
class OrganizerSponsorRequestAdmin(admin.ModelAdmin):
    list_display = ['rifa', 'organizador', 'sponsor', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['rifa__titulo', 'organizador__nombre', 'sponsor__nombre']
    readonly_fields = ['fecha_solicitud', 'fecha_respuesta', 'organizador']
