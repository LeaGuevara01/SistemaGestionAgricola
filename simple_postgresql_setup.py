#!/usr/bin/env python3
"""
🐘 Migración simple a PostgreSQL usando la base de datos de Render
"""

import os
import sys
import sqlite3
import psycopg2
from urllib.parse import urlparse
from pathlib import Path

def main():
    print("🐘 === MIGRACIÓN SIMPLIFICADA A POSTGRESQL ===")
    print()
    
    # Verificar DATABASE_URL de Render
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL no configurada")
        print("🔧 Configura la variable de entorno DATABASE_URL con la URL de tu base de datos de Render")
        print("   Ejemplo: set DATABASE_URL=postgresql://user:pass@host:port/database")
        return False
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"🔗 Usando base de datos: {database_url.split('@')[1] if '@' in database_url else 'configurada'}")
    
    # Probar conexión
    try:
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            sslmode='require'
        )
        print("✅ Conexión exitosa a PostgreSQL")
        conn.close()
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Actualizar configuración para usar solo PostgreSQL
    print("🔧 Actualizando configuración...")
    
    # Crear configuración optimizada
    config_content = '''# config.py - Configuración PostgreSQL
import os
from urllib.parse import urlparse

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    
    # Configuración de uploads
    UPLOAD_FOLDER_COMPONENTES = os.path.join(STATIC_DIR, 'fotos', 'componentes')
    UPLOAD_FOLDER_MAQUINAS = os.path.join(STATIC_DIR, 'fotos', 'maquinas')
    UPLOAD_FOLDER_GENERAL = os.path.join(STATIC_DIR, 'uploads')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
    
    # 🐘 POSTGRESQL ÚNICO
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Configuración optimizada para PostgreSQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'connect_args': {'sslmode': 'require'} if DATABASE_URL else {}
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-postgresql")
    
    # APIs externas
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5/weather")
    
    COORDENADAS_UCACHA = {'lat': -33.0320, 'lon': -63.5066}

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
'''
    
    # Actualizar config.py
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("✅ config.py actualizado")
    
    # Actualizar backend config si existe
    backend_config = Path('backend/app/config.py')
    if backend_config.exists():
        with open(backend_config, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ backend/app/config.py actualizado")
    
    # Crear .env optimizado
    env_content = f'''# Configuración PostgreSQL
DATABASE_URL={database_url}
SECRET_KEY=dev-secret-key-{os.urandom(8).hex()}
FLASK_ENV=development
FLASK_APP=backend/run.py
'''
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("✅ .env actualizado")
    
    # Actualizar utils/db.py para usar manejo robusto de transacciones
    db_utils_content = '''from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import InternalError, OperationalError, InvalidRequestError
import time

db = SQLAlchemy()

def commit_or_rollback():
    """Commit con manejo de errores mejorado"""
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Error en commit: {e}")
        raise e

def reset_transaction():
    """Reiniciar transacción PostgreSQL"""
    try:
        print("🔄 Reseteando transacción PostgreSQL...")
        db.session.rollback()
        db.session.close()
        db.session.remove()
        
        # Verificar nueva sesión
        db.session.execute(db.text("SELECT 1"))
        db.session.commit()
        print("✅ Transacción reseteada")
        return True
    except Exception as e:
        print(f"❌ Error reseteando: {e}")
        try:
            db.session.close()
            db.session.remove()
        except:
            pass
        return False

def safe_query_execute(query_func):
    """Ejecutar query con reintentos"""
    for attempt in range(3):
        try:
            return query_func()
        except (InternalError, OperationalError) as e:
            if 'current transaction is aborted' in str(e):
                print(f"🔄 Transacción abortada, reintentando ({attempt + 1}/3)")
                reset_transaction()
                if attempt < 2:
                    time.sleep(0.5)
                    continue
            raise e

def check_transaction_state():
    """Verificar estado de transacción"""
    try:
        db.session.execute(db.text("SELECT 1"))
        return True
    except Exception:
        return False
'''
    
    backend_db_utils = Path('backend/app/utils/db.py')
    if backend_db_utils.exists():
        with open(backend_db_utils, 'w', encoding='utf-8') as f:
            f.write(db_utils_content)
        print("✅ backend/app/utils/db.py actualizado")
    
    print()
    print("🎉 === MIGRACIÓN COMPLETADA ===")
    print()
    print("✅ Configuración actualizada para PostgreSQL único")
    print("✅ Manejo robusto de transacciones implementado")
    print("✅ Variables de entorno configuradas")
    print()
    print("🚀 Próximos pasos:")
    print("   1. Reinicia tu servidor backend:")
    print("      cd backend && python run.py")
    print()
    print("   2. Verifica el endpoint problemático:")
    print("      http://localhost:5000/api/v1/stock/resumen")
    print()
    print("✨ El error de transacciones abortadas debería estar resuelto!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
