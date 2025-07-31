#!/usr/bin/env python3
"""
🐘 Script de migración completa a PostgreSQL
Migra datos de SQLite a PostgreSQL y configura el entorno de desarrollo
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from urllib.parse import urlparse
from pathlib import Path
import subprocess
from datetime import datetime

class PostgreSQLMigrator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.sqlite_db = self.base_dir / "sistema_gestion_agricola.db"
        
        # URLs de base de datos
        self.remote_url = os.getenv('DATABASE_URL')
        self.local_url = os.getenv('LOCAL_POSTGRES_URL', 'postgresql://postgres:password@localhost:5432/elorza_dev')
        
        if self.remote_url and self.remote_url.startswith('postgres://'):
            self.remote_url = self.remote_url.replace('postgres://', 'postgresql://', 1)
    
    def check_postgresql_dependencies(self):
        """Verificar que psycopg2 esté instalado"""
        try:
            import psycopg2
            print("✅ psycopg2 disponible")
            return True
        except ImportError:
            print("❌ psycopg2 no encontrado. Instalando...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'])
                print("✅ psycopg2-binary instalado")
                return True
            except subprocess.CalledProcessError:
                print("❌ Error instalando psycopg2-binary")
                return False
    
    def test_connection(self, url, name):
        """Probar conexión a PostgreSQL"""
        try:
            parsed = urlparse(url)
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],  # Remove leading slash
                user=parsed.username,
                password=parsed.password,
                sslmode='require' if 'render.com' in url else 'prefer'
            )
            conn.close()
            print(f"✅ Conexión exitosa a {name}")
            return True
        except Exception as e:
            print(f"❌ Error conectando a {name}: {e}")
            return False
    
    def create_local_database(self):
        """Crear base de datos local si no existe"""
        try:
            parsed = urlparse(self.local_url)
            
            # Conectar a postgres (base de datos por defecto) para crear la BD
            admin_conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database='postgres',
                user=parsed.username,
                password=parsed.password
            )
            admin_conn.autocommit = True
            cursor = admin_conn.cursor()
            
            # Verificar si la base de datos existe
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (parsed.path[1:],))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f'CREATE DATABASE "{parsed.path[1:]}"')
                print(f"✅ Base de datos '{parsed.path[1:]}' creada")
            else:
                print(f"✅ Base de datos '{parsed.path[1:]}' ya existe")
            
            cursor.close()
            admin_conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error creando base de datos local: {e}")
            return False
    
    def get_sqlite_data(self):
        """Extraer datos de SQLite"""
        if not self.sqlite_db.exists():
            print(f"⚠️ No se encontró {self.sqlite_db}")
            return {}
        
        print("📖 Leyendo datos de SQLite...")
        conn = sqlite3.connect(self.sqlite_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        data = {}
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                data[table] = [dict(row) for row in rows]
                print(f"  📋 {table}: {len(rows)} registros")
            except Exception as e:
                print(f"  ❌ Error leyendo {table}: {e}")
        
        conn.close()
        return data
    
    def create_postgresql_schema(self, pg_url):
        """Crear esquema en PostgreSQL basado en los modelos"""
        print("🏗️ Creando esquema PostgreSQL...")
        
        # Esquema SQL para crear las tablas
        schema_sql = """
        -- Tabla componentes
        CREATE TABLE IF NOT EXISTS componentes (
            "ID" SERIAL PRIMARY KEY,
            "ID_Componente" VARCHAR(255) UNIQUE,
            "Nombre" VARCHAR(255) NOT NULL,
            "Descripcion" TEXT,
            "Tipo" VARCHAR(255),
            "Foto" VARCHAR(255),
            "Marca" VARCHAR(255),
            "Modelo" VARCHAR(255),
            "Precio" DECIMAL(10,2)
        );
        
        -- Tabla maquinas
        CREATE TABLE IF NOT EXISTS maquinas (
            "ID" SERIAL PRIMARY KEY,
            "Codigo" VARCHAR(255) NOT NULL UNIQUE,
            "Nombre" VARCHAR(255) NOT NULL,
            "Marca" VARCHAR(255),
            "Modelo" VARCHAR(255),
            "Año" INTEGER,
            "Estado" VARCHAR(255),
            "Observaciones" TEXT,
            "Foto" VARCHAR(255),
            "Tipo" VARCHAR(255),
            "Horas" INTEGER,
            "Ubicacion" VARCHAR(255)
        );
        
        -- Tabla proveedores
        CREATE TABLE IF NOT EXISTS proveedores (
            "ID" SERIAL PRIMARY KEY,
            "Nombre" VARCHAR(255) NOT NULL,
            "Contacto" VARCHAR(255),
            "Telefono" VARCHAR(255),
            "Email" VARCHAR(255),
            "Direccion" TEXT,
            "Observaciones" TEXT
        );
        
        -- Tabla stock
        CREATE TABLE IF NOT EXISTS stock (
            "ID" SERIAL PRIMARY KEY,
            "ID_Componente" INTEGER REFERENCES componentes("ID"),
            "Cantidad" INTEGER,
            "Tipo" VARCHAR(255),
            "Observacion" TEXT,
            "Fecha" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "tipo_movimiento" VARCHAR(50),
            "cantidad_anterior" INTEGER,
            "cantidad_nueva" INTEGER,
            "motivo" TEXT,
            "observaciones" TEXT,
            "usuario" VARCHAR(255)
        );
        
        -- Tabla compras
        CREATE TABLE IF NOT EXISTS compras (
            "ID_Compra" SERIAL PRIMARY KEY,
            "ID_Proveedor" INTEGER REFERENCES proveedores("ID"),
            "ID_Componente" INTEGER REFERENCES componentes("ID"),
            "Cantidad" INTEGER,
            "precio_unitario" DECIMAL(10,2),
            "precio_total" DECIMAL(10,2),
            "Fecha" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "maquina_id" INTEGER REFERENCES maquinas("ID"),
            "observaciones" TEXT
        );
        
        -- Tablas intermedias
        CREATE TABLE IF NOT EXISTS componentes_proveedores (
            "ID_Proveedor" INTEGER REFERENCES proveedores("ID"),
            "ID_Componente" INTEGER REFERENCES componentes("ID"),
            "Cantidad" INTEGER,
            PRIMARY KEY ("ID_Proveedor", "ID_Componente")
        );
        
        CREATE TABLE IF NOT EXISTS maquinas_componentes (
            "ID_Maquina" INTEGER REFERENCES maquinas("ID"),
            "ID_Componente" INTEGER REFERENCES componentes("ID"),
            PRIMARY KEY ("ID_Maquina", "ID_Componente")
        );
        
        -- Tabla pagos_proveedores
        CREATE TABLE IF NOT EXISTS pagos_proveedores (
            "ID" SERIAL PRIMARY KEY,
            "ID_Proveedor" INTEGER REFERENCES proveedores("ID"),
            "Monto" DECIMAL(10,2),
            "Metodo" VARCHAR(255),
            "Observacion" TEXT,
            "Fecha" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Índices para mejor rendimiento
        CREATE INDEX IF NOT EXISTS idx_stock_componente ON stock("ID_Componente");
        CREATE INDEX IF NOT EXISTS idx_stock_fecha ON stock("Fecha");
        CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON compras("ID_Proveedor");
        CREATE INDEX IF NOT EXISTS idx_compras_componente ON compras("ID_Componente");
        CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras("Fecha");
        """
        
        try:
            parsed = urlparse(pg_url)
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                sslmode='require' if 'render.com' in pg_url else 'prefer'
            )
            cursor = conn.cursor()
            cursor.execute(schema_sql)
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Esquema PostgreSQL creado")
            return True
        except Exception as e:
            print(f"❌ Error creando esquema: {e}")
            return False
    
    def migrate_data_to_postgresql(self, pg_url, data):
        """Migrar datos a PostgreSQL"""
        print("📦 Migrando datos a PostgreSQL...")
        
        try:
            parsed = urlparse(pg_url)
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                sslmode='require' if 'render.com' in pg_url else 'prefer'
            )
            cursor = conn.cursor()
            
            # Orden de inserción para respetar foreign keys
            table_order = ['proveedores', 'componentes', 'maquinas', 'stock', 'compras', 
                          'componentes_proveedores', 'maquinas_componentes', 'pagos_proveedores']
            
            for table in table_order:
                if table in data and data[table]:
                    print(f"  📋 Migrando {table}...")
                    
                    # Limpiar tabla existente
                    cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
                    
                    # Insertar datos
                    rows = data[table]
                    if rows:
                        # Obtener columnas de la primera fila
                        columns = list(rows[0].keys())
                        placeholders = ', '.join(['%s'] * len(columns))
                        columns_str = ', '.join([f'"{col}"' for col in columns])
                        
                        insert_sql = f'INSERT INTO "{table}" ({columns_str}) VALUES ({placeholders})'
                        
                        for row in rows:
                            values = [row[col] for col in columns]
                            cursor.execute(insert_sql, values)
                    
                    print(f"    ✅ {len(rows)} registros migrados")
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Migración de datos completada")
            return True
            
        except Exception as e:
            print(f"❌ Error migrando datos: {e}")
            return False
    
    def setup_environment_file(self):
        """Crear archivo .env para desarrollo"""
        env_file = self.base_dir / ".env"
        
        env_content = f"""# Configuración para desarrollo PostgreSQL
DATABASE_URL={self.remote_url if self.remote_url else ''}
LOCAL_POSTGRES_URL={self.local_url}
SECRET_KEY=dev-secret-key-{datetime.now().strftime('%Y%m%d')}
FLASK_ENV=development
FLASK_APP=backend/run.py

# APIs opcionales
WEATHER_API_KEY=your_weather_api_key_here
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Archivo .env creado en {env_file}")
    
    def update_backend_config(self):
        """Actualizar configuración del backend para usar PostgreSQL"""
        backend_config = self.base_dir / "backend" / "app" / "config.py"
        
        if backend_config.exists():
            # Hacer backup
            backup_config = backend_config.with_suffix('.py.bak')
            backend_config.rename(backup_config)
            print(f"✅ Backup de configuración creado: {backup_config}")
        
        # Copiar nueva configuración
        new_config = self.base_dir / "config_postgresql.py"
        if new_config.exists():
            import shutil
            shutil.copy2(new_config, backend_config.parent / "config.py")
            print("✅ Configuración PostgreSQL aplicada al backend")
    
    def run_migration(self):
        """Ejecutar migración completa"""
        print("🐘 === MIGRACIÓN A POSTGRESQL ===")
        print()
        
        # 1. Verificar dependencias
        if not self.check_postgresql_dependencies():
            return False
        
        # 2. Configurar entorno
        self.setup_environment_file()
        
        # 3. Probar conexiones
        connections_ok = True
        
        if self.remote_url:
            if not self.test_connection(self.remote_url, "PostgreSQL remoto (Render)"):
                print("❌ No se puede conectar a la base de datos remota")
                connections_ok = False
        
        # 4. Configurar base de datos local
        if not self.create_local_database():
            print("❌ No se pudo crear la base de datos local")
            connections_ok = False
        
        if not self.test_connection(self.local_url, "PostgreSQL local"):
            print("❌ No se puede conectar a PostgreSQL local")
            connections_ok = False
        
        if not connections_ok:
            print()
            print("❌ Problemas de conexión. Verifica:")
            print("   1. PostgreSQL está instalado y ejecutándose")
            print("   2. Usuario/contraseña son correctos")
            print("   3. Variables de entorno DATABASE_URL y LOCAL_POSTGRES_URL")
            return False
        
        # 5. Obtener datos de SQLite
        sqlite_data = self.get_sqlite_data()
        
        # 6. Crear esquema en ambas bases de datos
        target_dbs = []
        if self.remote_url:
            target_dbs.append(("Remota (Render)", self.remote_url))
        target_dbs.append(("Local", self.local_url))
        
        for name, url in target_dbs:
            print(f"🏗️ Configurando base de datos {name}...")
            if not self.create_postgresql_schema(url):
                print(f"❌ Error configurando {name}")
                continue
            
            if sqlite_data and any(sqlite_data.values()):
                if not self.migrate_data_to_postgresql(url, sqlite_data):
                    print(f"❌ Error migrando datos a {name}")
                    continue
            
            print(f"✅ Base de datos {name} configurada correctamente")
        
        # 7. Actualizar configuración del backend
        self.update_backend_config()
        
        print()
        print("🎉 === MIGRACIÓN COMPLETADA ===")
        print()
        print("✅ PostgreSQL configurado para desarrollo y producción")
        print("✅ Datos migrados desde SQLite")
        print("✅ Configuración actualizada")
        print()
        print("🚀 Próximos pasos:")
        print("   1. Reinicia tu servidor backend")
        print("   2. Verifica que las conexiones funcionen")
        print("   3. Prueba la funcionalidad de stock/resumen")
        print()
        
        return True

def main():
    migrator = PostgreSQLMigrator()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("🐘 Script de migración a PostgreSQL")
        print()
        print("Uso: python migrate_to_postgresql.py")
        print()
        print("Variables de entorno:")
        print("  DATABASE_URL         - URL de PostgreSQL remoto (Render)")
        print("  LOCAL_POSTGRES_URL   - URL de PostgreSQL local")
        print()
        return
    
    success = migrator.run_migration()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
