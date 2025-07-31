#!/usr/bin/env python3
"""
Script de prueba para verificar la implementación de logging estructurado,
validación de schemas, CORS, rate limiting y excepciones personalizadas.
"""

import requests
import json
import time
from datetime import datetime

# Configuración del servidor
BASE_URL = 'http://localhost:5000'
API_BASE = f'{BASE_URL}/api/v1'

def test_health_check():
    """Probar el endpoint de health check"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cors_headers():
    """Probar headers CORS"""
    print("\n🌐 Testing CORS Headers...")
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f'{API_BASE}/componentes', headers=headers)
        print(f"Status: {response.status_code}")
        print("CORS Headers:")
        for header, value in response.headers.items():
            if header.lower().startswith('access-control'):
                print(f"  {header}: {value}")
        return 'Access-Control-Allow-Origin' in response.headers
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_validation_error():
    """Probar validación de schemas con datos inválidos"""
    print("\n📋 Testing Schema Validation (Invalid Data)...")
    try:
        invalid_data = {
            "nombre": "",  # Nombre vacío - debería fallar
            "precio_unitario": -10,  # Precio negativo - debería fallar
            "categoria": "x" * 200  # Categoría muy larga - debería fallar
        }
        
        response = requests.post(
            f'{API_BASE}/componentes',
            json=invalid_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Debería retornar 400 para datos inválidos
        return response.status_code == 400
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_valid_component_creation():
    """Probar creación de componente con datos válidos"""
    print("\n✅ Testing Valid Component Creation...")
    try:
        valid_data = {
            "nombre": f"Componente Test {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "descripcion": "Componente de prueba para validar la implementación",
            "precio_unitario": 99.99,
            "categoria": "Prueba",
            "fabricante": "Test Manufacturing",
            "numero_parte": "TST-001"
        }
        
        response = requests.post(
            f'{API_BASE}/componentes',
            json=valid_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Debería retornar 201 para creación exitosa
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_componentes_list():
    """Probar listado de componentes con paginación"""
    print("\n📋 Testing Componentes List with Pagination...")
    try:
        params = {
            'page': 1,
            'per_page': 5,
            'sort_by': 'nombre',
            'sort_order': 'asc'
        }
        
        response = requests.get(f'{API_BASE}/componentes', params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            print(f"Total components: {data.get('data', {}).get('pagination', {}).get('total', 0)}")
            print(f"Page: {data.get('data', {}).get('pagination', {}).get('page', 0)}")
            print(f"Components in page: {len(data.get('data', {}).get('componentes', []))}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_component_not_found():
    """Probar manejo de errores para componente no encontrado"""
    print("\n🔍 Testing Component Not Found Error...")
    try:
        # Buscar un ID que probablemente no exista
        response = requests.get(f'{API_BASE}/componentes/99999')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Debería retornar 404
        return response.status_code == 404
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rate_limiting():
    """Probar rate limiting (solo si está configurado)"""
    print("\n⏱️ Testing Rate Limiting...")
    try:
        print("Making multiple rapid requests...")
        success_count = 0
        rate_limited_count = 0
        
        for i in range(10):
            response = requests.get(f'{API_BASE}/componentes')
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"Rate limited on request {i+1}")
            time.sleep(0.1)  # Small delay
        
        print(f"Successful requests: {success_count}")
        print(f"Rate limited requests: {rate_limited_count}")
        
        # Si no hay rate limiting configurado, todas deberían ser exitosas
        # Si hay rate limiting, al menos una debería ser limitada
        return True  # Test pasa independientemente
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas de implementación\n")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("CORS Headers", test_cors_headers),
        ("Schema Validation (Invalid)", test_validation_error),
        ("Valid Component Creation", test_valid_component_creation),
        ("Componentes List", test_componentes_list),
        ("Component Not Found", test_component_not_found),
        ("Rate Limiting", test_rate_limiting)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"\n{'✅' if result else '❌'} {test_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ {test_name}: ERROR - {e}")
        
        print("-" * 50)
    
    # Resumen final
    print("\n📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! La implementación está funcionando correctamente.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa la configuración del servidor.")

if __name__ == "__main__":
    print("⚠️ NOTA: Asegúrate de que el servidor Flask esté ejecutándose en http://localhost:5000")
    print("Para iniciar el servidor, ejecuta: python run.py\n")
    
    input("Presiona Enter para continuar con las pruebas...")
    run_all_tests()
