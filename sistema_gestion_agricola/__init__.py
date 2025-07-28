# __init__.py
import os
import logging
from flask import Flask, render_template, make_response, jsonify, request

# Helper para Render
from .utils.vite_helper import vite_asset #onrender

# Cargar instancia única de cache
from flask_caching import Cache
from .cache_config import cache

from flask_migrate import Migrate
from .models import db
migrate = Migrate()

# Middleware de seguridad
from .middleware.security import validate_secret_key
from .middleware.error_handlers import register_error_handlers
from .middleware.rate_limiting import create_limiter, simple_limiter, get_client_ip
from .utils.logging_config import setup_logging, log_request, security_logger

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
    
    # Validar SECRET_KEY
    if not validate_secret_key(ConfigClass.SECRET_KEY):
        raise RuntimeError("SECRET_KEY no es suficientemente segura")

    app = Flask(__name__)
    # Cargar configuración desde la clase
    app.config.from_object(ConfigClass)

    # Configurar logging
    access_logger = setup_logging(app)
    security_logger.init_app(app)
    log_request(app, access_logger)
    
    if not app.config.get('DEBUG'):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Rate limiting
    limiter = create_limiter(app)
    if limiter:
        app.limiter = limiter

    # Cache Config
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 1800
    cache.init_app(app)

    # Asignar rutas personalizadas desde la clase de configuración
    app.config['UPLOAD_FOLDER_MAQUINAS'] = ConfigClass.UPLOAD_FOLDER_MAQUINAS
    app.config['UPLOAD_FOLDER_COMPONENTES'] = ConfigClass.UPLOAD_FOLDER_COMPONENTES

    # Crear carpetas necesarias
    os.makedirs(app.config['UPLOAD_FOLDER_MAQUINAS'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_COMPONENTES'], exist_ok=True)

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
    from .routes.auth import auth_bp
    from .routes.analytics import analytics_bp
    from .routes.mantenimiento import mantenimiento_bp
    from .routes.api_mobile import api_mobile_bp
    from .routes.notifications import notifications_bp
    from .routes.reports import reports_bp

    from .routes.routes import main as main_bp
    app.register_blueprint(main_bp)

    app.register_blueprint(clima_bp)
    app.register_blueprint(maquinas_bp)
    app.register_blueprint(componentes_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(estadisticas_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(mantenimiento_bp)
    app.register_blueprint(api_mobile_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(reports_bp)

    # Middleware de rate limiting simple
    @app.before_request
    def rate_limit_check():
        # Excluir archivos estáticos y favicon del rate limiting
        if (request.path.startswith('/static/') or 
            request.path.startswith('/favicon.ico') or
            request.path.startswith('/.well-known/') or
            app.config.get('TESTING')):
            return None
            
        client_ip = get_client_ip()
        if not simple_limiter.is_allowed(client_ip):
            security_logger.log_rate_limit_exceeded(client_ip)
            return jsonify({
                    'status': 'error',
                    'message': 'Demasiadas peticiones. Intente más tarde.',
                    'error_code': 429
                }), 429

    # Funciones de ruta generales
    @app.route('/')
    def index():
        return render_template('index.html')  # Template tradicional

    @app.route('/vite')
    def vite_app():
        return render_template('vite.html')  # React app
    
    app.jinja_env.globals['vite_asset'] = vite_asset

    # Registrar manejadores de errores seguros
    register_error_handlers(app)
    
    return app
