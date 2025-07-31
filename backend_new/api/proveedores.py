"""
API para gestión de proveedores
"""
from flask import request, jsonify

from . import api_bp
from models.proveedor import Proveedor
from extensions import db

@api_bp.route('/proveedores', methods=['GET'])
def get_proveedores():
    """Obtener lista de proveedores"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('q', '').strip()
        tipo = request.args.get('tipo')
        activo = request.args.get('activo', 'true').lower() == 'true'
        
        # Query base
        query = Proveedor.query.filter(Proveedor.activo == activo)
        
        # Filtros
        if search:
            query = Proveedor.buscar(search)
        
        if tipo:
            query = query.filter(Proveedor.tipo_proveedor == tipo)
        
        # Ordenamiento
        sort_by = request.args.get('sort_by', 'nombre')
        sort_order = request.args.get('sort_order', 'asc')
        
        if hasattr(Proveedor, sort_by):
            column = getattr(Proveedor, sort_by)
            if sort_order == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        else:
            query = query.order_by(Proveedor.nombre.asc())
        
        # Paginación
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [proveedor.to_dict() for proveedor in pagination.items],
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

@api_bp.route('/proveedores/<int:id>', methods=['GET'])
def get_proveedor(id):
    """Obtener un proveedor específico"""
    try:
        proveedor = Proveedor.get_by_id(id)
        if not proveedor:
            return jsonify({
                'success': False,
                'error': 'Proveedor no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': proveedor.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/proveedores', methods=['POST'])
def create_proveedor():
    """Crear un nuevo proveedor"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['codigo_proveedor', 'nombre']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo {field} es requerido'
                }), 400
        
        # Verificar que el código no exista
        if Proveedor.query.filter_by(codigo_proveedor=data['codigo_proveedor']).first():
            return jsonify({
                'success': False,
                'error': 'El código de proveedor ya existe'
            }), 400
        
        # Crear proveedor
        proveedor = Proveedor(
            codigo_proveedor=data['codigo_proveedor'],
            nombre=data['nombre'],
            razon_social=data.get('razon_social'),
            tipo_proveedor=data.get('tipo_proveedor', 'nacional'),
            email=data.get('email'),
            telefono=data.get('telefono'),
            sitio_web=data.get('sitio_web'),
            direccion=data.get('direccion'),
            ciudad=data.get('ciudad'),
            provincia=data.get('provincia'),
            codigo_postal=data.get('codigo_postal'),
            pais=data.get('pais', 'Argentina'),
            cuit_dni=data.get('cuit_dni'),
            condicion_iva=data.get('condicion_iva'),
            condiciones_pago=data.get('condiciones_pago'),
            descuento_general=data.get('descuento_general', 0),
            moneda_preferida=data.get('moneda_preferida', 'ARS'),
            notas=data.get('notas')
        )
        
        proveedor.save()
        
        return jsonify({
            'success': True,
            'data': proveedor.to_dict(),
            'message': 'Proveedor creado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/proveedores/<int:id>', methods=['PUT'])
def update_proveedor(id):
    """Actualizar un proveedor"""
    try:
        proveedor = Proveedor.get_by_id(id)
        if not proveedor:
            return jsonify({
                'success': False,
                'error': 'Proveedor no encontrado'
            }), 404
        
        data = request.get_json()
        
        # Actualizar campos
        updatable_fields = [
            'nombre', 'razon_social', 'tipo_proveedor', 'email', 'telefono',
            'sitio_web', 'direccion', 'ciudad', 'provincia', 'codigo_postal',
            'pais', 'cuit_dni', 'condicion_iva', 'condiciones_pago',
            'descuento_general', 'moneda_preferida', 'calificacion',
            'notas', 'activo'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(proveedor, field, data[field])
        
        # Verificar código único si se cambia
        if 'codigo_proveedor' in data and data['codigo_proveedor'] != proveedor.codigo_proveedor:
            if Proveedor.query.filter_by(codigo_proveedor=data['codigo_proveedor']).first():
                return jsonify({
                    'success': False,
                    'error': 'El código de proveedor ya existe'
                }), 400
            proveedor.codigo_proveedor = data['codigo_proveedor']
        
        proveedor.save()
        
        return jsonify({
            'success': True,
            'data': proveedor.to_dict(),
            'message': 'Proveedor actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/proveedores/<int:id>', methods=['DELETE'])
def delete_proveedor(id):
    """Eliminar (desactivar) un proveedor"""
    try:
        proveedor = Proveedor.get_by_id(id)
        if not proveedor:
            return jsonify({
                'success': False,
                'error': 'Proveedor no encontrado'
            }), 404
        
        # Soft delete
        proveedor.activo = False
        proveedor.save()
        
        return jsonify({
            'success': True,
            'message': 'Proveedor desactivado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/proveedores/tipos', methods=['GET'])
def get_tipos_proveedor():
    """Obtener tipos de proveedor únicos"""
    try:
        tipos = db.session.query(Proveedor.tipo_proveedor)\
            .filter(Proveedor.tipo_proveedor.isnot(None), Proveedor.activo == True)\
            .distinct().all()
        
        return jsonify({
            'success': True,
            'data': [tipo[0] for tipo in tipos if tipo[0]]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/proveedores/mejor-calificados', methods=['GET'])
def get_proveedores_mejor_calificados():
    """Obtener proveedores mejor calificados"""
    try:
        limite = int(request.args.get('limite', 10))
        proveedores = Proveedor.mejor_calificados(limite).all()
        
        return jsonify({
            'success': True,
            'data': [proveedor.to_dict() for proveedor in proveedores]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/proveedores/<int:id>/calificacion', methods=['POST'])
def actualizar_calificacion_proveedor(id):
    """Actualizar calificación de proveedor"""
    try:
        proveedor = Proveedor.get_by_id(id)
        if not proveedor:
            return jsonify({
                'success': False,
                'error': 'Proveedor no encontrado'
            }), 404
        
        data = request.get_json()
        calificacion = data.get('calificacion')
        
        if not calificacion or not (1.0 <= calificacion <= 5.0):
            return jsonify({
                'success': False,
                'error': 'Calificación debe estar entre 1.0 y 5.0'
            }), 400
        
        if proveedor.actualizar_calificacion(calificacion):
            proveedor.save()
            
            return jsonify({
                'success': True,
                'data': {'calificacion': proveedor.calificacion},
                'message': 'Calificación actualizada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error actualizando calificación'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
