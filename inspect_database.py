#!/usr/bin/env python3
"""
Script para inspeccionar la estructura real de la base de datos PostgreSQL
"""

import os
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def inspect_database():
    try:
        from app import create_app
        from app.utils.db import db
        from sqlalchemy import inspect, text
        
        app = create_app()
        
        with app.app_context():
            inspector = inspect(db.engine)
            
            print("🔍 === INSPECCIÓN DE BASE DE DATOS ===")
            print()
            
            # Inspeccionar tabla stock
            print("📋 Estructura de tabla 'stock':")
            if 'stock' in inspector.get_table_names():
                columns = inspector.get_columns('stock')
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                
                print()
                print("📊 Muestra de datos en tabla 'stock':")
                try:
                    result = db.session.execute(text('SELECT * FROM stock LIMIT 5'))
                    rows = result.fetchall()
                    if rows:
                        for i, row in enumerate(rows):
                            print(f"  Fila {i+1}: {dict(row._mapping)}")
                    else:
                        print("  (Sin datos)")
                except Exception as e:
                    print(f"  Error consultando datos: {e}")
            else:
                print("  ❌ Tabla 'stock' no encontrada")
            
            print()
            print("📋 Estructura de tabla 'componentes':")
            if 'componentes' in inspector.get_table_names():
                columns = inspector.get_columns('componentes')
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                
                print()
                print("📊 Muestra de datos en tabla 'componentes':")
                try:
                    result = db.session.execute(text('SELECT * FROM componentes LIMIT 3'))
                    rows = result.fetchall()
                    if rows:
                        for i, row in enumerate(rows):
                            print(f"  Fila {i+1}: {dict(row._mapping)}")
                    else:
                        print("  (Sin datos)")
                except Exception as e:
                    print(f"  Error consultando datos: {e}")
            
            print()
            print("📋 Todas las tablas disponibles:")
            tables = inspector.get_table_names()
            for table in tables:
                try:
                    result = db.session.execute(text(f'SELECT COUNT(*) as total FROM "{table}"'))
                    count = result.scalar()
                    print(f"  - {table}: {count} registros")
                except Exception as e:
                    print(f"  - {table}: Error contando - {e}")
            
            db.session.commit()
            
    except Exception as e:
        print(f"❌ Error inspeccionando base de datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_database()
