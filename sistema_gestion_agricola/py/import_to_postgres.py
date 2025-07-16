import json
from sistema_gestion_agricola import create_app, db
from sistema_gestion_agricola.models import (
    Proveedor, Componente, ComponentesProveedores,
    Compra, Frecuencia, Maquina, MaquinaComponente,
    PagoProveedor, Stock
)

TABLAS_MODELOS = {
    "proveedores": Proveedor,
    "componentes": Componente,
    "componentes_proveedores": ComponentesProveedores,
    "compras": Compra,
    "frecuencias": Frecuencia,
    "maquinas": Maquina,
    "maquinas_componentes": MaquinaComponente,
    "pagos_proveedores": PagoProveedor,
    "stock": Stock,
}

import os
ruta = os.path.join(os.path.dirname(__file__), "backup_sqlite.json")
with open(ruta, "r", encoding="utf-8") as f:
    datos = json.load(f)

app = create_app()
with app.app_context():
    for tabla, modelo in TABLAS_MODELOS.items():
        registros = datos.get(tabla, [])
        print(f"Importando {len(registros)} registros a {tabla}...")
        for registro in registros:
            try:
                # Corrección para el modelo 'frecuencias'
                if tabla == "frecuencias":
                    if 'Unidad tiempo' in registro:
                        registro['Unidad_tiempo'] = registro.pop('Unidad tiempo')
                    if 'Criterio adicional' in registro:
                        registro['Criterio_adicional'] = registro.pop('Criterio adicional')

                obj = modelo(**registro)
                db.session.merge(obj)
            except Exception as e:
                print(f"❌ Error al importar registro en {tabla}: {e}")
        db.session.commit()
    print("✅ Todos los datos fueron importados a PostgreSQL")
