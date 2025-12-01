"""
Script para limpiar la base de datos dejando solo el admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.raffles.models import Raffle, Ticket
from apps.payments.models import Payment
from apps.users.models import Notification

def clean_database():
    print("\n" + "="*60)
    print("LIMPIEZA DE BASE DE DATOS")
    print("="*60)
    
    # Buscar admin
    admin = User.objects.filter(rol='admin').first()
    if admin:
        print(f"\n✅ Admin encontrado: {admin.email}")
    else:
        print("\n⚠️  No se encontró ningún admin")
        return
    
    print("\n📊 Estado antes de la limpieza:")
    print(f"   Usuarios: {User.objects.count()}")
    print(f"   Rifas: {Raffle.objects.count()}")
    print(f"   Tickets: {Ticket.objects.count()}")
    print(f"   Pagos: {Payment.objects.count()}")
    print(f"   Notificaciones: {Notification.objects.count()}")
    
    # Eliminar en orden (respetando foreign keys)
    print("\n🗑️  Eliminando datos...")
    
    tickets_deleted = Ticket.objects.all().delete()
    print(f"   ✓ Tickets eliminados: {tickets_deleted[0]}")
    
    payments_deleted = Payment.objects.all().delete()
    print(f"   ✓ Pagos eliminados: {payments_deleted[0]}")
    
    raffles_deleted = Raffle.objects.all().delete()
    print(f"   ✓ Rifas eliminadas: {raffles_deleted[0]}")
    
    notifications_deleted = Notification.objects.all().delete()
    print(f"   ✓ Notificaciones eliminadas: {notifications_deleted[0]}")
    
    users_deleted = User.objects.exclude(id=admin.id).delete()
    print(f"   ✓ Usuarios eliminados: {users_deleted[0]}")
    
    print("\n📊 Estado después de la limpieza:")
    print(f"   Usuarios: {User.objects.count()}")
    print(f"   Rifas: {Raffle.objects.count()}")
    print(f"   Tickets: {Ticket.objects.count()}")
    print(f"   Pagos: {Payment.objects.count()}")
    print(f"   Notificaciones: {Notification.objects.count()}")
    
    print("\n" + "="*60)
    print("✅ LIMPIEZA COMPLETADA - BASE DE DATOS LISTA PARA PRODUCCIÓN")
    print("="*60)
    print(f"\nUsuario admin: {admin.email}")
    print("Todos los datos de prueba han sido eliminados.\n")

if __name__ == '__main__':
    clean_database()
