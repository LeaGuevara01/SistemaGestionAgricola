from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from app.routes.api import api_bp
from app.models import Maquina
from app.utils.db import db, commit_or_rollback
from app.services.file_service import FileService

@api_bp.route('/maquinas', methods=['GET'])
def get_maquinas():
    try:
        # Filtros
        tipo = request.args.get('tipo')
        estado = request.args.get('estado')
        activo = request.args.get('activo', 'true').lower() == 'true'
        search = request.args.get('search', '').strip()
        
        query = Maquina.query
        
        if tipo:
            query = query.filter(Maquina.tipo == tipo)
        if estado:
            query = query.filter(Maquina.estado == estado)
        
        query = query.filter(Maquina.activo == activo)
        
        if search:
            query = query.filter(
                db.or_(
                    Maquina.nombre.ilike(f'%{search}%'),
                    Maquina.marca.ilike(f'%{search}%'),
                    Maquina.modelo.ilike(f'%{search}%'),
                    Maquina.numero_serie.ilike(f'%{search}%')
                )
            )
        
        maquinas = query.order_by(Maquina.nombre).all()
        
        return jsonify({
            'success': True,
            'data': [maq.to_dict() for maq in maquinas],
            'total': len(maquinas)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas', methods=['POST'])
def create_maquina():
    try:
        data = request.get_json()
        
        if not data.get('nombre'):
            raise BadRequest("El nombre es requerido")
        
        # Verificar número de serie único
        if data.get('numero_serie'):
            existing = Maquina.query.filter_by(numero_serie=data['numero_serie']).first()
            if existing:
                raise BadRequest("El número de serie ya existe")
        
        maquina = Maquina(
            nombre=data.get('nombre'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            numero_serie=data.get('numero_serie'),
            año=data.get('año'),
            tipo=data.get('tipo'),
            estado=data.get('estado', 'operativo'),
            horas_trabajo=data.get('horas_trabajo', 0),
            ubicacion=data.get('ubicacion'),
            observaciones=data.get('observaciones')
        )
        
        db.session.add(maquina)
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'data': maquina.to_dict(),
            'message': 'Máquina creada exitosamente'
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

@api_bp.route('/maquinas/<int:id>', methods=['GET'])
def get_maquina(id):
    try:
        maquina = Maquina.query.get_or_404(id)
        include_relations = request.args.get('include_relations', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': maquina.to_dict(include_relations=include_relations)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>', methods=['PUT'])
def update_maquina(id):
    try:
        maquina = Maquina.query.get_or_404(id)
        data = request.get_json()
        
        # Verificar número de serie único
        if data.get('numero_serie') and data['numero_serie'] != maquina.numero_serie:
            existing = Maquina.query.filter_by(numero_serie=data['numero_serie']).first()
            if existing:
                raise BadRequest("El número de serie ya existe")
        
        # Actualizar campos
        for field in ['nombre', 'marca', 'modelo', 'numero_serie', 'año', 'tipo', 'estado', 'horas_trabajo', 'ubicacion', 'observaciones', 'activo']:
            if field in data:
                setattr(maquina, field, data[field])
        
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'data': maquina.to_dict(),
            'message': 'Máquina actualizada exitosamente'
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

@api_bp.route('/maquinas/<int:id>/upload-photo', methods=['POST'])
def upload_maquina_photo(id):
    try:
        maquina = Maquina.query.get_or_404(id)
        
        if 'photo' not in request.files:
            raise BadRequest("No se proporcionó archivo")
        
        file = request.files['photo']
        if file.filename == '':
            raise BadRequest("No se seleccionó archivo")
        
        if maquina.foto:
            FileService.delete_file(maquina.foto)
        
        file_path = FileService.save_file(file, 'maquinas')
        if not file_path:
            raise BadRequest("Archivo no válido")
        
        maquina.foto = file_path
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

from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from app.routes.api import api_bp
from app.models import Maquina
from app.utils.db import db, commit_or_rollback
from app.services.file_service import FileService

# ...existing code...

# NUEVAS RUTAS PARA IMPORTACIÓN
@api_bp.route('/maquinas/import', methods=['POST'])
def import_maquinas():
    """Importar máquinas desde CSV"""
    try:
        if 'csvFile' not in request.files:
            raise BadRequest('No se proporcionó archivo CSV')
        
        file = request.files['csvFile']
        if file.filename == '':
            raise BadRequest('No se seleccionó archivo')
        
        # Usar el FileService existente
        try:
            filepath = FileService.save_import_file(file, 'imports/maquinas')
            if not filepath:
                raise BadRequest('Tipo de archivo no permitido. Solo CSV, XLS, XLSX')
        except ValueError as e:
            raise BadRequest(str(e))
        
        # Importar datos
        from app.services.import_service import ImportService
        result = ImportService.import_maquinas_from_csv(filepath)
        
        # Limpiar archivo temporal
        FileService.cleanup_temp_file(filepath)
        
        return jsonify({
            'success': True,
            'imported': result['imported'],
            'errors': result['errors'],
            'total': result['total']
        })
        
    except BadRequest as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error en la importación: {str(e)}'}), 500

@api_bp.route('/maquinas/import/template', methods=['GET'])
def get_maquinas_template():
    """Descargar plantilla CSV para máquinas"""
    try:
        from app.services.import_service import ImportService
        return ImportService.get_maquinas_template()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/maquinas/stats', methods=['GET'])
def get_maquinas_stats():
    """Estadísticas de máquinas"""
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
            'data': {
                'total': total,
                'operativo': operativo,
                'mantenimiento': mantenimiento,
                'fuera_servicio': fuera_servicio,
                'por_tipo': [{'tipo': tipo[0] or 'Sin tipo', 'cantidad': tipo[1]} for tipo in tipos]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500