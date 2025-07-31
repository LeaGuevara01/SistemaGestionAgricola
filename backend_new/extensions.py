"""
Extensiones de Flask para el Sistema de Gestión Agrícola
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instancias de extensiones
db = SQLAlchemy()
migrate = Migrate()

def init_app(app):
    """Inicializar extensiones con la aplicación Flask"""
    db.init_app(app)
    migrate.init_app(app, db)
