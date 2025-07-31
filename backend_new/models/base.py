"""
Modelo base para todos los modelos del sistema
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# La instancia db se importará dinámicamente para evitar importaciones circulares
db = None

def get_db():
    """Obtener instancia de db de forma lazy"""
    global db
    if db is None:
        from extensions import db as app_db
        db = app_db
    return db

class BaseModel:
    """Modelo base con campos comunes"""
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Asegurar que cada subclase tenga acceso a db
        if not hasattr(cls, '_db_initialized'):
            cls._db_initialized = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
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
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Eliminar el modelo de la base de datos"""
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
        return f'<{self.__class__.__name__} {self.id}>'
