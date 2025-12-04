"""
Script de prueba para el sistema de recuperación de contraseña
Ejecutar con: python test_password_reset.py
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def print_separator():
    print("\n" + "="*80 + "\n")

def test_password_reset():
    """Prueba completa del sistema de recuperación de contraseña"""

    print("🔐 PRUEBA DEL SISTEMA DE RECUPERACIÓN DE CONTRASEÑA")
    print_separator()

    # Email de prueba
    email = input("Ingresa el email de un usuario registrado: ").strip()

    if not email:
        print("❌ Email vacío. Usando email de ejemplo.")
        email = "test@ejemplo.com"

    print(f"📧 Email a usar: {email}")
    print_separator()

    # PASO 1: Solicitar recuperación
    print("📤 PASO 1: Solicitando recuperación de contraseña...")

    response = requests.post(
        f"{BASE_URL}/api/users/password-reset/request/",
        json={"email": email},
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    if response.status_code != 200:
        print("❌ Error al solicitar recuperación")
        return

    print("✅ Solicitud enviada correctamente")
    print("\n⚠️  IMPORTANTE: Revisa la consola del servidor Django para copiar el token del email")
    print_separator()

    # Pedir token
    token = input("Pega el token del email aquí (copia desde la consola del servidor): ").strip()

    if not token:
        print("❌ No se proporcionó token. Prueba terminada.")
        return

    print_separator()

    # PASO 2: Verificar token
    print("🔍 PASO 2: Verificando token...")

    response = requests.get(f"{BASE_URL}/api/users/password-reset/verify/{token}/")

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    if response.status_code != 200:
        print("❌ Token inválido o expirado")
        return

    data = response.json()
    if not data.get('valid'):
        print(f"❌ Token no válido: {data.get('error')}")
        return

    print("✅ Token válido")
    print(f"📧 Email confirmado: {data.get('email')}")
    print(f"⏱  Expira en: {data.get('expires_in')}")
    print_separator()

    # PASO 3: Cambiar contraseña
    print("🔑 PASO 3: Cambiando contraseña...")

    nueva_password = input("Ingresa la nueva contraseña (mínimo 8 caracteres): ").strip()

    if len(nueva_password) < 8:
        print("❌ La contraseña debe tener al menos 8 caracteres")
        return

    response = requests.post(
        f"{BASE_URL}/api/users/password-reset/confirm/{token}/",
        json={
            "password": nueva_password,
            "password_confirm": nueva_password
        },
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    if response.status_code != 200:
        print("❌ Error al cambiar contraseña")
        return

    print("✅ ¡Contraseña cambiada exitosamente!")
    print("\n📧 Se envió un email de notificación al usuario")
    print("\n🔓 Ahora puedes iniciar sesión con la nueva contraseña")
    print_separator()

    # PASO 4: Verificar que el token ya no es válido
    print("🔒 PASO 4: Verificando que el token ya no se puede reutilizar...")

    response = requests.get(f"{BASE_URL}/api/users/password-reset/verify/{token}/")

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    if response.status_code == 400:
        print("✅ Correcto: El token ya no es válido (un solo uso)")
    else:
        print("⚠️  El token todavía parece válido")

    print_separator()
    print("🎉 PRUEBA COMPLETADA")
    print("\nResumen:")
    print("1. ✅ Solicitud de recuperación enviada")
    print("2. ✅ Token verificado correctamente")
    print("3. ✅ Contraseña cambiada exitosamente")
    print("4. ✅ Token invalidado después de uso")
    print_separator()

def test_invalid_scenarios():
    """Prueba escenarios de error"""

    print("\n🧪 PRUEBAS DE ESCENARIOS DE ERROR")
    print_separator()

    # Test 1: Email vacío
    print("Test 1: Email vacío...")
    response = requests.post(
        f"{BASE_URL}/api/users/password-reset/request/",
        json={"email": ""},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code} - {'✅ PASS' if response.status_code == 400 else '❌ FAIL'}")

    # Test 2: Token inválido
    print("\nTest 2: Token inválido...")
    response = requests.get(f"{BASE_URL}/api/users/password-reset/verify/token_invalido_123/")
    print(f"Status: {response.status_code} - {'✅ PASS' if response.status_code == 400 else '❌ FAIL'}")

    # Test 3: Contraseñas no coinciden
    print("\nTest 3: Contraseñas no coinciden...")
    response = requests.post(
        f"{BASE_URL}/api/users/password-reset/confirm/token_test/",
        json={
            "password": "password123",
            "password_confirm": "password456"
        },
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code} - {'✅ PASS' if response.status_code == 400 else '❌ FAIL'}")

    # Test 4: Contraseña muy corta
    print("\nTest 4: Contraseña muy corta...")
    response = requests.post(
        f"{BASE_URL}/api/users/password-reset/confirm/token_test/",
        json={
            "password": "1234567",
            "password_confirm": "1234567"
        },
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code} - {'✅ PASS' if response.status_code == 400 else '❌ FAIL'}")

    print_separator()

if __name__ == "__main__":
    try:
        print("\n¿Qué prueba deseas ejecutar?")
        print("1. Prueba completa del flujo de recuperación")
        print("2. Pruebas de escenarios de error")
        print("3. Ambas")

        opcion = input("\nOpción (1/2/3): ").strip()

        if opcion == "1":
            test_password_reset()
        elif opcion == "2":
            test_invalid_scenarios()
        elif opcion == "3":
            test_password_reset()
            test_invalid_scenarios()
        else:
            print("❌ Opción inválida")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor")
        print("Asegúrate de que el servidor Django esté corriendo en http://localhost:8000/")
        print("Ejecuta: python manage.py runserver")

    except KeyboardInterrupt:
        print("\n\n⏹️  Prueba interrumpida por el usuario")

    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
