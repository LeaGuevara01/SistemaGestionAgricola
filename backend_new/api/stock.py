"""
API para gestión de stock y movimientos de inventario
"""
from flask import request, jsonify
from datetime import datetime, date

from . import api_bp
from models.stock import Stock
from models.componente import Componente
from extensions import db

@api_bp.route('/stock', methods=['GET'])
def get_movimientos_stock():
    """Obtener lista de movimientos de stock"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        componente_id = request.args.get('componente_id')
        tipo_movimiento = request.args.get('tipo_movimiento')
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Query base
        query = Stock.query
        
        # Filtros
        if componente_id:
            query = query.filter(Stock.componente_id == componente_id)
        
        if tipo_movimiento:
            query = query.filter(Stock.tipo_movimiento == tipo_movimiento)
        
        # Filtros de fecha
        if fecha_inicio:
            try:
                fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                query = query.filter(Stock.created_at >= fecha_inicio_obj)
            except ValueError:
                pass
        
        if fecha_fin:
            try:
                fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d')
                # Agregar 23:59:59 para incluir todo el día
                fecha_fin_obj = fecha_fin_obj.replace(hour=23, minute=59, second=59)
                query = query.filter(Stock.created_at <= fecha_fin_obj)
            except ValueError:
                pass
        
        # Ordenamiento
        query = query.order_by(Stock.created_at.desc())
        
        # Paginación
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [movimiento.to_dict() for movimiento in pagination.items],
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/<int:id>', methods=['GET'])
def get_movimiento_stock(id):
    """Obtener un movimiento de stock específico"""
    try:
        movimiento = Stock.get_by_id(id)
        if not movimiento:
            return jsonify({
                'success': False,
                'error': 'Movimiento no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': movimiento.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/movimiento', methods=['POST'])
def crear_movimiento_stock():
    """Crear un nuevo movimiento de stock"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['componente_id', 'tipo_movimiento', 'cantidad']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo {field} es requerido'
                }), 400
        
        componente_id = data['componente_id']
        tipo_movimiento = data['tipo_movimiento']
        cantidad = data['cantidad']
        motivo = data.get('motivo', 'Movimiento manual')
        usuario = data.get('usuario', 'Sistema')
        precio_unitario = data.get('precio_unitario')
        numero_documento = data.get('numero_documento')
        observaciones = data.get('observaciones')
        
        # Validar componente
        componente = Componente.get_by_id(componente_id)
        if not componente:
            return jsonify({
                'success': False,
                'error': 'Componente no encontrado'
            }), 404
        
        # Validar cantidad
        try:
            cantidad = int(cantidad)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Cantidad debe ser un número entero'
            }), 400
        
        # Validar tipo de movimiento
        tipos_validos = ['entrada', 'salida', 'ajuste', 'compra', 'consumo', 'devolucion']
        if tipo_movimiento not in tipos_validos:
            return jsonify({
                'success': False,
                'error': f'Tipo de movimiento debe ser uno de: {", ".join(tipos_validos)}'
            }), 400
        
        # Para salidas, hacer la cantidad negativa
        if tipo_movimiento in ['salida', 'consumo'] and cantidad > 0:
            cantidad = -cantidad
        
        # Crear movimiento
        movimiento = Stock.crear_movimiento(
            componente_id=componente_id,
            tipo_movimiento=tipo_movimiento,
            cantidad=cantidad,
            motivo=motivo,
            usuario=usuario,
            precio_unitario=precio_unitario,
            numero_documento=numero_documento,
            observaciones=observaciones
        )
        
        movimiento.save()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': movimiento.to_dict(),
            'message': 'Movimiento de stock creado exitosamente'
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/componente/<int:componente_id>', methods=['GET'])
def get_movimientos_por_componente(componente_id):
    """Obtener movimientos de stock de un componente específico"""
    try:
        componente = Componente.get_by_id(componente_id)
        if not componente:
            return jsonify({
                'success': False,
                'error': 'Componente no encontrado'
            }), 404
        
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        movimientos_query = Stock.por_componente(componente_id)
        
        pagination = movimientos_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Obtener resumen
        resumen = Stock.resumen_por_componente(componente_id)
        
        return jsonify({
            'success': True,
            'data': {
                'componente': componente.to_dict(),
                'movimientos': [mov.to_dict() for mov in pagination.items],
                'resumen': resumen
            },
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/resumen', methods=['GET'])
def get_resumen_stock():
    """Obtener resumen general de stock"""
    try:
        # Estadísticas generales
        total_componentes = Componente.query.filter(Componente.activo == True).count()
        componentes_sin_stock = Componente.query.filter(
            Componente.stock_actual == 0,
            Componente.activo == True
        ).count()
        componentes_stock_bajo = Componente.con_stock_bajo().count()
        
        # Valor total del inventario
        valor_total = db.session.query(
            db.func.sum(Componente.stock_actual * Componente.precio_unitario)
        ).filter(Componente.activo == True).scalar() or 0
        
        # Movimientos recientes
        movimientos_hoy = Stock.query.filter(
            db.func.date(Stock.created_at) == date.today()
        ).count()
        
        # Tipos de movimientos más comunes
        tipos_movimientos = db.session.query(
            Stock.tipo_movimiento,
            db.func.count(Stock.id).label('cantidad')
        ).group_by(Stock.tipo_movimiento).all()
        
        return jsonify({
            'success': True,
            'data': {
                'componentes': {
                    'total': total_componentes,
                    'sin_stock': componentes_sin_stock,
                    'stock_bajo': componentes_stock_bajo
                },
                'inventario': {
                    'valor_total': float(valor_total),
                    'valor_formateado': f"USD {valor_total:,.2f}"
                },
                'movimientos': {
                    'hoy': movimientos_hoy,
                    'por_tipo': [{'tipo': tipo, 'cantidad': cantidad} for tipo, cantidad in tipos_movimientos]
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/tipos-movimiento', methods=['GET'])
def get_tipos_movimiento():
    """Obtener tipos de movimiento disponibles"""
    return jsonify({
        'success': True,
        'data': [
            {'valor': 'entrada', 'label': 'Entrada'},
            {'valor': 'salida', 'label': 'Salida'},
            {'valor': 'ajuste', 'label': 'Ajuste'},
            {'valor': 'compra', 'label': 'Compra'},
            {'valor': 'consumo', 'label': 'Consumo'},
            {'valor': 'devolucion', 'label': 'Devolución'}
        ]
    })

@api_bp.route('/stock/entradas', methods=['GET'])
def get_entradas_stock():
    """Obtener solo movimientos de entrada"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        query = Stock.entradas().order_by(Stock.created_at.desc())
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [movimiento.to_dict() for movimiento in pagination.items],
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/salidas', methods=['GET'])
def get_salidas_stock():
    """Obtener solo movimientos de salida"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        query = Stock.salidas().order_by(Stock.created_at.desc())
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [movimiento.to_dict() for movimiento in pagination.items],
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
