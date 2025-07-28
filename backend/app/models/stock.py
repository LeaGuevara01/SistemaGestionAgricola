from app.utils.db import db
from datetime import datetime

class Stock(db.Model):
    __tablename__ = 'stock'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_movimiento = db.Column(db.String(20), nullable=False)  # entrada, salida, ajuste
    cantidad = db.Column(db.Integer, nullable=False)
    cantidad_anterior = db.Column(db.Integer, nullable=False)
    cantidad_nueva = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.Column(db.String(50))
    
    # Foreign Keys
    componente_id = db.Column(db.Integer, db.ForeignKey('componentes.id'), nullable=False)
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'tipo_movimiento': self.tipo_movimiento,
            'cantidad': self.cantidad,
            'cantidad_anterior': self.cantidad_anterior,
            'cantidad_nueva': self.cantidad_nueva,
            'motivo': self.motivo,
            'observaciones': self.observaciones,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'usuario': self.usuario,
            'componente_id': self.componente_id
        }
        
        if include_relations and self.componente:
            data['componente'] = self.componente.to_dict()
            
        return data
    
    def __repr__(self):
        return f'<Stock {self.tipo_movimiento} - {self.cantidad}>'