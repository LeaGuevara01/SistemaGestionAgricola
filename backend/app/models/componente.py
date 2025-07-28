from app.utils.db import db
from datetime import datetime

class Componente(db.Model):
    __tablename__ = 'componentes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    numero_parte = db.Column(db.String(50), unique=True)
    categoria = db.Column(db.String(50))
    precio_unitario = db.Column(db.Float)
    stock_minimo = db.Column(db.Integer, default=0)
    stock_actual = db.Column(db.Integer, default=0)
    foto = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    stock_items = db.relationship('Stock', backref='componente', lazy='dynamic', cascade='all, delete-orphan')
    compras = db.relationship('Compra', backref='componente', lazy='dynamic')
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'numero_parte': self.numero_parte,
            'categoria': self.categoria,
            'precio_unitario': self.precio_unitario,
            'stock_minimo': self.stock_minimo,
            'stock_actual': self.stock_actual,
            'foto': self.foto,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            data['stock_items'] = [item.to_dict() for item in self.stock_items]
            data['compras'] = [compra.to_dict() for compra in self.compras]
            
        return data
    
    @property
    def necesita_restock(self):
        return self.stock_actual <= self.stock_minimo
    
    def __repr__(self):
        return f'<Componente {self.nombre}>'