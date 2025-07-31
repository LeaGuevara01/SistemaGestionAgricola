"""
API para gestión de compras
"""
from flask import request, jsonify
from datetime import datetime, date

from . import api_bp
from extensions import db
from models.compra import Compra
from models.proveedor import Proveedor
from models.componente import Componente

@api_bp.route('/compras', methods=['GET'])
def get_compras():
    """Obtener lista de compras"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('q', '').strip()
        estado = request.args.get('estado')
        proveedor_id = request.args.get('proveedor_id')
        componente_id = request.args.get('componente_id')
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Query base
        query = Compra.query
        
        # Filtros
        if search:
            query = query.join(Proveedor).join(Componente).filter(
                db.or_(
                    Compra.numero_compra.ilike(f"%{search}%"),
                    Proveedor.nombre.ilike(f"%{search}%"),
                    Componente.nombre.ilike(f"%{search}%"),
                    Compra.numero_factura.ilike(f"%{search}%")
                )
            )
        
        if estado:
            query = query.filter(Compra.estado == estado)
        
        if proveedor_id:
            query = query.filter(Compra.proveedor_id == proveedor_id)
        
        if componente_id:
            query = query.filter(Compra.componente_id == componente_id)
        
        # Filtros de fecha
        if fecha_inicio:
            try:
                fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                query = query.filter(Compra.fecha_compra >= fecha_inicio_obj)
            except ValueError:
                pass
        
        if fecha_fin:
            try:
                fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                query = query.filter(Compra.fecha_compra <= fecha_fin_obj)
            except ValueError:
                pass
        
        # Ordenamiento
        sort_by = request.args.get('sort_by', 'fecha_compra')
        sort_order = request.args.get('sort_order', 'desc')
        
        if hasattr(Compra, sort_by):
            column = getattr(Compra, sort_by)
            if sort_order == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        else:
            query = query.order_by(Compra.fecha_compra.desc())
        
        # Paginación
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [compra.to_dict() for compra in pagination.items],
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

@api_bp.route('/compras/<int:id>', methods=['GET'])
def get_compra(id):
    """Obtener una compra específica"""
    try:
        compra = Compra.get_by_id(id)
        if not compra:
            return jsonify({
                'success': False,
                'error': 'Compra no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': compra.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/compras', methods=['POST'])
def create_compra():
    """Crear una nueva compra"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['numero_compra', 'proveedor_id', 'componente_id', 'cantidad', 'precio_unitario']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo {field} es requerido'
                }), 400
        
        # Verificar que el número de compra no exista
        if Compra.query.filter_by(numero_compra=data['numero_compra']).first():
            return jsonify({
                'success': False,
                'error': 'El número de compra ya existe'
            }), 400
        
        # Verificar que existan proveedor y componente
        proveedor = Proveedor.get_by_id(data['proveedor_id'])
        if not proveedor:
            return jsonify({
                'success': False,
                'error': 'Proveedor no encontrado'
            }), 404
        
        componente = Componente.get_by_id(data['componente_id'])
        if not componente:
            return jsonify({
                'success': False,
                'error': 'Componente no encontrado'
            }), 404
        
        # Parsear fechas
        fecha_compra = data.get('fecha_compra')
        if fecha_compra:
            try:
                fecha_compra = datetime.strptime(fecha_compra, '%Y-%m-%d').date()
            except ValueError:
                fecha_compra = date.today()
        else:
            fecha_compra = date.today()
        
        fecha_entrega_estimada = data.get('fecha_entrega_estimada')
        if fecha_entrega_estimada:
            try:
                fecha_entrega_estimada = datetime.strptime(fecha_entrega_estimada, '%Y-%m-%d').date()
            except ValueError:
                fecha_entrega_estimada = None
        
        # Crear compra
        compra = Compra(
            numero_compra=data['numero_compra'],
            proveedor_id=data['proveedor_id'],
            componente_id=data['componente_id'],
            cantidad=data['cantidad'],
            precio_unitario=data['precio_unitario'],
            fecha_compra=fecha_compra,
            fecha_entrega_estimada=fecha_entrega_estimada,
            descuento=data.get('descuento', 0),
            impuestos=data.get('impuestos', 0),
            moneda=data.get('moneda', 'ARS'),
            estado=data.get('estado', 'pendiente'),
            numero_factura=data.get('numero_factura'),
            numero_remito=data.get('numero_remito'),
            condiciones_pago=data.get('condiciones_pago'),
            notas=data.get('notas')
        )
        
        compra.save()
        
        return jsonify({
            'success': True,
            'data': compra.to_dict(),
            'message': 'Compra creada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/compras/<int:id>', methods=['PUT'])
def update_compra(id):
    """Actualizar una compra"""
    try:
        compra = Compra.get_by_id(id)
        if not compra:
            return jsonify({
                'success': False,
                'error': 'Compra no encontrada'
            }), 404
        
        data = request.get_json()
        
        # No permitir actualizar si ya está entregada
        if compra.estado == 'entregada' and data.get('estado') != 'entregada':
            return jsonify({
                'success': False,
                'error': 'No se puede modificar una compra ya entregada'
            }), 400
        
        # Actualizar campos básicos
        basic_fields = [
            'cantidad', 'precio_unitario', 'descuento', 'impuestos',
            'numero_factura', 'numero_remito', 'condiciones_pago', 'notas'
        ]
        
        for field in basic_fields:
            if field in data:
                setattr(compra, field, data[field])
        
        # Actualizar fechas
        if 'fecha_entrega_estimada' in data and data['fecha_entrega_estimada']:
            try:
                compra.fecha_entrega_estimada = datetime.strptime(data['fecha_entrega_estimada'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Recalcular totales si cambiaron campos monetarios
        if any(field in data for field in ['cantidad', 'precio_unitario', 'descuento', 'impuestos']):
            compra.calcular_totales()
        
        compra.save()
        
        return jsonify({
            'success': True,
            'data': compra.to_dict(),
            'message': 'Compra actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/compras/<int:id>', methods=['DELETE'])
def delete_compra(id):
    """Cancelar una compra"""
    try:
        compra = Compra.get_by_id(id)
        if not compra:
            return jsonify({
                'success': False,
                'error': 'Compra no encontrada'
            }), 404
        
        data = request.get_json() or {}
        motivo = data.get('motivo', 'Cancelada por usuario')
        
        if compra.cancelar_compra(motivo):
            compra.save()
            
            return jsonify({
                'success': True,
                'message': 'Compra cancelada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se puede cancelar la compra en su estado actual'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/compras/<int:id>/entregar', methods=['POST'])
def marcar_compra_entregada(id):
    """Marcar compra como entregada"""
    try:
        compra = Compra.get_by_id(id)
        if not compra:
            return jsonify({
                'success': False,
                'error': 'Compra no encontrada'
            }), 404
        
        data = request.get_json() or {}
        fecha_entrega = data.get('fecha_entrega')
        
        if fecha_entrega:
            try:
                fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d').date()
            except ValueError:
                fecha_entrega = None
        
        if compra.marcar_como_entregada(fecha_entrega):
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': compra.to_dict(),
                'message': 'Compra marcada como entregada y stock actualizado'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'La compra ya está marcada como entregada'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/compras/estados', methods=['GET'])
def get_estados_compra():
    """Obtener estados de compra disponibles"""
    return jsonify({
        'success': True,
        'data': ['pendiente', 'confirmada', 'entregada', 'cancelada']
    })

@api_bp.route('/compras/pendientes', methods=['GET'])
def get_compras_pendientes():
    """Obtener compras pendientes de entrega"""
    try:
        compras = Compra.pendientes_entrega().all()
        
        return jsonify({
            'success': True,
            'data': [compra.to_dict() for compra in compras],
            'count': len(compras)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/compras/con-retraso', methods=['GET'])
def get_compras_con_retraso():
    """Obtener compras con retraso en entrega"""
    try:
        compras = Compra.con_retraso().all()
        
        return jsonify({
            'success': True,
            'data': [compra.to_dict() for compra in compras],
            'count': len(compras)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/compras/resumen', methods=['GET'])
def get_resumen_compras():
    """Obtener resumen estadístico de compras"""
    try:
        # Contar por estado
        total_compras = Compra.query.count()
        pendientes = Compra.por_estado('pendiente').count()
        confirmadas = Compra.por_estado('confirmada').count()
        entregadas = Compra.por_estado('entregada').count()
        canceladas = Compra.por_estado('cancelada').count()
        con_retraso = Compra.con_retraso().count()
        
        # Calcular totales monetarios
        total_monto = db.session.query(db.func.sum(Compra.total)).filter(
            Compra.estado != 'cancelada'
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'totales': {
                    'total_compras': total_compras,
                    'pendientes': pendientes,
                    'confirmadas': confirmadas,
                    'entregadas': entregadas,
                    'canceladas': canceladas,
                    'con_retraso': con_retraso
                },
                'montos': {
                    'total_invertido': float(total_monto),
                    'total_formateado': f"ARS {total_monto:,.2f}"
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
