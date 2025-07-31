"""
Aplicación Flask para Sistema de Gestión Agrícola
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

from extensions import db, migrate, init_app

def create_app(config_name=None):
    """Factory function para crear la aplicación Flask"""
    
    # Crear instancia de Flask
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static')
    
    # Configurar la aplicación
    from config import config
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensiones
    init_app(app)
    
    # Configurar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Importar modelos (importante para las migraciones)
    import models
    
    # Registrar blueprints
    from api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Configurar manejo de errores
    configure_error_handlers(app)
    
    # Configurar rutas de salud
    configure_health_routes(app)
    
    # Crear tablas si no existen (solo en desarrollo)
    if config_name == 'development':
        with app.app_context():
            db.create_all()
    
    return app

def configure_error_handlers(app):
    """Configurar manejadores de errores globales"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Solicitud incorrecta'}), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Acceso denegado'}), 403

def configure_health_routes(app):
    """Configurar rutas de salud y monitoreo"""
    
    @app.route('/health')
    def health_check():
        """Endpoint de verificación de salud"""
        try:
            # Verificar conexión a base de datos
            db.session.execute(db.text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'environment': app.config.get('FLASK_ENV', 'unknown'),
            'version': '1.0.0'
        })
    
    @app.route('/api/test')
    def api_test():
        """Endpoint de prueba de API"""
        from datetime import datetime
        return jsonify({
            'message': 'API funcionando correctamente',
            'timestamp': datetime.now().isoformat(),
            'environment': app.config.get('FLASK_ENV'),
            'status': 'success'
        })
    
    @app.route('/')
    def index():
        """Página principal del backend"""
        from flask import request
        
        # Debug: imprimir headers
        print(f"DEBUG: Accept header: {request.headers.get('Accept', 'None')}")
        print(f"DEBUG: All headers: {dict(request.headers)}")
        print(f"DEBUG: URL args: {dict(request.args)}")
        
        # Si es una petición AJAX o API específicamente, devolver JSON
        accept_header = request.headers.get('Accept', '')
        is_json_request = (
            request.args.get('format') == 'json' or
            'application/json' in accept_header and 'text/html' not in accept_header or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        )
        
        print(f"DEBUG: is_json_request: {is_json_request}")
        
        if is_json_request:
            return jsonify({
                'name': 'Sistema de Gestión Agrícola - Backend',
                'version': '2.0.0',
                'status': 'running',
                'endpoints': {
                    'health': '/health',
                    'api_test': '/api/test',
                    'components': '/api/v1/componentes',
                    'machines': '/api/v1/maquinas',
                    'suppliers': '/api/v1/proveedores',
                    'purchases': '/api/v1/compras',
                    'stock': '/api/v1/stock',
                    'dashboard': '/api/v1/estadisticas/dashboard'
                },
                'documentation': 'Ver BACKEND_REIMPLEMENTADO.md para documentación completa'
            })
        
        # Para navegadores, devolver HTML
        html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sistema de Gestión Agrícola - Backend</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c5530; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
                .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .endpoints { background: #f8f9fa; padding: 20px; border-radius: 5px; }
                .endpoint { margin: 8px 0; }
                .endpoint a { color: #2c5530; text-decoration: none; font-family: monospace; }
                .endpoint a:hover { text-decoration: underline; }
                .badge { background: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌾 Sistema de Gestión Agrícola</h1>
                <div class="status">
                    <strong>Estado:</strong> <span class="badge">FUNCIONANDO</span><br>
                    <strong>Versión:</strong> 2.0.0<br>
                    <strong>Entorno:</strong> """ + app.config.get('FLASK_ENV', 'unknown') + """
                </div>
                
                <h2>📋 Endpoints Disponibles</h2>
                <div class="endpoints">
                    <div class="endpoint">🔍 <a href="/health">Health Check</a> - Estado del sistema</div>
                    <div class="endpoint">🧪 <a href="/api/test">API Test</a> - Prueba de conectividad</div>
                    <div class="endpoint">🔧 <a href="/api/v1/componentes">Componentes</a> - Gestión de repuestos</div>
                    <div class="endpoint">🚜 <a href="/api/v1/maquinas">Máquinas</a> - Equipos agrícolas</div>
                    <div class="endpoint">🏢 <a href="/api/v1/proveedores">Proveedores</a> - Gestión de proveedores</div>
                    <div class="endpoint">🛒 <a href="/api/v1/compras">Compras</a> - Órdenes de compra</div>
                    <div class="endpoint">📦 <a href="/api/v1/stock">Stock</a> - Inventario y movimientos</div>
                    <div class="endpoint">📊 <a href="/api/v1/estadisticas/dashboard">Dashboard</a> - Estadísticas principales</div>
                </div>
                
                <h2>📚 Documentación</h2>
                <p>Para documentación completa, consulta el archivo <code>BACKEND_REIMPLEMENTADO.md</code> en el repositorio.</p>
                
                <div class="footer">
                    <p>Backend reimplementado con Flask • Base de datos: PostgreSQL • CORS habilitado</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    @app.route('/favicon.ico')
    def favicon():
        """Servir favicon"""
        from flask import send_from_directory
        import os
        
        # Buscar favicon en static
        static_dir = os.path.join(app.root_path, 'static')
        
        # Intentar primero el SVG
        favicon_svg = os.path.join(static_dir, 'favicon.svg')
        if os.path.exists(favicon_svg):
            return send_from_directory(static_dir, 'favicon.svg', mimetype='image/svg+xml')
        
        # Luego buscar ICO
        favicon_ico = os.path.join(static_dir, 'favicon.ico')
        if os.path.exists(favicon_ico):
            return send_from_directory(static_dir, 'favicon.ico')
        else:
            # Devolver un 204 No Content si no hay favicon
            from flask import Response
            return Response(status=204)
    
    @app.route('/static/<path:filename>')
    def serve_static_files(filename):
        """Servir archivos estáticos"""
        from flask import send_from_directory
        import os
        
        static_dir = os.path.join(app.root_path, 'static')
        try:
            return send_from_directory(static_dir, filename)
        except Exception:
            from flask import abort
            abort(404)
