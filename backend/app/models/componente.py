from app.utils.db import db

class Componente(db.Model):
    __tablename__ = 'componentes'
    
    # COLUMNAS IMPORTANTES EXPLÍCITAS
    id = db.Column('ID', db.Integer, primary_key=True)
    nombre = db.Column('Nombre', db.String(255), nullable=False)
    precio = db.Column('Precio', db.Float)
    
    def to_dict(self):
        """Método customizado para serialización"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio or 0,
            'descripcion': getattr(self, 'Descripcion', None),
            'tipo': getattr(self, 'Tipo', None),
            'marca': getattr(self, 'Marca', None),
            'modelo': getattr(self, 'Modelo', None),
            'foto': getattr(self, 'Foto', None),
            'id_componente': getattr(self, 'ID_Componente', None)
        }
    
    @property
    def precio_formateado(self):
        """Precio con formato"""
        return f"${self.precio:,.2f}" if self.precio else "Sin precio"
    
    def __repr__(self):
        return f'<Componente {self.id}:{self.nombre}>'