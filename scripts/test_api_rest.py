"""
Script de prueba para la API REST de RifaTrust.
Prueba todos los endpoints principales con autenticación JWT.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

# Colores para consola
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'


def print_success(message):
    print(f"{GREEN}✅ {message}{END}")


def print_error(message):
    print(f"{RED}❌ {message}{END}")


def print_info(message):
    print(f"{BLUE}ℹ️  {message}{END}")


def print_section(title):
    print(f"\n{YELLOW}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{END}\n")


# 1. Prueba de Registro
def test_register():
    print_section("1. PRUEBA DE REGISTRO DE USUARIO")
    
    url = f"{BASE_URL}/users/register/"
    data = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "nombre": "Usuario de Prueba",
        "password": "TestPassword123!",
        "password_confirm": "TestPassword123!",
        "telefono": "+56912345678",
        "rol": "participante"
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        
        if response.status_code == 201:
            result = response.json()
            print_success(f"Usuario registrado: {result['user']['email']}")
            print_info(f"Access Token: {result['access'][:50]}...")
            return result['access'], result['refresh']
        else:
            print_error(f"Error en registro: {response.status_code}")
            print(response.json())
            return None, None
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return None, None


# 2. Prueba de Login
def test_login():
    print_section("2. PRUEBA DE LOGIN")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "email": "admin@example.com",
        "password": "admin"
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print_success("Login exitoso")
            print_info(f"Access Token: {result['access'][:50]}...")
            print_info(f"Refresh Token: {result['refresh'][:50]}...")
            return result['access'], result['refresh']
        else:
            print_error(f"Error en login: {response.status_code}")
            print(response.json())
            return None, None
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return None, None


# 3. Prueba de Perfil
def test_profile(access_token):
    print_section("3. PRUEBA DE OBTENER PERFIL")
    
    url = f"{BASE_URL}/users/me/"
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            print_success(f"Perfil obtenido: {user['nombre']} ({user['email']})")
            print_info(f"Rol: {user['rol']}")
            print_info(f"Cuenta validada: {user['cuenta_validada']}")
            return user
        else:
            print_error(f"Error al obtener perfil: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return None


# 4. Prueba de Lista de Rifas
def test_list_raffles(access_token):
    print_section("4. PRUEBA DE LISTA DE RIFAS")
    
    url = f"{BASE_URL}/raffles/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data))
            print_success(f"Rifas encontradas: {count}")
            
            if count > 0:
                results = data.get('results', data)
                if results:
                    rifa = results[0]
                    print_info(f"Primera rifa: {rifa['titulo']}")
                    print_info(f"Estado: {rifa['estado']}")
                    print_info(f"Precio boleto: ${rifa['precio_boleto']}")
            
            return data
        else:
            print_error(f"Error al listar rifas: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return None


# 5. Prueba de Rifas Activas
def test_active_raffles(access_token):
    print_section("5. PRUEBA DE RIFAS ACTIVAS")
    
    url = f"{BASE_URL}/raffles/activas/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            rifas = response.json()
            print_success(f"Rifas activas: {len(rifas)}")
            
            for rifa in rifas[:3]:  # Mostrar primeras 3
                print_info(f"- {rifa['titulo']} (${rifa['precio_boleto']})")
            
            return rifas
        else:
            print_error(f"Error al obtener rifas activas: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return None


# 6. Prueba de Estadísticas de Rifas
def test_raffle_stats(access_token):
    print_section("6. PRUEBA DE ESTADÍSTICAS DE RIFAS")
    
    url = f"{BASE_URL}/raffles/stats/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            stats = response.json()
            print_success("Estadísticas obtenidas:")
            print_info(f"Total rifas: {stats['total_rifas']}")
            print_info(f"Rifas activas: {stats['rifas_activas']}")
            print_info(f"Rifas finalizadas: {stats['rifas_finalizadas']}")
            print_info(f"Boletos vendidos: {stats['total_boletos_vendidos']}")
            print_info(f"Total recaudado: ${stats['total_recaudado']}")
            return stats
        else:
            print_error(f"Error al obtener estadísticas: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return None


# 7. Prueba de Notificaciones
def test_notifications(access_token):
    print_section("7. PRUEBA DE NOTIFICACIONES")
    
    # Contador de no leídas
    url_count = f"{BASE_URL}/notifications/unread_count/"
    # Lista de notificaciones
    url_list = f"{BASE_URL}/notifications/"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        # Contador
        response = requests.get(url_count, headers=headers)
        if response.status_code == 200:
            count = response.json()['count']
            print_success(f"Notificaciones no leídas: {count}")
        
        # Lista
        response = requests.get(url_list, headers=headers)
        if response.status_code == 200:
            data = response.json()
            total = data.get('count', len(data))
            print_success(f"Total notificaciones: {total}")
            
            results = data.get('results', data)
            if results:
                print_info(f"Primera notificación: {results[0]['titulo']}")
            
            return data
        else:
            print_error(f"Error al obtener notificaciones: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return None


# 8. Prueba de Refresh Token
def test_refresh_token(refresh_token):
    print_section("8. PRUEBA DE REFRESH TOKEN")
    
    url = f"{BASE_URL}/auth/refresh/"
    data = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print_success("Token renovado exitosamente")
            print_info(f"Nuevo Access Token: {result['access'][:50]}...")
            return result['access']
        else:
            print_error(f"Error al renovar token: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return None


# 9. Prueba de Documentación
def test_documentation():
    print_section("9. VERIFICACIÓN DE DOCUMENTACIÓN")
    
    urls = [
        ("Swagger UI", f"{BASE_URL}/docs/"),
        ("ReDoc", f"{BASE_URL}/redoc/"),
        ("OpenAPI Schema", f"{BASE_URL}/schema/")
    ]
    
    for name, url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print_success(f"{name} disponible: {url}")
            else:
                print_error(f"{name} no disponible: {response.status_code}")
        except Exception as e:
            print_error(f"{name} error: {str(e)}")


# Main
def main():
    print(f"\n{BLUE}{'='*60}")
    print("  🚀 PRUEBA DE API REST - RIFATRUST")
    print(f"{'='*60}{END}\n")
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Login
    access_token, refresh_token = test_login()
    
    if not access_token:
        print_error("No se pudo obtener token. Pruebas abortadas.")
        return
    
    # 2. Perfil
    test_profile(access_token)
    
    # 3. Rifas
    test_list_raffles(access_token)
    test_active_raffles(access_token)
    test_raffle_stats(access_token)
    
    # 4. Notificaciones
    test_notifications(access_token)
    
    # 5. Refresh Token
    test_refresh_token(refresh_token)
    
    # 6. Documentación
    test_documentation()
    
    # 7. Registro (opcional)
    # test_register()
    
    print(f"\n{GREEN}{'='*60}")
    print("  ✅ PRUEBAS COMPLETADAS")
    print(f"{'='*60}{END}\n")


if __name__ == "__main__":
    main()
