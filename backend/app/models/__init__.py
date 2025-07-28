from .componente import Componente
from .maquina import Maquina
from .compra import Compra
from .proveedor import Proveedor
from .stock import Stock

# IMPORTAR DESPUÉS para evitar circulares
from .asociaciones import Frecuencia, PagoProveedor, componentes_proveedores, maquinas_componentes

__all__ = [
    'Componente', 
    'Maquina', 
    'Compra', 
    'Proveedor', 
    'Stock',
    'Frecuencia',
    'PagoProveedor',
    'componentes_proveedores',
    'maquinas_componentes'
]