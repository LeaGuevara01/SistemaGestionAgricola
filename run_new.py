"""
Punto de entrada principal para el Sistema de Gestión Agrícola
Versión reimplementada - 2025
"""
import os
from backend_new.app import create_app

# Crear aplicación
app = create_app()

if __name__ == '__main__':
    # Obtener configuración del entorno
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("🚀 SISTEMA DE GESTIÓN AGRÍCOLA - BACKEND REIMPLEMENTADO")
    print("=" * 60)
    print(f"🌐 Host: {host}")
    print(f"🔌 Puerto: {port}")
    print(f"🔧 Debug: {debug}")
    print(f"📊 Entorno: {app.config.get('FLASK_ENV', 'unknown')}")
    print(f"💾 Base de datos: {'PostgreSQL' if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'}")
    print("=" * 60)
    print("📋 Endpoints disponibles:")
    print("  • GET  /health - Health check")
    print("  • GET  /api/test - Test de API")
    print("  • GET  /api/v1/componentes - Gestión de componentes")
    print("  • GET  /api/v1/maquinas - Gestión de máquinas")
    print("  • GET  /api/v1/proveedores - Gestión de proveedores")
    print("  • GET  /api/v1/compras - Gestión de compras")
    print("  • GET  /api/v1/stock - Gestión de stock")
    print("  • GET  /api/v1/estadisticas/dashboard - Dashboard principal")
    print("=" * 60)
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}")
