from app.utils.db import db

class Maquina(db.Model):
    __tablename__ = 'maquinas'
    
    # COLUMNAS IMPORTANTES EXPLÍCITAS
    id = db.Column('ID', db.Integer, primary_key=True)
    codigo = db.Column('Codigo', db.String(255), nullable=False, unique=True)
    nombre = db.Column('Nombre', db.String(255), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'marca': getattr(self, 'Marca', None),
            'modelo': getattr(self, 'Modelo', None),
            'año': getattr(self, 'Año', None),
            'estado': getattr(self, 'Estado', None),
            'observaciones': getattr(self, 'Observaciones', None),
            'foto': getattr(self, 'Foto', None)
        }
    
    def __repr__(self):
        return f'<Maquina {self.codigo}:{self.nombre}>'