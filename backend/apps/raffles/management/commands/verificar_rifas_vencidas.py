"""
Comando de gestión para verificar rifas que llegaron a su fecha de sorteo
sin cumplir el mínimo de boletos vendidos.

Uso: python manage.py verificar_rifas_vencidas
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.raffles.models import Raffle
from apps.users.models import Notification


class Command(BaseCommand):
    help = 'Verifica rifas activas que llegaron a su fecha de sorteo sin cumplir el mínimo de viabilidad'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Buscar rifas activas cuya fecha de sorteo ya pasó
        rifas_vencidas = Raffle.objects.filter(
            estado='activa',
            fecha_sorteo__lte=now
        )
        
        self.stdout.write(self.style.WARNING(f'\n🔍 Verificando {rifas_vencidas.count()} rifas vencidas...'))
        
        rifas_cerradas = 0
        
        for rifa in rifas_vencidas:
            minimo_requerido = rifa.boletos_minimos_requeridos
            
            # Verificar si cumple el mínimo
            if not rifa.cumple_minimo_viabilidad:
                # Cerrar la rifa por no cumplir viabilidad
                rifa.estado = 'cerrada'
                rifa.motivo_pausa = f'No se alcanzó el mínimo de {minimo_requerido} boletos vendidos para viabilidad económica. Boletos vendidos: {rifa.boletos_vendidos}. Fecha límite: {rifa.fecha_sorteo.strftime("%d/%m/%Y %H:%M")}'
                rifa.fecha_pausa = now
                rifa.save()
                
                rifas_cerradas += 1
                
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠️  Rifa #{rifa.id} "{rifa.titulo}" cerrada'
                    )
                )
                self.stdout.write(
                    f'      • Mínimo requerido: {minimo_requerido} boletos'
                )
                self.stdout.write(
                    f'      • Vendidos: {rifa.boletos_vendidos} boletos'
                )
                self.stdout.write(
                    f'      • Déficit: {minimo_requerido - rifa.boletos_vendidos} boletos'
                )
                
                # Notificar al organizador
                Notification.objects.create(
                    usuario=rifa.organizador,
                    tipo='admin',
                    titulo='⚠️ Rifa cerrada por viabilidad',
                    mensaje=f'Tu rifa "{rifa.titulo}" ha sido cerrada automáticamente porque no se alcanzó el mínimo de {minimo_requerido} boletos vendidos. Requiere revisión administrativa para extensión o cancelación con reembolsos.',
                    enlace=f'/raffles/{rifa.id}/',
                    rifa_relacionada=rifa
                )
                
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✅ Rifa #{rifa.id} "{rifa.titulo}" cumple el mínimo ({rifa.boletos_vendidos}/{minimo_requerido})'
                    )
                )
        
        if rifas_cerradas > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Proceso completado: {rifas_cerradas} rifa(s) cerrada(s) por falta de viabilidad'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Estas rifas requieren revisión administrativa en el panel de admin'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✅ No hay rifas que requieran cierre automático'
                )
            )
