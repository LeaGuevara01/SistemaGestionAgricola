from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Importar todas las rutas
from . import componentes, compras, maquinas, proveedores, stock, estadisticas