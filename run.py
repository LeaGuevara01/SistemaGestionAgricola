# run.py - Punto de entrada principal consolidado
import os
import sys
from config import config

# AGREGAR LOGGING PARA DEBUG
print(f"🔍 Python path: {sys.path}")
print(f"🔍 Current directory: {os.getcwd()}")
print(f"🔍 Files in current dir: {os.listdir('.')}")

env = os.getenv('FLASK_ENV', 'development')
print(f"🔍 Environment: {env}")

# Determinar el entorno
if env not in config:
    env = 'default'

# Verificar configuración antes de iniciar
config_class = config[env]
config_class.check_env_vars()

# SIMPLIFICAR LA LÓGICA DE IMPORTACIÓN PARA DEPLOYMENT
app = None

# Para Render y producción, usar el backend principal directamente
try:
    # Primero intentar importar desde backend/app.py (backend principal)
    sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
    from app import app as flask_app
    app = flask_app
    print("✅ Backend principal import successful")
except ImportError as e:
    print(f"❌ Backend principal import failed: {e}")
    
    # Si falla, intentar con la estructura modular
    try:
        from backend.app import create_app
        app = create_app(env)
        print("✅ Backend modular import successful")
    except ImportError as e2:
        print(f"❌ Backend modular import failed: {e2}")
        
        # Último recurso: usar backend_new
        try:
            sys.path.insert(0, os.path.join(os.getcwd(), 'backend_new'))
            from app import create_app
            app = create_app(env)
            print("✅ Backend new import successful")
        except ImportError as e3:
            print(f"❌ All backend imports failed. Last error: {e3}")
            sys.exit(1)

if app is None:
    print("❌ No se pudo crear la aplicación")
    sys.exit(1)

# Configurar la aplicación con la configuración correcta
app.config.from_object(config_class)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando aplicación en puerto {port}")
    print(f"🔧 Entorno: {env}")
    print(f"💾 Base de datos: {'PostgreSQL' if app.config.get('SQLALCHEMY_DATABASE_URI') and 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'Mock/SQLite'}")
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))