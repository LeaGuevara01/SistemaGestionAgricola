# config.py
import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER_COMPONENTES = os.path.join(BASE_DIR, 'static/uploads/componentes')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not WEATHER_API_KEY:
        raise RuntimeError("La variable de entorno WEATHER_API_KEY no está definida")

    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL no está configurado")

