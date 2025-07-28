from app.utils.db import db
from datetime import datetime

class Compra(db.Model):
    __tablename__ = 'compras'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(50))
    fecha_compra = db.Column(db.Date, nullable=False)
    fecha_entrega = db.Column(db.Date)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    precio_total = db.Column(db.Float, nullable=False)
    iva = db.Column(db.Float, default=0)
    descuento = db.Column(db.Float, default=0)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, entregado, cancelado
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    componente_id = db.Column(db.Integer, db.ForeignKey('componentes.id'), nullable=True)
    maquina_id = db.Column(db.Integer, db.ForeignKey('maquinas.id'), nullable=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'numero_factura': self.numero_factura,
            'fecha_compra': self.fecha_compra.isoformat() if self.fecha_compra else None,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'precio_total': self.precio_total,
            'iva': self.iva,
            'descuento': self.descuento,
            'estado': self.estado,
            'observaciones': self.observaciones,
            'componente_id': self.componente_id,
            'maquina_id': self.maquina_id,
            'proveedor_id': self.proveedor_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            if self.componente:
                data['componente'] = self.componente.to_dict()
            if self.maquina:
                data['maquina'] = self.maquina.to_dict()
            if self.proveedor:
                data['proveedor'] = self.proveedor.to_dict()
                
        return data
    
    def __repr__(self):
        return f'<Compra {self.id} - {self.numero_factura}>'