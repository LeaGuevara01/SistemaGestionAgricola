# config.py - Configuración PostgreSQL
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
