# models/proveedor.py
from . import db

class Proveedor(db.Model):
    __tablename__ = 'proveedores'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String, nullable=False)
    Localidad = db.Column(db.String)
    Contacto = db.Column(db.String)
    Telefono = db.Column(db.String)
    Email = db.Column(db.String)
    Rubro = db.Column(db.String)
    Direccion = db.Column(db.String)
    Observaciones = db.Column(db.String)

    componentes = db.relationship('ComponentesProveedores', back_populates='proveedor', cascade='all, delete-orphan')
    compras = db.relationship('Compra', backref='proveedor', lazy=True)
    pagos = db.relationship('PagoProveedor', backref='proveedor', lazy=True)

class Compra(db.Model):
    __tablename__ = 'compras'

    ID_Compra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.ID', ondelete='SET NULL'))
    ID_Componente = db.Column(db.Integer, db.ForeignKey('componentes.ID', ondelete='SET NULL'))
    Cantidad = db.Column(db.Integer)
    Precio_Unitario = db.Column(db.Float)
    Observacion = db.Column(db.String)
    Fecha = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    Componente = db.relationship('Componente', backref='compras_componente')
    Proveedor = db.relationship('Proveedor', backref='compras_proveedor')

class PagoProveedor(db.Model):
    __tablename__ = 'pagos_proveedores'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.ID', ondelete='SET NULL'))
    Monto = db.Column(db.Float)
    Metodo = db.Column(db.String)
    Observacion = db.Column(db.String)
    Fecha = db.Column(db.DateTime, server_default=db.func.current_timestamp())
