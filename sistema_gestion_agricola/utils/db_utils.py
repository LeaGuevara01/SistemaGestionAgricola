# utils/db_utils.py
from sistema_gestion_agricola import create_app
from sistema_gestion_agricola.models import db
from sqlalchemy import text 

def sincronizar_secuencia():
    sql = """
    SELECT setval(pg_get_serial_sequence('componentes_proveedores', 'ID'), 
                  (SELECT MAX("ID") FROM componentes_proveedores));
    """
    try:
        db.session.execute(text(sql))
        db.session.commit()
        print("Secuencia sincronizada correctamente.")
    except Exception as e:
        db.session.rollback()
        print(f"Error al sincronizar secuencia: {e}")

if __name__ == '__main__':
    app = create_app()  # Crea la instancia de Flask
    with app.app_context():  # Activá el contexto de app
        sincronizar_secuencia()