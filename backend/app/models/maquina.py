from app.utils.db import db
from datetime import datetime

class Maquina(db.Model):
    __tablename__ = 'maquinas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    numero_serie = db.Column(db.String(100), unique=True)
    año = db.Column(db.Integer)
    tipo = db.Column(db.String(50))  # tractor, cosechadora, implemento, etc.
    estado = db.Column(db.String(20), default='operativo')  # operativo, mantenimiento, fuera_servicio
    horas_trabajo = db.Column(db.Float, default=0)
    ubicacion = db.Column(db.String(100))
    foto = db.Column(db.String(200))
    observaciones = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    compras = db.relationship('Compra', backref='maquina', lazy='dynamic')
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'marca': self.marca,
            'modelo': self.modelo,
            'numero_serie': self.numero_serie,
            'año': self.año,
            'tipo': self.tipo,
            'estado': self.estado,
            'horas_trabajo': self.horas_trabajo,
            'ubicacion': self.ubicacion,
            'foto': self.foto,
            'observaciones': self.observaciones,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            data['compras'] = [compra.to_dict() for compra in self.compras]
            
        return data
    
    def __repr__(self):
        return f'<Maquina {self.nombre}>'