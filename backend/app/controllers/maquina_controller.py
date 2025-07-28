from flask import request, jsonify
from app.models.maquina import Maquina
from app.utils.db import db
from app.services.file_service import FileService

def get_maquinas():
    """Obtener todas las máquinas con paginación y filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        estado = request.args.get('estado', '')
        tipo = request.args.get('tipo', '')
        activo = request.args.get('activo', None, type=bool)
        
        query = Maquina.query
        
        # Filtro por búsqueda
        if search:
            query = query.filter(
                db.or_(
                    Maquina.nombre.ilike(f'%{search}%'),
                    Maquina.marca.ilike(f'%{search}%'),
                    Maquina.modelo.ilike(f'%{search}%'),
                    Maquina.numero_serie.ilike(f'%{search}%')
                )
            )
        
        # Filtro por estado
        if estado:
            query = query.filter(Maquina.estado == estado)
        
        # Filtro por tipo
        if tipo:
            query = query.filter(Maquina.tipo == tipo)
        
        # Filtro por activo
        if activo is not None:
            query = query.filter(Maquina.activo == activo)
        
        maquinas = query.order_by(Maquina.nombre).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'maquinas': [maquina.to_dict() for maquina in maquinas.items],
            'total': maquinas.total,
            'pages': maquinas.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_maquina(maquina_id):
    """Obtener una máquina específica"""
    try:
        maquina = Maquina.query.get(maquina_id)
        if not maquina:
            return jsonify({'success': False, 'error': 'Máquina no encontrada'}), 404
        
        include_relations = request.args.get('include_relations', False, type=bool)
        
        return jsonify({
            'success': True,
            'maquina': maquina.to_dict(include_relations=include_relations)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def create_maquina():
    """Crear nueva máquina"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data.get('nombre'):
            return jsonify({
                'success': False, 
                'error': 'El nombre es requerido'
            }), 400
        
        # Verificar que el número de serie no exista (si se proporciona)
        if data.get('numero_serie'):
            existing = Maquina.query.filter_by(numero_serie=data['numero_serie']).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Número de serie ya existe'
                }), 400
        
        maquina = Maquina(
            nombre=data['nombre'],
            marca=data.get('marca', ''),
            modelo=data.get('modelo', ''),
            numero_serie=data.get('numero_serie'),
            año=data.get('año'),
            tipo=data.get('tipo', ''),
            estado=data.get('estado', 'operativo'),
            horas_trabajo=data.get('horas_trabajo', 0),
            ubicacion=data.get('ubicacion', ''),
            foto=data.get('foto'),
            observaciones=data.get('observaciones', ''),
            activo=data.get('activo', True)
        )
        
        db.session.add(maquina)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'maquina': maquina.to_dict(),
            'message': 'Máquina creada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def update_maquina(maquina_id):
    """Actualizar máquina"""
    try:
        maquina = Maquina.query.get(maquina_id)
        if not maquina:
            return jsonify({'success': False, 'error': 'Máquina no encontrada'}), 404
        
        data = request.get_json()
        
        # Verificar número de serie único (si se está cambiando)
        if data.get('numero_serie') and data['numero_serie'] != maquina.numero_serie:
            existing = Maquina.query.filter_by(numero_serie=data['numero_serie']).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Número de serie ya existe'
                }), 400
        
        # Actualizar campos
        maquina.nombre = data.get('nombre', maquina.nombre)
        maquina.marca = data.get('marca', maquina.marca)
        maquina.modelo = data.get('modelo', maquina.modelo)
        maquina.numero_serie = data.get('numero_serie', maquina.numero_serie)
        maquina.año = data.get('año', maquina.año)
        maquina.tipo = data.get('tipo', maquina.tipo)
        maquina.estado = data.get('estado', maquina.estado)
        maquina.horas_trabajo = data.get('horas_trabajo', maquina.horas_trabajo)
        maquina.ubicacion = data.get('ubicacion', maquina.ubicacion)
        maquina.foto = data.get('foto', maquina.foto)
        maquina.observaciones = data.get('observaciones', maquina.observaciones)
        maquina.activo = data.get('activo', maquina.activo)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'maquina': maquina.to_dict(),
            'message': 'Máquina actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def delete_maquina(maquina_id):
    """Eliminar máquina (soft delete)"""
    try:
        maquina = Maquina.query.get(maquina_id)
        if not maquina:
            return jsonify({'success': False, 'error': 'Máquina no encontrada'}), 404
        
        # Soft delete - marcar como inactivo
        maquina.activo = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Máquina desactivada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def upload_foto_maquina(maquina_id):
    """Subir foto para una máquina"""
    try:
        maquina = Maquina.query.get(maquina_id)
        if not maquina:
            return jsonify({'success': False, 'error': 'Máquina no encontrada'}), 404
        
        if 'foto' not in request.files:
            return jsonify({'success': False, 'error': 'No se proporcionó archivo'}), 400
        
        file = request.files['foto']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
        
        # Eliminar foto anterior si existe
        if maquina.foto:
            FileService.delete_file(maquina.foto)
        
        # Guardar nueva foto
        foto_path = FileService.save_file(file, subfolder='maquinas')
        if not foto_path:
            return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400
        
        maquina.foto = foto_path
        db.session.commit()
        
        return jsonify({
            'success': True,
            'foto_url': FileService.get_file_url(foto_path),
            'message': 'Foto subida exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def get_maquina_stats():
    """Obtener estadísticas de máquinas"""
    try:
        total = Maquina.query.filter_by(activo=True).count()
        operativo = Maquina.query.filter_by(estado='operativo', activo=True).count()
        mantenimiento = Maquina.query.filter_by(estado='mantenimiento', activo=True).count()
        fuera_servicio = Maquina.query.filter_by(estado='fuera_servicio', activo=True).count()
        
        # Estadísticas por tipo
        tipos = db.session.query(
            Maquina.tipo, 
            db.func.count(Maquina.id)
        ).filter_by(activo=True).group_by(Maquina.tipo).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'operativo': operativo,
                'mantenimiento': mantenimiento,
                'fuera_servicio': fuera_servicio,
                'por_tipo': [{'tipo': tipo[0], 'cantidad': tipo[1]} for tipo in tipos]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500