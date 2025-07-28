from flask import Flask, send_from_directory, render_template_string
from flask_cors import CORS
from flask_migrate import Migrate
from app.utils.db import db
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de .env

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
    
    # Inicializar extensiones
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)

    # Registrar comandos CLI
    from app import commands
    commands.init_app(app)
    
    # Registrar blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Configuración híbrida de base de datos
    with app.app_context():
        setup_hybrid_database()
        
        # Importar modelos después de configurar DB
        from app.models import Componente, Maquina, Compra, Proveedor, Stock
        
        # Configurar modelos híbridos
        from app.utils.hybrid_models import setup_hybrid_models
        hybrid_results = setup_hybrid_models()
        
        print(f"🎯 Configuración híbrida completada: {len(hybrid_results)} modelos procesados")

    # Rutas de debug y health check
    setup_debug_routes(app)

    return app

def setup_hybrid_database():
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
                reflected_table = db.metadata.tables[table_name]
                print(f"✅ {table_name} reflejada correctamente")
            else:
                print(f"⚠️  {table_name} no encontrada - se creará si es necesario")
                
    except Exception as e:
        print(f"❌ Error en configuración híbrida: {e}")
        # Continuar sin reflection en caso de error

def setup_debug_routes(app):
    """Configurar rutas de debug y health check"""
    
    @app.route('/health')
    def health_check():
        """Health check para monitoreo"""
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'database': 'connected' if db.engine else 'disconnected',
            'environment': app.config.get('FLASK_ENV', 'unknown')
        }
    
    @app.route('/test')
    def test_api():
        return {'status': 'API funcionando', 'message': 'Backend conectado correctamente'}
    
    @app.route('/debug/componentes')
    def debug_componentes():
        try:
            from app.models.componente import Componente
            
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

    # ✅ AGREGAR RUTA DE DEBUG PARA VER INFO DE MODELOS
    @app.route('/debug/models')
    def debug_models():
        try:
            from app.utils.hybrid_models import get_model_info
            from app.models import Componente, Proveedor, Maquina
            
            models_info = []
            for model in [Componente, Proveedor, Maquina]:
                info = get_model_info(model)
                if info:
                    models_info.append(info)
            
            return {
                'success': True,
                'models': models_info
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # Agregar esta ruta de debug para ver qué pasó con las columnas
    @app.route('/debug/hybrid-info')
    def debug_hybrid_info():
        try:
            from app.models.componente import Componente
            
            # Ver qué columnas tiene el modelo
            model_columns = []
            if hasattr(Componente, '__table__'):
                model_columns = list(Componente.__table__.columns.keys())
            
            # Ver qué atributos tiene la clase
            class_attrs = [attr for attr in dir(Componente) if not attr.startswith('_')]
            
            # Query SQL directo para comparar
            result = db.session.execute(db.text('SELECT COUNT(*) as total FROM componentes'))
            sql_count = result.scalar()
            
            # Query SQLAlchemy
            try:
                sqlalchemy_count = Componente.query.count()
            except Exception as e:
                sqlalchemy_count = f"Error: {str(e)}"
            
            # ✅ MÁS INFO DE DEBUG
            table_info = None
            if hasattr(Componente, '__table__'):
                table_info = {
                    'name': Componente.__table__.name,
                    'columns_count': len(Componente.__table__.columns),
                    'primary_key': [col.name for col in Componente.__table__.primary_key.columns],
                    'table_type': str(type(Componente.__table__))
                }
            
            return {
                'sql_direct_count': sql_count,
                'sqlalchemy_count': sqlalchemy_count,
                'model_columns': model_columns,
                'class_attributes': class_attrs,
                'table_name': Componente.__tablename__,
                'reflected_tables': list(db.metadata.tables.keys()),
                'table_info': table_info
            }
            
        except Exception as e:
            import traceback
            return {
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    # Agregar esta ruta de debug para verificar reflection:
    @app.route('/debug/reflection')
    def debug_reflection():
        try:
            # 1. Verificar metadata
            tables_info = {}
            
            for table_name, table in db.metadata.tables.items():
                tables_info[table_name] = {
                    'columns': list(table.c.keys()),
                    'column_count': len(table.c),
                    'primary_keys': [col.name for col in table.primary_key.columns]
                }
            
            # 2. Verificar reflection directa
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            direct_columns = inspector.get_columns('componentes')
            
            # 3. ✅ QUERY SQL COMPATIBLE CON SQLITE Y POSTGRESQL
            if 'sqlite' in str(db.engine.url):
                result = db.session.execute(db.text("PRAGMA table_info(componentes)"))
                sql_columns = [row[1] for row in result]
            else:
                # ✅ POSTGRESQL
                result = db.session.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'componentes' 
                    AND table_schema = 'public'
                    ORDER BY ordinal_position
                """))
                sql_columns = [row[0] for row in result]
            
            return {
                'metadata_tables': tables_info,
                'direct_inspection': [col['name'] for col in direct_columns],
                'sql_schema_columns': sql_columns,
                'db_engine': str(db.engine.url),
                'metadata_bound': hasattr(db.metadata, 'bind') and db.metadata.bind is not None,
                'db_type': 'sqlite' if 'sqlite' in str(db.engine.url) else 'postgresql'
            }
            
        except Exception as e:
            import traceback
            return {
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    # Rutas de archivos estáticos para imágenes
    @app.route('/static/fotos/<path:filename>')
    def serve_fotos(filename):
        """Servir archivos de fotos - redirigir a componentes por defecto"""
        static_dir = os.path.join(os.path.dirname(app.root_path), 'static', 'fotos', 'componentes')
        try:
            return send_from_directory(static_dir, filename)
        except:
            # Si no existe en componentes, intentar en la raíz de fotos
            static_dir = os.path.join(os.path.dirname(app.root_path), 'static', 'fotos')
            return send_from_directory(static_dir, filename)
    
    @app.route('/static/fotos/componentes/<path:filename>')
    def serve_fotos_componentes(filename):
        """Servir archivos de fotos de componentes"""
        static_dir = os.path.join(os.path.dirname(app.root_path), 'static', 'fotos', 'componentes')
        return send_from_directory(static_dir, filename)

    # Frontend routes
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
</html>"""
    
    @app.route('/')
    @app.route('/<path:path>')
    def serve_react(path=''):
        if path.startswith('api/'):
            from flask import abort
            abort(404)
        
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return render_template_string(INDEX_HTML)

    return app