# models/maquina.py
from . import db

class Maquina(db.Model):
    __tablename__ = 'maquinas'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Codigo = db.Column(db.String, unique=True, nullable=False)
    Nombre = db.Column(db.String, nullable=False)
    Marca = db.Column(db.String)
    Modelo = db.Column(db.String)
    Año = db.Column(db.Integer)
    Estado = db.Column(db.String)
    Observaciones = db.Column(db.String)
    Foto = db.Column(db.String)

class MaquinaComponente(db.Model):
    __tablename__ = 'maquinas_componentes'

    ID_Maquina = db.Column(db.Integer, db.ForeignKey('maquinas.ID', ondelete='CASCADE'), primary_key=True)
    ID_Componente = db.Column(db.Integer, db.ForeignKey('componentes.ID', ondelete='CASCADE'), primary_key=True)

class Frecuencia(db.Model):
    __tablename__ = 'frecuencias'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Maquina = db.Column(db.Integer, db.ForeignKey('maquinas.ID', ondelete='CASCADE'))
    ID_Componente = db.Column(db.Integer, db.ForeignKey('componentes.ID', ondelete='CASCADE'))
    Frecuencia = db.Column(db.Integer)
    Unidad_tiempo = db.Column(db.String)  # antes "Unidad tiempo"
    Criterio_adicional = db.Column(db.String)  # antes "Criterio adicional"
