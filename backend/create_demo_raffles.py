"""
Script para crear rifas de demostración con boletos vendidos.
Las rifas finalizarán entre las 18:30 y 20:30 hora de Chile (hoy).
"""
import os
import sys
import django
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Agregar el directorio backend al path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

django.setup()

from django.utils import timezone
from apps.users.models import User
from apps.raffles.models import Raffle, Ticket
from apps.payments.models import Payment

# Zona horaria de Chile
import pytz
CHILE_TZ = pytz.timezone('America/Santiago')

def limpiar_datos():
    """Elimina todas las rifas, boletos y pagos existentes"""
    print("=" * 60)
    print("LIMPIANDO DATOS EXISTENTES...")
    print("=" * 60)
    
    # Eliminar pagos primero (tienen FK a boletos)
    pagos_count = Payment.objects.count()
    Payment.objects.all().delete()
    print(f"✓ Eliminados {pagos_count} pagos")
    
    # Eliminar boletos
    boletos_count = Ticket.objects.count()
    Ticket.objects.all().delete()
    print(f"✓ Eliminados {boletos_count} boletos")
    
    # Eliminar rifas
    rifas_count = Raffle.objects.count()
    Raffle.objects.all().delete()
    print(f"✓ Eliminadas {rifas_count} rifas")
    
    print("")

def obtener_organizador():
    """Obtiene un usuario organizador o lo crea"""
    # Buscar un organizador existente
    organizador = User.objects.filter(rol='organizador', is_active=True).first()
    
    if not organizador:
        # Buscar cualquier usuario activo que no sea admin
        organizador = User.objects.filter(is_active=True, is_superuser=False).first()
    
    if not organizador:
        # Usar un admin como organizador
        organizador = User.objects.filter(is_active=True).first()
    
    if not organizador:
        print("❌ ERROR: No hay usuarios en el sistema")
        sys.exit(1)
    
    print(f"✓ Usando organizador: {organizador.email}")
    return organizador

def obtener_participantes():
    """Obtiene lista de usuarios para comprar boletos"""
    participantes = list(User.objects.filter(is_active=True))
    if len(participantes) < 3:
        print("⚠️ Advertencia: Pocos usuarios, se usará el mismo para múltiples compras")
    return participantes

def crear_rifas_demo():
    """Crea rifas de demostración con todos los boletos vendidos"""
    
    limpiar_datos()
    
    organizador = obtener_organizador()
    participantes = obtener_participantes()
    
    # Hora actual en Chile
    now_chile = timezone.now().astimezone(CHILE_TZ)
    hoy = now_chile.date()
    
    print("=" * 60)
    print(f"CREANDO RIFAS PARA HOY: {hoy}")
    print(f"Hora actual en Chile: {now_chile.strftime('%H:%M:%S')}")
    print("=" * 60)
    print("")
    
    # Definir las rifas a crear con horarios de sorteo entre 18:30 y 20:30
    rifas_data = [
        {
            "titulo": "🎮 PlayStation 5 Digital Edition",
            "descripcion": "¡Gana una PS5 Digital Edition completamente nueva! Incluye control DualSense y cables.",
            "premio_principal": "PlayStation 5 Digital Edition",
            "descripcion_premio": "Consola PS5 Digital Edition nueva en caja sellada. Incluye control DualSense y todos los accesorios originales.",
            "valor_premio": Decimal("450000"),
            "precio_boleto": Decimal("2500"),
            "total_boletos": 200,
            "hora_sorteo": "18:30",
        },
        {
            "titulo": "📱 iPhone 15 Pro Max 256GB",
            "descripcion": "El smartphone más avanzado de Apple. Color Titanio Natural, 256GB de almacenamiento.",
            "premio_principal": "iPhone 15 Pro Max 256GB",
            "descripcion_premio": "iPhone 15 Pro Max nuevo, color Titanio Natural, 256GB. Incluye cargador y cable USB-C.",
            "valor_premio": Decimal("1200000"),
            "precio_boleto": Decimal("5000"),
            "total_boletos": 300,
            "hora_sorteo": "18:45",
        },
        {
            "titulo": "💻 MacBook Air M3 15 pulgadas",
            "descripcion": "MacBook Air con chip M3, pantalla de 15 pulgadas, 8GB RAM, 256GB SSD.",
            "premio_principal": "MacBook Air M3 15\"",
            "descripcion_premio": "MacBook Air M3 nuevo, pantalla 15 pulgadas Liquid Retina, 8GB RAM, 256GB SSD. Color Medianoche.",
            "valor_premio": Decimal("1400000"),
            "precio_boleto": Decimal("7000"),
            "total_boletos": 250,
            "hora_sorteo": "19:00",
        },
        {
            "titulo": "🎧 AirPods Pro 2da Generación",
            "descripcion": "Los mejores audífonos inalámbricos de Apple con cancelación de ruido activa.",
            "premio_principal": "AirPods Pro 2da Gen",
            "descripcion_premio": "AirPods Pro 2da generación con estuche de carga MagSafe USB-C. Nuevos en caja sellada.",
            "valor_premio": Decimal("280000"),
            "precio_boleto": Decimal("1500"),
            "total_boletos": 200,
            "hora_sorteo": "19:15",
        },
        {
            "titulo": "🖥️ Monitor Gaming Samsung 27\" 144Hz",
            "descripcion": "Monitor curvo gaming de 27 pulgadas, resolución QHD, 144Hz, 1ms respuesta.",
            "premio_principal": "Monitor Samsung Odyssey G5",
            "descripcion_premio": "Monitor Samsung Odyssey G5 27\" QHD, 144Hz, 1ms, panel VA curvo. Nuevo en caja.",
            "valor_premio": Decimal("350000"),
            "precio_boleto": Decimal("2000"),
            "total_boletos": 200,
            "hora_sorteo": "19:30",
        },
        {
            "titulo": "⌚ Apple Watch Series 9 GPS",
            "descripcion": "El smartwatch más vendido del mundo. GPS, pantalla Always-On, sensor de oxígeno.",
            "premio_principal": "Apple Watch Series 9 45mm",
            "descripcion_premio": "Apple Watch Series 9 GPS 45mm, caja de aluminio color Medianoche con correa deportiva.",
            "valor_premio": Decimal("500000"),
            "precio_boleto": Decimal("2500"),
            "total_boletos": 220,
            "hora_sorteo": "19:45",
        },
        {
            "titulo": "🎮 Nintendo Switch OLED + Juegos",
            "descripcion": "Nintendo Switch modelo OLED con pantalla mejorada + 3 juegos a elección.",
            "premio_principal": "Nintendo Switch OLED Bundle",
            "descripcion_premio": "Nintendo Switch OLED blanca + 3 juegos físicos a elección del ganador. Valor total $450.000",
            "valor_premio": Decimal("450000"),
            "precio_boleto": Decimal("2000"),
            "total_boletos": 250,
            "hora_sorteo": "20:00",
        },
        {
            "titulo": "📷 GoPro Hero 12 Black",
            "descripcion": "La cámara de acción más avanzada. Grabación 5.3K, estabilización HyperSmooth 6.0.",
            "premio_principal": "GoPro Hero 12 Black",
            "descripcion_premio": "GoPro Hero 12 Black nueva en caja. Incluye batería Enduro y cable USB-C.",
            "valor_premio": Decimal("380000"),
            "precio_boleto": Decimal("2000"),
            "total_boletos": 200,
            "hora_sorteo": "20:15",
        },
        {
            "titulo": "🎤 Micrófono Blue Yeti X Pro",
            "descripcion": "Micrófono USB profesional para streaming, podcasting y grabación.",
            "premio_principal": "Blue Yeti X Professional",
            "descripcion_premio": "Micrófono Blue Yeti X con patrón de captación ajustable, LED inteligente y software Blue VO!CE.",
            "valor_premio": Decimal("180000"),
            "precio_boleto": Decimal("1000"),
            "total_boletos": 200,
            "hora_sorteo": "20:30",
        },
        {
            "titulo": "🖱️ Setup Gaming Completo",
            "descripcion": "Teclado mecánico + mouse gaming + mousepad XL + audífonos gaming RGB.",
            "premio_principal": "Kit Gaming Premium",
            "descripcion_premio": "Teclado Logitech G Pro + Mouse Logitech G502 + Mousepad XL + Audífonos HyperX Cloud II",
            "valor_premio": Decimal("320000"),
            "precio_boleto": Decimal("1500"),
            "total_boletos": 230,
            "hora_sorteo": "18:35",
        },
        {
            "titulo": "📚 Kindle Paperwhite + Crédito Amazon",
            "descripcion": "Kindle Paperwhite 2023 + $50.000 en crédito para libros Amazon.",
            "premio_principal": "Kindle Paperwhite Bundle",
            "descripcion_premio": "Kindle Paperwhite 2023 16GB + funda oficial + $50.000 crédito Amazon Kindle Store.",
            "valor_premio": Decimal("200000"),
            "precio_boleto": Decimal("1000"),
            "total_boletos": 220,
            "hora_sorteo": "19:10",
        },
        {
            "titulo": "🎵 Parlante JBL PartyBox 310",
            "descripcion": "El parlante más potente para fiestas. 240W, batería de 18 horas, luces LED.",
            "premio_principal": "JBL PartyBox 310",
            "descripcion_premio": "Parlante JBL PartyBox 310, 240W de potencia, batería 18 horas, entrada para micrófono y guitarra.",
            "valor_premio": Decimal("550000"),
            "precio_boleto": Decimal("3000"),
            "total_boletos": 200,
            "hora_sorteo": "19:50",
        },
        {
            "titulo": "🏠 Robot Aspiradora Roomba j7+",
            "descripcion": "Robot aspiradora inteligente con autovaciado y navegación por cámara.",
            "premio_principal": "iRobot Roomba j7+",
            "descripcion_premio": "Roomba j7+ con estación de autovaciado Clean Base. Mapeo inteligente y control por app.",
            "valor_premio": Decimal("700000"),
            "precio_boleto": Decimal("3500"),
            "total_boletos": 220,
            "hora_sorteo": "20:20",
        },
        {
            "titulo": "☕ Cafetera Nespresso Vertuo Plus",
            "descripcion": "Cafetera Nespresso con sistema Vertuo + 50 cápsulas de regalo.",
            "premio_principal": "Nespresso Vertuo Plus Bundle",
            "descripcion_premio": "Cafetera Nespresso Vertuo Plus + Aeroccino espumador + 50 cápsulas variadas.",
            "valor_premio": Decimal("250000"),
            "precio_boleto": Decimal("1500"),
            "total_boletos": 180,
            "hora_sorteo": "18:50",
        },
        {
            "titulo": "🎒 Mochila Peak Design + Accesorios",
            "descripcion": "La mochila favorita de fotógrafos y viajeros + kit de accesorios.",
            "premio_principal": "Peak Design Everyday Backpack 30L",
            "descripcion_premio": "Mochila Peak Design 30L + organizador Tech Pouch + correa Slide Lite para cámara.",
            "valor_premio": Decimal("380000"),
            "precio_boleto": Decimal("2000"),
            "total_boletos": 200,
            "hora_sorteo": "19:25",
        },
    ]
    
    rifas_creadas = []
    
    for idx, data in enumerate(rifas_data, 1):
        # Calcular fecha de sorteo
        hora, minuto = map(int, data["hora_sorteo"].split(":"))
        fecha_sorteo = CHILE_TZ.localize(datetime(hoy.year, hoy.month, hoy.day, hora, minuto, 0))
        
        # Fecha de inicio: hace 7 días
        fecha_inicio = timezone.now() - timedelta(days=7)
        
        # Crear la rifa
        rifa = Raffle.objects.create(
            organizador=organizador,
            titulo=data["titulo"],
            descripcion=data["descripcion"],
            precio_boleto=data["precio_boleto"],
            total_boletos=data["total_boletos"],
            boletos_vendidos=data["total_boletos"],  # ¡Todos vendidos!
            fecha_inicio=fecha_inicio,
            fecha_sorteo=fecha_sorteo,
            estado='activa',  # Activa y lista para sorteo
            premio_principal=data["premio_principal"],
            descripcion_premio=data["descripcion_premio"],
            valor_premio=data["valor_premio"],
            permite_multiples_boletos=True,
            max_boletos_por_usuario=20,
        )
        
        print(f"[{idx:02d}] ✓ Rifa creada: {data['titulo']}")
        print(f"     → Sorteo: {fecha_sorteo.strftime('%H:%M')} | Boletos: {data['total_boletos']} | Precio: ${data['precio_boleto']:,.0f}")
        
        # Crear todos los boletos vendidos
        boletos_creados = 0
        for num in range(1, data["total_boletos"] + 1):
            # Seleccionar un participante aleatorio
            participante = random.choice(participantes)
            
            # Crear el boleto
            Ticket.objects.create(
                rifa=rifa,
                usuario=participante,
                numero_boleto=num,
                estado='pagado',
                codigo_qr=f"QR-{rifa.id}-{num}-{uuid.uuid4().hex[:8].upper()}"
            )
            boletos_creados += 1
        
        print(f"     → {boletos_creados} boletos creados y pagados")
        
        rifas_creadas.append(rifa)
        print("")
    
    return rifas_creadas

def main():
    print("")
    print("=" * 60)
    print("  CREADOR DE RIFAS DE DEMOSTRACIÓN - RIFATRUST")
    print("=" * 60)
    print("")
    
    rifas = crear_rifas_demo()
    
    print("")
    print("=" * 60)
    print(f"  ✅ COMPLETADO: {len(rifas)} rifas creadas")
    print("=" * 60)
    print("")
    print("Resumen de sorteos programados:")
    print("-" * 40)
    
    for rifa in sorted(rifas, key=lambda r: r.fecha_sorteo):
        hora_chile = rifa.fecha_sorteo.astimezone(CHILE_TZ).strftime('%H:%M')
        print(f"  {hora_chile} → {rifa.titulo[:40]}")
    
    print("")
    print("¡Las rifas están listas para el sorteo!")
    print("")

if __name__ == '__main__':
    main()
