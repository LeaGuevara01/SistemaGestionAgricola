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

# SIMPLIFICAR LA LÓGICA DE IMPORTACIÓN
try:
    from backend.app import create_app
    print("✅ Backend import successful")
except ImportError as e:
    print(f"❌ Backend import failed: {e}")
    sys.exit(1)

try:
    app = create_app()
    print("✅ App creation successful")
except Exception as e:
    print(f"❌ App creation failed: {e}")
    sys.exit(1)

app.config.from_object(config_class)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando aplicación en puerto {port}")
    print(f"🔧 Entorno: {env}")
    print(f"💾 Base de datos: {'PostgreSQL' if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'}")
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])