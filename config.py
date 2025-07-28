# config.py - Configuración centralizada y consolidada
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
    
    # Base de datos - PostgreSQL con fallback a SQLite
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        # Render usa postgres:// pero SQLAlchemy necesita postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        # Configuración para PostgreSQL en producción
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'connect_args': {'sslmode': 'require'}
        }
    else:
        # Fallback a SQLite para desarrollo local
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "sistema_gestion_agricola.db")}'
        SQLALCHEMY_ENGINE_OPTIONS = {}
    
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
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "memory://")

    @classmethod
    def check_env_vars(cls):
        """Verificar variables de entorno críticas"""
        missing = []
        warnings = []
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == "dev-secret-key-change-in-production":
            warnings.append("SECRET_KEY usando valor por defecto - cambiar en producción")
        elif len(cls.SECRET_KEY) < 32:
            raise RuntimeError("SECRET_KEY debe tener al menos 32 caracteres")
            
        if not cls.DATABASE_URL:
            warnings.append("DATABASE_URL no configurada - usando SQLite local")
            
        if not cls.WEATHER_API_KEY:
            warnings.append("WEATHER_API_KEY no configurada - funcionalidad del clima deshabilitada")
        
        if warnings:
            print("⚠️  Advertencias de configuración:")
            for warning in warnings:
                print(f"   - {warning}")
        
        if missing:
            raise RuntimeError(f"Variables de entorno críticas faltantes: {', '.join(missing)}")

class DevelopmentConfig(Config):
    DEBUG = True
    FRONTEND_MODE = 'react'  # Usar React en desarrollo también

class ProductionConfig(Config):
    DEBUG = False
    FRONTEND_MODE = 'react'

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}