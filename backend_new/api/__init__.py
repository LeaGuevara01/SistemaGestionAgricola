"""
API Blueprint para el Sistema de Gestión Agrícola
"""
from flask import Blueprint

# Crear blueprint principal de la API
api_bp = Blueprint('api', __name__)

# Importar todas las rutas de los módulos
from . import componentes
from . import maquinas
from . import proveedores
from . import compras
from . import stock
from . import estadisticas

# Definir qué se exporta
__all__ = ['api_bp']
