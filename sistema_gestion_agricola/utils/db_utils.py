# utils/db_utils.py
from sistema_gestion_agricola import create_app
from sistema_gestion_agricola.models import db
from sqlalchemy import text 

def sincronizar_secuencia():
    """Sincroniza la secuencia de PostgreSQL de forma segura"""
    try:
        # Usar parámetros para evitar inyección SQL
        result = db.session.execute(text(
            "SELECT setval(pg_get_serial_sequence('componentes_proveedores', 'ID'), "
            "(SELECT COALESCE(MAX(\"ID\"), 1) FROM componentes_proveedores));"
        ))
        db.session.commit()
        print("Secuencia sincronizada correctamente.")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al sincronizar secuencia: {e}")
        return False

def verificar_integridad_db():
    """Verifica la integridad básica de la base de datos"""
    try:
        # Verificar conexión
        db.session.execute(text("SELECT 1"))
        
        # Verificar tablas principales
        tablas = ['proveedores', 'componentes', 'maquinas', 'stock']
        for tabla in tablas:
            count = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
            print(f"Tabla {tabla}: {count} registros")
        
        return True
    except Exception as e:
        print(f"Error al verificar integridad: {e}")
        return False

if __name__ == '__main__':
    app = create_app()  # Crea la instancia de Flask
    with app.app_context():  # Activá el contexto de app
        sincronizar_secuencia()