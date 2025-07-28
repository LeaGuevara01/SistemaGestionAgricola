from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
import os

# Importaciones locales se harán en create_app para evitar imports circulares

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object('app.config.Config')
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Importar db aquí para evitar imports circulares
    from app.utils.db import db
    db.init_app(app)
    
    # Migraciones
    migrate = Migrate(app, db)
    
    # Registrar blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)
    
    # Importar modelos para que se registren
    from app.models import Componente, Compra, Maquina, Proveedor, Stock
    
    return app