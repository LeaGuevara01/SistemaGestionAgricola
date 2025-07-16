# __init__.py
import os
from flask import Flask, render_template, make_response, jsonify

# Helper para Render
from .utils.vite_helper import vite_asset #onrender

# Cargar instancia única de cache
from flask_caching import Cache
from .cache_config import cache

from flask_migrate import Migrate
from .models import db
migrate = Migrate()

# Cargar variables de entorno
from dotenv import load_dotenv
import os

if os.environ.get("FLASK_ENV") == "development":
    load_dotenv(".env.development")
else:
    load_dotenv()

def create_app():
    
    # .env según entorno
    if os.getenv("FLASK_ENV") == "development":
        load_dotenv(".env.development")
        from config import DevelopmentConfig as ConfigClass
    else:
        load_dotenv(".env.production")
        from config import ProductionConfig as ConfigClass

    # Validate
    ConfigClass.check_env_vars()

    app = Flask(__name__)
    app.config.from_object(ConfigClass)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Cache Config
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 1800
    cache.init_app(app)

    # Folders Config
    os.makedirs(app.config['UPLOAD_FOLDER_MAQUINAS'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_COMPONENTES'], exist_ok=True)
    app.config['UPLOAD_FOLDER_MAQUINAS'] = ConfigClass.UPLOAD_FOLDER_MAQUINAS
    app.config['UPLOAD_FOLDER_COMPONENTES'] = ConfigClass.UPLOAD_FOLDER_COMPONENTES

    # Weather Config
    app.config['WEATHER_API_URL'] = ConfigClass.WEATHER_API_URL
    app.config['COORDENADAS_UCACHA'] = ConfigClass.COORDENADAS_UCACHA
    
    # Blueprints Registration
    from .routes.clima import clima_bp
    from .routes.maquinas import maquinas_bp
    from .routes.componentes import componentes_bp
    from .routes.stock import stock_bp
    from .routes.compras import compras_bp
    from .routes.pagos import pagos_bp
    from .routes.proveedores import proveedores_bp
    from .routes.estadisticas import estadisticas_bp
    from .routes.pdf_printing import pdf_bp

    app.register_blueprint(clima_bp)
    app.register_blueprint(maquinas_bp)
    app.register_blueprint(componentes_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(estadisticas_bp)
    app.register_blueprint(pdf_bp)

    def registrar_manejadores_errores(app):
        # Funciones de ruta generales
        @app.route('/')
        def index():
            return render_template('index.html')
        
        @app.errorhandler(404)
        def not_found(error):
            return jsonify({'status': 'error', 'message': 'Recurso no encontrado', 'data': None}), 404

        @app.errorhandler(500)
        def internal_error(error):
            return jsonify({'status': 'error', 'message': 'Error interno del servidor', 'data': None}), 500

        @app.errorhandler(Exception)
        def all_exception_handler(error):
            return jsonify({'status': 'error', 'message': str(error), 'data': None}), 500

    @app.route('/vite')
    def vite_app():
        return render_template('vite.html')  # plantilla que solo tiene <div id="app"></div> y carga Vite

    app.jinja_env.globals['vite_asset'] = vite_asset

    registrar_manejadores_errores(app)
    return app
