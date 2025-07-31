"""
Modelo base simplificado para todos los modelos del sistema
"""
from datetime import datetime

class BaseModelMixin:
    """Mixin con funcionalidades comunes para todos los modelos"""
    
    def to_dict(self):
        """Convertir modelo a diccionario"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def save(self):
        """Guardar el modelo en la base de datos"""
        from extensions import db
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Eliminar el modelo de la base de datos"""
        from extensions import db
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        """Obtener modelo por ID"""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """Obtener todos los registros"""
        return cls.query.all()
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {getattr(self, "id", "unknown")}>'
