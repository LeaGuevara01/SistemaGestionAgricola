from app.utils.db import db
from datetime import datetime

class Compra(db.Model):
    __tablename__ = 'compras'
    
    # COLUMNAS IMPORTANTES EXPLÍCITAS
    id = db.Column('ID_Compra', db.Integer, primary_key=True)
    proveedor_id = db.Column('ID_Proveedor', db.Integer, db.ForeignKey('proveedores.ID'))
    componente_id = db.Column('ID_Componente', db.Integer, db.ForeignKey('componentes.ID'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'proveedor_id': self.proveedor_id,
            'componente_id': self.componente_id,
            'cantidad': getattr(self, 'Cantidad', None),
            'precio_unitario': getattr(self, 'Precio_Unitario', None),
            'observacion': getattr(self, 'Observacion', None),
            'fecha': getattr(self, 'Fecha', None).isoformat() if getattr(self, 'Fecha', None) else None
        }
    
    @property
    def precio_total(self):
        cantidad = getattr(self, 'Cantidad', 0) or 0
        precio_unitario = getattr(self, 'Precio_Unitario', 0) or 0
        return cantidad * precio_unitario
    
    def __repr__(self):
        return f'<Compra {self.id}>'