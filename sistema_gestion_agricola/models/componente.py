# models/componente.py
from . import db

class Componente(db.Model):
    __tablename__ = 'componentes'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Componente = db.Column(db.String, unique=True)
    Nombre = db.Column(db.String, nullable=False)
    Descripcion = db.Column(db.String)
    Tipo = db.Column(db.String)
    Foto = db.Column(db.String)
    Marca = db.Column(db.String)
    Modelo = db.Column(db.String)
    Precio = db.Column(db.Float)

    proveedores = db.relationship('ComponentesProveedores', back_populates='componente', cascade='all, delete-orphan')
    stock = db.relationship('Stock', backref='componente', lazy=True)
    frecuencias = db.relationship('Frecuencia', backref='componente', cascade="all, delete-orphan")

class ComponentesProveedores(db.Model):
    __tablename__ = 'componentes_proveedores'

    ID_Proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.ID', ondelete='CASCADE'), primary_key=True)
    ID_Componente = db.Column(db.Integer, db.ForeignKey('componentes.ID', ondelete='CASCADE'), primary_key=True)
    Cantidad = db.Column(db.Integer, default=1)

    componente = db.relationship('Componente', back_populates='proveedores')
    proveedor = db.relationship('Proveedor', back_populates='componentes')
