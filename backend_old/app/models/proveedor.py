from ..utils.db import db

class Proveedor(db.Model):
    __tablename__ = 'proveedores'

    # COLUMNAS IMPORTANTES EXPLÍCITAS
    id = db.Column('ID', db.Integer, primary_key=True)
    nombre = db.Column('Nombre', db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'localidad': getattr(self, 'Localidad', None),
            'contacto': getattr(self, 'Contacto', None),
            'telefono': getattr(self, 'Telefono', None),
            'email': getattr(self, 'Email', None),
            'rubro': getattr(self, 'Rubro', None),
            'direccion': getattr(self, 'Direccion', None),
            'observaciones': getattr(self, 'Observaciones', None)
        }
    
    def __repr__(self):
        return f'<Proveedor {self.id}:{self.nombre}>'