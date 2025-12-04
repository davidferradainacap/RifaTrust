# Script de Pruebas Automatizadas - RifaTrust
# Ejecuta pruebas básicas del sistema

import requests
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
results = []

def test_endpoint(name, url, method="GET", data=None, expected_status=200, allow_redirects=True):
    """Prueba un endpoint y registra el resultado"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10, allow_redirects=allow_redirects)
        elif method == "POST":
            response = requests.post(url, data=data, timeout=10, allow_redirects=allow_redirects)
        
        success = response.status_code == expected_status
        results.append({
            "test": name,
            "status": "✅ PASS" if success else f"❌ FAIL ({response.status_code})",
            "expected": expected_status,
            "got": response.status_code,
            "time": response.elapsed.total_seconds()
        })
        return success
    except Exception as e:
        results.append({
            "test": name,
            "status": f"❌ ERROR",
            "expected": expected_status,
            "got": str(e),
            "time": 0
        })
        return False

print("=" * 70)
print("🧪 EJECUTANDO PLAN DE PRUEBAS - RIFATRUST")
print("=" * 70)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Base URL: {BASE_URL}")
print("=" * 70)
print()

# MÓDULO 1: PÁGINAS PRINCIPALES
print("📄 MÓDULO 1: PÁGINAS PRINCIPALES")
print("-" * 70)
test_endpoint("Home Page", f"{BASE_URL}/")
test_endpoint("Login Page", f"{BASE_URL}/login/")
test_endpoint("Register Page", f"{BASE_URL}/register/")
test_endpoint("Raffles List", f"{BASE_URL}/raffles/")
test_endpoint("Admin Panel", f"{BASE_URL}/admin-panel/dashboard/", expected_status=302, allow_redirects=False)  # Must redirect to login
print()

# MÓDULO 2: ARCHIVOS ESTÁTICOS
print("📦 MÓDULO 2: ARCHIVOS ESTÁTICOS")
print("-" * 70)
test_endpoint("CSS Principal", f"{BASE_URL}/static/css/styles.css")
test_endpoint("JavaScript Principal", f"{BASE_URL}/static/js/main.js")
test_endpoint("Admin CSS", f"{BASE_URL}/static/css/admin.css")
print()

# MÓDULO 3: API ENDPOINTS
print("🔌 MÓDULO 3: API ENDPOINTS")
print("-" * 70)
test_endpoint("API Root", f"{BASE_URL}/api/")
test_endpoint("API Raffles", f"{BASE_URL}/api/raffles/")
test_endpoint("API Schema", f"{BASE_URL}/api/schema/")
print()

# MÓDULO 4: RECOVERY ENDPOINTS
print("🔐 MÓDULO 4: PASSWORD RECOVERY")
print("-" * 70)
test_endpoint("Password Reset Request", f"{BASE_URL}/password-reset/")
print()

# RESUMEN
print("=" * 70)
print("📊 RESUMEN DE RESULTADOS")
print("=" * 70)

total = len(results)
passed = sum(1 for r in results if "✅ PASS" in r["status"])
failed = total - passed
success_rate = (passed / total * 100) if total > 0 else 0

for result in results:
    print(f"{result['status']:12} | {result['test']:40} | {result['time']:.3f}s")

print("-" * 70)
print(f"Total:   {total} pruebas")
print(f"✅ Pasó:  {passed} ({success_rate:.1f}%)")
print(f"❌ Falló: {failed}")
print("=" * 70)

sys.exit(0 if failed == 0 else 1)
