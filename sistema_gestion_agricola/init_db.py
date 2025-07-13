import sqlite3

def create_tables():
    conn = sqlite3.connect('sistema_gestion_agricola.db')
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS maquinas (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Codigo TEXT UNIQUE NOT NULL,
        Nombre TEXT NOT NULL,
        Marca TEXT,
        Modelo TEXT,
        Año INTEGER,
        Estado TEXT,
        Observaciones TEXT,
        Foto TEXT
    );

    CREATE TABLE IF NOT EXISTS componentes (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Componente TEXT UNIQUE,
        Nombre TEXT NOT NULL,
        Descripcion TEXT,
        Tipo TEXT,
        Foto TEXT,
        Marca TEXT,
        Modelo TEXT,
        Precio REAL
    );

    CREATE TABLE IF NOT EXISTS proveedores (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT NOT NULL,
        Localidad TEXT,
        Contacto TEXT,
        Telefono TEXT,
        Email TEXT,
        Rubro TEXT,
        Direccion TEXT,
        Observaciones TEXT
    );

    CREATE TABLE IF NOT EXISTS maquinas_componentes (
        ID_Maquina INTEGER,
        ID_Componente INTEGER,
        PRIMARY KEY (ID_Maquina, ID_Componente),
        FOREIGN KEY (ID_Maquina) REFERENCES maquinas(ID) ON DELETE CASCADE,
        FOREIGN KEY (ID_Componente) REFERENCES componentes(ID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS frecuencias (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Maquina INTEGER,
        ID_Componente INTEGER,
        Frecuencia INTEGER,
        "Unidad tiempo" TEXT,
        "Criterio adicional" TEXT,
        FOREIGN KEY (ID_Maquina) REFERENCES maquinas(ID) ON DELETE CASCADE,
        FOREIGN KEY (ID_Componente) REFERENCES componentes(ID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS compras (
        ID_Compra INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Proveedor INTEGER,
        ID_Componente INTEGER,
        Cantidad INTEGER,
        Precio_Unitario REAL,
        Observacion TEXT,
        Fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ID_Proveedor) REFERENCES proveedores(ID) ON DELETE SET NULL,
        FOREIGN KEY (ID_Componente) REFERENCES componentes(ID) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS stock (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Componente INTEGER,
        Cantidad INTEGER,
        Tipo TEXT,
        Observacion TEXT,
        Fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ID_Componente) REFERENCES componentes(ID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS pagos_proveedores (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Proveedor INTEGER,
        Monto REAL,
        Metodo TEXT,
        Observacion TEXT,
        Fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ID_Proveedor) REFERENCES proveedores(ID) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS componentes_proveedores (
        ID_Proveedor INTEGER,
        ID_Componente INTEGER,
        cantidad INTEGER DEFAULT 1,
        PRIMARY KEY (ID_Proveedor, ID_Componente),
        FOREIGN KEY (ID_Proveedor) REFERENCES proveedores(ID) ON DELETE CASCADE,
        FOREIGN KEY (ID_Componente) REFERENCES componentes(ID) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

if __name__ == "__main__":
    create_tables()
