"""
Comando de gestión para probar la verificación de emails desde la terminal

Uso:
    python manage.py verify_email test@gmail.com
    python manage.py verify_email --list test@gmail.com fake@tempmail.com invalid@test.com
"""

from django.core.management.base import BaseCommand
from apps.core.email_validator import verify_email, get_email_report


class Command(BaseCommand):
    help = 'Verifica la validez de uno o más emails usando la API de AbstractAPI'

    def add_arguments(self, parser):
        parser.add_argument(
            'emails',
            nargs='+',
            type=str,
            help='Uno o más emails a verificar'
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Mostrar resultado en formato JSON'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='Verificar múltiples emails (modo lista)'
        )

    def handle(self, *args, **options):
        emails = options['emails']
        show_json = options['json']
        is_list = options['list']

        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write(self.style.HTTP_INFO('🔍 VERIFICACIÓN DE EMAILS'))
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write('')

        for email in emails:
            self.stdout.write(self.style.WARNING(f'\n📧 Verificando: {email}'))
            self.stdout.write('-' * 70)

            try:
                # Verificar el email
                result = verify_email(email)

                if show_json:
                    # Mostrar JSON
                    import json
                    self.stdout.write(json.dumps(result, indent=2))
                else:
                    # Mostrar reporte legible
                    report = get_email_report(email)
                    self.stdout.write(report)

                # Resultado final
                self.stdout.write('')
                if result.get('is_valid') and not result.get('is_disposable'):
                    self.stdout.write(self.style.SUCCESS('✅ RESULTADO: Email válido y seguro'))
                elif result.get('is_disposable'):
                    self.stdout.write(self.style.ERROR('❌ RESULTADO: Email desechable/temporal (rechazar)'))
                else:
                    self.stdout.write(self.style.ERROR('❌ RESULTADO: Email inválido (rechazar)'))

                if result.get('error'):
                    self.stdout.write(self.style.WARNING(f'⚠️  Error API: {result["error"]}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))

            if not is_list or email == emails[-1]:
                self.stdout.write('')

        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'✅ Verificación completada: {len(emails)} email(s)'))
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
