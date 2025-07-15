from . import db

class Stock(db.Model):
    __tablename__ = 'stock'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Componente = db.Column(db.Integer, db.ForeignKey('componentes.ID', ondelete='CASCADE'))
    Cantidad = db.Column(db.Integer)
    Tipo = db.Column(db.String)
    Observacion = db.Column(db.String)
    Fecha = db.Column(db.DateTime, server_default=db.func.current_timestamp())
