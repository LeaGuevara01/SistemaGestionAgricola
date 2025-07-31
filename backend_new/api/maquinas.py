"""
API para gestión de máquinas
"""
from flask import request, jsonify

from . import api_bp
from models.maquina import Maquina
from models.componente import Componente
from extensions import db

@api_bp.route('/maquinas', methods=['GET'])
def get_maquinas():
    """Obtener lista de máquinas"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('q', '').strip()
        tipo = request.args.get('tipo')
        activa = request.args.get('activa', 'true').lower() == 'true'
        
        # Query base
        query = Maquina.query.filter(Maquina.activa == activa)
        
        # Filtros
        if search:
            query = Maquina.buscar(search)
        
        if tipo:
            query = query.filter(Maquina.tipo_maquina == tipo)
        
        # Ordenamiento
        sort_by = request.args.get('sort_by', 'nombre')
        sort_order = request.args.get('sort_order', 'asc')
        
        if hasattr(Maquina, sort_by):
            column = getattr(Maquina, sort_by)
            if sort_order == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        else:
            query = query.order_by(Maquina.nombre.asc())
        
        # Paginación
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [maquina.to_dict() for maquina in pagination.items],
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

@api_bp.route('/maquinas/<int:id>', methods=['GET'])
def get_maquina(id):
    """Obtener una máquina específica"""
    try:
        maquina = Maquina.get_by_id(id)
        if not maquina:
            return jsonify({
                'success': False,
                'error': 'Máquina no encontrada'
            }), 404
        
        # Incluir componentes asociados
        data = maquina.to_dict()
        data['componentes'] = [comp.to_dict() for comp in maquina.componentes]
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas', methods=['POST'])
def create_maquina():
    """Crear una nueva máquina"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['codigo_maquina', 'nombre']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo {field} es requerido'
                }), 400
        
        # Verificar que el código no exista
        if Maquina.query.filter_by(codigo_maquina=data['codigo_maquina']).first():
            return jsonify({
                'success': False,
                'error': 'El código de máquina ya existe'
            }), 400
        
        # Crear máquina
        maquina = Maquina(
            codigo_maquina=data['codigo_maquina'],
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            tipo_maquina=data.get('tipo_maquina'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            año_fabricacion=data.get('año_fabricacion'),
            numero_serie=data.get('numero_serie'),
            potencia=data.get('potencia'),
            capacidad=data.get('capacidad'),
            especificaciones=data.get('especificaciones'),
            estado=data.get('estado', 'operativa'),
            ubicacion=data.get('ubicacion'),
            valor_adquisicion=data.get('valor_adquisicion'),
            fecha_adquisicion=data.get('fecha_adquisicion'),
            moneda=data.get('moneda', 'USD'),
            horas_trabajo=data.get('horas_trabajo', 0)
        )
        
        maquina.save()
        
        return jsonify({
            'success': True,
            'data': maquina.to_dict(),
            'message': 'Máquina creada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>', methods=['PUT'])
def update_maquina(id):
    """Actualizar una máquina"""
    try:
        maquina = Maquina.get_by_id(id)
        if not maquina:
            return jsonify({
                'success': False,
                'error': 'Máquina no encontrada'
            }), 404
        
        data = request.get_json()
        
        # Actualizar campos
        updatable_fields = [
            'nombre', 'descripcion', 'tipo_maquina', 'marca', 'modelo',
            'año_fabricacion', 'numero_serie', 'potencia', 'capacidad',
            'especificaciones', 'estado', 'ubicacion', 'valor_adquisicion',
            'fecha_adquisicion', 'moneda', 'horas_trabajo', 'ultima_revision',
            'proxima_revision', 'activa'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(maquina, field, data[field])
        
        # Verificar código único si se cambia
        if 'codigo_maquina' in data and data['codigo_maquina'] != maquina.codigo_maquina:
            if Maquina.query.filter_by(codigo_maquina=data['codigo_maquina']).first():
                return jsonify({
                    'success': False,
                    'error': 'El código de máquina ya existe'
                }), 400
            maquina.codigo_maquina = data['codigo_maquina']
        
        maquina.save()
        
        return jsonify({
            'success': True,
            'data': maquina.to_dict(),
            'message': 'Máquina actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>', methods=['DELETE'])
def delete_maquina(id):
    """Eliminar (desactivar) una máquina"""
    try:
        maquina = Maquina.get_by_id(id)
        if not maquina:
            return jsonify({
                'success': False,
                'error': 'Máquina no encontrada'
            }), 404
        
        # Soft delete
        maquina.activa = False
        maquina.save()
        
        return jsonify({
            'success': True,
            'message': 'Máquina desactivada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>/componentes', methods=['GET'])
def get_maquina_componentes(id):
    """Obtener componentes de una máquina"""
    try:
        maquina = Maquina.get_by_id(id)
        if not maquina:
            return jsonify({
                'success': False,
                'error': 'Máquina no encontrada'
            }), 404
        
        componentes = [comp.to_dict() for comp in maquina.componentes]
        
        return jsonify({
            'success': True,
            'data': componentes,
            'total': len(componentes)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>/componentes', methods=['POST'])
def add_componente_to_maquina(id):
    """Agregar componente a una máquina"""
    try:
        maquina = Maquina.get_by_id(id)
        if not maquina:
            return jsonify({
                'success': False,
                'error': 'Máquina no encontrada'
            }), 404
        
        data = request.get_json()
        componente_id = data.get('componente_id')
        cantidad = data.get('cantidad', 1)
        es_critico = data.get('es_critico', False)
        
        if not componente_id:
            return jsonify({
                'success': False,
                'error': 'ID de componente es requerido'
            }), 400
        
        componente = Componente.get_by_id(componente_id)
        if not componente:
            return jsonify({
                'success': False,
                'error': 'Componente no encontrado'
            }), 404
        
        # Agregar componente a la máquina
        if maquina.agregar_componente(componente, cantidad, es_critico):
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Componente agregado a la máquina exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'El componente ya está asociado a esta máquina'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>/componentes/<int:componente_id>', methods=['DELETE'])
def remove_componente_from_maquina(id, componente_id):
    """Remover componente de una máquina"""
    try:
        maquina = Maquina.get_by_id(id)
        if not maquina:
            return jsonify({
                'success': False,
                'error': 'Máquina no encontrada'
            }), 404
        
        componente = Componente.get_by_id(componente_id)
        if not componente:
            return jsonify({
                'success': False,
                'error': 'Componente no encontrado'
            }), 404
        
        # Remover componente de la máquina
        if maquina.remover_componente(componente):
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Componente removido de la máquina exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'El componente no está asociado a esta máquina'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/tipos', methods=['GET'])
def get_tipos_maquina():
    """Obtener tipos de máquina únicos"""
    try:
        tipos = db.session.query(Maquina.tipo_maquina)\
            .filter(Maquina.tipo_maquina.isnot(None), Maquina.activa == True)\
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

@api_bp.route('/maquinas/necesitan-revision', methods=['GET'])
def get_maquinas_necesitan_revision():
    """Obtener máquinas que necesitan revisión"""
    try:
        maquinas = Maquina.necesitan_revision().all()
        
        return jsonify({
            'success': True,
            'data': [maquina.to_dict() for maquina in maquinas],
            'count': len(maquinas)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>/horas-trabajo', methods=['POST'])
def actualizar_horas_trabajo(id):
    """Actualizar horas de trabajo de una máquina"""
    try:
        maquina = Maquina.get_by_id(id)
        if not maquina:
            return jsonify({
                'success': False,
                'error': 'Máquina no encontrada'
            }), 404
        
        data = request.get_json()
        horas_adicionales = data.get('horas_adicionales', 0)
        
        if horas_adicionales <= 0:
            return jsonify({
                'success': False,
                'error': 'Horas adicionales debe ser mayor a cero'
            }), 400
        
        horas_anteriores = maquina.horas_trabajo
        maquina.actualizar_horas_trabajo(horas_adicionales)
        maquina.save()
        
        return jsonify({
            'success': True,
            'data': {
                'horas_anteriores': horas_anteriores,
                'horas_actuales': maquina.horas_trabajo,
                'proxima_revision': maquina.proxima_revision.isoformat() if maquina.proxima_revision else None
            },
            'message': 'Horas de trabajo actualizadas exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
