"""
Script para inspeccionar el schema de la base de datos PostgreSQL
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect
from sqlalchemy.sql import text

def print_database_schema():
    """Imprimir el schema completo de la base de datos"""
    
    # URL de la base de datos
    database_url = os.getenv('DATABASE_URL', 'postgresql://elorza:g65hHAdGLwoOYl33zlPRnVyzdsY6FsD1@dpg-d1qpnlodl3ps73eln790-a.oregon-postgres.render.com/sistema_gestion_agricola')
    
    try:
        # Crear conexión
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        print("🔍 INSPECCIÓN DEL SCHEMA DE LA BASE DE DATOS")
        print("=" * 60)
        print(f"📊 Base de datos: {database_url.split('@')[-1]}")
        print()
        
        # Obtener todas las tablas
        tables = inspector.get_table_names()
        print(f"📋 Tablas encontradas ({len(tables)}):")
        for table in tables:
            print(f"   - {table}")
        print()
        
        # Inspeccionar cada tabla
        for table_name in tables:
            print(f"🏗️  TABLA: {table_name}")
            print("-" * 40)
            
            # Obtener columnas
            columns = inspector.get_columns(table_name)
            print("📊 Columnas:")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col['default'] else ""
                print(f"   {col['name']:<20} {str(col['type']):<20} {nullable}{default}")
            
            # Obtener claves primarias
            pk = inspector.get_pk_constraint(table_name)
            if pk['constrained_columns']:
                print(f"🔑 Clave primaria: {', '.join(pk['constrained_columns'])}")
            
            # Obtener claves foráneas
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                print("🔗 Claves foráneas:")
                for fk in fks:
                    print(f"   {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            # Obtener índices
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print("📇 Índices:")
                for idx in indexes:
                    unique = "UNIQUE" if idx['unique'] else ""
                    print(f"   {idx['name']}: {', '.join(idx['column_names'])} {unique}")
            
            print()
        
        # Ejecutar algunas consultas de muestra para ver datos
        print("📋 DATOS DE MUESTRA")
        print("=" * 40)
        
        with engine.connect() as conn:
            for table_name in tables[:3]:  # Solo las primeras 3 tablas
                try:
                    result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    print(f"🔍 Muestra de {table_name}:")
                    if rows:
                        print(f"   Columnas: {list(columns)}")
                        for i, row in enumerate(rows):
                            print(f"   Fila {i+1}: {dict(zip(columns, row))}")
                    else:
                        print("   (Tabla vacía)")
                    print()
                except Exception as e:
                    print(f"   Error al leer {table_name}: {e}")
                    print()
        
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        print("Verifica la URL de conexión y que la base de datos esté accesible.")
        return False
    
    return True

if __name__ == "__main__":
    print_database_schema()
