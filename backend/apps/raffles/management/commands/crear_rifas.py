"""
Management command simple para crear rifas con boletos vendidos
Ejecutar con: python manage.py crear_rifas
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from decimal import Decimal
import random

from apps.users.models import User
from apps.raffles.models import Raffle, Ticket


class Command(BaseCommand):
    help = 'Crea rifas con boletos vendidos usando usuarios existentes'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("🎲 CREANDO RIFAS CON BOLETOS"))
        self.stdout.write("=" * 60)

        # Obtener usuarios existentes
        participantes = list(User.objects.filter(rol='participante'))
        organizadores = list(User.objects.filter(rol='organizador'))

        self.stdout.write(f"\n✅ Encontrados {len(participantes)} participantes")
        self.stdout.write(f"✅ Encontrados {len(organizadores)} organizadores")

        if not participantes or not organizadores:
            self.stdout.write(self.style.ERROR("\n❌ No hay suficientes usuarios"))
            return

        premios = [
            ('iPhone 15 Pro Max 256GB', 'Último modelo de Apple', Decimal('1299990.00')),
            ('Smart TV Samsung QLED 65"', 'TV Quantum Dot 4K', Decimal('899990.00')),
            ('Laptop HP Pavilion Gaming', 'Intel Core i7, 16GB RAM', Decimal('1199990.00')),
            ('PlayStation 5 + Juegos', 'PS5 Digital con juegos', Decimal('699990.00')),
            ('Auto Toyota Corolla Cross', 'SUV híbrido', Decimal('18990000.00')),
            ('Viaje a Cancún 2 personas', '7 días todo incluido', Decimal('3500000.00')),
            ('Bicicleta Eléctrica Trek', 'E-bike motor Bosch', Decimal('1890000.00')),
            ('Moto Honda CBR 500R', 'Deportiva 471cc', Decimal('4990000.00')),
            ('Set Electrodomésticos LG', 'Refrigerador, Lavadora', Decimal('1599990.00')),
            ('iPad Pro 12.9" M2', 'Con Apple Pencil 2', Decimal('1499990.00')),
        ]

        ahora = timezone.now()
        hoy = ahora.date()
        rifas_creadas = 0
        boletos_totales = 0

        # 3 rifas que terminan a las 04:55
        self.stdout.write("\n📅 Creando rifas para las 04:55...")
        for i in range(3):
            nombre, desc, valor = random.choice(premios)
            organizador = random.choice(organizadores)

            total_boletos = random.choice([100, 200, 300, 500])
            precio_boleto = Decimal(str(random.choice([1000, 2000, 5000, 10000])))

            fecha_sorteo = timezone.make_aware(
                datetime.combine(hoy, datetime.min.time().replace(hour=4, minute=55))
            )

            raffle = Raffle.objects.create(
                organizador=organizador,
                titulo=f"Sorteo {nombre} #{rifas_creadas + 1}",
                descripcion=f"{desc}. ¡Participa y gana!",
                precio_boleto=precio_boleto,
                total_boletos=total_boletos,
                boletos_vendidos=0,
                fecha_inicio=ahora - timedelta(days=7),
                fecha_sorteo=fecha_sorteo,
                estado='activa',
                premio_principal=nombre,
                descripcion_premio=desc,
                valor_premio=valor,
                permite_multiples_boletos=True,
                max_boletos_por_usuario=10
            )

            # Crear boletos (40-85% vendidos)
            boletos_vendidos = self.crear_boletos(raffle, participantes, total_boletos, precio_boleto)
            boletos_totales += boletos_vendidos
            rifas_creadas += 1

            self.stdout.write(f"  ✓ Rifa #{rifas_creadas}: {boletos_vendidos}/{total_boletos} boletos")

        # 15-20 rifas entre 13:00 y 18:00
        self.stdout.write("\n📅 Creando rifas para 13:00-18:00...")
        cantidad = random.randint(15, 20)

        for i in range(cantidad):
            nombre, desc, valor = random.choice(premios)
            organizador = random.choice(organizadores)

            total_boletos = random.choice([100, 200, 300, 500])
            precio_boleto = Decimal(str(random.choice([1000, 2000, 5000, 10000])))

            hora = random.randint(13, 17)
            minuto = random.choice([0, 15, 30, 45])

            fecha_sorteo = timezone.make_aware(
                datetime.combine(hoy, datetime.min.time().replace(hour=hora, minute=minuto))
            )

            raffle = Raffle.objects.create(
                organizador=organizador,
                titulo=f"Gran Rifa {nombre} #{rifas_creadas + 1}",
                descripcion=f"{desc}. ¡No te lo pierdas!",
                precio_boleto=precio_boleto,
                total_boletos=total_boletos,
                boletos_vendidos=0,
                fecha_inicio=ahora - timedelta(days=random.randint(2, 10)),
                fecha_sorteo=fecha_sorteo,
                estado='activa',
                premio_principal=nombre,
                descripcion_premio=desc,
                valor_premio=valor,
                permite_multiples_boletos=True,
                max_boletos_por_usuario=10
            )

            # Crear boletos
            boletos_vendidos = self.crear_boletos(raffle, participantes, total_boletos, precio_boleto)
            boletos_totales += boletos_vendidos
            rifas_creadas += 1

            self.stdout.write(f"  ✓ Rifa #{rifas_creadas}: {boletos_vendidos}/{total_boletos} boletos")

        # Resumen
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("📊 RESUMEN"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"🎲 Rifas creadas: {rifas_creadas}")
        self.stdout.write(f"🎫 Boletos vendidos: {boletos_totales}")
        self.stdout.write(f"👥 Participantes: {len(participantes)}")
        self.stdout.write(f"🎯 Organizadores: {len(organizadores)}")
        self.stdout.write("\n" + self.style.SUCCESS("✅ ¡Completado!"))
        self.stdout.write("=" * 60)

    def crear_boletos(self, raffle, participantes, total_boletos, precio_boleto):
        """Crea boletos vendidos para una rifa"""
        # Determinar cuántos boletos vender (40-85%)
        porcentaje = random.uniform(0.4, 0.85)
        cantidad_a_vender = int(total_boletos * porcentaje)

        # Seleccionar compradores aleatorios
        compradores = random.sample(participantes, min(30, len(participantes)))

        # Números disponibles
        numeros = list(range(1, total_boletos + 1))
        random.shuffle(numeros)

        vendidos = 0
        for comprador in compradores:
            if vendidos >= cantidad_a_vender:
                break

            # Cada comprador compra 1-5 boletos
            max_compra = min(5, cantidad_a_vender - vendidos, len(numeros))
            if max_compra <= 0:
                break

            cantidad = random.randint(1, max_compra)

            for _ in range(cantidad):
                if not numeros or vendidos >= cantidad_a_vender:
                    break

                numero = numeros.pop()

                # Generar código QR único
                import uuid
                codigo_qr = f"TKT-{raffle.id}-{numero}-{uuid.uuid4().hex[:8]}"

                Ticket.objects.create(
                    rifa=raffle,
                    usuario=comprador,
                    numero_boleto=numero,
                    estado='pagado',
                    codigo_qr=codigo_qr
                )
                vendidos += 1

        # Actualizar contador en la rifa
        raffle.boletos_vendidos = vendidos
        raffle.save(update_fields=['boletos_vendidos'])

        return vendidos
