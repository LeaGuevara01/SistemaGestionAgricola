"""
🚀 Utilidades optimizadas para PostgreSQL
Incluye connection pooling, manejo de errores y optimizaciones de rendimiento
"""

from flask_sqlalchemy import SQLAlchemy
from flask import request
from sqlalchemy.exc import InternalError, OperationalError, InvalidRequestError, DisconnectionError
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import create_engine, text
from contextlib import contextmanager
import time
import logging

# Configurar logging para SQL
logging.basicConfig()
sql_logger = logging.getLogger('sqlalchemy.engine')

class OptimizedSQLAlchemy(SQLAlchemy):
    """SQLAlchemy optimizado para PostgreSQL con connection pooling"""
    
    def __init__(self, app=None, **kwargs):
        super().__init__(app, **kwargs)
        self._connection_retries = 3
        self._retry_delay = 1.0
    
    def init_app(self, app):
        super().init_app(app)
        
        # Configurar engine con pooling optimizado
        if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
            self._configure_postgresql_engine(app)
    
    def _configure_postgresql_engine(self, app):
        """Configurar engine específicamente para PostgreSQL"""
        
        # Configuración optimizada para PostgreSQL
        engine_options = {
            'poolclass': QueuePool,
            'pool_size': 10,           # Conexiones permanentes en el pool
            'max_overflow': 20,        # Conexiones adicionales bajo carga
            'pool_timeout': 30,        # Timeout para obtener conexión del pool
            'pool_recycle': 3600,      # Reciclar conexiones cada hora
            'pool_pre_ping': True,     # Verificar conexión antes de usar
            'echo': app.config.get('DEBUG', False),  # Log SQL en debug
        }
        
        # SSL para conexiones remotas
        if any(host in app.config['SQLALCHEMY_DATABASE_URI'] for host in ['render.com', 'amazonaws.com', 'heroku.com']):
            engine_options['connect_args'] = {'sslmode': 'require'}
        
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
        
        print("🐘 PostgreSQL engine configurado con connection pooling")

# Instancia global optimizada
db = OptimizedSQLAlchemy()

def commit_or_rollback():
    """Helper para hacer commit o rollback automático con reintentos"""
    for attempt in range(3):
        try:
            db.session.commit()
            return True
        except (InternalError, OperationalError) as e:
            db.session.rollback()
            if attempt < 2:
                print(f"⚠️ Error en commit (intento {attempt + 1}/3): {e}")
                time.sleep(0.5)
                continue
            else:
                print(f"❌ Error persistente en commit: {e}")
                raise e
        except Exception as e:
            db.session.rollback()
            raise e

def reset_transaction():
    """Reiniciar transacción en caso de error con logging mejorado"""
    try:
        # Log del estado actual
        print("🔄 Reseteando transacción PostgreSQL...")
        
        # Rollback de la transacción actual
        try:
            db.session.rollback()
        except Exception as e:
            print(f"⚠️ Error en rollback: {e}")
        
        # Cerrar la sesión actual
        try:
            db.session.close()
        except Exception as e:
            print(f"⚠️ Error cerrando sesión: {e}")
        
        # Remover la sesión del pool
        try:
            db.session.remove()
        except Exception as e:
            print(f"⚠️ Error removiendo sesión: {e}")
        
        # Verificar que la nueva sesión funciona
        try:
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            print("✅ Transacción reseteada exitosamente")
            return True
        except Exception as e:
            print(f"⚠️ Error verificando nueva sesión: {e}")
            # Último intento de limpieza
            try:
                db.session.close()
                db.session.remove()
            except:
                pass
            return False
    
    except Exception as e:
        print(f"❌ Error crítico reseteando transacción: {e}")
        return False

def safe_query_execute(query_func, max_retries=3):
    """Ejecutar consulta de forma segura con manejo robusto de errores"""
    
    for attempt in range(max_retries):
        try:
            # Verificar estado de conexión antes de ejecutar
            if not check_transaction_state():
                reset_transaction()
            
            result = query_func()
            return result
            
        except (InternalError, DisconnectionError) as e:
            error_msg = str(e).lower()
            
            if 'current transaction is aborted' in error_msg:
                print(f"🔄 Transacción abortada, reseteando (intento {attempt + 1}/{max_retries})")
                reset_transaction()
                
                if attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))  # Backoff exponencial
                    continue
                else:
                    print("❌ Error persistente después de múltiples intentos")
                    raise e
            else:
                print(f"❌ Error de conexión: {e}")
                reset_transaction()
                raise e
                
        except OperationalError as e:
            print(f"❌ Error operacional en base de datos (intento {attempt + 1}/{max_retries}): {e}")
            reset_transaction()
            
            if attempt < max_retries - 1:
                time.sleep(1.0 * (attempt + 1))
                continue
            else:
                raise e
                
        except Exception as e:
            print(f"❌ Error inesperado en consulta: {e}")
            reset_transaction()
            raise e
    
    raise Exception("No se pudo ejecutar la consulta después de múltiples intentos")

def check_transaction_state():
    """Verificar el estado de la transacción actual de forma robusta"""
    try:
        # Test simple y rápido
        result = db.session.execute(text("SELECT 1"))
        result.close()
        return True
    except (InternalError, OperationalError, InvalidRequestError) as e:
        error_msg = str(e).lower()
        if 'current transaction is aborted' in error_msg:
            print("⚠️ Transacción en estado abortado detectada")
            return False
        else:
            print(f"⚠️ Error verificando transacción: {e}")
            return False
    except Exception as e:
        print(f"⚠️ Error inesperado verificando transacción: {e}")
        return False

@contextmanager
def database_transaction():
    """Context manager para manejar transacciones de forma segura"""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en transacción, rollback ejecutado: {e}")
        raise
    finally:
        db.session.close()

def get_connection_info():
    """Obtener información sobre el estado de las conexiones"""
    try:
        if hasattr(db.engine.pool, 'status'):
            pool_status = db.engine.pool.status()
            return {
                'pool_size': db.engine.pool.size(),
                'checked_in': pool_status.split(' ')[2],
                'checked_out': pool_status.split(' ')[5],
                'overflow': pool_status.split(' ')[8] if 'Overflow' in pool_status else '0',
                'invalid': pool_status.split(' ')[-1] if 'Invalid' in pool_status else '0'
            }
        else:
            return {'status': 'Pool info not available'}
    except Exception as e:
        return {'error': str(e)}

def optimize_query_performance():
    """Configurar optimizaciones de rendimiento para PostgreSQL"""
    optimizations = [
        "SET work_mem = '256MB'",
        "SET maintenance_work_mem = '512MB'", 
        "SET effective_cache_size = '1GB'",
        "SET random_page_cost = 1.1",
        "SET seq_page_cost = 1.0"
    ]
    
    for opt in optimizations:
        try:
            db.session.execute(text(opt))
            print(f"✅ Optimización aplicada: {opt}")
        except Exception as e:
            print(f"⚠️ No se pudo aplicar optimización: {opt} - {e}")
    
    try:
        db.session.commit()
        print("✅ Optimizaciones de rendimiento aplicadas")
    except Exception as e:
        print(f"⚠️ Error aplicando optimizaciones: {e}")
        db.session.rollback()

# Función para logs de rendimiento
def log_slow_queries(app):
    """Configurar logging para queries lentas"""
    
    @app.before_request
    def start_timer():
        app.start_time = time.time()
    
    @app.after_request
    def log_request(response):
        if hasattr(app, 'start_time'):
            duration = time.time() - app.start_time
            if duration > 1.0:  # Log requests que tomen más de 1 segundo
                print(f"🐌 Query lenta detectada: {duration:.2f}s en {request.endpoint}")
        return response
