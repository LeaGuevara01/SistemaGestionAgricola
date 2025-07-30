from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from . import api_bp
from ...models.maquina import Maquina
from ...utils.db import db, commit_or_rollback
from ...services.file_service import FileService

@api_bp.route('/maquinas', methods=['GET'])
def get_maquinas():
    try:
        search = request.args.get('search', '')
        tipo = request.args.get('tipo', '')
        estado = request.args.get('estado', '')
        
        query = Maquina.query
        
        if search:
            query = query.filter(getattr(Maquina, 'Nombre', Maquina.nombre).contains(search))
        
        if tipo:
            if hasattr(Maquina, 'Tipo'):
                query = query.filter(Maquina.Tipo.contains(tipo))
        
        if estado:
            if hasattr(Maquina, 'Estado'):
                query = query.filter(Maquina.Estado.contains(estado))
        
        maquinas = query.all()
        
        return jsonify({
            'success': True,
            'data': [maquina.to_dict() for maquina in maquinas],
            'total': len(maquinas)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/maquinas', methods=['POST'])
def create_maquina():
    try:
        data = request.get_json()
        
        if not data.get('nombre'):
            raise BadRequest("El nombre es requerido")
        
        # Los campos numero_serie, tipo, horas_trabajo, ubicacion, activo no existen en la BD
        # Solo usar campos que realmente existen
        
        maquina = Maquina(
            nombre=data.get('nombre'),
            codigo=data.get('codigo', f"M-{Maquina.query.count() + 1:03d}")  # Auto-generar código si no se proporciona
        )
        
        # Establecer campos reflejados que existen en la BD
        if data.get('marca'):
            setattr(maquina, 'Marca', data.get('marca'))
        if data.get('modelo'):
            setattr(maquina, 'Modelo', data.get('modelo'))
        if data.get('año'):
            setattr(maquina, 'Año', data.get('año'))
        if data.get('estado'):
            setattr(maquina, 'Estado', data.get('estado'))
        if data.get('observaciones'):
            setattr(maquina, 'Observaciones', data.get('observaciones'))
        
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
        
        print(f"🔧 Actualizando máquina ID: {id}")
        print(f"📝 Datos recibidos: {data}")
        
        # ✅ USAR METADATOS DINÁMICOS en lugar de hardcodear
        from ...services.field_metadata_service import FieldMetadataService
        metadata = FieldMetadataService.get_maquinas_metadata()
        
        # Crear mapeo dinámico basado en metadatos
        field_mapping = {}
        available_fields = []
        unavailable_fields = []
        
        for frontend_field, field_info in metadata['field_metadata'].items():
            if field_info['exists_in_db']:
                field_mapping[frontend_field] = field_info['db_field']
                available_fields.append(frontend_field)
            else:
                unavailable_fields.append(frontend_field)
        
        print(f"📊 Campos disponibles: {available_fields}")
        print(f"⚠️  Campos no disponibles: {unavailable_fields}")
        
        # Actualizar campos usando el mapeo dinámico
        for frontend_field, db_field in field_mapping.items():
            if frontend_field in data:
                value = data[frontend_field]
                
                # ✅ SKIP campos vacíos para evitar sobrescribir con valores vacíos
                if value == '' or value is None:
                    print(f"   ⚠️  Saltando campo vacío {frontend_field}")
                    continue
                
                print(f"   🔄 Actualizando {frontend_field} -> {db_field} = {value}")
                
                # Para campos explícitos, usar setattr directo
                if frontend_field in ['nombre', 'codigo']:
                    setattr(maquina, db_field, value)
                else:
                    # Para campos reflejados, usar setattr con el nombre de BD
                    setattr(maquina, db_field, value)
        
        # Manejar campos no disponibles de forma dinámica
        for field in unavailable_fields:
            if field in data:
                value = data[field]
                field_info = metadata['field_metadata'][field]
                if value != '' and value is not None:
                    print(f"   ⚠️  Ignorando campo {field} (no existe en BD): {value}")
                    print(f"      💡 Nota: {field_info.get('note', 'Campo no implementado')}")
                else:
                    print(f"   ⚠️  Ignorando campo vacío {field} (no existe en BD)")
        
        commit_or_rollback()
        
        print(f"✅ Máquina {id} actualizada exitosamente")
        
        return jsonify({
            'success': True,
            'data': maquina.to_dict(),
            'message': 'Máquina actualizada exitosamente',
            'metadata': {
                'updated_fields': list(field_mapping.keys()),
                'ignored_fields': unavailable_fields
            }
        })
        
    except BadRequest as e:
        print(f"❌ Error BadRequest: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"❌ Error en update_maquina: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>/upload-photo', methods=['POST'])
def upload_maquina_photo(id):
    """Subir foto de máquina"""
    try:
        print(f"📸 Subiendo foto para máquina ID: {id}")
        
        maquina = Maquina.query.get_or_404(id)
        
        if 'photo' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se encontró archivo en la petición'
            }), 400
        
        file = request.files['photo']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No se seleccionó archivo'
            }), 400
        
        # Verificar que el archivo tiene extensión válida
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if '.' not in file.filename:
            return jsonify({
                'success': False,
                'error': 'Archivo sin extensión válida'
            }), 400
            
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        if file_extension not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'Formato no permitido. Use: {", ".join(allowed_extensions)}'
            }), 400
        
        if file:
            # Importar las funciones necesarias
            from werkzeug.utils import secure_filename
            from flask import current_app
            import os
            
            # Generar nombre seguro
            filename = secure_filename(f"maquina_{id}.{file_extension}")
            
            # Crear directorio si no existe (guardar en raíz de fotos como el listado)
            upload_folder = os.path.join(current_app.root_path, '..', 'static', 'fotos')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Guardar archivo
            filepath = os.path.join(upload_folder, filename)
            
            # Eliminar foto anterior si existe
            old_filename = getattr(maquina, 'Foto', None)
            if old_filename:
                old_filepath = os.path.join(upload_folder, old_filename)
                if os.path.exists(old_filepath):
                    try:
                        os.remove(old_filepath)
                        print(f"🗑️ Foto anterior eliminada: {old_filename}")
                    except Exception as e:
                        print(f"⚠️ No se pudo eliminar foto anterior: {e}")
            
            # Guardar nueva foto
            file.save(filepath)
            
            # Actualizar máquina con el campo real 'Foto'
            setattr(maquina, 'Foto', filename)
            db.session.commit()
            
            print(f"✅ Foto guardada: {filename}")
            
            return jsonify({
                'success': True,
                'message': 'Foto subida exitosamente',
                'data': {
                    'foto': filename,
                    'maquina': maquina.to_dict()
                }
            })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en upload_maquina_photo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Las importaciones ya están al inicio del archivo
# No necesitamos importaciones duplicadas

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
        from ...services.import_service import ImportService
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
        from ...services.import_service import ImportService
        return ImportService.get_maquinas_template()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/maquinas/metadata', methods=['GET'])
def get_maquinas_metadata():
    """Obtener metadatos de campos para formularios dinámicos"""
    try:
        from ...services.field_metadata_service import FieldMetadataService
        metadata = FieldMetadataService.get_maquinas_metadata()
        
        return jsonify({
            'success': True,
            'data': metadata,
            'message': 'Metadatos obtenidos exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/stats', methods=['GET'])
def get_maquinas_stats():
    """Estadísticas de máquinas"""
    try:
        # ✅ QUITAR FILTROS POR 'activo' que no existe
        total = Maquina.query.count()
        
        # ✅ USAR CAMPOS HÍBRIDOS CORRECTOS
        operativo = Maquina.query.filter(
            getattr(Maquina, 'Estado', Maquina.nombre) == 'operativo'
        ).count() if hasattr(Maquina, 'Estado') else 0
        
        mantenimiento = Maquina.query.filter(
            getattr(Maquina, 'Estado', Maquina.nombre) == 'mantenimiento'
        ).count() if hasattr(Maquina, 'Estado') else 0
        
        fuera_servicio = Maquina.query.filter(
            getattr(Maquina, 'Estado', Maquina.nombre) == 'fuera_servicio'
        ).count() if hasattr(Maquina, 'Estado') else 0
        
        # Estadísticas por tipo
        tipos_query = db.session.query(
            getattr(Maquina, 'Tipo', Maquina.nombre), 
            db.func.count(Maquina.id)
        ).group_by(getattr(Maquina, 'Tipo', Maquina.nombre)) if hasattr(Maquina, 'Tipo') else []
        
        tipos = tipos_query.all() if tipos_query else []
        
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