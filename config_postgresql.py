# config.py - Configuración optimizada para PostgreSQL
import os
from urllib.parse import urlparse

class Config:
    # Directorios base
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    
    # Configuración de uploads
    UPLOAD_FOLDER_COMPONENTES = os.path.join(STATIC_DIR, 'fotos', 'componentes')
    UPLOAD_FOLDER_MAQUINAS = os.path.join(STATIC_DIR, 'fotos', 'maquinas')
    UPLOAD_FOLDER_GENERAL = os.path.join(STATIC_DIR, 'uploads')
    
    # Configuraciones de seguridad para uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    UPLOAD_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
    
    # ✅ CONFIGURACIÓN POSTGRESQL-FIRST
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Para desarrollo local, usar PostgreSQL local si está disponible
    LOCAL_POSTGRES_URL = os.getenv('LOCAL_POSTGRES_URL', 'postgresql://postgres:password@localhost:5432/elorza_dev')
    
    if DATABASE_URL:
        # Producción con Render
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        print("🐘 Usando PostgreSQL de producción (Render)")
    else:
        # Desarrollo - intentar PostgreSQL local primero
        try:
            import psycopg2
            SQLALCHEMY_DATABASE_URI = LOCAL_POSTGRES_URL
            print("🐘 Usando PostgreSQL local para desarrollo")
        except ImportError:
            # Solo como último recurso usar SQLite
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "sistema_gestion_agricola.db")}'
            print("⚠️ PostgreSQL no disponible, usando SQLite (no recomendado)")
    
    # Configuración optimizada para PostgreSQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'echo': False,  # Cambiar a True para debug SQL
    }
    
    # Solo agregar SSL para conexiones remotas
    if DATABASE_URL and ('render.com' in DATABASE_URL or 'amazonaws.com' in DATABASE_URL):
        SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {'sslmode': 'require'}
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # APIs externas
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5/weather")
    
    # Coordenadas de referencia
    COORDENADAS_UCACHA = {
        'lat': -33.0320,
        'lon': -63.5066
    }
    
    # Rate limiting
    RATE_LIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    
    # Configuración específica para desarrollo vs producción
    DEVELOPMENT = not bool(DATABASE_URL)

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': True,  # Ver SQL queries en desarrollo
    }

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost:5432/elorza_test'

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
