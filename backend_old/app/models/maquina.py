from ..utils.db import db

class Maquina(db.Model):
    __tablename__ = 'maquinas'
    
    # COLUMNAS EXPLÍCITAS SEGÚN LA ESTRUCTURA ACTUALIZADA DE LA BD
    id = db.Column('ID', db.Integer, primary_key=True)
    codigo = db.Column('Codigo', db.String(255), nullable=False, unique=True)
    nombre = db.Column('Nombre', db.String(255), nullable=False)
    marca = db.Column('Marca', db.String(255))
    modelo = db.Column('Modelo', db.String(255))
    año = db.Column('Año', db.Integer)
    estado = db.Column('Estado', db.String(255))
    observaciones = db.Column('Observaciones', db.String(255))
    foto = db.Column('Foto', db.String(255))
    tipo = db.Column('Tipo', db.String(255))
    horas = db.Column('Horas', db.Integer)
    ubicacion = db.Column('Ubicacion', db.String(255))
    activo = db.Column('Activo', db.Boolean)
    
    def to_dict(self, include_relations=False):
        base_dict = {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'marca': self.marca,
            'modelo': self.modelo,
            'año': self.año,
            'estado': self.estado,
            'observaciones': self.observaciones,
            'foto': self.foto,
            'tipo': self.tipo,
            'horas_trabajo': self.horas or 0,  # Mapear Horas a horas_trabajo
            'ubicacion': self.ubicacion,
            'activo': self.activo if self.activo is not None else True,
            # Campo que NO existe en la BD actual
            'numero_serie': None
        }
        
        if include_relations:
            # Si necesitamos incluir relaciones, podemos agregar componentes aquí
            # Por ahora, retornamos solo los datos básicos
            base_dict['componentes'] = []
            
        return base_dict
    
    def __repr__(self):
        return f'<Maquina {self.codigo}:{self.nombre}>'