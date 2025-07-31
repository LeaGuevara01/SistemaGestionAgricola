#!/usr/bin/env python3
"""
Script de prueba para el endpoint de stock/resumen
"""

import requests
import json
import sys

def test_endpoint():
    url = "http://localhost:5000/api/v1/stock/resumen"
    
    try:
        print("🔄 Probando endpoint de stock/resumen...")
        print(f"URL: {url}")
        
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Analizar los datos
            if 'data' in data and data['data']:
                print(f"\n📊 Análisis:")
                print(f"- Total componentes: {len(data['data'])}")
                print(f"- Valor inventario: ${data.get('valor_total_inventario', 0):,.2f}")
                
                for comp in data['data'][:3]:  # Mostrar primeros 3
                    print(f"- {comp['nombre_componente']}: Stock {comp['stock_actual']}")
            else:
                print("⚠️ Sin datos en la respuesta")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está ejecutándose el servidor?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint()
