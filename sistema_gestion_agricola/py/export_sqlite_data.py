import sqlite3
import json

TABLAS = [
    "proveedores",
    "componentes",
    "componentes_proveedores",
    "compras",
    "frecuencias",
    "maquinas",
    "maquinas_componentes",
    "pagos_proveedores",
    "stock"
]

conn = sqlite3.connect("../sistema_gestion_agricola.db")
cursor = conn.cursor()

datos = {}

for tabla in TABLAS:
    cursor.execute(f"SELECT * FROM {tabla}")
    columnas = [col[0] for col in cursor.description]
    registros = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    datos[tabla] = registros

with open("backup_sqlite.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, indent=2, ensure_ascii=False)

print("✅ Datos exportados a backup_sqlite.json")
