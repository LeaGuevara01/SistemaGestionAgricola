from ..models import Stock, Componente
from ..utils.db import db, commit_or_rollback

class StockService:
    
    @staticmethod
    def registrar_movimiento(componente_id, tipo_movimiento, cantidad, motivo=None, observaciones=None, usuario=None):
        """Registra un movimiento de stock y actualiza el stock actual del componente"""
        
        # Obtener componente
        componente = Componente.query.get(componente_id)
        if not componente:
            raise ValueError("Componente no encontrado")
        
        cantidad_anterior = componente.stock_actual
        
        # Calcular nueva cantidad según el tipo de movimiento
        if tipo_movimiento == 'entrada':
            cantidad_nueva = cantidad_anterior + cantidad
        elif tipo_movimiento == 'salida':
            if cantidad_anterior < cantidad:
                raise ValueError("Stock insuficiente")
            cantidad_nueva = cantidad_anterior - cantidad
        elif tipo_movimiento == 'ajuste':
            cantidad_nueva = cantidad
            cantidad = cantidad_nueva - cantidad_anterior
        else:
            raise ValueError("Tipo de movimiento inválido")
        
        # Crear registro de movimiento
        movimiento = Stock(
            componente_id=componente_id,
            tipo_movimiento=tipo_movimiento,
            cantidad=cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=cantidad_nueva,
            motivo=motivo,
            observaciones=observaciones,
            usuario=usuario
        )
        
        # Actualizar stock del componente
        componente.stock_actual = cantidad_nueva
        
        # Guardar cambios
        db.session.add(movimiento)
        commit_or_rollback()
        
        return movimiento
    
    @staticmethod
    def obtener_historial(componente_id=None, limit=100):
        """Obtiene el historial de movimientos de stock"""
        query = Stock.query
        
        if componente_id:
            query = query.filter_by(componente_id=componente_id)
        
        return query.order_by(Stock.fecha.desc()).limit(limit).all()
    
    @staticmethod
    def obtener_componentes_bajo_stock():
        """Obtiene componentes que necesitan restock"""
        return Componente.query.filter(
            Componente.stock_actual <= Componente.stock_minimo,
            Componente.activo == True
        ).all()