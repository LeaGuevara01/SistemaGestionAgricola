from flask import Blueprint

api_bp = Blueprint('api', __name__)

# ✅ IMPORTAR SOLO LOS ARCHIVOS QUE EXISTEN
from . import admin
from . import componentes
from . import compras
from . import maquinas
from . import proveedores
from . import stock
# Los archivos vacíos no se importan por ahora