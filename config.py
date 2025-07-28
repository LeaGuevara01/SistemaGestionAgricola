# config.py
import os

class Config:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sistema_gestion_agricola'))

    UPLOAD_FOLDER_COMPONENTES = os.path.join(BASE_DIR, 'static', 'fotos', 'componentes')
    UPLOAD_FOLDER_MAQUINAS = os.path.join(BASE_DIR, 'static', 'fotos', 'maquinas')

    COORDENADAS_UCACHA = {
        'lat': -33.0320,
        'lon': -63.5066
    }

    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5/weather")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Configuraciones de seguridad
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo para uploads
    UPLOAD_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "memory://")

    @classmethod
    def check_env_vars(cls):
        missing = []
        if not cls.WEATHER_API_KEY:
            missing.append("WEATHER_API_KEY")
        if not cls.SQLALCHEMY_DATABASE_URI:
            missing.append("DATABASE_URL")
        if not cls.SECRET_KEY:
            missing.append("SECRET_KEY")
        elif len(cls.SECRET_KEY) < 32:
            raise RuntimeError("SECRET_KEY debe tener al menos 32 caracteres")
        if missing:
            raise RuntimeError(f"Faltan variables de entorno: {', '.join(missing)}")

class DevelopmentConfig(Config):
    DEBUG = True
    USE_REACT = False  # HTML por defecto en desarrollo
    FRONTEND_MODE = 'html'

class ProductionConfig(Config):
    DEBUG = False
    USE_REACT = True   # React en producción
    FRONTEND_MODE = 'react'