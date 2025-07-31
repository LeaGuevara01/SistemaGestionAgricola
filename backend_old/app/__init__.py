from flask import Flask, send_from_directory, render_template_string, jsonify, request
from flask_migrate import Migrate
from .utils.db import db
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='../../frontend/dist')
    
    # Usar configuración centralizada
    env = os.getenv('FLASK_ENV', 'development')
    
    # Importar configuración desde config.py raíz
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    from config import config
    
    config_class = config.get(env, config['default'])
    app.config.from_object(config_class)
    
    # CONFIGURAR LOGGING ESTRUCTURADO
    try:
        from .utils.logging_config import configure_logging
        app.logger = configure_logging(app)
        app.logger.info("Logging estructurado configurado correctamente")
    except ImportError as e:
        print(f"⚠️ Error configurando logging: {e}")
    
    # Inicializar extensiones
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # CONFIGURAR CORS PROFESIONAL
    try:
        from .utils.cors_config import configure_cors
        cors = configure_cors(app)
        app.logger.info("CORS configurado correctamente")
    except ImportError as e:
        print(f"⚠️ Error configurando CORS: {e}")
        # Fallback a CORS básico
        from flask_cors import CORS
        CORS(app)
    
    # CONFIGURAR RATE LIMITING
    try:
        from .utils.rate_limiting import configure_rate_limiting
        limiter = configure_rate_limiting(app)
        app.limiter = limiter
        app.logger.info("Rate limiting configurado correctamente")
    except ImportError as e:
        if hasattr(app, 'logger'):
            app.logger.warning(f"Rate limiting no disponible: {e}")
        else:
            print(f"⚠️ Rate limiting no disponible: {e}")
        app.limiter = None
    
    # REGISTRAR MANEJADORES DE ERRORES
    try:
        from .utils.error_handlers import register_error_handlers
        register_error_handlers(app)
        if hasattr(app, 'logger'):
            app.logger.info("Manejadores de errores registrados")
    except ImportError as e:
        if hasattr(app, 'logger'):
            app.logger.warning(f"Error registrando manejadores de errores: {e}")
        else:
            print(f"⚠️ Error registrando manejadores de errores: {e}")
    
    # REGISTRAR MIDDLEWARE PARA MANEJAR TRANSACCIONES
    @app.before_request
    def check_database_state():
        """Verificar el estado de la base de datos antes de cada request"""
        from .utils.db import check_transaction_state, reset_transaction
        
        # Solo verificar en endpoints API, no en archivos estáticos
        if request.path.startswith('/api/'):
            try:
                if not check_transaction_state():
                    reset_transaction()
            except Exception as e:
                print(f"⚠️ Error verificando estado de transacción: {e}")
                reset_transaction()
    
    @app.after_request
    def cleanup_database_session(response):
        """Limpiar sesión de base de datos después de cada request"""
        from .utils.db import db
        
        try:
            # Solo hacer commit si la respuesta es exitosa
            if response.status_code < 400:
                db.session.commit()
            else:
                db.session.rollback()
        except Exception as e:
            print(f"⚠️ Error en cleanup de sesión: {e}")
            db.session.rollback()
        finally:
            db.session.remove()
        
        return response

    # CORREGIR IMPORTACIONES DE COMANDOS Y RUTAS
    try:
        from .commands import init_app as init_commands
        init_commands(app)
        if hasattr(app, 'logger'):
            app.logger.info("Comandos CLI inicializados")
    except ImportError:
        if hasattr(app, 'logger'):
            app.logger.warning("No se encontraron comandos CLI")
        else:
            print("⚠️ No se encontraron comandos CLI")
    
    # Registrar blueprints
    try:
        from .routes.api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api/v1')
        if hasattr(app, 'logger'):
            app.logger.info("Rutas API registradas correctamente")
            

    except ImportError:
        if hasattr(app, 'logger'):
            app.logger.warning("No se encontraron rutas API")
        else:
            print("⚠️ No se encontraron rutas API")
    
    # Configuración híbrida de base de datos
    with app.app_context():
        setup_hybrid_database(app)
        
        # CORREGIR IMPORTACIONES RELATIVAS
        try:
            from .models import Componente, Maquina, Compra, Proveedor, Stock
            if hasattr(app, 'logger'):
                app.logger.info("Modelos importados correctamente")
            else:
                print("✅ Modelos importados correctamente")
        except ImportError as e:
            if hasattr(app, 'logger'):
                app.logger.error(f"Error importando modelos: {e}")
            else:
                print(f"⚠️ Error importando modelos: {e}")
    
    # ENDPOINT DE HEALTH CHECK
    @app.route('/health')
    def health_check():
        """Endpoint de health check con información del sistema"""
        return jsonify({
            'status': 'healthy',
            'environment': env,
            'features': {
                'cors': True,
                'rate_limiting': hasattr(app, 'limiter') and app.limiter is not None,
                'structured_logging': True
            }
        })
    
    # Configurar rutas adicionales
    setup_debug_routes(app)
    
    if hasattr(app, 'logger'):
        app.logger.info(f"Aplicación inicializada correctamente en ambiente: {env}")
    else:
        print(f"✅ Aplicación inicializada correctamente en ambiente: {env}")
    
    return app

def setup_hybrid_database(app):
    """Configurar base de datos con reflection híbrida"""
    from sqlalchemy import inspect
    
    try:
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        print(f"📋 Tablas encontradas en BD: {table_names}")
        
        # Reflejar cada tabla individualmente
        for table_name in table_names:
            try:
                columns = inspector.get_columns(table_name)
                print(f"🔍 {table_name}: {len(columns)} columnas")
            except Exception as e:
                print(f"❌ Error inspeccionando {table_name}: {e}")
        
        # Hacer reflection completa
        db.reflect()
        
        # Verificar tablas críticas
        critical_tables = ['componentes', 'proveedores', 'maquinas', 'compras', 'stock']
        for table_name in critical_tables:
            if table_name in db.metadata.tables:
                print(f"✅ {table_name} reflejada correctamente")
            else:
                print(f"⚠️  {table_name} no encontrada - se creará si es necesario")
                
    except Exception as e:
        print(f"❌ Error en configuración híbrida: {e}")

def setup_debug_routes(app):
    """Configurar rutas de debug y health check"""
    
    @app.route('/test')
    def test_api():
        return {'status': 'API funcionando', 'message': 'Backend conectado correctamente'}
    
    @app.route('/debug/componentes')
    def debug_componentes():
        try:
            from .models.componente import Componente
            
            total = Componente.query.count()
            componentes = Componente.query.limit(3).all()
            
            table_columns = list(Componente.__table__.columns.keys()) if hasattr(Componente, '__table__') else []
            
            return {
                'success': True,
                'message': f'Debug: {total} componentes encontrados',
                'data': [comp.to_dict() for comp in componentes],
                'table_columns': table_columns,
                'database_type': 'PostgreSQL' if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
            }
        except Exception as e:
            import traceback
            return {
                'success': False, 
                'error': str(e), 
                'traceback': traceback.format_exc()
            }

    # CONFIGURAR RUTAS ESTÁTICAS PARA FRONTEND
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        """Servir archivos de assets del frontend con MIME types correctos"""
        try:
            response = send_from_directory(app.static_folder, f'assets/{filename}')
            
            if filename.endswith('.js'):
                response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
                response.headers['Cache-Control'] = 'public, max-age=31536000'
            elif filename.endswith('.css'):
                response.headers['Content-Type'] = 'text/css; charset=utf-8'
                response.headers['Cache-Control'] = 'public, max-age=31536000'
            elif filename.endswith('.map'):
                response.headers['Content-Type'] = 'application/json'
                
            return response
            
        except Exception as e:
            print(f"❌ Error sirviendo asset {filename}: {e}")
            from flask import abort
            abort(404)

    # Frontend routes
    @app.route('/')
    @app.route('/<path:path>')
    def serve_react(path=''):
        # No servir React para rutas de API
        if path.startswith('api/'):
            from flask import abort
            abort(404)
        
        if path and not path.startswith('assets/') and os.path.exists(os.path.join(app.static_folder, path)):
            try:
                response = send_from_directory(app.static_folder, path)
                
                if path.endswith('.js'):
                    response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
                elif path.endswith('.css'):
                    response.headers['Content-Type'] = 'text/css; charset=utf-8'
                elif path.endswith('.map'):
                    response.headers['Content-Type'] = 'application/json'
                    
                return response
            except Exception as e:
                print(f"❌ Error sirviendo archivo estático {path}: {e}")
        
        try:
            response = send_from_directory(app.static_folder, 'index.html')
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            return response
        except Exception as e:
            print(f"❌ Error sirviendo index.html: {e}")
            
            INDEX_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Gestión Agrícola - Elorza</title>
    <script type="module" crossorigin src="/assets/index.js"></script>
    <link rel="stylesheet" href="/assets/index.css">
</head>
<body>
    <div id="root"></div>
</body>
</html>"""
            return render_template_string(INDEX_HTML)