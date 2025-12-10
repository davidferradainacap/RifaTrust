"""
Script para poblar la base de datos con datos de prueba realistas
Crea usuarios, rifas, compras y patrocinios para testing
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configurar Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from apps.users.models import User
from apps.raffles.models import Raffle, Ticket, SponsorRequest

# Zona horaria de Chile
CHILE_TZ = timezone.get_current_timezone()

# ==================== DATOS PARA GENERAR USUARIOS ====================

NOMBRES = [
    'Juan', 'María', 'Pedro', 'Ana', 'Carlos', 'Lucía', 'José', 'Carmen',
    'Francisco', 'Isabel', 'Antonio', 'Dolores', 'Manuel', 'Pilar', 'David',
    'Teresa', 'Miguel', 'Rosa', 'Javier', 'Ángeles', 'Daniel', 'Patricia',
    'Alejandro', 'Laura', 'Fernando', 'Marta', 'Sergio', 'Cristina', 'Raúl',
    'Silvia', 'Enrique', 'Mercedes', 'Alberto', 'Beatriz', 'Roberto', 'Elena',
    'Luis', 'Raquel', 'Pablo', 'Monica', 'Jorge', 'Susana', 'Ángel', 'Victoria',
    'Diego', 'Natalia', 'Rubén', 'Gabriela', 'Adrián', 'Verónica', 'Óscar',
    'Andrea', 'Mario', 'Carolina', 'Gonzalo', 'Claudia', 'Ramón', 'Paula',
    'Felipe', 'Lorena', 'Iván', 'Sandra', 'Eduardo', 'Diana', 'Tomás', 'Alicia'
]

APELLIDOS = [
    'García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez',
    'Sánchez', 'Pérez', 'Martín', 'Gómez', 'Ruiz', 'Hernández', 'Jiménez',
    'Díaz', 'Álvarez', 'Moreno', 'Muñoz', 'Romero', 'Alonso', 'Gutiérrez',
    'Navarro', 'Torres', 'Domínguez', 'Vázquez', 'Ramos', 'Gil', 'Ramírez',
    'Serrano', 'Blanco', 'Suárez', 'Molina', 'Morales', 'Ortega', 'Delgado',
    'Castro', 'Ortiz', 'Rubio', 'Marín', 'Sanz', 'Iglesias', 'Medina', 'Garrido'
]

EMPRESAS_FAMOSAS = [
    'Coca-Cola Chile', 'Falabella', 'Ripley', 'Lider', 'Jumbo',
    'Samsung Chile', 'LG Electronics', 'Sony Chile', 'Apple Chile',
    'Banco de Chile', 'BancoEstado', 'Santander Chile', 'Banco Itaú',
    'Movistar Chile', 'Entel', 'Claro Chile', 'WOM',
    'Copec', 'Shell Chile', 'Petrobras Chile',
    'CCU (Cervecera)', 'Nestlé Chile', 'Unilever Chile',
    'Paris', 'Hites', 'La Polar'
]

TELEFONOS_CHILE = ['+569{:08d}'.format(random.randint(50000000, 99999999)) for _ in range(100)]

# ==================== DATOS PARA RIFAS ====================

TITULOS_RIFAS = [
    'Gran Sorteo iPhone 15 Pro Max',
    'Rifa Navideña - Smart TV Samsung 65"',
    'Sorteo Beneficencia - Laptop HP Gaming',
    'Rifa PlayStation 5 + Juegos',
    'Gran Sorteo Auto Toyota Corolla 2024',
    'Rifa Viaje a Cancún Todo Incluido',
    'Sorteo Bicicleta Eléctrica Trek',
    'Rifa Moto Honda CBR 500R',
    'Gran Sorteo Set Electrodomésticos',
    'Rifa Tablet iPad Pro + Apple Pencil',
    'Sorteo Consola Nintendo Switch OLED',
    'Rifa Drone DJI Mavic Pro',
    'Gran Sorteo Cámara Canon EOS R6',
    'Rifa Reloj Apple Watch Series 9',
    'Sorteo Auriculares Sony WH-1000XM5',
    'Rifa Robot Aspirador iRobot',
    'Gran Sorteo Notebook MacBook Air M2',
    'Rifa Guitarra Eléctrica Fender',
    'Sorteo Set Herramientas Bosch',
    'Rifa Parrilla Weber Genesis',
    'Gran Sorteo Xbox Series X',
    'Rifa Colchón King Size Premium',
    'Sorteo Máquina Café Nespresso',
    'Rifa Scooter Eléctrico Xiaomi',
    'Gran Sorteo Celular Samsung S24 Ultra'
]

DESCRIPCIONES_RIFAS = [
    'Increíble oportunidad de ganar un premio espectacular. Sorteo 100% transparente con verificación en vivo.',
    'Participa en nuestro sorteo y ayuda a una buena causa. Todos los fondos se destinan a {causa}.',
    'El sorteo más esperado del año. No te pierdas esta oportunidad única de ganar.',
    'Rifa benéfica con fines solidarios. Compra tu boleto y colabora con nuestra misión.',
    'Gran sorteo con premio garantizado. Boletos limitados, ¡no te quedes fuera!',
    'Sorteo transparente con notario público. Fecha y hora confirmadas.',
    'Participa y gana. Sorteo supervisado y verificado por autoridades competentes.',
]

CAUSAS_BENEFICAS = [
    'fundación de niños',
    'hospital regional',
    'centro de ancianos',
    'refugio de animales',
    'becas estudiantiles',
    'comedores comunitarios',
    'centros de rehabilitación'
]

PREMIOS = [
    {
        'nombre': 'iPhone 15 Pro Max 256GB',
        'descripcion': 'Último modelo de Apple, pantalla Super Retina XDR de 6.7", cámara de 48MP, chip A17 Pro, titanio grado aeroespacial.',
        'valor': Decimal('1299990.00')
    },
    {
        'nombre': 'Smart TV Samsung QLED 65"',
        'descripcion': 'TV Quantum Dot 4K, HDR10+, Tizen OS, sonido Dolby Atmos, diseño ultra delgado.',
        'valor': Decimal('899990.00')
    },
    {
        'nombre': 'Laptop HP Pavilion Gaming 16"',
        'descripcion': 'Intel Core i7 12th Gen, 16GB RAM, RTX 3060 6GB, SSD 512GB, pantalla 144Hz.',
        'valor': Decimal('1199990.00')
    },
    {
        'nombre': 'PlayStation 5 Digital + 3 Juegos',
        'descripcion': 'Consola PS5 Digital Edition, 825GB SSD, incluye FIFA 24, Spider-Man 2 y Gran Turismo 7.',
        'valor': Decimal('699990.00')
    },
    {
        'nombre': 'Auto Toyota Corolla Cross 2024',
        'descripcion': 'SUV híbrido, transmisión automática CVT, cámara 360°, Toyota Safety Sense, garantía 5 años.',
        'valor': Decimal('18990000.00')
    },
    {
        'nombre': 'Viaje a Cancún para 2 personas',
        'descripcion': '7 días / 6 noches en hotel 5 estrellas todo incluido, vuelos ida y vuelta, traslados aeropuerto.',
        'valor': Decimal('3500000.00')
    },
    {
        'nombre': 'Bicicleta Eléctrica Trek Allant+ 7',
        'descripcion': 'E-bike con motor Bosch, batería 500Wh, autonomía 120km, suspensión delantera.',
        'valor': Decimal('1890000.00')
    },
    {
        'nombre': 'Moto Honda CBR 500R',
        'descripcion': 'Deportiva 471cc, ABS, frenos de disco, computadora de abordo, velocímetro digital.',
        'valor': Decimal('4990000.00')
    },
    {
        'nombre': 'Set Electrodomésticos LG',
        'descripcion': 'Incluye: Refrigerador No Frost 350L, Lavadora 18kg, Microondas 30L, Aspiradora V5.',
        'valor': Decimal('1599990.00')
    },
    {
        'nombre': 'iPad Pro 12.9" M2 256GB',
        'descripcion': 'Chip M2, pantalla Liquid Retina XDR, Face ID, cámaras profesionales, incluye Apple Pencil 2.',
        'valor': Decimal('1499990.00')
    },
]

def crear_usuarios_participantes(cantidad=50):
    """Crea usuarios participantes con datos realistas"""
    print(f"\n🎭 Creando {cantidad} usuarios participantes...")
    participantes = []

    for i in range(cantidad):
        nombre = random.choice(NOMBRES)
        apellido = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
        nombre_completo = f"{nombre} {apellido}"
        email = f"participante{i+1}@rifatrust.cl"
        telefono = random.choice(TELEFONOS_CHILE)

        user = User.objects.create_user(
            email=email,
            nombre=nombre_completo,
            password='Participante123!',
            telefono=telefono,
            rol='participante',
            cuenta_validada=True,
            is_active=True
        )
        participantes.append(user)
        if (i + 1) % 10 == 0:
            print(f"  ✓ Creados {i + 1}/{cantidad} participantes")

    print(f"✅ {cantidad} participantes creados exitosamente")
    return participantes

def crear_usuarios_organizadores(cantidad=25):
    """Crea usuarios organizadores con datos realistas"""
    print(f"\n🎯 Creando {cantidad} usuarios organizadores...")
    organizadores = []

    for i in range(cantidad):
        nombre = random.choice(NOMBRES)
        apellido = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
        nombre_completo = f"{nombre} {apellido}"
        email = f"organizador{i+1}@rifatrust.cl"
        telefono = random.choice(TELEFONOS_CHILE)

        user = User.objects.create_user(
            email=email,
            nombre=nombre_completo,
            password='Organizador123!',
            telefono=telefono,
            rol='organizador',
            cuenta_validada=True,
            is_active=True
        )
        organizadores.append(user)
        if (i + 1) % 5 == 0:
            print(f"  ✓ Creados {i + 1}/{cantidad} organizadores")

    print(f"✅ {cantidad} organizadores creados exitosamente")
    return organizadores

def crear_usuarios_sponsors(cantidad=5):
    """Crea usuarios sponsors con nombres de empresas famosas"""
    print(f"\n🏢 Creando {cantidad} usuarios sponsors (empresas)...")
    sponsors = []
    empresas_seleccionadas = random.sample(EMPRESAS_FAMOSAS, cantidad)

    for i, empresa in enumerate(empresas_seleccionadas):
        email = f"sponsor{i+1}@rifatrust.cl"
        telefono = random.choice(TELEFONOS_CHILE)

        user = User.objects.create_user(
            email=email,
            nombre=empresa,
            password='Sponsor123!',
            telefono=telefono,
            rol='sponsor',
            cuenta_validada=True,
            is_active=True
        )
        sponsors.append(user)
        print(f"  ✓ Creado sponsor: {empresa}")

    print(f"✅ {cantidad} sponsors creados exitosamente")
    return sponsors

def crear_rifas(organizadores, sponsors, participantes):
    """Crea rifas con diferentes estados y fechas"""
    print(f"\n🎲 Creando rifas...")

    ahora = timezone.now()
    hoy = ahora.date()
    hora_actual = ahora.time()

    # 3 rifas que terminan hoy a las 04:55 (hora Chile)
    print("\n  📅 Creando 3 rifas que terminan hoy a las 04:55...")
    rifas_tempranas = []
    for i in range(3):
        organizador = random.choice(organizadores)
        premio = random.choice(PREMIOS)
        titulo = random.choice(TITULOS_RIFAS)
        descripcion = random.choice(DESCRIPCIONES_RIFAS)
        if '{causa}' in descripcion:
            descripcion = descripcion.format(causa=random.choice(CAUSAS_BENEFICAS))

        total_boletos = random.choice([100, 200, 300, 500, 1000])
        precio_boleto = Decimal(str(random.choice([500, 1000, 2000, 5000, 10000])))

        # Fecha de sorteo: hoy a las 04:55 Chile
        fecha_sorteo = timezone.make_aware(
            datetime.combine(hoy, datetime.min.time().replace(hour=4, minute=55))
        )

        # Fecha de inicio: hace 7 días
        fecha_inicio = ahora - timedelta(days=7)

        raffle = Raffle.objects.create(
            organizador=organizador,
            titulo=f"{titulo} #{i+1}",
            descripcion=descripcion,
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
        rifas_tempranas.append(raffle)
        print(f"    ✓ Rifa: {raffle.titulo} - Sorteo: {fecha_sorteo.strftime('%d/%m %H:%M')}")

    # Resto de rifas entre 13:00 y 18:00 hoy
    print("\n  📅 Creando rifas que terminan hoy entre 13:00 y 18:00...")
    rifas_tarde = []
    cantidad_rifas_tarde = random.randint(15, 20)

    for i in range(cantidad_rifas_tarde):
        organizador = random.choice(organizadores)
        premio = random.choice(PREMIOS)
        titulo = random.choice(TITULOS_RIFAS)
        descripcion = random.choice(DESCRIPCIONES_RIFAS)
        if '{causa}' in descripcion:
            descripcion = descripcion.format(causa=random.choice(CAUSAS_BENEFICAS))

        total_boletos = random.choice([100, 200, 300, 500, 1000, 1500, 2000])
        precio_boleto = Decimal(str(random.choice([500, 1000, 2000, 3000, 5000, 10000])))

        # Hora aleatoria entre 13:00 y 18:00
        hora = random.randint(13, 17)
        minuto = random.choice([0, 15, 30, 45])

        fecha_sorteo = timezone.make_aware(
            datetime.combine(hoy, datetime.min.time().replace(hour=hora, minute=minuto))
        )

        # Fecha de inicio: entre hace 2 y 10 días
        dias_atras = random.randint(2, 10)
        fecha_inicio = ahora - timedelta(days=dias_atras)

        # Estado aleatorio pero mayormente activas
        estado = random.choices(
            ['activa', 'aprobada', 'pendiente_aprobacion'],
            weights=[0.7, 0.2, 0.1]
        )[0]

        raffle = Raffle.objects.create(
            organizador=organizador,
            titulo=f"{titulo} #{i+4}",
            descripcion=descripcion,
            precio_boleto=precio_boleto,
            total_boletos=total_boletos,
            boletos_vendidos=0,
            fecha_inicio=fecha_inicio,
            fecha_sorteo=fecha_sorteo,
            estado=estado,
            premio_principal=premio['nombre'],
            descripcion_premio=premio['descripcion'],
            valor_premio=premio['valor'],
            permite_multiples_boletos=True,
            max_boletos_por_usuario=random.choice([5, 10, 15, 20])
        )
        rifas_tarde.append(raffle)

        if (i + 1) % 5 == 0:
            print(f"    ✓ Creadas {i + 1}/{cantidad_rifas_tarde} rifas")

    todas_las_rifas = rifas_tempranas + rifas_tarde
    print(f"\n✅ Total de rifas creadas: {len(todas_las_rifas)}")

    # Crear solicitudes de sponsors
    crear_solicitudes_sponsors(todas_las_rifas, sponsors)

    # Crear compras de boletos
    crear_compras_boletos(todas_las_rifas, participantes, sponsors)

    return todas_las_rifas

def crear_solicitudes_sponsors(rifas, sponsors):
    """Crea solicitudes de sponsors para las rifas"""
    print(f"\n💼 Creando solicitudes de sponsors...")

    # Cada sponsor hace entre 3 y 6 solicitudes
    total_solicitudes = 0
    for sponsor in sponsors:
        cantidad = random.randint(3, 6)
        rifas_seleccionadas = random.sample(rifas, min(cantidad, len(rifas)))

        for raffle in rifas_seleccionadas:
            monto = Decimal(str(random.choice([50000, 100000, 200000, 500000, 1000000])))
            estado = random.choices(
                ['pendiente', 'aprobada', 'rechazada'],
                weights=[0.3, 0.6, 0.1]
            )[0]

            SponsorRequest.objects.create(
                rifa=raffle,
                sponsor=sponsor,
                monto_aporte=monto,
                mensaje=f"Estamos interesados en patrocinar su rifa '{raffle.titulo}'. "
                        f"Ofrecemos ${monto:,.0f} para apoyar esta iniciativa.",
                estado=estado
            )
            total_solicitudes += 1

    print(f"✅ {total_solicitudes} solicitudes de sponsors creadas")

def crear_compras_boletos(rifas, participantes, sponsors):
    """Crea compras de boletos por participantes y sponsors"""
    print(f"\n🎫 Creando compras de boletos...")

    total_tickets = 0

    for raffle in rifas:
        if raffle.estado not in ['activa', 'aprobada']:
            continue

        # Determinar cuántos boletos se venden (entre 30% y 90% del total)
        porcentaje_venta = random.uniform(0.3, 0.9)
        boletos_a_vender = int(raffle.total_boletos * porcentaje_venta)

        # Mezclar participantes y algunos sponsors para comprar
        compradores = participantes + random.sample(sponsors, min(3, len(sponsors)))
        random.shuffle(compradores)

        numeros_disponibles = list(range(1, raffle.total_boletos + 1))
        random.shuffle(numeros_disponibles)

        boletos_vendidos = 0

        for comprador in compradores:
            if boletos_vendidos >= boletos_a_vender:
                break

            # Cantidad de boletos que compra este usuario
            max_compra = min(
                raffle.max_boletos_por_usuario,
                boletos_a_vender - boletos_vendidos,
                random.randint(1, 10)
            )

            cantidad = random.randint(1, max_compra)

            # Seleccionar números
            numeros_comprados = numeros_disponibles[:cantidad]
            numeros_disponibles = numeros_disponibles[cantidad:]

            # Crear tickets
            for numero in numeros_comprados:
                Ticket.objects.create(
                    rifa=raffle,
                    usuario=comprador,
                    numero_boleto=numero,
                    monto_pagado=raffle.precio_boleto,
                    estado_pago='completado',
                    metodo_pago=random.choice(['webpay', 'mercadopago', 'transferencia'])
                )
                total_tickets += 1
                boletos_vendidos += 1

        # Actualizar boletos vendidos en la rifa
        raffle.boletos_vendidos = boletos_vendidos
        raffle.save()

    print(f"✅ {total_tickets} boletos comprados en total")

def main():
    """Función principal que ejecuta todo el proceso"""
    print("=" * 60)
    print("🎰 SCRIPT DE POBLACIÓN DE BASE DE DATOS - RIFATRUST")
    print("=" * 60)

    # Limpiar datos existentes (opcional)
    respuesta = input("\n⚠️  ¿Deseas limpiar todos los datos existentes? (s/N): ")
    if respuesta.lower() == 's':
        print("\n🗑️  Limpiando base de datos...")
        Ticket.objects.all().delete()
        SponsorRequest.objects.all().delete()
        Raffle.objects.all().delete()
        User.objects.filter(rol__in=['participante', 'organizador', 'sponsor']).delete()
        print("✅ Base de datos limpiada")

    # Crear usuarios
    participantes = crear_usuarios_participantes(50)
    organizadores = crear_usuarios_organizadores(25)
    sponsors = crear_usuarios_sponsors(5)

    # Crear rifas y compras
    rifas = crear_rifas(organizadores, sponsors, participantes)

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"👥 Participantes creados: {len(participantes)}")
    print(f"🎯 Organizadores creados: {len(organizadores)}")
    print(f"🏢 Sponsors creados: {len(sponsors)}")
    print(f"🎲 Rifas creadas: {len(rifas)}")
    print(f"🎫 Boletos vendidos: {Ticket.objects.count()}")
    print(f"💼 Solicitudes sponsors: {SponsorRequest.objects.count()}")
    print("\n✅ Población completada exitosamente!")
    print("\n📝 Credenciales:")
    print("   - Participantes: participante1@rifatrust.cl hasta participante50@rifatrust.cl")
    print("   - Password: Participante123!")
    print("   - Organizadores: organizador1@rifatrust.cl hasta organizador25@rifatrust.cl")
    print("   - Password: Organizador123!")
    print("   - Sponsors: sponsor1@rifatrust.cl hasta sponsor5@rifatrust.cl")
    print("   - Password: Sponsor123!")
    print("=" * 60)

if __name__ == '__main__':
    main()
