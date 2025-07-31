#!/usr/bin/env python3
"""
Test directo de la query de stock con la estructura real
"""

import sys
import os
from pathlib import Path

# Agregar el directorio backend al path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_stock_query():
    try:
        from app import create_app
        from app.utils.db import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("🔍 === TEST DIRECTO DE QUERY DE STOCK ===")
            print()
            
            # Query corregida usando la estructura real
            query = """
            SELECT 
                c."ID" as componente_id,
                c."Nombre" as nombre_componente,
                c."Precio" as precio_unitario,
                COALESCE(COUNT(s."ID"), 0) as total_movimientos,
                COALESCE(SUM(CASE WHEN s."Tipo" = 'Ingreso' THEN s."Cantidad" ELSE 0 END), 0) as entradas,
                COALESCE(SUM(CASE WHEN s."Tipo" = 'Salida' THEN s."Cantidad" ELSE 0 END), 0) as salidas,
                COALESCE(SUM(CASE WHEN s."Tipo" = 'Ingreso' THEN s."Cantidad" 
                                 WHEN s."Tipo" = 'Salida' THEN -s."Cantidad" 
                                 ELSE 0 END), 0) as stock_actual
            FROM componentes c
            LEFT JOIN stock s ON s."ID_Componente" = c."ID"
            GROUP BY c."ID", c."Nombre", c."Precio"
            ORDER BY c."ID"
            LIMIT 10
            """
            
            print("📊 Ejecutando query de resumen de stock...")
            print(f"Query: {query}")
            print()
            
            result = db.session.execute(text(query))
            
            print("✅ Resultados:")
            total_valor = 0
            componentes_data = []
            
            for i, row in enumerate(result):
                stock_actual = int(row.stock_actual or 0)
                precio_unitario = float(row.precio_unitario or 0)
                valor_inventario = stock_actual * precio_unitario
                total_valor += valor_inventario
                
                comp_data = {
                    'componente_id': row.componente_id,
                    'nombre_componente': row.nombre_componente or 'Sin nombre',
                    'precio_unitario': precio_unitario,
                    'entradas': int(row.entradas or 0),
                    'salidas': int(row.salidas or 0),
                    'stock_actual': stock_actual,
                    'total_movimientos': int(row.total_movimientos or 0),
                    'valor_inventario': valor_inventario
                }
                
                componentes_data.append(comp_data)
                
                print(f"  {i+1}. {comp_data['nombre_componente']}")
                print(f"     - Stock actual: {comp_data['stock_actual']}")
                print(f"     - Entradas: {comp_data['entradas']}, Salidas: {comp_data['salidas']}")
                print(f"     - Precio: ${comp_data['precio_unitario']:,.2f}")
                print(f"     - Valor inventario: ${comp_data['valor_inventario']:,.2f}")
                print()
            
            print(f"🎯 RESUMEN GENERAL:")
            print(f"   - Total componentes: {len(componentes_data)}")
            print(f"   - Valor total inventario: ${total_valor:,.2f}")
            print(f"   - Componentes con stock: {len([c for c in componentes_data if c['stock_actual'] > 0])}")
            print()
            
            # Test del endpoint completo
            print("🔄 Probando endpoint completo...")
            import requests
            
            try:
                response = requests.get("http://localhost:5000/api/v1/stock/resumen", timeout=10)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"Componentes en respuesta: {len(data.get('data', []))}")
                    if data.get('data') and len(data['data']) > 1:
                        print("✅ Endpoint funcionando con datos reales!")
                    else:
                        print("⚠️ Endpoint en modo fallback")
                else:
                    print(f"❌ Error: {response.text}")
            except Exception as e:
                print(f"❌ Error probando endpoint: {e}")
            
            db.session.commit()
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stock_query()
