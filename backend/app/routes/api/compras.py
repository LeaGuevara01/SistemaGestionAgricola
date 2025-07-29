from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from datetime import datetime, date
from . import api_bp
from ...models import Compra, Componente, Maquina, Proveedor
from ...utils.db import db, commit_or_rollback

@api_bp.route('/compras', methods=['GET'])
def get_compras():
    try:
        # Filtros
        proveedor_id = request.args.get('proveedor_id')
        componente_id = request.args.get('componente_id')
        maquina_id = request.args.get('maquina_id')
        estado = request.args.get('estado')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        include_relations = request.args.get('include_relations', 'false').lower() == 'true'
        
        query = Compra.query
        
        if proveedor_id:
            query = query.filter(Compra.proveedor_id == proveedor_id)
        if componente_id:
            query = query.filter(Compra.componente_id == componente_id)
        if maquina_id:
            query = query.filter(Compra.maquina_id == maquina_id)
        if estado:
            query = query.filter(Compra.estado == estado)
        
        if fecha_desde:
            try:
                fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                query = query.filter(Compra.fecha_compra >= fecha_desde_obj)
            except ValueError:
                raise BadRequest("Formato de fecha inválido para fecha_desde")
        
        if fecha_hasta:
            try:
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                query = query.filter(Compra.fecha_compra <= fecha_hasta_obj)
            except ValueError:
                raise BadRequest("Formato de fecha inválido para fecha_hasta")
        
        compras = query.order_by(Compra.fecha_compra.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [compra.to_dict(include_relations=include_relations) for compra in compras],
            'total': len(compras)
        })
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/compras', methods=['POST'])
def create_compra():
    try:
        data = request.get_json()
        
        # Validaciones básicas
        required_fields = ['proveedor_id', 'fecha_compra', 'cantidad', 'precio_unitario']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise BadRequest(f"El campo '{field}' es requerido")
        
        # Verificar que al menos uno de componente_id o maquina_id esté presente
        if not data.get('componente_id') and not data.get('maquina_id'):
            raise BadRequest("Debe especificar un componente o una máquina")
        
        # Verificar que el proveedor existe
        proveedor = Proveedor.query.get(data['proveedor_id'])
        if not proveedor:
            raise BadRequest("Proveedor no encontrado")
        
        # Verificar componente si se especifica
        if data.get('componente_id'):
            componente = Componente.query.get(data['componente_id'])
            if not componente:
                raise BadRequest("Componente no encontrado")
        
        # Verificar máquina si se especifica
        if data.get('maquina_id'):
            maquina = Maquina.query.get(data['maquina_id'])
            if not maquina:
                raise BadRequest("Máquina no encontrada")
        
        # Parsear fecha
        try:
            fecha_compra = datetime.strptime(data['fecha_compra'], '%Y-%m-%d').date()
        except ValueError:
            raise BadRequest("Formato de fecha inválido")
        
        fecha_entrega = None
        if data.get('fecha_entrega'):
            try:
                fecha_entrega = datetime.strptime(data['fecha_entrega'], '%Y-%m-%d').date()
            except ValueError:
                raise BadRequest("Formato de fecha de entrega inválido")
        
        # Calcular precios
        cantidad = int(data['cantidad'])
        precio_unitario = float(data['precio_unitario'])
        iva = float(data.get('iva', 0))
        descuento = float(data.get('descuento', 0))
        
        subtotal = cantidad * precio_unitario
        total_descuento = subtotal * (descuento / 100)
        subtotal_con_descuento = subtotal - total_descuento
        total_iva = subtotal_con_descuento * (iva / 100)
        precio_total = subtotal_con_descuento + total_iva
        
        compra = Compra(
            numero_factura=data.get('numero_factura'),
            fecha_compra=fecha_compra,
            fecha_entrega=fecha_entrega,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            precio_total=precio_total,
            iva=iva,
            descuento=descuento,
            estado=data.get('estado', 'pendiente'),
            observaciones=data.get('observaciones'),
            componente_id=data.get('componente_id'),
            maquina_id=data.get('maquina_id'),
            proveedor_id=data['proveedor_id']
        )
        
        db.session.add(compra)
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'data': compra.to_dict(include_relations=True),
            'message': 'Compra registrada exitosamente'
        }), 201
        
    except BadRequest as e:
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

@api_bp.route('/compras/<int:id>', methods=['GET'])
def get_compra(id):
    try:
        compra = Compra.query.get_or_404(id)
        
        return jsonify({
            'success': True,
            'data': compra.to_dict(include_relations=True)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/compras/<int:id>', methods=['PUT'])
def update_compra(id):
    try:
        compra = Compra.query.get_or_404(id)
        data = request.get_json()
        
        # Actualizar campos básicos
        if 'numero_factura' in data:
            compra.numero_factura = data['numero_factura']
        
        if 'fecha_compra' in data:
            try:
                compra.fecha_compra = datetime.strptime(data['fecha_compra'], '%Y-%m-%d').date()
            except ValueError:
                raise BadRequest("Formato de fecha inválido")
        
        if 'fecha_entrega' in data:
            if data['fecha_entrega']:
                try:
                    compra.fecha_entrega = datetime.strptime(data['fecha_entrega'], '%Y-%m-%d').date()
                except ValueError:
                    raise BadRequest("Formato de fecha de entrega inválido")
            else:
                compra.fecha_entrega = None
        
        # Recalcular precios si cambian cantidad, precio unitario, IVA o descuento
        recalcular = False
        
        if 'cantidad' in data:
            compra.cantidad = int(data['cantidad'])
            recalcular = True
        
        if 'precio_unitario' in data:
            compra.precio_unitario = float(data['precio_unitario'])
            recalcular = True
        
        if 'iva' in data:
            compra.iva = float(data['iva'])
            recalcular = True
        
        if 'descuento' in data:
            compra.descuento = float(data['descuento'])
            recalcular = True
        
        if recalcular:
            subtotal = compra.cantidad * compra.precio_unitario
            total_descuento = subtotal * (compra.descuento / 100)
            subtotal_con_descuento = subtotal - total_descuento
            total_iva = subtotal_con_descuento * (compra.iva / 100)
            compra.precio_total = subtotal_con_descuento + total_iva
        
        if 'estado' in data:
            compra.estado = data['estado']
        
        if 'observaciones' in data:
            compra.observaciones = data['observaciones']
        
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'data': compra.to_dict(include_relations=True),
            'message': 'Compra actualizada exitosamente'
        })
        
    except BadRequest as e:
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