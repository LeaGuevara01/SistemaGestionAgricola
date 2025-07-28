from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from app.routes.api import api_bp
from app.models import Componente
from app.utils.db import db, commit_or_rollback
from app.services.file_service import FileService

@api_bp.route('/componentes', methods=['GET'])
def get_componentes():
    try:
        # Parámetros de filtrado
        categoria = request.args.get('categoria')
        activo = request.args.get('activo', 'true').lower() == 'true'
        search = request.args.get('search', '').strip()
        
        # Construir query
        query = Componente.query
        
        if categoria:
            query = query.filter(Componente.categoria == categoria)
        
        query = query.filter(Componente.activo == activo)
        
        if search:
            query = query.filter(
                db.or_(
                    Componente.nombre.ilike(f'%{search}%'),
                    Componente.descripcion.ilike(f'%{search}%'),
                    Componente.numero_parte.ilike(f'%{search}%')
                )
            )
        
        componentes = query.order_by(Componente.nombre).all()
        
        return jsonify({
            'success': True,
            'data': [comp.to_dict() for comp in componentes],
            'total': len(componentes)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes', methods=['POST'])
def create_componente():
    try:
        data = request.get_json()
        
        # Validaciones
        if not data.get('nombre'):
            raise BadRequest("El nombre es requerido")
        
        # Verificar si el número de parte ya existe
        if data.get('numero_parte'):
            existing = Componente.query.filter_by(numero_parte=data['numero_parte']).first()
            if existing:
                raise BadRequest("El número de parte ya existe")
        
        componente = Componente(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            numero_parte=data.get('numero_parte'),
            categoria=data.get('categoria'),
            precio_unitario=data.get('precio_unitario'),
            stock_minimo=data.get('stock_minimo', 0)
        )
        
        db.session.add(componente)
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'data': componente.to_dict(),
            'message': 'Componente creado exitosamente'
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

@api_bp.route('/componentes/<int:id>', methods=['GET'])
def get_componente(id):
    try:
        componente = Componente.query.get_or_404(id)
        include_relations = request.args.get('include_relations', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': componente.to_dict(include_relations=include_relations)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/<int:id>', methods=['PUT'])
def update_componente(id):
    try:
        componente = Componente.query.get_or_404(id)
        data = request.get_json()
        
        # Verificar número de parte único
        if data.get('numero_parte') and data['numero_parte'] != componente.numero_parte:
            existing = Componente.query.filter_by(numero_parte=data['numero_parte']).first()
            if existing:
                raise BadRequest("El número de parte ya existe")
        
        # Actualizar campos
        if 'nombre' in data:
            componente.nombre = data['nombre']
        if 'descripcion' in data:
            componente.descripcion = data['descripcion']
        if 'numero_parte' in data:
            componente.numero_parte = data['numero_parte']
        if 'categoria' in data:
            componente.categoria = data['categoria']
        if 'precio_unitario' in data:
            componente.precio_unitario = data['precio_unitario']
        if 'stock_minimo' in data:
            componente.stock_minimo = data['stock_minimo']
        if 'activo' in data:
            componente.activo = data['activo']
        
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'data': componente.to_dict(),
            'message': 'Componente actualizado exitosamente'
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

@api_bp.route('/componentes/<int:id>', methods=['DELETE'])
def delete_componente(id):
    try:
        componente = Componente.query.get_or_404(id)
        
        # Verificar si tiene dependencias
        if componente.compras.count() > 0:
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar el componente porque tiene compras asociadas'
            }), 400
        
        # Eliminar foto si existe
        if componente.foto:
            FileService.delete_file(componente.foto)
        
        db.session.delete(componente)
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'message': 'Componente eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/<int:id>/upload-photo', methods=['POST'])
def upload_componente_photo(id):
    try:
        componente = Componente.query.get_or_404(id)
        
        if 'photo' not in request.files:
            raise BadRequest("No se proporcionó archivo")
        
        file = request.files['photo']
        if file.filename == '':
            raise BadRequest("No se seleccionó archivo")
        
        # Eliminar foto anterior si existe
        if componente.foto:
            FileService.delete_file(componente.foto)
        
        # Guardar nueva foto
        file_path = FileService.save_file(file, 'componentes')
        if not file_path:
            raise BadRequest("Archivo no válido")
        
        componente.foto = file_path
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'data': {
                'foto': file_path,
                'url': FileService.get_file_url(file_path)
            },
            'message': 'Foto subida exitosamente'
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

@api_bp.route('/componentes/categorias', methods=['GET'])
def get_categorias():
    try:
        categorias = db.session.query(Componente.categoria).filter(
            Componente.categoria.isnot(None),
            Componente.activo == True
        ).distinct().all()
        
        return jsonify({
            'success': True,
            'data': [cat[0] for cat in categorias if cat[0]]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500