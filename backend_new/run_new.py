#!/usr/bin/env python3
"""
Sistema de Gestión Agrícola - Backend Reimplementado
Archivo principal de ejecución
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def main():
    """Función principal"""
    print("🌾 Iniciando Sistema de Gestión Agrícola - Backend v2.0")
    print("=" * 60)
    
    # Crear la aplicación
    app = create_app()
    
    # Configuración del servidor
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"🔧 Configuración:")
    print(f"   - Host: {host}")
    print(f"   - Puerto: {port}")
    print(f"   - Debug: {debug}")
    print(f"   - Entorno: {app.config.get('FLASK_ENV', 'unknown')}")
    print(f"   - Base de datos: {app.config.get('SQLALCHEMY_DATABASE_URI', 'unknown')}")
    
    print("\n🚀 Iniciando servidor...")
    print(f"   - URL principal: http://{host}:{port}/")
    print(f"   - Health check: http://{host}:{port}/health")
    print(f"   - API components: http://{host}:{port}/api/v1/componentes")
    
    print("\n📝 Logs del servidor:")
    print("-" * 40)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # Evitar problemas con imports
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
