"""
Modelo de Proveedor
"""
from extensions import db
from .base_mixin import BaseModelMixin

class Proveedor(BaseModelMixin, db.Model):
    """Modelo para proveedores de componentes"""
    __tablename__ = 'proveedores'
    
    # Información básica
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)
    
    codigo_proveedor = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    razon_social = db.Column(db.String(250))
    tipo_proveedor = db.Column(db.String(50))  # 'nacional', 'internacional', 'local'
    
    # Información de contacto
    email = db.Column(db.String(120), index=True)
    telefono = db.Column(db.String(50))
    sitio_web = db.Column(db.String(200))
    
    # Dirección
    direccion = db.Column(db.String(300))
    ciudad = db.Column(db.String(100))
    provincia = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(20))
    pais = db.Column(db.String(100), default='Argentina')
    
    # Información fiscal
    cuit_dni = db.Column(db.String(20))
    condicion_iva = db.Column(db.String(50))  # 'responsable_inscripto', 'monotributo', etc.
    
    # Información comercial
    condiciones_pago = db.Column(db.String(200))  # 'contado', '30 días', etc.
    descuento_general = db.Column(db.Numeric(5, 2), default=0)  # Porcentaje
    moneda_preferida = db.Column(db.String(3), default='ARS')
    
    # Calificación y estado
    calificacion = db.Column(db.Numeric(3, 2))  # 1.00 a 5.00
    activo = db.Column(db.Boolean, default=True)
    
    # Metadatos
    notas = db.Column(db.Text)
    documentos = db.Column(db.JSON)  # Array de rutas a documentos
    
    # Relaciones
    compras = db.relationship('Compra', backref='proveedor_ref', lazy='dynamic')
    
    def __init__(self, codigo_proveedor, nombre, **kwargs):
        self.codigo_proveedor = codigo_proveedor
        self.nombre = nombre
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def direccion_completa(self):
        """Devuelve la dirección completa formateada"""
        partes = [self.direccion, self.ciudad, self.provincia, self.codigo_postal]
        return ', '.join([parte for parte in partes if parte])
    
    @property
    def total_compras(self):
        """Calcula el total de compras realizadas a este proveedor"""
        return sum([compra.total for compra in self.compras if compra.total])
    
    @property
    def ultima_compra(self):
        """Devuelve la fecha de la última compra"""
        ultima = self.compras.order_by(db.desc('fecha_compra')).first()
        return ultima.fecha_compra if ultima else None
    
    def to_dict(self):
        """Convertir a diccionario con información extendida"""
        data = super().to_dict()
        data.update({
            'direccion_completa': self.direccion_completa,
            'total_compras': self.total_compras,
            'ultima_compra': self.ultima_compra.isoformat() if self.ultima_compra else None,
            'cantidad_compras': self.compras.count()
        })
        return data
    
    @classmethod
    def buscar(cls, termino):
        """Buscar proveedores por término"""
        termino = f"%{termino}%"
        return cls.query.filter(
            db.or_(
                cls.nombre.ilike(termino),
                cls.codigo_proveedor.ilike(termino),
                cls.razon_social.ilike(termino),
                cls.email.ilike(termino),
                cls.cuit_dni.ilike(termino)
            )
        ).filter(cls.activo == True)
    
    @classmethod
    def por_tipo(cls, tipo):
        """Obtener proveedores por tipo"""
        return cls.query.filter(
            cls.tipo_proveedor == tipo,
            cls.activo == True
        )
    
    @classmethod
    def mejor_calificados(cls, limite=10):
        """Obtener proveedores mejor calificados"""
        return cls.query.filter(
            cls.activo == True,
            cls.calificacion.isnot(None)
        ).order_by(db.desc(cls.calificacion)).limit(limite)
    
    def actualizar_calificacion(self, nueva_calificacion):
        """Actualizar calificación del proveedor"""
        if 1.0 <= nueva_calificacion <= 5.0:
            self.calificacion = nueva_calificacion
            return True
        return False
    
    def __repr__(self):
        return f'<Proveedor {self.codigo_proveedor}: {self.nombre}>'
