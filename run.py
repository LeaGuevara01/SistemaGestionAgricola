# run.py - Punto de entrada principal consolidado
import os
from config import config, Config

# Determinar el entorno
env = os.getenv('FLASK_ENV', 'development')
if env not in config:
    env = 'default'

# Verificar configuración antes de iniciar
config_class = config[env]
config_class.check_env_vars()

# Crear aplicación
if os.path.exists('backend'):
    # Si existe directorio backend, usar esa estructura
    from backend.app import create_app
    app = create_app()
    app.config.from_object(config_class)
else:
    # Usar estructura anterior como fallback
    from sistema_gestion_agricola import create_app
    app = create_app()
    app.config.from_object(config_class)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando aplicación en puerto {port}")
    print(f"🔧 Entorno: {env}")
    print(f"💾 Base de datos: {'PostgreSQL' if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'}")
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])