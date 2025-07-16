# utils/db.py
import sqlite3
import os

def get_db_connection():
    db_url = os.getenv('DATABASE_URL', '')

    if db_url.startswith('sqlite:///'):
        # Uso local con SQLite
        path = db_url.replace('sqlite:///', '')
        conn = sqlite3.connect(path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    elif db_url.startswith('postgres://') or db_url.startswith('postgresql://'):
        # Producción: debe usarse SQLAlchemy, no sqlite3
        raise RuntimeError("En producción se debe usar SQLAlchemy, no sqlite3.connect()")

    else:
        raise RuntimeError("DATABASE_URL no configurada o formato no válido.")
