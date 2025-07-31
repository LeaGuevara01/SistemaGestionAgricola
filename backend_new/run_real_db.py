"""
Aplicación Flask simplificada que usa el schema real de la base de datos
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

from extensions import init_app
from api_real import api_real_bp

def create_app_real():
    """Factory para crear la aplicación Flask con modelos reales"""
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://elorza:g65hHAdGLwoOYl33zlPRnVyzdsY6FsD1@dpg-d1qpnlodl3ps73eln790-a.oregon-postgres.render.com/sistema_gestion_agricola')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-real-db')
    
    # Inicializar extensiones
    init_app(app)
    
    # Configurar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Registrar blueprint
    app.register_blueprint(api_real_bp, url_prefix='/api/v1')
    
    # Rutas básicas
    @app.route('/')
    def home():
        return jsonify({
            'message': 'Sistema de Gestión Agrícola - Backend Real DB',
            'version': '1.0.0',
            'database': 'PostgreSQL Real Schema'
        })
    
    @app.route('/health')
    def health():
        try:
            # Probar conexión a BD
            from extensions import db
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'version': '1.0.0',
            'environment': os.getenv('FLASK_ENV', 'development')
        })
    
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(app.static_folder or 'static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
    return app

if __name__ == '__main__':
    app = create_app_real()
    print("🌾 Sistema de Gestión Agrícola - Backend Real DB")
    print("="*60)
    print("🚀 Servidor iniciado en http://127.0.0.1:5001")
    print("📊 APIs disponibles:")
    print("   - GET /api/v1/componentes")
    print("   - GET /api/v1/proveedores") 
    print("   - GET /api/v1/maquinas")
    print("   - GET /api/v1/compras")
    print("   - GET /api/v1/stock")
    print("   - GET /api/v1/estadisticas/dashboard")
    print("✅ Health check: http://127.0.0.1:5001/health")
    
    app.run(host='127.0.0.1', port=5001, debug=False)
