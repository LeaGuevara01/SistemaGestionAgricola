"""
Modelo de Stock (Movimientos de inventario)
"""
from datetime import datetime
from extensions import db
from .base_mixin import BaseModelMixin

class Stock(BaseModelMixin, db.Model):
    """Modelo para registrar movimientos de stock"""
    __tablename__ = 'stock'
    
    # Información básica
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)
    
    # Relación con componente
    componente_id = db.Column(db.Integer, db.ForeignKey('componentes.id'), nullable=False)
    
    # Información del movimiento
    tipo_movimiento = db.Column(db.String(50), nullable=False)  # 'entrada', 'salida', 'ajuste', 'compra', 'consumo'
    motivo = db.Column(db.String(200))  # Motivo del movimiento
    
    # Cantidades
    cantidad = db.Column(db.Integer, nullable=False)  # Puede ser negativo para salidas
    stock_anterior = db.Column(db.Integer, nullable=False)
    stock_nuevo = db.Column(db.Integer, nullable=False)
    
    # Información adicional
    precio_unitario = db.Column(db.Numeric(10, 2))  # Precio al momento del movimiento
    valor_total = db.Column(db.Numeric(10, 2))  # Valor total del movimiento
    
    # Referencias a otros documentos
    numero_documento = db.Column(db.String(100))  # Número de factura, remito, etc.
    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'))  # Si es por compra
    
    # Usuario responsable
    usuario = db.Column(db.String(100))  # Quien realizó el movimiento
    
    # Notas adicionales
    observaciones = db.Column(db.Text)
    
    def __init__(self, componente_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, **kwargs):
        self.componente_id = componente_id
        self.tipo_movimiento = tipo_movimiento
        self.cantidad = cantidad
        self.stock_anterior = stock_anterior
        self.stock_nuevo = stock_nuevo
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Calcular valor total si se proporciona precio
        if kwargs.get('precio_unitario'):
            self.valor_total = abs(cantidad) * kwargs['precio_unitario']
    
    @property
    def es_entrada(self):
        """Verifica si es un movimiento de entrada"""
        return self.cantidad > 0
    
    @property
    def es_salida(self):
        """Verifica si es un movimiento de salida"""
        return self.cantidad < 0
    
    @property
    def cantidad_absoluta(self):
        """Devuelve la cantidad en valor absoluto"""
        return abs(self.cantidad)
    
    def to_dict(self):
        """Convertir a diccionario con información extendida"""
        data = super().to_dict()
        data.update({
            'componente_nombre': self.componente_ref.nombre if self.componente_ref else None,
            'componente_numero_parte': self.componente_ref.numero_parte if self.componente_ref else None,
            'es_entrada': self.es_entrada,
            'es_salida': self.es_salida,
            'cantidad_absoluta': self.cantidad_absoluta,
            'valor_formateado': f"${self.valor_total:,.2f}" if self.valor_total else None
        })
        return data
    
    @classmethod
    def por_componente(cls, componente_id):
        """Obtener movimientos por componente"""
        return cls.query.filter(cls.componente_id == componente_id).order_by(cls.created_at.desc())
    
    @classmethod
    def por_tipo(cls, tipo_movimiento):
        """Obtener movimientos por tipo"""
        return cls.query.filter(cls.tipo_movimiento == tipo_movimiento)
    
    @classmethod
    def entradas(cls):
        """Obtener solo movimientos de entrada"""
        return cls.query.filter(cls.cantidad > 0)
    
    @classmethod
    def salidas(cls):
        """Obtener solo movimientos de salida"""
        return cls.query.filter(cls.cantidad < 0)
    
    @classmethod
    def por_rango_fecha(cls, fecha_inicio, fecha_fin):
        """Obtener movimientos en un rango de fechas"""
        return cls.query.filter(
            cls.created_at >= fecha_inicio,
            cls.created_at <= fecha_fin
        )
    
    @classmethod
    def resumen_por_componente(cls, componente_id):
        """Obtener resumen de movimientos por componente"""
        movimientos = cls.por_componente(componente_id).all()
        
        total_entradas = sum([m.cantidad for m in movimientos if m.cantidad > 0])
        total_salidas = sum([abs(m.cantidad) for m in movimientos if m.cantidad < 0])
        valor_total_entradas = sum([m.valor_total or 0 for m in movimientos if m.cantidad > 0])
        valor_total_salidas = sum([m.valor_total or 0 for m in movimientos if m.cantidad < 0])
        
        return {
            'total_movimientos': len(movimientos),
            'total_entradas': total_entradas,
            'total_salidas': total_salidas,
            'stock_actual': movimientos[0].stock_nuevo if movimientos else 0,
            'valor_total_entradas': valor_total_entradas,
            'valor_total_salidas': valor_total_salidas,
            'ultimo_movimiento': movimientos[0].created_at if movimientos else None
        }
    
    @classmethod
    def crear_movimiento(cls, componente_id, tipo_movimiento, cantidad, motivo=None, **kwargs):
        """Crear un nuevo movimiento de stock"""
        from .componente import Componente
        
        componente = Componente.get_by_id(componente_id)
        if not componente:
            raise ValueError("Componente no encontrado")
        
        stock_anterior = componente.stock_actual
        stock_nuevo = stock_anterior + cantidad
        
        # Validar que no quede stock negativo
        if stock_nuevo < 0:
            raise ValueError("El movimiento resultaría en stock negativo")
        
        # Crear movimiento
        movimiento = cls(
            componente_id=componente_id,
            tipo_movimiento=tipo_movimiento,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            motivo=motivo,
            **kwargs
        )
        
        # Actualizar stock del componente
        componente.stock_actual = stock_nuevo
        
        return movimiento
    
    def __repr__(self):
        return f'<Stock {self.tipo_movimiento}: {self.cantidad} unidades>'
