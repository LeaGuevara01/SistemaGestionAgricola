from app.utils.db import db
from datetime import datetime

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    razon_social = db.Column(db.String(150))
    cuit = db.Column(db.String(15), unique=True)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    ciudad = db.Column(db.String(50))
    provincia = db.Column(db.String(50))
    codigo_postal = db.Column(db.String(10))
    contacto = db.Column(db.String(100))
    condicion_iva = db.Column(db.String(50))
    forma_pago = db.Column(db.String(50))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    compras = db.relationship('Compra', backref='proveedor', lazy='dynamic')
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'razon_social': self.razon_social,
            'cuit': self.cuit,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'provincia': self.provincia,
            'codigo_postal': self.codigo_postal,
            'contacto': self.contacto,
            'condicion_iva': self.condicion_iva,
            'forma_pago': self.forma_pago,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            data['compras'] = [compra.to_dict() for compra in self.compras]
            
        return data
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'