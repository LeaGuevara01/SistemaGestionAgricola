from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import InternalError, OperationalError, InvalidRequestError
import time

db = SQLAlchemy()

def commit_or_rollback():
    """Commit con manejo de errores mejorado"""
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Error en commit: {e}")
        raise e

def reset_transaction():
    """Reiniciar transacción PostgreSQL"""
    try:
        print("🔄 Reseteando transacción PostgreSQL...")
        db.session.rollback()
        db.session.close()
        db.session.remove()
        
        # Verificar nueva sesión
        db.session.execute(db.text("SELECT 1"))
        db.session.commit()
        print("✅ Transacción reseteada")
        return True
    except Exception as e:
        print(f"❌ Error reseteando: {e}")
        try:
            db.session.close()
            db.session.remove()
        except:
            pass
        return False

def safe_query_execute(query_func):
    """Ejecutar query con reintentos"""
    for attempt in range(3):
        try:
            return query_func()
        except (InternalError, OperationalError) as e:
            if 'current transaction is aborted' in str(e):
                print(f"🔄 Transacción abortada, reintentando ({attempt + 1}/3)")
                reset_transaction()
                if attempt < 2:
                    time.sleep(0.5)
                    continue
            raise e

def check_transaction_state():
    """Verificar estado de transacción"""
    try:
        db.session.execute(db.text("SELECT 1"))
        return True
    except Exception:
        return False
