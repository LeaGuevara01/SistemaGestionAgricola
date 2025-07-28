from app.utils.db import db
from datetime import datetime

# ✅ TABLAS INTERMEDIAS CON NOMBRES REALES
componentes_proveedores = db.Table('componentes_proveedores',
    db.Column('ID_Proveedor', db.Integer, db.ForeignKey('proveedores.ID'), primary_key=True),
    db.Column('ID_Componente', db.Integer, db.ForeignKey('componentes.ID'), primary_key=True),
    db.Column('Cantidad', db.Integer)
)

maquinas_componentes = db.Table('maquinas_componentes',
    db.Column('ID_Maquina', db.Integer, db.ForeignKey('maquinas.ID'), primary_key=True),
    db.Column('ID_Componente', db.Integer, db.ForeignKey('componentes.ID'), primary_key=True)
)

class Frecuencia(db.Model):
    __tablename__ = 'frecuencias'
    
    # ✅ MAPEAR A NOMBRES REALES
    id = db.Column('ID', db.Integer, primary_key=True)
    maquina_id = db.Column('ID_Maquina', db.Integer, db.ForeignKey('maquinas.ID'))
    componente_id = db.Column('ID_Componente', db.Integer, db.ForeignKey('componentes.ID'))
    frecuencia = db.Column('Frecuencia', db.Integer)
    unidad_tiempo = db.Column('Unidad_tiempo', db.String(255))
    criterio_adicional = db.Column('Criterio_adicional', db.String(255))
    
    def to_dict(self):
        return {
            'id': self.id,
            'maquina_id': self.maquina_id,
            'componente_id': self.componente_id,
            'frecuencia': self.frecuencia,
            'unidad_tiempo': self.unidad_tiempo,
            'criterio_adicional': self.criterio_adicional
        }

class PagoProveedor(db.Model):
    __tablename__ = 'pagos_proveedores'
    
    # ✅ MAPEAR A NOMBRES REALES
    id = db.Column('ID', db.Integer, primary_key=True)
    proveedor_id = db.Column('ID_Proveedor', db.Integer, db.ForeignKey('proveedores.ID'))
    monto = db.Column('Monto', db.Float)
    metodo = db.Column('Metodo', db.String(255))
    observacion = db.Column('Observacion', db.String(255))
    fecha = db.Column('Fecha', db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'proveedor_id': self.proveedor_id,
            'monto': self.monto,
            'metodo': self.metodo,
            'observacion': self.observacion,
            'fecha': self.fecha.isoformat() if self.fecha else None
        }