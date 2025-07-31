#!/usr/bin/env python3
"""
Test rápido para verificar las rutas de máquinas y componentes
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_routes():
    print("🧪 Iniciando tests de rutas...")
    
    # Test 1: Health check
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: Listar máquinas
    try:
        response = requests.get(f'{BASE_URL}/api/v1/maquinas')
        print(f"✅ GET /api/v1/maquinas: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total máquinas: {data.get('total', 0)}")
            if data.get('data'):
                primera_maquina = data['data'][0]
                print(f"   Primera máquina: {primera_maquina.get('nombre')} ({primera_maquina.get('codigo')})")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ GET maquinas failed: {e}")
    
    # Test 3: Listar componentes
    try:
        response = requests.get(f'{BASE_URL}/api/v1/componentes')
        print(f"✅ GET /api/v1/componentes: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total componentes: {data.get('total', 0)}")
            if data.get('data'):
                primer_componente = data['data'][0]
                print(f"   Primer componente: {primer_componente.get('nombre')} - {primer_componente.get('categoria')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ GET componentes failed: {e}")
    
    # Test 4: Estadísticas de máquinas
    try:
        response = requests.get(f'{BASE_URL}/api/v1/maquinas/stats')
        print(f"✅ GET /api/v1/maquinas/stats: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('data', {})
            print(f"   Total: {stats.get('total')}, Activas: {stats.get('activas')}")
            print(f"   Operativas: {stats.get('operativo')}, Mantenimiento: {stats.get('mantenimiento')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ GET stats failed: {e}")
    
    # Test 5: Máquina específica
    try:
        response = requests.get(f'{BASE_URL}/api/v1/maquinas/2')
        print(f"✅ GET /api/v1/maquinas/2: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            maquina = data.get('data', {})
            print(f"   Máquina: {maquina.get('nombre')} - {maquina.get('marca')} {maquina.get('modelo')}")
            print(f"   Estado: {maquina.get('estado')}, Año: {maquina.get('año')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ GET maquina específica failed: {e}")
    
    print("\n🎉 Tests completados!")

if __name__ == '__main__':
    test_routes()
