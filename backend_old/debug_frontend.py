#!/usr/bin/env python3
"""
Debug script para verificar exactamente qué respuestas están llegando al frontend
"""

from app import create_app
import json

app = create_app()
with app.test_client() as client:
    print("🔍 DEBUG: Verificando respuestas exactas de las APIs")
    
    # Test detallado de componentes
    print("\n=== TEST COMPONENTES ===")
    response = client.get('/api/v1/componentes')
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.get_json()
        print("\n📋 Estructura completa de respuesta:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        print(f"\n📊 Análisis:")
        print(f"- success: {data.get('success')}")
        print(f"- total: {data.get('total')}")
        print(f"- data type: {type(data.get('data'))}")
        print(f"- data length: {len(data.get('data', []))}")
        
        if data.get('data'):
            primer_componente = data['data'][0]
            print(f"\n🔍 Primer componente keys: {list(primer_componente.keys())}")
            print(f"- id: {primer_componente.get('id')}")
            print(f"- nombre: {primer_componente.get('nombre')}")
            print(f"- categoria: {primer_componente.get('categoria')}")
            print(f"- precio_unitario: {primer_componente.get('precio_unitario')}")
    else:
        print(f"❌ Error: {response.get_data(as_text=True)}")
    
    # Test con filtros
    print("\n=== TEST COMPONENTES CON FILTROS ===")
    response = client.get('/api/v1/componentes?q=aceite&page=1&per_page=5')
    if response.status_code == 200:
        data = response.get_json()
        print(f"Resultados con filtro 'aceite': {len(data.get('data', []))}")
        if data.get('data'):
            for comp in data['data']:
                print(f"- {comp.get('nombre')} ({comp.get('categoria')})")
    
    # Test de máquinas para comparar
    print("\n=== TEST MÁQUINAS (COMPARACIÓN) ===")
    response = client.get('/api/v1/maquinas')
    if response.status_code == 200:
        data = response.get_json()
        print(f"Máquinas - Keys: {list(data.keys())}")
        print(f"Máquinas - Total: {data.get('total')}")
        print(f"Máquinas - Data type: {type(data.get('data'))}")
        print(f"Máquinas - Data length: {len(data.get('data', []))}")
    
    print("\n✅ Debug completado!")
