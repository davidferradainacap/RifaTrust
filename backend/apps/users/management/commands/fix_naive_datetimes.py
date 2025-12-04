"""
Comando para corregir datetimes naive (sin timezone) en la base de datos.
Convierte todos los datetimes naive a aware usando la zona horaria de Django.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction, connection
from apps.users.models import User
from apps.payments.models import Payment
from datetime import datetime
import pytz
import warnings


class Command(BaseCommand):
    help = 'Corrige datetimes naive en la base de datos convirtiéndolos a aware'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se haría sin hacer cambios reales',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        tz = pytz.timezone('America/Santiago')

        if dry_run:
            self.stdout.write(self.style.WARNING('=== MODO DRY RUN (No se harán cambios) ===\n'))

        total_fixed = 0

        # ============================
        # CORREGIR USUARIOS
        # ============================
        self.stdout.write('\n📋 Revisando Users...')
        users_to_fix = []

        for user in User.objects.all():
            if user.fecha_registro and timezone.is_naive(user.fecha_registro):
                users_to_fix.append(user)
                self.stdout.write(
                    f'  ⚠️  User {user.id} ({user.email}): {user.fecha_registro} es naive'
                )

        if users_to_fix:
            if not dry_run:
                with transaction.atomic():
                    for user in users_to_fix:
                        # Convertir a aware usando la zona horaria configurada
                        user.fecha_registro = timezone.make_aware(
                            user.fecha_registro,
                            tz
                        )
                        user.save(update_fields=['fecha_registro'])
                        total_fixed += 1

                self.stdout.write(
                    self.style.SUCCESS(f'✅ {len(users_to_fix)} usuarios corregidos')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'   Se corregirían {len(users_to_fix)} usuarios')
                )
        else:
            self.stdout.write(self.style.SUCCESS('✅ Todos los usuarios tienen datetime aware'))

        # ============================
        # CORREGIR PAGOS
        # ============================
        self.stdout.write('\n💳 Revisando Payments...')
        payments_to_fix = []

        for payment in Payment.objects.all():
            if payment.fecha_creacion and timezone.is_naive(payment.fecha_creacion):
                payments_to_fix.append(payment)
                self.stdout.write(
                    f'  ⚠️  Payment {payment.id}: {payment.fecha_creacion} es naive'
                )

        if payments_to_fix:
            if not dry_run:
                with transaction.atomic():
                    for payment in payments_to_fix:
                        payment.fecha_creacion = timezone.make_aware(
                            payment.fecha_creacion,
                            tz
                        )
                        payment.save(update_fields=['fecha_creacion'])
                        total_fixed += 1

                self.stdout.write(
                    self.style.SUCCESS(f'✅ {len(payments_to_fix)} pagos corregidos')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'   Se corregirían {len(payments_to_fix)} pagos')
                )
        else:
            self.stdout.write(self.style.SUCCESS('✅ Todos los pagos tienen datetime aware'))

        # ============================
        # RESUMEN FINAL
        # ============================
        self.stdout.write('\n' + '='*50)
        if dry_run:
            total_to_fix = len(users_to_fix) + len(payments_to_fix)
            if total_to_fix > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'\n📊 Se corregirían {total_to_fix} registros en total.\n'
                        f'   Ejecuta sin --dry-run para aplicar los cambios.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n✨ No hay registros que corregir. Todo está bien!'
                    )
                )
        else:
            if total_fixed > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✨ ¡Completado! {total_fixed} registros corregidos exitosamente.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n✨ No había registros que corregir. Todo está bien!'
                    )
                )

        self.stdout.write('='*50 + '\n')
