# utils/db.py
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('sistema_gestion_agricola.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn