#!/usr/bin/env python
"""
Script para crear rifas usando usuarios existentes
Ejecutar: python populate_rifas_only.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from apps.users.models import User
from apps.raffles.models import Raffle, Ticket

def main():
    print("=" * 60)
    print("🎰 CREANDO RIFAS CON USUARIOS EXISTENTES")
    print("=" * 60)

    # Obtener usuarios existentes
    participantes = list(User.objects.filter(rol='participante', email__contains='@rifatrust.cl'))
    organizadores = list(User.objects.filter(rol='organizador', email__contains='@rifatrust.cl'))

    print(f"\n✅ {len(participantes)} participantes encontrados")
    print(f"✅ {len(organizadores)} organizadores encontrados")

    if not participantes or not organizadores:
        print("\n❌ Error: No hay usuarios suficientes en la base de datos")
        return

    premios = [
        {
            'nombre': 'iPhone 15 Pro Max 256GB',
            'descripcion': 'Último modelo de Apple, pantalla Super Retina XDR de 6.7", cámara de 48MP, chip A17 Pro.',
            'valor': Decimal('1299990.00')
        },
        {
            'nombre': 'Smart TV Samsung QLED 65"',
            'descripcion': 'TV Quantum Dot 4K, HDR10+, Tizen OS, sonido Dolby Atmos.',
            'valor': Decimal('899990.00')
        },
        {
            'nombre': 'Laptop HP Pavilion Gaming',
            'descripcion': 'Intel Core i7, 16GB RAM, RTX 3060, SSD 512GB.',
            'valor': Decimal('1199990.00')
        },
        {
            'nombre': 'PlayStation 5 + Juegos',
            'descripcion': 'PS5 Digital, 825GB SSD, incluye FIFA 24, Spider-Man 2.',
            'valor': Decimal('699990.00')
        },
        {
            'nombre': 'Auto Toyota Corolla Cross',
            'descripcion': 'SUV híbrido, transmisión CVT, cámara 360°.',
            'valor': Decimal('18990000.00')
        },
        {
            'nombre': 'Viaje a Cancún 2 personas',
            'descripcion': '7 días todo incluido, hotel 5 estrellas, vuelos.',
            'valor': Decimal('3500000.00')
        },
        {
            'nombre': 'Bicicleta Eléctrica Trek',
            'descripcion': 'E-bike motor Bosch, batería 500Wh, 120km autonomía.',
            'valor': Decimal('1890000.00')
        },
        {
            'nombre': 'Moto Honda CBR 500R',
            'descripcion': 'Deportiva 471cc, ABS, frenos de disco.',
            'valor': Decimal('4990000.00')
        },
        {
            'nombre': 'Set Electrodomésticos LG',
            'descripcion': 'Refrigerador, Lavadora, Microondas, Aspiradora.',
            'valor': Decimal('1599990.00')
        },
        {
            'nombre': 'iPad Pro 12.9" M2 + Pencil',
            'descripcion': 'Chip M2, Liquid Retina XDR, incluye Apple Pencil 2.',
            'valor': Decimal('1499990.00')
        },
    ]

    ahora = timezone.now()
    hoy = ahora.date()

    rifas_creadas = 0
    boletos_totales = 0

    # 3 rifas que terminan a las 04:55
    print("\n📅 Creando rifas que terminan a las 04:55...")
    for i in range(3):
        premio = random.choice(premios)
        organizador = random.choice(organizadores)

        total_boletos = random.choice([100, 200, 300, 500, 1000])
        precio_boleto = Decimal(str(random.choice([500, 1000, 2000, 5000, 10000])))

        fecha_sorteo = timezone.make_aware(
            datetime.combine(hoy, datetime.min.time().replace(hour=4, minute=55))
        )
        fecha_inicio = timezone.now() - timedelta(days=7)

        titulo = f"Gran Sorteo {premio['nombre']} #{rifas_creadas + 1}"

        raffle = Raffle.objects.create(
            organizador=organizador,
            titulo=titulo,
            descripcion=f'Sorteo transparente del premio: {premio["nombre"]}. Compra tu boleto y participa.',
            precio_boleto=precio_boleto,
            total_boletos=total_boletos,
            boletos_vendidos=0,
            fecha_inicio=fecha_inicio,
            fecha_sorteo=fecha_sorteo,
            estado='activa',
            premio_principal=premio['nombre'],
            descripcion_premio=premio['descripcion'],
            valor_premio=premio['valor'],
            permite_multiples_boletos=True,
            max_boletos_por_usuario=random.choice([5, 10, 20])
        )

        # Crear boletos
        porcentaje_venta = random.uniform(0.4, 0.85)
        boletos_a_vender = int(total_boletos * porcentaje_venta)

        compradores = random.sample(participantes, min(30, len(participantes)))
        numeros_disponibles = list(range(1, total_boletos + 1))
        random.shuffle(numeros_disponibles)

        boletos_vendidos = 0
        for comprador in compradores:
            if boletos_vendidos >= boletos_a_vender:
                break

            max_a_comprar = min(5, boletos_a_vender - boletos_vendidos, len(numeros_disponibles))
            if max_a_comprar <= 0:
                break

            cantidad = random.randint(1, max_a_comprar)

            for _ in range(cantidad):
                if not numeros_disponibles or boletos_vendidos >= boletos_a_vender:
                    break

                numero = numeros_disponibles.pop(0)

                Ticket.objects.create(
                    rifa=raffle,
                    usuario=comprador,
                    numero_boleto=numero,
                    monto_pagado=precio_boleto,
                    estado_pago='completado',
                    metodo_pago=random.choice(['webpay', 'mercadopago'])
                )
                boletos_vendidos += 1

        raffle.boletos_vendidos = boletos_vendidos
        raffle.save(update_fields=['boletos_vendidos'])

        print(f"  ✓ {titulo[:50]}... - {boletos_vendidos}/{total_boletos} boletos")
        rifas_creadas += 1
        boletos_totales += boletos_vendidos

    # Rifas entre 13:00 y 18:00
    print("\n📅 Creando rifas que terminan entre 13:00-18:00...")
    cantidad_tarde = random.randint(15, 20)

    for i in range(cantidad_tarde):
        premio = random.choice(premios)
        organizador = random.choice(organizadores)

        total_boletos = random.choice([100, 200, 300, 500, 1000])
        precio_boleto = Decimal(str(random.choice([500, 1000, 2000, 5000, 10000])))

        hora = random.randint(13, 17)
        minuto = random.choice([0, 15, 30, 45])

        fecha_sorteo = timezone.make_aware(
            datetime.combine(hoy, datetime.min.time().replace(hour=hora, minute=minuto))
        )
        fecha_inicio = timezone.now() - timedelta(days=random.randint(2, 10))

        titulo = f"Rifa Especial {premio['nombre']} #{rifas_creadas + 1}"

        raffle = Raffle.objects.create(
            organizador=organizador,
            titulo=titulo,
            descripcion=f'Sorteo transparente del premio: {premio["nombre"]}. Compra tu boleto y participa.',
            precio_boleto=precio_boleto,
            total_boletos=total_boletos,
            boletos_vendidos=0,
            fecha_inicio=fecha_inicio,
            fecha_sorteo=fecha_sorteo,
            estado='activa',
            premio_principal=premio['nombre'],
            descripcion_premio=premio['descripcion'],
            valor_premio=premio['valor'],
            permite_multiples_boletos=True,
            max_boletos_por_usuario=random.choice([5, 10, 20])
        )

        # Crear boletos
        porcentaje_venta = random.uniform(0.4, 0.85)
        boletos_a_vender = int(total_boletos * porcentaje_venta)

        compradores = random.sample(participantes, min(30, len(participantes)))
        numeros_disponibles = list(range(1, total_boletos + 1))
        random.shuffle(numeros_disponibles)

        boletos_vendidos = 0
        for comprador in compradores:
            if boletos_vendidos >= boletos_a_vender:
                break

            max_a_comprar = min(5, boletos_a_vender - boletos_vendidos, len(numeros_disponibles))
            if max_a_comprar <= 0:
                break

            cantidad = random.randint(1, max_a_comprar)

            for _ in range(cantidad):
                if not numeros_disponibles or boletos_vendidos >= boletos_a_vender:
                    break

                numero = numeros_disponibles.pop(0)

                Ticket.objects.create(
                    rifa=raffle,
                    usuario=comprador,
                    numero_boleto=numero,
                    monto_pagado=precio_boleto,
                    estado_pago='completado',
                    metodo_pago=random.choice(['webpay', 'mercadopago'])
                )
                boletos_vendidos += 1

        raffle.boletos_vendidos = boletos_vendidos
        raffle.save(update_fields=['boletos_vendidos'])

        print(f"  ✓ {titulo[:50]}... - {boletos_vendidos}/{total_boletos} boletos")
        rifas_creadas += 1
        boletos_totales += boletos_vendidos

    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print(f"🎲 Rifas creadas: {rifas_creadas}")
    print(f"🎫 Boletos vendidos: {boletos_totales}")
    print(f"👥 Participantes: {len(participantes)}")
    print(f"🎯 Organizadores: {len(organizadores)}")
    print("\n✅ ¡Población completada exitosamente!")
    print("=" * 60)

if __name__ == '__main__':
    main()
