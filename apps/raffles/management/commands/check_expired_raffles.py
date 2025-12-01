from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.raffles.models import Raffle

class Command(BaseCommand):
    help = 'Verifica rifas expiradas y las pausa si no vendieron todos los boletos'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Buscar rifas activas cuya fecha de sorteo ya pasó
        rifas_expiradas = Raffle.objects.filter(
            estado='activa',
            fecha_sorteo__lt=now
        )
        
        rifas_pausadas = 0
        
        for rifa in rifas_expiradas:
            # Si no se vendieron todos los boletos, pausar la rifa
            if rifa.boletos_vendidos < rifa.total_boletos:
                rifa.estado = 'pausada'
                rifa.fecha_pausa = now
                rifa.motivo_pausa = (
                    f'Rifa pausada automáticamente. '
                    f'La fecha de sorteo ({rifa.fecha_sorteo.strftime("%d/%m/%Y %H:%M")}) expiró '
                    f'con solo {rifa.boletos_vendidos} de {rifa.total_boletos} boletos vendidos '
                    f'({rifa.porcentaje_vendido:.1f}%). '
                    f'Esperando revisión del administrador.'
                )
                rifa.save()
                rifas_pausadas += 1
                
                self.stdout.write(
                    self.style.WARNING(
                        f'✋ Rifa pausada: "{rifa.titulo}" - '
                        f'{rifa.boletos_vendidos}/{rifa.total_boletos} boletos vendidos'
                    )
                )
            else:
                # Si se vendieron todos los boletos, cerrar la rifa
                rifa.estado = 'cerrada'
                rifa.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Rifa cerrada: "{rifa.titulo}" - Todos los boletos vendidos'
                    )
                )
        
        if rifas_pausadas > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🔍 Se pausaron {rifas_pausadas} rifa(s) para revisión administrativa'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('✅ No hay rifas que requieran pausa'))
