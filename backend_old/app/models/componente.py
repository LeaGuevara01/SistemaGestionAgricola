from ..utils.db import db

class Componente(db.Model):
    __tablename__ = 'componentes'
    
    # COLUMNAS EXPLÍCITAS SEGÚN LA ESTRUCTURA REAL DE LA BD
    id = db.Column('ID', db.Integer, primary_key=True)
    id_componente = db.Column('ID_Componente', db.String(255), unique=True)
    nombre = db.Column('Nombre', db.String(255), nullable=False)
    descripcion = db.Column('Descripcion', db.String(255))
    tipo = db.Column('Tipo', db.String(255))
    foto = db.Column('Foto', db.String(255))
    marca = db.Column('Marca', db.String(255))
    modelo = db.Column('Modelo', db.String(255))
    precio = db.Column('Precio', db.Float)
    
    def to_dict(self):
        """Método customizado para serialización"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'numero_parte': self.id_componente,
            'categoria': self.tipo,
            'precio_unitario': self.precio or 0,
            'stock_minimo': 0,  # Campo no existe en BD actual
            'marca': self.marca,
            'modelo': self.modelo,
            'foto': self.foto
        }
    
    @property
    def precio_formateado(self):
        """Precio con formato"""
        return f"${self.precio:,.2f}" if self.precio else "Sin precio"
    
    def __repr__(self):
        return f'<Componente {self.id}:{self.nombre}>'