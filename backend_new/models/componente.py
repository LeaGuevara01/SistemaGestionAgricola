"""
Modelo de Componente
"""
from extensions import db
from .base_mixin import BaseModelMixin

class Componente(BaseModelMixin, db.Model):
    """Modelo para componentes de máquinas agrícolas"""
    __tablename__ = 'componentes'
    
    # Información básica
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)
    
    numero_parte = db.Column(db.String(100), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(100), index=True)
    
    # Información técnica
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    especificaciones = db.Column(db.JSON)  # Para almacenar specs técnicas
    
    # Información económica
    precio_unitario = db.Column(db.Numeric(10, 2), default=0)
    moneda = db.Column(db.String(3), default='USD')
    
    # Gestión de stock
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=1)
    stock_maximo = db.Column(db.Integer, default=100)
    
    # Archivos y multimedia
    foto = db.Column(db.String(255))  # Ruta a la imagen
    documentos = db.Column(db.JSON)  # Array de rutas a documentos
    
    # Estado
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    compras = db.relationship('Compra', backref='componente_ref', lazy='dynamic')
    movimientos_stock = db.relationship('Stock', backref='componente_ref', lazy='dynamic')
    
    def __init__(self, numero_parte, nombre, **kwargs):
        self.numero_parte = numero_parte
        self.nombre = nombre
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def necesita_restock(self):
        """Verifica si el componente necesita restock"""
        return self.stock_actual <= self.stock_minimo
    
    @property
    def valor_total_stock(self):
        """Calcula el valor total del stock actual"""
        return float(self.stock_actual * (self.precio_unitario or 0))
    
    def actualizar_stock(self, cantidad, tipo_movimiento='manual'):
        """Actualizar stock del componente"""
        self.stock_actual += cantidad
        
        # Crear registro en tabla de movimientos
        from .stock import Stock
        movimiento = Stock(
            componente_id=self.id,
            tipo_movimiento=tipo_movimiento,
            cantidad=cantidad,
            stock_anterior=self.stock_actual - cantidad,
            stock_nuevo=self.stock_actual
        )
        db.session.add(movimiento)
        
        return self.stock_actual
    
    def to_dict(self):
        """Convertir a diccionario con información extendida"""
        data = super().to_dict()
        data.update({
            'necesita_restock': self.necesita_restock,
            'valor_total_stock': self.valor_total_stock,
            'precio_formateado': f"{self.moneda} {self.precio_unitario or 0:,.2f}"
        })
        return data
    
    @classmethod
    def buscar(cls, termino):
        """Buscar componentes por término"""
        termino = f"%{termino}%"
        return cls.query.filter(
            db.or_(
                cls.nombre.ilike(termino),
                cls.numero_parte.ilike(termino),
                cls.descripcion.ilike(termino),
                cls.categoria.ilike(termino),
                cls.marca.ilike(termino)
            )
        ).filter(cls.activo == True)
    
    @classmethod
    def por_categoria(cls, categoria):
        """Obtener componentes por categoría"""
        return cls.query.filter(
            cls.categoria == categoria,
            cls.activo == True
        )
    
    @classmethod
    def con_stock_bajo(cls):
        """Obtener componentes con stock bajo"""
        return cls.query.filter(
            cls.stock_actual <= cls.stock_minimo,
            cls.activo == True
        )
    
    def __repr__(self):
        return f'<Componente {self.numero_parte}: {self.nombre}>'
