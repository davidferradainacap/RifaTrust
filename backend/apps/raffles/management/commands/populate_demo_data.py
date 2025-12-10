"""
Management command para poblar la base de datos con datos de prueba realistas
Ejecutar con: python manage.py populate_demo_data
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
    help = 'Pobla la base de datos con datos de demostración realistas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpia los datos existentes antes de poblar',
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("🎰 POBLACIÓN DE BASE DE DATOS - RIFATRUST"))
        self.stdout.write("=" * 60)

        if options['clear']:
            self.stdout.write("\n🗑️  Limpiando base de datos...")
            Ticket.objects.all().delete()
            Raffle.objects.all().delete()
            User.objects.filter(rol__in=['participante', 'organizador', 'sponsor']).delete()
            self.stdout.write(self.style.SUCCESS("✅ Base de datos limpiada"))

        # Datos de generación
        self.nombres = [
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

        self.apellidos = [
            'García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez',
            'Sánchez', 'Pérez', 'Martín', 'Gómez', 'Ruiz', 'Hernández', 'Jiménez',
            'Díaz', 'Álvarez', 'Moreno', 'Muñoz', 'Romero', 'Alonso', 'Gutiérrez',
            'Navarro', 'Torres', 'Domínguez', 'Vázquez', 'Ramos', 'Gil', 'Ramírez',
            'Serrano', 'Blanco', 'Suárez', 'Molina', 'Morales', 'Ortega', 'Delgado'
        ]

        self.empresas_famosas = [
            'Coca-Cola Chile', 'Falabella', 'Ripley', 'Lider', 'Jumbo',
            'Samsung Chile', 'LG Electronics', 'Sony Chile', 'Apple Chile',
            'Banco de Chile', 'BancoEstado', 'Santander Chile', 'Banco Itaú',
            'Movistar Chile', 'Entel', 'Claro Chile', 'WOM',
            'Copec', 'Shell Chile', 'Petrobras Chile',
            'CCU Cervecera', 'Nestlé Chile', 'Unilever Chile',
            'Paris', 'Hites', 'La Polar'
        ]

        self.premios = [
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

        # Crear usuarios
        participantes = self.crear_participantes(50)
        organizadores = self.crear_organizadores(25)
        sponsors = self.crear_sponsors(5)

        # Crear rifas y compras
        self.crear_rifas_completas(organizadores, sponsors, participantes)

        # Resumen
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("📊 RESUMEN FINAL"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"👥 Participantes: {len(participantes)}")
        self.stdout.write(f"🎯 Organizadores: {len(organizadores)}")
        self.stdout.write(f"🏢 Sponsors: {len(sponsors)}")
        self.stdout.write(f"🎲 Rifas: {Raffle.objects.count()}")
        self.stdout.write(f"🎫 Boletos vendidos: {Ticket.objects.count()}")
        self.stdout.write("\n" + self.style.SUCCESS("✅ Población completada!"))
        self.stdout.write("=" * 60)

    def crear_participantes(self, cantidad):
        """Crea usuarios participantes"""
        self.stdout.write(f"\n🎭 Obteniendo/Creando {cantidad} participantes...")
        participantes = []

        for i in range(cantidad):
            email = f"participante{i+1}@rifatrust.cl"

            # Intentar obtener usuario existente primero
            try:
                user = User.objects.get(email=email)
                participantes.append(user)
            except User.DoesNotExist:
                # Si no existe, crearlo
                nombre = random.choice(self.nombres)
                apellido = f"{random.choice(self.apellidos)} {random.choice(self.apellidos)}"
                telefono = f"+569{random.randint(50000000, 99999999)}"

                try:
                    user = User.objects.create_user(
                        email=email,
                        nombre=f"{nombre} {apellido}",
                        password='Participante123!',
                        telefono=telefono,
                        rol='participante',
                        cuenta_validada=True
                    )
                    participantes.append(user)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ⚠ Error creando {email}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"✅ {len(participantes)} participantes disponibles"))
        return participantes

    def crear_organizadores(self, cantidad):
        """Crea usuarios organizadores"""
        self.stdout.write(f"\n🎯 Obteniendo/Creando {cantidad} organizadores...")
        organizadores = []

        for i in range(cantidad):
            email = f"organizador{i+1}@rifatrust.cl"

            # Intentar obtener usuario existente primero
            try:
                user = User.objects.get(email=email)
                organizadores.append(user)
            except User.DoesNotExist:
                # Si no existe, crearlo
                nombre = random.choice(self.nombres)
                apellido = f"{random.choice(self.apellidos)} {random.choice(self.apellidos)}"
                telefono = f"+569{random.randint(50000000, 99999999)}"

                try:
                    user = User.objects.create_user(
                        email=email,
                        nombre=f"{nombre} {apellido}",
                        password='Organizador123!',
                        telefono=telefono,
                        rol='organizador',
                        cuenta_validada=True
                    )
                    organizadores.append(user)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ⚠ Error creando {email}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"✅ {len(organizadores)} organizadores disponibles"))
        return organizadores

    def crear_sponsors(self, cantidad):
        """Crea usuarios sponsors"""
        self.stdout.write(f"\n🏢 Obteniendo/Creando {cantidad} sponsors...")
        sponsors = []
        empresas = random.sample(self.empresas_famosas, cantidad)

        for i, empresa in enumerate(empresas):
            email = f"sponsor{i+1}@rifatrust.cl"

            # Intentar obtener usuario existente primero
            try:
                user = User.objects.get(email=email)
                sponsors.append(user)
                self.stdout.write(f"  ✓ {empresa} (existente)")
            except User.DoesNotExist:
                # Si no existe, crearlo
                telefono = f"+569{random.randint(50000000, 99999999)}"

                try:
                    user = User.objects.create_user(
                        email=email,
                        nombre=empresa,
                        password='Sponsor123!',
                        telefono=telefono,
                        rol='sponsor',
                        cuenta_validada=True
                    )
                    sponsors.append(user)
                    self.stdout.write(f"  ✓ {empresa} (nuevo)")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ⚠ Error creando {empresa}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"✅ {len(sponsors)} sponsors disponibles"))
        return sponsors

    @transaction.atomic
    def crear_rifas_completas(self, organizadores, sponsors, participantes):
        """Crea rifas con diferentes fechas y compras"""
        self.stdout.write(f"\n🎲 Creando rifas...")

        ahora = timezone.now()
        hoy = ahora.date()

        # 3 rifas que terminan a las 04:55
        self.stdout.write("\n  📅 Rifas que terminan hoy a las 04:55...")
        for i in range(3):
            self.crear_rifa_individual(
                organizadores, sponsors, participantes,
                hoy, 4, 55, i+1, "temprana"
            )

        # Rifas entre 13:00 y 18:00
        self.stdout.write("\n  📅 Rifas que terminan entre 13:00 y 18:00...")
        cantidad_tarde = random.randint(15, 20)
        for i in range(cantidad_tarde):
            hora = random.randint(13, 17)
            minuto = random.choice([0, 15, 30, 45])
            self.crear_rifa_individual(
                organizadores, sponsors, participantes,
                hoy, hora, minuto, i+4, "tarde"
            )

        self.stdout.write(self.style.SUCCESS(f"✅ Rifas creadas exitosamente"))

    def crear_rifa_individual(self, organizadores, sponsors, participantes, fecha, hora, minuto, numero, tipo):
        """Crea una rifa individual con todos sus datos"""
        try:
            if not participantes:
                self.stdout.write(self.style.ERROR(f"  ❌ No hay participantes disponibles para comprar boletos"))
                return

            organizador = random.choice(organizadores)
            premio = random.choice(self.premios)

            titulos = [
                f'Gran Sorteo {premio["nombre"]}',
                f'Rifa Especial {premio["nombre"]}',
                f'Sorteo Beneficencia {premio["nombre"]}'
            ]
            titulo = f"{random.choice(titulos)} #{numero}"

            total_boletos = random.choice([100, 200, 300, 500, 1000])
            precio_boleto = Decimal(str(random.choice([500, 1000, 2000, 5000, 10000])))

            fecha_sorteo = timezone.make_aware(
                datetime.combine(fecha, datetime.min.time().replace(hour=hora, minute=minuto))
            )

            dias_atras = 7 if tipo == "temprana" else random.randint(2, 10)
            fecha_inicio = timezone.now() - timedelta(days=dias_atras)

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

            # Crear solicitudes de patrocinio (30% de probabilidad por rifa)
            if sponsors and random.random() < 0.3:
                try:
                    from apps.raffles.models import SponsorshipRequest
                    
                    # Seleccionar 1-2 sponsors para esta rifa
                    num_sponsors = random.randint(1, min(2, len(sponsors)))
                    sponsors_seleccionados = random.sample(sponsors, num_sponsors)
                    
                    for sponsor in sponsors_seleccionados:
                        premios_sponsor = [
                            {'nombre': 'Kit Premium de Productos', 'desc': 'Set completo de productos exclusivos de nuestra marca', 'valor': Decimal('50000')},
                            {'nombre': 'Vale de Compra $100.000', 'desc': 'Vale canjeable en cualquiera de nuestras tiendas', 'valor': Decimal('100000')},
                            {'nombre': 'Set de Merchandising', 'desc': 'Polera, gorra, mochila y botella con logo de la marca', 'valor': Decimal('30000')},
                            {'nombre': 'Experiencia VIP', 'desc': 'Tour exclusivo por nuestras instalaciones + almuerzo', 'valor': Decimal('150000')},
                            {'nombre': 'Curso Online Premium', 'desc': 'Acceso completo a nuestra plataforma educativa por 1 año', 'valor': Decimal('200000')},
                            {'nombre': 'Pack Tecnología', 'desc': 'Audífonos Bluetooth + Power Bank + Cable USB-C', 'valor': Decimal('80000')},
                        ]
                        
                        premio_sponsor = random.choice(premios_sponsor)
                        
                        SponsorshipRequest.objects.create(
                            rifa=raffle,
                            sponsor=sponsor,
                            nombre_premio_adicional=premio_sponsor['nombre'],
                            descripcion_premio=premio_sponsor['desc'],
                            valor_premio=premio_sponsor['valor'],
                            nombre_marca=sponsor.nombre,
                            sitio_web=f'https://www.{sponsor.nombre.lower().replace(" ", "")}.cl',
                            mensaje_patrocinio=f'Orgullosos de apoyar esta causa. ¡Participa y gana!',
                            estado='aceptada',
                            fecha_solicitud=fecha_inicio,
                            fecha_respuesta=fecha_inicio + timedelta(hours=2)
                        )
                        
                    self.stdout.write(f"      + {num_sponsors} sponsor(s) agregado(s)")
                except ImportError:
                    pass
                except Exception as sponsor_error:
                    self.stdout.write(self.style.WARNING(f"      ⚠ Error agregando sponsor: {str(sponsor_error)}"))

            # Crear compras de boletos
            porcentaje_venta = random.uniform(0.4, 0.85)
            boletos_a_vender = int(total_boletos * porcentaje_venta)

            compradores = random.sample(participantes, min(30, len(participantes)))
            numeros_disponibles = list(range(1, total_boletos + 1))
            random.shuffle(numeros_disponibles)

            boletos_vendidos = 0
            for comprador in compradores:
                if boletos_vendidos >= boletos_a_vender:
                    break

                # Determinar cuántos boletos compra este usuario
                max_a_comprar = min(5, boletos_a_vender - boletos_vendidos, len(numeros_disponibles))
                if max_a_comprar <= 0:
                    break

                cantidad = random.randint(1, max_a_comprar)

                for _ in range(cantidad):
                    if not numeros_disponibles or boletos_vendidos >= boletos_a_vender:
                        break

                    numero = numeros_disponibles.pop(0)

                    try:
                        import uuid
                        Ticket.objects.create(
                            rifa=raffle,
                            usuario=comprador,
                            numero_boleto=numero,
                            estado='pagado',
                            codigo_qr=str(uuid.uuid4())[:20]  # Código QR único
                        )
                        boletos_vendidos += 1
                    except Exception as ticket_error:
                        self.stdout.write(self.style.WARNING(f"    ⚠ Error creando boleto {numero}: {str(ticket_error)}"))

            # Actualizar contador de boletos vendidos
            raffle.boletos_vendidos = boletos_vendidos
            raffle.save(update_fields=['boletos_vendidos'])

            self.stdout.write(f"    ✓ Rifa '{titulo[:40]}...' - {boletos_vendidos}/{total_boletos} boletos vendidos")

        except Exception as e:
            import traceback
            self.stdout.write(self.style.ERROR(f"  ❌ Error creando rifa #{numero}: {str(e)}"))
            self.stdout.write(self.style.ERROR(f"     Detalles: {traceback.format_exc()}"))
