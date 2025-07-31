"""
API para estadísticas y reportes del sistema
"""
from flask import request, jsonify
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_

from . import api_bp
from extensions import db
from models.componente import Componente
from models.maquina import Maquina
from models.proveedor import Proveedor
from models.compra import Compra
from models.stock import Stock

@api_bp.route('/estadisticas/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Obtener estadísticas principales para el dashboard"""
    try:
        # Contadores generales
        total_componentes = Componente.query.filter(Componente.activo == True).count()
        total_maquinas = Maquina.query.filter(Maquina.activa == True).count()
        total_proveedores = Proveedor.query.filter(Proveedor.activo == True).count()
        
        # Alertas y notificaciones
        componentes_stock_bajo = Componente.con_stock_bajo().count()
        maquinas_necesitan_revision = Maquina.necesitan_revision().count()
        compras_pendientes = Compra.pendientes_entrega().count()
        compras_con_retraso = Compra.con_retraso().count()
        
        # Valor del inventario
        valor_inventario = db.session.query(
            func.sum(Componente.stock_actual * Componente.precio_unitario)
        ).filter(Componente.activo == True).scalar() or 0
        
        # Compras del mes actual
        inicio_mes = date.today().replace(day=1)
        compras_mes = Compra.query.filter(
            Compra.fecha_compra >= inicio_mes,
            Compra.estado != 'cancelada'
        ).count()
        
        valor_compras_mes = db.session.query(func.sum(Compra.total)).filter(
            Compra.fecha_compra >= inicio_mes,
            Compra.estado != 'cancelada'
        ).scalar() or 0
        
        # Movimientos de stock del día
        movimientos_hoy = Stock.query.filter(
            func.date(Stock.created_at) == date.today()
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'contadores': {
                    'componentes': total_componentes,
                    'maquinas': total_maquinas,
                    'proveedores': total_proveedores
                },
                'alertas': {
                    'componentes_stock_bajo': componentes_stock_bajo,
                    'maquinas_necesitan_revision': maquinas_necesitan_revision,
                    'compras_pendientes': compras_pendientes,
                    'compras_con_retraso': compras_con_retraso
                },
                'inventario': {
                    'valor_total': float(valor_inventario),
                    'valor_formateado': f"USD {valor_inventario:,.2f}"
                },
                'mes_actual': {
                    'compras_realizadas': compras_mes,
                    'valor_compras': float(valor_compras_mes),
                    'valor_compras_formateado': f"ARS {valor_compras_mes:,.2f}",
                    'movimientos_hoy': movimientos_hoy
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/estadisticas/compras', methods=['GET'])
def get_estadisticas_compras():
    """Obtener estadísticas detalladas de compras"""
    try:
        periodo = request.args.get('periodo', '12')  # meses
        meses = int(periodo)
        
        fecha_inicio = date.today() - timedelta(days=meses * 30)
        
        # Compras por mes
        compras_por_mes = db.session.query(
            func.extract('year', Compra.fecha_compra).label('año'),
            func.extract('month', Compra.fecha_compra).label('mes'),
            func.count(Compra.id).label('cantidad'),
            func.sum(Compra.total).label('total')
        ).filter(
            Compra.fecha_compra >= fecha_inicio,
            Compra.estado != 'cancelada'
        ).group_by(
            func.extract('year', Compra.fecha_compra),
            func.extract('month', Compra.fecha_compra)
        ).order_by('año', 'mes').all()
        
        # Compras por proveedor
        compras_por_proveedor = db.session.query(
            Proveedor.nombre,
            func.count(Compra.id).label('cantidad'),
            func.sum(Compra.total).label('total')
        ).join(Compra).filter(
            Compra.fecha_compra >= fecha_inicio,
            Compra.estado != 'cancelada'
        ).group_by(Proveedor.nombre).order_by(func.sum(Compra.total).desc()).limit(10).all()
        
        # Compras por estado
        compras_por_estado = db.session.query(
            Compra.estado,
            func.count(Compra.id).label('cantidad')
        ).filter(
            Compra.fecha_compra >= fecha_inicio
        ).group_by(Compra.estado).all()
        
        # Componentes más comprados
        componentes_mas_comprados = db.session.query(
            Componente.nombre,
            func.sum(Compra.cantidad).label('cantidad_total'),
            func.count(Compra.id).label('ordenes')
        ).join(Compra).filter(
            Compra.fecha_compra >= fecha_inicio,
            Compra.estado != 'cancelada'
        ).group_by(Componente.nombre).order_by(func.sum(Compra.cantidad).desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'por_mes': [
                    {
                        'año': int(año),
                        'mes': int(mes),
                        'cantidad': cantidad,
                        'total': float(total or 0)
                    }
                    for año, mes, cantidad, total in compras_por_mes
                ],
                'por_proveedor': [
                    {
                        'proveedor': nombre,
                        'cantidad': cantidad,
                        'total': float(total or 0)
                    }
                    for nombre, cantidad, total in compras_por_proveedor
                ],
                'por_estado': [
                    {
                        'estado': estado,
                        'cantidad': cantidad
                    }
                    for estado, cantidad in compras_por_estado
                ],
                'componentes_mas_comprados': [
                    {
                        'componente': nombre,
                        'cantidad_total': cantidad_total,
                        'ordenes': ordenes
                    }
                    for nombre, cantidad_total, ordenes in componentes_mas_comprados
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/estadisticas/stock', methods=['GET'])
def get_estadisticas_stock():
    """Obtener estadísticas de stock e inventario"""
    try:
        # Distribución de stock por categoría
        stock_por_categoria = db.session.query(
            Componente.categoria,
            func.count(Componente.id).label('cantidad_componentes'),
            func.sum(Componente.stock_actual).label('stock_total'),
            func.sum(Componente.stock_actual * Componente.precio_unitario).label('valor_total')
        ).filter(
            Componente.activo == True,
            Componente.categoria.isnot(None)
        ).group_by(Componente.categoria).all()
        
        # Componentes con mayor valor en stock
        componentes_mayor_valor = db.session.query(
            Componente.nombre,
            Componente.stock_actual,
            Componente.precio_unitario,
            (Componente.stock_actual * Componente.precio_unitario).label('valor_total')
        ).filter(
            Componente.activo == True,
            Componente.stock_actual > 0
        ).order_by((Componente.stock_actual * Componente.precio_unitario).desc()).limit(10).all()
        
        # Movimientos de stock por tipo (últimos 30 días)
        fecha_inicio = date.today() - timedelta(days=30)
        movimientos_por_tipo = db.session.query(
            Stock.tipo_movimiento,
            func.count(Stock.id).label('cantidad'),
            func.sum(func.abs(Stock.cantidad)).label('cantidad_total')
        ).filter(
            Stock.created_at >= fecha_inicio
        ).group_by(Stock.tipo_movimiento).all()
        
        # Evolución del stock (últimos 7 días)
        entradas_por_dia = []
        salidas_por_dia = []
        
        for i in range(7):
            dia = date.today() - timedelta(days=i)
            
            entradas = db.session.query(func.sum(Stock.cantidad)).filter(
                func.date(Stock.created_at) == dia,
                Stock.cantidad > 0
            ).scalar() or 0
            
            salidas = db.session.query(func.sum(func.abs(Stock.cantidad))).filter(
                func.date(Stock.created_at) == dia,
                Stock.cantidad < 0
            ).scalar() or 0
            
            entradas_por_dia.append({
                'fecha': dia.isoformat(),
                'cantidad': entradas
            })
            
            salidas_por_dia.append({
                'fecha': dia.isoformat(),
                'cantidad': salidas
            })
        
        return jsonify({
            'success': True,
            'data': {
                'por_categoria': [
                    {
                        'categoria': categoria or 'Sin categoría',
                        'cantidad_componentes': cantidad_componentes,
                        'stock_total': stock_total or 0,
                        'valor_total': float(valor_total or 0)
                    }
                    for categoria, cantidad_componentes, stock_total, valor_total in stock_por_categoria
                ],
                'componentes_mayor_valor': [
                    {
                        'nombre': nombre,
                        'stock_actual': stock_actual,
                        'precio_unitario': float(precio_unitario or 0),
                        'valor_total': float(valor_total or 0)
                    }
                    for nombre, stock_actual, precio_unitario, valor_total in componentes_mayor_valor
                ],
                'movimientos_por_tipo': [
                    {
                        'tipo': tipo,
                        'cantidad_movimientos': cantidad,
                        'cantidad_total': cantidad_total or 0
                    }
                    for tipo, cantidad, cantidad_total in movimientos_por_tipo
                ],
                'evolucion_semanal': {
                    'entradas': list(reversed(entradas_por_dia)),
                    'salidas': list(reversed(salidas_por_dia))
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/estadisticas/proveedores', methods=['GET'])
def get_estadisticas_proveedores():
    """Obtener estadísticas de proveedores"""
    try:
        # Ranking de proveedores por volumen de compras
        ranking_proveedores = db.session.query(
            Proveedor.nombre,
            Proveedor.calificacion,
            func.count(Compra.id).label('total_compras'),
            func.sum(Compra.total).label('total_gastado'),
            func.avg(
                func.extract('day', Compra.fecha_entrega_real - Compra.fecha_entrega_estimada)
            ).label('promedio_retraso')
        ).join(Compra).filter(
            Compra.estado != 'cancelada'
        ).group_by(Proveedor.id, Proveedor.nombre, Proveedor.calificacion)\
         .order_by(func.sum(Compra.total).desc()).limit(10).all()
        
        # Distribución por tipo de proveedor
        proveedores_por_tipo = db.session.query(
            Proveedor.tipo_proveedor,
            func.count(Proveedor.id).label('cantidad')
        ).filter(
            Proveedor.activo == True,
            Proveedor.tipo_proveedor.isnot(None)
        ).group_by(Proveedor.tipo_proveedor).all()
        
        # Proveedores por calificación
        proveedores_por_calificacion = db.session.query(
            func.floor(Proveedor.calificacion).label('calificacion_rango'),
            func.count(Proveedor.id).label('cantidad')
        ).filter(
            Proveedor.activo == True,
            Proveedor.calificacion.isnot(None)
        ).group_by(func.floor(Proveedor.calificacion)).all()
        
        # Tiempo promedio de entrega por proveedor
        tiempo_entrega = db.session.query(
            Proveedor.nombre,
            func.avg(
                func.extract('day', Compra.fecha_entrega_real - Compra.fecha_compra)
            ).label('dias_promedio')
        ).join(Compra).filter(
            Compra.fecha_entrega_real.isnot(None),
            Compra.estado == 'entregada'
        ).group_by(Proveedor.nombre).order_by('dias_promedio').limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'ranking': [
                    {
                        'nombre': nombre,
                        'calificacion': float(calificacion or 0),
                        'total_compras': total_compras,
                        'total_gastado': float(total_gastado or 0),
                        'promedio_retraso': float(promedio_retraso or 0)
                    }
                    for nombre, calificacion, total_compras, total_gastado, promedio_retraso in ranking_proveedores
                ],
                'por_tipo': [
                    {
                        'tipo': tipo or 'Sin especificar',
                        'cantidad': cantidad
                    }
                    for tipo, cantidad in proveedores_por_tipo
                ],
                'por_calificacion': [
                    {
                        'rango': f"{int(rango)}-{int(rango)+1}",
                        'cantidad': cantidad
                    }
                    for rango, cantidad in proveedores_por_calificacion
                ],
                'tiempo_entrega': [
                    {
                        'proveedor': nombre,
                        'dias_promedio': round(float(dias_promedio or 0), 1)
                    }
                    for nombre, dias_promedio in tiempo_entrega
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/estadisticas/maquinas', methods=['GET'])
def get_estadisticas_maquinas():
    """Obtener estadísticas de máquinas"""
    try:
        # Distribución por tipo de máquina
        maquinas_por_tipo = db.session.query(
            Maquina.tipo_maquina,
            func.count(Maquina.id).label('cantidad')
        ).filter(
            Maquina.activa == True,
            Maquina.tipo_maquina.isnot(None)
        ).group_by(Maquina.tipo_maquina).all()
        
        # Distribución por estado
        maquinas_por_estado = db.session.query(
            Maquina.estado,
            func.count(Maquina.id).label('cantidad')
        ).filter(
            Maquina.activa == True
        ).group_by(Maquina.estado).all()
        
        # Máquinas por año de fabricación
        maquinas_por_año = db.session.query(
            func.floor(Maquina.año_fabricacion / 10) * 10,
            func.count(Maquina.id).label('cantidad')
        ).filter(
            Maquina.activa == True,
            Maquina.año_fabricacion.isnot(None)
        ).group_by(func.floor(Maquina.año_fabricacion / 10)).all()
        
        # Valor total del parque de máquinas
        valor_total_maquinas = db.session.query(
            func.sum(Maquina.valor_adquisicion)
        ).filter(
            Maquina.activa == True
        ).scalar() or 0
        
        # Top máquinas por horas de trabajo
        top_horas_trabajo = db.session.query(
            Maquina.nombre,
            Maquina.horas_trabajo,
            Maquina.estado
        ).filter(
            Maquina.activa == True,
            Maquina.horas_trabajo.isnot(None)
        ).order_by(Maquina.horas_trabajo.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'por_tipo': [
                    {
                        'tipo': tipo or 'Sin especificar',
                        'cantidad': cantidad
                    }
                    for tipo, cantidad in maquinas_por_tipo
                ],
                'por_estado': [
                    {
                        'estado': estado,
                        'cantidad': cantidad
                    }
                    for estado, cantidad in maquinas_por_estado
                ],
                'por_decada': [
                    {
                        'decada': f"{int(decada)}s",
                        'cantidad': cantidad
                    }
                    for decada, cantidad in maquinas_por_año
                ],
                'valor_total': {
                    'monto': float(valor_total_maquinas),
                    'formateado': f"USD {valor_total_maquinas:,.2f}"
                },
                'top_horas_trabajo': [
                    {
                        'nombre': nombre,
                        'horas_trabajo': horas_trabajo or 0,
                        'estado': estado
                    }
                    for nombre, horas_trabajo, estado in top_horas_trabajo
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
