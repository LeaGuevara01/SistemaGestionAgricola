import os
from urllib.parse import urlparse

class Config:
    # ✅ USAR DATABASE_URL de Render o SQLite como fallback
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if DATABASE_URL:
        # ✅ CONFIGURACIÓN PARA POSTGRESQL (Render)
        if DATABASE_URL.startswith('postgres://'):
            # Render puede usar postgres:// pero SQLAlchemy necesita postgresql://
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # ✅ FALLBACK A SQLITE LOCAL
        SQLALCHEMY_DATABASE_URI = 'sqlite:///elorza.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
    
    # ✅ CONFIGURACIÓN ADICIONAL PARA POSTGRESQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require'
        } if DATABASE_URL and 'postgres' in DATABASE_URL else {}
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}