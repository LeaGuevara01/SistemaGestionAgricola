from ..utils.db import db

class Stock(db.Model):
    __tablename__ = 'stock'
    
    # COLUMNAS IMPORTANTES EXPLÍCITAS
    id = db.Column('ID', db.Integer, primary_key=True)
    componente_id = db.Column('ID_Componente', db.Integer, db.ForeignKey('componentes.ID'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'componente_id': self.componente_id,
            'cantidad': getattr(self, 'Cantidad', None),
            'tipo': getattr(self, 'Tipo', None),
            'observacion': getattr(self, 'Observacion', None),
            'fecha': getattr(self, 'Fecha', None).isoformat() if getattr(self, 'Fecha', None) else None
        }
    
    def __repr__(self):
        return f'<Stock {self.id}: {getattr(self, "Tipo", "")}'