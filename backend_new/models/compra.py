"""
Modelo de Compra
"""
from datetime import datetime, date
from extensions import db
from .base_mixin import BaseModelMixin

class Compra(BaseModelMixin, db.Model):
    """Modelo para registrar compras de componentes"""
    __tablename__ = 'compras'
    
    # Información básica
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)
    
    numero_compra = db.Column(db.String(100), unique=True, nullable=False, index=True)
    fecha_compra = db.Column(db.Date, default=date.today, nullable=False)
    fecha_entrega_estimada = db.Column(db.Date)
    fecha_entrega_real = db.Column(db.Date)
    
    # Relaciones (Foreign Keys)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    componente_id = db.Column(db.Integer, db.ForeignKey('componentes.id'), nullable=False)
    
    # Información de la compra
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(5, 2), default=0)  # Porcentaje
    impuestos = db.Column(db.Numeric(10, 2), default=0)  # Monto fijo
    
    # Totales
    subtotal = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    moneda = db.Column(db.String(3), default='ARS')
    
    # Estado de la compra
    estado = db.Column(db.String(50), default='pendiente')  # 'pendiente', 'confirmada', 'entregada', 'cancelada'
    
    # Información adicional
    numero_factura = db.Column(db.String(100))
    numero_remito = db.Column(db.String(100))
    condiciones_pago = db.Column(db.String(200))
    notas = db.Column(db.Text)
    
    # Archivos relacionados
    documentos = db.Column(db.JSON)  # Array de rutas a documentos
    
    def __init__(self, numero_compra, proveedor_id, componente_id, cantidad, precio_unitario, **kwargs):
        self.numero_compra = numero_compra
        self.proveedor_id = proveedor_id
        self.componente_id = componente_id
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.calcular_totales()
    
    def calcular_totales(self):
        """Calcular subtotal y total de la compra"""
        self.subtotal = self.cantidad * self.precio_unitario
        
        # Aplicar descuento
        descuento_monto = self.subtotal * (self.descuento / 100) if self.descuento else 0
        subtotal_con_descuento = self.subtotal - descuento_monto
        
        # Agregar impuestos
        self.total = subtotal_con_descuento + (self.impuestos or 0)
    
    @property
    def dias_hasta_entrega(self):
        """Días hasta la entrega estimada"""
        if self.fecha_entrega_estimada:
            delta = self.fecha_entrega_estimada - date.today()
            return delta.days
        return None
    
    @property
    def entregada_a_tiempo(self):
        """Verifica si fue entregada a tiempo"""
        if self.fecha_entrega_real and self.fecha_entrega_estimada:
            return self.fecha_entrega_real <= self.fecha_entrega_estimada
        return None
    
    @property
    def dias_retraso(self):
        """Días de retraso en la entrega"""
        if self.fecha_entrega_real and self.fecha_entrega_estimada:
            if self.fecha_entrega_real > self.fecha_entrega_estimada:
                delta = self.fecha_entrega_real - self.fecha_entrega_estimada
                return delta.days
        return 0
    
    def marcar_como_entregada(self, fecha_entrega=None):
        """Marcar compra como entregada y actualizar stock"""
        if self.estado != 'entregada':
            self.estado = 'entregada'
            self.fecha_entrega_real = fecha_entrega or date.today()
            
            # Actualizar stock del componente
            if self.componente_ref:
                self.componente_ref.actualizar_stock(self.cantidad, 'compra')
            
            return True
        return False
    
    def cancelar_compra(self, motivo=None):
        """Cancelar la compra"""
        if self.estado not in ['entregada', 'cancelada']:
            self.estado = 'cancelada'
            if motivo:
                self.notas = f"Cancelada: {motivo}"
            return True
        return False
    
    def to_dict(self):
        """Convertir a diccionario con información extendida"""
        data = super().to_dict()
        data.update({
            'proveedor_nombre': self.proveedor_ref.nombre if self.proveedor_ref else None,
            'componente_nombre': self.componente_ref.nombre if self.componente_ref else None,
            'dias_hasta_entrega': self.dias_hasta_entrega,
            'entregada_a_tiempo': self.entregada_a_tiempo,
            'dias_retraso': self.dias_retraso,
            'total_formateado': f"{self.moneda} {self.total:,.2f}" if self.total else None
        })
        return data
    
    @classmethod
    def por_proveedor(cls, proveedor_id):
        """Obtener compras por proveedor"""
        return cls.query.filter(cls.proveedor_id == proveedor_id)
    
    @classmethod
    def por_componente(cls, componente_id):
        """Obtener compras por componente"""
        return cls.query.filter(cls.componente_id == componente_id)
    
    @classmethod
    def por_estado(cls, estado):
        """Obtener compras por estado"""
        return cls.query.filter(cls.estado == estado)
    
    @classmethod
    def por_rango_fecha(cls, fecha_inicio, fecha_fin):
        """Obtener compras en un rango de fechas"""
        return cls.query.filter(
            cls.fecha_compra >= fecha_inicio,
            cls.fecha_compra <= fecha_fin
        )
    
    @classmethod
    def pendientes_entrega(cls):
        """Obtener compras pendientes de entrega"""
        return cls.query.filter(
            cls.estado.in_(['pendiente', 'confirmada'])
        )
    
    @classmethod
    def con_retraso(cls):
        """Obtener compras con retraso en entrega"""
        return cls.query.filter(
            cls.fecha_entrega_estimada < date.today(),
            cls.estado != 'entregada'
        )
    
    def __repr__(self):
        return f'<Compra {self.numero_compra}: {self.cantidad} unidades>'
