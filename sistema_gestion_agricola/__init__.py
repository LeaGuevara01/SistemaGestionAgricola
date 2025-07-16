# __init__.py
import os
from flask import Flask, render_template, make_response

# Helper para Render
import pdfkit
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
    
    app = Flask(__name__)

    app.config.from_object('config')

    # Migrate Config
    db.init_app(app)
    migrate.init_app(app, db)

    # Cache Config
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 1800
    cache.init_app(app)

    # Folders Config
    app.config['UPLOAD_FOLDER_MAQUINAS'] = os.path.join(app.root_path, 'static/fotos/maquinas')
    app.config['UPLOAD_FOLDER_COMPONENTES'] = os.path.join(app.root_path, 'static/fotos/componentes')

    # Weather Config
    app.config['WEATHER_API_URL'] = "https://api.openweathermap.org/data/2.5/weather"
    app.config['COORDENADAS_UCACHA'] = {
        'lat': "-33.0320",
        'lon': "-63.5066"
    }
    
    # Blueprints Registration
    from .routes.clima import clima_bp
    from .routes.maquinas import maquinas_bp
    from .routes.componentes import componentes_bp
    from .routes.stock import stock_bp
    from .routes.compras import compras_bp
    from .routes.pagos import pagos_bp
    from .routes.proveedores import proveedores_bp
    from .routes.estadisticas import estadisticas_bp

    app.register_blueprint(clima_bp)
    app.register_blueprint(maquinas_bp)
    app.register_blueprint(componentes_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(estadisticas_bp)

    from .utils.db import get_db_connection

    # Home Page
    @app.route('/')
    def index():
        return render_template('index.html')

    # PDF Export
    from sqlalchemy.sql import text
    from .models import db

    @app.route('/resumen_cuentas/pdf')
    def exportar_resumen_pdf():
        resumen = db.session.execute(text('''
            SELECT p.ID, p.Nombre,
                COALESCE(SUM(c.Cantidad * c.Precio_Unitario), 0) AS Total_Compras,
                COALESCE(SUM(pg.Monto), 0) AS Total_Pagos,
                (COALESCE(SUM(c.Cantidad * c.Precio_Unitario), 0) - COALESCE(SUM(pg.Monto), 0)) AS Saldo
            FROM proveedores p
            LEFT JOIN compras c ON p.ID = c.ID_Proveedor
            LEFT JOIN pagos_proveedores pg ON p.ID = pg.ID_Proveedor
            GROUP BY p.ID
        ''')).fetchall()

        rendered = render_template('pagos/resumen_pdf.html', resumen=resumen)

        try:
            config = pdfkit.configuration(wkhtmltopdf=os.getenv("WKHTMLTOPDF_BIN"))
            pdf = pdfkit.from_string(rendered, False, configuration=config)
        except OSError:
            pdf = pdfkit.from_string(rendered, False)

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=resumen_cuentas.pdf'
        return response

    @app.route('/vite')
    def vite_app():
        return render_template('vite.html')  # plantilla que solo tiene <div id="app"></div> y carga Vite

    app.jinja_env.globals['vite_asset'] = vite_asset

    return app