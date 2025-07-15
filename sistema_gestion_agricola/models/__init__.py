from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar modelos aquí (para que Flask-Migrate los vea)
from .proveedor import Proveedor, Compra, PagoProveedor
from .componente import Componente, ComponentesProveedores
from .maquina import Maquina, MaquinaComponente, Frecuencia
from .stock import Stock