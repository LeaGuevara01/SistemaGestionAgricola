"""
API para gestión de componentes
"""
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os

from . import api_bp
from models.componente import Componente
from extensions import db
from utils import validate_json, paginate_query, save_uploaded_file

@api_bp.route('/componentes', methods=['GET'])
def get_componentes():
    """Obtener lista de componentes con filtros y paginación"""
    try:
        # Parámetros de consulta
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('q', '').strip()
        categoria = request.args.get('categoria')
        activo = request.args.get('activo', 'true').lower() == 'true'
        
        # Query base
        query = Componente.query.filter(Componente.activo == activo)
        
        # Filtros
        if search:
            query = Componente.buscar(search)
        
        if categoria:
            query = query.filter(Componente.categoria == categoria)
        
        # Ordenamiento
        sort_by = request.args.get('sort_by', 'nombre')
        sort_order = request.args.get('sort_order', 'asc')
        
        if hasattr(Componente, sort_by):
            column = getattr(Componente, sort_by)
            if sort_order == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        else:
            query = query.order_by(Componente.nombre.asc())
        
        # Paginación
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [componente.to_dict() for componente in pagination.items],
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

@api_bp.route('/componentes/<int:id>', methods=['GET'])
def get_componente(id):
    """Obtener un componente específico"""
    try:
        componente = Componente.get_by_id(id)
        if not componente:
            return jsonify({
                'success': False,
                'error': 'Componente no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': componente.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes', methods=['POST'])
def create_componente():
    """Crear un nuevo componente"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['numero_parte', 'nombre']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo {field} es requerido'
                }), 400
        
        # Verificar que el número de parte no exista
        if Componente.query.filter_by(numero_parte=data['numero_parte']).first():
            return jsonify({
                'success': False,
                'error': 'El número de parte ya existe'
            }), 400
        
        # Crear componente
        componente = Componente(
            numero_parte=data['numero_parte'],
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            categoria=data.get('categoria'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            precio_unitario=data.get('precio_unitario', 0),
            stock_actual=data.get('stock_actual', 0),
            stock_minimo=data.get('stock_minimo', 1),
            stock_maximo=data.get('stock_maximo', 100),
            especificaciones=data.get('especificaciones'),
            moneda=data.get('moneda', 'USD')
        )
        
        componente.save()
        
        return jsonify({
            'success': True,
            'data': componente.to_dict(),
            'message': 'Componente creado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/<int:id>', methods=['PUT'])
def update_componente(id):
    """Actualizar un componente"""
    try:
        componente = Componente.get_by_id(id)
        if not componente:
            return jsonify({
                'success': False,
                'error': 'Componente no encontrado'
            }), 404
        
        data = request.get_json()
        
        # Actualizar campos
        updatable_fields = [
            'nombre', 'descripcion', 'categoria', 'marca', 'modelo',
            'precio_unitario', 'stock_minimo', 'stock_maximo',
            'especificaciones', 'moneda', 'activo'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(componente, field, data[field])
        
        # Verificar número de parte único si se cambia
        if 'numero_parte' in data and data['numero_parte'] != componente.numero_parte:
            if Componente.query.filter_by(numero_parte=data['numero_parte']).first():
                return jsonify({
                    'success': False,
                    'error': 'El número de parte ya existe'
                }), 400
            componente.numero_parte = data['numero_parte']
        
        componente.save()
        
        return jsonify({
            'success': True,
            'data': componente.to_dict(),
            'message': 'Componente actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/<int:id>', methods=['DELETE'])
def delete_componente(id):
    """Eliminar (desactivar) un componente"""
    try:
        componente = Componente.get_by_id(id)
        if not componente:
            return jsonify({
                'success': False,
                'error': 'Componente no encontrado'
            }), 404
        
        # Soft delete: marcar como inactivo
        componente.activo = False
        componente.save()
        
        return jsonify({
            'success': True,
            'message': 'Componente desactivado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/<int:id>/foto', methods=['POST'])
def upload_componente_foto(id):
    """Subir foto de componente"""
    try:
        componente = Componente.get_by_id(id)
        if not componente:
            return jsonify({
                'success': False,
                'error': 'Componente no encontrado'
            }), 404
        
        if 'foto' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se encontró archivo de foto'
            }), 400
        
        file = request.files['foto']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No se seleccionó archivo'
            }), 400
        
        # Guardar archivo
        filename = save_uploaded_file(file, 'componentes')
        if filename:
            componente.foto = filename
            componente.save()
            
            return jsonify({
                'success': True,
                'data': {
                    'foto': filename,
                    'url': f'/static/uploads/componentes/{filename}'
                },
                'message': 'Foto subida exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error al guardar archivo'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/categorias', methods=['GET'])
def get_categorias():
    """Obtener lista de categorías únicas"""
    try:
        categorias = db.session.query(Componente.categoria)\
            .filter(Componente.categoria.isnot(None), Componente.activo == True)\
            .distinct().all()
        
        return jsonify({
            'success': True,
            'data': [cat[0] for cat in categorias if cat[0]]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/stock-bajo', methods=['GET'])
def get_componentes_stock_bajo():
    """Obtener componentes con stock bajo"""
    try:
        componentes = Componente.con_stock_bajo().all()
        
        return jsonify({
            'success': True,
            'data': [componente.to_dict() for componente in componentes],
            'count': len(componentes)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/<int:id>/stock', methods=['POST'])
def ajustar_stock_componente(id):
    """Ajustar stock de un componente"""
    try:
        componente = Componente.get_by_id(id)
        if not componente:
            return jsonify({
                'success': False,
                'error': 'Componente no encontrado'
            }), 404
        
        data = request.get_json()
        cantidad = data.get('cantidad', 0)
        motivo = data.get('motivo', 'Ajuste manual')
        
        if cantidad == 0:
            return jsonify({
                'success': False,
                'error': 'Cantidad debe ser diferente de cero'
            }), 400
        
        # Actualizar stock
        stock_nuevo = componente.actualizar_stock(cantidad, 'ajuste')
        
        # Crear registro de movimiento
        from models.stock import Stock
        movimiento = Stock.crear_movimiento(
            componente_id=id,
            tipo_movimiento='ajuste',
            cantidad=cantidad,
            motivo=motivo,
            usuario=data.get('usuario', 'Sistema')
        )
        movimiento.save()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'stock_anterior': stock_nuevo - cantidad,
                'stock_nuevo': stock_nuevo,
                'movimiento_id': movimiento.id
            },
            'message': 'Stock ajustado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
