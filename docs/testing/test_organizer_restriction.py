# Test rápido: Verificar restricción de organizadores comprando boletos
# Este script verifica que los organizadores no puedan comprar boletos

import os
import sys
import django

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.raffles.models import Raffle
from apps.raffles.serializers import RaffleSerializer
from django.test import RequestFactory

User = get_user_model()

print("=" * 70)
print("🧪 TEST: RESTRICCIÓN DE COMPRA PARA ORGANIZADORES")
print("=" * 70)
print()

# Crear usuarios de prueba
print("📝 Creando usuarios de prueba...")
try:
    participante = User.objects.create_user(
        username='test_participante',
        email='participante@test.com',
        password='test123',
        rol='participante'
    )
    print(f"✅ Participante creado: {participante.username} (rol: {participante.rol})")
except:
    participante = User.objects.get(username='test_participante')
    print(f"ℹ️  Participante existente: {participante.username} (rol: {participante.rol})")

try:
    organizador = User.objects.create_user(
        username='test_organizador',
        email='organizador@test.com',
        password='test123',
        rol='organizador'
    )
    print(f"✅ Organizador creado: {organizador.username} (rol: {organizador.rol})")
except:
    organizador = User.objects.get(username='test_organizador')
    print(f"ℹ️  Organizador existente: {organizador.username} (rol: {organizador.rol})")

print()

# Buscar una rifa activa
print("🔍 Buscando rifa activa...")
raffle = Raffle.objects.filter(estado='activa').first()

if not raffle:
    print("❌ No hay rifas activas para probar")
    exit(1)

print(f"✅ Rifa encontrada: {raffle.titulo}")
print(f"   - Estado: {raffle.estado}")
print(f"   - Boletos vendidos: {raffle.boletos_vendidos}/{raffle.total_boletos}")
print()

# Test con RequestFactory
factory = RequestFactory()

# TEST 1: Participante puede comprar
print("=" * 70)
print("TEST 1: Verificar que PARTICIPANTE puede comprar")
print("=" * 70)

request = factory.get('/api/raffles/')
request.user = participante

serializer = RaffleSerializer(raffle, context={'request': request})
puede_comprar = serializer.data.get('puede_comprar')

print(f"Usuario: {participante.username} (rol: {participante.rol})")
print(f"puede_comprar: {puede_comprar}")

if puede_comprar:
    print("✅ PASS - Participante PUEDE comprar boletos")
else:
    print("❌ FAIL - Participante debería poder comprar boletos")

print()

# TEST 2: Organizador NO puede comprar
print("=" * 70)
print("TEST 2: Verificar que ORGANIZADOR NO puede comprar")
print("=" * 70)

request = factory.get('/api/raffles/')
request.user = organizador

serializer = RaffleSerializer(raffle, context={'request': request})
puede_comprar = serializer.data.get('puede_comprar')

print(f"Usuario: {organizador.username} (rol: {organizador.rol})")
print(f"puede_comprar: {puede_comprar}")

if not puede_comprar:
    print("✅ PASS - Organizador NO puede comprar boletos (correcto)")
else:
    print("❌ FAIL - Organizador NO debería poder comprar boletos")

print()

# Limpiar usuarios de prueba
print("🧹 Limpiando usuarios de prueba...")
try:
    participante.delete()
    organizador.delete()
    print("✅ Usuarios de prueba eliminados")
except:
    print("ℹ️  No se pudieron eliminar usuarios de prueba")

print()
print("=" * 70)
print("✅ TEST COMPLETADO")
print("=" * 70)
