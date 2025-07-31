"""
Modelos ajustados al schema real de la base de datos PostgreSQL
"""
from extensions import db
from datetime import datetime

class ComponenteDB(db.Model):
    """Modelo que coincide con la tabla componentes real"""
    __tablename__ = 'componentes'
    
    # Columnas tal como están en la BD
    ID = db.Column(db.Integer, primary_key=True)
    ID_Componente = db.Column(db.String, unique=True)
    Nombre = db.Column(db.String, nullable=False)
    Descripcion = db.Column(db.String)
    Tipo = db.Column(db.String)
    Foto = db.Column(db.String)
    Marca = db.Column(db.String)
    Modelo = db.Column(db.String)
    Precio = db.Column(db.Float)
    
    def to_dict(self):
        """Convertir a diccionario para la API"""
        return {
            'id': self.ID,
            'numero_parte': self.ID_Componente,
            'nombre': self.Nombre,
            'descripcion': self.Descripcion,
            'categoria': self.Tipo,
            'marca': self.Marca,
            'modelo': self.Modelo,
            'precio_unitario': self.Precio,
            'foto': self.Foto,
            'activo': True  # Por defecto activo
        }
    
    @classmethod
    def get_all_active(cls):
        """Obtener todos los componentes activos"""
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, id):
        """Obtener por ID"""
        return cls.query.filter_by(ID=id).first()

class ProveedorDB(db.Model):
    """Modelo que coincide con la tabla proveedores real"""
    __tablename__ = 'proveedores'
    
    ID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String, nullable=False)
    Localidad = db.Column(db.String)
    Contacto = db.Column(db.String)
    Telefono = db.Column(db.String)
    Email = db.Column(db.String)
    Rubro = db.Column(db.String)
    Direccion = db.Column(db.String)
    Observaciones = db.Column(db.String)
    
    def to_dict(self):
        return {
            'id': self.ID,
            'nombre': self.Nombre,
            'localidad': self.Localidad,
            'contacto': self.Contacto,
            'telefono': self.Telefono,
            'email': self.Email,
            'rubro': self.Rubro,
            'direccion': self.Direccion,
            'observaciones': self.Observaciones,
            'activo': True
        }
    
    @classmethod
    def get_all_active(cls):
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(ID=id).first()

class CompraDB(db.Model):
    """Modelo que coincide con la tabla compras real"""
    __tablename__ = 'compras'
    
    ID_Compra = db.Column(db.Integer, primary_key=True)
    ID_Proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.ID'))
    ID_Componente = db.Column(db.Integer, db.ForeignKey('componentes.ID'))
    Cantidad = db.Column(db.Integer)
    Precio_Unitario = db.Column(db.Float)
    Observacion = db.Column(db.String)
    Fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    proveedor = db.relationship('ProveedorDB', backref='compras')
    componente = db.relationship('ComponenteDB', backref='compras')
    
    def to_dict(self):
        return {
            'id': self.ID_Compra,
            'proveedor_id': self.ID_Proveedor,
            'componente_id': self.ID_Componente,
            'cantidad': self.Cantidad,
            'precio_unitario': self.Precio_Unitario,
            'observacion': self.Observacion,
            'fecha_compra': self.Fecha.isoformat() if self.Fecha else None,
            'numero_compra': f"COMP-{self.ID_Compra:06d}",
            'estado': 'completada'
        }
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(ID_Compra=id).first()

class MaquinaDB(db.Model):
    """Modelo que coincide con la tabla maquinas real"""
    __tablename__ = 'maquinas'
    
    ID = db.Column(db.Integer, primary_key=True)
    Codigo = db.Column(db.String, unique=True, nullable=False)
    Nombre = db.Column(db.String, nullable=False)
    Marca = db.Column(db.String)
    Modelo = db.Column(db.String)
    Año = db.Column(db.Integer)
    Estado = db.Column(db.String)
    Observaciones = db.Column(db.String)
    Foto = db.Column(db.String)
    Tipo = db.Column(db.String)
    Horas = db.Column(db.Integer)
    Ubicacion = db.Column(db.String)
    Activo = db.Column(db.Boolean)
    
    def to_dict(self):
        return {
            'id': self.ID,
            'codigo': self.Codigo,
            'nombre': self.Nombre,
            'marca': self.Marca,
            'modelo': self.Modelo,
            'año': self.Año,
            'estado': self.Estado,
            'observaciones': self.Observaciones,
            'foto': self.Foto,
            'tipo': self.Tipo,
            'horas_uso': self.Horas,
            'ubicacion': self.Ubicacion,
            'activo': self.Activo if self.Activo is not None else True
        }
    
    @classmethod
    def get_all_active(cls):
        return cls.query.filter(cls.Activo.is_(True)).all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(ID=id).first()

class StockDB(db.Model):
    """Modelo que coincide con la tabla stock real"""
    __tablename__ = 'stock'
    
    ID = db.Column(db.Integer, primary_key=True)
    ID_Componente = db.Column(db.Integer, db.ForeignKey('componentes.ID'))
    Cantidad = db.Column(db.Integer)
    Tipo = db.Column(db.String)
    Observacion = db.Column(db.String)
    Fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    componente = db.relationship('ComponenteDB', backref='stocks')
    
    def to_dict(self):
        return {
            'id': self.ID,
            'componente_id': self.ID_Componente,
            'cantidad': self.Cantidad,
            'tipo': self.Tipo,
            'observacion': self.Observacion,
            'fecha': self.Fecha.isoformat() if self.Fecha else None
        }
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    
    @classmethod
    def get_by_componente(cls, componente_id):
        return cls.query.filter_by(ID_Componente=componente_id).all()
