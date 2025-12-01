"""
Comando para verificar la integridad de los campos encriptados
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import Profile
from apps.payments.models import Payment
from apps.core.encryption import encrypt_data, decrypt_data

User = get_user_model()

class Command(BaseCommand):
    help = 'Verifica la integridad de los campos encriptados'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Verificando Campos Encriptados ===\n'))
        
        errors = 0
        warnings = 0
        
        # Verificar usuarios
        self.stdout.write('Verificando usuarios...')
        users = User.objects.all()
        for user in users:
            try:
                if user.telefono:
                    # Intentar acceder al campo (esto desencripta automáticamente)
                    _ = user.telefono
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error en usuario {user.id}: {e}'))
                errors += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ {users.count()} usuarios verificados\n'))
        
        # Verificar perfiles
        self.stdout.write('Verificando perfiles...')
        profiles = Profile.objects.all()
        for profile in profiles:
            try:
                if profile.direccion:
                    _ = profile.direccion
                if profile.ciudad:
                    _ = profile.ciudad
                if profile.codigo_postal:
                    _ = profile.codigo_postal
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error en perfil {profile.id}: {e}'))
                errors += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ {profiles.count()} perfiles verificados\n'))
        
        # Verificar pagos
        self.stdout.write('Verificando pagos...')
        payments = Payment.objects.all()
        for payment in payments:
            try:
                if payment.transaction_id:
                    _ = payment.transaction_id
                if payment.payment_intent_id:
                    _ = payment.payment_intent_id
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error en pago {payment.id}: {e}'))
                errors += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ {payments.count()} pagos verificados\n'))
        
        # Test de encriptación/desencriptación
        self.stdout.write('Probando encriptación/desencriptación...')
        test_data = "Dato de prueba 123!@#"
        try:
            encrypted = encrypt_data(test_data)
            decrypted = decrypt_data(encrypted)
            if test_data == decrypted:
                self.stdout.write(self.style.SUCCESS('  ✅ Encriptación funciona correctamente\n'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ Error: dato desencriptado no coincide\n'))
                errors += 1
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error en test de encriptación: {e}\n'))
            errors += 1
        
        # Resumen
        self.stdout.write(self.style.SUCCESS('=== Resumen ==='))
        if errors == 0:
            self.stdout.write(self.style.SUCCESS(f'✅ Todo correcto. Todos los campos encriptados funcionan bien.'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ Se encontraron {errors} errores.'))
        
        if warnings > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  {warnings} advertencias'))
