"""
Script para simular rifas completas con sponsors y muchos boletos comprados
Ejecutar: python simulate_complete_raffles.py
"""

import os
import django
import sys

# Configurar Django
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from apps.raffles.models import Raffle, Ticket, Prize, SponsorshipRequest
import random
import uuid

def crear_rifas_completas():
    print("=" * 80)
    print("SIMULACIÓN DE RIFAS COMPLETAS CON SPONSORS")
    print("=" * 80)
    
    # Obtener usuarios
    print("\n[1/6] Obteniendo usuarios...")
    participantes = list(User.objects.filter(rol='participante'))
    organizadores = list(User.objects.filter(rol='organizador'))
    sponsors = list(User.objects.filter(rol='sponsor'))
    
    if not participantes or not organizadores:
        print("❌ ERROR: No hay usuarios en la base de datos.")
        print("Por favor ejecuta primero: python manage.py populate_demo_data")
        return
    
    print(f"✓ {len(participantes)} participantes")
    print(f"✓ {len(organizadores)} organizadores")
    print(f"✓ {len(sponsors)} sponsors")
    
    # Configuración de rifas
    rifas_config = [
        {
            'titulo': '🚗 Rifa Auto Último Modelo 2025',
            'descripcion': 'Increíble oportunidad de ganar un auto 0km completamente equipado. Incluye seguro por 1 año.',
            'total_boletos': 500,
            'precio_boleto': 15000,
            'vendidos_porcentaje': 95,
            'dias_hasta_sorteo': 2,
            'premio_principal': 'Auto Toyota Corolla 2025',
            'valor_premio': 18000000,
            'tiene_sponsor': True
        },
        {
            'titulo': '🏠 Gran Rifa Casa Prefabricada',
            'descripcion': 'Casa prefabricada de 60m² completamente equipada, lista para habitar. Incluye instalación.',
            'total_boletos': 1000,
            'precio_boleto': 8000,
            'vendidos_porcentaje': 78,
            'dias_hasta_sorteo': 5,
            'premio_principal': 'Casa Prefabricada 60m²',
            'valor_premio': 25000000,
            'tiene_sponsor': True
        },
        {
            'titulo': '💻 Rifa Laptop Gaming + Setup Completo',
            'descripcion': 'Laptop Gaming de última generación + monitor 144Hz + teclado mecánico + mouse gaming.',
            'total_boletos': 200,
            'precio_boleto': 5000,
            'vendidos_porcentaje': 88,
            'dias_hasta_sorteo': 1,
            'premio_principal': 'Laptop Gaming RTX 4070',
            'valor_premio': 2500000,
            'tiene_sponsor': True
        },
        {
            'titulo': '🎮 Mega Rifa PlayStation 5 Pro',
            'descripcion': 'PlayStation 5 Pro edición especial + 5 juegos AAA + 2 controles DualSense.',
            'total_boletos': 300,
            'precio_boleto': 3000,
            'vendidos_porcentaje': 92,
            'dias_hasta_sorteo': 3,
            'premio_principal': 'PS5 Pro Bundle Completo',
            'valor_premio': 1200000,
            'tiene_sponsor': False
        },
        {
            'titulo': '📱 Rifa iPhone 16 Pro Max + AirPods',
            'descripcion': 'iPhone 16 Pro Max 512GB + AirPods Pro 2 + Apple Watch Series 9.',
            'total_boletos': 400,
            'precio_boleto': 4000,
            'vendidos_porcentaje': 85,
            'dias_hasta_sorteo': 4,
            'premio_principal': 'iPhone 16 Pro Max Bundle',
            'valor_premio': 2800000,
            'tiene_sponsor': True
        },
    ]
    
    print(f"\n[2/6] Creando {len(rifas_config)} rifas...")
    rifas_creadas = []
    
    for idx, config in enumerate(rifas_config, 1):
        organizador = random.choice(organizadores)
        fecha_sorteo = timezone.now() + timedelta(days=config['dias_hasta_sorteo'])
        
        rifa = Raffle.objects.create(
            titulo=config['titulo'],
            descripcion=config['descripcion'],
            organizador=organizador,
            total_boletos=config['total_boletos'],
            precio_boleto=config['precio_boleto'],
            fecha_sorteo=fecha_sorteo,
            estado='activa',
            boletos_vendidos=0
        )
        
        # Crear premio principal
        Prize.objects.create(
            rifa=rifa,
            nombre=config['premio_principal'],
            descripcion=f"Premio principal valorado en CLP${config['valor_premio']:,}",
            valor_estimado=config['valor_premio'],
            posicion=1
        )
        
        rifas_creadas.append((rifa, config))
        print(f"✓ Rifa {idx}: {config['titulo']} (ID: {rifa.id})")
    
    print(f"\n[3/6] Agregando sponsors a las rifas...")
    sponsor_count = 0
    for rifa, config in rifas_creadas:
        if config['tiene_sponsor'] and sponsors:
            # Agregar 1-2 sponsors por rifa
            num_sponsors = random.randint(1, min(2, len(sponsors)))
            sponsors_seleccionados = random.sample(sponsors, num_sponsors)
            
            for sponsor in sponsors_seleccionados:
                # Crear solicitud de sponsor aceptada
                premio_sponsor = f"Premio adicional de {sponsor.nombre}"
                
                SponsorshipRequest.objects.create(
                    rifa=rifa,
                    sponsor=sponsor,
                    nombre_premio=premio_sponsor,
                    descripcion_premio=f"Premio adicional patrocinado por {sponsor.nombre}",
                    valor_estimado=random.randint(100000, 500000),
                    estado='aceptada',
                    mensaje=f"Quiero patrocinar esta rifa con {premio_sponsor}"
                )
                
                # Crear el premio del sponsor
                Prize.objects.create(
                    rifa=rifa,
                    nombre=premio_sponsor,
                    descripcion=f"Patrocinado por {sponsor.nombre}",
                    valor_estimado=random.randint(100000, 500000),
                    posicion=2
                )
                
                sponsor_count += 1
                print(f"  ✓ Sponsor agregado a '{rifa.titulo}': {sponsor.nombre}")
    
    print(f"✓ Total de sponsors agregados: {sponsor_count}")
    
    print(f"\n[4/6] Simulando compra de boletos...")
    total_tickets = 0
    
    for rifa, config in rifas_creadas:
        boletos_a_vender = int(config['total_boletos'] * (config['vendidos_porcentaje'] / 100))
        print(f"\n  Rifa: {rifa.titulo}")
        print(f"  Vendiendo {boletos_a_vender}/{config['total_boletos']} boletos ({config['vendidos_porcentaje']}%)")
        
        # Crear boletos vendidos
        compradores = random.sample(participantes, min(len(participantes), boletos_a_vender))
        boletos_por_comprador = boletos_a_vender // len(compradores)
        boletos_restantes = boletos_a_vender % len(compradores)
        
        numero_boleto = 1
        for idx, comprador in enumerate(compradores):
            # Algunos compradores compran más boletos
            cantidad = boletos_por_comprador
            if idx < boletos_restantes:
                cantidad += 1
            
            # Ocasionalmente dar más boletos a algunos usuarios (1-5 boletos)
            if random.random() < 0.3:
                cantidad = random.randint(1, 5)
            
            for _ in range(cantidad):
                if numero_boleto > boletos_a_vender:
                    break
                    
                Ticket.objects.create(
                    rifa=rifa,
                    usuario=comprador,
                    numero_boleto=numero_boleto,
                    codigo_qr=f"TKT-{rifa.id}-{numero_boleto}-{uuid.uuid4().hex[:8]}",
                    estado='pagado'
                )
                numero_boleto += 1
                total_tickets += 1
        
        # Actualizar contador de boletos vendidos
        rifa.boletos_vendidos = boletos_a_vender
        rifa.save()
        
        print(f"  ✓ {boletos_a_vender} boletos vendidos")
    
    print(f"\n✓ Total de boletos creados: {total_tickets}")
    
    print("\n[5/6] Resumen de rifas creadas:")
    print("-" * 80)
    for rifa, config in rifas_creadas:
        porcentaje_real = (rifa.boletos_vendidos / rifa.total_boletos) * 100
        sponsors_count = SponsorshipRequest.objects.filter(rifa=rifa, estado='aceptada').count()
        
        print(f"\n🎯 {rifa.titulo}")
        print(f"   ID: {rifa.id}")
        print(f"   Organizador: {rifa.organizador.nombre}")
        print(f"   Boletos: {rifa.boletos_vendidos}/{rifa.total_boletos} ({porcentaje_real:.1f}%)")
        print(f"   Precio: CLP${rifa.precio_boleto:,}")
        print(f"   Sorteo: {rifa.fecha_sorteo.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Sponsors: {sponsors_count}")
        print(f"   Recaudación: CLP${rifa.boletos_vendidos * rifa.precio_boleto:,}")
    
    print("\n" + "=" * 80)
    print("✅ SIMULACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    print(f"📊 Estadísticas:")
    print(f"   • Rifas creadas: {len(rifas_creadas)}")
    print(f"   • Sponsors agregados: {sponsor_count}")
    print(f"   • Boletos vendidos: {total_tickets}")
    print(f"   • Participantes únicos: {len(set([t.usuario for t in Ticket.objects.all()]))}")
    print("\n💡 Puedes ver las rifas en: http://127.0.0.1:8000/raffles/")
    print("=" * 80)

if __name__ == '__main__':
    try:
        crear_rifas_completas()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
