# __init__.py

import os
from flask import Flask, render_template, make_response
from flask_caching import Cache
from dotenv import load_dotenv
from .utils.vite_helper import vite_asset
import pdfkit

# Cargar variables de entorno
load_dotenv()

cache = Cache()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "elorza")

    # Weather Config
    app.config['WEATHER_API_KEY'] = os.getenv('WEATHER_API_KEY')
    app.config['WEATHER_API_URL'] = "https://api.openweathermap.org/data/2.5/weather"
    app.config['COORDENADAS_UCACHA'] = {
        'lat': "-33.0320",
        'lon': "-63.5066"
    }

    # Cache Config
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 1800
    cache.init_app(app)

    # Folders Config
    app.config['UPLOAD_FOLDER_MAQUINAS'] = os.path.join(app.root_path, 'static/fotos/maquinas')
    app.config['UPLOAD_FOLDER_COMPONENTES'] = os.path.join(app.root_path, 'static/fotos/componentes')

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

    @app.route('/vite')
    def vite_app():
        return render_template('vite.html')  # plantilla que solo tiene <div id="app"></div> y carga Vite

    # Home Page
    @app.route('/')
    def index():
        conn = get_db_connection()
        maquinas = conn.execute('SELECT * FROM maquinas').fetchall()
        conn.close()
        return render_template('index.html', maquinas=maquinas)

    # PDF Export
    @app.route('/resumen_cuentas/pdf')
    def exportar_resumen_pdf():
        conn = get_db_connection()
        resumen = conn.execute('''
            SELECT p.ID, p.Nombre,
                IFNULL(SUM(c.Cantidad * c.Precio_Unitario), 0) AS Total_Compras,
                IFNULL(SUM(pg.Monto), 0) AS Total_Pagos,
                (IFNULL(SUM(c.Cantidad * c.Precio_Unitario), 0) - IFNULL(SUM(pg.Monto), 0)) AS Saldo
            FROM proveedores p
            LEFT JOIN compras c ON p.ID = c.ID_Proveedor
            LEFT JOIN pagos_proveedores pg ON p.ID = pg.ID_Proveedor
            GROUP BY p.ID
        ''').fetchall()
        conn.close()

        rendered = render_template('pagos/resumen_pdf.html', resumen=resumen)

        # Si wkhtmltopdf no está en PATH, especificá la ruta
        try:
            config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
            pdf = pdfkit.from_string(rendered, False, configuration=config)
        except OSError:
            # Fallback for other OS
            pdf = pdfkit.from_string(rendered, False)


        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=resumen_cuentas.pdf'
        return response
    
    from sistema_gestion_agricola.utils.db import get_db_connection
    from sistema_gestion_agricola.utils.vite_helper import vite_asset
    app.jinja_env.globals['vite_asset'] = vite_asset

    return app
