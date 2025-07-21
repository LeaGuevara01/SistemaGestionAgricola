# sistema_gestion_agricola/config.py
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
    WEATHER_API_URL = os.getenv("WEATHER_API_URL")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    @classmethod
    def check_env_vars(cls):
        missing = []
        if not cls.WEATHER_API_KEY:
            missing.append("WEATHER_API_KEY")
        if not cls.SQLALCHEMY_DATABASE_URI:
            missing.append("DATABASE_URL")
        if not cls.SECRET_KEY:
            missing.append("SECRET_KEY")
        if missing:
            raise RuntimeError(f"Faltan variables de entorno: {', '.join(missing)}")

class DevelopmentConfig(Config):
    FLASK_ENV = "development"
    ENV = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'dev.db')}"

class ProductionConfig(Config):
    FLASK_ENV = "production"
    ENV = "production"
    DEBUG = False
    
class BaseConfig:
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    WEATHER_API_URL = os.getenv("WEATHER_API_URL") or "https://api.openweathermap.org/data/2.5/weather"
    COORDENADAS_UCACHA = {'lat': -32.3167, 'lon': -63.6667}

    @staticmethod
    def check_env_vars():
        missing = []
        if not os.getenv("WEATHER_API_KEY"):
            missing.append("WEATHER_API_KEY")
        if missing:
            raise EnvironmentError(f"Faltan variables de entorno requeridas: {', '.join(missing)}")