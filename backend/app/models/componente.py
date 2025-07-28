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
            'descripcion': getattr(self, 'Descripcion', None),
            'numero_parte': getattr(self, 'ID_Componente', None),  # Mapear ID_Componente a numero_parte
            'categoria': getattr(self, 'Tipo', None),              # Mapear Tipo a categoria
            'precio_unitario': self.precio or 0,                  # Mapear Precio a precio_unitario
            'stock_minimo': 0,                                     # Campo no existe en BD actual
            'marca': getattr(self, 'Marca', None),
            'modelo': getattr(self, 'Modelo', None),
            'foto': getattr(self, 'Foto', None)
        }
    
    @property
    def precio_formateado(self):
        """Precio con formato"""
        return f"${self.precio:,.2f}" if self.precio else "Sin precio"
    
    def __repr__(self):
        return f'<Componente {self.id}:{self.nombre}>'